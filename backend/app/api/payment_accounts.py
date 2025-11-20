from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.core.database import get_db
from app.models.payment_account import PaymentAccount, PaymentAccountType, PaymentAccountStatus
from app.schemas.payment_account import (
    PaymentAccountCreate, 
    PaymentAccountResponse, 
    PaymentAccountUpdate,
    PaymentAccountBulkUpload
)
import logging
logger = logging.getLogger(__name__)

router = APIRouter()

# AUTHENTICATION DISABLED - Admin bypass
def get_current_admin_bypass(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Bypass admin authentication - returns dummy admin payload"""
    return {"sub": "1", "email": "vardiano@tech", "is_admin": True}

@router.post("/upload", response_model=List[PaymentAccountResponse])
async def upload_payment_accounts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    """Upload payment accounts from JSON file"""
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JSON file"
        )
    
    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        # Validate structure
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON must be an object with 'upi', 'bank', and/or 'crypto' arrays"
            )
        
        created_accounts = []
        
        # Process UPI accounts
        if 'upi' in data and isinstance(data['upi'], list):
            for upi_data in data['upi']:
                account = PaymentAccount(
                    account_type=PaymentAccountType.UPI,
                    identifier_name=upi_data.get('identifier_name', f"upi_{len(created_accounts) + 1}"),
                    details=upi_data,
                    status=PaymentAccountStatus.PENDING,
                    is_active=False
                )
                db.add(account)
                created_accounts.append(account)
        
        # Process Bank accounts
        if 'bank' in data and isinstance(data['bank'], list):
            for bank_data in data['bank']:
                account = PaymentAccount(
                    account_type=PaymentAccountType.BANK,
                    identifier_name=bank_data.get('identifier_name', f"bank_{len(created_accounts) + 1}"),
                    details=bank_data,
                    status=PaymentAccountStatus.PENDING,
                    is_active=False
                )
                db.add(account)
                created_accounts.append(account)
        
        # Process Crypto accounts
        if 'crypto' in data and isinstance(data['crypto'], list):
            for crypto_data in data['crypto']:
                account = PaymentAccount(
                    account_type=PaymentAccountType.CRYPTO,
                    identifier_name=crypto_data.get('identifier_name', f"crypto_{len(created_accounts) + 1}"),
                    details=crypto_data,
                    status=PaymentAccountStatus.PENDING,
                    is_active=False
                )
                db.add(account)
                created_accounts.append(account)
        
        if not created_accounts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid accounts found in JSON. Expected 'upi', 'bank', and/or 'crypto' arrays"
            )
        
        db.commit()
        for account in created_accounts:
            db.refresh(account)
        
        logger.info(f"Uploaded {len(created_accounts)} payment accounts")
        return created_accounts
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/", response_model=List[PaymentAccountResponse])
def list_payment_accounts(
    account_type: Optional[PaymentAccountType] = None,
    status_filter: Optional[PaymentAccountStatus] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    """List all payment accounts (admin only)"""
    query = db.query(PaymentAccount)
    
    if account_type:
        query = query.filter(PaymentAccount.account_type == account_type)
    if status_filter:
        query = query.filter(PaymentAccount.status == status_filter)
    
    return query.order_by(PaymentAccount.created_at.desc()).all()

@router.post("/{account_id}/approve", response_model=PaymentAccountResponse)
def approve_account(
    account_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    """Approve a payment account"""
    account = db.query(PaymentAccount).filter(PaymentAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    from datetime import datetime
    account.status = PaymentAccountStatus.ACTIVE
    account.approved_at = datetime.utcnow()
    account.approved_by = 1  # Admin user ID
    
    db.commit()
    db.refresh(account)
    
    logger.info(f"Approved payment account {account_id}")
    return account

@router.post("/{account_id}/reject", response_model=PaymentAccountResponse)
def reject_account(
    account_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    """Reject a payment account"""
    account = db.query(PaymentAccount).filter(PaymentAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    account.status = PaymentAccountStatus.INACTIVE
    account.is_active = False
    
    db.commit()
    db.refresh(account)
    
    logger.info(f"Rejected payment account {account_id}")
    return account

@router.post("/{account_id}/activate", response_model=PaymentAccountResponse)
def activate_account(
    account_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    """Activate a payment account (deactivates others of same type)"""
    account = db.query(PaymentAccount).filter(PaymentAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.status != PaymentAccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account must be approved before activation"
        )
    
    # Deactivate all other accounts of the same type
    db.query(PaymentAccount).filter(
        PaymentAccount.account_type == account.account_type,
        PaymentAccount.id != account_id,
        PaymentAccount.is_active == True
    ).update({"is_active": False})
    
    # Activate this account
    account.is_active = True
    
    db.commit()
    db.refresh(account)
    
    logger.info(f"Activated payment account {account_id} (type: {account.account_type})")
    return account

@router.delete("/{account_id}", response_model=PaymentAccountResponse)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    """Delete a payment account"""
    account = db.query(PaymentAccount).filter(PaymentAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    db.delete(account)
    db.commit()
    
    logger.info(f"Deleted payment account {account_id}")
    return account


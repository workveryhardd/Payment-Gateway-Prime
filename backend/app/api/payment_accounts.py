from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from typing import List, Optional
import json
import logging
from app.models.payment_account import PaymentAccountType, PaymentAccountStatus
from app.schemas.payment_account import PaymentAccountResponse
from app.storage import repository

logger = logging.getLogger(__name__)

router = APIRouter()

# AUTHENTICATION DISABLED - Admin bypass
def get_current_admin_bypass(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Bypass admin authentication - returns dummy admin payload"""
    return {"sub": "1", "email": "vardiano@tech", "is_admin": True}

def _collect_payloads(data: dict) -> List[dict]:
    payloads: List[dict] = []

    if "upi" in data and isinstance(data["upi"], list):
        for entry in data["upi"]:
            payloads.append(
                {
                    "account_type": PaymentAccountType.UPI.value,
                    "identifier_name": entry.get("identifier_name"),
                    "details": entry,
                }
            )

    if "bank" in data and isinstance(data["bank"], list):
        for entry in data["bank"]:
            payloads.append(
                {
                    "account_type": PaymentAccountType.BANK.value,
                    "identifier_name": entry.get("identifier_name"),
                    "details": entry,
                }
            )

    if "crypto" in data and isinstance(data["crypto"], list):
        for entry in data["crypto"]:
            payloads.append(
                {
                    "account_type": PaymentAccountType.CRYPTO.value,
                    "identifier_name": entry.get("identifier_name"),
                    "details": entry,
                }
            )

    if "card" in data and isinstance(data["card"], list):
        for entry in data["card"]:
            payloads.append(
                {
                    "account_type": PaymentAccountType.CARD.value,
                    "identifier_name": entry.get("identifier_name"),
                    "details": entry,
                }
            )

    return payloads

@router.post("/upload", response_model=List[PaymentAccountResponse])
async def upload_payment_accounts(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_admin_bypass)
):
    """Upload payment accounts from JSON file"""
    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JSON file"
        )
    
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON must be an object with 'upi', 'bank', and/or 'crypto' arrays"
            )
        
        payloads = _collect_payloads(data)
        if not payloads:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid accounts found in JSON. Expected 'upi', 'bank', and/or 'crypto' arrays"
            )
        
        created_accounts = repository.create_payment_accounts(payloads)
        logger.info(f"Uploaded {len(created_accounts)} payment accounts")
        return created_accounts
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )

@router.get("/", response_model=List[PaymentAccountResponse])
def list_payment_accounts(
    account_type: Optional[PaymentAccountType] = None,
    status_filter: Optional[PaymentAccountStatus] = None,
    _: dict = Depends(get_current_admin_bypass)
):
    """List all payment accounts (admin only)"""
    return repository.list_payment_accounts(
        account_type=account_type,
        status=status_filter
    )

@router.post("/{account_id}/approve", response_model=PaymentAccountResponse)
def approve_account(
    account_id: int,
    _: dict = Depends(get_current_admin_bypass)
):
    """Approve a payment account"""
    account = repository.get_payment_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    updated = repository.approve_payment_account(account_id, approved_by=1)
    logger.info(f"Approved payment account {account_id}")
    return updated

@router.post("/{account_id}/reject", response_model=PaymentAccountResponse)
def reject_account(
    account_id: int,
    _: dict = Depends(get_current_admin_bypass)
):
    """Reject a payment account"""
    account = repository.reject_payment_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    logger.info(f"Rejected payment account {account_id}")
    return account

@router.post("/{account_id}/activate", response_model=PaymentAccountResponse)
def activate_account(
    account_id: int,
    _: dict = Depends(get_current_admin_bypass)
):
    """Activate a payment account (deactivates others of same type)"""
    account = repository.get_payment_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    try:
        updated = repository.activate_payment_account(account_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    logger.info(f"Activated payment account {account_id} (type: {updated['account_type']})")
    return updated

@router.delete("/{account_id}", response_model=PaymentAccountResponse)
def delete_account(
    account_id: int,
    _: dict = Depends(get_current_admin_bypass)
):
    """Delete a payment account"""
    account = repository.delete_payment_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    logger.info(f"Deleted payment account {account_id}")
    return account


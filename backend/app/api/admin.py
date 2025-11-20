from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.deposit import Deposit, DepositStatus
from app.models.incoming_ledger import IncomingLedger
from app.schemas.deposit import DepositResponse
from app.schemas.incoming_ledger import IncomingLedgerResponse
from app.utils.logger import logger

router = APIRouter()

# AUTHENTICATION DISABLED - Admin endpoints are open for now
# To re-enable: uncomment get_current_admin_real and change Depends(get_current_admin_bypass) to Depends(get_current_admin_real)

def get_current_admin_bypass(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Bypass admin authentication - returns dummy admin payload"""
    return {"sub": "1", "email": "admin@example.com", "is_admin": True}

def get_current_admin_real(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Real admin authentication function - currently disabled"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    if not payload.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return payload

# Use bypass for now - change to get_current_admin_real to enable auth
get_current_admin = get_current_admin_bypass

@router.get("/deposits", response_model=List[DepositResponse])
def list_deposits(
    status_filter: Optional[DepositStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    
    query = db.query(Deposit)
    if status_filter:
        query = query.filter(Deposit.status == status_filter)
    
    deposits = query.order_by(Deposit.created_at.desc()).all()
    return deposits

@router.post("/deposits/{deposit_id}/approve", response_model=DepositResponse)
def approve_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    from datetime import datetime
    deposit.status = DepositStatus.SUCCESS
    deposit.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(deposit)
    
    logger.info(f"Admin approved deposit {deposit_id}")
    return deposit

@router.post("/deposits/{deposit_id}/reject", response_model=DepositResponse)
def reject_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    deposit.status = DepositStatus.FAILED
    db.commit()
    db.refresh(deposit)
    
    logger.info(f"Admin rejected deposit {deposit_id}")
    return deposit

@router.get("/incoming-ledger", response_model=List[IncomingLedgerResponse])
def list_incoming_ledger(
    matched: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_bypass)
):
    
    query = db.query(IncomingLedger)
    if matched is not None:
        query = query.filter(IncomingLedger.matched == matched)
    
    entries = query.order_by(IncomingLedger.created_at.desc()).all()
    return entries


from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from typing import List, Optional
from app.core.security import decode_access_token
from app.models.deposit import DepositStatus
from app.schemas.deposit import DepositResponse
from app.schemas.incoming_ledger import IncomingLedgerResponse
from app.utils.logger import logger
from app.storage import repository

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
    _: dict = Depends(get_current_admin_bypass)
):
    return repository.list_deposits(status=status_filter)

@router.post("/deposits/{deposit_id}/approve", response_model=DepositResponse)
def approve_deposit(
    deposit_id: int,
    _: dict = Depends(get_current_admin_bypass)
):
    deposit = repository.get_deposit(deposit_id)
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    from datetime import datetime
    updated = repository.update_deposit(
        deposit_id,
        status=DepositStatus.SUCCESS.value,
        verified_at=datetime.utcnow().isoformat(),
    )
    logger.info(f"Admin approved deposit {deposit_id}")
    return updated

@router.post("/deposits/{deposit_id}/reject", response_model=DepositResponse)
def reject_deposit(
    deposit_id: int,
    _: dict = Depends(get_current_admin_bypass)
):
    deposit = repository.get_deposit(deposit_id)
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    updated = repository.update_deposit(
        deposit_id,
        status=DepositStatus.FAILED.value,
    )
    logger.info(f"Admin rejected deposit {deposit_id}")
    return updated

@router.get("/incoming-ledger", response_model=List[IncomingLedgerResponse])
def list_incoming_ledger(
    matched: Optional[bool] = Query(None),
    _: dict = Depends(get_current_admin_bypass)
):
    return repository.list_incoming_ledger(matched=matched)


from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.deposit import Deposit
from app.schemas.deposit import DepositCreate, DepositSubmitProof, DepositResponse
from app.utils.logger import logger

router = APIRouter()

# AUTHENTICATION DISABLED - Using default user_id for now
# To re-enable: uncomment get_current_user_id_real and change Depends(get_current_user_id_bypass) to Depends(get_current_user_id_real)

def get_current_user_id_bypass(authorization: Optional[str] = Header(None, alias="Authorization")) -> int:
    """Bypass authentication - returns default user_id 1"""
    return 1  # Default user ID when auth is disabled

def get_current_user_id_real(authorization: Optional[str] = Header(None, alias="Authorization")) -> int:
    """Real authentication function - currently disabled"""
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
    return int(payload["sub"])

# Use bypass for now - change to get_current_user_id_real to enable auth
get_current_user_id = get_current_user_id_bypass

@router.post("/create", response_model=DepositResponse)
def create_deposit(
    deposit_data: DepositCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    
    new_deposit = Deposit(
        user_id=user_id,
        method=deposit_data.method,
        amount=deposit_data.amount,
        status="PENDING"
    )
    db.add(new_deposit)
    db.commit()
    db.refresh(new_deposit)
    
    logger.info(f"Created deposit {new_deposit.id} for user {user_id}")
    return new_deposit

@router.post("/submit-proof", response_model=DepositResponse)
def submit_proof(
    proof_data: DepositSubmitProof,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    
    deposit = db.query(Deposit).filter(Deposit.id == proof_data.deposit_id).first()
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    # AUTHENTICATION DISABLED - Commented out user check
    # if deposit.user_id != user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to update this deposit"
    #     )
    
    if deposit.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit is not in PENDING status"
        )
    
    # Check if UTR/hash is already used
    existing = db.query(Deposit).filter(
        Deposit.utr_or_hash == proof_data.utr_or_hash,
        Deposit.id != deposit.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UTR/hash already used"
        )
    
    deposit.utr_or_hash = proof_data.utr_or_hash
    db.commit()
    db.refresh(deposit)
    
    logger.info(f"Updated deposit {deposit.id} with UTR/hash")
    return deposit

@router.get("/my", response_model=List[DepositResponse])
def get_my_deposits(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    
    deposits = db.query(Deposit).filter(Deposit.user_id == user_id).order_by(Deposit.created_at.desc()).all()
    return deposits


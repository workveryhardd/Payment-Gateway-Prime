from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List, Optional
from app.core.security import decode_access_token
from app.models.deposit import DepositStatus
from app.schemas.deposit import DepositCreate, DepositSubmitProof, DepositResponse
from app.utils.logger import logger
from app.storage import repository

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
    user_id: int = Depends(get_current_user_id)
):
    new_deposit = repository.create_deposit_record(
        user_id=user_id,
        method=deposit_data.method,
        amount=deposit_data.amount,
    )
    logger.info(f"Created deposit {new_deposit['id']} for user {user_id}")
    return new_deposit

@router.post("/submit-proof", response_model=DepositResponse)
def submit_proof(
    proof_data: DepositSubmitProof,
    user_id: int = Depends(get_current_user_id)
):
    deposit = repository.get_deposit(proof_data.deposit_id)
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit["status"] != DepositStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit is not in PENDING status"
        )
    
    if repository.utr_exists(proof_data.utr_or_hash, exclude_deposit_id=deposit["id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UTR/hash already used"
        )
    
    updated = repository.update_deposit(deposit["id"], utr_or_hash=proof_data.utr_or_hash)
    logger.info(f"Updated deposit {deposit['id']} with UTR/hash")
    return updated

@router.get("/my", response_model=List[DepositResponse])
def get_my_deposits(
    user_id: int = Depends(get_current_user_id)
):
    return repository.list_deposits(user_id=user_id)


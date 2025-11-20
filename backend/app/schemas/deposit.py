from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.deposit import DepositMethod, DepositStatus

class DepositCreate(BaseModel):
    method: DepositMethod
    amount: float

class DepositSubmitProof(BaseModel):
    deposit_id: int
    utr_or_hash: str

class DepositResponse(BaseModel):
    id: int
    user_id: int
    method: DepositMethod
    amount: float
    utr_or_hash: Optional[str]
    status: DepositStatus
    meta_data: Optional[dict]  # Renamed from metadata to avoid SQLAlchemy conflict
    created_at: datetime
    verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


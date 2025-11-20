from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.payment_account import PaymentAccountType, PaymentAccountStatus

class PaymentAccountCreate(BaseModel):
    account_type: PaymentAccountType
    identifier_name: str
    details: Dict[str, Any]  # JSON with all account details

class PaymentAccountResponse(BaseModel):
    id: int
    account_type: PaymentAccountType
    identifier_name: str
    status: PaymentAccountStatus
    details: Dict[str, Any]
    is_active: bool
    created_at: datetime
    approved_at: Optional[datetime]
    approved_by: Optional[int]
    
    class Config:
        from_attributes = True

class PaymentAccountUpdate(BaseModel):
    status: Optional[PaymentAccountStatus] = None
    is_active: Optional[bool] = None

class PaymentAccountBulkUpload(BaseModel):
    accounts: list[PaymentAccountCreate]


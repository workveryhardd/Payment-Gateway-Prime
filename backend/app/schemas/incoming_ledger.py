from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.incoming_ledger import LedgerSource, LedgerMethod

class IncomingLedgerCreate(BaseModel):
    source: LedgerSource
    method: LedgerMethod
    utr_or_hash: str
    amount: float
    sender: Optional[str] = None
    timestamp: datetime
    raw_data: Optional[dict] = None

class IncomingLedgerResponse(BaseModel):
    id: int
    source: LedgerSource
    method: LedgerMethod
    utr_or_hash: str
    amount: float
    sender: Optional[str]
    timestamp: datetime
    raw_data: Optional[dict]
    matched: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


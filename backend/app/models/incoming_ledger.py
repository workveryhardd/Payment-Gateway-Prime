from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class LedgerSource(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    BLOCKCHAIN = "BLOCKCHAIN"

class LedgerMethod(str, enum.Enum):
    UPI = "UPI"
    BANK = "BANK"
    CRYPTO = "CRYPTO"

class IncomingLedger(Base):
    __tablename__ = "incoming_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(SQLEnum(LedgerSource), nullable=False)
    method = Column(SQLEnum(LedgerMethod), nullable=False)
    utr_or_hash = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    sender = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    raw_data = Column(JSON, nullable=True)
    matched = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


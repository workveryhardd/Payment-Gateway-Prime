from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class PaymentAccountType(str, enum.Enum):
    UPI = "UPI"
    BANK = "BANK"
    CRYPTO = "CRYPTO"

class PaymentAccountStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class PaymentAccount(Base):
    __tablename__ = "payment_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_type = Column(SQLEnum(PaymentAccountType), nullable=False, index=True)
    identifier_name = Column(String, nullable=False)  # e.g., "id1", "main_upi", "backup_bank"
    status = Column(SQLEnum(PaymentAccountStatus), default=PaymentAccountStatus.PENDING, index=True)
    details = Column(JSON, nullable=False)  # All account details stored as JSON
    is_active = Column(Boolean, default=False, index=True)  # Only one active per type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, nullable=True)  # Admin user ID


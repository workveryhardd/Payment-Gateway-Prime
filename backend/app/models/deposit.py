from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class DepositMethod(str, enum.Enum):
    UPI = "UPI"
    BANK = "BANK"
    CRYPTO = "CRYPTO"

class DepositStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FLAGGED = "FLAGGED"

class Deposit(Base):
    __tablename__ = "deposits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method = Column(SQLEnum(DepositMethod), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    utr_or_hash = Column(String, nullable=True, index=True)
    status = Column(SQLEnum(DepositStatus), default=DepositStatus.PENDING, index=True)
    meta_data = Column("metadata", JSON, nullable=True)  # Using "metadata" as column name but "meta_data" as attribute
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", backref="deposits")


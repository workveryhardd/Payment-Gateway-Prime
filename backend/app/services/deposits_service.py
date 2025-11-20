from sqlalchemy.orm import Session
from app.models.deposit import Deposit
from app.schemas.deposit import DepositCreate

def create_deposit(db: Session, user_id: int, deposit_data: DepositCreate) -> Deposit:
    """Create a new deposit record."""
    deposit = Deposit(
        user_id=user_id,
        method=deposit_data.method,
        amount=deposit_data.amount,
        status="PENDING"
    )
    db.add(deposit)
    db.commit()
    db.refresh(deposit)
    return deposit


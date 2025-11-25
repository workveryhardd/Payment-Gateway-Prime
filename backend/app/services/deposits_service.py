from app.schemas.deposit import DepositCreate
from app.storage import repository

def create_deposit(user_id: int, deposit_data: DepositCreate):
    """Create a new deposit record via the JSON repository."""
    return repository.create_deposit_record(
        user_id=user_id,
        method=deposit_data.method,
        amount=deposit_data.amount,
    )


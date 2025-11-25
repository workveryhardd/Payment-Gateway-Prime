import enum

class DepositMethod(str, enum.Enum):
    UPI = "UPI"
    BANK = "BANK"
    CRYPTO = "CRYPTO"
    CARD = "CARD"
    PAYPAL = "PAYPAL"

class DepositStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FLAGGED = "FLAGGED"


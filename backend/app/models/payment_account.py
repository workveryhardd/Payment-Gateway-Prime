import enum

class PaymentAccountType(str, enum.Enum):
    UPI = "UPI"
    BANK = "BANK"
    CRYPTO = "CRYPTO"
    CARD = "CARD"
    PAYPAL = "PAYPAL"

class PaymentAccountStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


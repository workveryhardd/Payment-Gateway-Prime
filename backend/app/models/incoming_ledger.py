import enum

class LedgerSource(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    BLOCKCHAIN = "BLOCKCHAIN"

class LedgerMethod(str, enum.Enum):
    UPI = "UPI"
    BANK = "BANK"
    CRYPTO = "CRYPTO"
    CARD = "CARD"


from datetime import datetime
from app.schemas.incoming_ledger import IncomingLedgerCreate
from app.models.incoming_ledger import LedgerSource, LedgerMethod

def parse_trc20_tx(json_data: dict) -> IncomingLedgerCreate:
    """
    Parse TRC20 transaction JSON data.
    """
    txid = json_data.get("txid", "")
    amount = float(json_data.get("amount", 0))
    token = json_data.get("token", "")
    network = json_data.get("network", "")
    to_address = json_data.get("to", "")
    from_address = json_data.get("from", "")
    
    return IncomingLedgerCreate(
        source=LedgerSource.BLOCKCHAIN,
        method=LedgerMethod.CRYPTO,
        utr_or_hash=txid,
        amount=amount,
        sender=from_address,
        timestamp=datetime.utcnow(),
        raw_data=json_data
    )

def parse_erc20_tx(json_data: dict) -> IncomingLedgerCreate:
    """
    Parse ERC20 transaction JSON data.
    """
    tx_hash = json_data.get("tx_hash", "")
    amount = float(json_data.get("amount", 0))
    token = json_data.get("token", "")
    network = json_data.get("network", "")
    to_address = json_data.get("to", "")
    from_address = json_data.get("from", "")
    
    return IncomingLedgerCreate(
        source=LedgerSource.BLOCKCHAIN,
        method=LedgerMethod.CRYPTO,
        utr_or_hash=tx_hash,
        amount=amount,
        sender=from_address,
        timestamp=datetime.utcnow(),
        raw_data=json_data
    )


from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.payment_account import PaymentAccount, PaymentAccountType, PaymentAccountStatus

router = APIRouter()

def get_active_payment_accounts(db: Session):
    """Get active payment accounts from database"""
    active_accounts = db.query(PaymentAccount).filter(
        PaymentAccount.is_active == True,
        PaymentAccount.status == PaymentAccountStatus.ACTIVE
    ).all()
    
    result = {
        "upi": None,
        "bank": None,
        "crypto": None
    }
    
    for account in active_accounts:
        if account.account_type == PaymentAccountType.UPI:
            result["upi"] = {
                "identifier_name": account.identifier_name,
                **account.details
            }
        elif account.account_type == PaymentAccountType.BANK:
            result["bank"] = {
                "identifier_name": account.identifier_name,
                **account.details
            }
        elif account.account_type == PaymentAccountType.CRYPTO:
            result["crypto"] = {
                "identifier_name": account.identifier_name,
                **account.details
            }
    
    return result

@router.get("/payment-instructions")
def get_payment_instructions(db: Session = Depends(get_db)):
    """Get active payment instructions for all methods"""
    active_accounts = get_active_payment_accounts(db)
    
    # Fallback to defaults if no active accounts
    if not active_accounts["upi"]:
        active_accounts["upi"] = {
            "upi_id": "yourupi@bank",
            "payee_name": "Your Business Name",
            "identifier_name": "default"
        }
    
    if not active_accounts["bank"]:
        active_accounts["bank"] = {
            "account_number": "123456789012",
            "ifsc": "BANK0001234",
            "bank_name": "Bank Name",
            "branch": "Branch Name",
            "identifier_name": "default"
        }
    
    if not active_accounts["crypto"]:
        active_accounts["crypto"] = {
            "btc": "bc1qexamplebtcaddress000000000000000000",
            "eth": "0xExampleEthereumAddress0000000000000000000000",
            "usdt_trc20": "TYExampleTronAddress0000000000000000",
            "usdt_erc20": "0xExampleERC20Address00000000000000000000",
            "usdt_bep20": "0xExampleBSCAddress000000000000000000000",
            "identifier_name": "default"
        }
    
    return active_accounts

@router.get("/qr-code")
def get_qr_code(db: Session = Depends(get_db)):
    """Serve QR code image from active UPI account"""
    active_upi = db.query(PaymentAccount).filter(
        PaymentAccount.account_type == PaymentAccountType.UPI,
        PaymentAccount.is_active == True,
        PaymentAccount.status == PaymentAccountStatus.ACTIVE
    ).first()
    
    if active_upi and active_upi.details.get("qr_location"):
        qr_location = active_upi.details["qr_location"]
        # Handle both absolute and relative paths
        if Path(qr_location).is_absolute():
            qr_path = Path(qr_location)
        else:
            # Relative path from project root
            qr_path = Path(__file__).parent.parent.parent.parent / qr_location
        if qr_path.exists():
            return FileResponse(qr_path, media_type="image/jpeg")
    
    # Fallback to default location
    qr_path = Path(__file__).parent.parent / "assets" / "qr.jpg"
    if qr_path.exists():
        return FileResponse(qr_path, media_type="image/jpeg")
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )


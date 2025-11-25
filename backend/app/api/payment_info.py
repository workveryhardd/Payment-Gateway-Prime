from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
from app.storage import repository

router = APIRouter()

def get_active_payment_accounts():
    """Get active payment accounts from JSON store."""
    return repository.get_active_accounts()

@router.get("/payment-instructions")
def get_payment_instructions():
    """Get active payment instructions for all methods"""
    active_accounts = get_active_payment_accounts()
    
    # Ensure all expected keys exist
    active_accounts.setdefault("card", None)
    active_accounts.setdefault("paypal", None)
    
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

    if not active_accounts["card"]:
        active_accounts["card"] = {
            "provider": "Card Gateway",
            "instructions": "Share payment link sent by support.",
            "identifier_name": "default"
        }
    
    if not active_accounts["paypal"]:
        active_accounts["paypal"] = {
            "enabled": True,
            "message": "Pay securely with your preferred payment method",
            "identifier_name": "default"
        }
    
    return active_accounts

@router.get("/qr-code")
def get_qr_code():
    """Serve QR code image from active UPI account"""
    active_upi = repository.get_active_accounts().get("upi")
    
    if active_upi and active_upi.get("qr_location"):
        qr_location = active_upi["qr_location"]
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


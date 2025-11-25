"""
PayPal payment API endpoints
Seamless integration - no PayPal branding visible to clients
"""
from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from pydantic import BaseModel
from app.services.paypal_service import paypal_service
from app.storage import repository
from app.models.deposit import DepositStatus
from app.utils.logger import logger

router = APIRouter()


class PayPalPaymentCreate(BaseModel):
    amount: float
    currency: str = "USD"
    description: str = "Payment"
    deposit_id: int
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None


class PayPalPaymentExecute(BaseModel):
    payment_id: str
    payer_id: str
    deposit_id: int


class PayPalPaymentResponse(BaseModel):
    payment_id: str
    approval_url: str
    state: str
    deposit_id: int


# AUTHENTICATION DISABLED - Using default user_id for now
def get_current_user_id_bypass(authorization: Optional[str] = Header(None, alias="Authorization")) -> int:
    """Bypass authentication - returns default user_id 1"""
    return 1


@router.post("/create", response_model=PayPalPaymentResponse)
async def create_paypal_payment(
    payment_data: PayPalPaymentCreate,
    user_id: int = Depends(get_current_user_id_bypass)
):
    """
    Create a secure payment for a deposit
    Returns approval URL that client can use to complete payment
    Completely seamless - no third-party branding visible
    """
    # Verify deposit exists and belongs to user
    deposit = repository.get_deposit(payment_data.deposit_id)
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if deposit["status"] != DepositStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit is not in PENDING status"
        )
    
    # Verify amount matches
    if abs(float(deposit["amount"]) - payment_data.amount) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount mismatch"
        )
    
    try:
        # Create PayPal payment
        paypal_result = paypal_service.create_payment(
            amount=payment_data.amount,
            currency=payment_data.currency,
            description=payment_data.description,
            return_url=payment_data.return_url,
            cancel_url=payment_data.cancel_url
        )
        
        # Store PayPal payment ID in deposit metadata
        meta_data = deposit.get("meta_data") or {}
        meta_data["paypal_payment_id"] = paypal_result["payment_id"]
        repository.update_deposit(
            payment_data.deposit_id,
            meta_data=meta_data
        )
        
        logger.info(f"PayPal payment created for deposit {payment_data.deposit_id}: {paypal_result['payment_id']}")
        
        return PayPalPaymentResponse(
            payment_id=paypal_result["payment_id"],
            approval_url=paypal_result["approval_url"],
            state=paypal_result["state"],
            deposit_id=payment_data.deposit_id
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to create PayPal payment: {error_msg}")
        # Provide more helpful error message
        if "400" in error_msg or "Bad Request" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment gateway configuration error. Please check credentials and API settings."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {error_msg}"
        )


@router.post("/execute")
async def execute_paypal_payment(
    execute_data: PayPalPaymentExecute,
    user_id: int = Depends(get_current_user_id_bypass)
):
    """
    Execute a PayPal payment after user approval
    This completes the payment and updates deposit status
    """
    # Verify deposit exists
    deposit = repository.get_deposit(execute_data.deposit_id)
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Verify PayPal payment ID matches
    meta_data = deposit.get("meta_data") or {}
    stored_payment_id = meta_data.get("paypal_payment_id")
    if stored_payment_id != execute_data.payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment ID mismatch"
        )
    
    try:
        # Execute PayPal payment
        result = paypal_service.execute_payment(
            payment_id=execute_data.payment_id,
            payer_id=execute_data.payer_id
        )
        
        if result["success"]:
            # Update deposit status to SUCCESS with chargeback protection data
            repository.update_deposit(
                execute_data.deposit_id,
                status=DepositStatus.SUCCESS.value,
                utr_or_hash=execute_data.payment_id,
                meta_data={
                    **meta_data,
                    "paypal_payer_id": execute_data.payer_id,
                    "paypal_executed": True,
                    "paypal_sale_id": result.get("sale_id"),  # For chargeback tracking
                    "paypal_captured": result.get("captured", False),  # Immediate capture flag
                    "chargeback_protection": "immediate_capture"
                }
            )
            logger.info(f"Payment executed successfully for deposit {execute_data.deposit_id}, sale_id: {result.get('sale_id')}")
            return {
                "success": True,
                "message": "Payment completed successfully",
                "payment_id": execute_data.payment_id,
                "sale_id": result.get("sale_id"),  # Return sale_id for tracking
                "deposit_id": execute_data.deposit_id,
                "captured": result.get("captured", False)
            }
        else:
            # Payment failed
            repository.update_deposit(
                execute_data.deposit_id,
                status=DepositStatus.FAILED.value
            )
            logger.warning(f"PayPal payment failed for deposit {execute_data.deposit_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment execution failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute PayPal payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute payment: {str(e)}"
        )


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    user_id: int = Depends(get_current_user_id_bypass)
):
    """Get status of a PayPal payment"""
    try:
        payment_details = paypal_service.get_payment_details(payment_id)
        return {
            "payment_id": payment_id,
            "state": payment_details.get("state"),
            "details": payment_details
        }
    except Exception as e:
        logger.error(f"Failed to get PayPal payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment status: {str(e)}"
        )


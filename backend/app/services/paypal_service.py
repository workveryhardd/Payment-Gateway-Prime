"""
PayPal integration service - seamless payment processing
Client-facing interface hides PayPal branding
"""
import requests
from typing import Dict, Optional
from app.core.config import settings
from app.utils.logger import logger


class PayPalService:
    """PayPal service with white-label integration"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.secret = settings.PAYPAL_SECRET
        self.mode = settings.PAYPAL_MODE
        self.base_url = "https://api-m.paypal.com" if self.mode == "live" else "https://api-m.sandbox.paypal.com"
        self._access_token: Optional[str] = None
    
    def _get_access_token(self) -> str:
        """Get PayPal OAuth access token"""
        if self._access_token:
            return self._access_token
        
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.secret),
                timeout=10
            )
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            logger.info("PayPal access token obtained successfully")
            return self._access_token
        except Exception as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise
    
    def create_payment(self, amount: float, currency: str = "USD", description: str = "Payment", return_url: str = None, cancel_url: str = None) -> Dict:
        """
        Create a PayPal payment
        Returns payment approval URL that can be used to redirect user
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/v1/payments/payment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Default return URLs if not provided (will be overridden by frontend)
        if not return_url:
            return_url = "https://payment-gateway-prime-pp3zpnu9b-workveryhardds-projects.vercel.app/deposit?payment_success=true"
        if not cancel_url:
            cancel_url = "https://payment-gateway-prime-pp3zpnu9b-workveryhardds-projects.vercel.app/deposit?payment_cancelled=true"
        
        # Validate URLs
        if not return_url.startswith(("http://", "https://")):
            raise ValueError("return_url must be a valid HTTP/HTTPS URL")
        if not cancel_url.startswith(("http://", "https://")):
            raise ValueError("cancel_url must be a valid HTTP/HTTPS URL")
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if amount > 1000000:  # PayPal limit
            raise ValueError("Amount exceeds maximum limit")
        
        # Simplified payload - PayPal v1 API minimum required fields
        payload = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": f"{amount:.2f}",
                    "currency": currency
                },
                "description": description[:127] if len(description) > 127 else description
            }],
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Log response for debugging
            if response.status_code != 201:
                error_detail = response.text
                logger.error(f"PayPal API error {response.status_code}: {error_detail}")
                raise Exception(f"PayPal API error: {response.status_code} - {error_detail}")
            
            payment_data = response.json()
            
            # Extract approval URL (user will be redirected here)
            approval_url = None
            for link in payment_data.get("links", []):
                if link.get("rel") == "approval_url":
                    approval_url = link.get("href")
                    break
            
            if not approval_url:
                logger.error(f"No approval URL in PayPal response: {payment_data}")
                raise Exception("No approval URL received from payment gateway")
            
            logger.info(f"PayPal payment created: {payment_data.get('id')}")
            return {
                "payment_id": payment_data.get("id"),
                "approval_url": approval_url,
                "state": payment_data.get("state")
            }
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            logger.error(f"PayPal HTTP error: {error_detail}")
            raise Exception(f"Payment gateway error: {error_detail}")
        except Exception as e:
            logger.error(f"Failed to create PayPal payment: {e}")
            raise
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Dict:
        """
        Execute a PayPal payment after user approval
        This completes the payment transaction with immediate capture
        Chargeback protection: Uses immediate sale intent and captures funds instantly
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/v1/payments/payment/{payment_id}/execute"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "payer_id": payer_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            payment_data = response.json()
            
            # Check if payment was successful
            state = payment_data.get("state")
            transactions = payment_data.get("transactions", [])
            amount = None
            sale_id = None
            
            if transactions:
                amount_info = transactions[0].get("amount", {})
                amount = float(amount_info.get("total", 0))
                
                # Get sale ID for chargeback tracking
                related_resources = transactions[0].get("related_resources", [])
                for resource in related_resources:
                    if "sale" in resource:
                        sale_id = resource["sale"].get("id")
                        sale_state = resource["sale"].get("state")
                        # Verify sale is completed (not pending)
                        if sale_state != "completed":
                            logger.warning(f"PayPal sale not completed: {sale_state}")
            
            # Additional chargeback protection: Verify payment is fully processed
            is_approved = state == "approved"
            if is_approved and sale_id:
                # Payment is captured immediately - reduces chargeback window
                logger.info(f"PayPal payment executed and captured: {payment_id}, sale: {sale_id}")
            
            logger.info(f"PayPal payment executed: {payment_id}, state: {state}")
            return {
                "payment_id": payment_id,
                "sale_id": sale_id,
                "state": state,
                "amount": amount,
                "success": is_approved,
                "captured": sale_id is not None  # Funds captured immediately
            }
        except Exception as e:
            logger.error(f"Failed to execute PayPal payment: {e}")
            raise
    
    def get_payment_details(self, payment_id: str) -> Dict:
        """Get details of a PayPal payment"""
        token = self._get_access_token()
        
        url = f"{self.base_url}/v1/payments/payment/{payment_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get PayPal payment details: {e}")
            raise


# Global instance
paypal_service = PayPalService()


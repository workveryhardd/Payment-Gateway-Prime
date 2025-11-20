import re
from datetime import datetime
from typing import List
from app.schemas.incoming_ledger import IncomingLedgerCreate
from app.models.incoming_ledger import LedgerSource, LedgerMethod

def parse_email_text(text: str) -> List[IncomingLedgerCreate]:
    """
    Parse email text to extract ledger entries.
    Currently supports the sample formats provided.
    """
    entries = []
    text_lower = text.lower()
    
    # Check if it's a UPI credit email
    if "upi credit" in text_lower or "received via upi" in text_lower:
        # Extract amount
        amount_match = re.search(r'rs\s+([\d,]+\.?\d*)', text_lower)
        if not amount_match:
            amount_match = re.search(r'₹\s*([\d,]+\.?\d*)', text_lower)
        
        # Extract reference number
        ref_match = re.search(r'reference\s+number[:\s]+(\d+)', text_lower, re.IGNORECASE)
        if not ref_match:
            ref_match = re.search(r'ref\s+(\d+)', text_lower, re.IGNORECASE)
        
        # Extract sender
        sender_match = re.search(r'from[:\s]+([A-Z\s]+)', text, re.IGNORECASE)
        
        # Extract timestamp
        time_match = re.search(r'time[:\s]+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', text)
        
        if amount_match and ref_match:
            amount = float(amount_match.group(1).replace(',', ''))
            utr = ref_match.group(1)
            sender = sender_match.group(1).strip() if sender_match else None
            
            timestamp = datetime.utcnow()
            if time_match:
                try:
                    timestamp = datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            entries.append(IncomingLedgerCreate(
                source=LedgerSource.EMAIL,
                method=LedgerMethod.UPI,
                utr_or_hash=utr,
                amount=amount,
                sender=sender,
                timestamp=timestamp,
                raw_data={"email_text": text}
            ))
    
    # Check if it's an IMPS credit email
    elif "imps credit" in text_lower or "imps ref" in text_lower:
        # Extract amount
        amount_match = re.search(r'inr\s+([\d,]+\.?\d*)', text_lower, re.IGNORECASE)
        if not amount_match:
            amount_match = re.search(r'rs\s+([\d,]+\.?\d*)', text_lower)
        
        # Extract IMPS reference
        ref_match = re.search(r'imps\s+ref\s+no[:\s]+(\d+)', text_lower, re.IGNORECASE)
        if not ref_match:
            ref_match = re.search(r'ref\s+no[:\s]+(\d+)', text_lower, re.IGNORECASE)
        
        # Extract sender
        sender_match = re.search(r'from[:\s]+([A-Z\s]+)', text, re.IGNORECASE)
        
        # Extract timestamp
        time_match = re.search(r'time[:\s]+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', text)
        
        if amount_match and ref_match:
            amount = float(amount_match.group(1).replace(',', ''))
            utr = ref_match.group(1)
            sender = sender_match.group(1).strip() if sender_match else None
            
            timestamp = datetime.utcnow()
            if time_match:
                try:
                    timestamp = datetime.strptime(time_match.group(1), "%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            entries.append(IncomingLedgerCreate(
                source=LedgerSource.EMAIL,
                method=LedgerMethod.BANK,
                utr_or_hash=utr,
                amount=amount,
                sender=sender,
                timestamp=timestamp,
                raw_data={"email_text": text}
            ))
    
    return entries


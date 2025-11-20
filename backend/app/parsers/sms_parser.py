import re
from datetime import datetime
from typing import List
from app.schemas.incoming_ledger import IncomingLedgerCreate
from app.models.incoming_ledger import LedgerSource, LedgerMethod

def parse_sms_text(text: str) -> List[IncomingLedgerCreate]:
    """
    Parse SMS text to extract ledger entries.
    Currently supports the sample formats provided.
    """
    entries = []
    text_lower = text.lower()
    
    # Check if it's a UPI SMS
    if "received via upi" in text_lower or "upi ref" in text_lower:
        # Extract amount
        amount_match = re.search(r'rs\s+([\d,]+\.?\d*)', text_lower)
        
        # Extract reference number
        ref_match = re.search(r'ref\s+(\d+)', text_lower, re.IGNORECASE)
        
        # Extract sender
        sender_match = re.search(r'from\s+([A-Z\s]+)', text, re.IGNORECASE)
        
        # Extract date and time
        date_match = re.search(r'(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2})', text)
        
        if amount_match and ref_match:
            amount = float(amount_match.group(1).replace(',', ''))
            utr = ref_match.group(1)
            sender = sender_match.group(1).strip() if sender_match else None
            
            timestamp = datetime.utcnow()
            if date_match:
                try:
                    date_str = date_match.group(1)
                    time_str = date_match.group(2)
                    # Convert DD-MM-YYYY to YYYY-MM-DD
                    day, month, year = date_str.split('-')
                    timestamp = datetime.strptime(f"{year}-{month}-{day} {time_str}", "%Y-%m-%d %H:%M")
                except:
                    pass
            
            entries.append(IncomingLedgerCreate(
                source=LedgerSource.SMS,
                method=LedgerMethod.UPI,
                utr_or_hash=utr,
                amount=amount,
                sender=sender,
                timestamp=timestamp,
                raw_data={"sms_text": text}
            ))
    
    # Check if it's an IMPS SMS
    elif "imps credit" in text_lower or "imps" in text_lower:
        # Extract amount
        amount_match = re.search(r'rs\s+([\d,]+\.?\d*)', text_lower)
        
        # Extract reference number
        ref_match = re.search(r'ref\s+(\d+)', text_lower, re.IGNORECASE)
        
        # Extract sender
        sender_match = re.search(r'from\s+([A-Z\s]+)', text, re.IGNORECASE)
        
        # Extract date and time
        date_match = re.search(r'(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2})', text)
        
        if amount_match and ref_match:
            amount = float(amount_match.group(1).replace(',', ''))
            utr = ref_match.group(1)
            sender = sender_match.group(1).strip() if sender_match else None
            
            timestamp = datetime.utcnow()
            if date_match:
                try:
                    date_str = date_match.group(1)
                    time_str = date_match.group(2)
                    day, month, year = date_str.split('-')
                    timestamp = datetime.strptime(f"{year}-{month}-{day} {time_str}", "%Y-%m-%d %H:%M")
                except:
                    pass
            
            entries.append(IncomingLedgerCreate(
                source=LedgerSource.SMS,
                method=LedgerMethod.BANK,
                utr_or_hash=utr,
                amount=amount,
                sender=sender,
                timestamp=timestamp,
                raw_data={"sms_text": text}
            ))
    
    return entries


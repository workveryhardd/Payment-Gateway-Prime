from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.deposit import Deposit, DepositStatus
from app.models.incoming_ledger import IncomingLedger
from app.utils.logger import logger
from app.core.celery_app import celery_app

def match_pending_deposits(db: Session):
    """
    Match pending deposits with incoming ledger entries.
    """
    # Get all pending deposits with UTR/hash
    pending_deposits = db.query(Deposit).filter(
        Deposit.status == DepositStatus.PENDING,
        Deposit.utr_or_hash.isnot(None)
    ).all()
    
    matched_count = 0
    
    for deposit in pending_deposits:
        # Find matching ledger entry
        ledger_entry = db.query(IncomingLedger).filter(
            IncomingLedger.utr_or_hash == deposit.utr_or_hash,
            IncomingLedger.method == deposit.method.value,
            IncomingLedger.matched == False
        ).first()
        
        if ledger_entry:
            # Check amount match (with small tolerance for floating point)
            amount_diff = abs(float(deposit.amount) - float(ledger_entry.amount))
            if amount_diff < 0.01:  # 1 paisa tolerance
                # Check timestamp difference (within 30 minutes)
                time_diff = abs((deposit.created_at - ledger_entry.timestamp).total_seconds())
                if time_diff < 1800:  # 30 minutes
                    # Match found!
                    deposit.status = DepositStatus.SUCCESS
                    deposit.verified_at = datetime.utcnow()
                    ledger_entry.matched = True
                    matched_count += 1
                    logger.info(f"Matched deposit {deposit.id} with ledger entry {ledger_entry.id}")
    
    db.commit()
    logger.info(f"Matched {matched_count} deposits")
    return matched_count

def flag_stale_deposits(db: Session):
    """
    Flag deposits that have been pending for more than 60 minutes
    with UTR/hash set but no matching ledger entry.
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=60)
    
    stale_deposits = db.query(Deposit).filter(
        Deposit.status == DepositStatus.PENDING,
        Deposit.utr_or_hash.isnot(None),
        Deposit.created_at < cutoff_time
    ).all()
    
    flagged_count = 0
    
    for deposit in stale_deposits:
        # Check if there's a matching ledger entry
        ledger_entry = db.query(IncomingLedger).filter(
            IncomingLedger.utr_or_hash == deposit.utr_or_hash,
            IncomingLedger.method == deposit.method.value
        ).first()
        
        if not ledger_entry:
            deposit.status = DepositStatus.FLAGGED
            flagged_count += 1
            logger.info(f"Flagged stale deposit {deposit.id}")
    
    db.commit()
    logger.info(f"Flagged {flagged_count} stale deposits")
    return flagged_count

@celery_app.task
def match_pending_deposits_task():
    """Celery task wrapper for matching deposits."""
    db = SessionLocal()
    try:
        return match_pending_deposits(db)
    finally:
        db.close()

@celery_app.task
def flag_stale_deposits_task():
    """Celery task wrapper for flagging stale deposits."""
    db = SessionLocal()
    try:
        return flag_stale_deposits(db)
    finally:
        db.close()


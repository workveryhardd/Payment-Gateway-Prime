from datetime import datetime, timedelta
from app.models.deposit import DepositStatus
from app.utils.logger import logger
from app.core.celery_app import celery_app
from app.storage import repository

def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)

def match_pending_deposits():
    """
    Match pending deposits with incoming ledger entries stored in JSON.
    """
    deposits = repository.list_deposits()
    ledger_entries = repository.list_incoming_ledger()

    pending_deposits = [
        deposit for deposit in deposits
        if deposit["status"] == DepositStatus.PENDING.value and deposit.get("utr_or_hash")
    ]

    matched_count = 0

    for deposit in pending_deposits:
        match = next(
            (
                entry for entry in ledger_entries
                if entry["utr_or_hash"] == deposit["utr_or_hash"]
                and entry["method"] == deposit["method"]
                and not entry.get("matched", False)
            ),
            None,
        )

        if not match:
            continue

        amount_diff = abs(float(deposit["amount"]) - float(match["amount"]))
        if amount_diff >= 0.01:
            continue

        deposit_time = _parse_dt(deposit["created_at"])
        ledger_time = _parse_dt(match["timestamp"])
        if abs((deposit_time - ledger_time).total_seconds()) >= 1800:
            continue

        repository.update_deposit(
            deposit["id"],
            status=DepositStatus.SUCCESS.value,
            verified_at=datetime.utcnow().isoformat(),
        )
        repository.update_incoming_ledger(match["id"], matched=True)
        match["matched"] = True
        matched_count += 1
        logger.info(f"Matched deposit {deposit['id']} with ledger entry {match['id']}")

    logger.info(f"Matched {matched_count} deposits")
    return matched_count

def flag_stale_deposits():
    """
    Flag deposits that have been pending for more than 60 minutes
    with UTR/hash set but no matching ledger entry.
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=60)
    deposits = repository.list_deposits()
    ledger_entries = repository.list_incoming_ledger()

    flagged_count = 0

    for deposit in deposits:
        if deposit["status"] != DepositStatus.PENDING.value:
            continue
        if not deposit.get("utr_or_hash"):
            continue
        if _parse_dt(deposit["created_at"]) >= cutoff_time:
            continue

        ledger_entry = next(
            (
                entry for entry in ledger_entries
                if entry["utr_or_hash"] == deposit["utr_or_hash"]
                and entry["method"] == deposit["method"]
            ),
            None,
        )

        if ledger_entry:
            continue

        repository.update_deposit(
            deposit["id"],
            status=DepositStatus.FLAGGED.value,
        )
        flagged_count += 1
        logger.info(f"Flagged stale deposit {deposit['id']}")

    logger.info(f"Flagged {flagged_count} stale deposits")
    return flagged_count

@celery_app.task
def match_pending_deposits_task():
    """Celery task wrapper for matching deposits."""
    return match_pending_deposits()

@celery_app.task
def flag_stale_deposits_task():
    """Celery task wrapper for flagging stale deposits."""
    return flag_stale_deposits()


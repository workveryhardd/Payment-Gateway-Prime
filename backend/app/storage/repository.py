from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.models.deposit import DepositMethod, DepositStatus
from app.models.payment_account import PaymentAccountStatus, PaymentAccountType
from app.storage.file_store import FileStore

store = FileStore(settings.DATA_FILE_PATH)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _next_id(data: Dict[str, Any], bucket: str) -> int:
    counters = data.setdefault("counters", {})
    counters[bucket] = counters.get(bucket, 0) + 1
    return counters[bucket]


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------
def list_users() -> List[Dict[str, Any]]:
    return store.read().get("users", [])


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    lowered = email.lower()
    for user in store.read().get("users", []):
        if user["email"].lower() == lowered:
            return user
    return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    for user in store.read().get("users", []):
        if user["id"] == user_id:
            return user
    return None


def create_user(email: str, password_hash: str, is_admin: bool = False) -> Dict[str, Any]:
    def mutator(data: Dict[str, Any]):
        lowered = email.lower()
        if any(u["email"].lower() == lowered for u in data["users"]):
            raise ValueError("Email already exists")
        user = {
            "id": _next_id(data, "users"),
            "email": email,
            "password_hash": password_hash,
            "is_admin": is_admin,
            "created_at": _now_iso(),
        }
        data["users"].append(user)
        return user

    return store.write(mutator)


def ensure_admin_exists(email: str, password_hash: str) -> None:
    if get_user_by_email(email):
        return

    # Ignore ValueError since we just checked for existence.
    try:
        create_user(email=email, password_hash=password_hash, is_admin=True)
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Deposit helpers
# ---------------------------------------------------------------------------
def _filter_deposits(
    deposits: List[Dict[str, Any]],
    *,
    user_id: Optional[int] = None,
    status: Optional[DepositStatus] = None,
) -> List[Dict[str, Any]]:
    result = deposits
    if user_id is not None:
        result = [d for d in result if d["user_id"] == user_id]
    if status is not None:
        result = [d for d in result if d["status"] == status.value]
    return sorted(result, key=lambda d: d.get("created_at", ""), reverse=True)


def list_deposits(user_id: Optional[int] = None, status: Optional[DepositStatus] = None) -> List[Dict[str, Any]]:
    deposits = store.read().get("deposits", [])
    return _filter_deposits(deposits, user_id=user_id, status=status)


def get_deposit(deposit_id: int) -> Optional[Dict[str, Any]]:
    for deposit in store.read().get("deposits", []):
        if deposit["id"] == deposit_id:
            return deposit
    return None


def create_deposit_record(user_id: int, method: DepositMethod, amount: float) -> Dict[str, Any]:
    def mutator(data: Dict[str, Any]):
        deposit = {
            "id": _next_id(data, "deposits"),
            "user_id": user_id,
            "method": method.value,
            "amount": float(amount),
            "utr_or_hash": None,
            "status": DepositStatus.PENDING.value,
            "meta_data": None,
            "created_at": _now_iso(),
            "verified_at": None,
        }
        data["deposits"].append(deposit)
        return deposit

    return store.write(mutator)


def update_deposit(deposit_id: int, **changes: Any) -> Optional[Dict[str, Any]]:
    def mutator(data: Dict[str, Any]):
        for deposit in data["deposits"]:
            if deposit["id"] == deposit_id:
                deposit.update(changes)
                return deposit
        return None

    return store.write(mutator)


def utr_exists(utr: str, exclude_deposit_id: Optional[int] = None) -> bool:
    for deposit in store.read().get("deposits", []):
        if deposit["utr_or_hash"] == utr and deposit["id"] != exclude_deposit_id:
            return True
    return False


# ---------------------------------------------------------------------------
# Payment account helpers
# ---------------------------------------------------------------------------
def list_payment_accounts(
    account_type: Optional[PaymentAccountType] = None,
    status: Optional[PaymentAccountStatus] = None,
) -> List[Dict[str, Any]]:
    accounts = store.read().get("payment_accounts", [])
    if account_type:
        accounts = [a for a in accounts if a["account_type"] == account_type.value]
    if status:
        accounts = [a for a in accounts if a["status"] == status.value]
    return sorted(accounts, key=lambda a: a.get("created_at", ""), reverse=True)


def get_payment_account(account_id: int) -> Optional[Dict[str, Any]]:
    for account in store.read().get("payment_accounts", []):
        if account["id"] == account_id:
            return account
    return None


def create_payment_accounts(payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def mutator(data: Dict[str, Any]):
        created = []
        for payload in payloads:
            new_id = _next_id(data, "payment_accounts")
            details = dict(payload.get("details") or {})
            account = {
                "id": new_id,
                "account_type": payload["account_type"],
                "identifier_name": payload.get("identifier_name") or f"{payload['account_type'].lower()}_{new_id}",
                "details": details,
                "status": PaymentAccountStatus.PENDING.value,
                "is_active": False,
                "created_at": _now_iso(),
                "approved_at": None,
                "approved_by": None,
            }
            data["payment_accounts"].append(account)
            created.append(account)
        return created

    return store.write(mutator)


def approve_payment_account(account_id: int, approved_by: int) -> Optional[Dict[str, Any]]:
    iso_now = _now_iso()

    def mutator(data: Dict[str, Any]):
        for account in data["payment_accounts"]:
            if account["id"] == account_id:
                account["status"] = PaymentAccountStatus.ACTIVE.value
                account["approved_at"] = iso_now
                account["approved_by"] = approved_by
                return account
        return None

    return store.write(mutator)


def reject_payment_account(account_id: int) -> Optional[Dict[str, Any]]:
    def mutator(data: Dict[str, Any]):
        for account in data["payment_accounts"]:
            if account["id"] == account_id:
                account["status"] = PaymentAccountStatus.INACTIVE.value
                account["is_active"] = False
                return account
        return None

    return store.write(mutator)


def activate_payment_account(account_id: int) -> Optional[Dict[str, Any]]:
    def mutator(data: Dict[str, Any]):
        target = None
        for account in data["payment_accounts"]:
            if account["id"] == account_id:
                target = account
                break
        if not target:
            return None
        if target["status"] != PaymentAccountStatus.ACTIVE.value:
            raise ValueError("Account must be approved before activation")

        for account in data["payment_accounts"]:
            if account["account_type"] == target["account_type"]:
                account["is_active"] = account["id"] == target["id"]
        return target

    return store.write(mutator)


def delete_payment_account(account_id: int) -> Optional[Dict[str, Any]]:
    def mutator(data: Dict[str, Any]):
        accounts = data["payment_accounts"]
        for idx, account in enumerate(accounts):
            if account["id"] == account_id:
                removed = accounts.pop(idx)
                return removed
        return None

    return store.write(mutator)


def get_active_accounts() -> Dict[str, Optional[Dict[str, Any]]]:
    active = {"upi": None, "bank": None, "crypto": None, "card": None}
    for account in store.read().get("payment_accounts", []):
        if account["is_active"] and account["status"] == PaymentAccountStatus.ACTIVE.value:
            key = account["account_type"].lower()
            active[key] = {
                "identifier_name": account["identifier_name"],
                **account["details"],
            }
    return active


# ---------------------------------------------------------------------------
# Incoming ledger helpers
# ---------------------------------------------------------------------------
def list_incoming_ledger(matched: Optional[bool] = None) -> List[Dict[str, Any]]:
    entries = store.read().get("incoming_ledger", [])
    if matched is not None:
        entries = [entry for entry in entries if entry.get("matched", False) == matched]
    return sorted(
        entries,
        key=lambda entry: entry.get("created_at") or entry.get("timestamp"),
        reverse=True,
    )


def update_incoming_ledger(entry_id: int, **changes: Any) -> Optional[Dict[str, Any]]:
    def mutator(data: Dict[str, Any]):
        for entry in data["incoming_ledger"]:
            if entry["id"] == entry_id:
                entry.update(changes)
                return entry
        return None

    return store.write(mutator)



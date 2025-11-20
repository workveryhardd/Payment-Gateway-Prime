import json
import os
from pathlib import Path
from typing import Optional, Dict

def get_crypto_sample_path() -> Path:
    """Get path to crypto sample files."""
    return Path(__file__).parent.parent / "assets" / "samples" / "crypto"

def check_trc20_tx(hash: str) -> Optional[Dict]:
    """
    Check TRC20 transaction by hash.
    For now, loads from sample JSON file.
    In production, would call TRONSCAN API.
    """
    sample_path = get_crypto_sample_path() / "sample_trc20_tx.json"
    if sample_path.exists():
        with open(sample_path, 'r') as f:
            data = json.load(f)
            # Replace with actual hash if provided
            if hash:
                data["txid"] = hash
            return data
    return None

def check_erc20_tx(hash: str) -> Optional[Dict]:
    """
    Check ERC20 transaction by hash.
    For now, loads from sample JSON file.
    In production, would call Etherscan API.
    """
    sample_path = get_crypto_sample_path() / "sample_erc20_tx.json"
    if sample_path.exists():
        with open(sample_path, 'r') as f:
            data = json.load(f)
            # Replace with actual hash if provided
            if hash:
                data["tx_hash"] = hash
            return data
    return None

def check_bep20_tx(hash: str) -> Optional[Dict]:
    """
    Check BEP20 transaction by hash.
    For now, returns None.
    In production, would call BSCScan API.
    """
    # Similar structure to ERC20
    return None


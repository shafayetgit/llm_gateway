import hashlib
import secrets


def generate_api_key(prefix: str = "gw_live_") -> tuple[str, str, str]:
    """Generates a new API key.

    Returns:
        tuple: (raw_key, key_prefix, key_hash)
        - raw_key: The full secret key shown to the user ONCE.
        - key_prefix: The prefix (first 8 chars) stored in DB for display.
        - key_hash: SHA-256 hash stored in DB for verification.
    """
    random_bytes = secrets.token_hex(24)
    raw_key = f"{prefix}{random_bytes}"
    key_prefix = raw_key[:8]
    key_hash = hash_api_key(raw_key)

    return raw_key, key_prefix, key_hash


def hash_api_key(key: str) -> str:
    """Hashes an API key using SHA-256."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

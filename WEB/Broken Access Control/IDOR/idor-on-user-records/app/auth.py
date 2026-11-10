"""Credential derivation and session token helpers for the patient portal."""

from __future__ import annotations

import hashlib
import hmac
import secrets

PBKDF2_ROUNDS = 600_000
SALT_BYTES = 16
TOKEN_BYTES = 32


def new_salt() -> str:
    """Return a fresh hex-encoded salt for one account."""
    return secrets.token_hex(SALT_BYTES)


def derive(secret: str, salt_hex: str) -> str:
    """Derive the stored value for a sign-in secret."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ROUNDS,
    ).hex()


def matches(secret: str, salt_hex: str, stored_hash: str) -> bool:
    """Constant-time comparison of a submitted secret against the stored value."""
    return hmac.compare_digest(derive(secret, salt_hex), stored_hash)


def new_token() -> str:
    """Return an opaque session token."""
    return secrets.token_urlsafe(TOKEN_BYTES)

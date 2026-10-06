import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600_000,
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its stored hash."""

    try:
        salt, password_hash = stored_hash.split("$", 1)
    except ValueError:
        return False

    calculated_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600_000,
    ).hex()

    return secrets.compare_digest(calculated_hash, password_hash)
    
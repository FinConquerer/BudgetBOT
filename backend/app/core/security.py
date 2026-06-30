"""Hàm hỗ trợ hash mật khẩu và tạo/kiểm tra JWT cho Auth/User API."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from dotenv import load_dotenv

load_dotenv()

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
_PBKDF2_ITERATIONS = 210_000

if ENVIRONMENT.lower() == "production" and SECRET_KEY == "dev-secret-key-change-me":
    raise RuntimeError("SECRET_KEY must be set in production")


def hash_password(password: str) -> str:
    """Hash mật khẩu bằng PBKDF2-HMAC-SHA256 với salt ngẫu nhiên."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${_PBKDF2_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    """Kiểm tra mật khẩu với chuỗi hash PBKDF2 đã lưu."""
    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_text)
        expected_digest = base64.b64decode(digest_text)
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual_digest, expected_digest)


def create_access_token(subject: str) -> tuple[str, int]:
    """Tạo Bearer token đã ký theo định dạng JWT HS256."""
    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + expires_in}
    token = _encode_jwt(payload)
    return token, expires_in


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Giải mã và kiểm tra JWT HS256; trả None nếu token không hợp lệ."""
    try:
        header_text, payload_text, signature_text = token.split(".")
        signing_input = f"{header_text}.{payload_text}".encode("ascii")
        expected_signature = _sign(signing_input)
        actual_signature = _b64url_decode(signature_text)
        if not hmac.compare_digest(actual_signature, expected_signature):
            return None

        header = json.loads(_b64url_decode(header_text))
        if header.get("alg") != JWT_ALGORITHM:
            return None

        payload = json.loads(_b64url_decode(payload_text))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except (binascii.Error, UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError):
        return None


def _encode_jwt(payload: dict[str, Any]) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_text = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_text = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_text}.{payload_text}".encode("ascii")
    signature_text = _b64url_encode(_sign(signing_input))
    return f"{header_text}.{payload_text}.{signature_text}"


def _sign(signing_input: bytes) -> bytes:
    if JWT_ALGORITHM != "HS256":
        raise ValueError("Only HS256 JWT is supported")
    return hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

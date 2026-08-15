"""profile PII 加密 — phone 用 AES-256-GCM，绝不进同步协议。

密钥从环境变量 PROFILE_PHONE_KEY（base64, 32 字节）读取。
未配置密钥时降级为明文存储（开发环境）。
"""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes | None:
    key = os.getenv("PROFILE_PHONE_KEY")
    if not key:
        return None
    try:
        raw = base64.b64decode(key)
        return raw if len(raw) == 32 else None
    except Exception:
        return None


def encrypt_phone(plaintext: str) -> str:
    """AES-256-GCM 加密；无密钥或空值则原样返回。"""
    key = _get_key()
    if not key or not plaintext:
        return plaintext
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt_phone(ciphertext: str) -> str:
    """AES-256-GCM 解密；失败返回原值（降级，不抛异常）。"""
    key = _get_key()
    if not key or not ciphertext:
        return ciphertext
    try:
        raw = base64.b64decode(ciphertext)
        nonce, ct = raw[:12], raw[12:]
        return AESGCM(key).decrypt(nonce, ct, None).decode()
    except Exception:
        return ciphertext

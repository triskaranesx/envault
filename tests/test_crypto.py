"""Tests for envault.crypto encryption/decryption module."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-password"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db\nSECRET_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_decrypt_roundtrip():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == PLAINTEXT


def test_encrypt_produces_different_blobs():
    """Each encryption should produce a unique ciphertext due to random salt/nonce."""
    blob1 = encrypt(PLAINTEXT, PASSWORD)
    blob2 = encrypt(PLAINTEXT, PASSWORD)
    assert blob1 != blob2


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrong-password")


def test_decrypt_corrupted_data_raises():
    with pytest.raises(ValueError):
        decrypt("not-valid-base64!!!", PASSWORD)


def test_decrypt_too_short_raises():
    import base64
    short_blob = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short_blob, PASSWORD)


def test_encrypt_empty_string():
    encrypted = encrypt("", PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == ""


def test_encrypt_unicode():
    unicode_text = "API_KEY=clésecrète_日本語"
    encrypted = encrypt(unicode_text, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == unicode_text

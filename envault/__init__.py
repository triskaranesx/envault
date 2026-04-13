"""envault — Encrypt and version .env files with team-sharing support."""

__version__ = "0.1.0"
__author__ = "envault contributors"

from envault.crypto import encrypt, decrypt

__all__ = ["encrypt", "decrypt"]

"""File and string hashing utility."""

import hashlib
from typing import Optional


SUPPORTED_ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]


def hash_string(text: str, algo: str = "sha256") -> str:
    """Hash a string using the specified algorithm."""
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def hash_file(path: str, algo: str = "sha256") -> Optional[str]:
    """Hash a file using the specified algorithm."""
    try:
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None

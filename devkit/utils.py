"""Shared utility functions for devkit."""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: String to validate.

    Returns:
        True if the string is a valid URL with scheme and netloc.
    """
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


def parse_json(string: str) -> Optional[dict]:
    """Parse a JSON string, returning None on failure.

    Args:
        string: JSON string to parse.

    Returns:
        Parsed dict or None if parsing fails.
    """
    try:
        return json_loads(string)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def json_dumps(data: Any, indent: int = 2) -> str:
    """Serialize data to JSON string with datetime support.

    Args:
        data: Data to serialize.
        indent: Indentation level.

    Returns:
        JSON string.
    """
    def safe_serializer(obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    return json.dumps(data, indent=indent, default=safe_serializer, ensure_ascii=False)


def json_loads(data: str) -> Any:
    """Parse JSON string with relaxed parsing.

    Args:
        data: JSON string.

    Returns:
        Parsed object.
    """
    return json.loads(data, strict=False)


def create_uuid_from_string(val: str) -> uuid.UUID:
    """Generate a deterministic UUID from a string using MD5 hashing.

    Args:
        val: Input string.

    Returns:
        UUID derived from the string.
    """
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)


def deduplicate(target_list: list) -> list:
    """Remove duplicates from a list while preserving order.

    Args:
        target_list: List with potential duplicates.

    Returns:
        Deduplicated list.
    """
    seen = set()
    result = []
    for item in target_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

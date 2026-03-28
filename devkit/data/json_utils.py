"""JSON processing utilities."""

import json
import os
from typing import Any, Optional


def flatten_json(data: dict, separator: str = ".", prefix: str = "") -> dict:
    """Flatten a nested dict into a single-level dict with dotted keys."""
    result = {}
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_json(value, separator, new_key))
        else:
            result[new_key] = value
    return result


def unflatten_json(data: dict, separator: str = ".") -> dict:
    """Unflatten a dotted-key dict into a nested dict."""
    result: dict = {}
    for compound_key, value in data.items():
        keys = compound_key.split(separator)
        current = result
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    return result


def json_query(data: Any, path: str, separator: str = ".") -> Optional[Any]:
    """Query a nested dict using dot-notation path."""
    keys = path.split(separator)
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def merge_jsonl(files: list, output: str) -> None:
    """Merge multiple JSONL files into one."""
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as out:
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        out.write(line + "\n")

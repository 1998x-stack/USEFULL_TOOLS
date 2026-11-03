"""Lossless JSON path utilities and validated JSON Lines merge."""

import json
from typing import Any, Optional

from devkit.data.io import atomic_text_output

_ESCAPE = "\\"


def _check_separator(separator: str) -> None:
    if not separator or _ESCAPE in separator:
        raise ValueError("Separator must be non-empty and cannot contain backslashes")


def _encode_segment(segment: str, separator: str) -> str:
    if not isinstance(segment, str):
        raise TypeError("JSON object keys must be strings")
    return segment.replace(_ESCAPE, _ESCAPE * 2).replace(separator, _ESCAPE + separator)


def _decode_path(path: str, separator: str) -> list:
    """Decode escaped literal separators/backslashes in a flat JSON path."""
    _check_separator(separator)
    if not isinstance(path, str):
        raise TypeError("JSON paths must be strings")
    segments = []
    part = []
    i = 0
    while i < len(path):
        if path[i] == _ESCAPE:
            if path.startswith(separator, i + 1):
                part.append(separator)
                i += 1 + len(separator)
            elif i + 1 < len(path) and path[i + 1] == _ESCAPE:
                part.append(_ESCAPE)
                i += 2
            else:
                raise ValueError(f"Invalid path escape: {path!r}")
        elif path.startswith(separator, i):
            segments.append("".join(part))
            part = []
            i += len(separator)
        else:
            part.append(path[i])
            i += 1
    segments.append("".join(part))
    return segments


def flatten_json(data: dict, separator: str = ".", prefix: str = "") -> dict:
    """Flatten nested dictionaries with reversible escapes for literal key separators.

    Empty dictionaries are retained. Lists remain leaf values. A prefix is a
    pre-encoded path, as in the previous API.
    """
    _check_separator(separator)
    if not isinstance(data, dict):
        raise TypeError("flatten_json expects a dictionary")
    result = {}

    def visit(node, segments):
        for key, value in node.items():
            path = segments + [_encode_segment(key, separator)]
            encoded = separator.join(path)
            if isinstance(value, dict) and value:
                visit(value, path)
            else:
                if encoded in result:
                    raise ValueError(f"Duplicate flattened key: {encoded!r}")
                result[encoded] = value

    visit(data, [prefix] if prefix else [])
    return result


def unflatten_json(data: dict, separator: str = ".") -> dict:
    """Rebuild nested JSON and reject ambiguous/conflicting paths."""
    _check_separator(separator)
    if not isinstance(data, dict):
        raise TypeError("unflatten_json expects a dictionary")
    result = {}
    leaves = set()
    for compound_key, value in data.items():
        segments = _decode_path(compound_key, separator)
        current = result
        for depth, key in enumerate(segments[:-1], start=1):
            if tuple(segments[:depth]) in leaves:
                raise ValueError(f"Conflicting JSON paths near {compound_key!r}")
            if key not in current:
                current[key] = {}
            if not isinstance(current[key], dict):
                raise ValueError(f"Conflicting JSON paths near {compound_key!r}")
            current = current[key]
        last = segments[-1]
        full_path = tuple(segments)
        if last in current:
            raise ValueError(f"Conflicting JSON path: {compound_key!r}")
        current[last] = value
        leaves.add(full_path)
    return result


def json_query(data: Any, path: str, separator: str = ".") -> Optional[Any]:
    """Query JSON with the same escape conventions as flatten_json."""
    current = data
    for key in _decode_path(path, separator):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def reject_duplicate_pairs(pairs: list) -> dict:
    """Raise rather than silently overwrite repeated JSON object keys."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str):
    """Reject NaN/Infinity, which are not standard JSON constants."""
    raise ValueError(f"Non-standard JSON constant: {value}")


def merge_jsonl(files: list, output: str) -> None:
    """Merge JSONL, validating every nonempty line before publishing output."""
    if not files:
        raise ValueError("At least one JSONL input is required")
    with atomic_text_output(output, files) as out:
        for filepath in files:
            with open(filepath, "r", encoding="utf-8-sig") as source:
                for line_number, line in enumerate(source, start=1):
                    value = line.strip()
                    if not value:
                        continue
                    try:
                        json.loads(
                            value,
                            object_pairs_hook=reject_duplicate_pairs,
                            parse_constant=reject_nonfinite_constant,
                        )
                    except (json.JSONDecodeError, ValueError) as exc:
                        raise ValueError(
                            f"Invalid JSONL in {filepath} on line {line_number}: {exc}"
                        ) from exc
                    out.write(value + "\n")

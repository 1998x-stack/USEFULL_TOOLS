"""Test shared utilities."""

import json
import os
import tempfile
from datetime import datetime

from devkit.utils import (
    is_valid_url,
    parse_json,
    json_dumps,
    json_loads,
    create_uuid_from_string,
    deduplicate,
)


def test_is_valid_url_valid():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://example.com/path?q=1") is True


def test_is_valid_url_invalid():
    assert is_valid_url("not-a-url") is False
    assert is_valid_url("") is False
    assert is_valid_url("ftp://") is False


def test_parse_json_valid():
    result = parse_json('{"key": "value", "num": 42}')
    assert result == {"key": "value", "num": 42}


def test_parse_json_invalid():
    result = parse_json("not json")
    assert result is None


def test_json_dumps_with_datetime():
    data = {"time": datetime(2026, 1, 1, 12, 0)}
    result = json_dumps(data)
    assert "2026-01-01T12:00:00" in result


def test_json_dumps_chinese():
    data = {"name": "你好"}
    result = json_dumps(data)
    assert "你好" in result  # ensure_ascii=False


def test_json_loads():
    result = json_loads('{"key": "value"}')
    assert result == {"key": "value"}


def test_create_uuid_deterministic():
    uuid1 = create_uuid_from_string("test")
    uuid2 = create_uuid_from_string("test")
    assert uuid1 == uuid2


def test_create_uuid_different_inputs():
    uuid1 = create_uuid_from_string("test1")
    uuid2 = create_uuid_from_string("test2")
    assert uuid1 != uuid2


def test_deduplicate():
    assert deduplicate([1, 2, 3, 2, 1]) == [1, 2, 3]


def test_deduplicate_preserves_order():
    assert deduplicate([3, 1, 2, 1, 3]) == [3, 1, 2]


def test_deduplicate_empty():
    assert deduplicate([]) == []

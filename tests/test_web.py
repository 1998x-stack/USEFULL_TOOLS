"""Tests for web utility tools."""

from devkit.web.url_validator import is_valid_url


def test_valid_urls():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://example.com/path") is True
    assert is_valid_url("https://sub.example.com:8080/path?q=1") is True


def test_invalid_urls():
    assert is_valid_url("not a url") is False
    assert is_valid_url("") is False
    assert is_valid_url("ftp://files.example.com") is False

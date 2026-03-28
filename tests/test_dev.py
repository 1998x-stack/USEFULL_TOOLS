"""Tests for developer utility tools."""

import os
import socket
import tempfile

from devkit.dev.hash_tool import hash_string, hash_file
from devkit.dev.port_finder import is_port_available, find_available_ports
from devkit.dev.env_checker import check_environment
from devkit.dev.git_stats import get_stats


def test_hash_string_sha256():
    result = hash_string("hello", algo="sha256")
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_string_md5():
    result = hash_string("hello", algo="md5")
    assert result == "5d41402abc4b2a76b9719d911017c592"


def test_hash_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    result = hash_file(str(f), algo="sha256")
    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_file_not_found():
    result = hash_file("/nonexistent/file.txt")
    assert result is None


def test_is_port_available():
    result = is_port_available(58932)
    assert isinstance(result, bool)


def test_find_available_ports():
    ports = find_available_ports(start=49152, end=49200, count=3)
    assert isinstance(ports, list)
    assert len(ports) <= 3
    for port in ports:
        assert 49152 <= port <= 49200


def test_check_environment_python():
    results = check_environment(tools=["python"])
    assert "python" in results
    assert results["python"]["found"] is True
    assert "version" in results["python"]


def test_check_environment_nonexistent():
    results = check_environment(tools=["nonexistent_tool_xyz"])
    assert "nonexistent_tool_xyz" in results
    assert results["nonexistent_tool_xyz"]["found"] is False


def test_get_stats_current_repo():
    stats = get_stats(".")
    assert "total_commits" in stats
    assert "contributors" in stats
    assert isinstance(stats["total_commits"], int)
    assert stats["total_commits"] > 0


def test_get_stats_invalid_path():
    stats = get_stats("/tmp/not_a_git_repo_xyz")
    assert stats.get("error") is not None

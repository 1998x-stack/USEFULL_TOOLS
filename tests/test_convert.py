"""Tests for conversion tools."""

import os

from devkit.convert.pdf_merge import merge_pdfs
from devkit.convert.media import resize_image


def test_merge_pdfs_empty_dir(tmp_path):
    out = str(tmp_path / "out.pdf")
    count = merge_pdfs(str(tmp_path), out)
    assert count == 0


def test_resize_image_missing_file():
    result = resize_image("/nonexistent.jpg", "300x300")
    assert result is None

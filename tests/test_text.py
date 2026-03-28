"""Tests for text processing tools."""

from devkit.text.text_length import calculate_custom_length
from devkit.text.split_sentence import split_sentence


def test_text_length_english():
    result = calculate_custom_length("Hello world")
    assert isinstance(result, int)
    assert result >= 0


def test_text_length_chinese():
    result = calculate_custom_length("你好世界")
    assert result == 4


def test_text_length_mixed():
    result = calculate_custom_length("Hello 你好 World")
    assert result > 0


def test_text_length_empty():
    result = calculate_custom_length("")
    assert result == 0


def test_split_sentence_coarse():
    text = "第一句话。第二句话。第三句话。"
    result = split_sentence(text, criterion="coarse")
    assert len(result) == 3


def test_split_sentence_fine():
    text = "你好，世界！今天天气很好。"
    result = split_sentence(text, criterion="fine")
    assert len(result) >= 2


def test_split_sentence_empty():
    result = split_sentence("", criterion="coarse")
    assert result == []

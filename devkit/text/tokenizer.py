"""Simple tokenizer utilities (word/char level, no external deps)."""

import re
from typing import List


def word_tokenize(text: str) -> List[str]:
    """Simple word tokenizer for mixed CJK/English text.

    Args:
        text: Input text.

    Returns:
        List of tokens.
    """
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z]+|[0-9]+", text)


def char_count(text: str) -> dict:
    """Count characters by category.

    Args:
        text: Input text.

    Returns:
        Dict with counts for 'cjk', 'english', 'digits', 'spaces', 'punctuation', 'other'.
    """
    counts = {"cjk": 0, "english": 0, "digits": 0, "spaces": 0, "punctuation": 0, "other": 0}
    for char in text:
        if "\u4E00" <= char <= "\u9FFF":
            counts["cjk"] += 1
        elif char.isalpha():
            counts["english"] += 1
        elif char.isdigit():
            counts["digits"] += 1
        elif char.isspace():
            counts["spaces"] += 1
        elif not char.isalnum():
            counts["punctuation"] += 1
        else:
            counts["other"] += 1
    return counts

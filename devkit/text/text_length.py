"""Information-entropy based text length calculation.

Assigns weights to different character types based on their information density:
- CJK characters: 1.0 (high density)
- English words: 0.47 per word (semantic unit)
- Numbers: 0.01 per digit
- Spaces: 0.001
- Punctuation: 0.05
- Emoji: 0.2
"""

import math
import re
import unicodedata

_PATTERN = re.compile(
    r"(?P<word>\b[a-zA-Z]+\b)"
    r"|(?P<mixed>[a-zA-Z0-9]*[a-zA-Z][a-zA-Z0-9]*[0-9][a-zA-Z0-9]*|[a-zA-Z0-9]*[0-9][a-zA-Z0-9]*[a-zA-Z][a-zA-Z0-9]*)"
    r"|(?P<digit>\b\d+\b)"
    r"|(?P<space>\s+)"
    r"|(?P<punctuation>[\u2000-\u206F\u2E00-\u2E7F'!\"#$%&()*+,\-./:;<=>?@\[\]^_`{|}~])"
    r"|(?P<fullwidth>[\uFF00-\uFFEF])"
    r"|(?P<control>[\u0000-\u001F\u007F-\u009F])"
    r"|(?P<emoji>[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF])",
    re.UNICODE,
)


def _unclassified_length(text: str) -> float:
    """Calculate length for characters not matched by the main pattern."""
    length = 0.0
    for char in text:
        if "\u4E00" <= char <= "\u9FFF" or "\u3400" <= char <= "\u4DBF":
            length += 1.0
        elif "\uFF65" <= char <= "\uFF9F":
            length += 0.7
        else:
            cat = unicodedata.category(char)
            if cat.startswith("L"):
                length += 0.5
            elif cat.startswith("M"):
                length += 0.3
            elif cat.startswith("N"):
                length += 0.01
            elif cat.startswith("S"):
                length += 0.2
            else:
                length += 0.3
    return length


def calculate_custom_length(text: str) -> int:
    """Calculate information-weighted text length.

    Args:
        text: Input text string.

    Returns:
        Weighted length as integer (floor).
    """
    if not text:
        return 0

    total = 0.0
    last_index = 0

    for match in _PATTERN.finditer(text):
        start, end = match.span()
        if last_index < start:
            total += _unclassified_length(text[last_index:start])
        last_index = end

        if match.group("word"):
            total += 0.47
        elif match.group("mixed"):
            total += len(match.group("mixed")) * 0.01
        elif match.group("digit"):
            total += len(match.group("digit")) * 0.01
        elif match.group("space"):
            total += len(match.group("space")) * 0.001
        elif match.group("punctuation"):
            total += 0.05
        elif match.group("fullwidth"):
            total += 0.8
        elif match.group("control"):
            continue
        elif match.group("emoji"):
            total += 0.2

    if last_index < len(text):
        total += _unclassified_length(text[last_index:])

    return math.floor(total)

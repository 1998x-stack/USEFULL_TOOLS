"""Chinese sentence splitter.

Splits Chinese text into sentences with proper handling of quotation marks.
Supports coarse (period-level) and fine (all punctuation) granularity.
"""

import re
from typing import List

_PUNCS_FINE = {"……", "\r\n", "，", "。", ";", "；", "…", "！", "!",
               "?", "？", "\r", "\n", "\u201c", "\u201d", "\u2018", "\u2019", "："}
_PUNCS_COARSE = {"。", "！", "？", "\n", "\u201c", "\u201d", "\u2018", "\u2019"}
_FRONT_QUOTES = {"\u201c", "\u2018"}
_BACK_QUOTES = {"\u201d", "\u2019"}

_COARSE_PTN = re.compile('([。\u201c\u201d！？\n])')
_FINE_PTN = re.compile('([，：。;\u201c\u201d；…！!?？\r\n])')


def split_sentence(text: str, criterion: str = "coarse") -> List[str]:
    """Split text into sentences.

    Args:
        text: Input text.
        criterion: 'coarse' (sentence-level) or 'fine' (clause-level).

    Returns:
        List of sentence strings.
    """
    if not text or not text.strip():
        return []

    if criterion == "coarse":
        tmp_list = _COARSE_PTN.split(text)
        puncs = _PUNCS_COARSE
    elif criterion == "fine":
        tmp_list = _FINE_PTN.split(text)
        puncs = _PUNCS_FINE
    else:
        raise ValueError("criterion must be 'coarse' or 'fine'")

    sentences: List[str] = []
    quote_flag = False

    for seg in tmp_list:
        if seg == "":
            continue

        if seg in puncs:
            if len(sentences) == 0:
                if seg in _FRONT_QUOTES:
                    quote_flag = True
                sentences.append(seg)
                continue

            if seg in _FRONT_QUOTES:
                if sentences[-1][-1] in puncs:
                    sentences.append(seg)
                else:
                    sentences[-1] += seg
                quote_flag = True
            else:
                sentences[-1] += seg
            continue

        if len(sentences) == 0:
            sentences.append(seg)
            continue

        if quote_flag:
            sentences[-1] += seg
            quote_flag = False
        else:
            if sentences[-1][-1] in _BACK_QUOTES:
                if len(sentences[-1]) <= 1:
                    sentences[-1] += seg
                else:
                    if sentences[-1][-2] in puncs:
                        sentences.append(seg)
                    else:
                        sentences[-1] += seg
            else:
                sentences.append(seg)

    return sentences

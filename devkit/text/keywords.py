"""Weighted keyword extraction for Chinese and English text."""

import re
from typing import Dict, List, Union


def extract_keywords(text: str, lang: str = "zh", mode: str = "all", top_k: int = 10) -> List[Dict[str, Union[str, float]]]:
    text = str(text).strip()
    if not text:
        return []
    if lang == "en":
        return _extract_english(text, top_k)
    return _extract_chinese(text, mode, top_k)


def _extract_english(text: str, top_k: int) -> List[Dict[str, Union[str, float]]]:
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                  "being", "have", "has", "had", "do", "does", "did", "will",
                  "would", "could", "should", "may", "might", "can", "shall",
                  "of", "in", "to", "for", "with", "on", "at", "from", "by",
                  "as", "into", "through", "during", "before", "after", "and",
                  "but", "or", "nor", "not", "so", "yet", "both", "either",
                  "neither", "each", "every", "all", "any", "few", "more",
                  "most", "other", "some", "such", "no", "only", "own", "same",
                  "than", "too", "very", "just", "because", "this", "that",
                  "these", "those", "it", "its"}
    words = [w for w in words if w not in stop_words]
    freq: Dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    max_freq = sorted_words[0][1] if sorted_words else 1
    return [{"word": w, "boost": round(c / max_freq * 2, 2)} for w, c in sorted_words[:top_k]]


def _extract_chinese(text: str, mode: str, top_k: int) -> List[Dict[str, Union[str, float]]]:
    try:
        import jieba.analyse as analyse
    except ImportError:
        raise ImportError("jieba is required: pip install devkit-tools[nlp]")
    allow_pos = ("n", "ns", "nt", "nz", "v", "vn", "a", "an", "eng")
    extracted = analyse.extract_tags(text, topK=top_k, withWeight=True, allowPOS=allow_pos)
    if not extracted:
        return [{"word": text, "boost": 2.0}]
    max_weight = extracted[0][1] if extracted else 1
    return [{"word": word, "boost": round(weight / max_weight * 2, 2)} for word, weight in extracted]

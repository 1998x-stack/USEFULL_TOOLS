"""Token counter for LLM models."""

from typing import List

MODEL_ENCODINGS = {
    "gpt-4o": "o200k_base", "gpt-4o-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base", "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "claude-opus": "cl100k_base", "claude-sonnet": "cl100k_base", "claude-haiku": "cl100k_base",
}


def supported_models() -> List[str]:
    return list(MODEL_ENCODINGS.keys())


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    try:
        import tiktoken
    except ImportError:
        raise ImportError("tiktoken is required: pip install devkit-tools[ai]")
    encoding_name = MODEL_ENCODINGS.get(model, "cl100k_base")
    enc = tiktoken.get_encoding(encoding_name)
    return len(enc.encode(text))


def count_tokens_file(file_path: str, model: str = "gpt-4o") -> int:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return count_tokens(text, model)

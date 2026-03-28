"""Extract and merge source code files."""

import os
from typing import List, Optional

DEFAULT_EXTENSIONS = ["py", "js", "ts", "html", "css", "java", "go", "rs", "c", "cpp", "h"]

LANG_MAP = {
    "py": "python", "js": "javascript", "ts": "typescript",
    "html": "html", "css": "css", "java": "java", "go": "go",
    "rs": "rust", "c": "c", "cpp": "cpp", "h": "c",
    "sh": "bash", "rb": "ruby", "php": "php", "swift": "swift",
}


def extract_code_files(directory: str, extensions: Optional[List[str]] = None, output: Optional[str] = None) -> str:
    """Extract code files from a directory into a single document."""
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS
    ext_set = set(extensions)
    parts = []
    for root, _, files in os.walk(directory):
        for filename in sorted(files):
            ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
            if ext not in ext_set:
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, directory)
            lang = LANG_MAP.get(ext, "")
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except (PermissionError, OSError):
                continue
            parts.append(f"{rel_path}\n```{lang}\n{content}\n```\n")
    result = "\n".join(parts)
    if output:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
    return result

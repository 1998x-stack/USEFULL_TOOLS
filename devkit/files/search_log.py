"""Search through log files."""

import os
from typing import List


def search_file(filepath: str, query: str, context_lines: int = 3, max_results: int = 50) -> List[dict]:
    """Search for a string in a file and return matching lines with context."""
    if not os.path.isfile(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (PermissionError, OSError):
        return []
    results = []
    for i, line in enumerate(lines):
        if query in line:
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = [ln.rstrip("\n") for ln in lines[start:end]]
            results.append({"line_number": i + 1, "line": line.rstrip("\n"), "context": context})
            if len(results) >= max_results:
                break
    return results

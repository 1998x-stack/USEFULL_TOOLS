"""Remove duplicate files based on naming patterns."""

import os
import re
from typing import List, Optional

DUPLICATE_PATTERN = re.compile(r" \((\d+)\)(\.[a-zA-Z0-9]+)$")


def find_duplicates(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """Find duplicate files matching pattern 'name (N).ext'."""
    if extensions is None:
        extensions = ["*.html", "*.pdf", "*.mp3", "*.mp4"]
    ext_set = {e.lstrip("*.") for e in extensions}
    duplicates = []
    for root, _, files in os.walk(directory):
        for filename in files:
            file_ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
            if ext_set and file_ext not in ext_set:
                continue
            match = DUPLICATE_PATTERN.search(filename)
            if match:
                base = DUPLICATE_PATTERN.sub(match.group(2), filename)
                original = os.path.join(root, base)
                if os.path.exists(original):
                    duplicates.append(os.path.join(root, filename))
    return duplicates


def remove_duplicates(directory: str, extensions: Optional[List[str]] = None, dry_run: bool = True) -> List[str]:
    """Remove duplicate files."""
    duplicates = find_duplicates(directory, extensions)
    if not dry_run:
        for filepath in duplicates:
            os.remove(filepath)
    return duplicates

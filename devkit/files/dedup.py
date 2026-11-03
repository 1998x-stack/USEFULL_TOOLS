"""Find identical numbered file copies before optionally removing them.

Only files with identical SHA-256 content are duplicates. Neither symlinks
nor hard links are candidates. This tool does not replace filesystem backups
or provide atomic safety against concurrent filesystem modifications.
"""

import hashlib
import os
import re
from typing import List, Optional

DUPLICATE_PATTERN = re.compile(r" \((\d+)\)(\.[a-zA-Z0-9]+)$")
_CHUNK_SIZE = 1024 * 1024


def _digest(path: str) -> bytes:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.digest()


def _identical_regular_files(original: str, candidate: str) -> bool:
    """Compare size and bytes, excluding links and unavailable files."""
    if os.path.islink(original) or os.path.islink(candidate):
        return False
    try:
        if not os.path.isfile(original) or not os.path.isfile(candidate):
            return False
        if os.path.samefile(original, candidate):
            return False
        if os.path.getsize(original) != os.path.getsize(candidate):
            return False
        return _digest(original) == _digest(candidate)
    except OSError:
        return False


def find_duplicates(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """Find numbered copies whose bytes match their unnumbered counterpart."""
    if extensions is None:
        extensions = ["*.html", "*.pdf", "*.mp3", "*.mp4"]
    ext_set = {e.lstrip("*.").lower() for e in extensions}
    duplicates = []
    for root, _, files in os.walk(directory):
        for filename in sorted(files):
            file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext_set and file_ext not in ext_set:
                continue
            match = DUPLICATE_PATTERN.search(filename)
            if match is None:
                continue
            base = DUPLICATE_PATTERN.sub(match.group(2), filename)
            original = os.path.join(root, base)
            candidate = os.path.join(root, filename)
            if _identical_regular_files(original, candidate):
                duplicates.append(candidate)
    return sorted(duplicates)


def remove_duplicates(directory: str, extensions: Optional[List[str]] = None, dry_run: bool = True) -> List[str]:
    """List or remove identical numbered copies. Reverify before deletion."""
    candidates = find_duplicates(directory, extensions)
    if dry_run:
        return candidates
    removed = []
    for candidate in candidates:
        name = os.path.basename(candidate)
        match = DUPLICATE_PATTERN.search(name)
        if match is None:
            continue
        original = os.path.join(os.path.dirname(candidate), DUPLICATE_PATTERN.sub(match.group(2), name))
        if _identical_regular_files(original, candidate):
            os.remove(candidate)
            removed.append(candidate)
    return removed

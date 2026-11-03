"""Batch rename files with preflight collision checks and staged renames."""

import os
import string
import tempfile
from datetime import datetime
from typing import List, Optional, Tuple

_ALLOWED_FIELDS = {"n", "name", "ext", "date"}


def _check_pattern(pattern: str) -> None:
    for _, field, spec, conversion in string.Formatter().parse(pattern):
        if field is not None and (field not in _ALLOWED_FIELDS or conversion is not None or "{" in spec):
            raise ValueError("Only {n}, {name}, {ext}, and {date} placeholders are allowed")


def _check_filename(filename: str) -> None:
    if not filename or filename in (".", "..") or "/" in filename or "\\" in filename or "\x00" in filename:
        raise ValueError("Rename pattern must produce a filename, not a path")


def batch_rename(directory: str, pattern: str, filter_ext: Optional[str] = None, dry_run: bool = True) -> List[Tuple[str, str]]:
    """Safely rename files in one directory without overwriting existing targets.

    Preflight validates the complete plan. Execution stages sources under unique
    temporary names so name cycles work. On ordinary exceptions rollback is
    attempted; a crash or concurrent filesystem modification is not atomic.
    """
    if not os.path.isdir(directory):
        return []
    _check_pattern(pattern)
    files = sorted(f for f in os.listdir(directory)
                   if os.path.isfile(os.path.join(directory, f)) and not os.path.islink(os.path.join(directory, f)))
    if filter_ext:
        files = [f for f in files if f.endswith(f".{filter_ext}")]
    planned = []
    today = datetime.now().strftime("%Y-%m-%d")
    for i, filename in enumerate(files, start=1):
        name, ext = os.path.splitext(filename)
        new_name = pattern.format(n=i, name=name, ext=ext.lstrip("."), date=today)
        _check_filename(new_name)
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        if old_path != new_path:
            planned.append((old_path, new_path))

    source_paths = {os.path.normcase(old) for old, _ in planned}
    target_paths = [os.path.normcase(new) for _, new in planned]
    if len(target_paths) != len(set(target_paths)):
        raise FileExistsError("Multiple files would be renamed to the same destination")
    for _, target in planned:
        if os.path.lexists(target) and os.path.normcase(target) not in source_paths:
            raise FileExistsError(f"Destination already exists: {target}")

    if dry_run or not planned:
        return planned

    staged = []
    try:
        for source, target in planned:
            fd, temporary = tempfile.mkstemp(prefix=".devkit-rename-", dir=directory)
            os.close(fd)
            os.unlink(temporary)
            os.rename(source, temporary)
            staged.append((source, temporary, target))
        for _, temporary, target in staged:
            if os.path.lexists(target):
                raise FileExistsError(f"Destination appeared during rename: {target}")
            os.rename(temporary, target)
    except Exception:
        # Recover previously moved destinations into their staging slots.
        for _, temporary, target in reversed(staged):
            if not os.path.lexists(temporary) and os.path.lexists(target):
                os.rename(target, temporary)
        for source, temporary, _ in reversed(staged):
            if os.path.lexists(temporary):
                os.rename(temporary, source)
        raise
    return planned

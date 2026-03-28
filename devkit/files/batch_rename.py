"""Batch file renaming with pattern templates."""

import os
from datetime import datetime
from typing import List, Optional, Tuple


def batch_rename(directory: str, pattern: str, filter_ext: Optional[str] = None, dry_run: bool = True) -> List[Tuple[str, str]]:
    """Rename files in a directory using a pattern template.

    Supported placeholders: {n} or {n:03d}, {name}, {ext}, {date}
    """
    if not os.path.isdir(directory):
        return []
    files = sorted(os.listdir(directory))
    files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
    if filter_ext:
        files = [f for f in files if f.endswith(f".{filter_ext}")]
    renames = []
    today = datetime.now().strftime("%Y-%m-%d")
    for i, filename in enumerate(files, start=1):
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip(".")
        new_name = pattern.format(n=i, name=name, ext=ext, date=today)
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        renames.append((old_path, new_path))
    if not dry_run:
        for old_path, new_path in renames:
            os.rename(old_path, new_path)
    return renames

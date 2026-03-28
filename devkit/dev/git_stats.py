"""Git repository statistics."""

import os
import subprocess
from typing import Dict, List, Optional


def _run_git(args: List[str], cwd: str = ".") -> Optional[str]:
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, cwd=cwd, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_stats(path: str = ".") -> dict:
    """Get repository statistics."""
    if not os.path.isdir(path):
        return {"error": f"Directory not found: {path}"}
    commit_count = _run_git(["rev-list", "--count", "HEAD"], cwd=path)
    if commit_count is None:
        return {"error": f"Not a git repository: {path}"}
    contributors_raw = _run_git(["shortlog", "-sn", "--all", "--no-merges"], cwd=path)
    contributors = []
    if contributors_raw:
        for line in contributors_raw.split("\n"):
            line = line.strip()
            if line:
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    contributors.append({"commits": int(parts[0].strip()), "name": parts[1].strip()})
    file_count_raw = _run_git(["ls-files"], cwd=path)
    file_count = len(file_count_raw.split("\n")) if file_count_raw else 0
    return {"total_commits": int(commit_count), "contributors": contributors, "file_count": file_count}


def top_contributors(path: str = ".", n: int = 10) -> List[dict]:
    """Get top N contributors by commit count."""
    stats = get_stats(path)
    if "error" in stats:
        return []
    return stats["contributors"][:n]


def commit_frequency(path: str = ".", days: int = 30) -> Dict[str, int]:
    """Get commit count per day for the last N days."""
    raw = _run_git(["log", f"--since={days} days ago", "--format=%cd", "--date=short"], cwd=path)
    if not raw:
        return {}
    freq: Dict[str, int] = {}
    for date in raw.split("\n"):
        date = date.strip()
        if date:
            freq[date] = freq.get(date, 0) + 1
    return freq

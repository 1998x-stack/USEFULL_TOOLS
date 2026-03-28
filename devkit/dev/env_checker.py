"""Check development environment for required tools."""

import shutil
import subprocess
from typing import Dict, List, Optional


DEFAULT_TOOLS = ["python", "python3", "pip", "git", "node", "npm", "docker", "ffmpeg"]


def _get_version(tool: str) -> Optional[str]:
    """Get version string for a tool."""
    version_flags = {"python": "--version", "python3": "--version", "pip": "--version",
                     "git": "--version", "node": "--version", "npm": "--version",
                     "docker": "--version", "ffmpeg": "-version", "java": "-version",
                     "go": "version", "rustc": "--version", "cargo": "--version"}
    flag = version_flags.get(tool, "--version")
    try:
        result = subprocess.run([tool, flag], capture_output=True, text=True, timeout=5)
        output = result.stdout.strip() or result.stderr.strip()
        return output.split("\n")[0] if output else "installed"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def check_environment(tools: Optional[List[str]] = None) -> Dict[str, dict]:
    """Check if development tools are installed and get their versions."""
    if tools is None:
        tools = DEFAULT_TOOLS
    results = {}
    for tool in tools:
        path = shutil.which(tool)
        if path:
            version = _get_version(tool)
            results[tool] = {"found": True, "version": version or "unknown", "path": path}
        else:
            results[tool] = {"found": False, "version": None, "path": None}
    return results


def format_report(results: Dict[str, dict]) -> str:
    """Format environment check results as a readable string."""
    lines = ["Development Environment Check", "=" * 40]
    for tool, info in results.items():
        status = "OK" if info["found"] else "MISSING"
        version = info.get("version", "") or ""
        lines.append(f"  [{status:>7}] {tool:<12} {version}")
    found = sum(1 for v in results.values() if v["found"])
    lines.append(f"\n{found}/{len(results)} tools found.")
    return "\n".join(lines)

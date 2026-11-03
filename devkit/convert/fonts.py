"""CJK font discovery, fallback selection and glyph preflight.

Font binaries remain system-owned; no licensed fonts are vendored with devkit.
"""

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass(frozen=True)
class FontChoice:
    family: str
    path: str
    index: int
    coverage_checked: int


_PREFERENCES = (
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "Noto Sans CJK KR",
    "Source Han Sans SC",
    "WenQuanYi Micro Hei",
    "Droid Sans Fallback",
)


def is_cjk(char: str) -> bool:
    number = ord(char)
    return (
        0x3400 <= number <= 0x9FFF
        or 0xF900 <= number <= 0xFAFF
        or 0x20000 <= number <= 0x2FA1F
        or 0x3040 <= number <= 0x30FF
        or 0xAC00 <= number <= 0xD7AF
        or 0x3000 <= number <= 0x303F
    )


def _font_characters(path: str, index: int) -> set:
    """Inspect the actual CMap; a fontconfig substitution is not sufficient."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        raise ImportError("fonttools is required: pip install -e '.[convert]'") from exc

    font = TTFont(path, fontNumber=index, lazy=True)
    try:
        codes = set()
        for table in font["cmap"].tables:
            if table.isUnicode():
                codes.update(table.cmap)
        return codes
    finally:
        font.close()


def _fontconfig_match(family: str) -> Optional[Tuple[str, str, int]]:
    binary = shutil.which("fc-match")
    if not binary:
        return None
    result = subprocess.run(
        [binary, "--format", "%{family}\n%{file}\n%{index}\n", family],
        capture_output=True, text=True, timeout=10, check=False,
    )
    if result.returncode != 0:
        return None
    lines = result.stdout.splitlines()
    if len(lines) < 2 or not Path(lines[1]).is_file():
        return None
    try:
        index = int(lines[2]) if len(lines) > 2 and lines[2] else 0
    except ValueError:
        index = 0
    return lines[0].split(",")[0], lines[1], index


def choose_cjk_font(text: str, preferred_family: Optional[str] = None) -> Optional[FontChoice]:
    """Find an installed font covering all CJK characters in the input.

    For Latin-only input, return None and allow the platform's default fonts.
    For CJK input, fail closed when adequate installed font coverage cannot be
    demonstrated. Font discovery currently requires fontconfig.
    """
    wanted = {ord(char) for char in text if is_cjk(char)}
    if not wanted:
        return None
    if not shutil.which("fc-match"):
        raise RuntimeError(
            "CJK font discovery requires fontconfig (fc-match) and an installed CJK font"
        )
    families = (preferred_family,) if preferred_family else _PREFERENCES
    seen = set()
    candidates = []
    for family in families:
        match = _fontconfig_match(family)
        if not match:
            continue
        matched_family, path, index = match
        if (path, index) in seen:
            continue
        seen.add((path, index))
        try:
            covered = _font_characters(path, index)
        except (OSError, KeyError, ValueError):
            continue
        missing = wanted - covered
        if not missing:
            return FontChoice(
                family=matched_family, path=path, index=index, coverage_checked=len(wanted)
            )
        candidates.append((matched_family, len(missing)))
    hint = ", ".join(f"{name}: {missing} missing" for name, missing in candidates) or "no installed CJK fonts"
    raise ValueError(f"Unable to find a CJK font with complete glyph coverage ({hint})")

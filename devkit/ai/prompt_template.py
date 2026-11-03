"""Prompt template manager with name validation and Jinja2 support."""

import os
import re
from typing import Dict, List, Optional

DEFAULT_PROMPTS_DIR = os.path.expanduser("~/.devkit/prompts")
_TEMPLATE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")


def render_template(template: str, variables: Dict[str, str]) -> str:
    if "{%" in template or "{{" in template:
        try:
            from jinja2.sandbox import SandboxedEnvironment
            return SandboxedEnvironment(autoescape=False).from_string(template).render(**variables)
        except ImportError:
            pass
    return template.format(**variables)


def _template_path(name: str, prompts_dir: Optional[str]) -> str:
    if not isinstance(name, str) or _TEMPLATE_NAME.fullmatch(name) is None:
        raise ValueError("Template name must contain only letters, digits, hyphens, or underscores")
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    path = os.path.join(directory, f"{name}.txt")
    if os.path.islink(path):
        raise ValueError("Symbolic-link templates are not supported")
    return path


def save_template(name: str, content: str, prompts_dir: Optional[str] = None) -> str:
    path = _template_path(name, prompts_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Refuse symlinks even if one appeared between validation and opening.
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(content)
    return path


def load_template(name: str, prompts_dir: Optional[str] = None) -> Optional[str]:
    path = _template_path(name, prompts_dir)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as stream:
        return stream.read()


def list_templates(prompts_dir: Optional[str] = None) -> List[str]:
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    if not os.path.isdir(directory):
        return []
    return sorted(f[:-4] for f in os.listdir(directory)
                  if f.endswith(".txt") and _TEMPLATE_NAME.fullmatch(f[:-4])
                  and not os.path.islink(os.path.join(directory, f)))

"""Prompt template manager with Jinja2 support."""

import os
from typing import Dict, List, Optional

DEFAULT_PROMPTS_DIR = os.path.expanduser("~/.devkit/prompts")


def render_template(template: str, variables: Dict[str, str]) -> str:
    if "{%" in template or "{{" in template:
        try:
            from jinja2 import Template
            j2 = Template(template)
            return j2.render(**variables)
        except ImportError:
            pass
    return template.format(**variables)


def save_template(name: str, content: str, prompts_dir: Optional[str] = None) -> str:
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def load_template(name: str, prompts_dir: Optional[str] = None) -> Optional[str]:
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    path = os.path.join(directory, f"{name}.txt")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_templates(prompts_dir: Optional[str] = None) -> List[str]:
    directory = prompts_dir or DEFAULT_PROMPTS_DIR
    if not os.path.isdir(directory):
        return []
    return [f.rsplit(".", 1)[0] for f in os.listdir(directory) if f.endswith(".txt")]

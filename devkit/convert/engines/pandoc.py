"""Explicit Pandoc reader/writer pipeline for structure-aware DOCX conversion."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

from devkit.convert.ir import DocumentIR, from_pandoc_ast


class PandocEngine:
    def __init__(self, executable=None, timeout=120):
        self.executable = executable or shutil.which("pandoc")
        if not self.executable:
            raise FileNotFoundError("Pandoc binary not found. Install pandoc to convert Markdown to DOCX.")
        self.timeout = timeout

    def _run(self, args, *, content=None):
        completed = subprocess.run(
            [self.executable] + list(args),
            input=content, capture_output=True, text=True,
            encoding="utf-8", timeout=self.timeout, check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[-1500:]
            raise RuntimeError(f"Pandoc failed (exit {completed.returncode}): {detail}")
        return completed.stdout

    def parse_markdown(self, source) -> DocumentIR:
        source = Path(source).absolute()
        if not source.is_file():
            raise FileNotFoundError(str(source))
        ast_json = self._run(["--from=gfm", "--to=json", str(source)])
        try:
            return from_pandoc_ast(json.loads(ast_json))
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Invalid Pandoc reader output: {exc}") from exc

    @staticmethod
    def check_local_media(document: DocumentIR, source) -> None:
        """Allow images only from the Markdown file's own directory tree.

        Forbid remote images (network access), data URIs, absolute paths, and
        symlink escapes. Ordinary HTTP hyperlinks do not fetch any resources.
        """
        root = Path(source).absolute().parent.resolve()
        for target in document.image_sources:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith(("/", "\\")):
                raise ValueError(f"Unsupported external or absolute image reference: {target}")
            local = (root / unquote(parsed.path)).resolve()
            if os.path.commonpath((str(root), str(local))) != str(root):
                raise ValueError(f"Image reference escapes source directory: {target}")
            if not local.is_file():
                raise FileNotFoundError(f"Referenced image not found: {target}")

    def write_docx(self, document: DocumentIR, output_path, source, reference_doc=None) -> None:
        source = Path(source).absolute()
        self.check_local_media(document, source)
        args = [
            "--from=json", "--to=docx",
            "--resource-path=" + str(source.parent),
            "--output", str(output_path),
        ]
        if reference_doc is not None:
            reference = Path(reference_doc).absolute()
            if not reference.is_file():
                raise FileNotFoundError(f"Reference DOCX not found: {reference}")
            args.extend(["--reference-doc", str(reference)])
        self._run(args, content=document.ast_json)
        if not Path(output_path).is_file():
            raise RuntimeError("Pandoc exited successfully but did not produce a DOCX file")

"""Shared output guards for data-processing commands.

Successful writes replace the output atomically on the same filesystem.
This is not a multi-file transaction or protection from concurrent writers.
"""

import os
import tempfile
from contextlib import contextmanager
from typing import Iterable, Iterator, TextIO


def ensure_distinct_output(output: str, inputs: Iterable[str] = ()) -> None:
    """Reject output aliases and symlink destinations before writing."""
    if os.path.islink(output):
        raise ValueError(f"Refusing symbolic-link output: {output}")
    resolved = os.path.realpath(output)
    for source in inputs:
        if os.path.realpath(source) == resolved or (
            os.path.exists(output) and os.path.exists(source) and os.path.samefile(output, source)
        ):
            raise ValueError(f"Output must differ from input: {output}")


@contextmanager
def atomic_text_output(output: str, inputs: Iterable[str] = (), newline=None) -> Iterator[TextIO]:
    """Write to a sibling temp file and publish only after successful validation."""
    sources = tuple(inputs)
    ensure_distinct_output(output, sources)
    parent = os.path.dirname(os.path.abspath(output))
    os.makedirs(parent, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".devkit-write-", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline=newline) as stream:
            yield stream
            stream.flush()
            os.fsync(stream.fileno())
        # Also protect against a destination replaced with an alias meanwhile.
        ensure_distinct_output(output, sources)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

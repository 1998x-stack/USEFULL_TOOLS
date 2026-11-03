"""Validated, streaming CSV operations with safe output publication."""

import csv
import json
import os
import tempfile
from typing import Iterator, List, TextIO

from devkit.data.io import atomic_text_output
from devkit.data.json_utils import reject_duplicate_pairs, reject_nonfinite_constant


def _read_header(reader, source: str) -> List[str]:
    try:
        header = next(reader)
    except StopIteration as exc:
        raise ValueError(f"Empty CSV file: {source}") from exc
    if not header or any(not name.strip() for name in header):
        raise ValueError(f"CSV header contains an empty column name: {source}")
    if len(header) != len(set(header)):
        raise ValueError(f"CSV header contains duplicate column names: {source}")
    return header


def _checked_rows(reader, header: List[str], source: str) -> Iterator[List[str]]:
    for row in reader:
        if len(row) != len(header):
            raise ValueError(
                f"CSV column count mismatch in {source}, record ending on line {reader.line_num}: "
                f"expected {len(header)}, found {len(row)}"
            )
        yield row


def merge_csvs(files: List[str], output: str) -> None:
    """Merge compatible CSV files; validate exact header order and row widths."""
    if not files:
        raise ValueError("At least one CSV input is required")
    with atomic_text_output(output, files, newline="") as out:
        writer = csv.writer(out)
        expected = None
        for path in files:
            with open(path, "r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream, strict=True)
                header = _read_header(reader, path)
                if expected is None:
                    expected = header
                    writer.writerow(header)
                elif header != expected:
                    raise ValueError(
                        f"CSV header mismatch in {path}: expected {expected!r}, found {header!r}"
                    )
                writer.writerows(_checked_rows(reader, expected, path))


def split_csv(file: str, rows_per_file: int, output_dir: str) -> List[str]:
    """Stream into staged chunks; refuse to overwrite any existing part file.

    The commit uses hard links to publish each prepared file without overwrite.
    If publication fails, newly published parts are removed on a best-effort
    basis; concurrent directory mutation or abrupt process exit is not atomic.
    """
    if rows_per_file <= 0:
        raise ValueError("rows_per_file must be positive")
    os.makedirs(output_dir, exist_ok=True)
    published = []
    with tempfile.TemporaryDirectory(prefix=".devkit-split-", dir=output_dir) as staging:
        staged = []
        with open(file, "r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = _read_header(reader, file)
            part_stream = None
            try:
                for index, row in enumerate(_checked_rows(reader, header, file)):
                    if index % rows_per_file == 0:
                        if part_stream is not None:
                            part_stream.close()
                        name = f"part_{len(staged) + 1:03d}.csv"
                        source = os.path.join(staging, name)
                        destination = os.path.join(output_dir, name)
                        staged.append((source, destination))
                        part_stream = open(source, "w", encoding="utf-8", newline="")
                        writer = csv.writer(part_stream)
                        writer.writerow(header)
                    writer.writerow(row)
            finally:
                if part_stream is not None:
                    part_stream.close()

        for _, destination in staged:
            if os.path.lexists(destination):
                raise FileExistsError(f"Refusing to overwrite existing CSV chunk: {destination}")
        try:
            for source, destination in staged:
                os.link(source, destination)
                published.append((source, destination))
        except BaseException:
            for source, destination in reversed(published):
                if os.path.lexists(destination) and os.path.samefile(source, destination):
                    os.unlink(destination)
            raise
        return [destination for _, destination in staged]


def csv_to_json(file: str, output: str) -> None:
    """Convert validated CSV to a JSON array without collecting rows in memory."""
    with open(file, "r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = _read_header(reader, file)
        with atomic_text_output(output, [file]) as out:
            out.write("[")
            for index, row in enumerate(_checked_rows(reader, header, file)):
                out.write(",\n" if index else "\n")
                json.dump(dict(zip(header, row)), out, ensure_ascii=False)
            out.write("\n]\n")


def _iter_json_array(stream: TextIO, chunk_size: int = 65536) -> Iterator[dict]:
    """Read a top-level JSON array incrementally using the stdlib decoder."""
    decoder = json.JSONDecoder(
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_nonfinite_constant,
    )
    buffer = ""
    offset = 0
    eof = False
    limit = 32 * 1024 * 1024

    def load_more():
        nonlocal buffer, offset, eof
        buffer = buffer[offset:]
        offset = 0
        next_chunk = stream.read(chunk_size)
        if next_chunk:
            buffer += next_chunk
        else:
            eof = True

    def peek():
        nonlocal offset
        while True:
            while offset < len(buffer) and buffer[offset].isspace():
                offset += 1
            if offset < len(buffer):
                return buffer[offset]
            if eof:
                return None
            load_more()

    if peek() != "[":
        raise ValueError("Expected a JSON array")
    offset += 1
    if peek() == "]":
        offset += 1
        if peek() is not None:
            raise ValueError("Trailing content after JSON array")
        return

    while True:
        while True:
            try:
                item, ending = decoder.raw_decode(buffer, offset)
                offset = ending
                break
            except json.JSONDecodeError as exc:
                if eof:
                    raise ValueError(f"Invalid JSON array item: {exc}") from exc
                if len(buffer) - offset > limit:
                    raise ValueError("JSON array item exceeds 32 MiB limit") from exc
                load_more()
        if not isinstance(item, dict):
            raise ValueError("JSON array must contain only objects")
        yield item
        marker = peek()
        if marker == "]":
            offset += 1
            if peek() is not None:
                raise ValueError("Trailing content after JSON array")
            return
        if marker != ",":
            raise ValueError("Expected comma or closing bracket in JSON array")
        offset += 1
        if peek() in (None, "]"):
            raise ValueError("Trailing comma or incomplete JSON array")


def _cell(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def json_to_csv(file: str, output: str) -> None:
    """Stream a JSON array of equally shaped objects into CSV.

    An empty array is rejected because no column schema can be inferred.
    """
    with open(file, "r", encoding="utf-8-sig") as stream:
        with atomic_text_output(output, [file], newline="") as out:
            writer = csv.writer(out)
            fieldnames = None
            for index, item in enumerate(_iter_json_array(stream), start=1):
                if fieldnames is None:
                    fieldnames = list(item)
                    if not fieldnames:
                        raise ValueError("JSON objects require at least one key for CSV")
                    writer.writerow(fieldnames)
                elif set(item) != set(fieldnames):
                    raise ValueError(f"JSON object {index} has a different field schema")
                writer.writerow([_cell(item[key]) for key in fieldnames])
            if fieldnames is None:
                raise ValueError("Empty JSON array: cannot infer CSV columns")

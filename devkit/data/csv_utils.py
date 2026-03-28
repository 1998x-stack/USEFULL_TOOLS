"""CSV processing utilities."""

import csv
import json
import os
from typing import List


def merge_csvs(files: List[str], output: str) -> None:
    """Merge multiple CSV files into one (assumes same headers)."""
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    header_written = False
    with open(output, "w", newline="", encoding="utf-8") as out:
        writer = None
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                if not header_written:
                    writer = csv.writer(out)
                    writer.writerow(header)
                    header_written = True
                for row in reader:
                    writer.writerow(row)


def split_csv(file: str, rows_per_file: int, output_dir: str) -> List[str]:
    """Split a large CSV into smaller files."""
    os.makedirs(output_dir, exist_ok=True)
    output_files = []
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        file_index = 1
        current_rows: list = []
        for row in reader:
            current_rows.append(row)
            if len(current_rows) >= rows_per_file:
                out_path = os.path.join(output_dir, f"part_{file_index:03d}.csv")
                _write_csv(out_path, header, current_rows)
                output_files.append(out_path)
                current_rows = []
                file_index += 1
        if current_rows:
            out_path = os.path.join(output_dir, f"part_{file_index:03d}.csv")
            _write_csv(out_path, header, current_rows)
            output_files.append(out_path)
    return output_files


def _write_csv(path: str, header: list, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def csv_to_json(file: str, output: str) -> None:
    """Convert CSV to JSON array."""
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def json_to_csv(file: str, output: str) -> None:
    """Convert JSON array to CSV."""
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        return
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    fieldnames = list(data[0].keys())
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

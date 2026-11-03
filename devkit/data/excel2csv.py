"""Excel to CSV converter with streamed rows and atomic output."""

import csv
from typing import List, Optional

from devkit.data.io import atomic_text_output


def _load_workbook(path: str):
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise ImportError("openpyxl is required: pip install -e '.[data]'") from exc
    return load_workbook(path, read_only=True)


def list_sheets(file: str) -> List[str]:
    """List sheet names in an Excel file."""
    wb = _load_workbook(file)
    try:
        return list(wb.sheetnames)
    finally:
        wb.close()


def excel_to_csv(file: str, output: str, sheet: Optional[str] = None) -> None:
    """Convert the chosen sheet to CSV without loading all rows into memory."""
    wb = _load_workbook(file)
    try:
        ws = wb[sheet] if sheet else wb.active
        with atomic_text_output(output, [file], newline="") as out:
            writer = csv.writer(out)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(row)
    finally:
        wb.close()

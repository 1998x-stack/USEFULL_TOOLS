"""Media conversion tools."""

import os
import shutil
import subprocess
from typing import Optional


def mp4_to_mp3(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg is required but not found.")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".mp3"
    result = subprocess.run(
        ["ffmpeg", "-i", input_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", output_path, "-y"],
        capture_output=True,
    )
    return output_path if result.returncode == 0 else None


def webp_to_png(input_path: str, output_path: Optional[str] = None) -> Optional[str]:
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow is required: pip install devkit-tools[convert]")
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".png"
    try:
        img = Image.open(input_path)
        img.save(output_path, "PNG")
        return output_path
    except Exception:
        return None


def resize_image(input_path: str, size: str, output_path: Optional[str] = None) -> Optional[str]:
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow is required: pip install devkit-tools[convert]")
    if not os.path.isfile(input_path):
        return None
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_resized{ext}"
    if "x" in size:
        width, height = map(int, size.split("x"))
    else:
        width = height = int(size)
    try:
        img = Image.open(input_path)
        img = img.resize((width, height))
        img.save(output_path)
        return output_path
    except Exception:
        return None

"""Independent fixed-baseline visual evaluation for rendered PDF documents.

Baseline assets are immutable during verification. Candidate images must be
reviewed and separately committed before becoming approved reference assets.
"""

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageStat


@dataclass(frozen=True)
class RegionMetric:
    name: str
    page: int
    changed_fraction: float
    mean_absolute_error: float
    passed: bool


@dataclass(frozen=True)
class PageMetric:
    page: int
    changed_fraction: float
    mean_absolute_error: float
    passed: bool
    regions: tuple


def inspect_line_overlaps(path, minimum_ratio=0.25):
    """Detect substantive overlap of separately laid-out text lines.

    The PDF text extractor is independent of the source Markdown. A tiny
    intersection caused by font ascent/descent is ignored; only a shared
    rectangle covering >= minimum_ratio of the smaller line is reported.
    """
    if not 0 < minimum_ratio <= 1:
        raise ValueError("minimum_ratio must be in (0,1]")
    findings = []
    with fitz.open(str(path)) as pdf:
        for page_index, page in enumerate(pdf, 1):
            lines = []
            for block in page.get_text("dict")["blocks"]:
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    if line.get("spans"):
                        rect = fitz.Rect(line["bbox"])
                        if rect.get_area() > 0:
                            lines.append(rect)
            for i, left in enumerate(lines):
                for right in lines[i + 1:]:
                    intersection = left & right
                    area = intersection.get_area()
                    if area < 12:
                        continue
                    ratio = area / min(left.get_area(), right.get_area())
                    if ratio >= minimum_ratio:
                        findings.append({
                            "page": page_index,
                            "intersection_ratio": round(ratio, 4),
                            "left": list(left),
                            "right": list(right),
                        })
    return findings


def _digest(path):
    digest = hashlib.sha256()
    with open(path, "rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_environment(font=None):
    """Stable renderer fingerprint, avoiding host-dependent absolute paths."""
    def version(command):
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=20, check=True,
        )
        return result.stdout.splitlines()[0].strip()

    return {
        "pandoc": version(["pandoc", "--version"]),
        "libreoffice": version(["libreoffice", "--version"]),
        "pymupdf": fitz.VersionBind,
        "font_family": font.family if font is not None else None,
        "font_index": font.index if font is not None else None,
        "font_sha256": _digest(font.path) if font is not None else None,
    }


def render_pages(path, dpi=96, max_pages=8):
    """Rasterize using fixed RGB, alpha and scale. Bound malicious inputs."""
    if not 72 <= dpi <= 180:
        raise ValueError("DPI outside supported [72, 180] range")
    with fitz.open(str(path)) as pdf:
        if not 1 <= pdf.page_count <= max_pages:
            raise ValueError(f"Unexpected page count {pdf.page_count}; maximum {max_pages}")
        output = []
        for page in pdf:
            pix = page.get_pixmap(
                matrix=fitz.Matrix(dpi / 72, dpi / 72),
                colorspace=fitz.csRGB, alpha=False,
                annots=False,
            )
            if pix.width * pix.height > 5_000_000:
                raise ValueError("Rendered page exceeds 5 million pixels")
            output.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    return output


def compare_images(reference, actual, *, pixel_threshold=28, max_fraction=0.008, max_mean_error=2.5):
    """Compare pixels without alignment so shifts are detectable.

    Returns normalized changed-pixel ratio, raw per-channel absolute mean,
    passed flag and an RGB diagnostic image with changed regions red.
    """
    reference = reference.convert("RGB")
    actual = actual.convert("RGB")
    if reference.size != actual.size:
        raise ValueError(f"Different raster dimensions: {reference.size} vs {actual.size}")
    if not 1 <= pixel_threshold <= 255:
        raise ValueError("pixel_threshold must be in [1,255]")
    if not 0 <= max_fraction <= 1 or not 0 <= max_mean_error <= 255:
        raise ValueError("Invalid comparison thresholds")
    delta = ImageChops.difference(reference, actual)
    r, g, b = delta.split()
    max_channel = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mask = max_channel.point(lambda n: 255 if n >= pixel_threshold else 0)
    changed = mask.histogram()[255] / (reference.width * reference.height)
    mae = sum(ImageStat.Stat(delta).mean) / 3
    passed = changed <= max_fraction and mae <= max_mean_error
    marked = Image.composite(Image.new("RGB", actual.size, (245, 45, 48)), actual, mask)
    return changed, mae, passed, marked


def _clip_rect(region, size):
    values = region["rect"]
    if not isinstance(values, list) or len(values) != 4:
        raise ValueError("Region requires normalized rect [x0,y0,x1,y1]")
    x0, y0, x1, y1 = values
    if not all(isinstance(v, (float, int)) for v in values):
        raise ValueError("Region must contain numeric coordinates")
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ValueError(f"Invalid normalized region: {values}")
    width, height = size
    return (
        int(x0 * width), int(y0 * height),
        max(int(x0 * width) + 1, int(x1 * width)),
        max(int(y0 * height) + 1, int(y1 * height)),
    )


def compare_page(reference, actual, page_number, config, regions):
    changed, mae, good, overlay = compare_images(
        reference, actual,
        pixel_threshold=config["pixel_threshold"],
        max_fraction=config["max_changed_fraction"],
        max_mean_error=config["max_mean_error"],
    )
    details = []
    for region in regions:
        if region["page"] != page_number:
            continue
        rect = _clip_rect(region, actual.size)
        percent, error, passed, _ = compare_images(
            reference.crop(rect), actual.crop(rect),
            pixel_threshold=config["pixel_threshold"],
            max_fraction=region.get("max_changed_fraction", config["max_changed_fraction"]),
            max_mean_error=region.get("max_mean_error", config["max_mean_error"]),
        )
        details.append(RegionMetric(region["name"], page_number, percent, error, passed))
    good = good and all(item.passed for item in details)
    return PageMetric(page_number, changed, mae, good, tuple(details)), overlay


def validate_manifest(manifest):
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported golden manifest schema version")
    if not isinstance(manifest.get("cases"), list) or not manifest["cases"]:
        raise ValueError("Golden manifest requires non-empty cases")
    config = manifest.get("render")
    if not isinstance(config, dict):
        raise ValueError("Golden manifest missing render configuration")
    for key in ("dpi", "max_pages", "pixel_threshold", "max_changed_fraction", "max_mean_error"):
        if key not in config:
            raise ValueError(f"Golden render setting missing: {key}")
    identifiers = [x.get("id") for x in manifest["cases"]]
    if any(not isinstance(i, str) or not i.replace("-", "").isalnum() for i in identifiers):
        raise ValueError("Golden IDs must be simple alphanumeric/dash slugs")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Duplicate golden case ID")
    return manifest


def load_manifest(path):
    with open(path, encoding="utf-8") as source:
        return validate_manifest(json.load(source))


def evaluate_pages(case, rendered_pages, manifest, approved_dir, artifact_dir):
    """Compare against hash-verified, separately approved, checked-in snapshots."""
    config = manifest["render"]
    expected_count = case.get("expected_pages")
    if not isinstance(expected_count, int) or expected_count < 1:
        raise ValueError(f"No approved page count for {case['id']}")
    if len(rendered_pages) != expected_count:
        raise ValueError(
            f"{case['id']}: pagination regression ({len(rendered_pages)} actual, {expected_count} approved)"
        )
    expected_hashes = case.get("sha256")
    if not isinstance(expected_hashes, list) or len(expected_hashes) != expected_count:
        raise ValueError(f"{case['id']}: approved PNG SHA-256 list incomplete")
    metrics = []
    for index, current in enumerate(rendered_pages):
        name = f"{case['id']}-p{index + 1:02d}.png"
        reference_path = approved_dir / name
        if not reference_path.is_file():
            raise FileNotFoundError(f"Approved golden PNG missing: {reference_path}")
        if _digest(reference_path) != expected_hashes[index]:
            raise ValueError(f"Golden asset changed without approval: {name}")
        with Image.open(reference_path) as opened:
            reference = opened.convert("RGB")
        metric, marked = compare_page(reference, current, index + 1, config, case.get("regions", []))
        current.save(artifact_dir / f"{case['id']}-p{index + 1:02d}-actual.png", optimize=True)
        marked.save(artifact_dir / f"{case['id']}-p{index + 1:02d}-diff.png", optimize=True)
        metrics.append(metric)
    return {
        "id": case["id"],
        "status": "pass" if all(item.passed for item in metrics) else "fail",
        "pages": [asdict(item) for item in metrics],
    }


def save_report(report, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # HTML only contains escaped, fixed-schema report content, never input HTML.
    import html
    cells = []
    for case in report.get("cases", []):
        name, status = html.escape(str(case.get("id", ""))), html.escape(str(case.get("status", "")))
        reason = html.escape(str(case.get("error", "")))
        cells.append(f"<tr><td>{name}</td><td>{status}</td><td>{reason}</td></tr>")
        for page in case.get("pages", []):
            page_name = f"{name}-p{page['page']:02d}"
            cells.append(
                f"<tr><td>{name} page {page['page']} "
                f"<a href='{page_name}-actual.png'>actual</a> / "
                f"<a href='{page_name}-diff.png'>diff</a></td>"
                f"<td>{'PASS' if page['passed'] else 'FAIL'}</td>"
                f"<td>changed={page['changed_fraction']:.6f}, mae={page['mean_absolute_error']:.3f}</td></tr>"
            )
            for region in page.get("regions", []):
                cells.append(
                    f"<tr><td>{name}: page {page['page']} / {html.escape(region['name'])}</td>"
                    f"<td>{'PASS' if region['passed'] else 'FAIL'}</td>"
                    f"<td>changed={region['changed_fraction']:.6f}, mae={region['mean_absolute_error']:.3f}</td></tr>"
                )
    content = (
        "<!doctype html><html><head><meta charset='utf-8'><title>Visual regression report</title>"
        "<style>body{font-family:system-ui;margin:2rem}td,th{border:1px solid #ccc;"
        "padding:.5rem}table{border-collapse:collapse}tr:nth-child(even){background:#eee}</style>"
        "</head><body><h1>V0.4-D PDF Visual Regression</h1><p>Result: "
        + html.escape(report.get("status", "unknown"))
        + "</p><table><tr><th>Fixture / region</th><th>Status</th><th>Detail</th></tr>"
        + "".join(cells) + "</table></body></html>"
    )
    (out_dir / "report.html").write_text(content, encoding="utf-8")
    return report_path

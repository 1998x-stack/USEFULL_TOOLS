"""Candidate capture and approved golden verification CLI.

Use 'candidate' only to prepare screenshots for human review. It NEVER writes
approved assets. 'verify' is read-only for baselines and exits nonzero on drift.
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from devkit.convert.fonts import choose_cjk_font
from devkit.convert.md2pdf import markdown_to_pdf
from devkit.convert.visual import (
    current_environment, evaluate_pages, inspect_line_overlaps, load_manifest, render_pages, save_report, _digest,
)
from devkit.convert.validate.pdf_quality import expected_text_from_ast
from devkit.convert.engines import PandocEngine


def run_suite(manifest_path, out_dir, mode, emit_base64=False):
    manifest_path = Path(manifest_path).absolute()
    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    out_dir = Path(out_dir).absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    golden_root = root / "approved"
    config = manifest["render"]
    baseline_lock = root / "baseline.lock.json"
    result = {"schema_version": 1, "mode": mode, "cases": [], "status": "pass"}
    for case in manifest["cases"]:
        identifier = case["id"]
        try:
            markdown = (root / case["markdown"]).resolve()
            if root.resolve() != markdown and root.resolve() not in markdown.parents:
                raise ValueError("Markdown path outside golden fixture root")
            doc = PandocEngine().parse_markdown(markdown)
            expected = expected_text_from_ast(doc.to_pandoc_ast())
            font = choose_cjk_font(expected)
            environment = current_environment(font)
            if mode == "verify":
                if not baseline_lock.is_file():
                    raise FileNotFoundError("Baseline lock missing; review and approve candidate first")
                lock = json.loads(baseline_lock.read_text(encoding="utf-8"))
                if environment != lock["environment"]:
                    raise ValueError("Renderer/font environment drift; approve a new baseline explicitly")
            target = out_dir / (identifier + ".pdf")
            markdown_to_pdf(str(markdown), str(target))
            pages = render_pages(target, dpi=config["dpi"], max_pages=config["max_pages"])
            overlaps = inspect_line_overlaps(target)
            if overlaps and mode == "verify":
                raise ValueError(
                    f"{identifier}: {len(overlaps)} substantive overlapping text-line pair(s)"
                )
            if emit_base64 and mode == "candidate":
                print(f"GOLDENOVERLAPS:{identifier}:{json.dumps(overlaps)}", flush=True)
            if mode == "candidate":
                hashes = []
                for index, page in enumerate(pages, 1):
                    name = f"{identifier}-p{index:02d}.png"
                    file = out_dir / name
                    page.save(file, optimize=True)
                    hashes.append(_digest(file))
                    if emit_base64:
                        print(f"GOLDENHASH:{name}:{hashes[-1]}", flush=True)
                        encoded = base64.b64encode(file.read_bytes()).decode("ascii")
                        print(f"GOLDENPNG:{name}:{encoded}", flush=True)
                if emit_base64:
                    print(f"GOLDENENV:{json.dumps(environment, sort_keys=True)}", flush=True)
                result["cases"].append({
                    "id": identifier, "status": "candidate", "expected_pages": len(pages),
                    "sha256": hashes, "environment": environment, "overlaps": overlaps,
                })
            else:
                result["cases"].append(evaluate_pages(case, pages, manifest, golden_root, out_dir))
        except Exception as exc:
            result["status"] = "fail"
            result["cases"].append({"id": identifier, "status": "fail", "error": str(exc)})
    save_report(result, out_dir)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate or verify PDF visual golden evidence")
    parser.add_argument("command", choices=("candidate", "verify"))
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Print candidate images for explicit GitHub baseline approval")
    args = parser.parse_args(argv)
    if args.emit_base64 and args.command != "candidate":
        parser.error("--emit-base64 only allowed in candidate mode")
    report = run_suite(args.manifest, args.out_dir, args.command, args.emit_base64)
    print(json.dumps({
        "mode": args.command, "status": report["status"],
        "cases": [{"id": c["id"], "status": c["status"], "error": c.get("error")} for c in report["cases"]],
    }, ensure_ascii=False))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())

"""Conversion quality profiles, evidence, and failure-safe publication.

All profiles retain converter-level safety gates. A strict PDF succeeds only
with an independently approved visual baseline; it never quietly downgrades
to text-only inspection.
"""

import hashlib
import json
import tempfile
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from devkit.convert._safe import publish_file, require_distinct, validate_docx, validate_pdf

PROFILE_NAMES = ("fast", "standard", "strict")


@dataclass(frozen=True)
class QualityProfile:
    name: str
    min_text_recall: float
    audit_structure: bool
    requires_visual_pdf: bool


PROFILES = {
    "fast": QualityProfile("fast", 0.995, False, False),
    "standard": QualityProfile("standard", 0.995, True, False),
    "strict": QualityProfile("strict", 0.999, True, True),
}


@dataclass
class QualityReport:
    schema_version: int
    profile: str
    operation: str
    source: str
    destination: str
    status: str = "running"
    achieved_level: str = "none"
    checks: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    diagnostics: List[Dict[str, str]] = field(default_factory=list)
    engine: Dict[str, str] = field(default_factory=dict)
    elapsed_ms: int = 0

    def as_dict(self):
        return asdict(self)

    def checked(self, name, evidence=None):
        self.checks.append({"name": name, "status": "pass", "evidence": evidence or {}})

    def diagnostic(self, code, message):
        self.diagnostics.append({"code": code, "severity": "error", "message": str(message)[:1200]})


@dataclass(frozen=True)
class ConversionResult:
    output_path: str
    report: QualityReport


class ConversionFailure(RuntimeError):
    def __init__(self, report):
        self.report = report
        message = report.diagnostics[-1]["message"] if report.diagnostics else "Unknown conversion failure"
        super().__init__(f"Conversion failed [{report.operation}/{report.profile}]: {message}")


def _profile(name):
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown quality profile: {name}; use fast, standard, or strict") from exc


def _text_recall(expected_text, actual_text):
    from devkit.convert.validate.pdf_quality import _normalize_text

    expected = Counter(_normalize_text(expected_text))
    actual = Counter(_normalize_text(actual_text))
    denominator = sum(expected.values())
    if denominator == 0:
        return 1.0
    return sum(min(n, actual[char]) for char, n in expected.items()) / denominator


def _expected_markdown(source):
    from devkit.convert.engines import PandocEngine
    from devkit.convert.validate.pdf_quality import expected_text_from_ast

    document = PandocEngine().parse_markdown(source)
    return document, expected_text_from_ast(document.to_pandoc_ast())


def _check_docx(source, stage, report, profile):
    from devkit.convert.validate.structure import verify_docx_structure

    validate_docx(stage)
    report.checked("docx_integrity")
    if profile.audit_structure:
        document, expected_text = _expected_markdown(source)
        info = verify_docx_structure(stage, document)
        structural = asdict(info)
        report.metrics["docx"] = structural
        report.checked("docx_structural_counts", structural)
        if profile.name == "strict":
            for key, source_tag in (("bold_runs", "Strong"), ("italic_runs", "Emph")):
                actual, wanted = getattr(info, key), document.feature_count(source_tag)
                if actual < wanted:
                    raise ValueError(f"DOCX lost {source_tag} formatting: {actual} < {wanted}")
            # Pandoc's list items can contain multiple Paragraph blocks; the
            # inspect_docx list counter is a minimum semantic anchor.
            from devkit.convert.engines import PandocEngine
            import json

            runner = PandocEngine()
            ast = json.loads(runner._run(["-f", "docx", "-t", "json", str(stage)]))
            from devkit.convert.validate.pdf_quality import expected_text_from_ast
            actual_text = expected_text_from_ast(ast)
            recall = _text_recall(expected_text, actual_text)
            report.metrics["docx_text_recall"] = recall
            if recall < profile.min_text_recall:
                raise ValueError(
                    f"DOCX text recall {recall:.4f} below strict minimum {profile.min_text_recall:.4f}"
                )
            report.checked("docx_strict_formatting_and_text", {"text_recall": recall})
        report.achieved_level = "L2"
    else:
        report.achieved_level = "L1"


def _check_pdf(source, stage, report, profile, *, baseline_manifest=None, baseline_case=None,
               artifacts_dir=None):
    from devkit.convert.validate.pdf_quality import inspect_pdf_quality

    pages = validate_pdf(stage)
    report.checked("pdf_integrity", {"pages": pages})
    report.achieved_level = "L1"
    if profile.audit_structure:
        document, expected = _expected_markdown(source)
        quality = inspect_pdf_quality(
            stage, expected_text=expected, min_recall=profile.min_text_recall,
            expected_images=document.feature_count("Image"),
        )
        report.metrics["pdf"] = quality.as_dict()
        report.checked("pdf_unicode_graphics_and_page_bounds", {
            "text_recall": quality.text_recall,
            "images": quality.image_instances,
            "clipped_characters": quality.clipped_characters,
        })
        report.achieved_level = "L2"
    if profile.requires_visual_pdf:
        if not baseline_manifest or not baseline_case:
            raise ValueError("Strict PDF profile requires --visual-manifest and --visual-case")
        if artifacts_dir is None:
            raise ValueError("Strict PDF profile requires --artifacts-dir for visual evidence")
        evaluation = _check_visual(source, stage, baseline_manifest, baseline_case, artifacts_dir)
        report.metrics["visual"] = evaluation
        report.checked("approved_visual_golden", {
            "case": baseline_case, "page_count": len(evaluation["pages"])
        })
        report.achieved_level = "L3"


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def _check_visual(source, stage, manifest_path, case_id, artifacts_dir):
    from devkit.convert.fonts import choose_cjk_font
    from devkit.convert.visual import current_environment, evaluate_pages, load_manifest, render_pages

    path = Path(manifest_path).resolve()
    manifest = load_manifest(path)
    matching = [case for case in manifest["cases"] if case["id"] == case_id]
    if len(matching) != 1:
        raise ValueError(f"Unknown approved golden case: {case_id}")
    case = matching[0]
    fixture_root = path.parent
    expected_source = (fixture_root / case["markdown"]).resolve()
    if expected_source != fixture_root and fixture_root not in expected_source.parents:
        raise ValueError("Golden source path escapes fixture root")
    if not expected_source.is_file() or _sha256(source) != _sha256(expected_source):
        raise ValueError("Strict visual baseline must match identical approved Markdown input")
    lock_path = fixture_root / "baseline.lock.json"
    if not lock_path.is_file():
        raise FileNotFoundError("Approved renderer lock is missing")
    with open(lock_path, encoding="utf-8") as stream:
        environment = json.load(stream)["environment"]
    _, expected = _expected_markdown(source)
    font = choose_cjk_font(expected)
    if current_environment(font) != environment:
        raise ValueError("Renderer or font differs from approved golden environment")
    raster = render_pages(stage, dpi=manifest["render"]["dpi"], max_pages=manifest["render"]["max_pages"])
    visual_path = Path(artifacts_dir)
    visual_path.mkdir(parents=True, exist_ok=True)
    result = evaluate_pages(case, raster, manifest, fixture_root / "approved", visual_path)
    if result["status"] != "pass":
        raise ValueError(f"Approved visual baseline mismatch: {case_id}")
    return result


def _validate_report_destination(report_path, source, destination):
    if report_path is None:
        return
    require_distinct([source, destination], report_path)


def _write_report(report, path, source, destination):
    if path is None:
        return
    _validate_report_destination(path, source, destination)
    destination_path = Path(path).absolute()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="devkit-quality-report-", dir=str(destination_path.parent)) as folder:
        staged = Path(folder) / "report.json"
        staged.write_text(
            json.dumps(report.as_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )
        publish_file(staged, destination_path, [source, destination])


def _route(source, to_format):
    suffix = Path(source).suffix.lower()
    if suffix == ".md" and to_format in ("pdf", "docx"):
        return "markdown_to_" + to_format
    if suffix in (".docx", ".doc") and to_format in ("pdf", "md"):
        return "word_to_" + to_format
    raise ValueError(f"Unsupported conversion pair: {suffix} -> {to_format}")


def _new_report(source, destination, profile, route):
    return QualityReport(
        schema_version=1, profile=profile, operation=route,
        source=str(source), destination=str(destination),
        engine={"pipeline": {
            "markdown_to_pdf": "pandoc+libreoffice+pymupdf",
            "markdown_to_docx": "pandoc+ooxml",
            "word_to_pdf": "libreoffice+pypdf",
            "word_to_md": "pandoc",
        }[route]},
    )


def _finish_failed(report, started, exc, report_path, source, destination):
    report.status = "failed"
    report.elapsed_ms = round((time.perf_counter() - started) * 1000)
    report.diagnostic(type(exc).__name__, str(exc))
    _write_report(report, report_path, source, destination)
    raise ConversionFailure(report) from exc


def _audit_existing(source, stage, report, profile, *, visual_manifest=None,
                    visual_case=None, artifacts_dir=None):
    if report.operation == "markdown_to_docx":
        _check_docx(source, stage, report, profile)
    elif report.operation == "markdown_to_pdf":
        _check_pdf(source, stage, report, profile,
                   baseline_manifest=visual_manifest, baseline_case=visual_case,
                   artifacts_dir=artifacts_dir)
    elif report.operation == "word_to_pdf":
        report.checked("pdf_integrity", {"pages": validate_pdf(stage)})
        report.achieved_level = "L1"
    elif report.operation == "word_to_md":
        text = stage.read_text(encoding="utf-8")
        report.checked("utf8_markdown_output", {"characters": len(text)})
        report.achieved_level = "L1"


def _validate_request(selected, source, destination, route, *, report_path=None,
                      reference_doc=None, font_family=None, min_text_recall=None,
                      visual_manifest=None, visual_case=None, artifacts_dir=None):
    require_distinct([source] + ([reference_doc] if reference_doc else []), destination)
    _validate_report_destination(report_path, source, destination)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    if reference_doc and route != "markdown_to_docx":
        raise ValueError("--reference-doc only applies to Markdown -> DOCX")
    if font_family and route != "markdown_to_pdf":
        raise ValueError("--font-family only applies to Markdown -> PDF")
    if selected.name == "strict" and route not in ("markdown_to_pdf", "markdown_to_docx"):
        raise ValueError(f"Strict profile is unsupported for {route}: no independent source baseline")
    if selected.requires_visual_pdf and route == "markdown_to_pdf" and (
        not visual_manifest or not visual_case or not artifacts_dir
    ):
        raise ValueError("Strict PDF requires approved visual manifest, case and artifacts directory")
    if min_text_recall is not None and not selected.min_text_recall <= min_text_recall <= 1:
        raise ValueError(
            f"min_text_recall must be >= {selected.min_text_recall} for profile {selected.name} and <= 1"
        )


def _publish_result(stage, source, destination, reference_doc, to_format, report):
    validator = {"pdf": validate_pdf, "docx": validate_docx}.get(to_format)
    publish_file(stage, destination, [source] + ([reference_doc] if reference_doc else []),
                 validator=validator)
    report.checked("atomic_output_published")


def convert_with_quality(input_path, to_format, output_path=None, *, profile="standard",
                         report_path=None, reference_doc=None, font_family=None,
                         min_text_recall=None, visual_manifest=None, visual_case=None,
                         artifacts_dir=None):
    """Convert and publish only after selected quality gates have passed.

    The report is written for ordinary conversion/validation failures. Publishing
    the final output and publishing its separate JSON report are not one atomic
    multi-file transaction: a report write error after conversion is surfaced
    directly (the successfully converted output remains published).
    """
    selected = _profile(profile)
    source = Path(input_path).absolute()
    route = _route(source, to_format)
    destination = Path(output_path).absolute() if output_path else source.with_suffix("." + to_format)
    report = _new_report(source, destination, profile, route)
    started = time.perf_counter()
    # Invalid report destinations are rejected before any source/output mutation.
    _validate_report_destination(report_path, source, destination)
    try:
        _validate_request(
            selected, source, destination, route, report_path=report_path,
            reference_doc=reference_doc, font_family=font_family,
            min_text_recall=min_text_recall, visual_manifest=visual_manifest,
            visual_case=visual_case, artifacts_dir=artifacts_dir,
        )
        with tempfile.TemporaryDirectory(prefix="devkit-quality-") as directory:
            stage = Path(directory) / ("converted." + to_format)
            if route == "markdown_to_pdf":
                from devkit.convert.md2pdf import markdown_to_pdf

                markdown_to_pdf(
                    str(source), str(stage), font_family=font_family,
                    min_text_recall=max(selected.min_text_recall, min_text_recall or 0),
                )
            elif route == "markdown_to_docx":
                from devkit.convert.md2docx import markdown_to_docx

                markdown_to_docx(str(source), str(stage), reference_doc=reference_doc)
            else:
                from devkit.convert.doc_convert import convert_document

                result = convert_document(str(source), to_format, str(stage))
                if not result or not stage.is_file():
                    raise RuntimeError(f"Backend did not produce {to_format}")
            _audit_existing(
                source, stage, report, selected,
                visual_manifest=visual_manifest, visual_case=visual_case,
                artifacts_dir=artifacts_dir,
            )
            _publish_result(stage, source, destination, reference_doc, to_format, report)
            report.status = "passed"
            report.elapsed_ms = round((time.perf_counter() - started) * 1000)
    except Exception as exc:
        _finish_failed(report, started, exc, report_path, source, destination)
    _write_report(report, report_path, source, destination)
    return ConversionResult(str(destination), report)


def audit_existing(input_path, output_path, *, profile="standard", report_path=None,
                   visual_manifest=None, visual_case=None, artifacts_dir=None):
    """Assess an existing conversion without altering its output.

    Format pair is inferred from the source/output suffixes. Structural and
    visual evidence are measured from the existing output, not by re-rendering.
    """
    selected = _profile(profile)
    source = Path(input_path).absolute()
    output = Path(output_path).absolute()
    route = _route(source, output.suffix.lower().lstrip("."))
    report = _new_report(source, output, profile, route)
    started = time.perf_counter()
    _validate_report_destination(report_path, source, output)
    try:
        _validate_request(
            selected, source, output, route, report_path=report_path,
            visual_manifest=visual_manifest, visual_case=visual_case,
            artifacts_dir=artifacts_dir,
        )
        if not output.is_file():
            raise FileNotFoundError(f"Converted output is missing: {output}")
        _audit_existing(
            source, output, report, selected, visual_manifest=visual_manifest,
            visual_case=visual_case, artifacts_dir=artifacts_dir,
        )
        report.checked("existing_output_assessed_without_modification")
        report.status = "passed"
        report.elapsed_ms = round((time.perf_counter() - started) * 1000)
    except Exception as exc:
        _finish_failed(report, started, exc, report_path, source, output)
    _write_report(report, report_path, source, output)
    return report

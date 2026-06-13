from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extractors.docx_extractor import extract_docx
from scripts.extractors.md_extractor import extract_md
from scripts.extractors.pdf_extractor import extract_pdf
from scripts.llm_client import LLMClient
from scripts.llm_summary import (
    LLM_SUMMARY_SYSTEM_PROMPT,
    build_llm_summary_prompt,
    build_llm_summary_repair_prompt,
    extract_json_from_llm_response,
    missing_llm_summary_status,
    normalize_llm_summary,
    source_pages_for_prompt,
    validate_llm_summary_schema,
)
from scripts.models import LectureUnit
from scripts.qa_report import write_qa_report
from scripts.run_registry import register_run
from scripts.site_builder import build_site
from scripts.utils import SUPPORTED_EXTENSIONS, build_heuristic_chinese_note, detect_lecture_number, now_stamp, slugify


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = {
    "projectName": "Local Lecture Knowledge Site",
    "inputDir": "input_materials",
    "outputDir": "output_sites",
    "templateDir": "templates",
    "minContentChars": 300,
    "generationMode": "offline",
    "llm": {
        "provider": "none",
        "baseUrl": "",
        "model": "",
        "apiKeyEnv": "OPENAI_API_KEY",
        "temperature": 0.2,
    },
}


def load_config(path: Path | None) -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    candidate = path or (ROOT / "config.json")
    if not candidate.exists():
        candidate = ROOT / "config.example.json"
    if candidate.exists():
        loaded = json.loads(candidate.read_text(encoding="utf-8"))
        deep_update(config, loaded)
    return config


def deep_update(target: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = value
    return target


def scan_input_files(input_dir: Path) -> list[Path]:
    files = [
        path
        for path in input_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and path.name.lower() != "readme.md"
    ]
    return sorted(files, key=lambda path: (detect_lecture_number(path) or 10_000, path.name.lower()))


def extract_unit(path: Path, index: int) -> LectureUnit:
    if path.suffix.lower() == ".pdf":
        return extract_pdf(path, index)
    if path.suffix.lower() in {".md", ".markdown"}:
        return extract_md(path, index)
    if path.suffix.lower() == ".docx":
        return extract_docx(path, index)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def build_llm_client(config: dict[str, Any]) -> LLMClient:
    llm_config = dict(config.get("llm") or {})
    return LLMClient(llm_config)


def summarize_units(units: list[LectureUnit], client: LLMClient) -> tuple[dict[str, dict[str, Any]], bool, dict[str, Any]]:
    telemetry: dict[str, Any] = {
        "llmEnabled": client.enabled,
        "llmConnectionOk": False,
        "llmCallsAttempted": 0,
        "llmCallsSucceeded": 0,
        "llmCallsFailed": 0,
        "llmParseSucceeded": 0,
        "llmRepairAttempted": 0,
        "llmRepairSucceeded": 0,
        "sourceNotesGeneratedBy": "fallback_cleaned_excerpt",
        "llmError": None,
        "diagnostics": client.diagnostics(),
        "lectureStatuses": [],
    }
    if not client.enabled:
        telemetry["llmError"] = "LLM disabled or missing configuration/API key."
        telemetry["lectureStatuses"] = [
            missing_llm_summary_status(unit.lecture_id, "llm_disabled", telemetry["llmError"], llm_enabled=False)
            for unit in units
        ]
        return {}, False, telemetry
    ok, message = client.test_connection()
    telemetry["llmConnectionOk"] = ok
    telemetry["llmError"] = None if ok else message
    if not ok:
        telemetry["llmCallsAttempted"] = client.calls_attempted
        telemetry["llmCallsSucceeded"] = client.calls_succeeded
        telemetry["llmCallsFailed"] = client.calls_failed
        telemetry["lectureStatuses"] = [
            missing_llm_summary_status(unit.lecture_id, "llm_connection_failed", message, llm_enabled=True)
            for unit in units
        ]
        return {}, False, telemetry

    notes: dict[str, dict[str, Any]] = {}
    for unit in units:
        status: dict[str, Any] = {
            "lectureId": unit.lecture_id,
            "llmSummaryStatus": "success",
            "llmCallAttempted": True,
            "llmCallSucceeded": False,
            "llmParseSucceeded": False,
            "llmRepairAttempted": False,
            "llmRepairSucceeded": False,
            "reasonIfMissing": None,
            "validationErrors": [],
        }
        pages = source_pages_for_prompt(unit)
        if not pages:
            status.update({
                "llmSummaryStatus": "skipped_insufficient_text",
                "llmCallAttempted": False,
                "reasonIfMissing": "No source pages with enough text.",
            })
            telemetry["lectureStatuses"].append(status)
            continue
        fallback_ref = pages[0]["sourceRef"]
        response = ""
        try:
            response = client.summarize(build_llm_summary_prompt(unit), system_prompt=LLM_SUMMARY_SYSTEM_PROMPT)
        except Exception as exc:
            telemetry["llmError"] = str(exc)
            status.update({"llmSummaryStatus": "llm_call_failed", "reasonIfMissing": str(exc)})
            telemetry["lectureStatuses"].append(status)
            continue
        status["llmCallSucceeded"] = True

        parsed = extract_json_from_llm_response(response)
        if parsed is None:
            status["llmRepairAttempted"] = True
            telemetry["llmRepairAttempted"] += 1
            try:
                repaired = client.summarize(
                    build_llm_summary_repair_prompt(response, [page["sourceRef"] for page in pages]),
                    system_prompt="You convert messy model output into the required JSON schema. Return valid JSON only. No Markdown. No explanations.",
                )
                parsed = extract_json_from_llm_response(repaired)
            except Exception as exc:
                status.update({"llmSummaryStatus": "llm_parse_failed", "reasonIfMissing": f"Repair call failed: {exc}"})
                telemetry["lectureStatuses"].append(status)
                continue
            if parsed is not None:
                status["llmRepairSucceeded"] = True
                telemetry["llmRepairSucceeded"] += 1
        if parsed is None:
            status.update({"llmSummaryStatus": "llm_parse_failed", "reasonIfMissing": "LLM response could not be parsed as JSON."})
            telemetry["lectureStatuses"].append(status)
            continue

        normalized = normalize_llm_summary(parsed, unit.lecture_title, fallback_ref)
        valid, errors = validate_llm_summary_schema(normalized)
        if not valid and not status["llmRepairAttempted"]:
            status["llmRepairAttempted"] = True
            telemetry["llmRepairAttempted"] += 1
            try:
                repaired = client.summarize(
                    build_llm_summary_repair_prompt(response, [page["sourceRef"] for page in pages]),
                    system_prompt="You convert messy model output into the required JSON schema. Return valid JSON only. No Markdown. No explanations.",
                )
                repaired_parsed = extract_json_from_llm_response(repaired)
                if repaired_parsed is not None:
                    repaired_normalized = normalize_llm_summary(repaired_parsed, unit.lecture_title, fallback_ref)
                    repaired_valid, repaired_errors = validate_llm_summary_schema(repaired_normalized)
                    if repaired_valid:
                        normalized = repaired_normalized
                        valid = True
                        errors = []
                        status["llmRepairSucceeded"] = True
                        telemetry["llmRepairSucceeded"] += 1
                    else:
                        errors = repaired_errors
            except Exception as exc:
                errors.append(f"Repair call failed: {exc}")
        if not valid:
            status.update({
                "llmSummaryStatus": "llm_schema_invalid",
                "reasonIfMissing": "; ".join(errors[:6]),
                "validationErrors": errors,
            })
            telemetry["lectureStatuses"].append(status)
            continue

        status["llmParseSucceeded"] = True
        telemetry["llmParseSucceeded"] += 1
        notes[unit.lecture_id] = normalized
        telemetry["lectureStatuses"].append(status)

    telemetry["llmCallsAttempted"] = client.calls_attempted
    telemetry["llmCallsSucceeded"] = client.calls_succeeded
    telemetry["llmCallsFailed"] = client.calls_failed
    if notes:
        telemetry["sourceNotesGeneratedBy"] = "llm_summary_zh"
    return notes, bool(notes), telemetry

def validate_input(input_dir: Path, files: list[Path]) -> list[str]:
    errors = []
    if not input_dir.exists():
        errors.append(f"Input directory does not exist: {input_dir}")
    if not files:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        errors.append(f"No supported files found in {input_dir}. Supported formats: {supported}")
    return errors


def generate_from_config(
    config: dict[str, Any],
    *,
    open_after: bool = False,
    log: Any = print,
) -> dict[str, Any]:
    project_name = str(config.get("projectName") or DEFAULT_CONFIG["projectName"])
    input_dir = (ROOT / str(config.get("inputDir", "input_materials"))).resolve()
    output_root = (ROOT / str(config.get("outputDir", "output_sites"))).resolve()
    template_dir = (ROOT / str(config.get("templateDir", "templates"))).resolve()
    min_content_chars = int(config.get("minContentChars", 300))

    files = scan_input_files(input_dir) if input_dir.exists() else []
    validation_errors = validate_input(input_dir, files)
    if validation_errors:
        for error in validation_errors:
            log(f"ERROR: {error}")
        raise RuntimeError("; ".join(validation_errors))

    units: list[LectureUnit] = []
    failed_files: list[dict[str, str]] = []
    for index, path in enumerate(files, start=1):
        try:
            unit = extract_unit(path, index)
            if len(unit.full_text.strip()) < 20:
                raise ValueError("Extracted text is empty or too short.")
            units.append(unit)
            log(f"Processed: {path.name} -> {unit.lecture_id}")
        except Exception as exc:
            failed_files.append({"file": str(path.relative_to(ROOT)), "reason": str(exc)})
            log(f"FAILED: {path.name}: {exc}")

    total_chars = sum(len(unit.full_text) for unit in units)
    if not units:
        raise RuntimeError("No files could be processed.")
    if total_chars < min_content_chars:
        message = f"Extracted content is too short ({total_chars} chars < minContentChars {min_content_chars})."
        log(f"ERROR: {message}")
        log("Lower minContentChars in config.json only if this is intentional.")
        raise RuntimeError(message)

    created_at, run_stamp = now_stamp()
    run_id = f"{slugify(project_name)}-{run_stamp}"
    output_path = output_root / run_id
    client = build_llm_client(config)
    llm_notes, llm_enabled, llm_telemetry = summarize_units(units, client)
    generation_mode = "online_llm" if llm_enabled and llm_telemetry.get("llmConnectionOk") else "offline"
    metadata = {
        "runId": run_id,
        "projectName": project_name,
        "createdAt": created_at,
        "inputDir": str(input_dir.relative_to(ROOT)),
        "outputDir": str(output_path.relative_to(ROOT)),
        "supportedFormats": sorted(SUPPORTED_EXTENSIONS),
        "processedFiles": [unit.source_file for unit in units],
        "failedFiles": failed_files,
        "totalExtractedChars": total_chars,
        "generationMode": generation_mode,
        "llmEnabled": bool(llm_telemetry.get("llmEnabled")),
        "llmProvider": client.provider if client.enabled else "none",
        "llmModel": client.model if client.enabled else "",
        "llmTelemetry": llm_telemetry,
        "llmConnectionOk": llm_telemetry.get("llmConnectionOk"),
        "llmCallsAttempted": llm_telemetry.get("llmCallsAttempted", 0),
        "llmCallsSucceeded": llm_telemetry.get("llmCallsSucceeded", 0),
        "llmCallsFailed": llm_telemetry.get("llmCallsFailed", 0),
        "llmParseSucceeded": llm_telemetry.get("llmParseSucceeded", 0),
        "llmRepairAttempted": llm_telemetry.get("llmRepairAttempted", 0),
        "llmRepairSucceeded": llm_telemetry.get("llmRepairSucceeded", 0),
        "llmSummaryStatuses": llm_telemetry.get("lectureStatuses", []),
        "sourceNotesGeneratedBy": llm_telemetry.get("sourceNotesGeneratedBy"),
        "llmError": llm_telemetry.get("llmError"),
        "offlineCapabilities": [
            "source_explorer",
            "search",
            "slide_figures",
            "slide_gallery",
            "lecture_map",
            "cross_lecture_references",
            "template_practice",
        ],
        "llmCapabilities": [
            "chinese_summaries",
            "enriched_glossary",
            "creative_extension_practice",
            "application_scenarios",
            "advanced_code_cloze",
            "cross_lecture_reasoning",
        ],
        "sourceGroundedPolicy": "Source-grounded sections are based on extracted local files and source references.",
        "creativeExtensionPolicy": "Creative Extension sections and scenario practice may go beyond source material and are labeled.",
    }
    build_site(units, output_path, project_name, metadata, template_dir, llm_notes, llm_enabled)
    language_report = metadata.get("languageNormalizationReport") or {}
    metadata["sourceNotesGeneratedByCounts"] = {
        "llm_summary_zh": int(language_report.get("highQualityChineseSummaryCount", 0)),
        "fallback_cleaned_excerpt": int(language_report.get("sourceExcerptCount", 0)),
        "visual_only": int(language_report.get("visualOnlySectionCount", 0)),
    }
    qa_report = write_qa_report(output_path, metadata)
    metadata["llmSummary"] = qa_report.get("llmSummary", {})
    metadata["qaReport"] = {
        "status": qa_report.get("status"),
        "path": str(Path(metadata["outputDir"]) / "qa_report.json"),
        "htmlPath": str(Path(metadata["outputDir"]) / "qa_report.html"),
        "summary": qa_report.get("summary", {}),
        "llmSummary": qa_report.get("llmSummary", {}),
        "llmTelemetry": qa_report.get("llmTelemetry", {}),
    }
    (output_path / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    register_run(output_root, metadata)

    index_path = output_path / "index.html"
    log("")
    log(f"Output site: {index_path}")
    log(f"Processed files: {len(units)}")
    log(f"Failed files: {len(failed_files)}")
    report = metadata.get("languageNormalizationReport") or {}
    telemetry = metadata.get("llmTelemetry") or {}
    if telemetry:
        log("LLM telemetry:")
        log(f"- llmEnabled: {telemetry.get('llmEnabled')}")
        log(f"- llmConnectionOk: {telemetry.get('llmConnectionOk')}")
        log(f"- llmCallsAttempted: {telemetry.get('llmCallsAttempted', 0)}")
        log(f"- llmCallsSucceeded: {telemetry.get('llmCallsSucceeded', 0)}")
        log(f"- llmCallsFailed: {telemetry.get('llmCallsFailed', 0)}")
        log(f"- sourceNotesGeneratedBy: {telemetry.get('sourceNotesGeneratedBy')}")
        if telemetry.get("llmError"):
            log(f"- llmError: {telemetry.get('llmError')}")
    if report:
        log("Language normalization report:")
        log(f"- suspicious raw English paragraphs detected: {report.get('suspiciousRawEnglishParagraphsDetected', 0)}")
        log(f"- suspicious raw English source inputs detected: {report.get('suspiciousRawEnglishSourceInputsDetected', 0)}")
        log(f"- rewritten with LLM: {report.get('rewrittenWithLLM', 0)}")
        log(f"- rewritten with fallback: {report.get('rewrittenWithFallback', 0)}")
        log(f"- blocked raw English paragraphs: {report.get('blockedRawEnglishParagraphs', 0)}")
        log(f"- English leakage paragraphs detected: {report.get('englishLeakageParagraphsDetected', 0)}")
        log(f"- metadata leakage hits detected: {report.get('metadataLeakageDetected', 0)}")
        log(f"- long English runs detected: {report.get('longEnglishRunsDetected', 0)}")
        log(f"- rendered as source quotes: {report.get('renderedAsSourceQuotes', 0)}")
        log(f"- low-quality Chinese fallback blocked: {report.get('lowQualityChineseFallbackBlocked', 0)}")
        log(f"- source excerpts rendered: {report.get('sourceExcerptCount', 0)}")
        log(f"- visual-only sections rendered: {report.get('visualOnlySectionCount', 0)}")
        log(f"- high-quality Chinese summaries rendered: {report.get('highQualityChineseSummaryCount', 0)}")
        log(f"- low-quality sections skipped: {report.get('skippedLowQualitySections', 0)}")
        quote_report = report.get("sourceQuoteControlReport") or {}
        if quote_report:
            log("Source quote control report:")
            log(f"- raw quotes collected: {quote_report.get('rawQuotesCollected', 0)}")
            log(f"- quotes after filtering: {quote_report.get('quotesAfterFiltering', 0)}")
            log(f"- quotes rendered: {quote_report.get('quotesRendered', 0)}")
            log(f"- duplicate quotes removed: {quote_report.get('duplicateQuotesRemoved', 0)}")
            log(f"- long quotes removed: {quote_report.get('longQuotesRemoved', 0)}")
            log(f"- low-information quotes removed: {quote_report.get('lowInformationQuotesRemoved', 0)}")
    qa = metadata.get("qaReport") or {}
    if qa:
        log(f"QA report: {qa.get('status')} -> {qa.get('path')}")
    if open_after:
        webbrowser.open(index_path.as_uri())
    return {
        "metadata": metadata,
        "indexPath": str(index_path),
        "outputPath": str(output_path),
        "processed": len(units),
        "failed": len(failed_files),
    }


def generate_site_from_config(config: dict[str, Any]) -> dict[str, Any]:
    """Compatibility wrapper used by local web dashboards and external callers."""
    logs: list[str] = []
    result = generate_from_config(config, open_after=False, log=lambda line="": logs.append(str(line)))
    metadata = result["metadata"]
    return {
        "runId": metadata["runId"],
        "outputPath": str(Path(metadata["outputDir"]) / "index.html"),
        "inputFileCount": len(metadata.get("processedFiles") or []),
        "warnings": metadata.get("failedFiles") or [],
        "logs": logs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a versioned local-first lecture knowledge site.")
    parser.add_argument("--config", type=Path, help="Path to config JSON. Defaults to config.json or config.example.json.")
    parser.add_argument("--open", action="store_true", help="Open the generated index.html after success.")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    try:
        generate_from_config(config, open_after=args.open, log=print)
    except RuntimeError:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


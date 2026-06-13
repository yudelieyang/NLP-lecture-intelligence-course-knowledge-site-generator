from __future__ import annotations

import html
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from scripts.utils import (
    count_ascii_words,
    count_chinese_chars,
    detect_english_leakage,
    is_low_quality_chinese_fallback,
    looks_like_raw_english_dump,
    normalize_ws,
)


BAD_GLOSSARY_PATTERNS = [
    "从源材料中提取的关键词",
    "重要术语",
    "关键词",
    "No explanation available",
]

CANONICAL_QUESTION_TYPES = {
    "multiple-choice",
    "concept",
    "short-answer",
    "code-cloze",
    "application-scenario",
    "mixed",
}


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", value or ""))


def strip_non_body_spans(value: str) -> str:
    value = re.sub(r'<span class="page-ref".*?</span>', " ", value or "", flags=re.S)
    value = re.sub(r'<span class="quote-label".*?</span>', " ", value, flags=re.S)
    return value


def class_set(value: str | None) -> set[str]:
    return set((value or "").split())


class BodyParagraphParser(HTMLParser):
    ALLOWED_CLASSES = {
        "source-quote",
        "sources",
        "slide-figure",
        "page-ref",
        "quote-label",
        "source",
        "ai-label",
        "source-excerpt-card",
        "excerpt-label",
        "llm-summary-status",
    }
    ALLOWED_TAGS = {"code", "pre", "script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict[str, str]] = []
        self.current: dict[str, Any] | None = None
        self.paragraphs: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        self.stack.append({"tag": tag, "class": attr.get("class", ""), "id": attr.get("id", "")})
        if tag == "p":
            self.current = {
                "class": attr.get("class", ""),
                "id": attr.get("id", ""),
                "ancestorClasses": " ".join(item.get("class", "") for item in self.stack),
                "ancestorIds": " ".join(item.get("id", "") for item in self.stack),
                "parts": [],
            }

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self.current is not None:
            text = normalize_ws(" ".join(self.current.pop("parts")))
            self.current["text"] = text
            if text:
                self.paragraphs.append(self.current)
            self.current = None
        if self.stack:
            for index in range(len(self.stack) - 1, -1, -1):
                if self.stack[index].get("tag") == tag:
                    del self.stack[index:]
                    break

    def handle_data(self, data: str) -> None:
        if self.current is None:
            return
        for item in self.stack:
            tag = item.get("tag", "")
            classes = class_set(item.get("class"))
            if tag in self.ALLOWED_TAGS or classes & self.ALLOWED_CLASSES:
                return
        self.current["parts"].append(data)


def final_body_paragraphs(index_html: str) -> list[dict[str, Any]]:
    parser = BodyParagraphParser()
    parser.feed(index_html)
    paragraphs = []
    for paragraph in parser.paragraphs:
        classes = class_set(paragraph.get("class"))
        ancestor_classes = class_set(paragraph.get("ancestorClasses"))
        ancestor_ids = (paragraph.get("ancestorIds") or "").split()
        if classes & BodyParagraphParser.ALLOWED_CLASSES:
            continue
        if ancestor_classes & BodyParagraphParser.ALLOWED_CLASSES:
            continue
        if any(item.endswith("-sources") or item.endswith("-terms") or item.endswith("-extension") for item in ancestor_ids):
            continue
        if any(item in {"overview", "practice-generator", "failed-files"} for item in ancestor_ids):
            continue
        paragraphs.append(paragraph)
    return paragraphs


def lecture_blocks(index_html: str) -> list[tuple[str, str, str]]:
    blocks: list[tuple[str, str, str]] = []
    pattern = re.compile(
        r'<section class="lecture-section" id="([^"]+)">(.*?)(?=<section class="lecture-section" id=|<section class="practice-generator")',
        re.S,
    )
    for lecture_id, block in pattern.findall(index_html):
        if lecture_id in {"overview", "failed-files"}:
            continue
        title_match = re.search(r"<h1>(.*?)</h1>", block, re.S)
        title = strip_tags(title_match.group(1)) if title_match else lecture_id
        blocks.append((lecture_id, title, block))
    return blocks


def bad_glossary_entries(block: str) -> int:
    rows = re.findall(r'<table class="glossary-table"><tbody>(.*?)</tbody></table>', block, re.S)
    if not rows:
        return 0
    bad = 0
    for row in re.findall(r"<tr>(.*?)</tr>", rows[0], re.S):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)
        if len(cells) < 2:
            continue
        explanation = normalize_ws(strip_tags(cells[1]))
        if not explanation or count_chinese_chars(explanation) < 20:
            bad += 1
            continue
        if any(pattern.lower() in explanation.lower() for pattern in BAD_GLOSSARY_PATTERNS):
            bad += 1
            continue
        if "page-ref" not in cells[1] and "ai-label" not in cells[1] and "term-source-label" not in cells[1]:
            bad += 1
    return bad


def glossary_count(block: str) -> int:
    rows = re.findall(r'<table class="glossary-table"><tbody>(.*?)</tbody></table>', block, re.S)
    if not rows:
        return 0
    return len(re.findall(r"<tr>", rows[0]))


def page_title_heading_count(block: str) -> int:
    headings = re.findall(r"<h[123][^>]*>(.*?)</h[123]>", block, re.S)
    return sum(1 for heading in headings if re.fullmatch(r"Page\s+\d+", strip_tags(heading).strip(), flags=re.I))


def overlong_english_title_count(block: str) -> int:
    headings = re.findall(r'<h3 class="source-note-heading">(.*?)</h3>', block, re.S)
    count = 0
    for heading in headings:
        plain = strip_tags(heading)
        if count_ascii_words(plain) > 10:
            count += 1
            continue
        leakage = detect_english_leakage(plain)
        if leakage.get("metadataHits") or leakage.get("longEnglishRuns"):
            count += 1
    return count


def source_paragraphs(block: str) -> list[str]:
    return re.findall(r'<p class="source-note-paragraph">(.*?)</p>', block, re.S)


def source_excerpt_count(block: str) -> int:
    return block.count('class="source-excerpt-card"')


def visual_only_section_count(block: str) -> int:
    return block.count('data-note-state="visual_only"')


def high_quality_summary_count(block: str) -> int:
    return block.count('data-note-state="llm_summary_zh"')


def source_generation_modes(block: str) -> dict[str, int]:
    return {
        "llm_summary_zh": block.count('data-note-state="llm_summary_zh"'),
        "fallback_cleaned_excerpt": block.count('data-note-state="fallback_cleaned_excerpt"'),
        "visual_only": block.count('data-note-state="visual_only"'),
    }


def markdown_artifact_count_in_llm_summary(index_html: str) -> int:
    count = 0
    for block in re.findall(r'<section class="llm-structured-summary.*?</section>\s*</section>', index_html, re.S):
        text = strip_tags(block)
        if re.search(r"```|(^|\s)#{1,6}\s|\*\*|-{3,}|以下是基于|根据您提供|Here is", text, re.I):
            count += 1
    return count


def build_llm_summary_report(metadata: dict[str, Any], index_html: str) -> dict[str, Any]:
    statuses = [item for item in metadata.get("llmSummaryStatuses") or [] if isinstance(item, dict)]
    lecture_count = len(statuses)
    success_count = sum(1 for item in statuses if item.get("llmSummaryStatus") == "success")
    missing = [item for item in statuses if item.get("llmSummaryStatus") != "success"]
    return {
        "lectureCount": lecture_count,
        "successCount": success_count,
        "missingCount": len(missing),
        "parseFailedCount": sum(1 for item in statuses if item.get("llmSummaryStatus") == "llm_parse_failed"),
        "schemaInvalidCount": sum(1 for item in statuses if item.get("llmSummaryStatus") == "llm_schema_invalid"),
        "fallbackCount": len(missing),
        "repairAttemptedCount": sum(1 for item in statuses if item.get("llmRepairAttempted")),
        "repairSucceededCount": sum(1 for item in statuses if item.get("llmRepairSucceeded")),
        "missingReasonCount": sum(1 for item in missing if item.get("reasonIfMissing")),
        "markdownArtifactCount": markdown_artifact_count_in_llm_summary(index_html),
    }


def low_quality_fallback_count(paragraphs: list[str]) -> int:
    return sum(1 for paragraph in paragraphs if is_low_quality_chinese_fallback(strip_tags(paragraph)))


def missing_source_refs(paragraphs: list[str]) -> int:
    return sum(1 for paragraph in paragraphs if "page-ref" not in paragraph and "source-ref" not in paragraph)


def practice_type_check(script_js: str) -> dict[str, Any]:
    missing = sorted(value for value in CANONICAL_QUESTION_TYPES if value not in script_js)
    legacy_present = sorted(value for value in ['value="mcq"', 'value="multipleChoice"', 'value="shortAnswer"', 'value="codeCloze"'] if value in script_js)
    return {"missingCanonicalValues": missing, "legacyValuesPresent": legacy_present, "ok": not missing and not legacy_present}


def build_qa_report(output_path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    index_html = (output_path / "index.html").read_text(encoding="utf-8")
    script_js = (output_path / "script.js").read_text(encoding="utf-8") if (output_path / "script.js").exists() else ""
    lectures = []
    llm_summary = build_llm_summary_report(metadata, index_html)
    llm_status_by_lecture = {
        str(item.get("lectureId")): item
        for item in metadata.get("llmSummaryStatuses") or []
        if isinstance(item, dict)
    }
    summary = {
        "lectureCount": 0,
        "sourceParagraphCount": 0,
        "rawLikeParagraphCount": 0,
        "sourceQuoteCount": 0,
        "glossaryTermCount": 0,
        "badGlossaryEntryCount": 0,
        "pageTitleHeadingCount": 0,
        "englishLeakageParagraphCount": 0,
        "metadataLeakageCount": 0,
        "longEnglishRunCount": 0,
        "overlongEnglishTitleCount": 0,
        "slideFigureCount": 0,
        "missingSourceRefCount": 0,
        "htmlBodyParagraphCount": 0,
        "htmlBodyMetadataLeakageCount": 0,
        "htmlBodyEnglishLeakageParagraphCount": 0,
        "htmlBodyLongEnglishRunCount": 0,
        "lowQualityChineseFallbackCount": 0,
        "sourceExcerptCount": 0,
        "visualOnlySectionCount": 0,
        "highQualityChineseSummaryCount": 0,
        "sourceNotesGeneratedBy": {
            "llm_summary_zh": 0,
            "fallback_cleaned_excerpt": 0,
            "visual_only": 0,
        },
        "offlineFeatureCount": len(metadata.get("offlineCapabilities") or []),
        "requiresLlmFeatureCount": len(metadata.get("llmCapabilities") or []),
        "lectureMapCount": index_html.count('class="lecture-map"'),
        "slideGalleryImageCount": index_html.count('class="gallery-card"'),
        "crossLectureReferenceCount": index_html.count('class="related-lecture-card"'),
        "sourcesPanelCount": index_html.count('class="sources-panel"'),
        "collapsibleSourcesCount": index_html.count('class="sources-panel"'),
        "sourcesListCount": index_html.count('class="sources-list"'),
        "llmSummaryMarkdownArtifactCount": llm_summary["markdownArtifactCount"],
    }
    all_body_paragraphs = final_body_paragraphs(index_html)
    summary["htmlBodyParagraphCount"] = len(all_body_paragraphs)
    html_body_reports = [detect_english_leakage(paragraph["text"]) for paragraph in all_body_paragraphs]
    summary["htmlBodyEnglishLeakageParagraphCount"] = sum(1 for report in html_body_reports if report.get("hasLeakage"))
    summary["htmlBodyMetadataLeakageCount"] = sum(len(report.get("metadataHits") or []) for report in html_body_reports)
    summary["htmlBodyLongEnglishRunCount"] = sum(len(report.get("longEnglishRuns") or []) for report in html_body_reports)
    for lecture_id, title, block in lecture_blocks(index_html):
        paragraphs = source_paragraphs(block)
        body_paragraphs = [strip_non_body_spans(paragraph) for paragraph in paragraphs]
        raw_like = sum(1 for paragraph in body_paragraphs if looks_like_raw_english_dump(strip_tags(paragraph)))
        leakage_reports = [detect_english_leakage(strip_tags(paragraph)) for paragraph in body_paragraphs]
        english_leakage = sum(1 for report in leakage_reports if report.get("hasLeakage"))
        metadata_leakage = sum(len(report.get("metadataHits") or []) for report in leakage_reports)
        long_runs = sum(len(report.get("longEnglishRuns") or []) for report in leakage_reports)
        cjk = count_chinese_chars(" ".join(strip_tags(paragraph) for paragraph in body_paragraphs))
        ascii_words = count_ascii_words(" ".join(strip_tags(paragraph) for paragraph in body_paragraphs))
        quote_count = block.count('class="source-quote"')
        glossary_terms = glossary_count(block)
        bad_glossary = bad_glossary_entries(block)
        page_headings = page_title_heading_count(block)
        overlong_titles = overlong_english_title_count(block)
        slide_figures = block.count('class="slide-figure"')
        source_excerpts = source_excerpt_count(block)
        visual_only = visual_only_section_count(block)
        high_quality_summaries = high_quality_summary_count(block)
        generation_modes = source_generation_modes(block)
        low_quality_fallbacks = low_quality_fallback_count(paragraphs)
        missing_refs = missing_source_refs(paragraphs)
        warnings: list[str] = []
        if raw_like:
            warnings.append(f"{raw_like} source-note paragraph(s) look like raw English dumps.")
        if english_leakage:
            warnings.append(f"{english_leakage} source-note paragraph(s) contain sentence-level English leakage.")
        if metadata_leakage:
            warnings.append(f"{metadata_leakage} metadata leakage hit(s) found in source-note paragraphs.")
        if long_runs:
            warnings.append(f"{long_runs} long English token run(s) found in source-note paragraphs.")
        if cjk < 120 and paragraphs:
            warnings.append("Chinese explanatory text is short for this lecture.")
        if quote_count > 8:
            warnings.append(f"Source quote count exceeds limit: {quote_count} > 8.")
        if bad_glossary:
            warnings.append(f"{bad_glossary} glossary entrie(s) need better explanations.")
        if page_headings:
            warnings.append(f"{page_headings} Page xx heading(s) found.")
        if overlong_titles:
            warnings.append(f"{overlong_titles} overlong English source-note heading(s) found.")
        if slide_figures == 0 and len(paragraphs) >= 8:
            warnings.append("No slide figures rendered for a multi-section lecture.")
        if missing_refs:
            warnings.append(f"{missing_refs} source paragraph(s) missing page/source refs.")
        if low_quality_fallbacks:
            warnings.append(f"{low_quality_fallbacks} low-quality Chinese fallback paragraph(s) found.")
        lecture_body_paragraphs = [
            paragraph for paragraph in all_body_paragraphs if lecture_id in (paragraph.get("ancestorIds") or "").split()
        ]
        lecture_body_reports = [detect_english_leakage(paragraph["text"]) for paragraph in lecture_body_paragraphs]
        html_body_metadata = sum(len(report.get("metadataHits") or []) for report in lecture_body_reports)
        html_body_english = sum(1 for report in lecture_body_reports if report.get("hasLeakage"))
        html_body_long_runs = sum(len(report.get("longEnglishRuns") or []) for report in lecture_body_reports)
        if html_body_metadata:
            warnings.append(f"{html_body_metadata} metadata leakage hit(s) found in final HTML body paragraphs.")
        if html_body_long_runs:
            warnings.append(f"{html_body_long_runs} long English token run(s) found in final HTML body paragraphs.")
        item = {
            "lectureId": lecture_id,
            "title": title,
            "llmSummaryStatus": (llm_status_by_lecture.get(lecture_id) or {}).get("llmSummaryStatus"),
            "llmCallAttempted": (llm_status_by_lecture.get(lecture_id) or {}).get("llmCallAttempted"),
            "llmCallSucceeded": (llm_status_by_lecture.get(lecture_id) or {}).get("llmCallSucceeded"),
            "llmParseSucceeded": (llm_status_by_lecture.get(lecture_id) or {}).get("llmParseSucceeded"),
            "llmRepairAttempted": (llm_status_by_lecture.get(lecture_id) or {}).get("llmRepairAttempted"),
            "llmRepairSucceeded": (llm_status_by_lecture.get(lecture_id) or {}).get("llmRepairSucceeded"),
            "reasonIfMissing": (llm_status_by_lecture.get(lecture_id) or {}).get("reasonIfMissing"),
            "sourceParagraphCount": len(paragraphs),
            "rawLikeParagraphCount": raw_like,
            "englishLeakageParagraphCount": english_leakage,
            "metadataLeakageCount": metadata_leakage,
            "longEnglishRunCount": long_runs,
            "chineseCharCount": cjk,
            "asciiWordCount": ascii_words,
            "sourceQuoteCount": quote_count,
            "glossaryTermCount": glossary_terms,
            "badGlossaryEntryCount": bad_glossary,
            "pageTitleHeadingCount": page_headings,
            "overlongEnglishTitleCount": overlong_titles,
            "slideFigureCount": slide_figures,
            "sourceExcerptCount": source_excerpts,
            "visualOnlySectionCount": visual_only,
            "highQualityChineseSummaryCount": high_quality_summaries,
            "sourceNotesGeneratedBy": generation_modes,
            "lowQualityChineseFallbackCount": low_quality_fallbacks,
            "missingSourceRefCount": missing_refs,
            "htmlBodyParagraphCount": len(lecture_body_paragraphs),
            "htmlBodyMetadataLeakageCount": html_body_metadata,
            "htmlBodyEnglishLeakageParagraphCount": html_body_english,
            "htmlBodyLongEnglishRunCount": html_body_long_runs,
            "warnings": warnings,
        }
        lectures.append(item)
        summary["lectureCount"] += 1
        summary["sourceParagraphCount"] += len(paragraphs)
        summary["rawLikeParagraphCount"] += raw_like
        summary["englishLeakageParagraphCount"] += english_leakage
        summary["metadataLeakageCount"] += metadata_leakage
        summary["longEnglishRunCount"] += long_runs
        summary["sourceQuoteCount"] += quote_count
        summary["glossaryTermCount"] += glossary_terms
        summary["badGlossaryEntryCount"] += bad_glossary
        summary["pageTitleHeadingCount"] += page_headings
        summary["overlongEnglishTitleCount"] += overlong_titles
        summary["slideFigureCount"] += slide_figures
        summary["sourceExcerptCount"] += source_excerpts
        summary["visualOnlySectionCount"] += visual_only
        summary["highQualityChineseSummaryCount"] += high_quality_summaries
        for mode, count in generation_modes.items():
            summary["sourceNotesGeneratedBy"][mode] += count
        summary["lowQualityChineseFallbackCount"] += low_quality_fallbacks
        summary["missingSourceRefCount"] += missing_refs
    practice = practice_type_check(script_js)
    if not practice["ok"]:
        summary["practiceGeneratorWarnings"] = 1
    if summary["lectureCount"] and summary["sourcesPanelCount"] < summary["lectureCount"]:
        summary["sourcesPanelWarning"] = "Some lecture source lists were not rendered as collapsible sources panels."
    if summary["sourcesPanelCount"] != summary["sourcesListCount"]:
        summary["sourcesPanelWarning"] = "A sources panel is missing its sources-list content."
    if llm_summary["missingCount"] and llm_summary["missingReasonCount"] < llm_summary["missingCount"]:
        summary["llmSummaryMissingReasonWarning"] = "Some missing LLM summaries do not include reasonIfMissing."
    llm_telemetry = metadata.get("llmTelemetry") or {}
    llm_enabled_requested = bool(llm_telemetry.get("llmEnabled"))
    llm_connection_ok = bool(llm_telemetry.get("llmConnectionOk"))
    llm_calls_attempted = int(llm_telemetry.get("llmCallsAttempted") or 0)
    if not llm_enabled_requested and summary["sourceNotesGeneratedBy"]["llm_summary_zh"] > 0:
        summary["llmModeMismatch"] = "LLM disabled but llm_summary_zh sections were rendered."
    if llm_enabled_requested and llm_connection_ok and llm_calls_attempted == 0:
        summary["llmModeMismatch"] = "LLM connection ok but no LLM calls were attempted."
    if llm_enabled_requested and llm_connection_ok and summary["sourceNotesGeneratedBy"]["fallback_cleaned_excerpt"] > summary["sourceNotesGeneratedBy"]["llm_summary_zh"]:
        summary["llmFallbackWarning"] = "LLM connected, but most Source-grounded Notes are fallback_cleaned_excerpt."
    hard_fail = (
        summary["metadataLeakageCount"] > 0
        or summary["englishLeakageParagraphCount"] > 0
        or summary["longEnglishRunCount"] > 0
        or summary["htmlBodyMetadataLeakageCount"] > 0
        or summary["htmlBodyEnglishLeakageParagraphCount"] > 0
        or summary["htmlBodyLongEnglishRunCount"] > 0
        or summary["lowQualityChineseFallbackCount"] > 0
        or summary["llmSummaryMarkdownArtifactCount"] > 0
        or bool(summary.get("llmSummaryMissingReasonWarning"))
        or bool(summary.get("llmModeMismatch"))
    )
    if llm_enabled_requested and llm_connection_ok and llm_summary["successCount"] < llm_summary["lectureCount"]:
        summary["llmSummaryWarning"] = "Some lectures did not produce a validated LLM summary."
    warning_only = bool(summary.get("llmFallbackWarning")) or (llm_enabled_requested and not llm_connection_ok)
    warning_only = warning_only or bool(summary.get("sourcesPanelWarning"))
    warning_only = warning_only or bool(summary.get("llmSummaryWarning"))
    status = "passed" if (
        not hard_fail
        and not warning_only
        and summary["rawLikeParagraphCount"] == 0
        and summary["overlongEnglishTitleCount"] == 0
        and summary["badGlossaryEntryCount"] == 0
        and summary["pageTitleHeadingCount"] == 0
        and summary["missingSourceRefCount"] == 0
        and practice["ok"]
    ) else ("failed" if hard_fail else "warnings")
    return {
        "runId": metadata.get("runId"),
        "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "status": status,
        "generationMode": metadata.get("generationMode", "offline"),
        "llmEnabled": llm_enabled_requested,
        "llmConnectionOk": llm_connection_ok,
        "llmCallsAttempted": llm_calls_attempted,
        "llmCallsSucceeded": int(llm_telemetry.get("llmCallsSucceeded") or 0),
        "llmCallsFailed": int(llm_telemetry.get("llmCallsFailed") or 0),
        "llmParseSucceeded": int(llm_telemetry.get("llmParseSucceeded") or 0),
        "llmRepairAttempted": int(llm_telemetry.get("llmRepairAttempted") or 0),
        "llmRepairSucceeded": int(llm_telemetry.get("llmRepairSucceeded") or 0),
        "sourceNotesGeneratedBy": summary["sourceNotesGeneratedBy"],
        "llmSummary": llm_summary,
        "llmTelemetry": llm_telemetry,
        "summary": summary,
        "practiceGenerator": practice,
        "lectures": lectures,
    }


def write_qa_report(output_path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    report = build_qa_report(output_path, metadata)
    (output_path / "qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = "\n".join(
        f"<tr><td>{html.escape(item['lectureId'])}</td><td>{html.escape(item['title'])}</td><td>{item['rawLikeParagraphCount']}</td><td>{item['sourceQuoteCount']}</td><td>{item['badGlossaryEntryCount']}</td><td>{html.escape('; '.join(item['warnings']))}</td></tr>"
        for item in report["lectures"]
    )
    report_html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QA Report - {html.escape(str(report.get('runId')))}</title>
<style>body{{font-family:Arial,sans-serif;line-height:1.6;margin:2rem;color:#17233c}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:.5rem;vertical-align:top}}th{{background:#f5f5f5}}</style></head>
<body><h1>QA Report</h1><p>Status: <strong>{html.escape(report['status'])}</strong></p>
<pre>{html.escape(json.dumps(report['summary'], ensure_ascii=False, indent=2))}</pre>
<table><thead><tr><th>Lecture</th><th>Title</th><th>Raw-like</th><th>Quotes</th><th>Bad glossary</th><th>Warnings</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>"""
    (output_path / "qa_report.html").write_text(report_html, encoding="utf-8")
    return report

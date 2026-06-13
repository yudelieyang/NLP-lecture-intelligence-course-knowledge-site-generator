from __future__ import annotations

import json
import re
from typing import Any

from scripts.models import LectureUnit
from scripts.utils import (
    contains_course_metadata,
    detect_english_leakage,
    normalize_ws,
    strip_course_metadata,
)


SUMMARY_SCHEMA_TEXT = """
{
  "summaryTitle": "string",
  "language": "zh",
  "generationType": "llm_summary_zh",
  "sections": [
    {
      "title": "string",
      "paragraphs": [
        {"text": "string", "sourceRefs": ["Lecture 02, p.1"]}
      ],
      "keyTerms": ["NLP"],
      "sourceQuotes": [{"text": "short quote", "sourceRef": "Lecture 02, p.1"}]
    }
  ],
  "glossaryCandidates": [
    {"term": "string", "briefExplanation": "string", "sourceRefs": ["Lecture 02, p.1"]}
  ],
  "warnings": []
}
""".strip()


LLM_SUMMARY_SYSTEM_PROMPT = """
You generate structured Chinese source-grounded study notes from lecture source text.
Return valid JSON only.
Do not return Markdown.
Do not wrap the JSON in ```json fences.
Do not include any introduction or explanation outside JSON.
Use only the provided source text.
Do not invent unsupported facts.
Write explanatory paragraphs in Chinese.
Preserve important English technical terms, model names, formulas, and variables.
Every paragraph must include sourceRefs from the provided source references.
Do not paste raw slide text as paragraphs.
Do not include course metadata such as course number, instructor name, university name, or repeated lecture title in paragraphs.
If original wording is important, put it into sourceQuotes as a short quote.
""".strip()


MARKDOWN_PREFIX_PATTERNS = [
    r"^#+\s*",
    r"^[-*]\s+",
    r"^\d+[.)]\s+",
]


INTRO_PATTERNS = [
    r"^以下是[^。.!?]*[。:：]\s*",
    r"^下面是[^。.!?]*[。:：]\s*",
    r"^根据您提供[^。.!?]*[。:：]\s*",
    r"^Here is[^.?!]*[.?:]\s*",
    r"^Based on the provided[^.?!]*[.?:]\s*",
]


def strip_markdown_artifacts(text: str) -> str:
    value = normalize_ws(text or "")
    value = re.sub(r"```(?:json)?|```", " ", value, flags=re.I)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"-{3,}", " ", value)
    for pattern in INTRO_PATTERNS:
        value = re.sub(pattern, "", value, flags=re.I)
    for pattern in MARKDOWN_PREFIX_PATTERNS:
        value = re.sub(pattern, "", value)
    return normalize_ws(value)


def sanitize_llm_paragraph(text: str, lecture_title: str) -> str:
    value = strip_markdown_artifacts(text)
    value = strip_course_metadata(value, lecture_title)
    value = re.sub(r"\s*#{1,6}\s*", " ", value)
    value = value.replace("**", "")
    return normalize_ws(value)


def extract_json_from_llm_response(response_text: str) -> dict[str, Any] | None:
    raw = (response_text or "").strip()
    if not raw:
        return None
    candidates = [raw]
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.I | re.S)
    if fence:
        candidates.insert(0, fence.group(1))
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        candidates.append(raw[start : end + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def source_pages_for_prompt(unit: LectureUnit, limit: int = 24, max_chars_per_page: int = 1800) -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    for section in unit.pages_or_sections[:limit]:
        text = strip_course_metadata(normalize_ws(section.text), unit.lecture_title)
        if not text:
            continue
        pages.append({"sourceRef": section.source_ref, "text": text[:max_chars_per_page]})
    return pages


def build_llm_summary_prompt(unit: LectureUnit) -> str:
    pages = source_pages_for_prompt(unit)
    source_refs = [page["sourceRef"] for page in pages]
    return (
        f"{LLM_SUMMARY_SYSTEM_PROMPT}\n\n"
        f"Lecture title:\n{unit.lecture_title}\n\n"
        f"Available source references:\n{json.dumps(source_refs, ensure_ascii=False, indent=2)}\n\n"
        f"Source pages:\n{json.dumps(pages, ensure_ascii=False, indent=2)}\n\n"
        "Task:\nGenerate Chinese source-grounded study notes using the required JSON schema.\n\n"
        f"Required JSON schema:\n{SUMMARY_SCHEMA_TEXT}\n\n"
        "Return JSON only."
    )


def build_llm_summary_repair_prompt(raw_response: str, source_refs: list[str]) -> str:
    return (
        "You convert messy model output into the required JSON schema.\n"
        "Return valid JSON only. No Markdown. No explanations.\n\n"
        "The previous model response was not valid JSON or did not match the schema:\n"
        f"{raw_response[:12000]}\n\n"
        f"Required schema:\n{SUMMARY_SCHEMA_TEXT}\n\n"
        f"Lecture source references:\n{json.dumps(source_refs, ensure_ascii=False, indent=2)}\n\n"
        "Convert it to valid JSON only."
    )


def validate_llm_summary_schema(data: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return False, ["summary is not an object"]
    if data.get("language") != "zh":
        errors.append("language must be zh")
    if data.get("generationType") != "llm_summary_zh":
        errors.append("generationType must be llm_summary_zh")
    title = data.get("summaryTitle")
    if not isinstance(title, str) or not title.strip():
        errors.append("summaryTitle is required")
    elif len(title) > 40:
        errors.append("summaryTitle is too long")
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty list")
    else:
        if len(sections) > 8:
            errors.append("sections should not exceed 8")
        for section_index, section in enumerate(sections):
            if not isinstance(section, dict):
                errors.append(f"sections[{section_index}] is not an object")
                continue
            if not isinstance(section.get("title"), str) or not section.get("title", "").strip():
                errors.append(f"sections[{section_index}].title is required")
            paragraphs = section.get("paragraphs")
            if not isinstance(paragraphs, list) or not paragraphs:
                errors.append(f"sections[{section_index}].paragraphs is required")
                continue
            for paragraph_index, paragraph in enumerate(paragraphs):
                if not isinstance(paragraph, dict):
                    errors.append(f"sections[{section_index}].paragraphs[{paragraph_index}] is not an object")
                    continue
                text = paragraph.get("text")
                refs = paragraph.get("sourceRefs")
                if not isinstance(text, str) or not text.strip():
                    errors.append(f"paragraph {section_index}.{paragraph_index} text is required")
                    continue
                if re.search(r"(^|\s)#{1,6}\s|```|\*\*|-{3,}", text):
                    errors.append(f"paragraph {section_index}.{paragraph_index} contains markdown artifacts")
                if contains_course_metadata(text) or detect_english_leakage(text).get("metadataHits"):
                    errors.append(f"paragraph {section_index}.{paragraph_index} contains course metadata")
                if not isinstance(refs, list) or not any(isinstance(ref, str) and ref.strip() for ref in refs):
                    errors.append(f"paragraph {section_index}.{paragraph_index} sourceRefs are required")
            quotes = section.get("sourceQuotes", [])
            if quotes is not None and not isinstance(quotes, list):
                errors.append(f"sections[{section_index}].sourceQuotes must be a list")
            elif isinstance(quotes, list):
                for quote_index, quote in enumerate(quotes):
                    if not isinstance(quote, dict):
                        errors.append(f"source quote {section_index}.{quote_index} is not an object")
                        continue
                    quote_text = normalize_ws(str(quote.get("text", "")))
                    if len(re.findall(r"[A-Za-z]+", quote_text)) > 30:
                        errors.append(f"source quote {section_index}.{quote_index} is too long")
    return not errors, errors


def normalize_llm_summary(data: dict[str, Any], lecture_title: str, fallback_ref: str) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "summaryTitle": strip_markdown_artifacts(str(data.get("summaryTitle") or "LLM Structured Summary"))[:40],
        "language": "zh",
        "generationType": "llm_summary_zh",
        "sections": [],
        "glossaryCandidates": [],
        "warnings": [],
    }
    for section in data.get("sections") or []:
        if not isinstance(section, dict):
            continue
        title = sanitize_llm_paragraph(str(section.get("title") or "核心概念"), lecture_title)[:36] or "核心概念"
        paragraphs = []
        for paragraph in section.get("paragraphs") or []:
            if not isinstance(paragraph, dict):
                continue
            text = sanitize_llm_paragraph(str(paragraph.get("text") or ""), lecture_title)
            if not text:
                continue
            refs = [normalize_ws(str(ref)) for ref in paragraph.get("sourceRefs") or [] if normalize_ws(str(ref))]
            if not refs:
                refs = [fallback_ref]
            paragraphs.append({"text": text, "sourceRefs": refs[:4]})
        if not paragraphs:
            continue
        key_terms = [strip_markdown_artifacts(str(term)) for term in section.get("keyTerms") or []]
        source_quotes = []
        for quote in section.get("sourceQuotes") or []:
            if not isinstance(quote, dict):
                continue
            quote_text = strip_markdown_artifacts(str(quote.get("text") or ""))
            words = re.findall(r"\S+", quote_text)
            if not quote_text or len(words) > 30:
                continue
            source_quotes.append({"text": quote_text, "sourceRef": normalize_ws(str(quote.get("sourceRef") or fallback_ref))})
        normalized["sections"].append(
            {
                "title": title,
                "paragraphs": paragraphs[:3],
                "keyTerms": [term for term in key_terms if term][:8],
                "sourceQuotes": source_quotes[:2],
            }
        )
    for item in data.get("glossaryCandidates") or []:
        if not isinstance(item, dict):
            continue
        term = strip_markdown_artifacts(str(item.get("term") or ""))
        explanation = sanitize_llm_paragraph(str(item.get("briefExplanation") or ""), lecture_title)
        refs = [normalize_ws(str(ref)) for ref in item.get("sourceRefs") or [] if normalize_ws(str(ref))]
        if term and explanation:
            normalized["glossaryCandidates"].append({"term": term, "briefExplanation": explanation, "sourceRefs": refs or [fallback_ref]})
    warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else []
    normalized["warnings"] = [strip_markdown_artifacts(str(item)) for item in warnings if str(item).strip()][:8]
    return normalized


def missing_llm_summary_status(lecture_id: str, status: str, reason: str | None, *, llm_enabled: bool = False) -> dict[str, Any]:
    return {
        "lectureId": lecture_id,
        "llmSummaryStatus": status,
        "llmCallAttempted": False,
        "llmCallSucceeded": False,
        "llmParseSucceeded": False,
        "llmRepairAttempted": False,
        "llmRepairSucceeded": False,
        "reasonIfMissing": reason,
        "llmEnabled": llm_enabled,
    }

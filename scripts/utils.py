from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".docx"}


LOW_QUALITY_CHINESE_FALLBACK_PATTERNS = [
    "这一部分围绕",
    "本节围绕",
    "本部分主要围绕",
    "本段原始材料主要围绕",
    "课件在这里不是单独罗列概念",
    "如何服务于本讲的问题",
    "保守中文概述",
    "当前未启用 LLM",
    "这里只提供基于关键词",
    "heuristic Chinese restructuring",
    "本页主要展示了当前小节的关键概念或示例",
    "由于可提取文本有限",
    "正文在这里做中文重组",
]


def slugify(value: str, fallback: str = "notes_site") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or fallback


def now_stamp() -> tuple[str, str]:
    now = datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M:%S"), now.strftime("%Y-%m-%d_%H%M%S")


def detect_lecture_number(path: Path) -> int | None:
    match = re.search(r"\blectures?\s*0*(\d+)\b", path.stem, flags=re.I)
    if match:
        return int(match.group(1))
    return None


def make_lecture_id(path: Path, fallback_index: int) -> str:
    number = detect_lecture_number(path)
    if number is not None:
        return f"lecture-{number:02d}"
    return f"lecture-unit-{fallback_index:02d}"


def make_lecture_title(path: Path, fallback_index: int) -> str:
    number = detect_lecture_number(path)
    title = path.stem.replace("_", " ").strip()
    if number is not None:
        return title
    return f"Lecture Unit {fallback_index:02d}: {title}"


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def count_chinese_chars(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text or ""))


def count_ascii_words(text: str) -> int:
    return len(re.findall(r"\b[A-Za-z][A-Za-z0-9_+-]*\b", text or ""))


ALLOWED_TECH_TERMS = {
    "nlp",
    "ml",
    "dl",
    "gpt",
    "gpt-2",
    "gpt-3",
    "bert",
    "t5",
    "rnn",
    "lstm",
    "gru",
    "asr",
    "bow",
    "tf-idf",
    "pca",
    "word2vec",
    "transformer",
    "attention",
    "self-attention",
    "softmax",
    "webtext",
    "temperature",
    "top-p",
    "moe",
    "mixture",
    "experts",
    "embedding",
    "embeddings",
    "pretraining",
    "fine-tuning",
    "token",
    "tokens",
    "language",
    "model",
    "models",
    "audio",
    "processing",
    "speech",
    "recognition",
    "acoustic",
    "perplexity",
    "smoothing",
    "sampling",
}


COURSE_METADATA_PATTERNS = [
    r"\bBoston\s+University\b",
    r"\bWayne\s+Snyder\b",
    r"\bCS\s*505\b",
    r"\bIntroduction\s+to\s+Natural\s+Language\s+Processing\b",
    r"\bNatural\s+Language\s+Processing\b",
    r"\bLecture\s+\d+\s*(?:--|:|-)\s*[A-Za-z0-9 ,.&/+-]+",
    r"\bLecture\s+\d+\b",
    r"\bPage\s+\d+\b",
    r"\bSec\.\s*\d+(?:\.\d+)*\b",
    r"\bCopyright\b",
    r"\bDepartment\b",
    r"\bCourse\b",
    r"\bUniversity\b",
]


def metadata_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in COURSE_METADATA_PATTERNS:
        for match in re.finditer(pattern, text or "", flags=re.I):
            value = normalize_ws(match.group(0))
            if value and value not in hits:
                hits.append(value)
    return hits


def contains_course_metadata(text: str) -> bool:
    return bool(metadata_hits(text))


def english_token_runs(text: str, min_run: int = 8) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_+-]*|[^A-Za-z]+", text or "")
    runs: list[str] = []
    current: list[str] = []
    for token in tokens:
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_+-]*", token):
            current.append(token)
            continue
        if len(current) >= min_run:
            runs.append(" ".join(current))
        current = []
    if len(current) >= min_run:
        runs.append(" ".join(current))
    return runs


def contains_long_english_run(text: str, min_run: int = 8) -> bool:
    for run in english_token_runs(text, min_run=min_run):
        words = [word.lower() for word in run.split()]
        non_term_words = [word for word in words if word not in ALLOWED_TECH_TERMS]
        if len(non_term_words) >= 4:
            return True
    return False


def detect_english_leakage(text: str) -> dict:
    clean = normalize_ws(text)
    chinese_chars = count_chinese_chars(clean)
    ascii_words = count_ascii_words(clean)
    total_units = chinese_chars + ascii_words
    english_ratio = ascii_words / total_units if total_units else 0.0
    long_runs = english_token_runs(clean, min_run=8)
    metadata = metadata_hits(clean)
    reasons: list[str] = []
    filtered_runs = []
    for run in long_runs:
        words = [word.lower() for word in run.split()]
        non_term_words = [word for word in words if word not in ALLOWED_TECH_TERMS]
        if len(non_term_words) >= 4:
            filtered_runs.append(run)
    if filtered_runs:
        reasons.append("long English run")
    if metadata:
        reasons.append("course metadata")
    if ascii_words >= 18 and chinese_chars < 80 and english_ratio > 0.35:
        reasons.append("high English token ratio")
    return {
        "hasLeakage": bool(reasons),
        "englishTokenRatio": english_ratio,
        "longEnglishRuns": filtered_runs,
        "metadataHits": metadata,
        "reason": " / ".join(reasons),
    }


def strip_course_metadata(text: str, lecture_title: str = "") -> str:
    cleaned = text or ""
    if lecture_title:
        cleaned = re.sub(re.escape(lecture_title), " ", cleaned, flags=re.I)
    for pattern in COURSE_METADATA_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\b(?:Wayne|Snyder|Boston|University)\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+([,.;:，。；：])", r"\1", cleaned)
    return normalize_ws(cleaned)


def is_low_quality_chinese_fallback(text: str) -> bool:
    clean = normalize_ws(text)
    return any(pattern.lower() in clean.lower() for pattern in LOW_QUALITY_CHINESE_FALLBACK_PATTERNS)


def rewrite_mixed_paragraph_to_chinese(
    text: str,
    source_refs: list[str] | None = None,
    llm_client: object | None = None,
    key_terms: list[str] | None = None,
    lecture_title: str | None = None,
) -> str:
    stripped = strip_course_metadata(text, lecture_title or "")
    leakage = detect_english_leakage(stripped)
    if not leakage["hasLeakage"] and not looks_like_raw_english_dump(stripped):
        return stripped
    if llm_client is not None and getattr(llm_client, "available", lambda: False)():
        prompt = (
            "You are cleaning and rewriting lecture note paragraphs into Chinese study notes.\n"
            "The output MUST be a Chinese explanatory paragraph. Preserve only important English technical terms, "
            "model names, formulas, and variables. Remove course metadata, slide headers, author names, "
            "university names, lecture titles, and raw extracted slide fragments. Do not paste long English source text.\n\n"
            f"Paragraph with possible English leakage:\n{stripped[:4000]}\n\n"
            f"Lecture title:\n{lecture_title or ''}\n\n"
            f"Source references:\n{source_refs or []}\n\n"
            f"Key terms:\n{key_terms or []}\n\n"
            "Rewrite this into 1 concise Chinese study-note paragraph. Return only the paragraph text."
        )
        try:
            rewritten = normalize_ws(llm_client.summarize(prompt))
            if rewritten and not detect_english_leakage(rewritten)["hasLeakage"]:
                return rewritten
        except Exception:
            pass
    terms = key_terms or extract_candidate_terms(stripped, limit=5)
    return build_heuristic_chinese_note(stripped, source_refs, terms)


def looks_like_raw_english_dump(text: str) -> bool:
    if not text:
        return False
    stripped = normalize_ws(text)
    if len(stripped) < 180:
        return False
    if count_chinese_chars(stripped) >= 20:
        return False
    ascii_words = count_ascii_words(stripped)
    if ascii_words < 25:
        return False
    code_formula_markers = ("def ", "class ", "import ", "return ", "\\frac", "$$", "```")
    if any(marker in stripped for marker in code_formula_markers):
        return False
    return True


def validate_source_note_paragraph(text: str) -> bool:
    return not looks_like_raw_english_dump(text) and not detect_english_leakage(text).get("hasLeakage")


def extract_candidate_terms(text: str, limit: int = 5) -> list[str]:
    text = strip_course_metadata(text or "")
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9_+-]*(?:\s+[A-Za-z][A-Za-z0-9_+-]*){0,2}\b", text or "")
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "are",
        "you",
        "can",
        "will",
        "lecture",
        "page",
        "introduction",
        "natural",
        "language",
        "processing",
        "wayne",
        "snyder",
        "boston",
        "university",
        "cs",
    }
    terms: list[str] = []
    for word in words:
        cleaned = normalize_ws(word).strip(".,:;()[]{}")
        if not cleaned or cleaned.lower() in stop:
            continue
        if len(cleaned) < 3:
            continue
        if cleaned not in terms:
            terms.append(cleaned)
        if len(terms) >= limit:
            break
    return terms


def build_heuristic_chinese_note(raw_text: str, source_refs: list[str] | None = None, terms: list[str] | None = None) -> str:
    return ""


def rewrite_source_text_to_chinese_note(
    raw_text: str,
    source_refs: list[str] | None = None,
    llm_client: object | None = None,
    terms: list[str] | None = None,
) -> str:
    if llm_client is not None and getattr(llm_client, "available", lambda: False)():
        prompt = (
            "You are rewriting extracted lecture slide text into Chinese source-grounded study notes.\n"
            "The output paragraph MUST be in Chinese. Preserve important English technical terms, model names, "
            "formulas, and variable names. Do not invent facts beyond the provided source text. "
            "Do not paste the raw English text as the paragraph.\n\n"
            f"Raw extracted source text:\n{raw_text[:4000]}\n\n"
            f"Source references:\n{source_refs or []}\n\n"
            "Write 1 concise Chinese study-note paragraph. Return only the paragraph text."
        )
        try:
            rewritten = normalize_ws(llm_client.summarize(prompt))
            if rewritten and validate_source_note_paragraph(rewritten):
                return rewritten
        except Exception:
            pass
    return build_heuristic_chinese_note(raw_text, source_refs, terms)


def split_text_sections(text: str, lecture_label: str, section_prefix: str) -> list[tuple[str, str, str]]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    if not blocks and text.strip():
        blocks = [text.strip()]
    sections: list[tuple[str, str, str]] = []
    current: list[str] = []
    current_title = "Section 1"
    section_no = 1
    for block in blocks:
        heading = block.strip().splitlines()[0].strip()
        is_heading = heading.startswith("#") or (len(heading) < 90 and not heading.endswith(".") and len(block.splitlines()) <= 2)
        if is_heading and current:
            sections.append((f"{section_prefix}-{section_no:03d}", current_title, "\n\n".join(current)))
            section_no += 1
            current = []
            current_title = heading.lstrip("#").strip() or f"Section {section_no}"
        elif is_heading:
            current_title = heading.lstrip("#").strip() or current_title
            continue
        current.append(block)
    if current:
        sections.append((f"{section_prefix}-{section_no:03d}", current_title, "\n\n".join(current)))
    if not sections:
        sections.append((f"{section_prefix}-001", "Section 1", text))
    return sections

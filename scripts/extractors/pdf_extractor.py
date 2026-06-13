from __future__ import annotations

from pathlib import Path
import re

from scripts.models import LectureUnit, SourceSection
from scripts.utils import make_lecture_id, make_lecture_title


GENERIC_TITLES = [
    "Core Idea",
    "Model Workflow",
    "Key Example",
    "Evaluation Setup",
    "Practical Limitation",
    "Conceptual Bridge",
]


def infer_semantic_section_title(page_text: str, lecture_title: str, page_number: int) -> str:
    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    bad_patterns = [
        r"^page\s+\d+$",
        r"^\d+$",
        r"^lecture\s+\d+",
        r"^cs\s+\d+",
        r"^ec508",
        r"^natural language processing$",
        r"^introduction to$",
        r"^wayne\s+snyder$",
        r"^boston\s+university$",
        r"^tree$",
    ]
    for line in lines[:8]:
        clean = re.sub(r"\s+", " ", line).strip(" -:\t")
        if not clean or len(clean) > 90:
            continue
        if any(re.search(pattern, clean, flags=re.I) for pattern in bad_patterns):
            continue
        if len(clean) >= 8 and len(clean.split()) <= 12 and re.search(r"[A-Za-z]", clean):
            return clean

    lower = page_text.lower()
    keyword_titles = [
        ("cosine", "Cosine Similarity"),
        ("tf-idf", "TF-IDF Weighting"),
        ("bag of words", "Bag-of-Words Representation"),
        ("bow", "Bag-of-Words Representation"),
        ("embedding", "Word and Text Embeddings"),
        ("word2vec", "word2vec Training Objective"),
        ("supervised", "Supervised Learning Setup"),
        ("gradient", "Gradient-based Optimization"),
        ("rnn", "RNN Sequence Modeling"),
        ("lstm", "Gate-based Memory with LSTM"),
        ("gru", "Gate-based Memory with GRU"),
        ("attention", "Attention Mechanism"),
        ("transformer", "Transformer Architecture"),
        ("bert", "BERT Pretraining"),
        ("gpt", "GPT-style Generation"),
        ("t5", "T5 Text-to-Text Framework"),
        ("asr", "ASR Pipeline"),
        ("acoustic", "Acoustic Modeling"),
        ("workflow", "Model Workflow"),
        ("evaluation", "Evaluation Setup"),
        ("perplexity", "Language Model Evaluation"),
        ("smoothing", "Smoothing for Sparse Counts"),
        ("language model", "Language Model Objective"),
    ]
    for keyword, title in keyword_titles:
        if keyword in lower:
            return title
    return GENERIC_TITLES[(page_number - 1) % len(GENERIC_TITLES)]


def visual_score(page: object, text: str) -> int:
    score = 0
    try:
        score += min(len(page.get_images()), 4) * 3
        score += min(len(page.get_drawings()), 12) // 2
    except Exception:
        pass
    lower = text.lower()
    visual_keywords = [
        "figure",
        "diagram",
        "model",
        "architecture",
        "workflow",
        "example",
        "cosine",
        "matrix",
        "vector",
        "attention",
        "transformer",
        "rnn",
        "pca",
        "loss",
        "perplexity",
    ]
    score += sum(2 for keyword in visual_keywords if keyword in lower)
    if re.search(r"[=∑ΣΠ√≤≥≈→←↔λθαβ]|\\frac|P\(", text):
        score += 4
    if len(text.strip()) < 120:
        score += 2
    return score


def extract_pdf(path: Path, fallback_index: int) -> LectureUnit:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required to read PDF files. Install requirements.txt.") from exc

    lecture_id = make_lecture_id(path, fallback_index)
    unit = LectureUnit(
        lecture_id=lecture_id,
        lecture_title=make_lecture_title(path, fallback_index),
        source_file=path.name,
        source_type="pdf",
        metadata={"source_path": str(path.resolve())},
    )
    document = fitz.open(path)
    for page_index, page in enumerate(document, start=1):
        text = page.get_text("text").strip()
        if not text:
            text = "[No extractable text on this page. OCR is not enabled in this version.]"
        title = infer_semantic_section_title(text, unit.lecture_title, page_index)
        unit.pages_or_sections.append(
            SourceSection(
                id=f"{lecture_id}-page-{page_index:03d}",
                title=title,
                text=text,
                source_ref=f"{unit.lecture_title}, p.{page_index}",
                page_number=page_index,
                metadata={"visual_score": visual_score(page, text)},
            )
        )
    document.close()
    return unit

from __future__ import annotations

from pathlib import Path

from scripts.models import LectureUnit, SourceSection
from scripts.utils import make_lecture_id, make_lecture_title, split_text_sections


def extract_docx(path: Path, fallback_index: int) -> LectureUnit:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("python-docx is required to read DOCX files. Install requirements.txt.") from exc

    lecture_id = make_lecture_id(path, fallback_index)
    document = Document(path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    text = "\n\n".join(paragraphs)
    unit = LectureUnit(
        lecture_id=lecture_id,
        lecture_title=make_lecture_title(path, fallback_index),
        source_file=path.name,
        source_type="docx",
    )
    for section_index, (section_id, title, body) in enumerate(split_text_sections(text, unit.lecture_title, lecture_id), start=1):
        unit.pages_or_sections.append(
            SourceSection(
                id=section_id,
                title=title,
                text=body,
                source_ref=f"{unit.lecture_title}, section {section_index}",
            )
        )
    return unit

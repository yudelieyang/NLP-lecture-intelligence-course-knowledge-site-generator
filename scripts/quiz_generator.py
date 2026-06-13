from __future__ import annotations

from scripts.models import LectureUnit
from scripts.site_builder import extract_terms


def build_source_grounded_prompt(unit: LectureUnit) -> str:
    """Return a compact prompt for source-grounded practice generation."""
    terms = ", ".join(extract_terms(unit.full_text)) or "course concepts"
    return (
        "Generate practice questions using only the supplied lecture text. "
        f"Lecture: {unit.lecture_title}. Key terms: {terms}. "
        "Preserve page references and do not introduce unsupported facts."
    )


def build_creative_extension_prompt(unit: LectureUnit) -> str:
    """Return a prompt for clearly labeled extension practice."""
    terms = ", ".join(extract_terms(unit.full_text)) or "course concepts"
    return (
        "Generate application-oriented practice inspired by the lecture. "
        f"Lecture: {unit.lecture_title}. Key terms: {terms}. "
        "Clearly label content as Creative Extension when it goes beyond the source."
    )

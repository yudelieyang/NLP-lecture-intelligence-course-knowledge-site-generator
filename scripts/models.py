from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceSection:
    id: str
    title: str
    text: str
    source_ref: str
    page_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LectureUnit:
    lecture_id: str
    lecture_title: str
    source_file: str
    source_type: str
    pages_or_sections: list[SourceSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(section.text for section in self.pages_or_sections if section.text)

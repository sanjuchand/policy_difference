"""Document data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class DocumentType(str, Enum):
    """Types of policy documents."""
    INSURANCE_POLICY = "insurance_policy"
    HEALTH_POLICY = "health_policy"
    LEGAL_CONTRACT = "legal_contract"
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    EMPLOYEE_HANDBOOK = "employee_handbook"
    UNKNOWN = "unknown"


@dataclass
class DocumentMetadata:
    """Metadata about a parsed document."""
    filename: str
    file_path: Optional[Path] = None
    file_size_bytes: int = 0
    page_count: int = 0
    word_count: int = 0
    character_count: int = 0
    document_type: DocumentType = DocumentType.UNKNOWN
    parsed_at: datetime = field(default_factory=datetime.now)
    pdf_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "filename": self.filename,
            "file_path": str(self.file_path) if self.file_path else None,
            "file_size_bytes": self.file_size_bytes,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "document_type": self.document_type.value,
            "parsed_at": self.parsed_at.isoformat(),
            "pdf_metadata": self.pdf_metadata,
        }


@dataclass
class PageContent:
    """Content of a single page."""
    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        """Count words in the page."""
        return len(self.text.split())


@dataclass
class Document:
    """Represents a fully parsed document."""
    metadata: DocumentMetadata
    pages: list[PageContent] = field(default_factory=list)
    full_text: str = ""
    sections: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Compute derived fields after initialization."""
        if not self.full_text and self.pages:
            self.full_text = "\n\n".join(page.text for page in self.pages)

        if self.full_text:
            self.metadata.word_count = len(self.full_text.split())
            self.metadata.character_count = len(self.full_text)

    def get_page(self, page_number: int) -> Optional[PageContent]:
        """Get a specific page by number (1-indexed)."""
        if 1 <= page_number <= len(self.pages):
            return self.pages[page_number - 1]
        return None

    def get_text_range(self, start_char: int, end_char: int) -> str:
        """Get text within a character range."""
        return self.full_text[start_char:end_char]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "metadata": self.metadata.to_dict(),
            "pages": [
                {
                    "page_number": p.page_number,
                    "text": p.text,
                    "word_count": p.word_count,
                }
                for p in self.pages
            ],
            "full_text": self.full_text,
            "sections": self.sections,
        }

"""PDF parsing module for document ingestion."""

import re
from pathlib import Path
from typing import Optional

import pdfplumber

from policy_diff.models.document import (
    Document,
    DocumentMetadata,
    DocumentType,
    PageContent,
)


class PDFParseError(Exception):
    """Exception raised when PDF parsing fails."""

    pass


class PDFParser:
    """Parser for extracting text and structure from PDF documents."""

    # Common section header patterns for policy documents
    SECTION_PATTERNS = [
        r"^(?:ARTICLE|Article)\s+[IVXLCDM\d]+[.:]?\s*(.+)?$",
        r"^(?:SECTION|Section)\s+[\d.]+[.:]?\s*(.+)?$",
        r"^(?:\d+\.)+\s+[A-Z].*$",  # Numbered sections like "1.2.3 Coverage"
        r"^[A-Z][A-Z\s]{2,}$",  # ALL CAPS headers
        r"^(?:PART|Part)\s+[IVXLCDM\d]+[.:]?\s*(.+)?$",
        r"^(?:SCHEDULE|Schedule)\s+[A-Z\d]+[.:]?\s*(.+)?$",
        r"^(?:APPENDIX|Appendix)\s+[A-Z\d]+[.:]?\s*(.+)?$",
        r"^(?:EXHIBIT|Exhibit)\s+[A-Z\d]+[.:]?\s*(.+)?$",
    ]

    def __init__(self, extract_tables: bool = True, detect_sections: bool = True):
        """Initialize PDF parser.

        Args:
            extract_tables: Whether to extract tables as structured data
            detect_sections: Whether to detect and label document sections
        """
        self.extract_tables = extract_tables
        self.detect_sections = detect_sections
        self._compiled_patterns = [re.compile(p, re.MULTILINE) for p in self.SECTION_PATTERNS]

    def parse(self, file_path: Path | str) -> Document:
        """Parse a PDF file and extract its content.

        Args:
            file_path: Path to the PDF file

        Returns:
            Document object containing extracted content

        Raises:
            PDFParseError: If parsing fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise PDFParseError(f"File not found: {file_path}")

        if not file_path.suffix.lower() == ".pdf":
            raise PDFParseError(f"Not a PDF file: {file_path}")

        try:
            return self._extract_content(file_path)
        except Exception as e:
            raise PDFParseError(f"Failed to parse PDF: {e}") from e

    def _extract_content(self, file_path: Path) -> Document:
        """Extract content from PDF using pdfplumber.

        Args:
            file_path: Path to the PDF file

        Returns:
            Document object with extracted content
        """
        pages: list[PageContent] = []
        full_text_parts: list[str] = []
        pdf_metadata: dict = {}

        with pdfplumber.open(file_path) as pdf:
            pdf_metadata = pdf.metadata or {}
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, start=1):
                page_content = self._extract_page(page, page_num)
                pages.append(page_content)
                full_text_parts.append(page_content.text)

        full_text = "\n\n".join(full_text_parts)

        # Detect document type based on content
        doc_type = self._detect_document_type(full_text)

        # Extract sections if enabled
        sections = {}
        if self.detect_sections:
            sections = self._extract_sections(full_text)

        # Build metadata
        metadata = DocumentMetadata(
            filename=file_path.name,
            file_path=file_path,
            file_size_bytes=file_path.stat().st_size,
            page_count=total_pages,
            word_count=len(full_text.split()),
            character_count=len(full_text),
            document_type=doc_type,
            pdf_metadata=pdf_metadata,
        )

        return Document(
            metadata=metadata,
            pages=pages,
            full_text=full_text,
            sections=sections,
        )

    def _extract_page(self, page: pdfplumber.page.Page, page_num: int) -> PageContent:
        """Extract content from a single page.

        Args:
            page: pdfplumber page object
            page_num: Page number (1-indexed)

        Returns:
            PageContent object
        """
        # Extract main text
        text = page.extract_text() or ""

        # Extract tables if enabled
        tables: list[list[list[str]]] = []
        if self.extract_tables:
            raw_tables = page.extract_tables() or []
            for table in raw_tables:
                # Clean up table cells
                cleaned_table = [
                    [str(cell) if cell is not None else "" for cell in row]
                    for row in table
                    if row  # Skip empty rows
                ]
                if cleaned_table:
                    tables.append(cleaned_table)

        # Detect section headers on this page (stored for future use)
        section_headers = self._find_section_headers(text) if self.detect_sections else []

        return PageContent(
            page_number=page_num,
            text=text,
            tables=tables,
        )

    def _find_section_headers(self, text: str) -> list[str]:
        """Find section headers in text.

        Args:
            text: Text to search

        Returns:
            List of detected section headers
        """
        headers: list[str] = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in self._compiled_patterns:
                if pattern.match(line):
                    headers.append(line)
                    break

        return headers

    def _extract_sections(self, full_text: str) -> dict[str, str]:
        """Extract document sections based on headers.

        Args:
            full_text: Full document text

        Returns:
            Dictionary mapping section names to their content
        """
        sections: dict[str, str] = {}
        lines = full_text.split("\n")

        current_section: Optional[str] = None
        current_content: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Check if this line is a section header
            is_header = False
            for pattern in self._compiled_patterns:
                if pattern.match(stripped):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = "\n".join(current_content).strip()

                    current_section = stripped
                    current_content = []
                    is_header = True
                    break

            if not is_header and current_section:
                current_content.append(line)

        # Save last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect the type of policy document based on content.

        Args:
            text: Document text

        Returns:
            Detected DocumentType
        """
        text_lower = text.lower()

        # Check for insurance policy indicators
        insurance_keywords = [
            "policy period",
            "premium",
            "deductible",
            "coverage",
            "insured",
            "underwriter",
            "claim",
            "exclusion",
            "endorsement",
            "declarations page",
        ]
        insurance_score = sum(1 for kw in insurance_keywords if kw in text_lower)

        # Check for terms of service indicators
        tos_keywords = [
            "terms of service",
            "terms and conditions",
            "user agreement",
            "acceptable use",
            "privacy policy",
            "cookie policy",
            "account termination",
        ]
        tos_score = sum(1 for kw in tos_keywords if kw in text_lower)

        # Check for legal contract indicators
        contract_keywords = [
            "whereas",
            "hereby",
            "party",
            "agreement",
            "witnesseth",
            "covenant",
            "indemnify",
            "jurisdiction",
            "governing law",
        ]
        contract_score = sum(1 for kw in contract_keywords if kw in text_lower)

        # Determine type based on scores
        if insurance_score >= 3:
            return DocumentType.INSURANCE_POLICY
        elif tos_score >= 2:
            return DocumentType.TERMS_OF_SERVICE
        elif contract_score >= 3:
            return DocumentType.LEGAL_CONTRACT
        else:
            return DocumentType.UNKNOWN


def parse_pdf(file_path: Path | str, **kwargs) -> Document:
    """Convenience function to parse a PDF file.

    Args:
        file_path: Path to the PDF file
        **kwargs: Additional arguments passed to PDFParser

    Returns:
        Document object containing extracted content
    """
    parser = PDFParser(**kwargs)
    return parser.parse(file_path)

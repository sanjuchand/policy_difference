"""Document chunking module for breaking documents into comparable units."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from policy_diff.models.document import Document


class ChunkType(str, Enum):
    """Type of document chunk."""

    PARAGRAPH = "paragraph"
    SECTION = "section"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"


@dataclass
class Chunk:
    """A chunk of document text for comparison."""

    chunk_id: str
    text: str
    chunk_type: ChunkType
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    section_path: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        """Get word count of chunk."""
        return len(self.text.split())

    @property
    def char_count(self) -> int:
        """Get character count of chunk."""
        return len(self.text)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "chunk_type": self.chunk_type.value,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "page_number": self.page_number,
            "section_path": self.section_path,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "metadata": self.metadata,
        }


class DocumentChunker:
    """Chunks documents into comparable units for diff analysis."""

    # Sentence boundary patterns
    SENTENCE_ENDINGS = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

    # Paragraph boundary pattern
    PARAGRAPH_BOUNDARY = re.compile(r"\n\s*\n")

    def __init__(
        self,
        chunk_type: ChunkType = ChunkType.PARAGRAPH,
        max_chunk_size: int = 1000,
        min_chunk_size: int = 50,
        overlap: int = 100,
    ):
        """Initialize chunker.

        Args:
            chunk_type: Type of chunking to perform
            max_chunk_size: Maximum characters per chunk
            min_chunk_size: Minimum characters per chunk (smaller chunks merged)
            overlap: Character overlap between chunks for context
        """
        self.chunk_type = chunk_type
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Chunk a document into comparable units.

        Args:
            document: Document to chunk

        Returns:
            List of Chunk objects
        """
        if self.chunk_type == ChunkType.PARAGRAPH:
            return self._chunk_by_paragraph(document)
        elif self.chunk_type == ChunkType.SENTENCE:
            return self._chunk_by_sentence(document)
        elif self.chunk_type == ChunkType.SECTION:
            return self._chunk_by_section(document)
        elif self.chunk_type == ChunkType.SEMANTIC:
            return self._chunk_semantic(document)
        else:
            return self._chunk_by_paragraph(document)

    def _chunk_by_paragraph(self, document: Document) -> list[Chunk]:
        """Chunk document by paragraphs.

        Args:
            document: Document to chunk

        Returns:
            List of paragraph chunks
        """
        chunks: list[Chunk] = []
        text = document.full_text
        doc_id = document.metadata.filename

        # Split by paragraph boundaries
        paragraphs = self.PARAGRAPH_BOUNDARY.split(text)

        current_pos = 0
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                current_pos += 2  # Account for \n\n
                continue

            # Find actual position in original text
            start_pos = text.find(para, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            end_pos = start_pos + len(para)

            # Handle oversized paragraphs
            if len(para) > self.max_chunk_size:
                sub_chunks = self._split_large_text(
                    para, start_pos, doc_id, chunk_index
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
            elif len(para) >= self.min_chunk_size:
                chunk = Chunk(
                    chunk_id=f"{doc_id}_p{chunk_index}",
                    text=para,
                    chunk_type=ChunkType.PARAGRAPH,
                    start_char=start_pos,
                    end_char=end_pos,
                    page_number=self._find_page_number(document, start_pos),
                    section_path=self._find_section(document, start_pos),
                )
                chunks.append(chunk)
                chunk_index += 1

            current_pos = end_pos

        # Merge small trailing chunks
        chunks = self._merge_small_chunks(chunks)

        return chunks

    def _chunk_by_sentence(self, document: Document) -> list[Chunk]:
        """Chunk document by sentences.

        Args:
            document: Document to chunk

        Returns:
            List of sentence chunks
        """
        chunks: list[Chunk] = []
        text = document.full_text
        doc_id = document.metadata.filename

        # Split by sentence boundaries
        sentences = self.SENTENCE_ENDINGS.split(text)

        current_pos = 0
        chunk_index = 0
        buffer: list[str] = []
        buffer_start = 0

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            # Find position
            start_pos = text.find(sent, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            # Buffer sentences until we hit min size
            if not buffer:
                buffer_start = start_pos

            buffer.append(sent)
            buffer_text = " ".join(buffer)

            # Create chunk when buffer is large enough
            if len(buffer_text) >= self.min_chunk_size:
                chunk = Chunk(
                    chunk_id=f"{doc_id}_s{chunk_index}",
                    text=buffer_text,
                    chunk_type=ChunkType.SENTENCE,
                    start_char=buffer_start,
                    end_char=buffer_start + len(buffer_text),
                    page_number=self._find_page_number(document, buffer_start),
                    section_path=self._find_section(document, buffer_start),
                )
                chunks.append(chunk)
                chunk_index += 1
                buffer = []

            current_pos = start_pos + len(sent)

        # Handle remaining buffer
        if buffer:
            buffer_text = " ".join(buffer)
            chunk = Chunk(
                chunk_id=f"{doc_id}_s{chunk_index}",
                text=buffer_text,
                chunk_type=ChunkType.SENTENCE,
                start_char=buffer_start,
                end_char=buffer_start + len(buffer_text),
                page_number=self._find_page_number(document, buffer_start),
                section_path=self._find_section(document, buffer_start),
            )
            chunks.append(chunk)

        return chunks

    def _chunk_by_section(self, document: Document) -> list[Chunk]:
        """Chunk document by detected sections.

        Args:
            document: Document to chunk

        Returns:
            List of section chunks
        """
        chunks: list[Chunk] = []
        doc_id = document.metadata.filename

        if not document.sections:
            # Fall back to paragraph chunking
            return self._chunk_by_paragraph(document)

        chunk_index = 0
        text = document.full_text

        for section_name, section_text in document.sections.items():
            section_text = section_text.strip()
            if not section_text:
                continue

            # Find position in original text
            start_pos = text.find(section_text)
            if start_pos == -1:
                start_pos = 0

            # Handle oversized sections
            if len(section_text) > self.max_chunk_size:
                sub_chunks = self._split_large_text(
                    section_text, start_pos, doc_id, chunk_index, section_name
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
            else:
                chunk = Chunk(
                    chunk_id=f"{doc_id}_sec{chunk_index}",
                    text=section_text,
                    chunk_type=ChunkType.SECTION,
                    start_char=start_pos,
                    end_char=start_pos + len(section_text),
                    page_number=self._find_page_number(document, start_pos),
                    section_path=section_name,
                )
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _chunk_semantic(self, document: Document) -> list[Chunk]:
        """Chunk document using semantic boundaries.

        This is a simplified version - a full implementation would use
        embeddings to find natural semantic breaks.

        Args:
            document: Document to chunk

        Returns:
            List of semantic chunks
        """
        # For MVP, use paragraph chunking with overlap
        base_chunks = self._chunk_by_paragraph(document)

        # Add overlap context
        enhanced_chunks: list[Chunk] = []
        for i, chunk in enumerate(base_chunks):
            # Add context from previous chunk
            prefix = ""
            if i > 0 and self.overlap > 0:
                prev_text = base_chunks[i - 1].text
                prefix = prev_text[-self.overlap :] + " ... "

            # Add context from next chunk
            suffix = ""
            if i < len(base_chunks) - 1 and self.overlap > 0:
                next_text = base_chunks[i + 1].text
                suffix = " ... " + next_text[: self.overlap]

            enhanced_chunk = Chunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                chunk_type=ChunkType.SEMANTIC,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                page_number=chunk.page_number,
                section_path=chunk.section_path,
                metadata={
                    "context_prefix": prefix,
                    "context_suffix": suffix,
                    "original_text": chunk.text,
                },
            )
            enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks

    def _split_large_text(
        self,
        text: str,
        start_pos: int,
        doc_id: str,
        chunk_index: int,
        section_name: Optional[str] = None,
    ) -> list[Chunk]:
        """Split oversized text into smaller chunks.

        Args:
            text: Text to split
            start_pos: Starting position in original document
            doc_id: Document identifier
            chunk_index: Starting chunk index
            section_name: Optional section name

        Returns:
            List of chunks
        """
        chunks: list[Chunk] = []
        current_pos = 0
        sub_index = 0

        while current_pos < len(text):
            # Find a good break point
            end_pos = min(current_pos + self.max_chunk_size, len(text))

            if end_pos < len(text):
                # Try to break at sentence boundary
                search_start = max(current_pos + self.min_chunk_size, end_pos - 200)
                best_break = end_pos

                for match in self.SENTENCE_ENDINGS.finditer(text[search_start:end_pos]):
                    best_break = search_start + match.end()

                # Try paragraph boundary
                para_break = text.rfind("\n\n", search_start, end_pos)
                if para_break > search_start:
                    best_break = para_break

                end_pos = best_break

            chunk_text = text[current_pos:end_pos].strip()
            if chunk_text:
                chunk = Chunk(
                    chunk_id=f"{doc_id}_p{chunk_index}_{sub_index}",
                    text=chunk_text,
                    chunk_type=self.chunk_type,
                    start_char=start_pos + current_pos,
                    end_char=start_pos + end_pos,
                    section_path=section_name,
                )
                chunks.append(chunk)
                sub_index += 1

            current_pos = end_pos

        return chunks

    def _merge_small_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """Merge chunks that are too small.

        Args:
            chunks: List of chunks

        Returns:
            List with small chunks merged
        """
        if not chunks:
            return chunks

        merged: list[Chunk] = []
        buffer: Optional[Chunk] = None

        for chunk in chunks:
            if buffer is None:
                if chunk.char_count < self.min_chunk_size:
                    buffer = chunk
                else:
                    merged.append(chunk)
            else:
                # Merge with buffer
                combined_text = buffer.text + "\n\n" + chunk.text
                combined = Chunk(
                    chunk_id=buffer.chunk_id,
                    text=combined_text,
                    chunk_type=buffer.chunk_type,
                    start_char=buffer.start_char,
                    end_char=chunk.end_char,
                    page_number=buffer.page_number,
                    section_path=buffer.section_path,
                )

                if combined.char_count >= self.min_chunk_size:
                    merged.append(combined)
                    buffer = None
                else:
                    buffer = combined

        # Add remaining buffer
        if buffer:
            merged.append(buffer)

        return merged

    def _find_page_number(self, document: Document, char_pos: int) -> Optional[int]:
        """Find page number for a character position.

        Args:
            document: Document to search
            char_pos: Character position

        Returns:
            Page number or None
        """
        cumulative = 0
        for page in document.pages:
            page_len = len(page.text) + 2  # Account for page separator
            if cumulative + page_len > char_pos:
                return page.page_number
            cumulative += page_len
        return None

    def _find_section(self, document: Document, char_pos: int) -> Optional[str]:
        """Find section for a character position.

        Args:
            document: Document to search
            char_pos: Character position

        Returns:
            Section path or None
        """
        text = document.full_text
        best_section: Optional[str] = None
        best_pos = -1

        for section_name, section_text in document.sections.items():
            pos = text.find(section_text)
            if pos != -1 and pos <= char_pos and pos > best_pos:
                best_section = section_name
                best_pos = pos

        return best_section


def chunk_document(
    document: Document, chunk_type: ChunkType = ChunkType.PARAGRAPH, **kwargs
) -> list[Chunk]:
    """Convenience function to chunk a document.

    Args:
        document: Document to chunk
        chunk_type: Type of chunking to perform
        **kwargs: Additional arguments passed to DocumentChunker

    Returns:
        List of Chunk objects
    """
    chunker = DocumentChunker(chunk_type=chunk_type, **kwargs)
    return chunker.chunk_document(document)

"""Tests for document chunker."""

import pytest

from policy_diff.core.chunker import (
    DocumentChunker,
    Chunk,
    ChunkType,
    chunk_document,
)
from policy_diff.models.document import Document, DocumentMetadata, PageContent


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    text = """First paragraph with some content.

Second paragraph with different content.

Third paragraph continues here.

SECTION 1: COVERAGE

This section describes coverage details.

SECTION 2: EXCLUSIONS

This section lists exclusions."""

    metadata = DocumentMetadata(filename="test.pdf")
    pages = [PageContent(page_number=1, text=text)]

    return Document(
        metadata=metadata,
        pages=pages,
        full_text=text,
        sections={
            "SECTION 1: COVERAGE": "This section describes coverage details.",
            "SECTION 2: EXCLUSIONS": "This section lists exclusions.",
        },
    )


class TestDocumentChunker:
    """Tests for DocumentChunker class."""

    def test_paragraph_chunking(self, sample_document):
        """Test chunking by paragraphs."""
        chunker = DocumentChunker(chunk_type=ChunkType.PARAGRAPH, min_chunk_size=10)
        chunks = chunker.chunk_document(sample_document)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.chunk_type == ChunkType.PARAGRAPH
            assert chunk.text.strip()

    def test_section_chunking(self, sample_document):
        """Test chunking by sections."""
        chunker = DocumentChunker(chunk_type=ChunkType.SECTION)
        chunks = chunker.chunk_document(sample_document)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.chunk_type == ChunkType.SECTION

    def test_chunk_has_location_info(self, sample_document):
        """Test that chunks have location information."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(sample_document)

        for chunk in chunks:
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char

    def test_max_chunk_size_respected(self, sample_document):
        """Test that max chunk size is respected."""
        max_size = 100
        chunker = DocumentChunker(max_chunk_size=max_size)
        chunks = chunker.chunk_document(sample_document)

        for chunk in chunks:
            # Allow some overflow for clean breaks
            assert chunk.char_count <= max_size * 1.5

    def test_chunk_ids_unique(self, sample_document):
        """Test that chunk IDs are unique."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(sample_document)

        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_to_dict(self, sample_document):
        """Test chunk serialization."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(sample_document)

        for chunk in chunks:
            d = chunk.to_dict()
            assert "chunk_id" in d
            assert "text" in d
            assert "chunk_type" in d
            assert "start_char" in d
            assert "end_char" in d


class TestChunkConvenienceFunction:
    """Tests for chunk_document convenience function."""

    def test_chunk_document_function(self, sample_document):
        """Test the convenience function."""
        chunks = chunk_document(sample_document, chunk_type=ChunkType.PARAGRAPH, min_chunk_size=10)

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)

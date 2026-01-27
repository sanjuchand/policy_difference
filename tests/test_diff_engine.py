"""Tests for diff engine."""

import pytest

from policy_diff.core.diff_engine import (
    TextDiffEngine,
    DiffConfig,
    ChunkMatch,
    diff_chunks,
)
from policy_diff.core.chunker import Chunk, ChunkType
from policy_diff.models.diff_result import ChangeType


@pytest.fixture
def create_chunk():
    """Factory for creating test chunks."""
    def _create(text, chunk_id="test", start=0):
        return Chunk(
            chunk_id=chunk_id,
            text=text,
            chunk_type=ChunkType.PARAGRAPH,
            start_char=start,
            end_char=start + len(text),
        )
    return _create


class TestTextDiffEngine:
    """Tests for TextDiffEngine class."""

    def test_exact_match_detection(self, create_chunk):
        """Test detection of exact matches."""
        chunks_a = [create_chunk("This is the same text.", "a1")]
        chunks_b = [create_chunk("This is the same text.", "b1")]

        engine = TextDiffEngine()
        report = engine.diff_documents(chunks_a, chunks_b)

        # Exact matches should not appear in changes
        assert report.summary.total_changes == 0

    def test_addition_detection(self, create_chunk):
        """Test detection of added content."""
        chunks_a = [create_chunk("Original text.", "a1")]
        chunks_b = [
            create_chunk("Original text.", "b1"),
            create_chunk("New text added.", "b2"),
        ]

        engine = TextDiffEngine()
        report = engine.diff_documents(chunks_a, chunks_b)

        added = [c for c in report.changes if c.change_type == ChangeType.ADDED]
        assert len(added) == 1
        assert "New text added" in added[0].text_after

    def test_removal_detection(self, create_chunk):
        """Test detection of removed content."""
        chunks_a = [
            create_chunk("Text to keep.", "a1"),
            create_chunk("Text to remove.", "a2"),
        ]
        chunks_b = [create_chunk("Text to keep.", "b1")]

        engine = TextDiffEngine()
        report = engine.diff_documents(chunks_a, chunks_b)

        removed = [c for c in report.changes if c.change_type == ChangeType.REMOVED]
        assert len(removed) == 1
        assert "Text to remove" in removed[0].text_before

    def test_modification_detection(self, create_chunk):
        """Test detection of modified content."""
        chunks_a = [create_chunk("The deductible is $500.", "a1")]
        chunks_b = [create_chunk("The deductible is $1000.", "b1")]

        engine = TextDiffEngine()
        report = engine.diff_documents(chunks_a, chunks_b)

        modified = [c for c in report.changes if c.change_type == ChangeType.MODIFIED]
        assert len(modified) == 1
        assert "$500" in modified[0].text_before
        assert "$1000" in modified[0].text_after

    def test_similarity_threshold(self, create_chunk):
        """Test similarity threshold affects matching."""
        chunks_a = [create_chunk("The quick brown fox.", "a1")]
        chunks_b = [create_chunk("The slow brown fox.", "b1")]

        # With low threshold, should match
        config_low = DiffConfig(similarity_threshold=0.3)
        engine_low = TextDiffEngine(config_low)
        report_low = engine_low.diff_documents(chunks_a, chunks_b)

        # Should be a modification, not separate add/remove
        modified = [c for c in report_low.changes if c.change_type == ChangeType.MODIFIED]
        assert len(modified) == 1

    def test_report_has_document_names(self, create_chunk):
        """Test that report contains document names."""
        chunks_a = [create_chunk("Test", "a1")]
        chunks_b = [create_chunk("Test", "b1")]

        engine = TextDiffEngine()
        report = engine.diff_documents(
            chunks_a, chunks_b,
            doc_a_name="Policy_v1.pdf",
            doc_b_name="Policy_v2.pdf"
        )

        assert report.document_a_name == "Policy_v1.pdf"
        assert report.document_b_name == "Policy_v2.pdf"


class TestDiffConfig:
    """Tests for DiffConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DiffConfig()

        assert config.similarity_threshold == 0.6
        assert config.exact_match_threshold == 0.99
        assert config.normalize_before_compare is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = DiffConfig(
            similarity_threshold=0.8,
            normalize_before_compare=False,
        )

        assert config.similarity_threshold == 0.8
        assert config.normalize_before_compare is False


class TestConvenienceFunction:
    """Tests for diff_chunks convenience function."""

    def test_diff_chunks_function(self, create_chunk):
        """Test the convenience function."""
        chunks_a = [create_chunk("Hello world", "a1")]
        chunks_b = [create_chunk("Hello there", "b1")]

        report = diff_chunks(chunks_a, chunks_b)

        assert report.report_id
        assert report.summary is not None

"""Tests for data models."""

import pytest
from datetime import datetime

from policy_diff.models.document import (
    Document,
    DocumentMetadata,
    PageContent,
    DocumentType,
)
from policy_diff.models.diff_result import (
    DiffReport,
    DiffSummary,
    ChangeItem,
    ChangeType,
    Significance,
    ChangeCategory,
    SemanticAnalysis,
    TextLocation,
)


class TestDocumentModels:
    """Tests for document models."""

    def test_document_metadata_creation(self):
        """Test DocumentMetadata creation."""
        metadata = DocumentMetadata(
            filename="test.pdf",
            page_count=10,
            word_count=1000,
        )

        assert metadata.filename == "test.pdf"
        assert metadata.page_count == 10
        assert metadata.word_count == 1000
        assert metadata.document_type == DocumentType.UNKNOWN

    def test_page_content_creation(self):
        """Test PageContent creation."""
        page = PageContent(
            page_number=1,
            text="Test content",
        )

        assert page.page_number == 1
        assert page.text == "Test content"
        assert page.word_count == 2

    def test_document_word_count(self):
        """Test document word count calculation."""
        metadata = DocumentMetadata(filename="test.pdf")
        doc = Document(
            metadata=metadata,
            full_text="One two three four five",
        )

        assert doc.metadata.word_count == 5

    def test_document_to_dict(self):
        """Test document serialization."""
        metadata = DocumentMetadata(filename="test.pdf", page_count=5)
        doc = Document(metadata=metadata, full_text="Test")

        d = doc.to_dict()
        assert "metadata" in d
        assert "full_text" in d
        assert d["metadata"]["filename"] == "test.pdf"


class TestDiffResultModels:
    """Tests for diff result models."""

    def test_change_item_creation(self):
        """Test ChangeItem creation."""
        change = ChangeItem(
            change_id="test123",
            change_type=ChangeType.MODIFIED,
            text_before="Old text",
            text_after="New text",
            similarity_score=0.8,
        )

        assert change.change_id == "test123"
        assert change.change_type == ChangeType.MODIFIED
        assert change.similarity_score == 0.8

    def test_change_item_significance_property(self):
        """Test significance property with semantic analysis."""
        analysis = SemanticAnalysis(
            significance=Significance.HIGH,
            confidence=0.9,
            categories=[ChangeCategory.COVERAGE],
            explanation="Coverage change",
            business_impact="Affects coverage",
        )

        change = ChangeItem(
            change_id="test",
            change_type=ChangeType.MODIFIED,
            text_before="Before",
            text_after="After",
            semantic_analysis=analysis,
        )

        assert change.significance == Significance.HIGH
        assert change.confidence == 0.9

    def test_change_item_to_dict(self):
        """Test ChangeItem serialization."""
        change = ChangeItem(
            change_id="test",
            change_type=ChangeType.ADDED,
            text_before="",
            text_after="New content",
        )

        d = change.to_dict()
        assert d["change_id"] == "test"
        assert d["change_type"] == "added"
        assert d["text_after"] == "New content"

    def test_diff_summary(self):
        """Test DiffSummary creation."""
        summary = DiffSummary(
            total_changes=10,
            critical_changes=2,
            high_changes=3,
        )

        assert summary.total_changes == 10
        assert summary.critical_changes == 2

    def test_diff_report_creation(self):
        """Test DiffReport creation."""
        report = DiffReport(
            report_id="report123",
            document_a_name="doc_a.pdf",
            document_b_name="doc_b.pdf",
        )

        assert report.report_id == "report123"
        assert report.document_a_name == "doc_a.pdf"
        assert isinstance(report.created_at, datetime)

    def test_diff_report_summary_computation(self):
        """Test that summary is computed from changes."""
        changes = [
            ChangeItem(
                change_id="1",
                change_type=ChangeType.MODIFIED,
                text_before="A",
                text_after="B",
                semantic_analysis=SemanticAnalysis(
                    significance=Significance.CRITICAL,
                    confidence=0.9,
                    categories=[ChangeCategory.COVERAGE],
                    explanation="Critical change",
                    business_impact="High impact",
                ),
            ),
            ChangeItem(
                change_id="2",
                change_type=ChangeType.ADDED,
                text_before="",
                text_after="C",
                semantic_analysis=SemanticAnalysis(
                    significance=Significance.LOW,
                    confidence=0.8,
                    categories=[ChangeCategory.FORMATTING],
                    explanation="Minor change",
                    business_impact="Low impact",
                ),
            ),
        ]

        report = DiffReport(
            report_id="test",
            document_a_name="a.pdf",
            document_b_name="b.pdf",
            changes=changes,
        )

        assert report.summary.total_changes == 2
        assert report.summary.critical_changes == 1
        assert report.summary.low_changes == 1

    def test_diff_report_get_critical_and_high(self):
        """Test filtering critical and high changes."""
        changes = [
            ChangeItem(
                change_id="1",
                change_type=ChangeType.MODIFIED,
                text_before="A",
                text_after="B",
                semantic_analysis=SemanticAnalysis(
                    significance=Significance.CRITICAL,
                    confidence=0.9,
                    categories=[],
                    explanation="",
                    business_impact="",
                ),
            ),
            ChangeItem(
                change_id="2",
                change_type=ChangeType.MODIFIED,
                text_before="C",
                text_after="D",
                semantic_analysis=SemanticAnalysis(
                    significance=Significance.LOW,
                    confidence=0.9,
                    categories=[],
                    explanation="",
                    business_impact="",
                ),
            ),
        ]

        report = DiffReport(
            report_id="test",
            document_a_name="a.pdf",
            document_b_name="b.pdf",
            changes=changes,
        )

        critical_high = report.get_critical_and_high()
        assert len(critical_high) == 1
        assert critical_high[0].change_id == "1"

    def test_diff_report_to_dict(self):
        """Test DiffReport serialization."""
        report = DiffReport(
            report_id="test",
            document_a_name="a.pdf",
            document_b_name="b.pdf",
        )

        d = report.to_dict()
        assert "report_id" in d
        assert "document_a_name" in d
        assert "changes" in d
        assert "summary" in d
        assert "created_at" in d


class TestTextLocation:
    """Tests for TextLocation model."""

    def test_text_location_creation(self):
        """Test TextLocation creation."""
        location = TextLocation(
            start_char=0,
            end_char=100,
            page_number=1,
            section_path="SECTION 1",
        )

        assert location.start_char == 0
        assert location.end_char == 100
        assert location.page_number == 1

    def test_text_location_to_dict(self):
        """Test TextLocation serialization."""
        location = TextLocation(start_char=10, end_char=50)

        d = location.to_dict()
        assert d["start_char"] == 10
        assert d["end_char"] == 50
        assert d["page_number"] is None

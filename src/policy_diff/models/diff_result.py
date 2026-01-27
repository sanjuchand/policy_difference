"""Diff result data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Significance(str, Enum):
    """Significance level of a change."""
    CRITICAL = "critical"  # Material change affecting rights/obligations
    HIGH = "high"          # Significant change requiring review
    MEDIUM = "medium"      # Notable change, may need attention
    LOW = "low"            # Minor change, likely cosmetic
    NONE = "none"          # No semantic change (formatting only)


class ChangeCategory(str, Enum):
    """Category of change detected."""
    COVERAGE = "coverage"           # Coverage scope changes
    EXCLUSION = "exclusion"         # Exclusion additions/removals
    LIMIT = "limit"                 # Numerical limits (amounts, time periods)
    DEFINITION = "definition"       # Definition changes
    OBLIGATION = "obligation"       # Obligation/requirement changes
    PERMISSION = "permission"       # Permission/right changes
    CONDITION = "condition"         # Condition/prerequisite changes
    FORMATTING = "formatting"       # Formatting/style only
    RESTRUCTURE = "restructure"     # Content reorganization
    OTHER = "other"                 # Other changes


class ChangeType(str, Enum):
    """Type of text change."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"
    UNCHANGED = "unchanged"


@dataclass
class TextLocation:
    """Location of text within a document."""
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    section_path: Optional[str] = None
    line_number: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "start_char": self.start_char,
            "end_char": self.end_char,
            "page_number": self.page_number,
            "section_path": self.section_path,
            "line_number": self.line_number,
        }


@dataclass
class SemanticAnalysis:
    """LLM-generated semantic analysis of a change."""
    significance: Significance
    confidence: float
    categories: list[ChangeCategory]
    explanation: str
    business_impact: str
    requires_review: bool = False
    regulatory_impact: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "significance": self.significance.value,
            "confidence": self.confidence,
            "categories": [c.value for c in self.categories],
            "explanation": self.explanation,
            "business_impact": self.business_impact,
            "requires_review": self.requires_review,
            "regulatory_impact": self.regulatory_impact,
        }


@dataclass
class ChangeItem:
    """A single detected change between documents."""
    change_id: str
    change_type: ChangeType
    text_before: str
    text_after: str
    location_before: Optional[TextLocation] = None
    location_after: Optional[TextLocation] = None
    similarity_score: float = 0.0
    semantic_analysis: Optional[SemanticAnalysis] = None
    is_pii_affected: bool = False
    rule_based_flags: list[str] = field(default_factory=list)

    @property
    def significance(self) -> Significance:
        """Get significance from semantic analysis or default."""
        if self.semantic_analysis:
            return self.semantic_analysis.significance
        return Significance.NONE

    @property
    def confidence(self) -> float:
        """Get confidence from semantic analysis or similarity."""
        if self.semantic_analysis:
            return self.semantic_analysis.confidence
        return self.similarity_score

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "text_before": self.text_before,
            "text_after": self.text_after,
            "location_before": self.location_before.to_dict() if self.location_before else None,
            "location_after": self.location_after.to_dict() if self.location_after else None,
            "similarity_score": self.similarity_score,
            "semantic_analysis": self.semantic_analysis.to_dict() if self.semantic_analysis else None,
            "is_pii_affected": self.is_pii_affected,
            "rule_based_flags": self.rule_based_flags,
            "significance": self.significance.value,
            "confidence": self.confidence,
        }


@dataclass
class DiffSummary:
    """Summary statistics of a diff operation."""
    total_changes: int = 0
    critical_changes: int = 0
    high_changes: int = 0
    medium_changes: int = 0
    low_changes: int = 0
    formatting_only: int = 0
    pii_affected_changes: int = 0
    changes_by_category: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_changes": self.total_changes,
            "critical_changes": self.critical_changes,
            "high_changes": self.high_changes,
            "medium_changes": self.medium_changes,
            "low_changes": self.low_changes,
            "formatting_only": self.formatting_only,
            "pii_affected_changes": self.pii_affected_changes,
            "changes_by_category": self.changes_by_category,
        }


@dataclass
class DiffReport:
    """Complete diff report between two documents."""
    report_id: str
    document_a_name: str
    document_b_name: str
    created_at: datetime = field(default_factory=datetime.now)
    changes: list[ChangeItem] = field(default_factory=list)
    summary: DiffSummary = field(default_factory=DiffSummary)
    processing_time_seconds: float = 0.0
    llm_calls_made: int = 0
    embeddings_computed: int = 0

    def __post_init__(self) -> None:
        """Compute summary after initialization."""
        self._compute_summary()

    def _compute_summary(self) -> None:
        """Compute summary statistics from changes."""
        self.summary.total_changes = len(self.changes)

        category_counts: dict[str, int] = {}

        for change in self.changes:
            sig = change.significance

            if sig == Significance.CRITICAL:
                self.summary.critical_changes += 1
            elif sig == Significance.HIGH:
                self.summary.high_changes += 1
            elif sig == Significance.MEDIUM:
                self.summary.medium_changes += 1
            elif sig == Significance.LOW:
                self.summary.low_changes += 1
            elif sig == Significance.NONE:
                self.summary.formatting_only += 1

            if change.is_pii_affected:
                self.summary.pii_affected_changes += 1

            if change.semantic_analysis:
                for cat in change.semantic_analysis.categories:
                    category_counts[cat.value] = category_counts.get(cat.value, 0) + 1

        self.summary.changes_by_category = category_counts

    def add_change(self, change: ChangeItem) -> None:
        """Add a change and update summary."""
        self.changes.append(change)
        self._compute_summary()

    def get_changes_by_significance(self, significance: Significance) -> list[ChangeItem]:
        """Get all changes with a specific significance level."""
        return [c for c in self.changes if c.significance == significance]

    def get_critical_and_high(self) -> list[ChangeItem]:
        """Get all critical and high significance changes."""
        return [
            c for c in self.changes
            if c.significance in (Significance.CRITICAL, Significance.HIGH)
        ]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "report_id": self.report_id,
            "document_a_name": self.document_a_name,
            "document_b_name": self.document_b_name,
            "created_at": self.created_at.isoformat(),
            "changes": [c.to_dict() for c in self.changes],
            "summary": self.summary.to_dict(),
            "processing_time_seconds": self.processing_time_seconds,
            "llm_calls_made": self.llm_calls_made,
            "embeddings_computed": self.embeddings_computed,
        }

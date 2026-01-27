"""
Policy Diff - AI-powered semantic diff for policy documents.

This package provides tools for comparing policy documents using:
- PDF text extraction
- PII detection and tokenization
- Embedding-based change detection
- LLM-powered semantic analysis
- RAG-enhanced context retrieval
"""

__version__ = "0.1.0"
__author__ = "Policy Diff Team"

from policy_diff.core import (
    parse_pdf,
    PDFParser,
    chunk_document,
    DocumentChunker,
    Chunk,
    ChunkType,
    TextDiffEngine,
    DiffConfig,
    diff_chunks,
)
from policy_diff.models import (
    Document,
    DocumentMetadata,
    DiffReport,
    ChangeItem,
    Significance,
    ChangeCategory,
)
from policy_diff.pii import (
    PIIDetector,
    PIITokenizer,
    detect_pii,
    tokenize_pii,
)
from policy_diff.ai import (
    EmbeddingEngine,
    LLMClient,
    SemanticAnalyzer,
)
from policy_diff.output import (
    HTMLReportGenerator,
    JSONExporter,
    generate_html_report,
    export_to_json,
)

__all__ = [
    # Core
    "parse_pdf",
    "PDFParser",
    "chunk_document",
    "DocumentChunker",
    "Chunk",
    "ChunkType",
    "TextDiffEngine",
    "DiffConfig",
    "diff_chunks",
    # Models
    "Document",
    "DocumentMetadata",
    "DiffReport",
    "ChangeItem",
    "Significance",
    "ChangeCategory",
    # PII
    "PIIDetector",
    "PIITokenizer",
    "detect_pii",
    "tokenize_pii",
    # AI
    "EmbeddingEngine",
    "LLMClient",
    "SemanticAnalyzer",
    # Output
    "HTMLReportGenerator",
    "JSONExporter",
    "generate_html_report",
    "export_to_json",
]

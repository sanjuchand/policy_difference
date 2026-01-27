"""Core document processing modules."""

from policy_diff.core.pdf_parser import PDFParser, parse_pdf, PDFParseError
from policy_diff.core.chunker import DocumentChunker, Chunk, ChunkType, chunk_document
from policy_diff.core.normalizer import (
    TextNormalizer,
    PolicyTextNormalizer,
    NormalizationLevel,
    normalize_text,
    normalize_for_comparison,
)
from policy_diff.core.diff_engine import (
    TextDiffEngine,
    SemanticDiffEngine,
    DiffConfig,
    ChunkMatch,
    diff_chunks,
)

__all__ = [
    "PDFParser",
    "parse_pdf",
    "PDFParseError",
    "DocumentChunker",
    "Chunk",
    "ChunkType",
    "chunk_document",
    "TextNormalizer",
    "PolicyTextNormalizer",
    "NormalizationLevel",
    "normalize_text",
    "normalize_for_comparison",
    "TextDiffEngine",
    "SemanticDiffEngine",
    "DiffConfig",
    "ChunkMatch",
    "diff_chunks",
]

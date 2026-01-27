"""Text diff engine for comparing document chunks."""

import difflib
import uuid
from dataclasses import dataclass, field
from typing import Optional

from policy_diff.core.chunker import Chunk
from policy_diff.core.normalizer import TextNormalizer, NormalizationLevel
from policy_diff.models.diff_result import (
    ChangeItem,
    ChangeType,
    TextLocation,
    DiffReport,
)


@dataclass
class ChunkMatch:
    """A match between chunks from two documents."""

    chunk_a: Optional[Chunk]
    chunk_b: Optional[Chunk]
    similarity: float
    change_type: ChangeType
    text_diff: Optional[str] = None

    @property
    def is_exact_match(self) -> bool:
        """Check if this is an exact match."""
        return self.similarity >= 0.999

    @property
    def is_near_match(self) -> bool:
        """Check if this is a near match (similar but not exact)."""
        return 0.5 <= self.similarity < 0.999


@dataclass
class DiffConfig:
    """Configuration for diff engine."""

    similarity_threshold: float = 0.6  # Min similarity to consider a match
    exact_match_threshold: float = 0.99  # Similarity for exact match
    normalize_before_compare: bool = True
    normalization_level: NormalizationLevel = NormalizationLevel.STANDARD
    generate_text_diff: bool = True
    use_semantic_matching: bool = False  # Requires embeddings


class TextDiffEngine:
    """Engine for computing differences between document chunks."""

    def __init__(self, config: Optional[DiffConfig] = None):
        """Initialize diff engine.

        Args:
            config: Diff configuration
        """
        self.config = config or DiffConfig()
        self.normalizer = TextNormalizer(level=self.config.normalization_level)

    def diff_documents(
        self,
        chunks_a: list[Chunk],
        chunks_b: list[Chunk],
        doc_a_name: str = "Document A",
        doc_b_name: str = "Document B",
    ) -> DiffReport:
        """Compare two documents and generate a diff report.

        Args:
            chunks_a: Chunks from first document
            chunks_b: Chunks from second document
            doc_a_name: Name of first document
            doc_b_name: Name of second document

        Returns:
            DiffReport with detected changes
        """
        # Find matches between chunks
        matches = self._find_matches(chunks_a, chunks_b)

        # Convert matches to change items
        changes = self._matches_to_changes(matches)

        # Create report
        report = DiffReport(
            report_id=str(uuid.uuid4()),
            document_a_name=doc_a_name,
            document_b_name=doc_b_name,
            changes=changes,
        )

        return report

    def _find_matches(
        self, chunks_a: list[Chunk], chunks_b: list[Chunk]
    ) -> list[ChunkMatch]:
        """Find matching chunks between two documents.

        Args:
            chunks_a: Chunks from first document
            chunks_b: Chunks from second document

        Returns:
            List of chunk matches
        """
        matches: list[ChunkMatch] = []
        used_b_indices: set[int] = set()

        # Normalize texts if configured
        texts_a = [self._get_comparable_text(c) for c in chunks_a]
        texts_b = [self._get_comparable_text(c) for c in chunks_b]

        # Find best match for each chunk in A
        for i, chunk_a in enumerate(chunks_a):
            best_match_idx: Optional[int] = None
            best_similarity = 0.0

            for j, chunk_b in enumerate(chunks_b):
                if j in used_b_indices:
                    continue

                similarity = self._compute_similarity(texts_a[i], texts_b[j])

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = j

            # Determine match type
            if (
                best_match_idx is not None
                and best_similarity >= self.config.similarity_threshold
            ):
                used_b_indices.add(best_match_idx)
                chunk_b = chunks_b[best_match_idx]

                if best_similarity >= self.config.exact_match_threshold:
                    change_type = ChangeType.UNCHANGED
                else:
                    change_type = ChangeType.MODIFIED

                text_diff = None
                if self.config.generate_text_diff and change_type == ChangeType.MODIFIED:
                    text_diff = self._generate_text_diff(chunk_a.text, chunk_b.text)

                matches.append(
                    ChunkMatch(
                        chunk_a=chunk_a,
                        chunk_b=chunk_b,
                        similarity=best_similarity,
                        change_type=change_type,
                        text_diff=text_diff,
                    )
                )
            else:
                # No match found - chunk was removed
                matches.append(
                    ChunkMatch(
                        chunk_a=chunk_a,
                        chunk_b=None,
                        similarity=0.0,
                        change_type=ChangeType.REMOVED,
                    )
                )

        # Find chunks in B that weren't matched (additions)
        for j, chunk_b in enumerate(chunks_b):
            if j not in used_b_indices:
                matches.append(
                    ChunkMatch(
                        chunk_a=None,
                        chunk_b=chunk_b,
                        similarity=0.0,
                        change_type=ChangeType.ADDED,
                    )
                )

        return matches

    def _get_comparable_text(self, chunk: Chunk) -> str:
        """Get normalized text for comparison.

        Args:
            chunk: Chunk to get text from

        Returns:
            Text for comparison
        """
        if self.config.normalize_before_compare:
            return self.normalizer.normalize(chunk.text).normalized
        return chunk.text

    def _compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute similarity between two texts.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Similarity score between 0 and 1
        """
        if not text_a and not text_b:
            return 1.0
        if not text_a or not text_b:
            return 0.0

        # Use SequenceMatcher for basic similarity
        matcher = difflib.SequenceMatcher(None, text_a, text_b)
        return matcher.ratio()

    def _generate_text_diff(self, text_a: str, text_b: str) -> str:
        """Generate a human-readable diff between texts.

        Args:
            text_a: Original text
            text_b: Modified text

        Returns:
            Unified diff string
        """
        lines_a = text_a.splitlines(keepends=True)
        lines_b = text_b.splitlines(keepends=True)

        diff = difflib.unified_diff(lines_a, lines_b, lineterm="")
        return "".join(diff)

    def _matches_to_changes(self, matches: list[ChunkMatch]) -> list[ChangeItem]:
        """Convert chunk matches to change items.

        Args:
            matches: List of chunk matches

        Returns:
            List of change items
        """
        changes: list[ChangeItem] = []

        for match in matches:
            # Skip unchanged chunks
            if match.change_type == ChangeType.UNCHANGED:
                continue

            change_id = str(uuid.uuid4())[:8]

            location_before = None
            location_after = None
            text_before = ""
            text_after = ""

            if match.chunk_a:
                text_before = match.chunk_a.text
                location_before = TextLocation(
                    start_char=match.chunk_a.start_char,
                    end_char=match.chunk_a.end_char,
                    page_number=match.chunk_a.page_number,
                    section_path=match.chunk_a.section_path,
                )

            if match.chunk_b:
                text_after = match.chunk_b.text
                location_after = TextLocation(
                    start_char=match.chunk_b.start_char,
                    end_char=match.chunk_b.end_char,
                    page_number=match.chunk_b.page_number,
                    section_path=match.chunk_b.section_path,
                )

            change = ChangeItem(
                change_id=change_id,
                change_type=match.change_type,
                text_before=text_before,
                text_after=text_after,
                location_before=location_before,
                location_after=location_after,
                similarity_score=match.similarity,
            )

            changes.append(change)

        return changes


class SemanticDiffEngine(TextDiffEngine):
    """Diff engine with semantic similarity using embeddings."""

    def __init__(
        self,
        config: Optional[DiffConfig] = None,
        embedding_engine=None,
    ):
        """Initialize semantic diff engine.

        Args:
            config: Diff configuration
            embedding_engine: Embedding engine for semantic similarity
        """
        if config is None:
            config = DiffConfig(use_semantic_matching=True)
        super().__init__(config)
        self.embedding_engine = embedding_engine
        self._embeddings_cache: dict[str, list[float]] = {}

    def _compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute semantic similarity using embeddings.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Semantic similarity score
        """
        if self.embedding_engine is None:
            # Fall back to text similarity
            return super()._compute_similarity(text_a, text_b)

        # Get or compute embeddings
        emb_a = self._get_embedding(text_a)
        emb_b = self._get_embedding(text_b)

        if emb_a is None or emb_b is None:
            return super()._compute_similarity(text_a, text_b)

        # Compute cosine similarity
        return self._cosine_similarity(emb_a, emb_b)

    def _get_embedding(self, text: str) -> Optional[list[float]]:
        """Get embedding for text, using cache.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None
        """
        if text in self._embeddings_cache:
            return self._embeddings_cache[text]

        if self.embedding_engine is None:
            return None

        try:
            embedding = self.embedding_engine.embed(text)
            self._embeddings_cache[text] = embedding
            return embedding
        except Exception:
            return None

    def _cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between vectors.

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Cosine similarity
        """
        if len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


def diff_chunks(
    chunks_a: list[Chunk],
    chunks_b: list[Chunk],
    config: Optional[DiffConfig] = None,
    **kwargs,
) -> DiffReport:
    """Convenience function to diff two sets of chunks.

    Args:
        chunks_a: Chunks from first document
        chunks_b: Chunks from second document
        config: Diff configuration
        **kwargs: Additional arguments (doc_a_name, doc_b_name)

    Returns:
        DiffReport with detected changes
    """
    engine = TextDiffEngine(config)
    return engine.diff_documents(chunks_a, chunks_b, **kwargs)

"""Embedding engine for semantic text comparison."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class EmbeddingModel(str, Enum):
    """Available embedding models."""

    # sentence-transformers models
    MINILM = "all-MiniLM-L6-v2"  # Fast, good for general text
    MPNET = "all-mpnet-base-v2"  # Higher quality, slower
    LEGAL_BERT = "nlpaueb/legal-bert-base-uncased"  # Legal domain
    BGE_SMALL = "BAAI/bge-small-en-v1.5"  # Good balance
    BGE_BASE = "BAAI/bge-base-en-v1.5"  # Better quality


@dataclass
class SimilarityResult:
    """Result of similarity comparison."""

    text_a: str
    text_b: str
    similarity: float
    embedding_a: Optional[list[float]] = None
    embedding_b: Optional[list[float]] = None

    @property
    def is_similar(self) -> bool:
        """Check if texts are semantically similar (>0.7)."""
        return self.similarity > 0.7

    @property
    def is_near_duplicate(self) -> bool:
        """Check if texts are near duplicates (>0.9)."""
        return self.similarity > 0.9


class EmbeddingEngine:
    """Generates embeddings for semantic text comparison."""

    def __init__(
        self,
        model_name: str | EmbeddingModel = EmbeddingModel.MINILM,
        device: str = "cpu",
        cache_embeddings: bool = True,
        batch_size: int = 32,
    ):
        """Initialize embedding engine.

        Args:
            model_name: Name of the embedding model
            device: Device to run model on (cpu, cuda, mps)
            cache_embeddings: Whether to cache embeddings
            batch_size: Batch size for embedding computation
        """
        if isinstance(model_name, EmbeddingModel):
            model_name = model_name.value

        self.model_name = model_name
        self.device = device
        self.cache_embeddings = cache_embeddings
        self.batch_size = batch_size

        self._model: Optional[SentenceTransformer] = None
        self._cache: dict[str, np.ndarray] = {}

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_model()

    def _load_model(self) -> None:
        """Load the embedding model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return

        try:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}") from e

    @property
    def is_available(self) -> bool:
        """Check if embedding engine is available."""
        return self._model is not None

    @property
    def embedding_dimension(self) -> int:
        """Get dimension of embeddings."""
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return 0

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        if not self.is_available:
            raise RuntimeError("Embedding model not available")

        # Check cache
        if self.cache_embeddings and text in self._cache:
            return self._cache[text]

        embedding = self._model.encode(text, convert_to_numpy=True)

        if self.cache_embeddings:
            self._cache[text] = embedding

        return embedding

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Array of embeddings (num_texts x embedding_dim)
        """
        if not self.is_available:
            raise RuntimeError("Embedding model not available")

        # Find texts not in cache
        to_compute = []
        to_compute_indices = []
        cached_embeddings = {}

        for i, text in enumerate(texts):
            if self.cache_embeddings and text in self._cache:
                cached_embeddings[i] = self._cache[text]
            else:
                to_compute.append(text)
                to_compute_indices.append(i)

        # Compute new embeddings
        if to_compute:
            new_embeddings = self._model.encode(
                to_compute,
                convert_to_numpy=True,
                batch_size=self.batch_size,
                show_progress_bar=False,
            )

            # Cache new embeddings
            if self.cache_embeddings:
                for text, embedding in zip(to_compute, new_embeddings):
                    self._cache[text] = embedding

        # Combine cached and new embeddings
        result = np.zeros((len(texts), self.embedding_dimension))
        for i, embedding in cached_embeddings.items():
            result[i] = embedding
        for idx, i in enumerate(to_compute_indices):
            result[i] = new_embeddings[idx]

        return result

    def similarity(self, text_a: str, text_b: str) -> SimilarityResult:
        """Compute semantic similarity between two texts.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            SimilarityResult with score and embeddings
        """
        if not self.is_available:
            # Fall back to basic similarity
            return self._fallback_similarity(text_a, text_b)

        emb_a = self.embed(text_a)
        emb_b = self.embed(text_b)

        sim = self._cosine_similarity(emb_a, emb_b)

        return SimilarityResult(
            text_a=text_a,
            text_b=text_b,
            similarity=float(sim),
            embedding_a=emb_a.tolist(),
            embedding_b=emb_b.tolist(),
        )

    def similarity_matrix(self, texts_a: list[str], texts_b: list[str]) -> np.ndarray:
        """Compute similarity matrix between two sets of texts.

        Args:
            texts_a: First set of texts
            texts_b: Second set of texts

        Returns:
            Similarity matrix (len(texts_a) x len(texts_b))
        """
        if not self.is_available:
            # Fall back to basic similarity
            matrix = np.zeros((len(texts_a), len(texts_b)))
            for i, a in enumerate(texts_a):
                for j, b in enumerate(texts_b):
                    matrix[i, j] = self._fallback_similarity(a, b).similarity
            return matrix

        emb_a = self.embed_batch(texts_a)
        emb_b = self.embed_batch(texts_b)

        # Normalize embeddings
        emb_a_norm = emb_a / np.linalg.norm(emb_a, axis=1, keepdims=True)
        emb_b_norm = emb_b / np.linalg.norm(emb_b, axis=1, keepdims=True)

        # Compute cosine similarity matrix
        return np.dot(emb_a_norm, emb_b_norm.T)

    def find_best_matches(
        self,
        query_texts: list[str],
        candidate_texts: list[str],
        top_k: int = 1,
        threshold: float = 0.0,
    ) -> list[list[tuple[int, float]]]:
        """Find best matching candidates for each query.

        Args:
            query_texts: Query texts
            candidate_texts: Candidate texts to match against
            top_k: Number of top matches to return
            threshold: Minimum similarity threshold

        Returns:
            List of lists of (candidate_index, similarity) tuples
        """
        sim_matrix = self.similarity_matrix(query_texts, candidate_texts)

        results = []
        for i in range(len(query_texts)):
            similarities = sim_matrix[i]
            # Get indices sorted by similarity (descending)
            sorted_indices = np.argsort(similarities)[::-1]

            matches = []
            for idx in sorted_indices[:top_k]:
                sim = similarities[idx]
                if sim >= threshold:
                    matches.append((int(idx), float(sim)))

            results.append(matches)

        return results

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    def _fallback_similarity(self, text_a: str, text_b: str) -> SimilarityResult:
        """Compute basic similarity when embeddings unavailable.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            SimilarityResult using character-based similarity
        """
        # Simple Jaccard similarity on words
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a and not words_b:
            similarity = 1.0
        elif not words_a or not words_b:
            similarity = 0.0
        else:
            intersection = len(words_a & words_b)
            union = len(words_a | words_b)
            similarity = intersection / union

        return SimilarityResult(
            text_a=text_a,
            text_b=text_b,
            similarity=similarity,
        )

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._cache.clear()


def compute_similarity(
    text_a: str,
    text_b: str,
    model_name: str | EmbeddingModel = EmbeddingModel.MINILM,
) -> float:
    """Convenience function to compute semantic similarity.

    Args:
        text_a: First text
        text_b: Second text
        model_name: Embedding model to use

    Returns:
        Similarity score between 0 and 1
    """
    engine = EmbeddingEngine(model_name=model_name)
    return engine.similarity(text_a, text_b).similarity

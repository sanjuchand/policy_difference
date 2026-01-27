"""AI-powered analysis modules."""

from policy_diff.ai.embeddings import (
    EmbeddingEngine,
    EmbeddingModel,
    SimilarityResult,
    compute_similarity,
)
from policy_diff.ai.llm_client import (
    LLMClient,
    LLMConfig,
    LLMProvider,
    OllamaModel,
    SemanticAnalyzer,
)
from policy_diff.ai.prompts import PromptTemplates, PromptTemplate

__all__ = [
    "EmbeddingEngine",
    "EmbeddingModel",
    "SimilarityResult",
    "compute_similarity",
    "LLMClient",
    "LLMConfig",
    "LLMProvider",
    "OllamaModel",
    "SemanticAnalyzer",
    "PromptTemplates",
    "PromptTemplate",
]

"""LLM client for semantic analysis of policy changes."""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

from policy_diff.models.diff_result import (
    SemanticAnalysis,
    Significance,
    ChangeCategory,
)


class LLMProvider(str, Enum):
    """Available LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"  # Future support
    ANTHROPIC = "anthropic"  # Future support


class OllamaModel(str, Enum):
    """Available Ollama models."""

    LLAMA3_8B = "llama3:8b"
    LLAMA3_70B = "llama3:70b"
    MISTRAL = "mistral"
    MIXTRAL = "mixtral"
    PHI3 = "phi3"


@dataclass
class LLMConfig:
    """Configuration for LLM client."""

    provider: LLMProvider = LLMProvider.OLLAMA
    model: str = OllamaModel.LLAMA3_8B.value
    temperature: float = 0.1  # Low for consistent analysis
    max_tokens: int = 1024
    timeout: int = 60
    base_url: Optional[str] = None  # For Ollama: http://localhost:11434


class LLMClient:
    """Client for LLM-powered semantic analysis."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize LLM client.

        Args:
            config: LLM configuration
        """
        self.config = config or LLMConfig()
        self._call_count = 0

    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        if self.config.provider == LLMProvider.OLLAMA:
            return OLLAMA_AVAILABLE and self._check_ollama_connection()
        return False

    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running."""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def analyze_change(
        self,
        text_before: str,
        text_after: str,
        context: Optional[str] = None,
    ) -> Optional[SemanticAnalysis]:
        """Analyze a change between two text segments.

        Args:
            text_before: Original text
            text_after: Modified text
            context: Optional surrounding context

        Returns:
            SemanticAnalysis or None if LLM unavailable
        """
        if not self.is_available:
            return None

        prompt = self._build_analysis_prompt(text_before, text_after, context)

        try:
            response = self._call_llm(prompt)
            self._call_count += 1
            return self._parse_analysis_response(response)
        except Exception:
            return None

    def analyze_batch(
        self,
        changes: list[tuple[str, str]],
        contexts: Optional[list[str]] = None,
    ) -> list[Optional[SemanticAnalysis]]:
        """Analyze multiple changes.

        Args:
            changes: List of (text_before, text_after) tuples
            contexts: Optional list of contexts

        Returns:
            List of SemanticAnalysis or None for each change
        """
        results = []
        contexts = contexts or [None] * len(changes)

        for (before, after), context in zip(changes, contexts):
            result = self.analyze_change(before, after, context)
            results.append(result)

        return results

    def _build_analysis_prompt(
        self,
        text_before: str,
        text_after: str,
        context: Optional[str] = None,
    ) -> str:
        """Build prompt for semantic analysis.

        Args:
            text_before: Original text
            text_after: Modified text
            context: Optional context

        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the following change in a policy document and provide a structured assessment.

ORIGINAL TEXT:
{text_before or "[REMOVED]"}

MODIFIED TEXT:
{text_after or "[ADDED]"}
"""

        if context:
            prompt += f"""
CONTEXT:
{context}
"""

        prompt += """
Provide your analysis in the following JSON format:
{
    "significance": "critical|high|medium|low|none",
    "confidence": 0.0-1.0,
    "categories": ["coverage|exclusion|limit|definition|obligation|permission|condition|formatting|restructure|other"],
    "explanation": "Brief explanation of the change",
    "business_impact": "Impact on policyholder or business",
    "requires_review": true/false,
    "regulatory_impact": "Any regulatory implications or null"
}

Guidelines:
- CRITICAL: Material change affecting rights, coverage, or obligations
- HIGH: Significant change requiring stakeholder review
- MEDIUM: Notable change that may need attention
- LOW: Minor change, likely cosmetic or clarifying
- NONE: No semantic change (formatting only)

Respond ONLY with the JSON object, no other text."""

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with a prompt.

        Args:
            prompt: Prompt to send

        Returns:
            LLM response text
        """
        if self.config.provider == LLMProvider.OLLAMA:
            return self._call_ollama(prompt)
        else:
            raise NotImplementedError(f"Provider {self.config.provider} not implemented")

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API.

        Args:
            prompt: Prompt to send

        Returns:
            Response text
        """
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama not available")

        response = ollama.generate(
            model=self.config.model,
            prompt=prompt,
            options={
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        )

        return response["response"]

    def _parse_analysis_response(self, response: str) -> Optional[SemanticAnalysis]:
        """Parse LLM response into SemanticAnalysis.

        Args:
            response: Raw LLM response

        Returns:
            SemanticAnalysis or None if parsing fails
        """
        try:
            # Extract JSON from response
            response = response.strip()

            # Handle potential markdown code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith("```") and not in_json:
                        in_json = True
                        continue
                    elif line.startswith("```") and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                response = "\n".join(json_lines)

            data = json.loads(response)

            # Parse significance
            sig_str = data.get("significance", "none").lower()
            try:
                significance = Significance(sig_str)
            except ValueError:
                significance = Significance.NONE

            # Parse categories
            categories = []
            for cat_str in data.get("categories", []):
                try:
                    categories.append(ChangeCategory(cat_str.lower()))
                except ValueError:
                    pass
            if not categories:
                categories = [ChangeCategory.OTHER]

            return SemanticAnalysis(
                significance=significance,
                confidence=float(data.get("confidence", 0.5)),
                categories=categories,
                explanation=str(data.get("explanation", "")),
                business_impact=str(data.get("business_impact", "")),
                requires_review=bool(data.get("requires_review", False)),
                regulatory_impact=data.get("regulatory_impact"),
            )

        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    @property
    def call_count(self) -> int:
        """Get number of LLM calls made."""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset call counter."""
        self._call_count = 0


class SemanticAnalyzer:
    """High-level semantic analyzer combining embeddings and LLM."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        embedding_engine=None,
        confidence_threshold: float = 0.7,
        skip_llm_above_similarity: float = 0.95,
    ):
        """Initialize semantic analyzer.

        Args:
            llm_client: LLM client for deep analysis
            embedding_engine: Embedding engine for similarity
            confidence_threshold: Minimum confidence for LLM results
            skip_llm_above_similarity: Skip LLM if similarity above this
        """
        self.llm_client = llm_client or LLMClient()
        self.embedding_engine = embedding_engine
        self.confidence_threshold = confidence_threshold
        self.skip_llm_above_similarity = skip_llm_above_similarity

    def analyze(
        self,
        text_before: str,
        text_after: str,
        similarity_score: Optional[float] = None,
    ) -> Optional[SemanticAnalysis]:
        """Analyze a change with smart LLM routing.

        Args:
            text_before: Original text
            text_after: Modified text
            similarity_score: Pre-computed similarity if available

        Returns:
            SemanticAnalysis or None
        """
        # Compute similarity if not provided
        if similarity_score is None and self.embedding_engine:
            result = self.embedding_engine.similarity(text_before, text_after)
            similarity_score = result.similarity

        # Skip LLM for near-identical text
        if similarity_score and similarity_score >= self.skip_llm_above_similarity:
            return SemanticAnalysis(
                significance=Significance.NONE,
                confidence=similarity_score,
                categories=[ChangeCategory.FORMATTING],
                explanation="No significant semantic change detected",
                business_impact="None - formatting change only",
                requires_review=False,
            )

        # Use LLM for significant changes
        return self.llm_client.analyze_change(text_before, text_after)

    def should_use_llm(
        self,
        text_before: str,
        text_after: str,
        similarity_score: Optional[float] = None,
    ) -> bool:
        """Determine if LLM analysis is needed.

        Args:
            text_before: Original text
            text_after: Modified text
            similarity_score: Pre-computed similarity

        Returns:
            True if LLM analysis recommended
        """
        # Always use LLM for additions/deletions
        if not text_before or not text_after:
            return True

        # Check similarity
        if similarity_score is None and self.embedding_engine:
            result = self.embedding_engine.similarity(text_before, text_after)
            similarity_score = result.similarity

        if similarity_score and similarity_score >= self.skip_llm_above_similarity:
            return False

        return True

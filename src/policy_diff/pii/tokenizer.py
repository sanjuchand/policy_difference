"""PII tokenization module for masking sensitive data before LLM processing."""

import hashlib
import secrets
import string
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from policy_diff.pii.detector import PIIDetector, PIIEntity, PIIType, SensitivityLevel


class TokenizationStrategy(str, Enum):
    """Strategy for tokenizing PII."""

    PLACEHOLDER = "placeholder"  # Replace with type placeholder: [PERSON_1]
    HASH = "hash"  # Replace with hash: [HASH_a1b2c3]
    RANDOM = "random"  # Replace with random token: [TOKEN_xyz123]
    REDACT = "redact"  # Replace with fixed marker: [REDACTED]
    MASK = "mask"  # Partial masking: J*** D**


@dataclass
class TokenMapping:
    """Mapping from token to original PII value."""

    token: str
    original_value: str
    entity_type: PIIType
    sensitivity: SensitivityLevel
    start: int
    end: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "token": self.token,
            "original_value": self.original_value,
            "entity_type": self.entity_type.value,
            "sensitivity": self.sensitivity.value,
            "start": self.start,
            "end": self.end,
        }


@dataclass
class TokenizationResult:
    """Result of PII tokenization."""

    original_text: str
    tokenized_text: str
    mappings: list[TokenMapping] = field(default_factory=list)
    pii_count: int = 0

    def __post_init__(self):
        """Compute derived fields."""
        self.pii_count = len(self.mappings)

    def detokenize(self) -> str:
        """Restore original text from tokenized text.

        Returns:
            Original text with PII restored
        """
        result = self.tokenized_text

        # Sort mappings by token length (longest first) to avoid partial replacements
        sorted_mappings = sorted(self.mappings, key=lambda m: len(m.token), reverse=True)

        for mapping in sorted_mappings:
            result = result.replace(mapping.token, mapping.original_value)

        return result

    def get_mappings_by_type(self, pii_type: PIIType) -> list[TokenMapping]:
        """Get all mappings of a specific type."""
        return [m for m in self.mappings if m.entity_type == pii_type]


class PIITokenizer:
    """Tokenizes PII in text for safe LLM processing."""

    def __init__(
        self,
        strategy: TokenizationStrategy = TokenizationStrategy.PLACEHOLDER,
        detector: Optional[PIIDetector] = None,
        min_sensitivity: SensitivityLevel = SensitivityLevel.LOW,
        preserve_format: bool = True,
    ):
        """Initialize tokenizer.

        Args:
            strategy: Tokenization strategy to use
            detector: PII detector instance
            min_sensitivity: Minimum sensitivity level to tokenize
            preserve_format: Whether to preserve format hints in tokens
        """
        self.strategy = strategy
        self.detector = detector or PIIDetector()
        self.min_sensitivity = min_sensitivity
        self.preserve_format = preserve_format

        # Token counters for placeholder strategy
        self._type_counters: dict[PIIType, int] = {}

        # Token registry for consistent tokenization
        self._token_registry: dict[str, str] = {}

    def tokenize(self, text: str) -> TokenizationResult:
        """Tokenize PII in text.

        Args:
            text: Text to tokenize

        Returns:
            TokenizationResult with tokenized text and mappings
        """
        # Detect PII
        detection_result = self.detector.detect(text)

        # Filter by sensitivity
        entities = [
            e
            for e in detection_result.entities
            if e.sensitivity >= self.min_sensitivity
        ]

        if not entities:
            return TokenizationResult(
                original_text=text,
                tokenized_text=text,
                mappings=[],
            )

        # Sort entities by position (reverse for replacement)
        entities.sort(key=lambda e: e.start, reverse=True)

        mappings: list[TokenMapping] = []
        result_text = text

        for entity in entities:
            token = self._generate_token(entity)

            mapping = TokenMapping(
                token=token,
                original_value=entity.text,
                entity_type=entity.entity_type,
                sensitivity=entity.sensitivity,
                start=entity.start,
                end=entity.end,
            )
            mappings.append(mapping)

            # Replace in text
            result_text = result_text[: entity.start] + token + result_text[entity.end :]

        # Reverse mappings to match original order
        mappings.reverse()

        return TokenizationResult(
            original_text=text,
            tokenized_text=result_text,
            mappings=mappings,
        )

    def _generate_token(self, entity: PIIEntity) -> str:
        """Generate a token for a PII entity.

        Args:
            entity: PII entity to tokenize

        Returns:
            Token string
        """
        # Check registry for consistent tokenization
        registry_key = f"{entity.entity_type.value}:{entity.text}"
        if registry_key in self._token_registry:
            return self._token_registry[registry_key]

        if self.strategy == TokenizationStrategy.PLACEHOLDER:
            token = self._placeholder_token(entity)
        elif self.strategy == TokenizationStrategy.HASH:
            token = self._hash_token(entity)
        elif self.strategy == TokenizationStrategy.RANDOM:
            token = self._random_token(entity)
        elif self.strategy == TokenizationStrategy.REDACT:
            token = self._redact_token(entity)
        elif self.strategy == TokenizationStrategy.MASK:
            token = self._mask_token(entity)
        else:
            token = self._placeholder_token(entity)

        self._token_registry[registry_key] = token
        return token

    def _placeholder_token(self, entity: PIIEntity) -> str:
        """Generate placeholder token like [PERSON_1].

        Args:
            entity: PII entity

        Returns:
            Placeholder token
        """
        pii_type = entity.entity_type
        count = self._type_counters.get(pii_type, 0) + 1
        self._type_counters[pii_type] = count

        # Simplify type name
        type_name = pii_type.value.replace("_", "").upper()

        return f"[{type_name}_{count}]"

    def _hash_token(self, entity: PIIEntity) -> str:
        """Generate hash-based token.

        Args:
            entity: PII entity

        Returns:
            Hash token
        """
        # Create deterministic hash
        hash_input = f"{entity.entity_type.value}:{entity.text}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

        return f"[HASH_{hash_value}]"

    def _random_token(self, entity: PIIEntity) -> str:
        """Generate random token.

        Args:
            entity: PII entity

        Returns:
            Random token
        """
        chars = string.ascii_lowercase + string.digits
        random_str = "".join(secrets.choice(chars) for _ in range(8))

        return f"[TOKEN_{random_str}]"

    def _redact_token(self, entity: PIIEntity) -> str:
        """Generate redaction marker.

        Args:
            entity: PII entity

        Returns:
            Redaction marker
        """
        if self.preserve_format:
            # Preserve length hint
            length = len(entity.text)
            return f"[REDACTED_{length}]"
        return "[REDACTED]"

    def _mask_token(self, entity: PIIEntity) -> str:
        """Generate masked token preserving some characters.

        Args:
            entity: PII entity

        Returns:
            Masked value
        """
        text = entity.text

        if len(text) <= 2:
            return "*" * len(text)

        # Mask strategy based on entity type
        if entity.entity_type == PIIType.EMAIL:
            # Show first char and domain: j***@example.com
            at_pos = text.find("@")
            if at_pos > 0:
                return text[0] + "*" * (at_pos - 1) + text[at_pos:]

        elif entity.entity_type == PIIType.PHONE:
            # Show last 4 digits: ***-***-1234
            digits = "".join(c for c in text if c.isdigit())
            if len(digits) >= 4:
                return "*" * (len(text) - 4) + text[-4:]

        elif entity.entity_type == PIIType.CREDIT_CARD:
            # Show last 4 digits: ****-****-****-1234
            return "*" * (len(text) - 4) + text[-4:]

        elif entity.entity_type == PIIType.SSN:
            # Show last 4: ***-**-1234
            if len(text) >= 4:
                return "*" * (len(text) - 4) + text[-4:]

        elif entity.entity_type == PIIType.PERSON_NAME:
            # Show initials: J*** D**
            words = text.split()
            masked_words = [w[0] + "*" * (len(w) - 1) if w else "" for w in words]
            return " ".join(masked_words)

        # Default: show first and last char
        if len(text) > 2:
            return text[0] + "*" * (len(text) - 2) + text[-1]
        return "*" * len(text)

    def reset(self) -> None:
        """Reset token counters and registry."""
        self._type_counters.clear()
        self._token_registry.clear()


class BatchTokenizer:
    """Tokenizes multiple texts with consistent token mappings."""

    def __init__(
        self,
        strategy: TokenizationStrategy = TokenizationStrategy.PLACEHOLDER,
        **kwargs,
    ):
        """Initialize batch tokenizer.

        Args:
            strategy: Tokenization strategy
            **kwargs: Arguments passed to PIITokenizer
        """
        self.tokenizer = PIITokenizer(strategy=strategy, **kwargs)

    def tokenize_batch(self, texts: list[str]) -> list[TokenizationResult]:
        """Tokenize a batch of texts with consistent mappings.

        Args:
            texts: List of texts to tokenize

        Returns:
            List of TokenizationResults
        """
        self.tokenizer.reset()
        return [self.tokenizer.tokenize(text) for text in texts]

    def tokenize_pair(
        self, text_a: str, text_b: str
    ) -> tuple[TokenizationResult, TokenizationResult]:
        """Tokenize a pair of texts with consistent mappings.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Tuple of TokenizationResults
        """
        self.tokenizer.reset()
        return self.tokenizer.tokenize(text_a), self.tokenizer.tokenize(text_b)


def tokenize_pii(
    text: str,
    strategy: TokenizationStrategy = TokenizationStrategy.PLACEHOLDER,
    **kwargs,
) -> TokenizationResult:
    """Convenience function to tokenize PII in text.

    Args:
        text: Text to tokenize
        strategy: Tokenization strategy
        **kwargs: Arguments passed to PIITokenizer

    Returns:
        TokenizationResult
    """
    tokenizer = PIITokenizer(strategy=strategy, **kwargs)
    return tokenizer.tokenize(text)

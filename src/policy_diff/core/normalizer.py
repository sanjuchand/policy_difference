"""Text normalization module for consistent text comparison."""

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class NormalizationLevel(str, Enum):
    """Level of text normalization to apply."""

    NONE = "none"  # No normalization
    MINIMAL = "minimal"  # Whitespace only
    STANDARD = "standard"  # Whitespace + case + punctuation
    AGGRESSIVE = "aggressive"  # Full normalization including numbers


@dataclass
class NormalizationResult:
    """Result of text normalization."""

    original: str
    normalized: str
    transformations: list[str]

    @property
    def was_modified(self) -> bool:
        """Check if text was modified."""
        return self.original != self.normalized


class TextNormalizer:
    """Normalizes text for consistent comparison."""

    # Common ligatures and their expansions
    LIGATURES = {
        "æ": "ae",
        "œ": "oe",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
    }

    # Smart quotes and their ASCII equivalents
    QUOTE_CHARS = {
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
        "«": '"',
        "»": '"',
        "‹": "'",
        "›": "'",
    }

    # Dash variants
    DASH_CHARS = {
        "–": "-",  # en-dash
        "—": "-",  # em-dash
        "−": "-",  # minus sign
        "‐": "-",  # hyphen
        "‑": "-",  # non-breaking hyphen
    }

    # Whitespace variants
    WHITESPACE_CHARS = {
        "\u00a0": " ",  # non-breaking space
        "\u2000": " ",  # en quad
        "\u2001": " ",  # em quad
        "\u2002": " ",  # en space
        "\u2003": " ",  # em space
        "\u2004": " ",  # three-per-em space
        "\u2005": " ",  # four-per-em space
        "\u2006": " ",  # six-per-em space
        "\u2007": " ",  # figure space
        "\u2008": " ",  # punctuation space
        "\u2009": " ",  # thin space
        "\u200a": " ",  # hair space
        "\u202f": " ",  # narrow no-break space
        "\u205f": " ",  # medium mathematical space
        "\u3000": " ",  # ideographic space
        "\t": " ",  # tab
    }

    # Number word mappings
    NUMBER_WORDS = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "eleven": "11",
        "twelve": "12",
        "thirteen": "13",
        "fourteen": "14",
        "fifteen": "15",
        "sixteen": "16",
        "seventeen": "17",
        "eighteen": "18",
        "nineteen": "19",
        "twenty": "20",
        "thirty": "30",
        "forty": "40",
        "fifty": "50",
        "sixty": "60",
        "seventy": "70",
        "eighty": "80",
        "ninety": "90",
        "hundred": "100",
        "thousand": "1000",
        "million": "1000000",
    }

    def __init__(
        self,
        level: NormalizationLevel = NormalizationLevel.STANDARD,
        preserve_structure: bool = True,
        custom_rules: list[tuple[str, str]] | None = None,
    ):
        """Initialize normalizer.

        Args:
            level: Level of normalization to apply
            preserve_structure: Whether to preserve paragraph structure
            custom_rules: List of (pattern, replacement) tuples for custom normalization
        """
        self.level = level
        self.preserve_structure = preserve_structure
        self.custom_rules = custom_rules or []

        # Compile custom rule patterns
        self._compiled_rules: list[tuple[re.Pattern, str]] = [
            (re.compile(pattern), replacement)
            for pattern, replacement in self.custom_rules
        ]

    def normalize(self, text: str) -> NormalizationResult:
        """Normalize text according to configured level.

        Args:
            text: Text to normalize

        Returns:
            NormalizationResult with original and normalized text
        """
        if self.level == NormalizationLevel.NONE:
            return NormalizationResult(
                original=text, normalized=text, transformations=[]
            )

        original = text
        transformations: list[str] = []
        normalizers: list[tuple[str, Callable[[str], str]]] = []

        # Build normalization pipeline based on level
        if self.level in (
            NormalizationLevel.MINIMAL,
            NormalizationLevel.STANDARD,
            NormalizationLevel.AGGRESSIVE,
        ):
            normalizers.extend([
                ("unicode_normalize", self._normalize_unicode),
                ("whitespace", self._normalize_whitespace),
            ])

        if self.level in (NormalizationLevel.STANDARD, NormalizationLevel.AGGRESSIVE):
            normalizers.extend([
                ("quotes", self._normalize_quotes),
                ("dashes", self._normalize_dashes),
                ("ligatures", self._normalize_ligatures),
                ("case", self._normalize_case),
            ])

        if self.level == NormalizationLevel.AGGRESSIVE:
            normalizers.extend([
                ("numbers", self._normalize_numbers),
                ("punctuation", self._normalize_punctuation),
            ])

        # Always apply custom rules last
        if self.custom_rules:
            normalizers.append(("custom", self._apply_custom_rules))

        # Apply normalizers
        result = text
        for name, normalizer in normalizers:
            before = result
            result = normalizer(result)
            if before != result:
                transformations.append(name)

        # Final whitespace cleanup
        if self.preserve_structure:
            result = self._preserve_paragraph_structure(result)
        else:
            result = " ".join(result.split())

        return NormalizationResult(
            original=original, normalized=result, transformations=transformations
        )

    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode to NFC form.

        Args:
            text: Text to normalize

        Returns:
            Unicode-normalized text
        """
        return unicodedata.normalize("NFC", text)

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace characters.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized whitespace
        """
        # Replace special whitespace characters
        for char, replacement in self.WHITESPACE_CHARS.items():
            text = text.replace(char, replacement)

        # Collapse multiple spaces
        text = re.sub(r" +", " ", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove trailing whitespace from lines
        text = re.sub(r" +\n", "\n", text)

        return text

    def _normalize_quotes(self, text: str) -> str:
        """Normalize quote characters.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized quotes
        """
        for char, replacement in self.QUOTE_CHARS.items():
            text = text.replace(char, replacement)
        return text

    def _normalize_dashes(self, text: str) -> str:
        """Normalize dash characters.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized dashes
        """
        for char, replacement in self.DASH_CHARS.items():
            text = text.replace(char, replacement)
        return text

    def _normalize_ligatures(self, text: str) -> str:
        """Expand ligature characters.

        Args:
            text: Text to normalize

        Returns:
            Text with expanded ligatures
        """
        for char, replacement in self.LIGATURES.items():
            text = text.replace(char, replacement)
        return text

    def _normalize_case(self, text: str) -> str:
        """Normalize to lowercase.

        Args:
            text: Text to normalize

        Returns:
            Lowercase text
        """
        return text.lower()

    def _normalize_numbers(self, text: str) -> str:
        """Normalize number representations.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized numbers
        """
        # Convert number words to digits
        for word, digit in self.NUMBER_WORDS.items():
            text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)

        # Normalize currency symbols
        text = re.sub(r"\$\s*(\d)", r"$\1", text)  # Remove space after $
        text = re.sub(r"(\d)\s*%", r"\1%", text)  # Remove space before %

        # Normalize number formatting
        text = re.sub(r"(\d),(\d{3})", r"\1\2", text)  # Remove thousands separators

        return text

    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized punctuation
        """
        # Remove multiple periods
        text = re.sub(r"\.{2,}", ".", text)

        # Normalize ellipsis
        text = text.replace("…", "...")

        # Remove spaces before punctuation
        text = re.sub(r"\s+([.,:;!?])", r"\1", text)

        # Add space after punctuation if missing
        text = re.sub(r"([.,:;!?])([A-Za-z])", r"\1 \2", text)

        return text

    def _apply_custom_rules(self, text: str) -> str:
        """Apply custom normalization rules.

        Args:
            text: Text to normalize

        Returns:
            Text with custom rules applied
        """
        for pattern, replacement in self._compiled_rules:
            text = pattern.sub(replacement, text)
        return text

    def _preserve_paragraph_structure(self, text: str) -> str:
        """Preserve paragraph structure while normalizing.

        Args:
            text: Text to process

        Returns:
            Text with preserved paragraph structure
        """
        # Split into paragraphs
        paragraphs = re.split(r"\n\s*\n", text)

        # Normalize each paragraph
        normalized_paragraphs = []
        for para in paragraphs:
            # Collapse whitespace within paragraph
            para = " ".join(para.split())
            if para:
                normalized_paragraphs.append(para)

        # Join with double newline
        return "\n\n".join(normalized_paragraphs)


class PolicyTextNormalizer(TextNormalizer):
    """Specialized normalizer for policy documents."""

    # Policy-specific patterns
    POLICY_PATTERNS = [
        # Normalize section references
        (r"(?:section|sect\.?|sec\.?)\s*(\d+)", r"section \1"),
        # Normalize article references
        (r"(?:article|art\.?)\s*(\d+)", r"article \1"),
        # Normalize paragraph references
        (r"(?:paragraph|para\.?|par\.?)\s*(\d+)", r"paragraph \1"),
        # Normalize clause references
        (r"(?:clause|cl\.?)\s*(\d+)", r"clause \1"),
        # Normalize "pursuant to"
        (r"pursuant\s+to", "under"),
        # Normalize "in accordance with"
        (r"in\s+accordance\s+with", "under"),
        # Normalize "hereinafter"
        (r"hereinafter\s+(?:referred\s+to\s+as\s+)?", ""),
        # Normalize legal Latin
        (r"\binter\s+alia\b", "among other things"),
        (r"\bmutatis\s+mutandis\b", "with necessary changes"),
    ]

    def __init__(
        self,
        level: NormalizationLevel = NormalizationLevel.STANDARD,
        normalize_legal_terms: bool = True,
        **kwargs,
    ):
        """Initialize policy normalizer.

        Args:
            level: Normalization level
            normalize_legal_terms: Whether to normalize legal terminology
            **kwargs: Additional arguments passed to parent
        """
        custom_rules = kwargs.pop("custom_rules", [])
        if normalize_legal_terms:
            custom_rules = self.POLICY_PATTERNS + list(custom_rules)

        super().__init__(level=level, custom_rules=custom_rules, **kwargs)


def normalize_text(
    text: str, level: NormalizationLevel = NormalizationLevel.STANDARD, **kwargs
) -> str:
    """Convenience function to normalize text.

    Args:
        text: Text to normalize
        level: Normalization level
        **kwargs: Additional arguments passed to TextNormalizer

    Returns:
        Normalized text
    """
    normalizer = TextNormalizer(level=level, **kwargs)
    return normalizer.normalize(text).normalized


def normalize_for_comparison(text_a: str, text_b: str, **kwargs) -> tuple[str, str]:
    """Normalize two texts for comparison.

    Args:
        text_a: First text
        text_b: Second text
        **kwargs: Arguments passed to TextNormalizer

    Returns:
        Tuple of normalized texts
    """
    normalizer = TextNormalizer(**kwargs)
    return normalizer.normalize(text_a).normalized, normalizer.normalize(text_b).normalized

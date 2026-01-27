"""Tests for text normalizer."""

import pytest

from policy_diff.core.normalizer import (
    TextNormalizer,
    PolicyTextNormalizer,
    NormalizationLevel,
    normalize_text,
    normalize_for_comparison,
)


class TestTextNormalizer:
    """Tests for TextNormalizer class."""

    def test_no_normalization(self):
        """Test that NONE level preserves text exactly."""
        normalizer = TextNormalizer(level=NormalizationLevel.NONE)
        text = "Hello  World\n\nTest"
        result = normalizer.normalize(text)

        assert result.normalized == text
        assert not result.was_modified

    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        normalizer = TextNormalizer(level=NormalizationLevel.MINIMAL)
        text = "Hello   World\t\tTest"
        result = normalizer.normalize(text)

        assert "   " not in result.normalized
        assert "\t" not in result.normalized

    def test_quote_normalization(self):
        """Test smart quote normalization."""
        normalizer = TextNormalizer(level=NormalizationLevel.STANDARD)
        text = '"Hello" and 'World'"
        result = normalizer.normalize(text)

        assert '"' not in result.normalized
        assert "'" not in result.normalized
        assert '"' in result.normalized or "'" in result.normalized

    def test_dash_normalization(self):
        """Test dash/hyphen normalization."""
        normalizer = TextNormalizer(level=NormalizationLevel.STANDARD)
        text = "test–value—example"  # en-dash and em-dash
        result = normalizer.normalize(text)

        assert "–" not in result.normalized
        assert "—" not in result.normalized

    def test_case_normalization(self):
        """Test case normalization in standard mode."""
        normalizer = TextNormalizer(level=NormalizationLevel.STANDARD)
        text = "HELLO World"
        result = normalizer.normalize(text)

        assert result.normalized == "hello world"

    def test_paragraph_preservation(self):
        """Test that paragraph structure is preserved."""
        normalizer = TextNormalizer(level=NormalizationLevel.STANDARD, preserve_structure=True)
        text = "First paragraph.\n\nSecond paragraph."
        result = normalizer.normalize(text)

        assert "\n\n" in result.normalized

    def test_transformations_tracked(self):
        """Test that transformations are tracked."""
        normalizer = TextNormalizer(level=NormalizationLevel.STANDARD)
        text = "HELLO  World"
        result = normalizer.normalize(text)

        assert len(result.transformations) > 0
        assert "whitespace" in result.transformations
        assert "case" in result.transformations


class TestPolicyTextNormalizer:
    """Tests for PolicyTextNormalizer class."""

    def test_section_reference_normalization(self):
        """Test section reference normalization."""
        normalizer = PolicyTextNormalizer()
        text = "See Sect. 5 and Section 10"
        result = normalizer.normalize(text)

        # Should normalize to consistent format
        assert "section 5" in result.normalized
        assert "section 10" in result.normalized

    def test_article_reference_normalization(self):
        """Test article reference normalization."""
        normalizer = PolicyTextNormalizer()
        text = "See Art. 3 for details"
        result = normalizer.normalize(text)

        assert "article 3" in result.normalized

    def test_legal_latin_normalization(self):
        """Test legal Latin term normalization."""
        normalizer = PolicyTextNormalizer()
        text = "This includes, inter alia, the following"
        result = normalizer.normalize(text)

        assert "among other things" in result.normalized


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_normalize_text(self):
        """Test normalize_text function."""
        result = normalize_text("HELLO  World", level=NormalizationLevel.STANDARD)
        assert result == "hello world"

    def test_normalize_for_comparison(self):
        """Test normalize_for_comparison function."""
        text_a = "HELLO  World"
        text_b = "hello world"
        norm_a, norm_b = normalize_for_comparison(text_a, text_b)

        assert norm_a == norm_b

"""PII detection module using Presidio and custom patterns."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

try:
    from presidio_analyzer import AnalyzerEngine, RecognizerResult
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    AnalyzerEngine = None
    RecognizerResult = None


class PIIType(str, Enum):
    """Types of PII that can be detected."""

    # Personal identifiers
    PERSON_NAME = "PERSON"
    EMAIL = "EMAIL_ADDRESS"
    PHONE = "PHONE_NUMBER"
    SSN = "US_SSN"
    PASSPORT = "US_PASSPORT"
    DRIVER_LICENSE = "US_DRIVER_LICENSE"

    # Financial
    CREDIT_CARD = "CREDIT_CARD"
    BANK_ACCOUNT = "US_BANK_NUMBER"
    IBAN = "IBAN_CODE"

    # Location
    ADDRESS = "ADDRESS"
    ZIP_CODE = "ZIP_CODE"

    # Network
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"

    # Medical
    MEDICAL_LICENSE = "MEDICAL_LICENSE"
    NPI = "NPI"

    # Dates
    DATE_OF_BIRTH = "DATE_TIME"

    # Other
    POLICY_NUMBER = "POLICY_NUMBER"
    CLAIM_NUMBER = "CLAIM_NUMBER"
    ACCOUNT_NUMBER = "ACCOUNT_NUMBER"


class SensitivityLevel(int, Enum):
    """Sensitivity level of PII."""

    LOW = 1  # Names, general info
    MEDIUM = 2  # Contact info, addresses
    HIGH = 3  # Financial info
    CRITICAL = 4  # SSN, medical info


@dataclass
class PIIEntity:
    """A detected PII entity."""

    entity_type: PIIType
    text: str
    start: int
    end: int
    confidence: float
    sensitivity: SensitivityLevel
    source: str = "presidio"  # presidio, regex, or custom

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "entity_type": self.entity_type.value,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "sensitivity": self.sensitivity.value,
            "source": self.source,
        }


@dataclass
class PIIDetectionResult:
    """Result of PII detection on text."""

    original_text: str
    entities: list[PIIEntity] = field(default_factory=list)
    has_pii: bool = False
    highest_sensitivity: SensitivityLevel = SensitivityLevel.LOW

    def __post_init__(self):
        """Compute derived fields."""
        self.has_pii = len(self.entities) > 0
        if self.entities:
            self.highest_sensitivity = max(e.sensitivity for e in self.entities)

    def get_entities_by_type(self, pii_type: PIIType) -> list[PIIEntity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.entity_type == pii_type]

    def get_entities_by_sensitivity(
        self, min_sensitivity: SensitivityLevel
    ) -> list[PIIEntity]:
        """Get all entities at or above a sensitivity level."""
        return [e for e in self.entities if e.sensitivity >= min_sensitivity]


class PIIDetector:
    """Detects PII in text using Presidio and custom patterns."""

    # Sensitivity mapping for entity types
    SENSITIVITY_MAP = {
        PIIType.PERSON_NAME: SensitivityLevel.LOW,
        PIIType.EMAIL: SensitivityLevel.MEDIUM,
        PIIType.PHONE: SensitivityLevel.MEDIUM,
        PIIType.ADDRESS: SensitivityLevel.MEDIUM,
        PIIType.ZIP_CODE: SensitivityLevel.LOW,
        PIIType.URL: SensitivityLevel.LOW,
        PIIType.IP_ADDRESS: SensitivityLevel.MEDIUM,
        PIIType.DATE_OF_BIRTH: SensitivityLevel.MEDIUM,
        PIIType.CREDIT_CARD: SensitivityLevel.HIGH,
        PIIType.BANK_ACCOUNT: SensitivityLevel.HIGH,
        PIIType.IBAN: SensitivityLevel.HIGH,
        PIIType.SSN: SensitivityLevel.CRITICAL,
        PIIType.PASSPORT: SensitivityLevel.CRITICAL,
        PIIType.DRIVER_LICENSE: SensitivityLevel.HIGH,
        PIIType.MEDICAL_LICENSE: SensitivityLevel.HIGH,
        PIIType.NPI: SensitivityLevel.HIGH,
        PIIType.POLICY_NUMBER: SensitivityLevel.MEDIUM,
        PIIType.CLAIM_NUMBER: SensitivityLevel.MEDIUM,
        PIIType.ACCOUNT_NUMBER: SensitivityLevel.HIGH,
    }

    # Custom regex patterns for insurance-specific PII
    CUSTOM_PATTERNS = {
        PIIType.POLICY_NUMBER: [
            r"\b(?:policy\s*(?:no\.?|number|#)\s*:?\s*)([A-Z]{2,4}[-\s]?\d{6,12})\b",
            r"\b([A-Z]{2,3}\d{2}[-\s]?\d{6,8})\b",  # Common policy format
        ],
        PIIType.CLAIM_NUMBER: [
            r"\b(?:claim\s*(?:no\.?|number|#)\s*:?\s*)(\d{8,15})\b",
            r"\b(?:CLM|CL)[-\s]?(\d{8,12})\b",
        ],
        PIIType.ACCOUNT_NUMBER: [
            r"\b(?:account\s*(?:no\.?|number|#)\s*:?\s*)(\d{8,17})\b",
            r"\b(?:acct\.?\s*#?\s*:?\s*)(\d{8,17})\b",
        ],
    }

    def __init__(
        self,
        use_presidio: bool = True,
        use_custom_patterns: bool = True,
        min_confidence: float = 0.5,
        language: str = "en",
    ):
        """Initialize PII detector.

        Args:
            use_presidio: Whether to use Presidio for detection
            use_custom_patterns: Whether to use custom regex patterns
            min_confidence: Minimum confidence threshold
            language: Language for NLP processing
        """
        self.use_presidio = use_presidio and PRESIDIO_AVAILABLE
        self.use_custom_patterns = use_custom_patterns
        self.min_confidence = min_confidence
        self.language = language

        self._analyzer: Optional[AnalyzerEngine] = None
        self._compiled_patterns: dict[PIIType, list[re.Pattern]] = {}

        if self.use_presidio:
            self._init_presidio()

        if self.use_custom_patterns:
            self._compile_patterns()

    def _init_presidio(self) -> None:
        """Initialize Presidio analyzer."""
        if not PRESIDIO_AVAILABLE:
            return

        try:
            # Configure NLP engine with spaCy
            provider = NlpEngineProvider(nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            })
            nlp_engine = provider.create_engine()
            self._analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        except Exception:
            # Fall back to default engine
            try:
                self._analyzer = AnalyzerEngine()
            except Exception:
                self._analyzer = None
                self.use_presidio = False

    def _compile_patterns(self) -> None:
        """Compile custom regex patterns."""
        for pii_type, patterns in self.CUSTOM_PATTERNS.items():
            self._compiled_patterns[pii_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def detect(self, text: str) -> PIIDetectionResult:
        """Detect PII in text.

        Args:
            text: Text to analyze

        Returns:
            PIIDetectionResult with detected entities
        """
        entities: list[PIIEntity] = []

        # Run Presidio detection
        if self.use_presidio and self._analyzer:
            presidio_entities = self._detect_with_presidio(text)
            entities.extend(presidio_entities)

        # Run custom pattern detection
        if self.use_custom_patterns:
            custom_entities = self._detect_with_patterns(text)
            # Merge, avoiding duplicates
            entities = self._merge_entities(entities, custom_entities)

        # Filter by confidence
        entities = [e for e in entities if e.confidence >= self.min_confidence]

        # Sort by position
        entities.sort(key=lambda e: e.start)

        return PIIDetectionResult(original_text=text, entities=entities)

    def _detect_with_presidio(self, text: str) -> list[PIIEntity]:
        """Detect PII using Presidio.

        Args:
            text: Text to analyze

        Returns:
            List of detected entities
        """
        if not self._analyzer:
            return []

        try:
            results = self._analyzer.analyze(
                text=text,
                language=self.language,
            )
        except Exception:
            return []

        entities = []
        for result in results:
            try:
                pii_type = PIIType(result.entity_type)
            except ValueError:
                continue  # Skip unknown entity types

            sensitivity = self.SENSITIVITY_MAP.get(pii_type, SensitivityLevel.MEDIUM)

            entity = PIIEntity(
                entity_type=pii_type,
                text=text[result.start : result.end],
                start=result.start,
                end=result.end,
                confidence=result.score,
                sensitivity=sensitivity,
                source="presidio",
            )
            entities.append(entity)

        return entities

    def _detect_with_patterns(self, text: str) -> list[PIIEntity]:
        """Detect PII using custom patterns.

        Args:
            text: Text to analyze

        Returns:
            List of detected entities
        """
        entities = []

        for pii_type, patterns in self._compiled_patterns.items():
            sensitivity = self.SENSITIVITY_MAP.get(pii_type, SensitivityLevel.MEDIUM)

            for pattern in patterns:
                for match in pattern.finditer(text):
                    # Get the captured group or full match
                    if match.groups():
                        matched_text = match.group(1)
                        start = match.start(1)
                        end = match.end(1)
                    else:
                        matched_text = match.group(0)
                        start = match.start()
                        end = match.end()

                    entity = PIIEntity(
                        entity_type=pii_type,
                        text=matched_text,
                        start=start,
                        end=end,
                        confidence=0.85,  # High confidence for regex matches
                        sensitivity=sensitivity,
                        source="regex",
                    )
                    entities.append(entity)

        return entities

    def _merge_entities(
        self, primary: list[PIIEntity], secondary: list[PIIEntity]
    ) -> list[PIIEntity]:
        """Merge entity lists, avoiding overlaps.

        Args:
            primary: Primary entities (take precedence)
            secondary: Secondary entities

        Returns:
            Merged list
        """
        merged = list(primary)

        for sec_entity in secondary:
            # Check for overlap with existing entities
            overlaps = False
            for pri_entity in merged:
                if self._entities_overlap(sec_entity, pri_entity):
                    overlaps = True
                    break

            if not overlaps:
                merged.append(sec_entity)

        return merged

    def _entities_overlap(self, a: PIIEntity, b: PIIEntity) -> bool:
        """Check if two entities overlap.

        Args:
            a: First entity
            b: Second entity

        Returns:
            True if they overlap
        """
        return not (a.end <= b.start or b.end <= a.start)


def detect_pii(text: str, **kwargs) -> PIIDetectionResult:
    """Convenience function to detect PII in text.

    Args:
        text: Text to analyze
        **kwargs: Arguments passed to PIIDetector

    Returns:
        PIIDetectionResult
    """
    detector = PIIDetector(**kwargs)
    return detector.detect(text)

"""Prompt templates for LLM interactions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """A prompt template with placeholders."""

    template: str
    description: str
    required_vars: list[str]

    def format(self, **kwargs) -> str:
        """Format the template with provided variables.

        Args:
            **kwargs: Variables to substitute

        Returns:
            Formatted prompt

        Raises:
            ValueError: If required variables missing
        """
        missing = set(self.required_vars) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        return self.template.format(**kwargs)


class PromptTemplates:
    """Collection of prompt templates for policy diff analysis."""

    # Semantic change analysis
    CHANGE_ANALYSIS = PromptTemplate(
        template="""You are an expert policy analyst. Analyze the following change in a policy document.

ORIGINAL TEXT:
{text_before}

MODIFIED TEXT:
{text_after}

{context_section}

Provide your analysis in JSON format:
{{
    "significance": "critical|high|medium|low|none",
    "confidence": 0.0-1.0,
    "categories": ["coverage|exclusion|limit|definition|obligation|permission|condition|formatting|restructure|other"],
    "explanation": "Brief explanation of what changed",
    "business_impact": "Impact on policyholder or business",
    "requires_review": true/false,
    "regulatory_impact": "Any regulatory implications or null"
}}

Significance levels:
- CRITICAL: Material change affecting rights, coverage amounts, or legal obligations
- HIGH: Significant change requiring stakeholder review
- MEDIUM: Notable change that may need attention
- LOW: Minor change, likely cosmetic or clarifying
- NONE: No semantic change (formatting/rewording only)

Respond ONLY with the JSON object.""",
        description="Analyzes a single change for semantic significance",
        required_vars=["text_before", "text_after", "context_section"],
    )

    # Batch analysis
    BATCH_ANALYSIS = PromptTemplate(
        template="""You are an expert policy analyst. Analyze the following changes in a policy document.

{changes_section}

For EACH change, provide analysis in this JSON array format:
[
    {{
        "change_id": "1",
        "significance": "critical|high|medium|low|none",
        "confidence": 0.0-1.0,
        "categories": ["category1", "category2"],
        "explanation": "Brief explanation",
        "business_impact": "Impact description",
        "requires_review": true/false
    }},
    ...
]

Respond ONLY with the JSON array.""",
        description="Analyzes multiple changes in a single request",
        required_vars=["changes_section"],
    )

    # Executive summary
    EXECUTIVE_SUMMARY = PromptTemplate(
        template="""You are an expert policy analyst. Create an executive summary of the following policy changes.

DOCUMENT: {document_name}
TOTAL CHANGES: {total_changes}
CRITICAL CHANGES: {critical_changes}
HIGH PRIORITY CHANGES: {high_changes}

KEY CHANGES:
{key_changes}

Write a concise executive summary (2-3 paragraphs) that:
1. Highlights the most significant changes
2. Explains business impact
3. Recommends priority actions

Be specific and actionable. Use plain language suitable for executives.""",
        description="Generates executive summary of changes",
        required_vars=[
            "document_name",
            "total_changes",
            "critical_changes",
            "high_changes",
            "key_changes",
        ],
    )

    # Change comparison
    COMPARE_CHANGES = PromptTemplate(
        template="""Compare these two policy excerpts and explain the key differences:

POLICY A ({policy_a_name}):
{policy_a_text}

POLICY B ({policy_b_name}):
{policy_b_text}

Provide:
1. Summary of differences
2. Which policy is more favorable to the policyholder
3. Specific clauses that differ
4. Recommendations""",
        description="Compares two policy versions",
        required_vars=["policy_a_name", "policy_a_text", "policy_b_name", "policy_b_text"],
    )

    # Coverage analysis
    COVERAGE_ANALYSIS = PromptTemplate(
        template="""Analyze this policy coverage change:

BEFORE:
{text_before}

AFTER:
{text_after}

Determine:
1. Is coverage expanded or reduced?
2. What specific events/conditions are affected?
3. Are there new exclusions or limitations?
4. Quantify any changes to limits or deductibles
5. Rate the impact: BENEFICIAL / NEUTRAL / ADVERSE for policyholder""",
        description="Analyzes coverage-specific changes",
        required_vars=["text_before", "text_after"],
    )

    # Exclusion analysis
    EXCLUSION_ANALYSIS = PromptTemplate(
        template="""Analyze this policy exclusion change:

BEFORE:
{text_before}

AFTER:
{text_after}

Determine:
1. Are exclusions being added, removed, or modified?
2. What specific scenarios are now excluded or included?
3. How might this affect claims?
4. Are there any ambiguities in the new language?
5. Regulatory compliance considerations""",
        description="Analyzes exclusion-specific changes",
        required_vars=["text_before", "text_after"],
    )

    # Definition analysis
    DEFINITION_ANALYSIS = PromptTemplate(
        template="""Analyze this policy definition change:

TERM: {term}

OLD DEFINITION:
{definition_before}

NEW DEFINITION:
{definition_after}

Determine:
1. How has the scope of the term changed?
2. What clauses in the policy might be affected?
3. Are there interpretation risks?
4. Impact on claims processing
5. Comparison to industry standard definitions""",
        description="Analyzes definition changes",
        required_vars=["term", "definition_before", "definition_after"],
    )

    @classmethod
    def get_analysis_prompt(
        cls,
        text_before: str,
        text_after: str,
        context: Optional[str] = None,
    ) -> str:
        """Get formatted analysis prompt.

        Args:
            text_before: Original text
            text_after: Modified text
            context: Optional context

        Returns:
            Formatted prompt
        """
        context_section = ""
        if context:
            context_section = f"CONTEXT:\n{context}\n"

        return cls.CHANGE_ANALYSIS.format(
            text_before=text_before or "[REMOVED]",
            text_after=text_after or "[ADDED]",
            context_section=context_section,
        )

    @classmethod
    def get_batch_prompt(
        cls,
        changes: list[tuple[str, str, str]],  # (id, before, after)
    ) -> str:
        """Get formatted batch analysis prompt.

        Args:
            changes: List of (change_id, text_before, text_after)

        Returns:
            Formatted prompt
        """
        changes_parts = []
        for change_id, before, after in changes:
            changes_parts.append(
                f"Change {change_id}:\nBEFORE: {before or '[REMOVED]'}\nAFTER: {after or '[ADDED]'}\n"
            )

        return cls.BATCH_ANALYSIS.format(changes_section="\n".join(changes_parts))

    @classmethod
    def get_summary_prompt(
        cls,
        document_name: str,
        total_changes: int,
        critical_changes: int,
        high_changes: int,
        key_changes: list[str],
    ) -> str:
        """Get formatted executive summary prompt.

        Args:
            document_name: Name of document
            total_changes: Total number of changes
            critical_changes: Number of critical changes
            high_changes: Number of high priority changes
            key_changes: List of key change descriptions

        Returns:
            Formatted prompt
        """
        return cls.EXECUTIVE_SUMMARY.format(
            document_name=document_name,
            total_changes=total_changes,
            critical_changes=critical_changes,
            high_changes=high_changes,
            key_changes="\n".join(f"• {c}" for c in key_changes),
        )

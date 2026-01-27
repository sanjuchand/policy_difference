# Policy Diff Application - Enterprise Architecture

## Executive Summary

An enterprise-grade document comparison platform for policy documents that provides secure, scalable, and auditable diff capabilities with support for high-volume processing, multi-tenancy, and compliance requirements.

---

## GenAI Problem Statement

### Why Policy Diff is Hard

Policy document comparison is a deceptively complex problem that traditional text diff tools fail to solve adequately.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     THE POLICY DIFF CHALLENGE                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Traditional Diff Tools See This:                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │  - "The coverage limit shall not exceed $500,000"                           │   │
│  │  + "Coverage limits will not be greater than $500,000.00"                   │   │
│  │                                                                              │   │
│  │  Result: 🔴 15 characters changed - SIGNIFICANT DIFFERENCE                  │   │
│  │                                                                              │   │
│  │  Reality: 🟢 Semantically IDENTICAL - just rewording                        │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  Meanwhile, Traditional Diff Tools Miss This:                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │  - "Coverage includes all employees"                                        │   │
│  │  + "Coverage includes all full-time employees"                              │   │
│  │                                                                              │   │
│  │  Result: 🟡 2 words added - MINOR CHANGE                                    │   │
│  │                                                                              │   │
│  │  Reality: 🔴 CRITICAL - Excludes part-time workers from coverage!           │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### The Core Challenges

| Challenge | Description | Why It's Hard |
|-----------|-------------|---------------|
| **Semantic Equivalence** | Different words, same meaning | "shall" ≈ "will" ≈ "must" in legal context |
| **Context Dependency** | Meaning depends on surrounding text | "30 days" means different things in different clauses |
| **Structural Variance** | Same content, different organization | Sections reordered, lists reformatted |
| **Legal Precision** | Single word changes matter enormously | "and" vs "or" can flip entire meaning |
| **Cross-References** | Changes ripple through document | Definition change affects every usage |
| **Implicit Changes** | What's removed is as important as what's added | Missing exclusion = expanded coverage |
| **Domain Knowledge** | Understanding requires expertise | "Material adverse change" has specific legal meaning |

#### Real-World Examples of Diff Complexity

```
┌─────────────────────────────────────────────────────────────────┐
│           Examples: Why Traditional Diff Fails                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EXAMPLE 1: False Positive (Noise)                              │
│  ─────────────────────────────────                              │
│  Before: "Payment shall be made within thirty (30) days"        │
│  After:  "Payment will be made within 30 days"                  │
│                                                                  │
│  Text diff: 6 changes detected                                  │
│  Semantic diff: NO CHANGE (identical meaning)                   │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  EXAMPLE 2: False Negative (Missed Critical Change)             │
│  ─────────────────────────────────────────────────              │
│  Before: "Claims must be filed within 90 days"                  │
│  After:  "Claims must be filed within 30 days"                  │
│                                                                  │
│  Text diff: 1 character changed (9→3)                           │
│  Semantic diff: CRITICAL (60-day reduction in filing window!)   │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  EXAMPLE 3: Structural Change (Reorganization)                  │
│  ─────────────────────────────────────────────                  │
│  Before: Section 4.1, 4.2, 4.3 contain coverage details         │
│  After:  Same content now in Section 5.1, 5.2, 5.3              │
│                                                                  │
│  Text diff: MASSIVE changes (all section numbers different)     │
│  Semantic diff: NO CHANGE (content moved, not modified)         │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  EXAMPLE 4: Subtle Scope Change                                 │
│  ───────────────────────────────                                │
│  Before: "This policy covers damage caused by fire"             │
│  After:  "This policy covers direct damage caused by fire"      │
│                                                                  │
│  Text diff: 1 word added                                        │
│  Semantic diff: SIGNIFICANT (excludes indirect/consequential)   │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  EXAMPLE 5: Negation Insertion                                  │
│  ───────────────────────────────                                │
│  Before: "Pre-existing conditions are covered after 12 months"  │
│  After:  "Pre-existing conditions are not covered"              │
│                                                                  │
│  Text diff: Minor edit                                          │
│  Semantic diff: COMPLETE REVERSAL of coverage!                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### The Business Impact

```
┌─────────────────────────────────────────────────────────────────┐
│              Cost of Getting Policy Diff Wrong                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FALSE NEGATIVES (Missed Changes):                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Undetected coverage reduction → Claim denials       │     │
│  │  • Missed premium changes → Revenue/cost surprises     │     │
│  │  • Overlooked exclusions → Unexpected liability        │     │
│  │  • Regulatory non-compliance → Fines, sanctions        │     │
│  │                                                         │     │
│  │  Real Example: A missed "not" in a coverage clause     │     │
│  │  resulted in $2.3M in unexpected claim payouts         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  FALSE POSITIVES (Alert Fatigue):                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • 500+ "changes" per document review                  │     │
│  │  • Reviewers skip/skim due to noise                    │     │
│  │  • Real changes buried in formatting noise             │     │
│  │  • Review time: 4-6 hours per policy pair              │     │
│  │                                                         │     │
│  │  Real Example: Legal team ignores diff reports because │     │
│  │  95% of flagged changes are meaningless formatting     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CURRENT STATE (Manual Review):                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Average policy: 50-200 pages                        │     │
│  │  • Manual comparison: 4-8 hours per pair               │     │
│  │  • Error rate: 15-20% of significant changes missed    │     │
│  │  • Cost: $200-500 per policy review                    │     │
│  │  • Scalability: Cannot keep pace with volume           │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Why Semantic Diff is Required

Traditional diff operates at the **syntactic** level (characters, words, lines). Policy comparison requires **semantic** understanding—comparing meaning, not text.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    SYNTACTIC vs SEMANTIC DIFF                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────────────┐  │
│  │      SYNTACTIC DIFF             │  │         SEMANTIC DIFF                   │  │
│  │      (Traditional)              │  │         (AI-Powered)                    │  │
│  ├─────────────────────────────────┤  ├─────────────────────────────────────────┤  │
│  │                                 │  │                                          │  │
│  │  Compares: Characters/Words     │  │  Compares: Meaning/Intent               │  │
│  │                                 │  │                                          │  │
│  │  "shall" → "will"              │  │  "shall" → "will"                       │  │
│  │  Result: CHANGED               │  │  Result: EQUIVALENT (legal synonyms)    │  │
│  │                                 │  │                                          │  │
│  │  "$1,000,000" → "$1M"          │  │  "$1,000,000" → "$1M"                   │  │
│  │  Result: CHANGED               │  │  Result: EQUIVALENT (same value)        │  │
│  │                                 │  │                                          │  │
│  │  "is covered" → "is not covered"│ │  "is covered" → "is not covered"        │  │
│  │  Result: 4 chars added          │  │  Result: CRITICAL (negation reversal)  │  │
│  │                                 │  │                                          │  │
│  │  ─────────────────────────────  │  │  ──────────────────────────────────────│  │
│  │  Strengths:                     │  │  Strengths:                             │  │
│  │  ✓ Fast                        │  │  ✓ Understands meaning                  │  │
│  │  ✓ Deterministic               │  │  ✓ Filters noise                        │  │
│  │  ✓ No false negatives*         │  │  ✓ Catches subtle changes              │  │
│  │                                 │  │  ✓ Prioritizes by significance         │  │
│  │  Weaknesses:                    │  │                                          │  │
│  │  ✗ Massive false positives     │  │  Weaknesses:                            │  │
│  │  ✗ No context awareness        │  │  ✗ Requires careful implementation     │  │
│  │  ✗ Cannot prioritize           │  │  ✗ Probabilistic (needs thresholds)    │  │
│  │  ✗ Misses meaning changes      │  │  ✗ Computationally expensive           │  │
│  │                                 │  │                                          │  │
│  └─────────────────────────────────┘  └─────────────────────────────────────────┘  │
│                                                                                      │
│  * Syntactic diff catches all text changes but cannot distinguish important ones    │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### What Semantic Diff Must Understand

```
┌─────────────────────────────────────────────────────────────────┐
│           Semantic Understanding Requirements                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LINGUISTIC EQUIVALENCE                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Recognize that these pairs mean the same thing:        │     │
│  │                                                         │     │
│  │  • "shall not exceed" ≈ "must not be greater than"     │     │
│  │  • "prior to" ≈ "before"                               │     │
│  │  • "in the event that" ≈ "if"                          │     │
│  │  • "notwithstanding" ≈ "despite" ≈ "regardless of"     │     │
│  │  • "30 days" ≈ "thirty (30) days" ≈ "one month"        │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. NUMERICAL REASONING                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Understand magnitude and impact:                       │     │
│  │                                                         │     │
│  │  • $500,000 → $1,000,000 (100% increase - SIGNIFICANT) │     │
│  │  • $500,000 → $500,000.00 (formatting only - IGNORE)   │     │
│  │  • 90 days → 30 days (67% reduction - CRITICAL)        │     │
│  │  • 10% → 10.0% (no change - IGNORE)                    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. LOGICAL RELATIONSHIPS                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Detect changes in logical structure:                   │     │
│  │                                                         │     │
│  │  • "A and B" → "A or B" (CRITICAL - different logic)   │     │
│  │  • "must" → "may" (CRITICAL - obligation → permission) │     │
│  │  • "all" → "some" (SIGNIFICANT - scope reduction)      │     │
│  │  • "included" → "excluded" (CRITICAL - reversal)       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  4. DOMAIN KNOWLEDGE                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Apply industry-specific understanding:                 │     │
│  │                                                         │     │
│  │  • "Occurrence" vs "Claims-made" (insurance types)     │     │
│  │  • "Material adverse change" (legal significance)      │     │
│  │  • "Force majeure" (contract implications)             │     │
│  │  • "Deductible" vs "Co-pay" (different mechanisms)     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  5. CONTEXTUAL INTERPRETATION                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Same words, different meaning based on context:        │     │
│  │                                                         │     │
│  │  • "30 days" in claims filing (deadline)               │     │
│  │  • "30 days" in cancellation (notice period)           │     │
│  │  • "30 days" in payment terms (billing cycle)          │     │
│  │                                                         │     │
│  │  Changing any of these has different business impact   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Why LLMs Help

Large Language Models bring capabilities that make semantic diff possible at scale.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         LLM CAPABILITIES FOR POLICY DIFF                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                     WHAT LLMs BRING TO THE TABLE                             │   │
│  │                                                                              │   │
│  │  1. NATURAL LANGUAGE UNDERSTANDING                                          │   │
│  │     ├── Pre-trained on massive legal/business corpora                       │   │
│  │     ├── Understands synonyms, paraphrases, idioms                          │   │
│  │     ├── Recognizes legal terminology and conventions                        │   │
│  │     └── Handles complex sentence structures                                 │   │
│  │                                                                              │   │
│  │  2. CONTEXTUAL REASONING                                                    │   │
│  │     ├── Considers surrounding text when evaluating changes                  │   │
│  │     ├── Understands how definitions affect usage                           │   │
│  │     ├── Recognizes cross-references and dependencies                        │   │
│  │     └── Evaluates cumulative impact of multiple changes                    │   │
│  │                                                                              │   │
│  │  3. SEMANTIC SIMILARITY                                                     │   │
│  │     ├── Embeddings capture meaning, not just words                         │   │
│  │     ├── Cluster similar clauses across documents                           │   │
│  │     ├── Detect paraphrased content                                         │   │
│  │     └── Identify structural reorganization                                  │   │
│  │                                                                              │   │
│  │  4. GENERATIVE EXPLANATION                                                  │   │
│  │     ├── Explain WHY a change is significant                                │   │
│  │     ├── Summarize impact in plain language                                 │   │
│  │     ├── Generate recommended actions                                        │   │
│  │     └── Produce human-readable diff reports                                │   │
│  │                                                                              │   │
│  │  5. FEW-SHOT LEARNING                                                       │   │
│  │     ├── Adapt to organization-specific terminology                         │   │
│  │     ├── Learn from human feedback quickly                                  │   │
│  │     ├── Handle new policy types without retraining                         │   │
│  │     └── Incorporate domain expert knowledge via prompts                    │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### LLM-Powered Analysis Examples

```
┌─────────────────────────────────────────────────────────────────┐
│           LLM Analysis vs Traditional Diff                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT:                                                          │
│  ─────                                                          │
│  Before: "Benefits are payable for covered services rendered    │
│           by network providers"                                  │
│  After:  "Benefits may be payable for covered services rendered │
│           by in-network providers, subject to prior approval"   │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  TRADITIONAL DIFF OUTPUT:                                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  - "Benefits are payable for covered services rendered │     │
│  │  -  by network providers"                              │     │
│  │  + "Benefits may be payable for covered services rendered│    │
│  │  +  by in-network providers, subject to prior approval"│     │
│  │                                                         │     │
│  │  Changes: 4 words modified, 5 words added              │     │
│  │  Assessment: MODERATE CHANGE                           │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  LLM SEMANTIC ANALYSIS:                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  SIGNIFICANCE: 🔴 CRITICAL                             │     │
│  │                                                         │     │
│  │  CHANGES DETECTED:                                      │     │
│  │                                                         │     │
│  │  1. Obligation Weakened                                │     │
│  │     "are payable" → "may be payable"                   │     │
│  │     Impact: Benefits changed from guaranteed to        │     │
│  │             discretionary                              │     │
│  │                                                         │     │
│  │  2. New Restriction Added                              │     │
│  │     "subject to prior approval"                        │     │
│  │     Impact: Administrative barrier to receiving        │     │
│  │             benefits; claims can be denied retroactively│    │
│  │                                                         │     │
│  │  3. Terminology Clarification (Minor)                  │     │
│  │     "network" → "in-network"                           │     │
│  │     Impact: Cosmetic; standard industry term           │     │
│  │                                                         │     │
│  │  BUSINESS IMPACT:                                       │     │
│  │  This change fundamentally alters the coverage promise.│     │
│  │  Policyholders no longer have guaranteed benefits;     │     │
│  │  the insurer now has discretion and can require        │     │
│  │  pre-approval before any service.                      │     │
│  │                                                         │     │
│  │  RECOMMENDED ACTION: Legal review required             │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Why Naive LLM Use is Dangerous

Simply sending documents to an LLM API creates serious risks. This section explains why careful architecture is essential.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        DANGERS OF NAIVE LLM IMPLEMENTATION                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│                           ⚠️  WARNING: CRITICAL RISKS  ⚠️                           │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │   NAIVE APPROACH:                                                           │   │
│  │   ┌──────────────────────────────────────────────────────────────────┐     │   │
│  │   │                                                                   │     │   │
│  │   │   policy_a = read_pdf("policy_v1.pdf")                           │     │   │
│  │   │   policy_b = read_pdf("policy_v2.pdf")                           │     │   │
│  │   │                                                                   │     │   │
│  │   │   response = openai.chat.completions.create(                     │     │   │
│  │   │       model="gpt-4",                                             │     │   │
│  │   │       messages=[{                                                │     │   │
│  │   │           "role": "user",                                        │     │   │
│  │   │           "content": f"Compare these policies: {policy_a} vs {policy_b}"│ │   │
│  │   │       }]                                                         │     │   │
│  │   │   )                                                              │     │   │
│  │   │                                                                   │     │   │
│  │   │   return response.choices[0].message.content                     │     │   │
│  │   │                                                                   │     │   │
│  │   └──────────────────────────────────────────────────────────────────┘     │   │
│  │                                                                              │   │
│  │   THIS IS DANGEROUS. HERE'S WHY:                                           │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Risk 1: PII and Confidential Data Exposure

```
┌─────────────────────────────────────────────────────────────────┐
│     RISK 1: Sensitive Data Sent to External LLM Providers       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Policy documents contain:                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  • Names, addresses, SSNs of policyholders             │     │
│  │  • Medical information (PHI under HIPAA)               │     │
│  │  • Financial data (account numbers, salaries)          │     │
│  │  • Proprietary business terms                          │     │
│  │  • Trade secrets in commercial policies                │     │
│  │  • Attorney-client privileged content                  │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  When sent to external LLM:                                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ❌ Data may be logged by provider                     │     │
│  │  ❌ Data may be used for model training                │     │
│  │  ❌ Data transits public internet                      │     │
│  │  ❌ Data stored in provider's infrastructure           │     │
│  │  ❌ No control over data residency                     │     │
│  │  ❌ Violates HIPAA, GDPR, CCPA, SOX...                 │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CONSEQUENCE:                                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  "Company fined $4.2M for sending customer health data │     │
│  │   to ChatGPT without consent" - Hypothetical headline  │     │
│  │   that WILL become real if you're not careful          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  MITIGATION (Implemented in this architecture):                 │
│  ├── PII detection and sanitization before LLM                  │
│  ├── Tokenization (replace PII with placeholders)               │
│  ├── Self-hosted LLM option for sensitive data                  │
│  ├── LLM proxy gateway with content filtering                   │
│  └── Audit trail of all data sent to LLMs                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Risk 2: Hallucination and Fabrication

```
┌─────────────────────────────────────────────────────────────────┐
│         RISK 2: LLM Hallucinations in Legal Context             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LLMs can confidently generate FALSE information:               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  EXAMPLE HALLUCINATION:                                 │     │
│  │                                                         │     │
│  │  User: "What changed in Section 4.2?"                  │     │
│  │                                                         │     │
│  │  LLM: "Section 4.2 now includes a new sub-limit of    │     │
│  │        $50,000 for cyber liability coverage."          │     │
│  │                                                         │     │
│  │  Reality: Section 4.2 has no mention of cyber          │     │
│  │           liability. The LLM fabricated this.          │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Why this happens:                                               │
│  ├── LLM has seen similar policies in training                  │
│  ├── Pattern-matches to common policy structures                │
│  ├── Generates plausible-sounding but false content             │
│  └── No grounding to actual document content                    │
│                                                                  │
│  CONSEQUENCE:                                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Legal team relies on AI-generated diff report.        │     │
│  │  Report contains hallucinated clause.                  │     │
│  │  Contract signed based on false information.           │     │
│  │  Litigation ensues when hallucinated coverage doesn't  │     │
│  │  exist.                                                 │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  MITIGATION (Implemented in this architecture):                 │
│  ├── RAG grounding (LLM only sees actual document content)      │
│  ├── Citation requirements (must reference source text)         │
│  ├── Confidence scoring with thresholds                         │
│  ├── Human-in-the-loop verification                             │
│  └── Structured output validation                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Risk 3: Inconsistent and Non-Deterministic Results

```
┌─────────────────────────────────────────────────────────────────┐
│           RISK 3: Non-Deterministic Behavior                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Same input, different outputs:                                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  RUN 1:                                                 │     │
│  │  "The change from 'shall' to 'will' is significant     │     │
│  │   as it weakens the contractual obligation."           │     │
│  │                                                         │     │
│  │  RUN 2 (same input):                                   │     │
│  │  "The change from 'shall' to 'will' is cosmetic        │     │
│  │   with no practical legal difference."                 │     │
│  │                                                         │     │
│  │  RUN 3 (same input):                                   │     │
│  │  "I found 3 changes in this section..."                │     │
│  │  (Completely different response structure)             │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Problems:                                                       │
│  ├── Cannot reproduce results for audit                         │
│  ├── Different reviewers get different reports                  │
│  ├── No baseline for comparison                                 │
│  ├── Impossible to validate systematically                      │
│  └── Legal/compliance implications of inconsistency             │
│                                                                  │
│  MITIGATION (Implemented in this architecture):                 │
│  ├── Temperature=0 for deterministic outputs                    │
│  ├── Structured output schemas (JSON mode)                      │
│  ├── Seed parameters for reproducibility                        │
│  ├── Caching layer for identical inputs                         │
│  ├── Ensemble approaches for critical decisions                 │
│  └── Version-locked model deployments                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Risk 4: Context Window and Chunking Failures

```
┌─────────────────────────────────────────────────────────────────┐
│         RISK 4: Document Too Large for Context Window           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  The problem:                                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Typical policy document:     150 pages = ~75,000 tokens│    │
│  │  Two documents for comparison: ~150,000 tokens         │     │
│  │  GPT-4 context window:        128,000 tokens           │     │
│  │  Claude context window:       200,000 tokens           │     │
│  │                                                         │     │
│  │  Even with large context, comparing full documents     │     │
│  │  is expensive and degrades quality at the edges.       │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Naive chunking causes:                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ❌ Cross-reference breaks                             │     │
│  │     "As defined in Section 2.1" - but Section 2.1     │     │
│  │     is in a different chunk                            │     │
│  │                                                         │     │
│  │  ❌ Context loss                                       │     │
│  │     A clause's meaning depends on the definition       │     │
│  │     section, which was in chunk 1 (now in chunk 5)     │     │
│  │                                                         │     │
│  │  ❌ Boundary artifacts                                 │     │
│  │     Sentence split across chunks = misinterpretation   │     │
│  │                                                         │     │
│  │  ❌ Missed holistic changes                            │     │
│  │     Pattern of small changes across document missed    │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  MITIGATION (Implemented in this architecture):                 │
│  ├── Hierarchical chunking (section-aware boundaries)           │
│  ├── Overlapping chunks with context preservation               │
│  ├── Definition extraction and injection                        │
│  ├── Cross-reference resolution before chunking                 │
│  ├── Multi-pass analysis (local then global)                    │
│  └── RAG for retrieving relevant context                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Risk 5: Lack of Auditability and Explainability

```
┌─────────────────────────────────────────────────────────────────┐
│         RISK 5: Black Box Decision Making                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Regulatory requirement:                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  "Explain why this change was flagged as significant"  │     │
│  │                                                         │     │
│  │  Naive LLM response: "The AI determined this was       │     │
│  │  significant based on its analysis."                   │     │
│  │                                                         │     │
│  │  Regulator: "That's not acceptable. Show your work."   │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Problems:                                                       │
│  ├── Cannot explain WHY a decision was made                     │
│  ├── No audit trail for compliance                              │
│  ├── Cannot justify decisions in litigation                     │
│  ├── Model updates change behavior unpredictably                │
│  └── No way to prove due diligence                              │
│                                                                  │
│  MITIGATION (Implemented in this architecture):                 │
│  ├── Structured reasoning chains in prompts                     │
│  ├── Citation requirements for every claim                      │
│  ├── Confidence scores with calibration                         │
│  ├── Human review audit trail                                   │
│  ├── Model versioning and reproducibility                       │
│  ├── Explanation generation alongside decisions                 │
│  └── Complete request/response logging (sanitized)              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Risk 6: Cost Explosion

```
┌─────────────────────────────────────────────────────────────────┐
│                    RISK 6: Runaway Costs                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Cost calculation for naive approach:                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Per comparison:                                        │     │
│  │  ├── 2 documents × 75,000 tokens = 150,000 input tokens│     │
│  │  ├── Output: ~5,000 tokens                             │     │
│  │  ├── GPT-4 Turbo: $0.01/1K in + $0.03/1K out          │     │
│  │  ├── Cost per comparison: ~$1.65                       │     │
│  │  │                                                      │     │
│  │  At scale:                                              │     │
│  │  ├── 1,000 comparisons/day = $1,650/day               │     │
│  │  ├── Monthly cost: ~$50,000                            │     │
│  │  ├── With retries/errors: ~$75,000                     │     │
│  │  │                                                      │     │
│  │  Hidden costs:                                          │     │
│  │  ├── Re-runs for non-deterministic failures           │     │
│  │  ├── Iterative refinement prompts                      │     │
│  │  ├── Context stuffing attempts                         │     │
│  │  └── No caching = duplicate processing                 │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  MITIGATION (Implemented in this architecture):                 │
│  ├── Tiered processing (rule-based first, LLM for complex)      │
│  ├── Intelligent chunking (only compare changed sections)       │
│  ├── Caching layer for repeated comparisons                     │
│  ├── Self-hosted models for high-volume workloads               │
│  ├── Model routing (smaller models for simple tasks)            │
│  └── Token budget management per request                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Summary: The Right Approach

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    NAIVE vs PRODUCTION-READY LLM IMPLEMENTATION                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌────────────────────────────────┐  ┌────────────────────────────────────────┐    │
│  │   ❌ NAIVE APPROACH            │  │   ✓ PRODUCTION APPROACH                │    │
│  ├────────────────────────────────┤  ├────────────────────────────────────────┤    │
│  │                                │  │                                         │    │
│  │ Send raw documents to API     │  │ PII detection & sanitization           │    │
│  │                                │  │                                         │    │
│  │ Trust LLM output directly      │  │ RAG grounding + citation required      │    │
│  │                                │  │                                         │    │
│  │ Use external API for all data │  │ Self-hosted for sensitive, external    │    │
│  │                                │  │ for sanitized                           │    │
│  │                                │  │                                         │    │
│  │ No output validation          │  │ Structured output + confidence scores  │    │
│  │                                │  │                                         │    │
│  │ Manual prompt engineering      │  │ Systematic evaluation framework        │    │
│  │                                │  │                                         │    │
│  │ Hope for consistency          │  │ Deterministic config + caching         │    │
│  │                                │  │                                         │    │
│  │ No audit trail                │  │ Complete observability + audit         │    │
│  │                                │  │                                         │    │
│  │ Unlimited API calls           │  │ Cost management + tiered processing    │    │
│  │                                │  │                                         │    │
│  │ Ship and pray                 │  │ Human-in-the-loop + continuous         │    │
│  │                                │  │ improvement                             │    │
│  │                                │  │                                         │    │
│  └────────────────────────────────┘  └────────────────────────────────────────┘    │
│                                                                                      │
│  This architecture implements all production-ready patterns.                        │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## AI Design Decisions & Tradeoffs

This section documents the key architectural decisions for AI components, explaining the reasoning behind each choice and the tradeoffs involved.

### Decision 1: Why Embeddings Over Direct GPT Comparison

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│              EMBEDDINGS vs DIRECT LLM COMPARISON                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  TWO APPROACHES TO SEMANTIC COMPARISON:                                             │
│                                                                                      │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────────────┐  │
│  │   APPROACH A: Direct LLM        │  │   APPROACH B: Embeddings + LLM          │  │
│  │   (Send full docs to GPT)       │  │   (Hybrid architecture)                 │  │
│  ├─────────────────────────────────┤  ├─────────────────────────────────────────┤  │
│  │                                 │  │                                          │  │
│  │   Doc A ──┐                     │  │   Doc A ──▶ Embed ──▶ ┌────────────┐   │  │
│  │           ├──▶ GPT ──▶ Result   │  │                       │  Vector    │   │  │
│  │   Doc B ──┘                     │  │   Doc B ──▶ Embed ──▶ │  Similarity│   │  │
│  │                                 │  │                       └─────┬──────┘   │  │
│  │                                 │  │                             │          │  │
│  │                                 │  │                             ▼          │  │
│  │                                 │  │                    Only changed sections│  │
│  │                                 │  │                             │          │  │
│  │                                 │  │                             ▼          │  │
│  │                                 │  │                     LLM for analysis   │  │
│  │                                 │  │                                          │  │
│  └─────────────────────────────────┘  └─────────────────────────────────────────┘  │
│                                                                                      │
│  ✓ WE CHOSE: APPROACH B (Embeddings + Selective LLM)                               │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Comparison Matrix

| Factor | Direct LLM | Embeddings + LLM | Winner |
|--------|-----------|------------------|--------|
| **Cost per comparison** | $1.50-3.00 (150K tokens) | $0.05-0.30 (targeted) | Embeddings |
| **Latency** | 30-60 seconds | 2-5 seconds (parallel) | Embeddings |
| **Scalability** | Poor (API limits) | Excellent (local compute) | Embeddings |
| **Determinism** | Low (LLM variability) | High (cosine similarity) | Embeddings |
| **Context window** | Limited (128K-200K) | Unlimited (chunked) | Embeddings |
| **Change localization** | Approximate | Precise (character-level) | Embeddings |
| **Semantic depth** | Excellent | Good + LLM for complex | Tie |
| **Explainability** | Variable | Quantified similarity | Embeddings |

#### How the Hybrid Approach Works

```
┌─────────────────────────────────────────────────────────────────┐
│           Embeddings + Selective LLM Pipeline                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STAGE 1: Embedding-Based Change Detection (Fast, Cheap)        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  1. Chunk both documents into sections                  │     │
│  │  2. Generate embeddings for each chunk                  │     │
│  │  3. Compute pairwise cosine similarity                  │     │
│  │  4. Flag sections with similarity < 0.95 as "changed"   │     │
│  │                                                         │     │
│  │  Result: 85% of sections marked "unchanged" → SKIP LLM  │     │
│  │          15% of sections marked "changed" → ANALYZE     │     │
│  │                                                         │     │
│  │  Cost: ~$0.002 per document (embedding only)            │     │
│  │  Time: <1 second                                        │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  STAGE 2: LLM Analysis (Only for Changed Sections)              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  For each changed section:                              │     │
│  │  1. Retrieve section from both documents                │     │
│  │  2. Add context (definitions, cross-references)         │     │
│  │  3. Send to LLM for semantic analysis                   │     │
│  │  4. Get structured significance assessment              │     │
│  │                                                         │     │
│  │  Input: ~2,000 tokens (section + context)              │     │
│  │  vs Direct approach: ~150,000 tokens (full documents)  │     │
│  │                                                         │     │
│  │  Cost savings: 75x reduction in LLM tokens             │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  STAGE 3: Rule-Based Post-Processing                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Apply deterministic rules to LLM output:               │     │
│  │  • Numerical change detection (regex + math)           │     │
│  │  • Negation detection ("not" insertion/removal)        │     │
│  │  • Known false positive filtering                      │     │
│  │                                                         │     │
│  │  Purpose: Catch what LLM might miss, reduce FN         │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Why Not Pure Embeddings?

```
┌─────────────────────────────────────────────────────────────────┐
│         Embeddings Alone Are Insufficient                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Embeddings detect THAT something changed, not WHAT it means:   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Example:                                               │     │
│  │                                                         │     │
│  │  Text A: "Coverage limit is $500,000"                  │     │
│  │  Text B: "Coverage limit is $5,000,000"                │     │
│  │                                                         │     │
│  │  Embedding similarity: 0.97 (very similar!)            │     │
│  │  Semantic reality: 10x increase in coverage            │     │
│  │                                                         │     │
│  │  ─────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  Text A: "Claims must be filed within 90 days"         │     │
│  │  Text B: "Claims must be filed within 30 days"         │     │
│  │                                                         │     │
│  │  Embedding similarity: 0.98 (nearly identical!)        │     │
│  │  Semantic reality: 67% reduction in filing window      │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CONCLUSION: Embeddings for detection, LLM for interpretation   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Decision 2: Why Tokenization Over Redaction

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    TOKENIZATION vs REDACTION                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  When protecting PII before LLM processing, two main approaches:                    │
│                                                                                      │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────────────┐  │
│  │   REDACTION                     │  │   TOKENIZATION                          │  │
│  │   (Remove/replace with labels)  │  │   (Replace with reversible tokens)      │  │
│  ├─────────────────────────────────┤  ├─────────────────────────────────────────┤  │
│  │                                 │  │                                          │  │
│  │  Before:                        │  │  Before:                                 │  │
│  │  "John Smith (SSN: 123-45-6789) │  │  "John Smith (SSN: 123-45-6789)         │  │
│  │   lives at 123 Main St"         │  │   lives at 123 Main St"                 │  │
│  │                                 │  │                                          │  │
│  │  After:                         │  │  After:                                  │  │
│  │  "[REDACTED] (SSN: [REDACTED])  │  │  "[PERSON_1] (SSN: [SSN_1])             │  │
│  │   lives at [REDACTED]"          │  │   lives at [ADDR_1]"                    │  │
│  │                                 │  │                                          │  │
│  │  Recovery: ❌ IMPOSSIBLE        │  │  Recovery: ✓ Via token vault            │  │
│  │                                 │  │                                          │  │
│  └─────────────────────────────────┘  └─────────────────────────────────────────┘  │
│                                                                                      │
│  ✓ WE CHOSE: TOKENIZATION                                                          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Why Tokenization Wins for Policy Diff

| Requirement | Redaction | Tokenization | Winner |
|-------------|-----------|--------------|--------|
| **Diff comparison accuracy** | Poor - loses entity identity | Good - consistent placeholders | Tokenization |
| **LLM context preservation** | Poor - "[REDACTED]" provides no info | Good - "[PERSON_1]" maintains reference | Tokenization |
| **Result reconstruction** | Impossible | Full fidelity | Tokenization |
| **Cross-document entity linking** | Broken | Preserved | Tokenization |
| **PII protection** | Excellent | Excellent | Tie |
| **Audit trail** | Complete removal | Token → value mapping logged | Tokenization |

#### The Critical Diff Use Case

```
┌─────────────────────────────────────────────────────────────────┐
│         Why Tokenization Matters for Diff                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SCENARIO: Person's address changed between policy versions      │
│                                                                  │
│  WITH REDACTION:                                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Doc A: "[REDACTED] lives at [REDACTED]"               │     │
│  │  Doc B: "[REDACTED] lives at [REDACTED]"               │     │
│  │                                                         │     │
│  │  LLM sees: No difference (both are [REDACTED])         │     │
│  │  Reality: Address changed from 123 Main to 456 Oak     │     │
│  │                                                         │     │
│  │  ❌ CRITICAL CHANGE MISSED                             │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  WITH TOKENIZATION:                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Doc A: "[PERSON_1] lives at [ADDR_1]"                 │     │
│  │  Doc B: "[PERSON_1] lives at [ADDR_2]"                 │     │
│  │                                                         │     │
│  │  LLM sees: [ADDR_1] → [ADDR_2] (address changed!)      │     │
│  │  Token vault: ADDR_1=123 Main, ADDR_2=456 Oak          │     │
│  │                                                         │     │
│  │  ✓ CHANGE DETECTED WITHOUT EXPOSING ACTUAL ADDRESS    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SAME-ENTITY CONSISTENCY:                                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  If "John Smith" appears 15 times in document:         │     │
│  │                                                         │     │
│  │  Redaction: 15x "[REDACTED]" - no way to know if same  │     │
│  │  Tokenization: 15x "[PERSON_1]" - clearly same person  │     │
│  │                                                         │     │
│  │  This matters when tracking who is affected by changes │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Tokenization Implementation

```
┌─────────────────────────────────────────────────────────────────┐
│              Tokenization Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  1. DETECTION: Find all PII in document                │     │
│  │     └── Presidio + regex + NER                         │     │
│  │                                                         │     │
│  │  2. TOKEN GENERATION: Create consistent placeholders   │     │
│  │     └── Hash-based for cross-document consistency      │     │
│  │     └── Type-prefixed: [PERSON_X], [SSN_X], [ADDR_X]   │     │
│  │                                                         │     │
│  │  3. VAULT STORAGE: Encrypted token → value mapping     │     │
│  │     └── AES-256-GCM encryption                         │     │
│  │     └── TTL-based auto-expiration                      │     │
│  │     └── Audit logging on every access                  │     │
│  │                                                         │     │
│  │  4. DOCUMENT TRANSFORMATION: Replace PII with tokens   │     │
│  │     └── Maintain exact positions for reconstruction    │     │
│  │                                                         │     │
│  │  5. LLM PROCESSING: Analyze tokenized documents        │     │
│  │     └── LLM never sees actual PII                      │     │
│  │     └── Can still reason about entities                │     │
│  │                                                         │     │
│  │  6. RECONSTRUCTION: Replace tokens in output           │     │
│  │     └── Only for authorized users                      │     │
│  │     └── Role-based: some see masked, some see full     │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  When to use REDACTION instead:                                 │
│  ├── Final export for external parties                          │
│  ├── Permanent anonymization requirements                       │
│  ├── When reconstruction is explicitly prohibited               │
│  └── Public-facing reports                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Decision 3: When LLM Calls Are Skipped Entirely

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    LLM BYPASS DECISION TREE                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Not every comparison needs an LLM. Rule-based processing handles many cases:       │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │                         INCOMING COMPARISON                                  │   │
│  │                               │                                              │   │
│  │                               ▼                                              │   │
│  │                    ┌─────────────────────┐                                  │   │
│  │                    │ Documents identical? │                                  │   │
│  │                    │   (hash match)       │                                  │   │
│  │                    └──────────┬──────────┘                                  │   │
│  │                          YES  │  NO                                          │   │
│  │                    ┌──────────┴──────────┐                                  │   │
│  │                    ▼                     ▼                                  │   │
│  │            ┌─────────────┐    ┌─────────────────────┐                       │   │
│  │            │ SKIP LLM    │    │ Embedding similarity │                       │   │
│  │            │ Return:     │    │ > 0.99?              │                       │   │
│  │            │ "No changes"│    └──────────┬──────────┘                       │   │
│  │            └─────────────┘          YES  │  NO                              │   │
│  │                              ┌───────────┴───────────┐                      │   │
│  │                              ▼                       ▼                      │   │
│  │                    ┌─────────────────┐    ┌─────────────────────┐          │   │
│  │                    │ Text diff only  │    │ Only whitespace/    │          │   │
│  │                    │ (formatting?)   │    │ formatting changes? │          │   │
│  │                    └────────┬────────┘    └──────────┬──────────┘          │   │
│  │                        YES  │  NO               YES  │  NO                  │   │
│  │                    ┌────────┴────┐         ┌────────┴────────┐             │   │
│  │                    ▼             ▼         ▼                 ▼             │   │
│  │            ┌─────────────┐  ┌────────┐  ┌─────────────┐  ┌────────────┐   │   │
│  │            │ SKIP LLM    │  │Continue│  │ SKIP LLM    │  │ USE LLM    │   │   │
│  │            │ Return:     │  │   ▼    │  │ Return:     │  │ for deep   │   │   │
│  │            │"Format only"│  │        │  │"Format only"│  │ analysis   │   │   │
│  │            └─────────────┘  │        │  └─────────────┘  └────────────┘   │   │
│  │                             ▼        │                                      │   │
│  │                    ┌─────────────────┴───┐                                 │   │
│  │                    │ Rule-based patterns? │                                 │   │
│  │                    │ (numbers, dates,     │                                 │   │
│  │                    │  known equivalences) │                                 │   │
│  │                    └──────────┬──────────┘                                 │   │
│  │                        MATCH  │  NO MATCH                                   │   │
│  │                    ┌──────────┴──────────┐                                 │   │
│  │                    ▼                     ▼                                 │   │
│  │            ┌─────────────────┐    ┌─────────────┐                          │   │
│  │            │ SKIP LLM        │    │ USE LLM     │                          │   │
│  │            │ Apply rule      │    │ Complex     │                          │   │
│  │            │ result directly │    │ analysis    │                          │   │
│  │            └─────────────────┘    └─────────────┘                          │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Rule-Based Patterns (No LLM Needed)

```
┌─────────────────────────────────────────────────────────────────┐
│           Changes Handled Without LLM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CATEGORY 1: Formatting Only (SKIP - No significance)           │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Pattern                     │ Detection Method        │     │
│  │  ────────────────────────────┼────────────────────────│     │
│  │  Whitespace changes          │ Normalize & compare     │     │
│  │  Capitalization only         │ Case-insensitive match  │     │
│  │  Punctuation normalization   │ Regex strip & compare   │     │
│  │  Number formatting           │ Parse & compare values  │     │
│  │  "30" vs "thirty (30)"       │ Number extraction       │     │
│  │  Line break differences      │ Whitespace normalize    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CATEGORY 2: Known Equivalences (SKIP - Semantic match)         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Pattern                     │ Detection Method        │     │
│  │  ────────────────────────────┼────────────────────────│     │
│  │  "shall" ↔ "will" ↔ "must"   │ Equivalence dictionary │     │
│  │  "prior to" ↔ "before"       │ Equivalence dictionary │     │
│  │  "$1,000,000" ↔ "$1M"        │ Number normalization   │     │
│  │  Date format changes         │ Date parsing           │     │
│  │  Section renumbering only    │ Structure analysis     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CATEGORY 3: Clear Numerical Changes (RULE - High confidence)   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Pattern                     │ Rule                    │     │
│  │  ────────────────────────────┼────────────────────────│     │
│  │  Dollar amount change        │ Flag if delta > 10%    │     │
│  │  Percentage change           │ Flag any change        │     │
│  │  Day/time period change      │ Flag if delta > 20%    │     │
│  │  Quantity change             │ Flag if delta > 25%    │     │
│  │                                                         │     │
│  │  These get HIGH significance without LLM because       │     │
│  │  numerical changes are almost always material          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CATEGORY 4: Critical Patterns (RULE - Always flag)             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Pattern                     │ Significance            │     │
│  │  ────────────────────────────┼────────────────────────│     │
│  │  "not" inserted/removed      │ CRITICAL               │     │
│  │  "excluded" ↔ "included"     │ CRITICAL               │     │
│  │  "and" ↔ "or" swap           │ HIGH                   │     │
│  │  "may" ↔ "must" swap         │ HIGH                   │     │
│  │  "all" ↔ "some" swap         │ HIGH                   │     │
│  │                                                         │     │
│  │  Regex + position tracking catches these with 99%+     │     │
│  │  accuracy - no LLM needed for detection                │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  WHEN LLM IS REQUIRED:                                          │
│  ├── Complex semantic rephrasing                                │
│  ├── Ambiguous context-dependent meaning                        │
│  ├── Multi-sentence restructuring                               │
│  ├── Implicit meaning changes                                   │
│  └── Significance assessment for edge cases                     │
│                                                                  │
│  RESULT: ~70% of changes handled by rules, 30% need LLM        │
│  COST SAVINGS: 70% reduction in LLM API calls                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Decision 4: When Self-Hosted Models Are Mandatory

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    MODEL ROUTING DECISION MATRIX                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │                              INPUT REQUEST                                   │   │
│  │                                    │                                         │   │
│  │                                    ▼                                         │   │
│  │                    ┌───────────────────────────────┐                        │   │
│  │                    │    Data Classification?        │                        │   │
│  │                    └───────────────┬───────────────┘                        │   │
│  │                                    │                                         │   │
│  │        ┌───────────────┬───────────┼───────────┬───────────────┐           │   │
│  │        ▼               ▼           ▼           ▼               ▼           │   │
│  │   ┌─────────┐    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐      │   │
│  │   │ PUBLIC  │    │INTERNAL │  │CONFIDEN-│  │REGULATED│  │RESTRICTED│      │   │
│  │   │         │    │         │  │  TIAL   │  │(HIPAA/  │  │  (PII)   │      │   │
│  │   │         │    │         │  │         │  │ GDPR)   │  │          │      │   │
│  │   └────┬────┘    └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘      │   │
│  │        │              │            │            │             │            │   │
│  │        ▼              ▼            ▼            ▼             ▼            │   │
│  │   ┌─────────┐    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐      │   │
│  │   │EXTERNAL │    │EXTERNAL │  │ SELF-   │  │ SELF-   │  │  SELF-   │      │   │
│  │   │   OK    │    │  w/DPA  │  │ HOSTED  │  │ HOSTED  │  │  HOSTED  │      │   │
│  │   │         │    │         │  │  ONLY   │  │  ONLY   │  │   ONLY   │      │   │
│  │   │ GPT-4   │    │ Azure   │  │ Llama   │  │ Llama + │  │  Llama + │      │   │
│  │   │ Claude  │    │ OpenAI  │  │ Mistral │  │  BAA    │  │  Audit   │      │   │
│  │   └─────────┘    └─────────┘  └─────────┘  └─────────┘  └──────────┘      │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Mandatory Self-Hosted Scenarios

```
┌─────────────────────────────────────────────────────────────────┐
│         When Self-Hosted LLM is REQUIRED                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SCENARIO 1: Unsanitized PII Present                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Condition: PII detected AND sanitization failed/skipped│    │
│  │  Reason: Cannot send real SSNs, medical data to external│    │
│  │  Action: Route to self-hosted Llama/Mistral             │     │
│  │                                                         │     │
│  │  if pii_detected and not successfully_sanitized:       │     │
│  │      return route_to_self_hosted()                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SCENARIO 2: HIPAA-Covered Data                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Condition: Document contains PHI (Protected Health Info)│   │
│  │  Reason: HIPAA requires BAA; most external LLMs don't   │    │
│  │          qualify even with sanitization                 │     │
│  │  Action: Self-hosted with HIPAA-compliant infrastructure│     │
│  │                                                         │     │
│  │  if document.contains_phi or tenant.is_hipaa_covered:  │     │
│  │      return route_to_hipaa_compliant_self_hosted()     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SCENARIO 3: Data Residency Requirements                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Condition: Tenant requires data stay in specific region│    │
│  │  Reason: GDPR, local regulations, contractual obligation│    │
│  │  Action: Route to self-hosted in compliant region       │     │
│  │                                                         │     │
│  │  if tenant.data_residency_region not in                │     │
│  │     external_provider.available_regions:               │     │
│  │      return route_to_regional_self_hosted()            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SCENARIO 4: Confidential Classification                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Condition: Document marked CONFIDENTIAL or above       │     │
│  │  Reason: Organization policy prohibits external AI      │     │
│  │  Action: Self-hosted regardless of sanitization         │     │
│  │                                                         │     │
│  │  if document.classification >= CONFIDENTIAL:           │     │
│  │      return route_to_self_hosted()  # No exceptions    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SCENARIO 5: Tenant Contractual Requirement                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Condition: Customer contract prohibits external AI     │     │
│  │  Reason: Enterprise customers often require this        │     │
│  │  Action: Self-hosted for all tenant's documents         │     │
│  │                                                         │     │
│  │  if tenant.requires_self_hosted_only:                  │     │
│  │      return route_to_self_hosted()                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SCENARIO 6: Zero Data Retention Requirement                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Condition: Must guarantee no data retained by provider │     │
│  │  Reason: Some external providers log/retain briefly     │     │
│  │  Action: Self-hosted where we control all storage       │     │
│  │                                                         │     │
│  │  if tenant.requires_zero_retention and                 │     │
│  │     not external_provider.guarantees_zero_retention:   │     │
│  │      return route_to_self_hosted()                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### External LLM Acceptable Scenarios

```
┌─────────────────────────────────────────────────────────────────┐
│         When External LLM is Acceptable                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ALL conditions must be true:                                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ✓ Data successfully sanitized (PII tokenized)         │     │
│  │  ✓ Document classification ≤ INTERNAL                  │     │
│  │  ✓ No HIPAA/regulated data present                     │     │
│  │  ✓ Tenant allows external AI processing                │     │
│  │  ✓ Data residency requirements met                     │     │
│  │  ✓ DPA (Data Processing Agreement) in place            │     │
│  │  ✓ Provider configured for no training on data         │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Even then, prefer:                                              │
│  1. Azure OpenAI (private endpoints, enterprise DPA)            │
│  2. AWS Bedrock (VPC, no data retention)                        │
│  3. Anthropic/OpenAI API (only with explicit opt-out)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Decision 5: What Happens When Confidence < Threshold

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    LOW CONFIDENCE HANDLING                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Every LLM analysis returns a confidence score. What happens when it's low?         │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │   CONFIDENCE THRESHOLDS AND ACTIONS                                         │   │
│  │                                                                              │   │
│  │   Confidence    │ Interpretation        │ Action                            │   │
│  │   ─────────────────────────────────────────────────────────────────────────│   │
│  │   ≥ 0.90        │ HIGH CONFIDENCE       │ Accept result, auto-process      │   │
│  │   0.75 - 0.89   │ MEDIUM CONFIDENCE     │ Accept with flag for review      │   │
│  │   0.50 - 0.74   │ LOW CONFIDENCE        │ Require human review             │   │
│  │   < 0.50        │ VERY LOW CONFIDENCE   │ Escalate + alternative analysis  │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Low Confidence Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│           Low Confidence Decision Tree                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │               LLM returns result                        │     │
│  │               confidence = 0.62                         │     │
│  │                      │                                  │     │
│  │                      ▼                                  │     │
│  │          ┌─────────────────────┐                       │     │
│  │          │ Confidence < 0.75?  │                       │     │
│  │          └──────────┬──────────┘                       │     │
│  │                     │ YES                               │     │
│  │                     ▼                                   │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │  STEP 1: Retry with Enhanced Context             │   │     │
│  │  │                                                   │   │     │
│  │  │  • Add more surrounding text                     │   │     │
│  │  │  • Include definitions section                   │   │     │
│  │  │  • Retrieve similar examples from RAG            │   │     │
│  │  │  • Use more detailed prompt template             │   │     │
│  │  │                                                   │   │     │
│  │  │  New confidence: 0.71 (still low)                │   │     │
│  │  └──────────────────────┬──────────────────────────┘   │     │
│  │                         │                               │     │
│  │                         ▼                               │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │  STEP 2: Alternative Model Analysis              │   │     │
│  │  │                                                   │   │     │
│  │  │  • Run same analysis on different model          │   │     │
│  │  │  • Compare results for agreement                 │   │     │
│  │  │  • If models agree → increase confidence         │   │     │
│  │  │  • If models disagree → definitely needs human   │   │     │
│  │  │                                                   │   │     │
│  │  │  Model A: "HIGH significance"  (conf: 0.71)      │   │     │
│  │  │  Model B: "HIGH significance"  (conf: 0.68)      │   │     │
│  │  │  Agreement: YES → Ensemble confidence: 0.78      │   │     │
│  │  └──────────────────────┬──────────────────────────┘   │     │
│  │                         │                               │     │
│  │                         ▼                               │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │  STEP 3: Rule-Based Validation                   │   │     │
│  │  │                                                   │   │     │
│  │  │  • Check if deterministic rules confirm/deny     │   │     │
│  │  │  • Numerical change? → Rules override LLM        │   │     │
│  │  │  • Negation detected? → Rules override LLM       │   │     │
│  │  │  • Known pattern match? → Rules boost confidence │   │     │
│  │  │                                                   │   │     │
│  │  │  Rule check: Found numerical change ($500K→$1M)  │   │     │
│  │  │  Rule says: ALWAYS HIGH significance             │   │     │
│  │  │  Final confidence: RULE_OVERRIDE (deterministic) │   │     │
│  │  └──────────────────────┬──────────────────────────┘   │     │
│  │                         │                               │     │
│  │                         ▼                               │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │  STEP 4: If Still Low → Human Review Queue       │   │     │
│  │  │                                                   │   │     │
│  │  │  When automated methods cannot resolve:          │   │     │
│  │  │  • Add to human review queue                     │   │     │
│  │  │  • Include all analysis attempts                 │   │     │
│  │  │  • Show confidence scores from each method       │   │     │
│  │  │  • Highlight areas of disagreement               │   │     │
│  │  │  • Track resolution for future training          │   │     │
│  │  │                                                   │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Confidence Calibration

```
┌─────────────────────────────────────────────────────────────────┐
│           Ensuring Confidence Scores Are Meaningful              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PROBLEM: LLM confidence doesn't always match accuracy          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Uncalibrated:                                          │     │
│  │  • LLM says 90% confident → Actually right 75% of time │     │
│  │  • LLM says 60% confident → Actually right 60% of time │     │
│  │                                                         │     │
│  │  LLMs are often OVERconfident on high scores            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  SOLUTION: Calibration via human feedback                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  1. COLLECT: Human judgments on LLM outputs            │     │
│  │  2. BUCKET: Group by reported confidence               │     │
│  │  3. MEASURE: Actual accuracy per bucket                │     │
│  │  4. ADJUST: Create calibration curve                   │     │
│  │                                                         │     │
│  │  Calibration Table:                                     │     │
│  │  ┌───────────────────────────────────────────────┐     │     │
│  │  │ LLM Reports │ Actual Accuracy │ Calibrated    │     │     │
│  │  │ ────────────┼─────────────────┼──────────────│     │     │
│  │  │    0.95     │      0.82       │     0.82     │     │     │
│  │  │    0.90     │      0.78       │     0.78     │     │     │
│  │  │    0.85     │      0.76       │     0.76     │     │     │
│  │  │    0.80     │      0.74       │     0.74     │     │     │
│  │  │    0.70     │      0.68       │     0.68     │     │     │
│  │  │    0.60     │      0.61       │     0.61     │     │     │
│  │  └───────────────────────────────────────────────┘     │     │
│  │                                                         │     │
│  │  Thresholds adjusted based on CALIBRATED scores:       │     │
│  │  • Auto-accept: calibrated ≥ 0.78 (was 0.90 raw)      │     │
│  │  • Human review: calibrated < 0.68                     │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CONTINUOUS IMPROVEMENT:                                         │
│  ├── Recalibrate weekly based on new feedback                   │
│  ├── Track calibration drift over time                          │
│  ├── Alert if accuracy drops below threshold                    │
│  └── Adjust routing thresholds dynamically                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Human Review Queue Design

```
┌─────────────────────────────────────────────────────────────────┐
│           Human Review for Low Confidence Items                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Review Queue Item:                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  CHANGE ID: diff_4521                                  │     │
│  │  CONFIDENCE: 0.58 (LOW)                                │     │
│  │  REASON: Models disagreed on significance              │     │
│  │                                                         │     │
│  │  ─────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  ORIGINAL TEXT:                                         │     │
│  │  "The insurer shall provide coverage for claims        │     │
│  │   arising from professional services."                 │     │
│  │                                                         │     │
│  │  MODIFIED TEXT:                                         │     │
│  │  "The insurer may provide coverage for claims          │     │
│  │   arising from professional services, subject to       │     │
│  │   underwriting approval."                              │     │
│  │                                                         │     │
│  │  ─────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  AI ANALYSIS:                                           │     │
│  │  ┌─────────────────────────────────────────────────┐  │     │
│  │  │ Model A (Llama):  CRITICAL - "shall→may changes │  │     │
│  │  │                   obligation to discretion"      │  │     │
│  │  │ Confidence: 0.71                                 │  │     │
│  │  │                                                   │  │     │
│  │  │ Model B (GPT-4):  MEDIUM - "Added clarification  │  │     │
│  │  │                   on approval process"           │  │     │
│  │  │ Confidence: 0.65                                 │  │     │
│  │  │                                                   │  │     │
│  │  │ Rule Engine: FLAGGED - "shall→may" pattern       │  │     │
│  │  └─────────────────────────────────────────────────┘  │     │
│  │                                                         │     │
│  │  YOUR ASSESSMENT:                                       │     │
│  │  [ ] CRITICAL  [●] HIGH  [ ] MEDIUM  [ ] LOW  [ ] NONE │     │
│  │                                                         │     │
│  │  Comments: [Model A is correct - this weakens_______] │     │
│  │                                                         │     │
│  │  [Submit] [Skip] [Escalate to Expert]                  │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Feedback Loop:                                                  │
│  ├── Human decision stored with original AI outputs             │
│  ├── Used to retrain confidence calibration                     │
│  ├── Patterns of disagreement analyzed for model improvement    │
│  └── Similar future cases may get boosted confidence            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Summary: AI Design Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    AI DESIGN DECISIONS SUMMARY                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Decision                │ Choice              │ Key Tradeoff                       │
│  ────────────────────────┼─────────────────────┼───────────────────────────────────│
│  Comparison approach     │ Embeddings + LLM    │ Cost/speed vs depth of analysis   │
│  PII protection          │ Tokenization        │ Reversibility vs simplicity       │
│  LLM invocation          │ Selective (30%)     │ Cost vs coverage                  │
│  Model hosting           │ Hybrid routing      │ Privacy vs capability             │
│  Low confidence          │ Escalation ladder   │ Automation vs accuracy            │
│                                                                                      │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│                                                                                      │
│  GUIDING PRINCIPLES:                                                                │
│                                                                                      │
│  1. NEVER MISS CRITICAL CHANGES (prioritize recall over precision)                  │
│  2. NEVER EXPOSE SENSITIVE DATA (self-hosted when in doubt)                         │
│  3. ALWAYS EXPLAIN DECISIONS (auditability over black-box)                          │
│  4. PREFER RULES OVER LLM (determinism over probabilism where possible)             │
│  5. HUMAN-IN-THE-LOOP FOR UNCERTAINTY (escalate, don't guess)                       │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRESENTATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐    │
│  │   Web UI    │  │  REST API   │  │ GraphQL API │  │   CLI / SDK Clients     │    │
│  │  (React)    │  │  Gateway    │  │   Gateway   │  │  (Python, Node, Java)   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   GATEWAY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  API Gateway    │  │  Load Balancer  │  │  Rate Limiter   │  │  WAF / DDoS   │  │
│  │  (Kong/AWS)     │  │  (nginx/ALB)    │  │                 │  │  Protection   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AUTHENTICATION & AUTHORIZATION                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Identity       │  │  OAuth 2.0 /    │  │  RBAC / ABAC    │  │  API Key      │  │
│  │  Provider       │  │  OIDC / SAML    │  │  Policy Engine  │  │  Management   │  │
│  │  (Okta/Azure AD)│  │                 │  │  (OPA)          │  │               │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 APPLICATION LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                           MICROSERVICES CLUSTER                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │  Document   │  │  PDF        │  │  Diff       │  │  Report             │  │  │
│  │  │  Ingestion  │  │  Processing │  │  Engine     │  │  Generation         │  │  │
│  │  │  Service    │  │  Service    │  │  Service    │  │  Service            │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│  │                                                                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │  Template   │  │  Comparison │  │  Workflow   │  │  Notification       │  │  │
│  │  │  Management │  │  History    │  │  Orchestrat │  │  Service            │  │  │
│  │  │  Service    │  │  Service    │  │  Service    │  │                     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MESSAGE & EVENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Message Queue  │  │  Event Bus      │  │  Task Queue     │  │  Pub/Sub      │  │
│  │  (RabbitMQ/SQS) │  │  (Kafka)        │  │  (Celery)       │  │  (Redis)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  PostgreSQL     │  │  Elasticsearch  │  │  Redis Cache    │  │  S3 / Blob    │  │
│  │  (Primary DB)   │  │  (Search/Index) │  │  (Session/Cache)│  │  (Documents)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │
│  │  MongoDB        │  │  Vector DB      │  │  Time Series    │                      │
│  │  (Documents)    │  │  (Semantic)     │  │  (Metrics)      │                      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            OBSERVABILITY & OPERATIONS                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Logging        │  │  Metrics        │  │  Tracing        │  │  Alerting     │  │
│  │  (ELK/Loki)     │  │  (Prometheus)   │  │  (Jaeger)       │  │  (PagerDuty)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Audit Logging  │  │  APM            │  │  Health Checks  │  │  Dashboards   │  │
│  │  (Compliance)   │  │  (Datadog/NR)   │  │                 │  │  (Grafana)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Microservices

### 1. Document Ingestion Service

**Responsibility**: Secure document upload, validation, and storage

```
┌─────────────────────────────────────────────────────────────────┐
│                  Document Ingestion Service                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input Channels:                                                 │
│  ├── REST API Upload (multipart/form-data)                      │
│  ├── S3/Azure Blob Event Trigger                                │
│  ├── Email Attachment Processor                                 │
│  ├── SFTP/FTP Watch Directory                                   │
│  └── Webhook Integration                                        │
│                                                                  │
│  Processing Pipeline:                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Receive  │─▶│ Validate │─▶│ Virus    │─▶│ Store &      │    │
│  │ Document │  │ Format   │  │ Scan     │  │ Index        │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
│                                                                  │
│  Validation Rules:                                               │
│  ├── File size limits (configurable per tenant)                 │
│  ├── MIME type verification                                     │
│  ├── PDF/A compliance check                                     │
│  ├── Encryption detection                                       │
│  └── Malware scanning (ClamAV/Commercial)                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. PDF Processing Service

**Responsibility**: Extract structured content from PDF documents

```
┌─────────────────────────────────────────────────────────────────┐
│                    PDF Processing Service                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Extraction Pipeline:                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │     │
│  │  │  Text   │  │  Table  │  │  Image  │  │ Metadata│   │     │
│  │  │ Extract │  │ Extract │  │  OCR    │  │ Extract │   │     │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │     │
│  │       │            │            │            │         │     │
│  │       └────────────┴─────┬──────┴────────────┘         │     │
│  │                          ▼                             │     │
│  │                 ┌─────────────────┐                    │     │
│  │                 │ Content Merger  │                    │     │
│  │                 │ & Structurer    │                    │     │
│  │                 └────────┬────────┘                    │     │
│  │                          ▼                             │     │
│  │                 ┌─────────────────┐                    │     │
│  │                 │ Section/Chapter │                    │     │
│  │                 │ Detection       │                    │     │
│  │                 └─────────────────┘                    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Output Schema:                                                  │
│  {                                                               │
│    "document_id": "uuid",                                       │
│    "metadata": { ... },                                         │
│    "structure": {                                               │
│      "sections": [...],                                         │
│      "headers": [...],                                          │
│      "tables": [...],                                           │
│      "lists": [...]                                             │
│    },                                                           │
│    "content": {                                                 │
│      "raw_text": "...",                                         │
│      "normalized_text": "...",                                  │
│      "paragraphs": [...]                                        │
│    }                                                            │
│  }                                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Diff Engine Service

**Responsibility**: Multi-level document comparison

```
┌─────────────────────────────────────────────────────────────────┐
│                      Diff Engine Service                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Comparison Levels:                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Level 1: Character Diff                                │     │
│  │  └── Exact character-by-character comparison           │     │
│  │                                                         │     │
│  │  Level 2: Word Diff                                     │     │
│  │  └── Word-level changes with context                   │     │
│  │                                                         │     │
│  │  Level 3: Sentence Diff                                 │     │
│  │  └── Sentence restructuring detection                  │     │
│  │                                                         │     │
│  │  Level 4: Section Diff                                  │     │
│  │  └── Section moves, additions, deletions               │     │
│  │                                                         │     │
│  │  Level 5: Semantic Diff (AI-powered)                    │     │
│  │  └── Meaning-preserving vs meaning-changing            │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Diff Algorithms:                                                │
│  ├── Myers Diff (default for text)                              │
│  ├── Patience Diff (for structured content)                     │
│  ├── Histogram Diff (for large documents)                       │
│  ├── LCS (Longest Common Subsequence)                           │
│  └── ML-based semantic similarity                               │
│                                                                  │
│  Change Categories:                                              │
│  ├── ADDED      - New content                                   │
│  ├── REMOVED    - Deleted content                               │
│  ├── MODIFIED   - Changed content                               │
│  ├── MOVED      - Relocated content                             │
│  ├── REFORMATTED - Style changes only                           │
│  └── SEMANTIC   - Meaning change detected                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Report Generation Service

**Responsibility**: Generate diff reports in multiple formats

```
┌─────────────────────────────────────────────────────────────────┐
│                  Report Generation Service                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Output Formats:                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │     │
│  │  │  HTML   │  │  PDF    │  │  JSON   │  │  DOCX   │   │     │
│  │  │ Report  │  │ Report  │  │ Export  │  │ Track   │   │     │
│  │  │         │  │         │  │         │  │ Changes │   │     │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │     │
│  │                                                         │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐               │     │
│  │  │  CSV    │  │  XML    │  │ Markdown│               │     │
│  │  │ Summary │  │ Export  │  │ Report  │               │     │
│  │  └─────────┘  └─────────┘  └─────────┘               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Report Views:                                                   │
│  ├── Side-by-side comparison                                    │
│  ├── Inline diff (unified)                                      │
│  ├── Executive summary                                          │
│  ├── Change-only view                                           │
│  ├── Section-by-section                                         │
│  └── Regulatory compliance view                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Core Entities

```sql
-- Tenant (Multi-tenancy)
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    external_id VARCHAR(255), -- SSO provider ID
    role VARCHAR(50) NOT NULL,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    uploaded_by UUID REFERENCES users(id),
    filename VARCHAR(500) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    file_hash VARCHAR(64) NOT NULL, -- SHA-256
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    extracted_content JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Comparisons
CREATE TABLE comparisons (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    created_by UUID REFERENCES users(id),
    document_a_id UUID REFERENCES documents(id),
    document_b_id UUID REFERENCES documents(id),
    status VARCHAR(50) DEFAULT 'pending',
    comparison_type VARCHAR(50) DEFAULT 'full',
    settings JSONB DEFAULT '{}',
    result_summary JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Diff Results
CREATE TABLE diff_results (
    id UUID PRIMARY KEY,
    comparison_id UUID REFERENCES comparisons(id),
    section_path VARCHAR(500),
    change_type VARCHAR(50) NOT NULL,
    content_a TEXT,
    content_b TEXT,
    position_a JSONB, -- {start: line, end: line}
    position_b JSONB,
    confidence_score DECIMAL(5,4),
    metadata JSONB DEFAULT '{}'
);

-- Audit Log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_documents_tenant ON documents(tenant_id);
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_comparisons_tenant ON comparisons(tenant_id);
CREATE INDEX idx_audit_logs_tenant_time ON audit_logs(tenant_id, created_at DESC);
```

---

## API Design

### RESTful API Endpoints

```yaml
# OpenAPI 3.0 Specification (abbreviated)

paths:
  # Document Management
  /api/v1/documents:
    post:
      summary: Upload document
      security: [bearerAuth: []]
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                metadata:
                  type: object
    get:
      summary: List documents
      parameters:
        - name: page
        - name: limit
        - name: sort
        - name: filter

  /api/v1/documents/{id}:
    get:
      summary: Get document details
    delete:
      summary: Delete document

  # Comparisons
  /api/v1/comparisons:
    post:
      summary: Create comparison
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                document_a_id:
                  type: string
                  format: uuid
                document_b_id:
                  type: string
                  format: uuid
                settings:
                  type: object
                  properties:
                    comparison_level:
                      enum: [character, word, sentence, section, semantic]
                    ignore_formatting:
                      type: boolean
                    ignore_whitespace:
                      type: boolean
    get:
      summary: List comparisons

  /api/v1/comparisons/{id}:
    get:
      summary: Get comparison details

  /api/v1/comparisons/{id}/results:
    get:
      summary: Get diff results
      parameters:
        - name: format
          enum: [json, unified, side-by-side]
        - name: change_type
          enum: [all, added, removed, modified]

  /api/v1/comparisons/{id}/report:
    get:
      summary: Generate report
      parameters:
        - name: format
          enum: [html, pdf, docx, json, csv]

  # Webhooks
  /api/v1/webhooks:
    post:
      summary: Register webhook
    get:
      summary: List webhooks

  # Health & Status
  /health:
    get:
      summary: Health check
  /ready:
    get:
      summary: Readiness check
```

### Async Job API

```yaml
  /api/v1/jobs/{id}:
    get:
      summary: Get job status
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  status:
                    enum: [pending, processing, completed, failed]
                  progress:
                    type: integer
                    minimum: 0
                    maximum: 100
                  result_url:
                    type: string
                  error:
                    type: object
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Authentication Methods:                                         │
│  ├── SAML 2.0 (Enterprise SSO)                                  │
│  ├── OAuth 2.0 / OIDC                                           │
│  ├── API Keys (Service-to-Service)                              │
│  └── JWT Tokens (Session Management)                            │
│                                                                  │
│  Authorization Model (RBAC + ABAC):                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Roles:                                                 │     │
│  │  ├── Admin       - Full system access                  │     │
│  │  ├── Manager     - Team & comparison management        │     │
│  │  ├── Analyst     - Create/view comparisons             │     │
│  │  ├── Viewer      - View-only access                    │     │
│  │  └── API User    - Programmatic access                 │     │
│  │                                                         │     │
│  │  Permissions:                                           │     │
│  │  ├── document:upload                                   │     │
│  │  ├── document:read                                     │     │
│  │  ├── document:delete                                   │     │
│  │  ├── comparison:create                                 │     │
│  │  ├── comparison:read                                   │     │
│  │  ├── report:generate                                   │     │
│  │  ├── report:export                                     │     │
│  │  └── admin:*                                           │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Data Security:                                                  │
│  ├── Encryption at rest (AES-256)                               │
│  ├── Encryption in transit (TLS 1.3)                            │
│  ├── Document-level encryption (optional)                       │
│  ├── Key management (AWS KMS / HashiCorp Vault)                 │
│  └── Data masking for sensitive content                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Compliance Features

```
┌─────────────────────────────────────────────────────────────────┐
│                    Compliance Framework                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Regulatory Support:                                             │
│  ├── SOC 2 Type II                                              │
│  ├── GDPR (Data residency, Right to deletion)                   │
│  ├── HIPAA (Healthcare policies)                                │
│  ├── CCPA (California privacy)                                  │
│  └── ISO 27001                                                  │
│                                                                  │
│  Audit Capabilities:                                             │
│  ├── Complete action audit trail                                │
│  ├── User activity logging                                      │
│  ├── Document access logs                                       │
│  ├── Export audit reports                                       │
│  └── Retention policies                                         │
│                                                                  │
│  Data Governance:                                                │
│  ├── Data classification tags                                   │
│  ├── Retention period configuration                             │
│  ├── Automated data purging                                     │
│  ├── Geographic data residency                                  │
│  └── Cross-border transfer controls                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## PII Protection Architecture

### Overview

Policy documents frequently contain Personally Identifiable Information (PII) such as names, addresses, SSNs, financial data, and health information. This architecture implements defense-in-depth PII protection across all system layers.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PII PROTECTION FRAMEWORK                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         DETECTION LAYER                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   Pattern   │  │     NER     │  │  ML-based   │  │   Custom Rule   │    │   │
│  │  │   Matching  │  │  Detection  │  │  Classifier │  │     Engine      │    │   │
│  │  │  (Regex)    │  │  (spaCy)    │  │ (Presidio)  │  │  (Domain-spec)  │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                        CLASSIFICATION LAYER                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   PII       │  │  Sensitivity│  │  Regulatory │  │   Confidence    │    │   │
│  │  │   Type      │  │   Level     │  │  Category   │  │   Scoring       │    │   │
│  │  │  Tagging    │  │  Assignment │  │  Mapping    │  │                 │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         PROTECTION LAYER                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   Masking   │  │  Redaction  │  │ Tokenization│  │   Encryption    │    │   │
│  │  │  (Display)  │  │  (Removal)  │  │  (Replace)  │  │   (Storage)     │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                          ACCESS CONTROL LAYER                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   Role-     │  │  Purpose    │  │   Time-     │  │   Audit &       │    │   │
│  │  │   Based     │  │  Limitation │  │   Bound     │  │   Logging       │    │   │
│  │  │   Access    │  │             │  │   Access    │  │                 │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### PII Detection Service

**Responsibility**: Automatically detect and classify PII in documents

```
┌─────────────────────────────────────────────────────────────────┐
│                    PII Detection Service                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Detectable PII Types:                                           │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  IDENTIFIERS:                                           │     │
│  │  ├── Social Security Numbers (SSN)                     │     │
│  │  ├── National ID Numbers                               │     │
│  │  ├── Passport Numbers                                  │     │
│  │  ├── Driver's License Numbers                          │     │
│  │  ├── Employee IDs                                      │     │
│  │  └── Tax Identification Numbers                        │     │
│  │                                                         │     │
│  │  PERSONAL DATA:                                         │     │
│  │  ├── Full Names                                        │     │
│  │  ├── Email Addresses                                   │     │
│  │  ├── Phone Numbers                                     │     │
│  │  ├── Physical Addresses                                │     │
│  │  ├── Dates of Birth                                    │     │
│  │  └── IP Addresses                                      │     │
│  │                                                         │     │
│  │  FINANCIAL DATA:                                        │     │
│  │  ├── Credit Card Numbers                               │     │
│  │  ├── Bank Account Numbers                              │     │
│  │  ├── Routing Numbers                                   │     │
│  │  ├── IBAN / SWIFT Codes                                │     │
│  │  └── Financial Account Identifiers                     │     │
│  │                                                         │     │
│  │  HEALTH DATA (PHI):                                     │     │
│  │  ├── Medical Record Numbers                            │     │
│  │  ├── Health Plan IDs                                   │     │
│  │  ├── Prescription Information                          │     │
│  │  ├── Diagnosis Codes (ICD)                             │     │
│  │  └── Treatment Information                             │     │
│  │                                                         │     │
│  │  BIOMETRIC DATA:                                        │     │
│  │  ├── Fingerprint References                            │     │
│  │  ├── Facial Recognition Data                           │     │
│  │  └── Voice Print Identifiers                           │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Detection Methods:                                              │
│  ├── 1. Regex Pattern Matching (fast, high precision)           │
│  │      └── SSN: \d{3}-\d{2}-\d{4}                              │
│  │      └── Email: [a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+             │
│  │      └── Credit Card: Luhn algorithm validation             │
│  │                                                               │
│  ├── 2. NER (Named Entity Recognition)                          │
│  │      └── spaCy/Stanza for person names, locations           │
│  │      └── Custom trained models for domain-specific           │
│  │                                                               │
│  ├── 3. Microsoft Presidio (ML-based)                           │
│  │      └── Pre-trained PII recognizers                        │
│  │      └── Ensemble detection with confidence scoring         │
│  │                                                               │
│  └── 4. Context-Aware Detection                                 │
│         └── Field label analysis ("SSN:", "Name:")              │
│         └── Table header inference                              │
│         └── Surrounding text context                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### PII Classification & Sensitivity Levels

```
┌─────────────────────────────────────────────────────────────────┐
│                  PII Classification Matrix                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Sensitivity Levels:                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  CRITICAL (Level 4):                                    │     │
│  │  ├── Social Security Numbers                           │     │
│  │  ├── Financial Account Numbers                         │     │
│  │  ├── Biometric Data                                    │     │
│  │  ├── Medical Records                                   │     │
│  │  └── Authentication Credentials                        │     │
│  │  → Always encrypted, tokenized, strict access          │     │
│  │                                                         │     │
│  │  HIGH (Level 3):                                        │     │
│  │  ├── Full Names + Other Identifier                     │     │
│  │  ├── Driver's License Numbers                          │     │
│  │  ├── Passport Numbers                                  │     │
│  │  └── Date of Birth                                     │     │
│  │  → Encrypted, masked in display, role-based access     │     │
│  │                                                         │     │
│  │  MEDIUM (Level 2):                                      │     │
│  │  ├── Email Addresses                                   │     │
│  │  ├── Phone Numbers                                     │     │
│  │  ├── Physical Addresses                                │     │
│  │  └── Employee IDs                                      │     │
│  │  → Masked in logs, access controlled                   │     │
│  │                                                         │     │
│  │  LOW (Level 1):                                         │     │
│  │  ├── First Name Only                                   │     │
│  │  ├── Job Title                                         │     │
│  │  ├── Company Name                                      │     │
│  │  └── General Location (City/State)                     │     │
│  │  → Standard access controls                            │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Regulatory Mapping:                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  PII Type          │ GDPR │ HIPAA │ CCPA │ PCI-DSS    │     │
│  │  ─────────────────────────────────────────────────────│     │
│  │  SSN               │  ✓   │   ✓   │  ✓   │            │     │
│  │  Health Data       │  ✓   │   ✓   │  ✓   │            │     │
│  │  Credit Card       │  ✓   │       │  ✓   │     ✓      │     │
│  │  Name + Email      │  ✓   │   ✓   │  ✓   │            │     │
│  │  Biometric         │  ✓   │   ✓   │  ✓   │            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### PII Protection Methods

```
┌─────────────────────────────────────────────────────────────────┐
│                    PII Protection Methods                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. MASKING (Display-time protection)                           │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Original:    John Smith, SSN: 123-45-6789             │     │
│  │  Masked:      J*** S*****, SSN: ***-**-6789            │     │
│  │                                                         │     │
│  │  Use Cases:                                             │     │
│  │  ├── UI display for non-privileged users               │     │
│  │  ├── Report generation with PII protection             │     │
│  │  └── Log file sanitization                             │     │
│  │                                                         │     │
│  │  Masking Strategies:                                    │     │
│  │  ├── Partial mask (show last 4 digits)                 │     │
│  │  ├── Full mask (replace with asterisks)                │     │
│  │  ├── Character substitution                            │     │
│  │  └── Hash-based pseudonymization                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. REDACTION (Permanent removal)                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Original:    Contact: john@company.com, 555-123-4567  │     │
│  │  Redacted:    Contact: [EMAIL REDACTED], [PHONE REDACTED] │  │
│  │                                                         │     │
│  │  Use Cases:                                             │     │
│  │  ├── Document export for external sharing              │     │
│  │  ├── Legal discovery with PII removal                  │     │
│  │  ├── Data retention compliance                         │     │
│  │  └── Public report generation                          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. TOKENIZATION (Reversible replacement)                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Original:    SSN: 123-45-6789                         │     │
│  │  Tokenized:   SSN: TKN_8f3a2b1c                        │     │
│  │                                                         │     │
│  │  Token Vault stores: TKN_8f3a2b1c → 123-45-6789        │     │
│  │                                                         │     │
│  │  Benefits:                                              │     │
│  │  ├── Preserves data format for processing              │     │
│  │  ├── Enables diff comparison without exposing PII      │     │
│  │  ├── Reversible with proper authorization              │     │
│  │  └── Tokens are meaningless if vault compromised       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  4. ENCRYPTION (At-rest protection)                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Encryption Layers:                                     │     │
│  │  ├── Field-level encryption (AES-256-GCM)              │     │
│  │  │   └── Individual PII fields encrypted separately    │     │
│  │  ├── Document-level encryption                         │     │
│  │  │   └── Entire document encrypted at rest             │     │
│  │  ├── Database encryption (TDE)                         │     │
│  │  │   └── Transparent data encryption for DB            │     │
│  │  └── Storage encryption                                │     │
│  │      └── S3 SSE-KMS / Azure Storage encryption         │     │
│  │                                                         │     │
│  │  Key Management:                                        │     │
│  │  ├── AWS KMS / Azure Key Vault / HashiCorp Vault       │     │
│  │  ├── Key rotation every 90 days                        │     │
│  │  ├── Separate keys per tenant                          │     │
│  │  └── HSM-backed key storage                            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### PII-Aware Diff Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                   PII-Aware Diff Processing                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Processing Pipeline:                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐            │     │
│  │  │Document │───▶│  PII    │───▶│Tokenize │            │     │
│  │  │  Input  │    │Detection│    │   PII   │            │     │
│  │  └─────────┘    └─────────┘    └────┬────┘            │     │
│  │                                      │                 │     │
│  │                                      ▼                 │     │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐            │     │
│  │  │  Diff   │◀───│  Diff   │◀───│Tokenized│            │     │
│  │  │ Output  │    │ Engine  │    │ Content │            │     │
│  │  └────┬────┘    └─────────┘    └─────────┘            │     │
│  │       │                                                │     │
│  │       ▼                                                │     │
│  │  ┌───────────────────────────────────────────┐        │     │
│  │  │         Output Generation Options          │        │     │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐   │        │     │
│  │  │  │Full PII │  │ Masked  │  │Redacted │   │        │     │
│  │  │  │(Priv'd) │  │  View   │  │  View   │   │        │     │
│  │  │  └─────────┘  └─────────┘  └─────────┘   │        │     │
│  │  └───────────────────────────────────────────┘        │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Diff Report PII Handling:                                       │
│  ├── PII locations tracked separately from diff results         │
│  ├── Change detection works on tokenized content                │
│  ├── Original PII never stored in diff results                  │
│  ├── Detokenization only at authorized display time             │
│  └── PII changes flagged with special markers                   │
│                                                                  │
│  Example Output (Masked View):                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Section 3.2 - Employee Benefits                       │     │
│  │  - Employee: J*** D** (SSN: ***-**-4567)              │     │
│  │  + Employee: J*** D** (SSN: ***-**-8901)              │     │
│  │    ^ PII CHANGE DETECTED: SSN Modified                 │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### PII Access Control & Audit

```
┌─────────────────────────────────────────────────────────────────┐
│                    PII Access Control                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Permission Matrix:                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Role          │ View  │ View  │ Export│ Export│ Admin │     │
│  │                │Masked │ Full  │Masked │ Full  │  PII  │     │
│  │  ─────────────────────────────────────────────────────│     │
│  │  Viewer        │   ✓   │       │       │       │       │     │
│  │  Analyst       │   ✓   │   ✓*  │   ✓   │       │       │     │
│  │  Manager       │   ✓   │   ✓   │   ✓   │   ✓*  │       │     │
│  │  Admin         │   ✓   │   ✓   │   ✓   │   ✓   │   ✓   │     │
│  │  Compliance    │   ✓   │   ✓   │   ✓   │   ✓   │   ✓   │     │
│  │                                                         │     │
│  │  * Requires additional justification / approval         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Access Requirements:                                            │
│  ├── Purpose limitation (must specify reason for access)        │
│  ├── Time-bound access (auto-revoke after period)               │
│  ├── Break-glass procedures for emergency access                │
│  ├── Manager approval for sensitive PII access                  │
│  └── Legal hold override capabilities                           │
│                                                                  │
│  Audit Trail:                                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Every PII access logged:                               │     │
│  │  {                                                      │     │
│  │    "timestamp": "2025-01-27T10:30:00Z",                │     │
│  │    "user_id": "uuid",                                  │     │
│  │    "action": "VIEW_UNMASKED_PII",                      │     │
│  │    "document_id": "uuid",                              │     │
│  │    "pii_types_accessed": ["SSN", "DOB"],               │     │
│  │    "justification": "Policy review requirement",       │     │
│  │    "ip_address": "192.168.1.100",                      │     │
│  │    "session_id": "uuid",                               │     │
│  │    "approval_id": "uuid" // if required                │     │
│  │  }                                                      │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### PII Data Model Extensions

```sql
-- PII Detection Results
CREATE TABLE pii_detections (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    pii_type VARCHAR(50) NOT NULL,          -- SSN, EMAIL, PHONE, etc.
    sensitivity_level INTEGER NOT NULL,      -- 1-4
    detection_method VARCHAR(50),            -- REGEX, NER, ML, CUSTOM
    confidence_score DECIMAL(5,4),           -- 0.0000 to 1.0000
    location_start INTEGER,                  -- Character offset start
    location_end INTEGER,                    -- Character offset end
    section_path VARCHAR(500),               -- Document section location
    token_id VARCHAR(100),                   -- Reference to token vault
    context_hash VARCHAR(64),                -- Hash of surrounding context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Token Vault (encrypted storage)
CREATE TABLE pii_token_vault (
    token_id VARCHAR(100) PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    encrypted_value BYTEA NOT NULL,          -- AES-256-GCM encrypted
    pii_type VARCHAR(50) NOT NULL,
    key_version INTEGER NOT NULL,            -- For key rotation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,     -- Auto-deletion
    access_count INTEGER DEFAULT 0
);

-- PII Access Requests (for privileged access)
CREATE TABLE pii_access_requests (
    id UUID PRIMARY KEY,
    requester_id UUID REFERENCES users(id),
    approver_id UUID REFERENCES users(id),
    document_id UUID REFERENCES documents(id),
    pii_types VARCHAR(50)[] NOT NULL,        -- Array of requested types
    justification TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',    -- pending, approved, denied
    access_window_start TIMESTAMP WITH TIME ZONE,
    access_window_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- PII Access Audit Log
CREATE TABLE pii_access_audit (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    document_id UUID REFERENCES documents(id),
    comparison_id UUID REFERENCES comparisons(id),
    action VARCHAR(50) NOT NULL,             -- VIEW, EXPORT, DETOKENIZE
    pii_types_accessed VARCHAR(50)[],
    access_level VARCHAR(50),                -- MASKED, PARTIAL, FULL
    access_request_id UUID REFERENCES pii_access_requests(id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for PII tables
CREATE INDEX idx_pii_detections_document ON pii_detections(document_id);
CREATE INDEX idx_pii_detections_type ON pii_detections(pii_type);
CREATE INDEX idx_pii_token_vault_tenant ON pii_token_vault(tenant_id);
CREATE INDEX idx_pii_access_audit_user_time ON pii_access_audit(user_id, created_at DESC);
CREATE INDEX idx_pii_access_audit_document ON pii_access_audit(document_id);
```

### PII API Endpoints

```yaml
# PII Management API

paths:
  # PII Detection
  /api/v1/documents/{id}/pii:
    get:
      summary: Get PII detection results for document
      description: Returns detected PII with masking based on user permissions
      parameters:
        - name: include_locations
          type: boolean
        - name: pii_types
          type: array
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  document_id:
                    type: string
                  pii_summary:
                    type: object
                    properties:
                      total_detections:
                        type: integer
                      by_type:
                        type: object
                      by_sensitivity:
                        type: object
                  detections:
                    type: array
                    items:
                      type: object
                      properties:
                        pii_type:
                          type: string
                        sensitivity_level:
                          type: integer
                        masked_value:
                          type: string
                        location:
                          type: object

  # PII Access Request
  /api/v1/pii/access-requests:
    post:
      summary: Request access to view unmasked PII
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - document_id
                - pii_types
                - justification
              properties:
                document_id:
                  type: string
                pii_types:
                  type: array
                  items:
                    type: string
                justification:
                  type: string
                duration_hours:
                  type: integer
                  default: 24

  /api/v1/pii/access-requests/{id}/approve:
    post:
      summary: Approve PII access request (manager only)

  /api/v1/pii/access-requests/{id}/deny:
    post:
      summary: Deny PII access request

  # PII Detokenization (privileged)
  /api/v1/pii/detokenize:
    post:
      summary: Retrieve original PII value from token
      description: Requires valid access request approval
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - token_ids
                - access_request_id
              properties:
                token_ids:
                  type: array
                  items:
                    type: string
                access_request_id:
                  type: string

  # Comparison with PII handling
  /api/v1/comparisons/{id}/results:
    get:
      summary: Get diff results with PII handling
      parameters:
        - name: pii_handling
          enum: [masked, redacted, tokenized, full]
          description: |
            - masked: Show partially masked PII
            - redacted: Remove all PII from output
            - tokenized: Replace PII with tokens
            - full: Show unmasked PII (requires authorization)
        - name: access_request_id
          description: Required for pii_handling=full

  # PII Reports
  /api/v1/reports/pii-exposure:
    get:
      summary: Generate PII exposure report
      description: Shows PII detected across documents and access patterns
      parameters:
        - name: start_date
        - name: end_date
        - name: tenant_id

  /api/v1/reports/pii-access-audit:
    get:
      summary: Generate PII access audit report
      description: Shows who accessed what PII and when
```

### PII Configuration (Tenant-level)

```json
{
  "pii_settings": {
    "detection": {
      "enabled": true,
      "auto_scan_on_upload": true,
      "detection_methods": ["regex", "ner", "ml"],
      "custom_patterns": [
        {
          "name": "EMPLOYEE_ID",
          "pattern": "EMP-\\d{6}",
          "sensitivity_level": 2
        }
      ],
      "confidence_threshold": 0.85
    },
    "protection": {
      "default_masking_strategy": "partial",
      "tokenization_enabled": true,
      "field_level_encryption": true,
      "auto_redact_on_export": false
    },
    "access_control": {
      "require_justification": true,
      "require_approval_for_sensitive": true,
      "max_access_duration_hours": 72,
      "auto_revoke_access": true
    },
    "retention": {
      "pii_token_retention_days": 365,
      "access_log_retention_days": 2555,
      "auto_purge_enabled": true
    },
    "notifications": {
      "notify_on_pii_detection": true,
      "notify_on_pii_access": true,
      "alert_threshold_detections": 100
    }
  }
}
```

### Technology Stack for PII

| Component | Technology | Purpose |
|-----------|------------|---------|
| **PII Detection** | Microsoft Presidio | ML-based entity recognition |
| **NER Engine** | spaCy / Stanza | Named entity extraction |
| **Pattern Matching** | Custom regex engine | Fast pattern detection |
| **Tokenization** | HashiCorp Vault Transit | Secure token generation |
| **Encryption** | AWS KMS / Azure Key Vault | Key management |
| **Field Encryption** | application-level AES-256 | Column-level protection |
| **Audit Logging** | Immutable audit trail | Compliance evidence |

---

## LLM Data Protection Architecture

### Overview

When using Large Language Models (LLMs) for semantic diff analysis, summarization, or intelligent document comparison, sensitive data must be protected from being transmitted to external AI providers. This section outlines a comprehensive strategy to prevent PII and confidential data leakage to LLMs.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           LLM DATA PROTECTION FRAMEWORK                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      PRE-PROCESSING LAYER                                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   PII       │  │   Data      │  │  Content    │  │   Prompt        │    │   │
│  │  │   Scrubbing │  │   Anonymiz. │  │  Filtering  │  │   Sanitization  │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      GATEWAY & ROUTING LAYER                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   LLM       │  │   Model     │  │  Data       │  │   Request       │    │   │
│  │  │   Proxy     │  │   Router    │  │  Residency  │  │   Validation    │    │   │
│  │  │   Gateway   │  │             │  │  Enforcer   │  │                 │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      MODEL DEPLOYMENT OPTIONS                                │   │
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │   │
│  │  │     SELF-HOSTED LLMs        │  │      EXTERNAL LLMs (Guarded)        │  │   │
│  │  │  ┌─────────┐  ┌─────────┐  │  │  ┌─────────┐  ┌─────────────────┐  │  │   │
│  │  │  │ Llama   │  │ Mistral │  │  │  │ OpenAI  │  │ Azure OpenAI    │  │  │   │
│  │  │  │ (Local) │  │ (Local) │  │  │  │  API    │  │ (Private Endpt) │  │  │   │
│  │  │  └─────────┘  └─────────┘  │  │  └─────────┘  └─────────────────┘  │  │   │
│  │  │                             │  │                                     │  │   │
│  │  │  ✓ Full data control       │  │  ⚠ Scrubbed data only              │  │   │
│  │  │  ✓ No external transfer    │  │  ⚠ Contractual protections         │  │   │
│  │  │  ✓ Compliance friendly     │  │  ⚠ Audit trail required            │  │   │
│  │  └─────────────────────────────┘  └─────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      POST-PROCESSING LAYER                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   Response  │  │   De-       │  │  Output     │  │   Audit &       │    │   │
│  │  │   Filtering │  │   Anonymize │  │  Validation │  │   Logging       │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Data Protection Strategies

#### 1. Pre-LLM Data Sanitization Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              Pre-LLM Sanitization Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input Document                                                  │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  STEP 1: PII Detection & Extraction                      │    │
│  │  ├── Run all PII detectors (regex, NER, ML)             │    │
│  │  ├── Build PII location map                             │    │
│  │  └── Assign sensitivity classifications                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  STEP 2: Entity Replacement Strategy                     │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  Original: "John Smith (SSN: 123-45-6789)       │    │    │
│  │  │            works at Acme Corp earning $150,000"  │    │    │
│  │  │                                                   │    │    │
│  │  │  Sanitized: "[PERSON_1] (SSN: [SSN_1])          │    │    │
│  │  │             works at [ORG_1] earning [SALARY_1]" │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                                                          │    │
│  │  Replacement Strategies:                                 │    │
│  │  ├── Placeholder tokens ([PERSON_1], [SSN_1])           │    │
│  │  ├── Synthetic data (fake but realistic values)         │    │
│  │  ├── Category labels ([NAME], [ADDRESS])                │    │
│  │  └── Hash-based pseudonyms (consistent replacement)     │    │
│  └─────────────────────────────────────────────────────────┘    │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  STEP 3: Context Preservation                            │    │
│  │  ├── Maintain document structure                        │    │
│  │  ├── Preserve semantic relationships                    │    │
│  │  ├── Keep section headers and formatting                │    │
│  │  └── Store replacement mapping for reconstruction       │    │
│  └─────────────────────────────────────────────────────────┘    │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  STEP 4: Final Validation                                │    │
│  │  ├── Re-scan for any missed PII                         │    │
│  │  ├── Verify no sensitive patterns remain                │    │
│  │  ├── Check for encoded/obfuscated data                  │    │
│  │  └── Validate replacement consistency                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│       │                                                          │
│       ▼                                                          │
│  Sanitized Document → Ready for LLM                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. LLM Proxy Gateway Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Proxy Gateway                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  All LLM requests MUST route through the proxy gateway          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Request Flow                          │    │
│  │                                                          │    │
│  │  Application                                             │    │
│  │       │                                                  │    │
│  │       ▼                                                  │    │
│  │  ┌─────────────┐                                        │    │
│  │  │  Request    │  ← Validate request structure          │    │
│  │  │  Validator  │  ← Check authorization                 │    │
│  │  └──────┬──────┘  ← Verify tenant permissions           │    │
│  │         │                                                │    │
│  │         ▼                                                │    │
│  │  ┌─────────────┐                                        │    │
│  │  │   Content   │  ← Scan prompt for PII                 │    │
│  │  │   Scanner   │  ← Detect sensitive patterns           │    │
│  │  └──────┬──────┘  ← Block/sanitize if found             │    │
│  │         │                                                │    │
│  │         ▼                                                │    │
│  │  ┌─────────────┐                                        │    │
│  │  │   Policy    │  ← Enforce data classification rules   │    │
│  │  │   Enforcer  │  ← Apply tenant-specific policies      │    │
│  │  └──────┬──────┘  ← Check regulatory compliance         │    │
│  │         │                                                │    │
│  │         ▼                                                │    │
│  │  ┌─────────────┐                                        │    │
│  │  │   Model     │  ← Route to appropriate LLM            │    │
│  │  │   Router    │  ← Self-hosted vs external             │    │
│  │  └──────┬──────┘  ← Based on data sensitivity           │    │
│  │         │                                                │    │
│  │         ▼                                                │    │
│  │  ┌─────────────┐                                        │    │
│  │  │   Audit     │  ← Log all requests (sanitized)        │    │
│  │  │   Logger    │  ← Track data flow                     │    │
│  │  └─────────────┘  ← Compliance evidence                 │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Blocking Rules:                                                 │
│  ├── Reject if PII detected and not sanitized                  │
│  ├── Reject if content exceeds sensitivity threshold           │
│  ├── Reject if tenant policy prohibits external LLM            │
│  ├── Reject if regulatory constraints not met                  │
│  └── Reject if audit trail cannot be maintained                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 3. Model Deployment Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│              LLM Routing Decision Matrix                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Data Sensitivity    │ Recommended Model    │ Requirements       │
│  ────────────────────┼─────────────────────┼──────────────────  │
│  PUBLIC              │ Any (External OK)    │ Basic logging      │
│  INTERNAL            │ External w/ contract │ DPA required       │
│  CONFIDENTIAL        │ Self-hosted only     │ No external        │
│  RESTRICTED/PII      │ Self-hosted + audit  │ Full isolation     │
│  REGULATED (HIPAA)   │ Self-hosted + BAA    │ Compliance cert    │
│                                                                  │
│  Routing Logic:                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  if data.sensitivity >= CONFIDENTIAL:                   │     │
│  │      route_to(self_hosted_llm)                         │     │
│  │  elif data.has_pii and not data.is_sanitized:          │     │
│  │      reject_request("PII must be sanitized")           │     │
│  │  elif tenant.requires_data_residency(region):          │     │
│  │      route_to(regional_llm_endpoint)                   │     │
│  │  elif data.is_sanitized:                               │     │
│  │      route_to(external_llm_with_audit)                 │     │
│  │  else:                                                  │     │
│  │      route_to(default_llm)                             │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Self-Hosted LLM Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                Self-Hosted LLM Infrastructure                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Benefits:                                                       │
│  ├── Complete data sovereignty                                  │
│  ├── No data leaves your infrastructure                         │
│  ├── Full audit control                                         │
│  ├── Compliance with strict regulations                         │
│  └── Customizable for domain-specific tasks                     │
│                                                                  │
│  Recommended Models:                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Model          │ Size    │ Use Case                   │     │
│  │  ────────────────────────────────────────────────────  │     │
│  │  Llama 3.1      │ 8B-70B  │ General semantic analysis  │     │
│  │  Mistral        │ 7B-22B  │ Fast inference, good qual. │     │
│  │  CodeLlama      │ 7B-34B  │ Code/technical policies    │     │
│  │  Phi-3          │ 3.8B    │ Lightweight, edge deploy   │     │
│  │  Qwen2          │ 7B-72B  │ Multi-language support     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Deployment Architecture:                                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │              Kubernetes Cluster                  │   │     │
│  │  │  ┌─────────────────────────────────────────┐    │   │     │
│  │  │  │         LLM Inference Pods              │    │   │     │
│  │  │  │  ┌───────┐  ┌───────┐  ┌───────┐      │    │   │     │
│  │  │  │  │ vLLM  │  │ vLLM  │  │ vLLM  │      │    │   │     │
│  │  │  │  │ Pod 1 │  │ Pod 2 │  │ Pod N │      │    │   │     │
│  │  │  │  │ GPU   │  │ GPU   │  │ GPU   │      │    │   │     │
│  │  │  │  └───────┘  └───────┘  └───────┘      │    │   │     │
│  │  │  └─────────────────────────────────────────┘    │   │     │
│  │  │                      │                          │   │     │
│  │  │                      ▼                          │   │     │
│  │  │  ┌─────────────────────────────────────────┐    │   │     │
│  │  │  │         Model Storage (NFS/S3)          │    │   │     │
│  │  │  │  - Model weights (encrypted at rest)    │    │   │     │
│  │  │  │  - Model versions                       │    │   │     │
│  │  │  │  - Fine-tuned adapters                  │    │   │     │
│  │  │  └─────────────────────────────────────────┘    │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Infrastructure Requirements:                                    │
│  ├── GPU nodes: NVIDIA A100/H100 for production                │
│  ├── Memory: 80GB+ VRAM for 70B models                         │
│  ├── Networking: Private VPC, no internet egress               │
│  └── Storage: High-speed NVMe for model loading                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### External LLM Safeguards

```
┌─────────────────────────────────────────────────────────────────┐
│           External LLM Provider Safeguards                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  When external LLMs must be used (sanitized data only):         │
│                                                                  │
│  1. CONTRACTUAL PROTECTIONS                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Required Agreements:                                   │     │
│  │  ├── Data Processing Agreement (DPA)                   │     │
│  │  ├── Business Associate Agreement (BAA) for HIPAA      │     │
│  │  ├── Standard Contractual Clauses (SCCs) for GDPR      │     │
│  │  ├── Zero data retention clause                        │     │
│  │  ├── No training on customer data clause               │     │
│  │  └── Breach notification requirements                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. TECHNICAL CONTROLS                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  API Configuration:                                     │     │
│  │  ├── Use Azure OpenAI Private Endpoints                │     │
│  │  ├── Enable "opt-out" of training data                 │     │
│  │  ├── Configure zero data retention                     │     │
│  │  ├── Use customer-managed encryption keys              │     │
│  │  └── Restrict to specific models/versions              │     │
│  │                                                         │     │
│  │  Network Security:                                      │     │
│  │  ├── VPC Private Link / Private Endpoints              │     │
│  │  ├── No public internet exposure                       │     │
│  │  ├── IP allowlisting                                   │     │
│  │  └── TLS 1.3 minimum                                   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. PROVIDER COMPARISON                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Provider        │ Data Ret. │ Training │ Private EP  │     │
│  │  ─────────────────────────────────────────────────────│     │
│  │  Azure OpenAI    │ Optional  │ Opt-out  │     ✓       │     │
│  │  AWS Bedrock     │ None      │ No       │     ✓       │     │
│  │  Google Vertex   │ Optional  │ Opt-out  │     ✓       │     │
│  │  OpenAI API      │ 30 days*  │ Opt-out  │     ✗       │     │
│  │  Anthropic API   │ 30 days*  │ Opt-out  │     ✗       │     │
│  │                                                         │     │
│  │  * Can be reduced with enterprise agreement            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Semantic Diff Without Exposing PII

```
┌─────────────────────────────────────────────────────────────────┐
│           PII-Safe Semantic Diff Workflow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Goal: Get semantic analysis without exposing sensitive data    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Document A                    Document B               │     │
│  │  "John Smith's policy          "John Smith's policy     │     │
│  │   covers medical at             covers medical at       │     │
│  │   123 Main St..."               456 Oak Ave..."         │     │
│  │       │                              │                  │     │
│  │       ▼                              ▼                  │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │              PII Extraction & Mapping            │   │     │
│  │  │                                                   │   │     │
│  │  │  Mapping Table (stored securely, never sent):    │   │     │
│  │  │  ┌─────────────────────────────────────────┐    │   │     │
│  │  │  │ Token      │ Doc A Value  │ Doc B Value │    │   │     │
│  │  │  │ [PERSON_1] │ John Smith   │ John Smith  │    │   │     │
│  │  │  │ [ADDR_1]   │ 123 Main St  │ 456 Oak Ave │    │   │     │
│  │  │  └─────────────────────────────────────────┘    │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  │       │                              │                  │     │
│  │       ▼                              ▼                  │     │
│  │  Sanitized A                    Sanitized B             │     │
│  │  "[PERSON_1]'s policy           "[PERSON_1]'s policy    │     │
│  │   covers medical at              covers medical at      │     │
│  │   [ADDR_1]..."                   [ADDR_1]..."           │     │
│  │       │                              │                  │     │
│  │       └──────────────┬───────────────┘                  │     │
│  │                      ▼                                  │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │              LLM Semantic Analysis               │   │     │
│  │  │                                                   │   │     │
│  │  │  Prompt: "Compare these policy documents and     │   │     │
│  │  │  identify semantic differences in coverage..."    │   │     │
│  │  │                                                   │   │     │
│  │  │  LLM Response: "The documents show a change in   │   │     │
│  │  │  [ADDR_1] which may indicate a location change   │   │     │
│  │  │  affecting coverage territory..."                 │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  │                      │                                  │     │
│  │                      ▼                                  │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │              Response Re-hydration               │   │     │
│  │  │                                                   │   │     │
│  │  │  Final Output (if user has permission):          │   │     │
│  │  │  "The documents show a change from 123 Main St   │   │     │
│  │  │  to 456 Oak Ave which may indicate a location    │   │     │
│  │  │  change affecting coverage territory..."          │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### LLM Audit & Monitoring

```
┌─────────────────────────────────────────────────────────────────┐
│                LLM Usage Audit & Monitoring                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Audit Log Schema:                                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  {                                                      │     │
│  │    "request_id": "uuid",                               │     │
│  │    "timestamp": "2025-01-27T10:30:00Z",                │     │
│  │    "tenant_id": "uuid",                                │     │
│  │    "user_id": "uuid",                                  │     │
│  │    "document_ids": ["uuid", "uuid"],                   │     │
│  │    "operation": "SEMANTIC_DIFF",                       │     │
│  │    "llm_provider": "self-hosted | azure | openai",     │     │
│  │    "model": "llama-3.1-70b",                           │     │
│  │    "data_classification": "CONFIDENTIAL",              │     │
│  │    "pii_detected": true,                               │     │
│  │    "pii_types": ["NAME", "ADDRESS", "SSN"],            │     │
│  │    "sanitization_applied": true,                       │     │
│  │    "tokens_replaced": 15,                              │     │
│  │    "prompt_hash": "sha256:abc123...",                  │     │
│  │    "response_hash": "sha256:def456...",                │     │
│  │    "routing_decision": "self-hosted",                  │     │
│  │    "routing_reason": "pii_detected",                   │     │
│  │    "latency_ms": 1250,                                 │     │
│  │    "tokens_in": 2500,                                  │     │
│  │    "tokens_out": 500                                   │     │
│  │  }                                                      │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Monitoring Dashboards:                                          │
│  ├── LLM requests by data sensitivity level                     │
│  ├── PII detection rate in LLM requests                         │
│  ├── Sanitization effectiveness metrics                         │
│  ├── External vs self-hosted routing ratio                      │
│  ├── Blocked requests (policy violations)                       │
│  └── Cost tracking by tenant/operation                          │
│                                                                  │
│  Alerts:                                                         │
│  ├── PII detected in request to external LLM                    │
│  ├── Sanitization bypass attempt                                │
│  ├── Unusual LLM usage patterns                                 │
│  ├── High volume of blocked requests                            │
│  └── Self-hosted LLM performance degradation                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model for LLM Protection

```sql
-- LLM Request Audit Log
CREATE TABLE llm_request_audit (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    comparison_id UUID REFERENCES comparisons(id),
    request_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Request details
    operation VARCHAR(50) NOT NULL,          -- SEMANTIC_DIFF, SUMMARIZE, etc.
    llm_provider VARCHAR(50) NOT NULL,       -- self-hosted, azure, openai
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),

    -- Data classification
    data_classification VARCHAR(50) NOT NULL,
    source_documents UUID[],

    -- PII handling
    pii_detected BOOLEAN DEFAULT FALSE,
    pii_types_detected VARCHAR(50)[],
    sanitization_applied BOOLEAN DEFAULT FALSE,
    tokens_replaced INTEGER DEFAULT 0,

    -- Routing
    routing_decision VARCHAR(50) NOT NULL,
    routing_reason VARCHAR(200),

    -- Content hashes (for audit, not content itself)
    prompt_hash VARCHAR(64),
    response_hash VARCHAR(64),

    -- Metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    latency_ms INTEGER,

    -- Status
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT
);

-- LLM Sanitization Mappings (temporary, auto-deleted)
CREATE TABLE llm_sanitization_mappings (
    id UUID PRIMARY KEY,
    request_id UUID REFERENCES llm_request_audit(id) ON DELETE CASCADE,
    token_placeholder VARCHAR(100) NOT NULL,
    pii_type VARCHAR(50) NOT NULL,
    -- Encrypted reference to actual value (not the value itself)
    value_reference_encrypted BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL  -- Auto-purge
);

-- LLM Policy Rules
CREATE TABLE llm_routing_policies (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    policy_name VARCHAR(200) NOT NULL,
    priority INTEGER DEFAULT 100,

    -- Conditions
    data_classification_min VARCHAR(50),
    pii_types_blocked VARCHAR(50)[],
    regulatory_requirements VARCHAR(50)[],

    -- Actions
    allowed_providers VARCHAR(50)[],
    require_sanitization BOOLEAN DEFAULT TRUE,
    require_approval BOOLEAN DEFAULT FALSE,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_llm_audit_tenant_time ON llm_request_audit(tenant_id, request_timestamp DESC);
CREATE INDEX idx_llm_audit_pii ON llm_request_audit(pii_detected, sanitization_applied);
CREATE INDEX idx_llm_mappings_expires ON llm_sanitization_mappings(expires_at);
```

### Configuration

```json
{
  "llm_protection_settings": {
    "global": {
      "require_sanitization_for_external": true,
      "default_routing": "self-hosted",
      "max_prompt_length": 100000,
      "audit_all_requests": true
    },
    "sanitization": {
      "enabled": true,
      "methods": ["placeholder", "synthetic"],
      "preserve_format": true,
      "double_check_before_send": true,
      "replacement_style": "placeholder"
    },
    "self_hosted": {
      "enabled": true,
      "endpoint": "http://llm-service.internal:8080",
      "models": ["llama-3.1-70b", "mistral-7b"],
      "default_model": "llama-3.1-70b",
      "max_concurrent_requests": 50
    },
    "external_providers": {
      "azure_openai": {
        "enabled": true,
        "endpoint": "https://your-resource.openai.azure.com",
        "allowed_for_classifications": ["PUBLIC", "INTERNAL"],
        "require_sanitization": true,
        "data_retention": "none"
      },
      "openai": {
        "enabled": false,
        "reason": "No private endpoint available"
      }
    },
    "routing_rules": [
      {
        "condition": "data_classification >= CONFIDENTIAL",
        "action": "route_to_self_hosted",
        "allow_override": false
      },
      {
        "condition": "pii_detected AND NOT sanitized",
        "action": "block",
        "message": "PII must be sanitized before LLM processing"
      },
      {
        "condition": "tenant.requires_data_residency",
        "action": "route_to_regional_endpoint"
      }
    ],
    "monitoring": {
      "log_prompts": false,
      "log_responses": false,
      "log_hashes": true,
      "alert_on_pii_to_external": true,
      "alert_on_sanitization_failure": true
    }
  }
}
```

### Technology Stack for LLM Protection

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM Proxy** | Custom gateway (FastAPI) | Request routing, validation |
| **Self-hosted LLM** | vLLM / Text Generation Inference | High-performance inference |
| **Models** | Llama 3.1, Mistral, Phi-3 | Open-weight models |
| **Sanitization** | Microsoft Presidio + custom | PII replacement |
| **Token Vault** | Redis (encrypted) | Temporary mapping storage |
| **Audit DB** | PostgreSQL | Request logging |
| **Monitoring** | Prometheus + Grafana | Usage metrics |
| **GPU Infrastructure** | NVIDIA A100/H100 | Model inference |

---

## RAG (Retrieval-Augmented Generation) Architecture

### Overview

The RAG component enhances semantic diff quality by providing contextual knowledge about policy terminology, regulatory requirements, standard clauses, and historical comparison patterns. This enables more accurate and contextually-aware document comparison.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              RAG ARCHITECTURE                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         KNOWLEDGE SOURCES                                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │  Policy     │  │  Regulatory │  │  Industry   │  │   Historical    │    │   │
│  │  │  Templates  │  │  Documents  │  │  Standards  │  │   Comparisons   │    │   │
│  │  │             │  │  (HIPAA,    │  │  (ISO,NIST) │  │   & Feedback    │    │   │
│  │  │             │  │   GDPR)     │  │             │  │                 │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         INGESTION PIPELINE                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │  Document   │  │   Chunk     │  │  Embedding  │  │   Metadata      │    │   │
│  │  │  Parser     │──▶│  Strategy  │──▶│  Generation │──▶│   Enrichment   │    │   │
│  │  │             │  │             │  │             │  │                 │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         VECTOR STORE                                         │   │
│  │  ┌───────────────────────────────────────────────────────────────────────┐  │   │
│  │  │                                                                        │  │   │
│  │  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │   │
│  │  │   │  Policy Clause  │  │   Regulatory    │  │   Comparison    │      │  │   │
│  │  │   │   Embeddings    │  │   Reference     │  │    Patterns     │      │  │   │
│  │  │   │   Collection    │  │   Collection    │  │   Collection    │      │  │   │
│  │  │   └─────────────────┘  └─────────────────┘  └─────────────────┘      │  │   │
│  │  │                                                                        │  │   │
│  │  │   Vector DB: Pinecone / Weaviate / pgvector / Qdrant                  │  │   │
│  │  └───────────────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         RETRIEVAL & GENERATION                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │   │
│  │  │   Query     │  │  Semantic   │  │  Context    │  │   Augmented     │    │   │
│  │  │  Embedding  │──▶│   Search   │──▶│  Assembly  │──▶│   Generation    │    │   │
│  │  │             │  │  + Rerank   │  │             │  │                 │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Knowledge Base Collections

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Knowledge Collections                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. POLICY CLAUSE LIBRARY                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Purpose: Standard policy language reference            │     │
│  │                                                         │     │
│  │  Contents:                                              │     │
│  │  ├── Standard clause templates by policy type           │     │
│  │  ├── Industry-specific terminology definitions          │     │
│  │  ├── Common clause variations and equivalents           │     │
│  │  ├── Boilerplate vs substantive language markers       │     │
│  │  └── Clause importance/criticality ratings              │     │
│  │                                                         │     │
│  │  Use Case: Identify if a change is:                     │     │
│  │  • Standard language update (low significance)          │     │
│  │  • Substantive coverage change (high significance)      │     │
│  │  • Regulatory compliance update (medium significance)   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. REGULATORY REFERENCE LIBRARY                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Purpose: Compliance and regulatory context             │     │
│  │                                                         │     │
│  │  Contents:                                              │     │
│  │  ├── HIPAA requirements and safe harbor provisions      │     │
│  │  ├── GDPR articles and recitals                        │     │
│  │  ├── State-specific insurance regulations               │     │
│  │  ├── Industry compliance standards (PCI-DSS, SOX)       │     │
│  │  └── Recent regulatory updates and effective dates      │     │
│  │                                                         │     │
│  │  Use Case: Identify if a change:                        │     │
│  │  • Affects regulatory compliance                        │     │
│  │  • Aligns with recent regulatory updates                │     │
│  │  • Creates potential compliance gaps                    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. HISTORICAL COMPARISON PATTERNS                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Purpose: Learn from past comparisons and feedback      │     │
│  │                                                         │     │
│  │  Contents:                                              │     │
│  │  ├── Previous diff results with human annotations       │     │
│  │  ├── False positive patterns (changes marked trivial)   │     │
│  │  ├── False negative patterns (missed important changes) │     │
│  │  ├── User feedback on diff significance ratings         │     │
│  │  └── Domain expert corrections and overrides            │     │
│  │                                                         │     │
│  │  Use Case: Improve accuracy by:                         │     │
│  │  • Recognizing previously seen change patterns          │     │
│  │  • Adjusting significance based on historical feedback  │     │
│  │  • Reducing known false positive triggers               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  4. SEMANTIC EQUIVALENCE MAPPINGS                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Purpose: Detect meaning-preserving rewrites            │     │
│  │                                                         │     │
│  │  Contents:                                              │     │
│  │  ├── Synonym mappings for policy terminology            │     │
│  │  ├── Equivalent phrase patterns                         │     │
│  │  ├── Legal language normalization rules                 │     │
│  │  └── Style variation vs meaning change indicators       │     │
│  │                                                         │     │
│  │  Example:                                               │     │
│  │  "shall not exceed" ≈ "must not be greater than"       │     │
│  │  "within 30 days" ≈ "no later than thirty (30) days"   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### RAG-Enhanced Semantic Diff Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              RAG-Enhanced Diff Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 1: Initial Diff Detection                         │     │
│  │                                                          │     │
│  │  Document A          Document B                          │     │
│  │       │                   │                              │     │
│  │       └───────┬───────────┘                              │     │
│  │               ▼                                          │     │
│  │    ┌─────────────────────┐                              │     │
│  │    │  Text Diff Engine   │  → Identify changed sections │     │
│  │    └─────────────────────┘                              │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 2: Context Retrieval (RAG)                        │     │
│  │                                                          │     │
│  │  For each changed section:                               │     │
│  │  ┌─────────────────────────────────────────────────┐    │     │
│  │  │                                                   │    │     │
│  │  │  Query: "Coverage limit changed from $1M to $2M" │    │     │
│  │  │                    │                              │    │     │
│  │  │                    ▼                              │    │     │
│  │  │  ┌─────────────────────────────────────────┐    │    │     │
│  │  │  │         Vector Search Results            │    │    │     │
│  │  │  │                                          │    │    │     │
│  │  │  │  1. Similar clause from template library │    │    │     │
│  │  │  │  2. Regulatory requirement reference     │    │    │     │
│  │  │  │  3. Historical feedback on similar change│    │    │     │
│  │  │  │  4. Semantic equivalence mappings        │    │    │     │
│  │  │  └─────────────────────────────────────────┘    │    │     │
│  │  │                                                   │    │     │
│  │  └─────────────────────────────────────────────────┘    │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 3: Augmented LLM Analysis                         │     │
│  │                                                          │     │
│  │  ┌─────────────────────────────────────────────────┐    │     │
│  │  │  Prompt Construction:                            │    │     │
│  │  │                                                   │    │     │
│  │  │  """                                              │    │     │
│  │  │  CONTEXT FROM KNOWLEDGE BASE:                    │    │     │
│  │  │  - This clause type typically indicates [...]    │    │     │
│  │  │  - Regulatory requirement: [...]                 │    │     │
│  │  │  - Similar changes were rated as [significance]  │    │     │
│  │  │  - Historical feedback: [...]                    │    │     │
│  │  │                                                   │    │     │
│  │  │  CHANGE DETECTED:                                │    │     │
│  │  │  - Old: "Coverage limit: $1,000,000"            │    │     │
│  │  │  - New: "Coverage limit: $2,000,000"            │    │     │
│  │  │                                                   │    │     │
│  │  │  TASK: Analyze the semantic significance of      │    │     │
│  │  │  this change considering the context provided.   │    │     │
│  │  │  """                                              │    │     │
│  │  └─────────────────────────────────────────────────┘    │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 4: Structured Output                              │     │
│  │                                                          │     │
│  │  {                                                       │     │
│  │    "change_id": "uuid",                                 │     │
│  │    "change_type": "COVERAGE_MODIFICATION",              │     │
│  │    "significance": "HIGH",                              │     │
│  │    "confidence": 0.92,                                  │     │
│  │    "analysis": "Coverage limit doubled...",            │     │
│  │    "regulatory_impact": ["State filing required"],     │     │
│  │    "similar_historical_changes": 15,                   │     │
│  │    "historical_accuracy": 0.89,                        │     │
│  │    "recommended_action": "REVIEW_REQUIRED",            │     │
│  │    "supporting_references": [...]                      │     │
│  │  }                                                       │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Chunking Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Document Chunking Strategy                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Policy documents require semantic-aware chunking:               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  HIERARCHICAL CHUNKING                                  │     │
│  │                                                         │     │
│  │  Level 1: Document                                      │     │
│  │    └── Level 2: Section/Article                        │     │
│  │          └── Level 3: Clause/Paragraph                 │     │
│  │                └── Level 4: Sub-clause                 │     │
│  │                                                         │     │
│  │  Each chunk retains:                                    │     │
│  │  ├── Parent section context                            │     │
│  │  ├── Document metadata                                 │     │
│  │  ├── Clause numbering/reference                        │     │
│  │  └── Semantic boundaries (not mid-sentence)            │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Chunking Parameters:                                            │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Parameter            │ Value   │ Rationale            │     │
│  │  ─────────────────────┼─────────┼─────────────────────│     │
│  │  chunk_size           │ 512     │ Optimal for embedding│     │
│  │  chunk_overlap        │ 50      │ Context preservation │     │
│  │  separator_priority   │ section │ Semantic boundaries  │     │
│  │  min_chunk_size       │ 100     │ Avoid tiny fragments │     │
│  │  preserve_formatting  │ true    │ Lists, tables intact │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Special Handling:                                               │
│  ├── Tables: Keep as single chunk with structured metadata      │
│  ├── Definitions: Cross-reference to usage locations            │
│  ├── References: Link to referenced sections                    │
│  └── Amendments: Track version lineage                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Embedding Model Selection

```
┌─────────────────────────────────────────────────────────────────┐
│                    Embedding Model Comparison                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Model              │ Dims │ Context │ Best For        │ Cost  │
│  ──────────────────────────────────────────────────────────────│
│  text-embedding-3-large │ 3072 │ 8191  │ High accuracy   │ $$$  │
│  text-embedding-3-small │ 1536 │ 8191  │ Cost-effective  │ $    │
│  voyage-law-2       │ 1024 │ 16000 │ Legal documents │ $$   │
│  BGE-large-en-v1.5  │ 1024 │ 512   │ Self-hosted     │ Free │
│  E5-large-v2        │ 1024 │ 512   │ Self-hosted     │ Free │
│  GTE-large          │ 1024 │ 512   │ Self-hosted     │ Free │
│                                                                  │
│  Recommended: voyage-law-2 for legal/policy documents           │
│  Alternative: BGE-large for self-hosted deployments             │
│                                                                  │
│  Hybrid Search Strategy:                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Query: "deductible modification clause"                │     │
│  │           │                                             │     │
│  │           ├──▶ Dense Search (Embeddings)               │     │
│  │           │    └── Semantic similarity                 │     │
│  │           │                                             │     │
│  │           ├──▶ Sparse Search (BM25)                    │     │
│  │           │    └── Keyword matching                    │     │
│  │           │                                             │     │
│  │           └──▶ Reciprocal Rank Fusion                  │     │
│  │                └── Combined ranking                    │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### RAG Data Model

```sql
-- Vector store collections metadata
CREATE TABLE rag_collections (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    collection_name VARCHAR(100) NOT NULL,
    collection_type VARCHAR(50) NOT NULL,  -- policy_clauses, regulatory, historical
    embedding_model VARCHAR(100) NOT NULL,
    embedding_dimensions INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks for RAG
CREATE TABLE rag_chunks (
    id UUID PRIMARY KEY,
    collection_id UUID REFERENCES rag_collections(id),
    source_document_id UUID,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,

    -- Hierarchical context
    section_path VARCHAR(500),
    parent_chunk_id UUID REFERENCES rag_chunks(id),

    -- Metadata for filtering
    document_type VARCHAR(100),
    policy_type VARCHAR(100),
    jurisdiction VARCHAR(100),
    effective_date DATE,

    -- Embedding stored in vector DB, reference here
    vector_id VARCHAR(200),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RAG retrieval audit
CREATE TABLE rag_retrieval_audit (
    id UUID PRIMARY KEY,
    comparison_id UUID REFERENCES comparisons(id),
    query_text TEXT NOT NULL,
    query_embedding_model VARCHAR(100),

    -- Retrieved chunks
    retrieved_chunk_ids UUID[],
    retrieval_scores DECIMAL(5,4)[],

    -- Reranking
    reranked_chunk_ids UUID[],
    rerank_model VARCHAR(100),

    -- Usage
    chunks_used_in_prompt INTEGER,
    total_context_tokens INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rag_chunks_collection ON rag_chunks(collection_id);
CREATE INDEX idx_rag_chunks_document ON rag_chunks(source_document_id);
CREATE INDEX idx_rag_chunks_type ON rag_chunks(document_type, policy_type);
```

---

## Semantic Diff Evaluation Framework

### Overview

Evaluating semantic diff accuracy is critical for production reliability. This framework measures precision, recall, and provides mechanisms to continuously improve through human feedback.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         EVALUATION FRAMEWORK                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         METRICS HIERARCHY                                    │   │
│  │                                                                              │   │
│  │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐      │   │
│  │   │   DETECTION     │   │  CLASSIFICATION │   │   SIGNIFICANCE      │      │   │
│  │   │   ACCURACY      │   │   ACCURACY      │   │   ACCURACY          │      │   │
│  │   │                 │   │                 │   │                     │      │   │
│  │   │ • Precision     │   │ • Change type   │   │ • Impact rating     │      │   │
│  │   │ • Recall        │   │   accuracy      │   │   correlation       │      │   │
│  │   │ • F1 Score      │   │ • Multi-label   │   │ • Priority ranking  │      │   │
│  │   │                 │   │   F1            │   │   accuracy          │      │   │
│  │   └─────────────────┘   └─────────────────┘   └─────────────────────┘      │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### False Positives & False Negatives

```
┌─────────────────────────────────────────────────────────────────┐
│           False Positive / False Negative Analysis               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CONFUSION MATRIX FOR SEMANTIC DIFF                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │                    ACTUAL (Human Judgment)              │     │
│  │                    ─────────────────────────           │     │
│  │                    │ Significant │ Not Signif. │       │     │
│  │  ┌─────────────────┼─────────────┼─────────────┤       │     │
│  │  │ PREDICTED       │             │             │       │     │
│  │  │ ────────────────┼─────────────┼─────────────┤       │     │
│  │  │ Significant     │     TP      │     FP      │       │     │
│  │  │                 │  (Correct)  │ (False Pos) │       │     │
│  │  │ ────────────────┼─────────────┼─────────────┤       │     │
│  │  │ Not Significant │     FN      │     TN      │       │     │
│  │  │                 │ (False Neg) │  (Correct)  │       │     │
│  │  └─────────────────┴─────────────┴─────────────┘       │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  FALSE POSITIVES (Type I Error)                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Definition: System flags a change as significant       │     │
│  │              when it's actually trivial                 │     │
│  │                                                         │     │
│  │  Common Causes:                                         │     │
│  │  ├── Formatting-only changes flagged as semantic       │     │
│  │  │   Example: "Section 1" → "SECTION 1"                │     │
│  │  │                                                      │     │
│  │  ├── Synonym substitution flagged as meaning change    │     │
│  │  │   Example: "shall" → "will" (often equivalent)      │     │
│  │  │                                                      │     │
│  │  ├── Reordering without meaning change                 │     │
│  │  │   Example: Clause order swapped, same content       │     │
│  │  │                                                      │     │
│  │  ├── Punctuation/whitespace changes                    │     │
│  │  │   Example: "30 days" → "30-days"                    │     │
│  │  │                                                      │     │
│  │  ├── Legal boilerplate updates                         │     │
│  │  │   Example: Standard liability language refresh      │     │
│  │  │                                                      │     │
│  │  └── Date/version number updates                       │     │
│  │      Example: "Effective 2024" → "Effective 2025"      │     │
│  │                                                         │     │
│  │  Business Impact: Wastes reviewer time, alert fatigue  │     │
│  │  Target FP Rate: < 10%                                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  FALSE NEGATIVES (Type II Error)                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Definition: System misses a significant change,        │     │
│  │              marking it as trivial or not detecting it  │     │
│  │                                                         │     │
│  │  Common Causes:                                         │     │
│  │  ├── Subtle numerical changes                          │     │
│  │  │   Example: "Coverage: $1,000,000" → "$100,000"      │     │
│  │  │   (Missing a zero - 10x difference!)                │     │
│  │  │                                                      │     │
│  │  ├── Negation insertion/removal                        │     │
│  │  │   Example: "is covered" → "is not covered"          │     │
│  │  │                                                      │     │
│  │  ├── Scope modifications                               │     │
│  │  │   Example: "all employees" → "full-time employees"  │     │
│  │  │                                                      │     │
│  │  ├── Conditional changes                               │     │
│  │  │   Example: "covered" → "covered if pre-approved"    │     │
│  │  │                                                      │     │
│  │  ├── Definition changes affecting multiple clauses     │     │
│  │  │   Example: Redefining "dependent" to exclude adults │     │
│  │  │                                                      │     │
│  │  ├── Exclusion additions buried in text                │     │
│  │  │   Example: New exclusion added to long list         │     │
│  │  │                                                      │     │
│  │  └── Cross-reference changes                           │     │
│  │      Example: "per Section 3.1" → "per Section 3.2"    │     │
│  │      (Different section, different terms!)              │     │
│  │                                                         │     │
│  │  Business Impact: CRITICAL - missed changes = risk     │     │
│  │  Target FN Rate: < 2% (much stricter than FP)          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Evaluation Metrics

```
┌─────────────────────────────────────────────────────────────────┐
│                    Evaluation Metrics                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CORE METRICS                                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Precision = TP / (TP + FP)                            │     │
│  │  "Of changes flagged as significant, how many truly are?"│    │
│  │  Target: > 90%                                          │     │
│  │                                                         │     │
│  │  Recall = TP / (TP + FN)                               │     │
│  │  "Of all significant changes, how many did we catch?"  │     │
│  │  Target: > 98% (prioritize not missing changes)        │     │
│  │                                                         │     │
│  │  F1 Score = 2 * (Precision * Recall) / (Prec + Recall) │     │
│  │  "Harmonic mean balancing precision and recall"        │     │
│  │  Target: > 93%                                          │     │
│  │                                                         │     │
│  │  F2 Score = 5 * (Prec * Recall) / (4*Prec + Recall)    │     │
│  │  "Recall-weighted F-score (penalizes FN more)"         │     │
│  │  Target: > 95%                                          │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ADVANCED METRICS                                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Significance Correlation (Spearman's ρ)               │     │
│  │  ├── Compares predicted significance score vs human    │     │
│  │  ├── Range: -1 to 1 (1 = perfect correlation)          │     │
│  │  └── Target: > 0.85                                    │     │
│  │                                                         │     │
│  │  Ranking Accuracy (NDCG@k)                             │     │
│  │  ├── How well are changes prioritized?                 │     │
│  │  ├── Top-k changes should be most significant          │     │
│  │  └── Target: > 0.90 for NDCG@10                        │     │
│  │                                                         │     │
│  │  Category Accuracy (Multi-label)                       │     │
│  │  ├── Coverage, Exclusion, Limit, Definition, etc.      │     │
│  │  ├── Micro-F1 across all categories                    │     │
│  │  └── Target: > 85%                                     │     │
│  │                                                         │     │
│  │  Confidence Calibration (ECE)                          │     │
│  │  ├── Is 90% confidence actually 90% accurate?          │     │
│  │  ├── Expected Calibration Error                        │     │
│  │  └── Target: ECE < 0.05                                │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  OPERATIONAL METRICS                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Review Efficiency                                      │     │
│  │  ├── Time saved vs manual review                       │     │
│  │  ├── Changes requiring human override                  │     │
│  │  └── Target: > 70% time reduction                      │     │
│  │                                                         │     │
│  │  Alert Quality                                          │     │
│  │  ├── High-priority alerts that were truly high-priority│     │
│  │  ├── Alert fatigue score (FP rate for high-severity)   │     │
│  │  └── Target: < 5% high-severity FP rate                │     │
│  │                                                         │     │
│  │  Coverage by Document Type                              │     │
│  │  ├── Performance breakdown by policy type              │     │
│  │  ├── Identify weak areas needing improvement           │     │
│  │  └── Target: No category below 85% F1                  │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Ground Truth Dataset

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ground Truth Dataset                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Dataset Structure:                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  evaluation_dataset/                                    │     │
│  │  ├── documents/                                        │     │
│  │  │   ├── pair_001/                                     │     │
│  │  │   │   ├── document_a.pdf                           │     │
│  │  │   │   ├── document_b.pdf                           │     │
│  │  │   │   └── annotations.json                         │     │
│  │  │   ├── pair_002/                                     │     │
│  │  │   └── ...                                           │     │
│  │  ├── metadata.json                                     │     │
│  │  └── splits/                                           │     │
│  │      ├── train.json  (60%)                            │     │
│  │      ├── val.json    (20%)                            │     │
│  │      └── test.json   (20%)                            │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Annotation Schema:                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  {                                                      │     │
│  │    "pair_id": "pair_001",                              │     │
│  │    "document_type": "health_insurance_policy",         │     │
│  │    "annotators": ["expert_1", "expert_2"],             │     │
│  │    "inter_annotator_agreement": 0.92,                  │     │
│  │    "changes": [                                         │     │
│  │      {                                                  │     │
│  │        "change_id": "c001",                            │     │
│  │        "location_a": {"section": "3.1", "para": 2},   │     │
│  │        "location_b": {"section": "3.1", "para": 2},   │     │
│  │        "text_a": "Coverage limit: $500,000",          │     │
│  │        "text_b": "Coverage limit: $1,000,000",        │     │
│  │        "change_type": ["COVERAGE_LIMIT"],              │     │
│  │        "significance": "HIGH",                         │     │
│  │        "significance_score": 0.95,                     │     │
│  │        "semantic_change": true,                        │     │
│  │        "requires_review": true,                        │     │
│  │        "regulatory_impact": false,                     │     │
│  │        "explanation": "Coverage doubled - material"    │     │
│  │      },                                                 │     │
│  │      {                                                  │     │
│  │        "change_id": "c002",                            │     │
│  │        "text_a": "Section 5",                          │     │
│  │        "text_b": "SECTION 5",                          │     │
│  │        "change_type": ["FORMATTING"],                  │     │
│  │        "significance": "NONE",                         │     │
│  │        "significance_score": 0.0,                      │     │
│  │        "semantic_change": false,                       │     │
│  │        "requires_review": false                        │     │
│  │      }                                                  │     │
│  │    ]                                                    │     │
│  │  }                                                      │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Dataset Requirements:                                           │
│  ├── Minimum 500 document pairs for statistical significance    │
│  ├── Stratified by document type, change type, significance     │
│  ├── Multiple expert annotators with agreement metrics          │
│  ├── Regular updates with new edge cases                        │
│  └── Versioned for reproducibility                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Automated Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              Automated Evaluation Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────────────┐    │     │
│  │  │  Test   │───▶│  Diff   │───▶│   Compare to    │    │     │
│  │  │ Dataset │    │ Engine  │    │  Ground Truth   │    │     │
│  │  └─────────┘    └─────────┘    └────────┬────────┘    │     │
│  │                                          │             │     │
│  │                                          ▼             │     │
│  │  ┌───────────────────────────────────────────────┐    │     │
│  │  │           Metrics Calculation                  │    │     │
│  │  │                                                │    │     │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │    │     │
│  │  │  │Precision│  │ Recall  │  │Significance │   │    │     │
│  │  │  │ /Recall │  │ by Type │  │ Correlation │   │    │     │
│  │  │  └─────────┘  └─────────┘  └─────────────┘   │    │     │
│  │  └───────────────────────────────────────────────┘    │     │
│  │                          │                             │     │
│  │                          ▼                             │     │
│  │  ┌───────────────────────────────────────────────┐    │     │
│  │  │           Reporting & Alerting                 │    │     │
│  │  │                                                │    │     │
│  │  │  • Dashboard update                            │    │     │
│  │  │  • Regression alerts                           │    │     │
│  │  │  • CI/CD gate (fail if below threshold)       │    │     │
│  │  │  • Detailed error analysis                     │    │     │
│  │  └───────────────────────────────────────────────┘    │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  CI/CD Integration:                                              │
│  ├── Run on every model/prompt change                           │
│  ├── Block deployment if recall < 98%                           │
│  ├── Warn if precision drops > 5%                               │
│  └── Generate comparison reports vs baseline                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Human-in-the-Loop (HITL) Review System

### Overview

The HITL system captures expert feedback on diff results to continuously improve model accuracy, adjust thresholds, and build training data for future model improvements.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      HUMAN-IN-THE-LOOP ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FEEDBACK COLLECTION                                  │   │
│  │                                                                              │   │
│  │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐      │   │
│  │   │   Review UI     │   │  Inline         │   │   Batch Review      │      │   │
│  │   │   (Per Change)  │   │  Corrections    │   │   Queue             │      │   │
│  │   │                 │   │                 │   │                     │      │   │
│  │   │ • Agree/Disagree│   │ • Edit signif.  │   │ • Expert review     │      │   │
│  │   │ • Rate severity │   │ • Reclassify    │   │ • Quality sampling  │      │   │
│  │   │ • Add comments  │   │ • Mark FP/FN    │   │ • Edge case triage  │      │   │
│  │   └─────────────────┘   └─────────────────┘   └─────────────────────┘      │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FEEDBACK PROCESSING                                  │   │
│  │                                                                              │   │
│  │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐      │   │
│  │   │   Aggregation   │   │   Conflict      │   │   Pattern           │      │   │
│  │   │   & Consensus   │   │   Resolution    │   │   Extraction        │      │   │
│  │   │                 │   │                 │   │                     │      │   │
│  │   │ • Multi-reviewer│   │ • Expert tiebreak│  │ • Common FP/FN      │      │   │
│  │   │ • Weighted votes│   │ • Escalation    │   │ • Threshold drift   │      │   │
│  │   │ • Agreement calc│   │                 │   │ • Edge cases        │      │   │
│  │   └─────────────────┘   └─────────────────┘   └─────────────────────┘      │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                           │
│                                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         MODEL IMPROVEMENT                                    │   │
│  │                                                                              │   │
│  │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐      │   │
│  │   │   Threshold     │   │   RAG Knowledge │   │   Fine-tuning       │      │   │
│  │   │   Adjustment    │   │   Update        │   │   Data Generation   │      │   │
│  │   │                 │   │                 │   │                     │      │   │
│  │   │ • Auto-tune     │   │ • Add patterns  │   │ • Training pairs    │      │   │
│  │   │ • A/B testing   │   │ • Update refs   │   │ • RLHF candidates   │      │   │
│  │   │ • Rollback      │   │ • Semantic equiv│   │ • DPO dataset       │      │   │
│  │   └─────────────────┘   └─────────────────┘   └─────────────────────┘      │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Feedback Collection Interface

```
┌─────────────────────────────────────────────────────────────────┐
│                    Review Interface Design                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Per-Change Review Widget:                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  CHANGE #1                           [HIGH] 0.92  │  │     │
│  │  │  ────────────────────────────────────────────────│  │     │
│  │  │  Section: 4.2 Coverage Limits                    │  │     │
│  │  │                                                   │  │     │
│  │  │  - "Maximum benefit: $500,000 per occurrence"    │  │     │
│  │  │  + "Maximum benefit: $1,000,000 per occurrence"  │  │     │
│  │  │                                                   │  │     │
│  │  │  System Analysis:                                 │  │     │
│  │  │  "Coverage limit doubled - significant change    │  │     │
│  │  │   affecting policy value"                         │  │     │
│  │  │                                                   │  │     │
│  │  │  ─────────────────────────────────────────────── │  │     │
│  │  │  Your Assessment:                                 │  │     │
│  │  │                                                   │  │     │
│  │  │  Significance: [✓] Agree  [ ] Disagree           │  │     │
│  │  │                                                   │  │     │
│  │  │  If disagree, correct rating:                    │  │     │
│  │  │  [ ] Critical [ ] High [●] Medium [ ] Low [ ] None│  │     │
│  │  │                                                   │  │     │
│  │  │  Change Type: [✓] Coverage [✓] Limit [ ] Exclusion│  │     │
│  │  │                                                   │  │     │
│  │  │  Comments: [Optional feedback________________]    │  │     │
│  │  │                                                   │  │     │
│  │  │  [Submit Feedback]  [Skip]  [Flag for Expert]    │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Quick Actions:                                                  │
│  ├── ✓ Agree (Keyboard: A) - Confirm system assessment          │
│  ├── ✗ Disagree (Keyboard: D) - Open correction panel           │
│  ├── → Skip (Keyboard: S) - Move to next                        │
│  ├── ! Flag (Keyboard: F) - Escalate to expert                  │
│  └── ? Uncertain (Keyboard: U) - Mark for second opinion        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Feedback Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              Feedback Processing Pipeline                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 1: Feedback Aggregation                           │     │
│  │                                                          │     │
│  │  Multiple reviewers per change (when available):         │     │
│  │  ┌─────────────────────────────────────────────────┐    │     │
│  │  │  Change #1:                                      │    │     │
│  │  │  ├── Reviewer A: Agree (HIGH) - Expert          │    │     │
│  │  │  ├── Reviewer B: Agree (HIGH) - Analyst         │    │     │
│  │  │  └── Reviewer C: Disagree (MEDIUM) - Analyst    │    │     │
│  │  │                                                   │    │     │
│  │  │  Weighted Consensus:                              │    │     │
│  │  │  • Expert weight: 2.0                            │    │     │
│  │  │  • Senior Analyst weight: 1.5                    │    │     │
│  │  │  • Analyst weight: 1.0                           │    │     │
│  │  │                                                   │    │     │
│  │  │  Result: HIGH (weighted agreement: 0.83)         │    │     │
│  │  └─────────────────────────────────────────────────┘    │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 2: Disagreement Resolution                        │     │
│  │                                                          │     │
│  │  When reviewers disagree significantly:                  │     │
│  │  ┌─────────────────────────────────────────────────┐    │     │
│  │  │                                                   │    │     │
│  │  │  Disagreement Type    │ Resolution               │    │     │
│  │  │  ─────────────────────┼─────────────────────────│    │     │
│  │  │  Minor (1 level diff) │ Take weighted average   │    │     │
│  │  │  Major (2+ levels)    │ Escalate to expert      │    │     │
│  │  │  Categorical conflict │ Expert tiebreaker       │    │     │
│  │  │  Persistent pattern   │ Create guideline update │    │     │
│  │  │                                                   │    │     │
│  │  └─────────────────────────────────────────────────┘    │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  STEP 3: Pattern Extraction                             │     │
│  │                                                          │     │
│  │  Identify systematic errors:                             │     │
│  │  ┌─────────────────────────────────────────────────┐    │     │
│  │  │                                                   │    │     │
│  │  │  False Positive Pattern Detected:                 │    │     │
│  │  │  ────────────────────────────────                │    │     │
│  │  │  Pattern: Date format changes (MM/DD → DD/MM)    │    │     │
│  │  │  Occurrences: 47 in last 30 days                 │    │     │
│  │  │  Override rate: 94%                              │    │     │
│  │  │  Recommendation: Add to ignore rules             │    │     │
│  │  │                                                   │    │     │
│  │  │  False Negative Pattern Detected:                 │    │     │
│  │  │  ────────────────────────────────                │    │     │
│  │  │  Pattern: "including but not limited to" removal │    │     │
│  │  │  Occurrences: 12 (all marked as missed)          │    │     │
│  │  │  Impact: Changes scope significantly              │    │     │
│  │  │  Recommendation: Add detection rule              │    │     │
│  │  │                                                   │    │     │
│  │  └─────────────────────────────────────────────────┘    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Threshold Auto-Tuning

```
┌─────────────────────────────────────────────────────────────────┐
│              Threshold Auto-Tuning System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Dynamic Threshold Adjustment:                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  The system maintains multiple thresholds:              │     │
│  │                                                         │     │
│  │  ┌─────────────────────────────────────────────────┐   │     │
│  │  │  Threshold Type        │ Current │ Range        │   │     │
│  │  │  ──────────────────────┼─────────┼─────────────│   │     │
│  │  │  Significance (HIGH)   │  0.75   │ 0.60 - 0.90 │   │     │
│  │  │  Significance (MED)    │  0.50   │ 0.35 - 0.65 │   │     │
│  │  │  Confidence minimum    │  0.80   │ 0.70 - 0.95 │   │     │
│  │  │  Semantic change       │  0.65   │ 0.50 - 0.80 │   │     │
│  │  └─────────────────────────────────────────────────┘   │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Auto-Tuning Algorithm:                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  def auto_tune_thresholds(feedback_window=30_days):    │     │
│  │      """                                                │     │
│  │      Adjust thresholds based on human feedback         │     │
│  │      while maintaining recall > 98%                     │     │
│  │      """                                                │     │
│  │      feedback = get_recent_feedback(feedback_window)   │     │
│  │                                                         │     │
│  │      # Calculate current metrics                        │     │
│  │      fp_rate = feedback.false_positives / feedback.total│     │
│  │      fn_rate = feedback.false_negatives / feedback.total│     │
│  │                                                         │     │
│  │      # PRIORITY: Minimize false negatives               │     │
│  │      if fn_rate > 0.02:  # Above 2% target             │     │
│  │          # Lower threshold to catch more                │     │
│  │          threshold.significance -= 0.05                │     │
│  │          log("Lowered threshold due to FN rate")       │     │
│  │                                                         │     │
│  │      # SECONDARY: Reduce false positives if FN is OK   │     │
│  │      elif fn_rate < 0.01 and fp_rate > 0.15:           │     │
│  │          # Safe to raise threshold slightly            │     │
│  │          threshold.significance += 0.02                │     │
│  │          log("Raised threshold to reduce FP")          │     │
│  │                                                         │     │
│  │      # Validate on holdout set before applying         │     │
│  │      if validate_threshold(threshold, holdout_set):    │     │
│  │          apply_threshold(threshold)                    │     │
│  │      else:                                              │     │
│  │          rollback_threshold()                          │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Threshold Adjustment Safeguards:                                │
│  ├── Maximum adjustment per cycle: ±0.05                        │
│  ├── Minimum feedback samples: 100 before adjusting             │
│  ├── Validation on holdout set required                         │
│  ├── Automatic rollback if metrics degrade                      │
│  ├── Human approval for changes > 0.10                          │
│  └── Audit trail of all threshold changes                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Continuous Learning Loop

```
┌─────────────────────────────────────────────────────────────────┐
│              Continuous Learning Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │                    FEEDBACK LOOP                        │     │
│  │                                                         │     │
│  │    ┌─────────────┐                                     │     │
│  │    │  Production │                                     │     │
│  │    │    Diffs    │◄────────────────────────────┐      │     │
│  │    └──────┬──────┘                             │      │     │
│  │           │                                     │      │     │
│  │           ▼                                     │      │     │
│  │    ┌─────────────┐                             │      │     │
│  │    │   Human     │                             │      │     │
│  │    │   Review    │                             │      │     │
│  │    └──────┬──────┘                             │      │     │
│  │           │                                     │      │     │
│  │           ▼                                     │      │     │
│  │    ┌─────────────┐     ┌─────────────┐        │      │     │
│  │    │  Feedback   │────▶│   Pattern   │        │      │     │
│  │    │  Database   │     │  Analysis   │        │      │     │
│  │    └─────────────┘     └──────┬──────┘        │      │     │
│  │                               │                │      │     │
│  │           ┌───────────────────┼────────────┐  │      │     │
│  │           ▼                   ▼            ▼  │      │     │
│  │    ┌───────────┐      ┌───────────┐  ┌──────────┐   │     │
│  │    │ Threshold │      │    RAG    │  │ Training │   │     │
│  │    │   Tuning  │      │  Updates  │  │   Data   │   │     │
│  │    └─────┬─────┘      └─────┬─────┘  └────┬─────┘   │     │
│  │          │                  │              │         │     │
│  │          └──────────────────┴──────────────┘         │     │
│  │                             │                         │     │
│  │                             ▼                         │     │
│  │                      ┌─────────────┐                 │     │
│  │                      │   Updated   │                 │     │
│  │                      │    Model    │─────────────────┘     │
│  │                      └─────────────┘                       │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Update Triggers:                                                │
│  ┌────────────────────────────────────────────────────────┐     │
│  │                                                         │     │
│  │  Immediate Updates:                                     │     │
│  │  ├── RAG knowledge base (new patterns, corrections)    │     │
│  │  └── Semantic equivalence mappings                     │     │
│  │                                                         │     │
│  │  Daily Updates:                                         │     │
│  │  ├── Threshold recalculation                           │     │
│  │  └── FP/FN pattern rules                               │     │
│  │                                                         │     │
│  │  Weekly Updates:                                        │     │
│  │  ├── Evaluation metrics recalculation                  │     │
│  │  └── Model performance reports                         │     │
│  │                                                         │     │
│  │  Monthly/Quarterly:                                     │     │
│  │  ├── Model fine-tuning with accumulated feedback       │     │
│  │  ├── Ground truth dataset expansion                    │     │
│  │  └── Full evaluation suite rerun                       │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### HITL Data Model

```sql
-- Human feedback on diff results
CREATE TABLE diff_feedback (
    id UUID PRIMARY KEY,
    comparison_id UUID REFERENCES comparisons(id),
    diff_result_id UUID REFERENCES diff_results(id),
    reviewer_id UUID REFERENCES users(id),

    -- Original system prediction
    predicted_significance VARCHAR(20),
    predicted_confidence DECIMAL(5,4),
    predicted_change_types VARCHAR(50)[],

    -- Human assessment
    assessment VARCHAR(20) NOT NULL,  -- AGREE, DISAGREE, UNCERTAIN
    corrected_significance VARCHAR(20),
    corrected_change_types VARCHAR(50)[],

    -- Detailed feedback
    is_false_positive BOOLEAN DEFAULT FALSE,
    is_false_negative BOOLEAN DEFAULT FALSE,
    feedback_comment TEXT,

    -- Reviewer metadata
    reviewer_expertise_level VARCHAR(50),
    review_time_seconds INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Aggregated feedback consensus
CREATE TABLE feedback_consensus (
    id UUID PRIMARY KEY,
    diff_result_id UUID REFERENCES diff_results(id),

    -- Aggregated result
    feedback_count INTEGER NOT NULL,
    agreement_score DECIMAL(5,4),
    final_significance VARCHAR(20),
    final_change_types VARCHAR(50)[],

    -- Conflict tracking
    had_disagreement BOOLEAN DEFAULT FALSE,
    resolution_method VARCHAR(50),  -- WEIGHTED_VOTE, EXPERT_OVERRIDE, ESCALATED

    -- Impact tracking
    was_system_correct BOOLEAN,
    error_type VARCHAR(50),  -- FALSE_POSITIVE, FALSE_NEGATIVE, MISCLASSIFIED

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Threshold adjustment history
CREATE TABLE threshold_adjustments (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),

    -- Threshold details
    threshold_name VARCHAR(100) NOT NULL,
    previous_value DECIMAL(5,4) NOT NULL,
    new_value DECIMAL(5,4) NOT NULL,
    adjustment_reason TEXT,

    -- Metrics at time of adjustment
    fp_rate_before DECIMAL(5,4),
    fn_rate_before DECIMAL(5,4),
    fp_rate_after DECIMAL(5,4),
    fn_rate_after DECIMAL(5,4),

    -- Approval
    auto_adjusted BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users(id),

    -- Rollback tracking
    was_rolled_back BOOLEAN DEFAULT FALSE,
    rollback_reason TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Detected error patterns
CREATE TABLE error_patterns (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),

    -- Pattern details
    pattern_type VARCHAR(50) NOT NULL,  -- FALSE_POSITIVE, FALSE_NEGATIVE
    pattern_description TEXT NOT NULL,
    pattern_regex VARCHAR(500),

    -- Statistics
    occurrence_count INTEGER DEFAULT 0,
    override_rate DECIMAL(5,4),
    first_detected TIMESTAMP WITH TIME ZONE,
    last_detected TIMESTAMP WITH TIME ZONE,

    -- Resolution
    status VARCHAR(50) DEFAULT 'detected',  -- detected, reviewing, resolved
    resolution_action VARCHAR(100),
    resolved_by UUID REFERENCES users(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_feedback_comparison ON diff_feedback(comparison_id);
CREATE INDEX idx_feedback_reviewer ON diff_feedback(reviewer_id, created_at DESC);
CREATE INDEX idx_feedback_fp_fn ON diff_feedback(is_false_positive, is_false_negative);
CREATE INDEX idx_consensus_error ON feedback_consensus(error_type) WHERE error_type IS NOT NULL;
CREATE INDEX idx_patterns_type_status ON error_patterns(pattern_type, status);
```

### HITL Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              HITL Metrics Dashboard                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  REAL-TIME ACCURACY METRICS                Last 30 days │     │
│  │  ──────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  Precision: 91.2% ████████████████████░░░ Target: 90%  │     │
│  │  Recall:    98.7% █████████████████████████ Target: 98%│     │
│  │  F1 Score:  94.8% ██████████████████████░░ Target: 93% │     │
│  │                                                         │     │
│  │  FP Rate:   8.8%  ████░░░░░░░░░░░░░░░░░░░ Target: <10% │     │
│  │  FN Rate:   1.3%  █░░░░░░░░░░░░░░░░░░░░░░ Target: <2%  │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  FEEDBACK VOLUME                                        │     │
│  │  ──────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  Total Reviews:        4,523                           │     │
│  │  Agreements:           3,892 (86.0%)                   │     │
│  │  Disagreements:          631 (14.0%)                   │     │
│  │  │                                                      │     │
│  │  ├── Severity Corrections:    412                      │     │
│  │  ├── Category Corrections:    189                      │     │
│  │  └── Flagged for Expert:       30                      │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  THRESHOLD CHANGES (Last 90 days)                       │     │
│  │  ──────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  Date       │ Threshold        │ Change │ Reason       │     │
│  │  ───────────┼──────────────────┼────────┼─────────────│     │
│  │  2025-01-15 │ HIGH significance│ +0.03  │ FP reduction │     │
│  │  2025-01-08 │ Confidence min   │ -0.02  │ FN increase  │     │
│  │  2024-12-20 │ HIGH significance│ -0.05  │ FN spike     │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  TOP FALSE POSITIVE PATTERNS                            │     │
│  │  ──────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  1. Date format changes (42 occurrences) - RESOLVED    │     │
│  │  2. Capitalization only (38 occurrences) - RESOLVED    │     │
│  │  3. "shall" → "will" (23 occurrences) - IN REVIEW      │     │
│  │  4. Whitespace changes (19 occurrences) - RESOLVED     │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  TOP FALSE NEGATIVE PATTERNS                            │     │
│  │  ──────────────────────────────────────────────────────│     │
│  │                                                         │     │
│  │  1. Single word negation (8 occurrences) - IN PROGRESS │     │
│  │  2. Number format changes (5 occurrences) - DETECTED   │     │
│  │  3. Cross-reference updates (3 occurrences) - DETECTED │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack for Evaluation & HITL

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Vector Store** | Pinecone / Qdrant / pgvector | RAG embeddings storage |
| **Embedding Model** | voyage-law-2 / BGE-large | Document embeddings |
| **Reranking** | Cohere Rerank / cross-encoder | Result refinement |
| **Evaluation Framework** | Custom + RAGAS | Metrics calculation |
| **Feedback UI** | React + Annotation tools | Human review interface |
| **A/B Testing** | LaunchDarkly / custom | Threshold experiments |
| **Metrics Dashboard** | Grafana + custom | Real-time monitoring |
| **Data Labeling** | Label Studio / custom | Ground truth creation |

---

## Scalability & Performance

### Horizontal Scaling Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Deployment                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Ingress Controller                    │    │
│  │                    (nginx / traefik)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐     │
│  │ API Service │      │ API Service │      │ API Service │     │
│  │  (Pod 1)    │      │  (Pod 2)    │      │  (Pod N)    │     │
│  │  HPA: 3-20  │      │             │      │             │     │
│  └─────────────┘      └─────────────┘      └─────────────┘     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Worker Nodes (Processing)                   │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │    │
│  │  │ Worker  │  │ Worker  │  │ Worker  │  │ Worker  │    │    │
│  │  │  Pod 1  │  │  Pod 2  │  │  Pod 3  │  │  Pod N  │    │    │
│  │  │ HPA:5-50│  │         │  │         │  │         │    │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Auto-scaling Triggers:                                          │
│  ├── CPU utilization > 70%                                      │
│  ├── Memory utilization > 80%                                   │
│  ├── Queue depth > 100 messages                                 │
│  └── Custom metrics (processing latency)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Caching Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Layer Caching                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: CDN (CloudFront/Cloudflare)                           │
│  └── Static assets, generated reports                           │
│                                                                  │
│  Layer 2: API Gateway Cache                                      │
│  └── Common queries, rate limiting                              │
│                                                                  │
│  Layer 3: Application Cache (Redis)                             │
│  ├── Session data (TTL: 24h)                                    │
│  ├── User permissions (TTL: 5m)                                 │
│  ├── Document metadata (TTL: 1h)                                │
│  ├── Comparison results (TTL: 24h)                              │
│  └── Rate limit counters                                        │
│                                                                  │
│  Layer 4: Database Query Cache                                   │
│  └── PostgreSQL query results                                   │
│                                                                  │
│  Cache Invalidation:                                             │
│  ├── Event-driven (document update → invalidate)                │
│  ├── TTL-based expiration                                       │
│  └── Manual purge API                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Targets

| Metric | Target | P99 |
|--------|--------|-----|
| API Response Time | < 200ms | < 500ms |
| Document Upload (10MB) | < 5s | < 10s |
| PDF Processing (100 pages) | < 30s | < 60s |
| Diff Computation (100 pages) | < 45s | < 90s |
| Report Generation | < 10s | < 30s |
| Concurrent Users | 1000+ | - |
| Documents/Day | 100,000+ | - |

---

## High Availability & Disaster Recovery

### HA Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                Multi-Region Deployment                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│     Region A (Primary)              Region B (Secondary)        │
│  ┌────────────────────┐          ┌────────────────────┐        │
│  │  ┌──────────────┐  │          │  ┌──────────────┐  │        │
│  │  │   K8s        │  │          │  │   K8s        │  │        │
│  │  │   Cluster    │  │          │  │   Cluster    │  │        │
│  │  └──────────────┘  │          │  └──────────────┘  │        │
│  │                    │          │                    │        │
│  │  ┌──────────────┐  │  Sync    │  ┌──────────────┐  │        │
│  │  │  PostgreSQL  │◄─┼──────────┼─▶│  PostgreSQL  │  │        │
│  │  │  (Primary)   │  │          │  │  (Standby)   │  │        │
│  │  └──────────────┘  │          │  └──────────────┘  │        │
│  │                    │          │                    │        │
│  │  ┌──────────────┐  │  Sync    │  ┌──────────────┐  │        │
│  │  │  S3 Bucket   │◄─┼──────────┼─▶│  S3 Bucket   │  │        │
│  │  └──────────────┘  │          │  └──────────────┘  │        │
│  └────────────────────┘          └────────────────────┘        │
│                                                                  │
│  Failover Strategy:                                              │
│  ├── DNS-based failover (Route53 / CloudFlare)                  │
│  ├── Database automatic failover (< 30s RTO)                    │
│  ├── Stateless services (instant failover)                      │
│  └── Document storage (cross-region replication)                │
│                                                                  │
│  Recovery Objectives:                                            │
│  ├── RTO (Recovery Time Objective): < 15 minutes                │
│  ├── RPO (Recovery Point Objective): < 1 minute                 │
│  └── Backup retention: 30 days                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## DevOps & CI/CD

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐ │
│  │  Code   │─▶│  Build  │─▶│  Test   │─▶│  Scan   │─▶│ Deploy│ │
│  │  Push   │  │         │  │         │  │         │  │       │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └───────┘ │
│                                                                  │
│  Build Stage:                                                    │
│  ├── Docker image build                                         │
│  ├── Dependency resolution                                      │
│  └── Artifact versioning                                        │
│                                                                  │
│  Test Stage:                                                     │
│  ├── Unit tests (>90% coverage)                                 │
│  ├── Integration tests                                          │
│  ├── E2E tests                                                  │
│  └── Performance tests                                          │
│                                                                  │
│  Security Scan:                                                  │
│  ├── SAST (SonarQube)                                           │
│  ├── DAST (OWASP ZAP)                                           │
│  ├── Container scan (Trivy)                                     │
│  ├── Dependency scan (Snyk)                                     │
│  └── License compliance                                         │
│                                                                  │
│  Deployment:                                                     │
│  ├── GitOps (ArgoCD / Flux)                                     │
│  ├── Blue-Green deployments                                     │
│  ├── Canary releases                                            │
│  └── Automated rollback                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Infrastructure as Code

```
infrastructure/
├── terraform/
│   ├── modules/
│   │   ├── vpc/
│   │   ├── eks/
│   │   ├── rds/
│   │   ├── elasticache/
│   │   ├── s3/
│   │   └── monitoring/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   └── backend.tf
├── kubernetes/
│   ├── base/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── configmaps/
│   │   └── secrets/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
└── helm/
    └── policy-diff/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

---

## Technology Stack Summary

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | React + TypeScript | Rich UI, type safety |
| **API Gateway** | Kong / AWS API Gateway | Enterprise features, scalability |
| **Backend Services** | Python (FastAPI) | Best PDF ecosystem, async support |
| **Message Queue** | RabbitMQ / AWS SQS | Reliable async processing |
| **Event Streaming** | Apache Kafka | High-throughput event processing |
| **Task Queue** | Celery + Redis | Distributed task processing |
| **Primary Database** | PostgreSQL | ACID, JSON support, reliability |
| **Document Store** | MongoDB | Flexible schema for extracted content |
| **Search** | Elasticsearch | Full-text search, analytics |
| **Cache** | Redis Cluster | High-performance caching |
| **Object Storage** | AWS S3 / Azure Blob | Scalable document storage |
| **Container Orchestration** | Kubernetes (EKS/AKS) | Enterprise container management |
| **CI/CD** | GitHub Actions + ArgoCD | GitOps workflow |
| **Monitoring** | Prometheus + Grafana | Metrics and visualization |
| **Logging** | ELK Stack / Loki | Centralized logging |
| **Tracing** | Jaeger / OpenTelemetry | Distributed tracing |
| **Secrets** | HashiCorp Vault | Secure secrets management |

---

## Project Structure

```
policy-diff/
├── services/
│   ├── api-gateway/
│   │   ├── src/
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── document-ingestion/
│   │   ├── src/
│   │   │   ├── handlers/
│   │   │   ├── validators/
│   │   │   ├── storage/
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── pdf-processing/
│   │   ├── src/
│   │   │   ├── extractors/
│   │   │   ├── parsers/
│   │   │   ├── normalizers/
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── diff-engine/
│   │   ├── src/
│   │   │   ├── algorithms/
│   │   │   ├── comparators/
│   │   │   ├── analyzers/
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── report-generator/
│   │   ├── src/
│   │   │   ├── templates/
│   │   │   ├── formatters/
│   │   │   ├── exporters/
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── Dockerfile
│   └── notification/
│       ├── src/
│       ├── tests/
│       └── Dockerfile
├── shared/
│   ├── models/
│   ├── utils/
│   ├── clients/
│   └── config/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── store/
│   ├── public/
│   └── package.json
├── infrastructure/
│   ├── terraform/
│   ├── kubernetes/
│   └── helm/
├── scripts/
│   ├── setup.sh
│   ├── migrate.sh
│   └── deploy.sh
├── docs/
│   ├── api/
│   ├── architecture/
│   └── runbooks/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
└── README.md
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
- [ ] Project scaffolding and CI/CD setup
- [ ] Core PDF processing service
- [ ] Basic diff engine (word-level)
- [ ] PostgreSQL schema and migrations
- [ ] S3 document storage integration
- [ ] Basic REST API

### Phase 2: Core Features (Weeks 5-8)
- [ ] Multi-level diff algorithms
- [ ] Report generation (HTML, PDF, JSON)
- [ ] Authentication (OAuth/SAML)
- [ ] Basic web UI
- [ ] Async job processing
- [ ] Webhook notifications

### Phase 3: Enterprise Features (Weeks 9-12)
- [ ] Multi-tenancy
- [ ] RBAC/ABAC authorization
- [ ] Audit logging
- [ ] Advanced caching
- [ ] Rate limiting
- [ ] API versioning

### Phase 4: Scale & Compliance (Weeks 13-16)
- [ ] Kubernetes deployment
- [ ] Auto-scaling
- [ ] Multi-region setup
- [ ] Compliance reporting
- [ ] Performance optimization
- [ ] Security hardening

### Phase 5: Advanced Features (Weeks 17-20)
- [ ] Semantic diff (ML-powered)
- [ ] Template management
- [ ] Workflow orchestration
- [ ] Advanced analytics
- [ ] SDK clients
- [ ] Documentation portal

---

## Cost Estimation (Monthly)

| Component | Dev | Staging | Production |
|-----------|-----|---------|------------|
| Compute (EKS) | $200 | $500 | $2,000 |
| Database (RDS) | $100 | $300 | $1,500 |
| Storage (S3) | $50 | $100 | $500 |
| Cache (ElastiCache) | $50 | $150 | $500 |
| Load Balancer | $50 | $50 | $200 |
| Monitoring | $100 | $200 | $500 |
| **Total** | **$550** | **$1,300** | **$5,200** |

*Note: Costs vary significantly based on usage patterns and region.*

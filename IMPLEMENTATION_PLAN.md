# Policy Diff Application - Implementation Plan

## Readiness Assessment

### What We Have ✅

| Asset | Status | Notes |
|-------|--------|-------|
| **Architecture Document** | Complete | 4800+ lines, enterprise-ready |
| **GenAI Problem Statement** | Complete | Clear value proposition |
| **AI Design Decisions** | Complete | Documented tradeoffs |
| **PII Protection Design** | Complete | Tokenization, detection, access control |
| **LLM Safety Architecture** | Complete | Self-hosted routing, sanitization |
| **RAG Design** | Complete | Knowledge base, retrieval pipeline |
| **Evaluation Framework** | Complete | Metrics, ground truth, HITL |
| **Data Models** | Complete | PostgreSQL schemas defined |
| **API Specifications** | Complete | REST endpoints documented |

### What We Need to Build 🔨

| Component | Complexity | Priority | Dependencies |
|-----------|------------|----------|--------------|
| PDF Text Extraction | Medium | P0 | None |
| Basic Text Diff Engine | Low | P0 | PDF Extraction |
| PII Detection Service | Medium | P0 | None |
| Embedding Pipeline | Medium | P1 | PDF Extraction |
| LLM Integration (Self-hosted) | High | P1 | PII Detection |
| RAG Knowledge Base | Medium | P1 | Embedding Pipeline |
| Evaluation Framework | Medium | P2 | Ground Truth Data |
| HITL Review UI | High | P2 | Core Diff Engine |
| Web Interface | High | P3 | All Backend Services |

---

## Build Strategy: Portfolio MVP vs Production

### Option A: Portfolio MVP (Recommended First)
**Goal:** Demonstrate GenAI skills with working code
**Timeline:** 2-3 weeks
**Scope:** Core diff + LLM + basic PII protection

### Option B: Full Production System
**Goal:** Enterprise-ready deployment
**Timeline:** 16-20 weeks
**Scope:** Everything in architecture document

**Recommendation:** Start with Option A, then iterate toward B.

---

## Phase 1: Portfolio MVP (Weeks 1-3)

### Week 1: Core Infrastructure

```
Day 1-2: Project Setup
├── Initialize Python project (Poetry/uv)
├── Set up project structure
├── Configure linting, formatting, testing
├── Create Docker development environment
└── Set up basic CI (GitHub Actions)

Day 3-4: PDF Processing
├── Implement PDF text extraction (pdfplumber)
├── Build document chunking logic
├── Create section detection heuristics
├── Write unit tests
└── Handle edge cases (scanned PDFs, tables)

Day 5-7: Basic Diff Engine
├── Implement text normalization
├── Build word-level diff (difflib)
├── Create change detection pipeline
├── Implement formatting-only filter
└── Build structured diff output
```

**Deliverables Week 1:**
- [ ] Working PDF → text pipeline
- [ ] Basic diff between two documents
- [ ] JSON output of detected changes
- [ ] 80%+ test coverage for core modules

### Week 2: AI Integration

```
Day 1-2: PII Detection
├── Integrate Microsoft Presidio
├── Add regex patterns for common PII
├── Build tokenization pipeline
├── Create token vault (in-memory for MVP)
└── Test with sample documents

Day 3-4: Embedding Pipeline
├── Integrate embedding model (sentence-transformers)
├── Build document chunking for embeddings
├── Implement similarity comparison
├── Create "changed section" detection
└── Benchmark embedding performance

Day 5-7: LLM Integration
├── Set up Ollama for local LLM (Llama 3.1 8B)
├── Build LLM prompt templates
├── Implement semantic diff analysis
├── Add confidence scoring
├── Create structured output parser
```

**Deliverables Week 2:**
- [ ] PII detection and tokenization working
- [ ] Embedding-based change detection
- [ ] LLM semantic analysis for changed sections
- [ ] End-to-end pipeline: PDF → Semantic Diff

### Week 3: Polish & Demo

```
Day 1-2: RAG Integration (Basic)
├── Set up ChromaDB for vector storage
├── Load sample policy clauses
├── Implement retrieval for context
├── Enhance LLM prompts with RAG context
└── Test improvement in accuracy

Day 3-4: CLI & Output
├── Build CLI interface (Typer/Click)
├── Create HTML diff report generator
├── Add JSON export format
├── Implement side-by-side view
└── Add summary statistics

Day 5-7: Documentation & Demo
├── Write README with examples
├── Create sample documents for demo
├── Record demo video (3-5 minutes)
├── Write blog post / LinkedIn article
├── Deploy demo (Streamlit/Gradio)
```

**Deliverables Week 3:**
- [ ] Complete CLI tool
- [ ] HTML and JSON output formats
- [ ] Basic RAG enhancement
- [ ] Demo application (Streamlit)
- [ ] Documentation and video

---

## MVP Architecture (Simplified)

```
┌─────────────────────────────────────────────────────────────────┐
│                     PORTFOLIO MVP                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │   PDF    │───▶│   PII    │───▶│ Embedding│───▶│   LLM    │  │
│  │  Parser  │    │ Detector │    │  Diff    │    │ Analysis │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                               │               │         │
│       ▼                               ▼               ▼         │
│  ┌──────────┐                   ┌──────────┐    ┌──────────┐   │
│  │  Text    │                   │ ChromaDB │    │  Ollama  │   │
│  │ Chunks   │                   │  (RAG)   │    │ (Local)  │   │
│  └──────────┘                   └──────────┘    └──────────┘   │
│                                                                  │
│  Output: CLI + HTML Report + JSON                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack (MVP)

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Language** | Python 3.11+ | Best AI/ML ecosystem |
| **PDF Parsing** | pdfplumber | Reliable, handles tables |
| **PII Detection** | Presidio + spaCy | Production-ready, extensible |
| **Embeddings** | sentence-transformers | Free, local, good quality |
| **Vector Store** | ChromaDB | Simple, no infra needed |
| **LLM** | Ollama + Llama 3.1 8B | Free, local, no API keys |
| **CLI** | Typer | Modern, great UX |
| **Demo UI** | Streamlit | Fast to build, looks good |
| **Testing** | pytest + hypothesis | Property-based testing |

---

## Project Structure (MVP)

```
policy-diff/
├── src/
│   └── policy_diff/
│       ├── __init__.py
│       ├── cli.py                 # CLI entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── pdf_parser.py      # PDF extraction
│       │   ├── text_diff.py       # Basic diff engine
│       │   ├── chunker.py         # Document chunking
│       │   └── normalizer.py      # Text normalization
│       ├── pii/
│       │   ├── __init__.py
│       │   ├── detector.py        # PII detection
│       │   ├── tokenizer.py       # PII tokenization
│       │   └── patterns.py        # Custom regex patterns
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── embeddings.py      # Embedding generation
│       │   ├── llm_client.py      # LLM integration
│       │   ├── prompts.py         # Prompt templates
│       │   └── rag.py             # RAG retrieval
│       ├── output/
│       │   ├── __init__.py
│       │   ├── html_report.py     # HTML generation
│       │   ├── json_export.py     # JSON output
│       │   └── templates/         # Jinja2 templates
│       └── models/
│           ├── __init__.py
│           ├── diff_result.py     # Data classes
│           └── document.py        # Document model
├── tests/
│   ├── conftest.py
│   ├── test_pdf_parser.py
│   ├── test_diff_engine.py
│   ├── test_pii_detection.py
│   └── fixtures/
│       └── sample_policies/       # Test PDFs
├── demo/
│   └── streamlit_app.py           # Demo UI
├── docs/
│   ├── ARCHITECTURE.md            # Full architecture
│   └── examples/                  # Usage examples
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Implementation Order (Detailed)

### Step 1: Project Scaffolding
```bash
# Create project
mkdir -p policy-diff && cd policy-diff
uv init  # or poetry init

# Install core dependencies
uv add pdfplumber spacy presidio-analyzer presidio-anonymizer
uv add sentence-transformers chromadb
uv add typer rich jinja2
uv add ollama  # For local LLM

# Install dev dependencies
uv add --dev pytest pytest-cov hypothesis ruff mypy

# Download spaCy model
python -m spacy download en_core_web_lg
```

### Step 2: PDF Parser
```python
# src/policy_diff/core/pdf_parser.py

from dataclasses import dataclass
from pathlib import Path
import pdfplumber

@dataclass
class ParsedDocument:
    """Represents a parsed PDF document."""
    filename: str
    pages: list[str]
    full_text: str
    metadata: dict

def parse_pdf(file_path: Path) -> ParsedDocument:
    """Extract text from PDF with structure preservation."""
    pages = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

    return ParsedDocument(
        filename=file_path.name,
        pages=pages,
        full_text="\n\n".join(pages),
        metadata={"page_count": len(pages)}
    )
```

### Step 3: PII Detection & Tokenization
```python
# src/policy_diff/pii/detector.py

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class PIIDetector:
    """Detect and tokenize PII in documents."""

    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.token_vault = {}  # token -> original value
        self._token_counter = 0

    def detect(self, text: str) -> list[dict]:
        """Detect PII entities in text."""
        results = self.analyzer.analyze(
            text=text,
            language="en",
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
                     "US_SSN", "CREDIT_CARD", "US_BANK_NUMBER"]
        )
        return [
            {
                "type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score,
                "text": text[r.start:r.end]
            }
            for r in results
        ]

    def tokenize(self, text: str) -> tuple[str, dict]:
        """Replace PII with tokens, return mapping."""
        detections = self.detect(text)
        tokenized = text
        mapping = {}

        # Process in reverse order to maintain positions
        for det in sorted(detections, key=lambda x: x["start"], reverse=True):
            token = f"[{det['type']}_{self._token_counter}]"
            self._token_counter += 1

            tokenized = (
                tokenized[:det["start"]] +
                token +
                tokenized[det["end"]:]
            )
            mapping[token] = det["text"]
            self.token_vault[token] = det["text"]

        return tokenized, mapping
```

### Step 4: Embedding-Based Diff
```python
# src/policy_diff/ai/embeddings.py

from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingDiffer:
    """Use embeddings to detect semantic changes."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = 0.95

    def get_embeddings(self, chunks: list[str]) -> np.ndarray:
        """Generate embeddings for text chunks."""
        return self.model.encode(chunks, convert_to_numpy=True)

    def find_changed_sections(
        self,
        chunks_a: list[str],
        chunks_b: list[str]
    ) -> list[tuple[int, int, float]]:
        """Find sections that changed between documents."""
        emb_a = self.get_embeddings(chunks_a)
        emb_b = self.get_embeddings(chunks_b)

        changed = []

        # Compare each chunk in A to most similar in B
        for i, vec_a in enumerate(emb_a):
            similarities = np.dot(emb_b, vec_a)
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]

            if best_similarity < self.similarity_threshold:
                changed.append((i, best_match_idx, best_similarity))

        return changed
```

### Step 5: LLM Semantic Analysis
```python
# src/policy_diff/ai/llm_client.py

import ollama
from dataclasses import dataclass

@dataclass
class SemanticAnalysis:
    """Result of LLM semantic analysis."""
    significance: str  # CRITICAL, HIGH, MEDIUM, LOW, NONE
    confidence: float
    change_type: list[str]
    explanation: str
    business_impact: str

ANALYSIS_PROMPT = """You are analyzing changes between two versions of a policy document.

ORIGINAL TEXT:
{text_a}

MODIFIED TEXT:
{text_b}

Analyze the semantic significance of this change. Consider:
1. Does the meaning change, or just the wording?
2. What is the business/legal impact?
3. Is this a material change that affects coverage, obligations, or rights?

Respond in JSON format:
{{
    "significance": "CRITICAL|HIGH|MEDIUM|LOW|NONE",
    "confidence": 0.0-1.0,
    "change_type": ["COVERAGE", "EXCLUSION", "LIMIT", "DEFINITION", "FORMATTING", "OTHER"],
    "explanation": "Brief explanation of the change",
    "business_impact": "Description of business/legal impact"
}}
"""

class LLMAnalyzer:
    """Use LLM for semantic diff analysis."""

    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model

    def analyze_change(self, text_a: str, text_b: str) -> SemanticAnalysis:
        """Analyze semantic significance of a change."""
        prompt = ANALYSIS_PROMPT.format(text_a=text_a, text_b=text_b)

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )

        result = response["message"]["content"]
        # Parse JSON response
        import json
        data = json.loads(result)

        return SemanticAnalysis(
            significance=data["significance"],
            confidence=data["confidence"],
            change_type=data["change_type"],
            explanation=data["explanation"],
            business_impact=data["business_impact"]
        )
```

### Step 6: Main Pipeline
```python
# src/policy_diff/cli.py

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from policy_diff.core.pdf_parser import parse_pdf
from policy_diff.core.chunker import chunk_document
from policy_diff.pii.detector import PIIDetector
from policy_diff.ai.embeddings import EmbeddingDiffer
from policy_diff.ai.llm_client import LLMAnalyzer
from policy_diff.output.html_report import generate_report

app = typer.Typer()
console = Console()

@app.command()
def compare(
    file_a: Path = typer.Argument(..., help="First PDF document"),
    file_b: Path = typer.Argument(..., help="Second PDF document"),
    output: Path = typer.Option("report.html", help="Output file"),
    use_llm: bool = typer.Option(True, help="Use LLM for semantic analysis"),
    protect_pii: bool = typer.Option(True, help="Detect and tokenize PII"),
):
    """Compare two policy documents and generate a diff report."""

    console.print("[bold blue]Policy Diff[/bold blue] - Semantic Document Comparison\n")

    # Step 1: Parse PDFs
    with console.status("Parsing documents..."):
        doc_a = parse_pdf(file_a)
        doc_b = parse_pdf(file_b)
    console.print(f"✓ Parsed {doc_a.filename} ({len(doc_a.pages)} pages)")
    console.print(f"✓ Parsed {doc_b.filename} ({len(doc_b.pages)} pages)")

    # Step 2: PII Detection (optional)
    if protect_pii:
        with console.status("Detecting PII..."):
            pii_detector = PIIDetector()
            text_a, mapping_a = pii_detector.tokenize(doc_a.full_text)
            text_b, mapping_b = pii_detector.tokenize(doc_b.full_text)
        console.print(f"✓ Tokenized {len(mapping_a) + len(mapping_b)} PII entities")
    else:
        text_a, text_b = doc_a.full_text, doc_b.full_text

    # Step 3: Chunk documents
    with console.status("Chunking documents..."):
        chunks_a = chunk_document(text_a)
        chunks_b = chunk_document(text_b)
    console.print(f"✓ Created {len(chunks_a)} / {len(chunks_b)} chunks")

    # Step 4: Embedding-based change detection
    with console.status("Detecting changes via embeddings..."):
        differ = EmbeddingDiffer()
        changed_sections = differ.find_changed_sections(chunks_a, chunks_b)
    console.print(f"✓ Found {len(changed_sections)} changed sections")

    # Step 5: LLM Analysis (optional, only for changed sections)
    results = []
    if use_llm and changed_sections:
        analyzer = LLMAnalyzer()
        with console.status("Analyzing changes with LLM..."):
            for idx_a, idx_b, similarity in changed_sections:
                analysis = analyzer.analyze_change(chunks_a[idx_a], chunks_b[idx_b])
                results.append({
                    "section_a": idx_a,
                    "section_b": idx_b,
                    "similarity": similarity,
                    "text_a": chunks_a[idx_a],
                    "text_b": chunks_b[idx_b],
                    "analysis": analysis
                })
        console.print(f"✓ Completed LLM analysis")

    # Step 6: Generate report
    with console.status("Generating report..."):
        generate_report(results, output)
    console.print(f"✓ Report saved to {output}")

    # Summary table
    table = Table(title="Diff Summary")
    table.add_column("Significance", style="cyan")
    table.add_column("Count", style="magenta")

    significance_counts = {}
    for r in results:
        sig = r["analysis"].significance
        significance_counts[sig] = significance_counts.get(sig, 0) + 1

    for sig, count in sorted(significance_counts.items()):
        table.add_row(sig, str(count))

    console.print(table)

if __name__ == "__main__":
    app()
```

---

## Success Metrics (MVP)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **PDF parsing accuracy** | >95% | Manual review of 20 documents |
| **PII detection recall** | >90% | Synthetic PII test dataset |
| **Change detection recall** | >95% | Manually labeled test pairs |
| **LLM analysis relevance** | >80% | Human evaluation |
| **End-to-end latency** | <30s for 50-page docs | Benchmark suite |
| **Demo impressiveness** | Qualitative | Show to 5 people, get feedback |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| PDF parsing fails on complex docs | Fall back to OCR (pytesseract) |
| LLM too slow locally | Use smaller model (Phi-3) or batch |
| PII detection misses custom patterns | Add domain-specific regex |
| Embeddings miss subtle changes | Hybrid: embeddings + text diff |
| Demo doesn't impress | Focus on real-world examples |

---

## Phase 2: Production Features (Post-MVP)

After MVP is complete and demonstrated:

### Weeks 4-6: Enterprise Foundation
- [ ] PostgreSQL data persistence
- [ ] User authentication (OAuth)
- [ ] Multi-tenant architecture
- [ ] API service (FastAPI)
- [ ] Background job processing (Celery)

### Weeks 7-9: Advanced AI
- [ ] Self-hosted LLM infrastructure (vLLM)
- [ ] Model routing logic
- [ ] Full RAG pipeline with Qdrant
- [ ] Confidence calibration system
- [ ] A/B testing framework

### Weeks 10-12: Evaluation & HITL
- [ ] Ground truth dataset creation
- [ ] Automated evaluation pipeline
- [ ] Human review interface
- [ ] Feedback collection system
- [ ] Threshold auto-tuning

### Weeks 13-16: Production Hardening
- [ ] Kubernetes deployment
- [ ] Monitoring & alerting
- [ ] Security audit
- [ ] Performance optimization
- [ ] Documentation & runbooks

---

## Immediate Next Steps

```
TODAY:
1. [ ] Create GitHub repository
2. [ ] Initialize Python project with dependencies
3. [ ] Set up development environment (Docker)
4. [ ] Implement basic PDF parser
5. [ ] Write first test

THIS WEEK:
1. [ ] Complete PDF parsing with tests
2. [ ] Implement basic text diff
3. [ ] Set up PII detection with Presidio
4. [ ] Create tokenization pipeline
5. [ ] Get Ollama running with Llama 3.1
```

---

## Commands to Get Started

```bash
# Create project directory
mkdir policy-diff && cd policy-diff

# Initialize with uv (fast Python package manager)
uv init
uv add pdfplumber presidio-analyzer presidio-anonymizer spacy
uv add sentence-transformers chromadb ollama
uv add typer rich jinja2
uv add --dev pytest pytest-cov ruff mypy

# Download models
python -m spacy download en_core_web_lg
ollama pull llama3.1:8b

# Create structure
mkdir -p src/policy_diff/{core,pii,ai,output,models}
mkdir -p tests/fixtures/sample_policies
mkdir -p demo docs

# Start coding!
touch src/policy_diff/__init__.py
touch src/policy_diff/core/pdf_parser.py
```

---

## Ready to Build?

**Answer: YES** - The architecture is solid, the plan is clear, and the MVP scope is achievable.

**Recommended approach:**
1. Start with Week 1, Day 1 tasks
2. Commit working code daily
3. Don't skip tests
4. Get something demo-able by end of Week 2
5. Polish and document in Week 3

Shall I start implementing the first component (PDF parser)?

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Policy Diff** is an AI-powered semantic document comparison platform for policy documents. Unlike traditional text diff tools that only detect character-level changes, this system uses embeddings and LLMs to understand semantic significance - distinguishing between meaningless formatting changes and critical policy modifications.

### Core Problem Being Solved

Traditional diff tools produce massive false positives (flagging "shall" → "will" as significant) and false negatives (missing critical changes like "employees" → "full-time employees"). This system:
- Filters noise from formatting/wording changes
- Detects semantically significant changes even with minimal text differences
- Protects PII before LLM processing
- Categorizes changes by significance (CRITICAL, HIGH, MEDIUM, LOW, NONE)
- Provides business impact analysis for each change

## Development Commands

### Setup
```bash
# Install dependencies (using uv or pip)
pip install -e ".[dev]"

# Download required spaCy model for PII detection
python -m spacy download en_core_web_lg

# Install and start Ollama (for LLM features)
# macOS: brew install ollama
ollama serve
ollama pull llama3.1:8b
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_diff_engine.py

# Run tests matching pattern
pytest -k "test_pii"

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=policy_diff --cov-report=html
```

### Code Quality
```bash
# Format and lint (ruff handles both)
ruff check .
ruff format .

# Type checking
mypy src/policy_diff
```

### Running the CLI
```bash
# Basic comparison
policy-diff file1.pdf file2.pdf

# With options
policy-diff file1.pdf file2.pdf \
  --output report.html \
  --format html \
  --llm \
  --pii \
  --chunk-type paragraph \
  --min-significance medium \
  --verbose

# Without LLM (faster, text diff only)
policy-diff file1.pdf file2.pdf --no-llm --no-embeddings

# Check system status
policy-diff info

# Show version
policy-diff version
```

## Architecture

### High-Level Pipeline

The system follows a multi-stage pipeline that progressively enriches the diff analysis:

```
PDF Parsing → Chunking → PII Protection → Text Diff → Semantic Analysis → Report
```

**Key architectural decisions:**

1. **Chunk-based comparison**: Documents are split into semantic chunks (paragraphs, sentences, or sections) rather than comparing line-by-line. This enables better semantic matching and handles structural reorganization.

2. **PII tokenization before LLM**: All PII is detected and tokenized BEFORE sending to LLM, with a vault maintaining the mappings. This enables using external LLMs safely in the future.

3. **Hybrid diff approach**: Combines traditional text diff (fast, catches everything) with semantic analysis (expensive, only for changed sections). This balances cost and accuracy.

4. **Lazy LLM invocation**: LLM is only called for changes that pass similarity thresholds and heuristics. Most formatting-only changes never reach the LLM.

5. **Significance-driven workflow**: Every change is classified by significance level, allowing users to filter noise and focus on critical changes.

### Module Architecture

**`policy_diff.core`** - Core document processing (no AI dependencies)
- `pdf_parser.py`: Extracts text from PDFs using pdfplumber
- `chunker.py`: Splits documents into semantic chunks (paragraph/sentence/section)
- `normalizer.py`: Text normalization (whitespace, Unicode, case)
- `diff_engine.py`: Traditional text diff using difflib, produces initial ChangeItems

**`policy_diff.pii`** - PII detection and tokenization
- `detector.py`: Detects PII using Presidio + spaCy (names, SSNs, emails, etc.)
- `tokenizer.py`: Replaces PII with tokens, maintains vault for de-tokenization
- Supports multiple strategies: PLACEHOLDER, HASH, ENCRYPT

**`policy_diff.ai`** - AI-powered semantic analysis
- `embeddings.py`: Generates embeddings using sentence-transformers, computes similarity
- `llm_client.py`: Interfaces with Ollama for LLM calls, handles retries and errors
- `prompts.py`: Structured prompts for semantic analysis
- `SemanticAnalyzer`: Orchestrates embedding + LLM analysis, decides when to invoke LLM

**`policy_diff.models`** - Data models (Pydantic)
- `document.py`: Document, Page, Metadata models
- `diff_result.py`: ChangeItem, DiffReport, SemanticAnalysis, Significance enums

**`policy_diff.output`** - Report generation
- `html_report.py`: Generates HTML reports with side-by-side diff view
- `json_export.py`: Exports structured JSON for API integration

**`policy_diff.cli`** - CLI interface using Typer + Rich for beautiful terminal output

### Data Flow: How a Change Gets Analyzed

1. **PDF Parser** extracts text → `Document` with pages and metadata
2. **Chunker** splits document → List of `Chunk` objects with text + location
3. **PII Tokenizer** (optional) replaces sensitive data → Modified chunks + token vault
4. **Diff Engine** compares chunks → `ChunkMatch` objects with similarity scores
5. **Semantic Analyzer** evaluates changes:
   - If similarity > 0.99: Skip (exact match)
   - If similarity > 0.95: Check with embeddings
   - If similarity < 0.95 AND substantive change: Invoke LLM
6. **LLM** returns `SemanticAnalysis` with significance, categories, business impact
7. **Report Generator** assembles `DiffReport` with all changes and summary

### Key Design Patterns

**Lazy evaluation**: AI models (embeddings, LLM) are only loaded if needed. If user runs with `--no-llm`, no models are loaded.

**Graceful degradation**: If Ollama isn't running, system falls back to text diff only. If embeddings fail, uses text similarity. System always produces output.

**Strategy pattern**: PII tokenization, chunking, normalization all use strategy pattern for flexibility.

**Separation of concerns**: Core text processing is independent of AI components. PII protection is independent of both. This enables testing and development of each layer independently.

## Important Implementation Details

### Change Significance Logic

Changes get significance from multiple sources (in priority order):
1. **LLM analysis** (if performed): CRITICAL/HIGH/MEDIUM/LOW/NONE
2. **Rule-based heuristics**: Numbers, dates, negations ("not", "no"), exclusions
3. **Similarity score**: Low similarity → likely significant change
4. **Default**: NONE (formatting only)

See `SemanticAnalyzer.should_use_llm()` for the decision logic on when to invoke LLM.

### PII Protection Strategy

The system detects these PII types using Presidio:
- PERSON (names)
- EMAIL_ADDRESS
- PHONE_NUMBER
- US_SSN
- CREDIT_CARD
- US_BANK_NUMBER
- Custom patterns (can be extended)

Tokenization happens BEFORE diff, so both documents are tokenized independently. This means PII changes are captured as token changes, maintaining privacy.

### Chunking Strategies

**Paragraph chunking** (default): Best for policy documents, balances granularity and context.
**Sentence chunking**: More granular, useful for detecting small changes, but can miss context.
**Section chunking**: Detects large structural changes, but may miss fine-grained edits.

Choose based on document structure and sensitivity to changes.

### Embedding Model

Uses `all-MiniLM-L6-v2` from sentence-transformers:
- Fast (processes 1000s of chunks/second)
- Small model size (80MB)
- Good accuracy for semantic similarity
- Runs locally, no API calls

Can be swapped for larger models (e.g., `all-mpnet-base-v2`) for better accuracy at cost of speed.

### LLM Integration

Currently supports **Ollama** with local models. The architecture is provider-agnostic (see `LLMProvider` enum) for future support of:
- OpenAI API
- Anthropic API
- Azure OpenAI
- Other providers

Ollama is chosen for MVP to avoid API costs and ensure PII protection.

## Testing Strategy

### Test Structure
- `tests/test_models.py`: Data model validation
- `tests/test_normalizer.py`: Text normalization edge cases
- `tests/test_chunker.py`: Document chunking logic
- `tests/test_diff_engine.py`: Core diff algorithm
- `tests/test_pii.py`: PII detection and tokenization

### Test Philosophy

Tests focus on **behavior, not implementation**. For example:
- PII tests verify that sensitive data is replaced, not how Presidio works internally
- Diff tests verify change detection, not the specific algorithm used
- Property-based tests (hypothesis) ensure robustness across diverse inputs

### Running Specific Tests

```bash
# Test PII detection
pytest tests/test_pii.py -v

# Test diff engine with a specific scenario
pytest tests/test_diff_engine.py::test_semantic_equivalence -v

# Test with hypothesis (property-based testing)
pytest tests/ --hypothesis-show-statistics
```

## Configuration

### Tool Configuration (pyproject.toml)

**Ruff** (linting + formatting):
- Line length: 100
- Enabled rules: E, F, I, N, W, UP, B, C4, SIM
- Ignores E501 (line too long) as it's handled by formatter

**MyPy** (type checking):
- Strict mode enabled
- Requires type hints on all functions

**Pytest**:
- Coverage threshold: implicit (aim for >80%)
- Test discovery: `tests/` directory

### Runtime Configuration

Configuration is passed via CLI flags or `DiffConfig` dataclass:
- `similarity_threshold`: Minimum similarity for chunk matching (default: 0.6)
- `normalization_level`: NONE, BASIC, STANDARD, AGGRESSIVE
- `use_semantic_matching`: Enable embedding-based matching

## Common Workflows

### Adding a New PII Type

1. Add to `PIIType` enum in `pii/detector.py`
2. Add detection pattern to Presidio configuration or custom regex
3. Add test case in `tests/test_pii.py`
4. Update documentation

### Adding a New Change Category

1. Add to `ChangeCategory` enum in `models/diff_result.py`
2. Update LLM prompt in `ai/prompts.py` to recognize new category
3. Add test case with sample text that should trigger this category
4. Update HTML report template to display new category

### Improving Semantic Analysis

LLM prompts are in `ai/prompts.py`. Key considerations:
- Provide clear examples in prompts
- Request structured JSON output for parsing
- Include legal/business context in prompt
- Test with diverse document pairs

### Debugging False Positives/Negatives

1. Run with `--verbose` to see similarity scores
2. Check `similarity_threshold` in DiffConfig
3. Examine normalization level (may be too aggressive)
4. Review LLM prompt - may need domain-specific guidance
5. Check if PII tokenization is affecting matching

## Project Status

**Current state**: MVP implementation with core features working
- ✅ PDF parsing
- ✅ Text chunking (paragraph/sentence/section)
- ✅ PII detection and tokenization
- ✅ Text diff engine
- ✅ Embedding-based similarity
- ✅ LLM semantic analysis (Ollama)
- ✅ HTML report generation
- ✅ JSON export
- ✅ CLI interface
- ✅ Unit tests

**Not yet implemented** (see IMPLEMENTATION_PLAN.md for roadmap):
- RAG knowledge base for domain-specific context
- Web UI
- Database persistence
- Multi-tenant architecture
- Production LLM infrastructure
- Human-in-the-loop review interface
- Evaluation framework with ground truth data

## Dependencies

**Required:**
- pdfplumber: PDF text extraction
- presidio-analyzer/anonymizer: PII detection
- spacy: NLP models for PII
- sentence-transformers: Embedding generation
- ollama: Local LLM interface
- typer: CLI framework
- rich: Terminal output
- pydantic: Data validation

**Optional (for full features):**
- ChromaDB: Vector storage for RAG (future)
- FastAPI: Web API (future)
- PostgreSQL: Data persistence (future)

**Development:**
- pytest: Testing framework
- hypothesis: Property-based testing
- ruff: Linting and formatting
- mypy: Type checking

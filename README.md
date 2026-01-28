# Policy Diff

AI-powered semantic document comparison for policy documents.

## Overview

Policy Diff uses embeddings and LLMs to detect semantically significant changes in policy documents, filtering out formatting noise and highlighting critical modifications.

## Features

- **Semantic Change Detection**: Understands meaning, not just text differences
- **PII Protection**: Tokenizes sensitive information before LLM processing
- **Significance Ranking**: Classifies changes as CRITICAL, HIGH, MEDIUM, LOW, or NONE
- **Multiple Output Formats**: HTML reports and JSON export
- **Flexible AI Integration**: Optional LLM and embedding analysis

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e ".[dev]"

# Download spaCy model for PII detection
python -m spacy download en_core_web_lg

# Install and start Ollama (optional, for LLM features)
# macOS: brew install ollama
ollama serve
ollama pull llama3.1:8b
```

## Quick Start

### Command Line Interface

```bash
# Compare two PDF documents
policy-diff document_v1.pdf document_v2.pdf

# Generate HTML report
policy-diff document_v1.pdf document_v2.pdf --output report.html

# With all features enabled
policy-diff document_v1.pdf document_v2.pdf \
  --llm \
  --pii \
  --chunk-type paragraph \
  --verbose
```

### Web Interface (Streamlit)

```bash
# Install web dependencies
pip install -e ".[web]"

# Run the Streamlit app
streamlit run streamlit_app.py

# The app will open in your browser at http://localhost:8501
```

The Streamlit interface provides:
- 📤 Drag-and-drop file upload for PDF documents
- ⚙️ Interactive configuration sidebar
- 📊 Real-time progress tracking
- 📈 Visual summary dashboard with metrics
- 📝 Expandable change viewer with semantic analysis
- 💾 Download buttons for HTML and JSON reports

## Usage

```bash
# Basic comparison
policy-diff file1.pdf file2.pdf

# Without LLM (faster, text diff only)
policy-diff file1.pdf file2.pdf --no-llm --no-embeddings

# JSON export
policy-diff file1.pdf file2.pdf --format json --output results.json

# Filter by significance
policy-diff file1.pdf file2.pdf --min-significance high

# Check system status
policy-diff info
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=policy_diff --cov-report=html

# Format and lint
ruff check .
ruff format .

# Type checking
mypy src/policy_diff
```

## Architecture

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation and [ARCHITECTURE.md](ARCHITECTURE.md) for the complete enterprise design.

## Project Status

**Current**: MVP implementation with core features
- ✅ PDF parsing and chunking
- ✅ PII detection and tokenization
- ✅ Text diff engine
- ✅ Embedding-based similarity
- ✅ LLM semantic analysis (Ollama)
- ✅ HTML and JSON reports
- ✅ CLI interface with Rich output
- ✅ Streamlit web interface

**Planned**: See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for roadmap

## License

MIT

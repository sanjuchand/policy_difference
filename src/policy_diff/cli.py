"""Command-line interface for policy diff."""

import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from policy_diff.core import (
    PDFParser,
    DocumentChunker,
    ChunkType,
    TextDiffEngine,
    DiffConfig,
)
from policy_diff.pii import PIITokenizer, TokenizationStrategy
from policy_diff.ai import EmbeddingEngine, LLMClient, SemanticAnalyzer
from policy_diff.output import HTMLReportGenerator, JSONExporter
from policy_diff.models.diff_result import DiffReport, Significance

app = typer.Typer(
    name="policy-diff",
    help="AI-powered semantic diff for policy documents",
    add_completion=False,
)
console = Console()


@app.command()
def compare(
    file_a: Path = typer.Argument(..., help="Path to first PDF document"),
    file_b: Path = typer.Argument(..., help="Path to second PDF document"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (HTML or JSON)"
    ),
    format: str = typer.Option(
        "html", "--format", "-f", help="Output format: html, json, or summary"
    ),
    use_llm: bool = typer.Option(
        True, "--llm/--no-llm", help="Use LLM for semantic analysis"
    ),
    use_embeddings: bool = typer.Option(
        True, "--embeddings/--no-embeddings", help="Use embeddings for similarity"
    ),
    protect_pii: bool = typer.Option(
        True, "--pii/--no-pii", help="Protect PII before LLM processing"
    ),
    chunk_type: str = typer.Option(
        "paragraph", "--chunk-type", "-c", help="Chunking: paragraph, sentence, section"
    ),
    min_significance: str = typer.Option(
        "low", "--min-significance", "-s", help="Minimum significance: critical, high, medium, low"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose output"
    ),
):
    """Compare two PDF policy documents and generate a diff report."""
    start_time = time.time()

    # Validate inputs
    if not file_a.exists():
        console.print(f"[red]Error: File not found: {file_a}[/red]")
        raise typer.Exit(1)
    if not file_b.exists():
        console.print(f"[red]Error: File not found: {file_b}[/red]")
        raise typer.Exit(1)

    # Parse chunk type
    try:
        chunk_type_enum = ChunkType(chunk_type)
    except ValueError:
        console.print(f"[red]Error: Invalid chunk type: {chunk_type}[/red]")
        raise typer.Exit(1)

    # Parse significance
    try:
        min_sig = Significance(min_significance)
    except ValueError:
        console.print(f"[red]Error: Invalid significance: {min_significance}[/red]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold]Policy Diff Analysis[/bold]\n"
        f"📄 {file_a.name} → {file_b.name}",
        border_style="blue"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Parse PDFs
        task = progress.add_task("Parsing PDFs...", total=None)
        parser = PDFParser()
        doc_a = parser.parse(file_a)
        doc_b = parser.parse(file_b)
        progress.update(task, completed=True)

        if verbose:
            console.print(f"  Doc A: {doc_a.metadata.page_count} pages, {doc_a.metadata.word_count} words")
            console.print(f"  Doc B: {doc_b.metadata.page_count} pages, {doc_b.metadata.word_count} words")

        # Chunk documents
        task = progress.add_task("Chunking documents...", total=None)
        chunker = DocumentChunker(chunk_type=chunk_type_enum)
        chunks_a = chunker.chunk_document(doc_a)
        chunks_b = chunker.chunk_document(doc_b)
        progress.update(task, completed=True)

        if verbose:
            console.print(f"  Doc A: {len(chunks_a)} chunks")
            console.print(f"  Doc B: {len(chunks_b)} chunks")

        # Protect PII if enabled
        tokenizer = None
        if protect_pii:
            task = progress.add_task("Protecting PII...", total=None)
            tokenizer = PIITokenizer(strategy=TokenizationStrategy.PLACEHOLDER)
            # Tokenize chunk texts
            for chunk in chunks_a:
                result = tokenizer.tokenize(chunk.text)
                chunk.text = result.tokenized_text
            tokenizer.reset()
            for chunk in chunks_b:
                result = tokenizer.tokenize(chunk.text)
                chunk.text = result.tokenized_text
            progress.update(task, completed=True)

        # Initialize AI components
        embedding_engine = None
        llm_client = None
        semantic_analyzer = None

        if use_embeddings:
            task = progress.add_task("Loading embedding model...", total=None)
            try:
                embedding_engine = EmbeddingEngine()
                if not embedding_engine.is_available:
                    embedding_engine = None
                    console.print("[yellow]  Embedding model not available, using text similarity[/yellow]")
            except Exception as e:
                if verbose:
                    console.print(f"[yellow]  Could not load embeddings: {e}[/yellow]")
            progress.update(task, completed=True)

        if use_llm:
            task = progress.add_task("Initializing LLM...", total=None)
            llm_client = LLMClient()
            if not llm_client.is_available:
                console.print("[yellow]  LLM not available (Ollama not running?), skipping semantic analysis[/yellow]")
                llm_client = None
            progress.update(task, completed=True)

        if llm_client or embedding_engine:
            semantic_analyzer = SemanticAnalyzer(
                llm_client=llm_client,
                embedding_engine=embedding_engine,
            )

        # Run diff
        task = progress.add_task("Computing differences...", total=None)
        config = DiffConfig(
            use_semantic_matching=embedding_engine is not None,
        )
        diff_engine = TextDiffEngine(config)
        report = diff_engine.diff_documents(
            chunks_a,
            chunks_b,
            doc_a_name=file_a.name,
            doc_b_name=file_b.name,
        )
        progress.update(task, completed=True)

        # Run semantic analysis on changes
        if semantic_analyzer and report.changes:
            task = progress.add_task("Analyzing changes semantically...", total=len(report.changes))
            for i, change in enumerate(report.changes):
                if semantic_analyzer.should_use_llm(
                    change.text_before,
                    change.text_after,
                    change.similarity_score,
                ):
                    analysis = semantic_analyzer.analyze(
                        change.text_before,
                        change.text_after,
                        change.similarity_score,
                    )
                    if analysis:
                        change.semantic_analysis = analysis
                progress.update(task, advance=1)

    # Update report metadata
    report.processing_time_seconds = time.time() - start_time
    if llm_client:
        report.llm_calls_made = llm_client.call_count
    if embedding_engine:
        report.embeddings_computed = len(chunks_a) + len(chunks_b)

    # Recompute summary after semantic analysis
    report._compute_summary()

    # Display summary
    _display_summary(report)

    # Generate output
    if output or format != "summary":
        _generate_output(report, output, format, min_sig)

    console.print(f"\n[green]✓ Analysis complete in {report.processing_time_seconds:.2f}s[/green]")


def _display_summary(report: DiffReport):
    """Display summary table."""
    table = Table(title="Change Summary", show_header=True, header_style="bold")
    table.add_column("Significance", style="cyan")
    table.add_column("Count", justify="right")

    table.add_row("Critical", str(report.summary.critical_changes), style="red bold")
    table.add_row("High", str(report.summary.high_changes), style="yellow")
    table.add_row("Medium", str(report.summary.medium_changes), style="blue")
    table.add_row("Low", str(report.summary.low_changes), style="dim")
    table.add_row("Formatting", str(report.summary.formatting_only), style="dim")
    table.add_row("─" * 10, "─" * 5)
    table.add_row("Total", str(report.summary.total_changes), style="bold")

    console.print(table)


def _generate_output(
    report: DiffReport,
    output_path: Optional[Path],
    format: str,
    min_sig: Significance,
):
    """Generate output file."""
    if format == "html":
        generator = HTMLReportGenerator()
        content = generator.generate(report)
        ext = ".html"
    elif format == "json":
        exporter = JSONExporter(filter_significance=min_sig)
        content = exporter.export(report)
        ext = ".json"
    else:
        return

    if output_path is None:
        # Generate default filename
        output_path = Path(f"diff_report_{report.report_id[:8]}{ext}")

    output_path.write_text(content, encoding="utf-8")
    console.print(f"\n[green]Report saved to: {output_path}[/green]")


@app.command()
def info():
    """Show system information and available features."""
    console.print(Panel.fit("[bold]Policy Diff System Info[/bold]", border_style="blue"))

    # Check dependencies
    table = Table(show_header=True, header_style="bold")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")

    # PDF parsing
    try:
        import pdfplumber
        table.add_row("PDF Parser", "[green]✓ Available[/green]", f"pdfplumber {pdfplumber.__version__}")
    except ImportError:
        table.add_row("PDF Parser", "[red]✗ Missing[/red]", "Install pdfplumber")

    # Embeddings
    try:
        from sentence_transformers import SentenceTransformer
        table.add_row("Embeddings", "[green]✓ Available[/green]", "sentence-transformers")
    except ImportError:
        table.add_row("Embeddings", "[yellow]○ Optional[/yellow]", "Install sentence-transformers")

    # Presidio
    try:
        from presidio_analyzer import AnalyzerEngine
        table.add_row("PII Detection", "[green]✓ Available[/green]", "presidio-analyzer")
    except ImportError:
        table.add_row("PII Detection", "[yellow]○ Optional[/yellow]", "Install presidio-analyzer")

    # Ollama
    try:
        import ollama
        try:
            ollama.list()
            table.add_row("LLM (Ollama)", "[green]✓ Running[/green]", "ollama")
        except Exception:
            table.add_row("LLM (Ollama)", "[yellow]○ Not Running[/yellow]", "Start with: ollama serve")
    except ImportError:
        table.add_row("LLM (Ollama)", "[yellow]○ Optional[/yellow]", "Install ollama")

    console.print(table)


@app.command()
def version():
    """Show version information."""
    console.print("[bold]policy-diff[/bold] version 0.1.0")


if __name__ == "__main__":
    app()

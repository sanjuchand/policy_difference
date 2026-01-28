"""Streamlit web interface for Policy Diff."""

import tempfile
import time
from pathlib import Path
from typing import Optional

import streamlit as st

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
from policy_diff.models.diff_result import DiffReport, Significance, ChangeType


# Page configuration
st.set_page_config(
    page_title="Policy Diff Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .critical { color: #d62728; font-weight: bold; }
    .high { color: #ff7f0e; font-weight: bold; }
    .medium { color: #2ca02c; }
    .low { color: #7f7f7f; }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "report" not in st.session_state:
        st.session_state.report = None
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "html_report" not in st.session_state:
        st.session_state.html_report = None
    if "json_report" not in st.session_state:
        st.session_state.json_report = None


def render_header():
    """Render page header."""
    st.markdown('<div class="main-header">📄 Policy Diff Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-powered semantic comparison for policy documents</div>',
        unsafe_allow_html=True
    )
    st.divider()


def render_sidebar() -> dict:
    """Render sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("Analysis Options")
        use_llm = st.checkbox("Use LLM Analysis", value=True,
                             help="Enable AI-powered semantic analysis using Ollama")
        use_embeddings = st.checkbox("Use Embeddings", value=True,
                                     help="Use embeddings for semantic similarity")
        protect_pii = st.checkbox("PII Protection", value=True,
                                  help="Detect and tokenize PII before LLM processing")

        st.subheader("Document Processing")
        chunk_type = st.selectbox(
            "Chunk Type",
            options=["paragraph", "sentence", "section"],
            index=0,
            help="How to split documents for comparison"
        )

        st.subheader("Filtering")
        min_significance = st.selectbox(
            "Minimum Significance",
            options=["none", "low", "medium", "high", "critical"],
            index=1,
            help="Filter changes by significance level"
        )

        st.divider()

        st.subheader("📊 System Status")

        # Check system components
        status_info = check_system_status()
        for component, status in status_info.items():
            icon = "✅" if status else "❌"
            st.text(f"{icon} {component}")

        return {
            "use_llm": use_llm,
            "use_embeddings": use_embeddings,
            "protect_pii": protect_pii,
            "chunk_type": chunk_type,
            "min_significance": min_significance,
        }


def check_system_status() -> dict:
    """Check availability of system components."""
    status = {}

    # Check embeddings
    try:
        from sentence_transformers import SentenceTransformer
        status["Embeddings"] = True
    except ImportError:
        status["Embeddings"] = False

    # Check Ollama
    try:
        import ollama
        ollama.list()
        status["LLM (Ollama)"] = True
    except Exception:
        status["LLM (Ollama)"] = False

    # Check PII detection
    try:
        from presidio_analyzer import AnalyzerEngine
        status["PII Detection"] = True
    except ImportError:
        status["PII Detection"] = False

    return status


def render_file_upload():
    """Render file upload interface."""
    st.subheader("📤 Upload Documents")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original Document**")
        file_a = st.file_uploader(
            "Upload first PDF",
            type=["pdf"],
            key="file_a",
            label_visibility="collapsed"
        )
        if file_a:
            st.success(f"✓ {file_a.name}")

    with col2:
        st.markdown("**Modified Document**")
        file_b = st.file_uploader(
            "Upload second PDF",
            type=["pdf"],
            key="file_b",
            label_visibility="collapsed"
        )
        if file_b:
            st.success(f"✓ {file_b.name}")

    return file_a, file_b


def process_documents(file_a, file_b, config: dict) -> Optional[DiffReport]:
    """Process documents and generate diff report."""

    # Create temporary files
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_a:
        tmp_a.write(file_a.read())
        path_a = Path(tmp_a.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_b:
        tmp_b.write(file_b.read())
        path_b = Path(tmp_b.name)

    try:
        start_time = time.time()

        # Parse chunk type
        chunk_type_enum = ChunkType(config["chunk_type"])

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Parse PDFs
        status_text.text("📄 Parsing PDFs...")
        progress_bar.progress(10)
        parser = PDFParser()
        doc_a = parser.parse(path_a)
        doc_b = parser.parse(path_b)

        # Chunk documents
        status_text.text("✂️ Chunking documents...")
        progress_bar.progress(25)
        chunker = DocumentChunker(chunk_type=chunk_type_enum)
        chunks_a = chunker.chunk_document(doc_a)
        chunks_b = chunker.chunk_document(doc_b)

        # PII protection
        if config["protect_pii"]:
            status_text.text("🔒 Protecting PII...")
            progress_bar.progress(35)
            tokenizer = PIITokenizer(strategy=TokenizationStrategy.PLACEHOLDER)
            for chunk in chunks_a:
                result = tokenizer.tokenize(chunk.text)
                chunk.text = result.tokenized_text
            tokenizer.reset()
            for chunk in chunks_b:
                result = tokenizer.tokenize(chunk.text)
                chunk.text = result.tokenized_text

        # Initialize AI components
        embedding_engine = None
        llm_client = None
        semantic_analyzer = None

        if config["use_embeddings"]:
            status_text.text("🧠 Loading embedding model...")
            progress_bar.progress(45)
            try:
                embedding_engine = EmbeddingEngine()
                if not embedding_engine.is_available:
                    embedding_engine = None
                    st.warning("⚠️ Embedding model not available, using text similarity")
            except Exception as e:
                st.warning(f"⚠️ Could not load embeddings: {e}")

        if config["use_llm"]:
            status_text.text("🤖 Initializing LLM...")
            progress_bar.progress(55)
            llm_client = LLMClient()
            if not llm_client.is_available:
                st.warning("⚠️ LLM not available (Ollama not running?), skipping semantic analysis")
                llm_client = None

        if llm_client or embedding_engine:
            semantic_analyzer = SemanticAnalyzer(
                llm_client=llm_client,
                embedding_engine=embedding_engine,
            )

        # Run diff
        status_text.text("🔍 Computing differences...")
        progress_bar.progress(65)
        diff_config = DiffConfig(
            use_semantic_matching=embedding_engine is not None,
        )
        diff_engine = TextDiffEngine(diff_config)
        report = diff_engine.diff_documents(
            chunks_a,
            chunks_b,
            doc_a_name=file_a.name,
            doc_b_name=file_b.name,
        )

        # Semantic analysis
        if semantic_analyzer and report.changes:
            status_text.text("🔬 Analyzing changes semantically...")
            progress_bar.progress(75)

            total_changes = len(report.changes)
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

                # Update progress
                progress_percent = 75 + int((i / total_changes) * 20)
                progress_bar.progress(min(progress_percent, 95))

        # Finalize report
        status_text.text("📊 Generating report...")
        progress_bar.progress(95)

        report.processing_time_seconds = time.time() - start_time
        if llm_client:
            report.llm_calls_made = llm_client.call_count
        if embedding_engine:
            report.embeddings_computed = len(chunks_a) + len(chunks_b)

        report._compute_summary()

        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        time.sleep(0.5)

        progress_bar.empty()
        status_text.empty()

        return report

    finally:
        # Cleanup temp files
        path_a.unlink(missing_ok=True)
        path_b.unlink(missing_ok=True)


def render_summary(report: DiffReport):
    """Render summary statistics."""
    st.subheader("📊 Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Critical",
            value=report.summary.critical_changes,
            delta=None,
            delta_color="off"
        )

    with col2:
        st.metric(
            label="High",
            value=report.summary.high_changes,
            delta=None,
            delta_color="off"
        )

    with col3:
        st.metric(
            label="Medium",
            value=report.summary.medium_changes,
            delta=None,
            delta_color="off"
        )

    with col4:
        st.metric(
            label="Low",
            value=report.summary.low_changes,
            delta=None,
            delta_color="off"
        )

    with col5:
        st.metric(
            label="Total Changes",
            value=report.summary.total_changes,
            delta=None,
            delta_color="off"
        )

    # Additional metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Processing Time", f"{report.processing_time_seconds:.2f}s")

    with col2:
        st.metric("LLM Calls", report.llm_calls_made or 0)

    with col3:
        st.metric("Embeddings Computed", report.embeddings_computed or 0)


def get_significance_badge(significance: Significance) -> str:
    """Get HTML badge for significance level."""
    colors = {
        Significance.CRITICAL: "#d62728",
        Significance.HIGH: "#ff7f0e",
        Significance.MEDIUM: "#2ca02c",
        Significance.LOW: "#7f7f7f",
        Significance.NONE: "#bcbcbc",
    }

    color = colors.get(significance, "#bcbcbc")

    return f'<span style="background-color: {color}; color: white; padding: 0.25rem 0.75rem; border-radius: 0.25rem; font-weight: bold; font-size: 0.8rem;">{significance.value.upper()}</span>'


def get_change_type_icon(change_type: ChangeType) -> str:
    """Get icon for change type."""
    icons = {
        ChangeType.ADDED: "➕",
        ChangeType.REMOVED: "➖",
        ChangeType.MODIFIED: "✏️",
        ChangeType.UNCHANGED: "➡️",
    }
    return icons.get(change_type, "•")


def render_changes(report: DiffReport, min_significance: str):
    """Render changes table."""
    st.subheader("📝 Changes")

    # Filter changes by significance
    min_sig = Significance(min_significance)
    sig_order = {
        Significance.CRITICAL: 5,
        Significance.HIGH: 4,
        Significance.MEDIUM: 3,
        Significance.LOW: 2,
        Significance.NONE: 1,
    }

    filtered_changes = [
        change for change in report.changes
        if sig_order.get(change.significance, 0) >= sig_order.get(min_sig, 0)
    ]

    if not filtered_changes:
        st.info(f"No changes found with significance level '{min_significance}' or higher.")
        return

    st.write(f"Showing {len(filtered_changes)} of {len(report.changes)} changes")

    # Render each change
    for i, change in enumerate(filtered_changes):
        with st.expander(
            f"{get_change_type_icon(change.change_type)} Change #{i+1} - "
            f"{change.change_type.value.upper()}",
            expanded=False
        ):
            # Significance badge
            st.markdown(get_significance_badge(change.significance), unsafe_allow_html=True)

            # Location info
            st.caption(f"Location: {change.location_before or change.location_after}")

            # Similarity score
            if change.similarity_score is not None:
                st.caption(f"Similarity: {change.similarity_score:.2%}")

            st.divider()

            # Show text changes
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Before:**")
                if change.text_before:
                    st.text_area(
                        "Before",
                        value=change.text_before,
                        height=150,
                        key=f"before_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    st.info("(Content added)")

            with col2:
                st.markdown("**After:**")
                if change.text_after:
                    st.text_area(
                        "After",
                        value=change.text_after,
                        height=150,
                        key=f"after_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    st.info("(Content removed)")

            # Semantic analysis
            if change.semantic_analysis:
                st.divider()
                st.markdown("**🔬 Semantic Analysis:**")

                analysis = change.semantic_analysis

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Confidence:** {analysis.confidence:.1%}")
                    st.write(f"**Requires Review:** {'Yes' if analysis.requires_review else 'No'}")

                with col2:
                    categories = ", ".join([cat.value for cat in analysis.categories])
                    st.write(f"**Categories:** {categories}")

                if analysis.explanation:
                    st.write(f"**Explanation:** {analysis.explanation}")

                if analysis.business_impact:
                    st.write(f"**Business Impact:** {analysis.business_impact}")

                if analysis.regulatory_impact:
                    st.write(f"**Regulatory Impact:** {analysis.regulatory_impact}")


def render_download_buttons(report: DiffReport, min_significance: str):
    """Render download buttons."""
    st.subheader("💾 Download Reports")

    col1, col2 = st.columns(2)

    # Generate reports if not already cached
    if st.session_state.html_report is None:
        generator = HTMLReportGenerator()
        st.session_state.html_report = generator.generate(report)

    if st.session_state.json_report is None:
        min_sig = Significance(min_significance)
        exporter = JSONExporter(filter_significance=min_sig)
        st.session_state.json_report = exporter.export(report)

    with col1:
        st.download_button(
            label="📄 Download HTML Report",
            data=st.session_state.html_report,
            file_name=f"diff_report_{report.report_id[:8]}.html",
            mime="text/html",
        )

    with col2:
        st.download_button(
            label="📊 Download JSON Report",
            data=st.session_state.json_report,
            file_name=f"diff_report_{report.report_id[:8]}.json",
            mime="application/json",
        )


def main():
    """Main application."""
    initialize_session_state()
    render_header()

    # Get configuration from sidebar
    config = render_sidebar()

    # File upload
    file_a, file_b = render_file_upload()

    # Compare button
    st.divider()
    compare_button = st.button("🚀 Compare Documents", disabled=not (file_a and file_b))

    if compare_button and file_a and file_b:
        st.session_state.processing_complete = False
        st.session_state.html_report = None
        st.session_state.json_report = None

        with st.spinner("Processing documents..."):
            report = process_documents(file_a, file_b, config)

            if report:
                st.session_state.report = report
                st.session_state.processing_complete = True
                st.success("✅ Analysis complete!")
            else:
                st.error("❌ Failed to process documents")

    # Display results
    if st.session_state.processing_complete and st.session_state.report:
        st.divider()
        render_summary(st.session_state.report)
        st.divider()
        render_changes(st.session_state.report, config["min_significance"])
        st.divider()
        render_download_buttons(st.session_state.report, config["min_significance"])

    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "Policy Diff Analyzer v0.1.0 | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

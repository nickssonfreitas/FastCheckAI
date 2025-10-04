"""
FastCheckAI - Automated PDF Technical Document Comparison

This package provides modules for comparing technical PDF documents using
hybrid processing (PyMuPDF + pdfplumber) and semantic analysis via Agno Framework.
"""

__version__ = "0.1.0"
__author__ = "FastCheckAI Team"

# =============================================================================
# Backward Compatibility Layer
# =============================================================================
# Re-export commonly used classes and functions to maintain old import paths
# This allows existing code to work without changes after refactoring

# Core configuration and exceptions
from src.comparators.semantic_comparator import (
    classify_semantic_significance,
    create_semantic_agent,
    get_semantic_stats,
)

# Comparators
from src.comparators.table_comparator import compare_tables
from src.comparators.text_comparator import compare_text
from src.core import config
from src.core.exceptions import (
    AlignmentError,
    ConfigurationError,
    FastCheckAIError,
    LLMError,
    PDFProcessingError,
    ReportGenerationError,
)

# Extractors
from src.extractors.pdf_loader import load_pdf, validate_pdf_size
from src.extractors.table_extractor import detect_table_pages, extract_tables
from src.extractors.text_extractor import (
    extract_text,
    is_text_corrupted,
    parse_section_hierarchy,
)

# Pipeline API (most important for external usage)
from src.pipelines.semantic_comparison import (
    ComparisonResult,
    PDFComparisonPipeline,
)

# Processing
from src.processing.section_aligner import align_sections, get_section_by_id

# Reporters
from src.reporters.report_generator import format_for_display, generate_report, save_report

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Configuration
    "config",
    # Exceptions
    "FastCheckAIError",
    "ConfigurationError",
    "PDFProcessingError",
    "AlignmentError",
    "LLMError",
    "ReportGenerationError",
    # Pipeline API
    "PDFComparisonPipeline",
    "ComparisonResult",
    # Extractors
    "load_pdf",
    "validate_pdf_size",
    "extract_text",
    "parse_section_hierarchy",
    "is_text_corrupted",
    "extract_tables",
    "detect_table_pages",
    # Processing
    "align_sections",
    "get_section_by_id",
    # Comparators
    "compare_text",
    "compare_tables",
    "classify_semantic_significance",
    "create_semantic_agent",
    "get_semantic_stats",
    # Reporters
    "generate_report",
    "save_report",
    "format_for_display",
]

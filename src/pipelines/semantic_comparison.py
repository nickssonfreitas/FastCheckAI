"""
Pipeline API Module for FastCheckAI

This module provides a programmatic Python API for PDF comparison, enabling
integration into scripts, automation workflows, and production systems without
requiring Jupyter notebooks.

The main entry point is PDFComparisonPipeline, which orchestrates the complete
comparison workflow from PDF loading to report generation.

Example:
    >>> from src.pipeline import PDFComparisonPipeline
    >>> pipeline = PDFComparisonPipeline(
    ...     enable_ocr=True,
    ...     llm_model="gpt-4o",
    ...     output_dir="outputs/"
    ... )
    >>> result = pipeline.run(
    ...     pdf1_path="data/inputs/astm_2015.pdf",
    ...     pdf2_path="data/inputs/astm_2016.pdf",
    ...     report_format="html"
    ... )
    >>> print(f"Changes found: {result.statistics['total_changes']}")
    >>> print(f"Report saved to: {result.report_path}")
"""

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional

from src.core import config
from src.extractors.pdf_loader import load_pdf
from src.reporters.report_generator import generate_report, save_report
from src.processing.section_aligner import align_sections, get_section_by_id
from src.comparators.semantic_comparator import (
    create_semantic_agent,
    classify_semantic_significance,
    get_semantic_stats,
)
from src.extractors.table_extractor import extract_tables, detect_table_pages
from src.comparators.text_comparator import compare_text
from src.extractors.text_extractor import extract_text, parse_section_hierarchy
from src.core.exceptions import (
    ConfigurationError,
    PDFProcessingError,
    AlignmentError,
    LLMError,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Result Dataclass
# =============================================================================


@dataclass
class ComparisonResult:
    """
    Structured output from pipeline execution.

    This dataclass encapsulates all results from a PDF comparison run,
    including changes detected, statistics, metadata, and file references.

    Attributes
    ----------
    changes : list[dict]
        List of change objects with section, type, severity, and diffs
    statistics : dict
        Summary statistics (total_changes, severity_breakdown, etc.)
    metadata : dict
        Processing information (timestamp, versions, configuration)
    pdf1_path : Path
        Path to first PDF (baseline version)
    pdf2_path : Path
        Path to second PDF (new version)
    report_path : Optional[Path]
        Path to generated report file (if report was created)
    alignment_confidence : float
        Average confidence of section alignments (0.0-1.0)
    ocr_pages_count : int
        Number of pages that required OCR processing
    llm_api_calls : int
        Number of LLM API calls made during analysis
    processing_time_seconds : float
        Total pipeline execution time in seconds

    Examples
    --------
    >>> result = pipeline.run("pdf1.pdf", "pdf2.pdf")
    >>> print(f"Found {len(result.changes)} changes")
    >>> print(f"Processing took {result.processing_time_seconds:.2f}s")
    >>> df = result.to_dataframe()  # Convert to pandas for analysis
    """

    changes: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    metadata: Dict[str, Any]
    pdf1_path: Path
    pdf2_path: Path
    report_path: Optional[Path] = None
    alignment_confidence: float = 0.0
    ocr_pages_count: int = 0
    llm_api_calls: int = 0
    processing_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Export result as dictionary for JSON serialization.

        Returns
        -------
        dict
            All result data as nested dictionary

        Examples
        --------
        >>> result_dict = result.to_dict()
        >>> import json
        >>> json.dump(result_dict, open('result.json', 'w'))
        """
        return {
            "changes": self.changes,
            "statistics": self.statistics,
            "metadata": self.metadata,
            "pdf1_path": str(self.pdf1_path),
            "pdf2_path": str(self.pdf2_path),
            "report_path": str(self.report_path) if self.report_path else None,
            "alignment_confidence": self.alignment_confidence,
            "ocr_pages_count": self.ocr_pages_count,
            "llm_api_calls": self.llm_api_calls,
            "processing_time_seconds": self.processing_time_seconds,
        }

    def to_dataframe(self):
        """
        Convert changes to pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame with one row per change

        Examples
        --------
        >>> df = result.to_dataframe()
        >>> critical = df[df['severity'] == 'CRITICAL']
        >>> print(f"Critical changes: {len(critical)}")
        """
        try:
            import pandas as pd

            return pd.DataFrame(self.changes)
        except ImportError:
            logger.warning("pandas not installed, cannot convert to DataFrame")
            return None


# =============================================================================
# Pipeline Class
# =============================================================================


class PDFComparisonPipeline:
    """
    End-to-end pipeline for comparing two PDF documents.

    This class orchestrates the complete workflow for comparing technical PDFs,
    including text extraction, section alignment, semantic analysis, and report
    generation. Designed for programmatic use in scripts and automation systems.

    Parameters
    ----------
    enable_ocr : bool, default=True
        Use OCR fallback for corrupted text (slower but more accurate)
    ocr_dpi : int, default=300
        OCR rendering resolution (150=fast, 300=standard, 600=high quality)
    corruption_threshold : float, default=0.3
        Text corruption detection sensitivity (0.0-1.0)
    llm_model : {"gpt-4o", "gpt-4o-mini", "gpt-4-turbo"}, default="gpt-4o"
        OpenAI model for semantic analysis
    llm_temperature : float, default=0.3
        LLM creativity level (0.0=deterministic, 1.0=creative)
    openai_api_key : str, optional
        OpenAI API key (defaults to OPENAI_API_KEY environment variable)
    fuzzy_match_threshold : float, default=0.8
        Minimum similarity for section alignment (0.0-1.0)
    use_llm_alignment : bool, default=True
        Use LLM for ambiguous section matches
    output_dir : str or Path, default="data/outputs"
        Directory for generated reports
    default_report_format : {"markdown", "html", "json"}, default="markdown"
        Default output format if not specified in run()
    log_level : {"DEBUG", "INFO", "WARNING", "ERROR"}, default="INFO"
        Logging verbosity
    progress_callback : callable, optional
        Function(stage, progress, message) for tracking progress

    Raises
    ------
    ConfigurationError
        If invalid configuration parameters provided
    EnvironmentError
        If OpenAI API key not found in environment

    Examples
    --------
    >>> # Basic usage
    >>> pipeline = PDFComparisonPipeline()
    >>> result = pipeline.run("pdf1.pdf", "pdf2.pdf")

    >>> # Custom configuration
    >>> pipeline = PDFComparisonPipeline(
    ...     enable_ocr=False,
    ...     llm_model="gpt-4o-mini",
    ...     output_dir="custom_output/",
    ...     log_level="DEBUG"
    ... )

    >>> # With progress tracking
    >>> def progress_handler(stage, pct, msg):
    ...     print(f"[{stage}] {pct:.0f}% - {msg}")
    >>> pipeline = PDFComparisonPipeline(progress_callback=progress_handler)
    """

    def __init__(
        self,
        # Extraction settings
        enable_ocr: bool = True,
        ocr_dpi: int = 300,
        corruption_threshold: float = 0.3,
        # LLM settings
        llm_model: Literal["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"] = "gpt-4o",
        llm_temperature: float = 0.3,
        openai_api_key: Optional[str] = None,
        # Alignment settings
        fuzzy_match_threshold: float = 0.8,
        use_llm_alignment: bool = True,
        # Output settings
        output_dir: str | Path = "data/outputs",
        default_report_format: Literal["markdown", "html", "json"] = "markdown",
        # Logging
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
        progress_callback: Optional[Callable[[str, float, str], None]] = None,
    ):
        """Initialize PDF comparison pipeline."""
        # Validate configuration
        self._validate_config(
            ocr_dpi=ocr_dpi,
            corruption_threshold=corruption_threshold,
            fuzzy_match_threshold=fuzzy_match_threshold,
            llm_temperature=llm_temperature,
        )

        # Store configuration
        self.enable_ocr = enable_ocr
        self.ocr_dpi = ocr_dpi
        self.corruption_threshold = corruption_threshold
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.fuzzy_match_threshold = fuzzy_match_threshold
        self.use_llm_alignment = use_llm_alignment
        self.output_dir = Path(output_dir)
        self.default_report_format = default_report_format
        self.progress_callback = progress_callback

        # Validate API key
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise EnvironmentError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass openai_api_key parameter."
            )

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Create output directory if needed
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize state
        self.last_result: Optional[ComparisonResult] = None
        self._semantic_agent = None  # Lazy loading

        self.logger.info(f"Pipeline initialized: OCR={enable_ocr}, Model={llm_model}")

    def _validate_config(
        self,
        ocr_dpi: int,
        corruption_threshold: float,
        fuzzy_match_threshold: float,
        llm_temperature: float,
    ):
        """Validate constructor parameters."""
        if not 150 <= ocr_dpi <= 600:
            raise ConfigurationError(
                f"ocr_dpi must be between 150-600, got {ocr_dpi}"
            )

        if not 0.0 <= corruption_threshold <= 1.0:
            raise ConfigurationError(
                f"corruption_threshold must be between 0.0-1.0, got {corruption_threshold}"
            )

        if not 0.0 <= fuzzy_match_threshold <= 1.0:
            raise ConfigurationError(
                f"fuzzy_match_threshold must be between 0.0-1.0, got {fuzzy_match_threshold}"
            )

        if not 0.0 <= llm_temperature <= 2.0:
            raise ConfigurationError(
                f"llm_temperature must be between 0.0-2.0, got {llm_temperature}"
            )

    def _progress(self, stage: str, pct: float, msg: str):
        """Internal progress tracking."""
        self.logger.info(f"[{stage.upper()}] {pct:.0f}% - {msg}")
        if self.progress_callback:
            try:
                self.progress_callback(stage, pct, msg)
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {e}")

    def run(
        self,
        pdf1_path: str | Path,
        pdf2_path: str | Path,
        report_format: Optional[Literal["markdown", "html", "json"]] = None,
        report_filename: Optional[str] = None,
    ) -> ComparisonResult:
        """
        Execute complete comparison pipeline.

        This method orchestrates all stages of PDF comparison:
        1. Load and validate PDFs
        2. Extract text (with OCR fallback if enabled)
        3. Extract tables
        4. Align sections between documents
        5. Compare text content
        6. Perform semantic analysis (LLM)
        7. Generate comparison report

        Parameters
        ----------
        pdf1_path : str or Path
            Path to first PDF (baseline/reference version)
        pdf2_path : str or Path
            Path to second PDF (new/modified version)
        report_format : {"markdown", "html", "json"}, optional
            Output format (overrides default_report_format)
        report_filename : str, optional
            Custom report filename (auto-generated if None)

        Returns
        -------
        ComparisonResult
            Structured results with changes, statistics, and file references

        Raises
        ------
        PDFProcessingError
            If PDF loading or text extraction fails
        AlignmentError
            If section alignment confidence is below threshold
        LLMError
            If semantic analysis fails after retries

        Examples
        --------
        >>> pipeline = PDFComparisonPipeline()
        >>> result = pipeline.run("v2015.pdf", "v2016.pdf", report_format="html")
        >>> print(f"Found {result.statistics['total_changes']} changes")
        >>> print(f"Report: {result.report_path}")
        """
        start_time = time.time()
        pdf1_path = Path(pdf1_path)
        pdf2_path = Path(pdf2_path)
        format_to_use = report_format or self.default_report_format

        self._progress("initialization", 0, "Starting pipeline")
        self.logger.info(f"Comparing: {pdf1_path.name} → {pdf2_path.name}")

        try:
            # Stage 1: Load PDFs (0-10%)
            self._progress("loading", 5, f"Loading {pdf1_path.name}")
            pdf1_doc = load_pdf(str(pdf1_path))
            self._progress("loading", 8, f"Loading {pdf2_path.name}")
            pdf2_doc = load_pdf(str(pdf2_path))
            self.logger.info(
                f"PDFs loaded: {len(pdf1_doc)} pages, {len(pdf2_doc)} pages"
            )

            # Stage 2: Extract text (10-40%)
            self._progress("extraction", 15, "Extracting text from PDF 1")
            text1 = extract_text(
                pdf1_doc,
                enable_ocr=self.enable_ocr,
                corruption_threshold=self.corruption_threshold,
                ocr_dpi=self.ocr_dpi,
            )
            self._progress("extraction", 30, "Extracting text from PDF 2")
            text2 = extract_text(
                pdf2_doc,
                enable_ocr=self.enable_ocr,
                corruption_threshold=self.corruption_threshold,
                ocr_dpi=self.ocr_dpi,
            )
            self.logger.info(f"Text extracted: {len(text1)} / {len(text2)} characters")

            # Stage 3: Parse sections (40-50%)
            self._progress("parsing", 42, "Parsing sections from PDF 1")
            sections_a = parse_section_hierarchy(text1)
            self._progress("parsing", 48, "Parsing sections from PDF 2")
            sections_b = parse_section_hierarchy(text2)
            self.logger.info(
                f"Sections parsed: {len(sections_a)} / {len(sections_b)}"
            )

            # Stage 4: Align sections (50-60%)
            self._progress("alignment", 55, "Aligning sections")
            alignment_result = align_sections(
                sections_a,
                sections_b,
                use_llm_fallback=self.use_llm_alignment,
            )

            avg_confidence = alignment_result["metadata"]["avg_confidence"]
            aligned_count = len(alignment_result["alignments"])
            self.logger.info(
                f"Alignment complete: {aligned_count} matches, "
                f"confidence={avg_confidence:.2%}"
            )

            # Check alignment quality
            if avg_confidence < 0.5:
                raise AlignmentError(
                    f"Section alignment confidence too low: {avg_confidence:.2%}. "
                    "Try enabling LLM alignment or check PDF quality."
                )

            # Stage 5-6: Compare and analyze (60-85%)
            self._progress("comparison", 65, "Comparing text content")
            changes = self._compare_and_analyze(
                alignment_result, sections_a, sections_b
            )
            self.logger.info(f"Comparison complete: {len(changes)} changes detected")

            # Stage 7: Generate report (85-95%)
            self._progress("reporting", 90, f"Generating {format_to_use} report")
            report_path = self._generate_report(
                changes,
                str(pdf1_path),
                str(pdf2_path),
                format_to_use,
                report_filename,
            )

            # Stage 8: Build result (95-100%)
            self._progress("finalization", 98, "Building result object")
            result = self._build_result(
                changes=changes,
                pdf1_path=pdf1_path,
                pdf2_path=pdf2_path,
                report_path=report_path,
                alignment_confidence=avg_confidence,
                processing_time=time.time() - start_time,
            )

            self.last_result = result
            self._progress("complete", 100, "Pipeline finished successfully")

            self.logger.info(
                f"Pipeline complete in {result.processing_time_seconds:.2f}s"
            )
            return result

        except PDFProcessingError:
            raise
        except AlignmentError:
            raise
        except LLMError:
            raise
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise PDFProcessingError(f"Pipeline execution failed: {e}") from e

    def _compare_and_analyze(
        self,
        alignment_result: Dict,
        sections_a: Dict,
        sections_b: Dict,
    ) -> List[Dict]:
        """
        Compare aligned sections and perform semantic analysis.

        Parameters
        ----------
        alignment_result : dict
            Result from align_sections()
        sections_a : dict
            Hierarchical sections from PDF 1
        sections_b : dict
            Hierarchical sections from PDF 2

        Returns
        -------
        list[dict]
            List of change objects with semantic analysis
        """
        changes = []
        self.logger.debug(f"Comparing {len(alignment_result['alignments'])} alignments")

        # Create semantic agent (lazy loading)
        if self._semantic_agent is None:
            try:
                self._semantic_agent = create_semantic_agent()
            except Exception as e:
                self.logger.warning(f"Failed to create semantic agent: {e}")
                self._semantic_agent = None

        # Process aligned sections
        for section_id_a, alignment_data in alignment_result["alignments"].items():
            section_id_b = alignment_data["section_b_id"]
            confidence = alignment_data["confidence"]

            # Get full section data
            section_a = get_section_by_id(sections_a, section_id_a)
            section_b = get_section_by_id(sections_b, section_id_b)

            if not section_a or not section_b:
                continue

            # Compare text content
            text_a = section_a.get("content", "")
            text_b = section_b.get("content", "")

            diff_result = compare_text(text_a, text_b)

            if diff_result.get("has_differences"):
                change = {
                    "section_id": section_id_a,
                    "section_title": alignment_data.get("title_a", section_id_a),
                    "type": "modified",
                    "confidence": confidence,
                    "old_text": text_a[:500],  # Preview only
                    "new_text": text_b[:500],
                    "diff_summary": diff_result.get("summary", ""),
                    "critical_terms": diff_result.get("critical_terms", []),
                    "severity": "MINOR",  # Default
                }

                # Semantic analysis if agent available
                if self._semantic_agent and diff_result.get("differences"):
                    first_diff = diff_result["differences"][0]
                    semantic_result = classify_semantic_significance(
                        {
                            "original": first_diff.get("original", ""),
                            "content": first_diff.get("modified", ""),
                        },
                        agent=self._semantic_agent,
                    )

                    change["semantic_analysis"] = semantic_result
                    change["severity"] = self._map_semantic_to_severity(
                        semantic_result.get("classification")
                    )

                # Check for critical terms
                if diff_result.get("critical_terms"):
                    change["severity"] = "CRITICAL"

                changes.append(change)

        # Add removed sections
        for section_data in alignment_result.get("removed", []):
            changes.append(
                {
                    "section_id": section_data["id"],
                    "section_title": section_data["title"],
                    "type": "removed",
                    "severity": "SIGNIFICANT",
                    "confidence": 1.0,
                }
            )

        # Add new sections
        for section_data in alignment_result.get("added", []):
            changes.append(
                {
                    "section_id": section_data["id"],
                    "section_title": section_data["title"],
                    "type": "added",
                    "severity": "SIGNIFICANT",
                    "confidence": 1.0,
                }
            )

        return changes

    def _map_semantic_to_severity(self, semantic_class: Optional[str]) -> str:
        """Map semantic classification to severity level."""
        mapping = {
            "EQUIVALENT": "MINOR",
            "MINOR": "MEDIUM",
            "SIGNIFICANT": "CRITICAL",
        }
        return mapping.get(semantic_class, "MEDIUM")

    def _generate_report(
        self,
        changes: List[Dict],
        doc_a: str,
        doc_b: str,
        format: str,
        filename: Optional[str],
    ) -> Path:
        """Generate comparison report."""
        # Generate filename if not provided
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            ext = "md" if format == "markdown" else format
            filename = f"comparison_report_{timestamp}.{ext}"

        output_path = self.output_dir / filename

        # Generate report content
        report_content = generate_report(
            comparison_results=changes,
            doc_a=doc_a,
            doc_b=doc_b,
            include_statistics=True,
            include_critical_analysis=True,
        )

        # Save report
        save_report(report_content, str(output_path))

        return output_path

    def _build_result(
        self,
        changes: List[Dict],
        pdf1_path: Path,
        pdf2_path: Path,
        report_path: Path,
        alignment_confidence: float,
        processing_time: float,
    ) -> ComparisonResult:
        """Build ComparisonResult from pipeline execution."""
        # Calculate statistics
        total_changes = len(changes)
        severity_counts = {}
        for change in changes:
            severity = change.get("severity", "MEDIUM")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        statistics = {
            "total_changes": total_changes,
            "severity_breakdown": severity_counts,
            "additions": sum(1 for c in changes if c.get("type") == "added"),
            "deletions": sum(1 for c in changes if c.get("type") == "removed"),
            "modifications": sum(1 for c in changes if c.get("type") == "modified"),
        }

        # Get semantic stats if available
        semantic_stats = get_semantic_stats()

        metadata = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pipeline_version": "1.0.0",
            "llm_model": self.llm_model,
            "ocr_enabled": self.enable_ocr,
            "semantic_stats": semantic_stats,
        }

        return ComparisonResult(
            changes=changes,
            statistics=statistics,
            metadata=metadata,
            pdf1_path=pdf1_path,
            pdf2_path=pdf2_path,
            report_path=report_path,
            alignment_confidence=alignment_confidence,
            ocr_pages_count=0,  # TODO: Track from extraction
            llm_api_calls=semantic_stats.get("total_llm_calls", 0),
            processing_time_seconds=processing_time,
        )

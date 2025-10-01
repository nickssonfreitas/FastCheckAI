"""
Table Extraction Module for FastCheckAI

This module handles detection and extraction of tables from PDF documents.
Uses a hybrid approach:
- PyMuPDF (fitz) for fast table detection via line/border analysis
- pdfplumber for accurate table extraction and parsing

Example:
    >>> from src.pdf_loader import load_pdf
    >>> from src.table_extractor import detect_table_pages, extract_tables
    >>> pdf_doc = load_pdf("document.pdf")
    >>> table_pages = detect_table_pages(pdf_doc)
    >>> result = extract_tables("document.pdf", table_pages)
    >>> print(f"Extracted {len(result.tables)} tables")
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pdfplumber
import pymupdf as fitz

from src import config

logger = logging.getLogger(__name__)


# =============================================================================
# Custom Exceptions
# =============================================================================


class TableExtractionError(Exception):
    """Base exception for table extraction errors."""

    pass


class TableDetectionError(TableExtractionError):
    """Raised when table detection fails."""

    pass


class TableParsingError(TableExtractionError):
    """Raised when table parsing fails."""

    pass


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class TableMetadata:
    """Metadata for an extracted table.

    Attributes:
        page_num: Page number where table was found (0-indexed)
        table_index: Index of table on the page (0-indexed)
        row_count: Number of rows in table
        column_count: Number of columns in table
        has_header: Whether table has a detected header row
        caption: Table caption/title if available
        section_context: Section ID where table appears (e.g., "3.2")
        extraction_method: Method used for extraction (e.g., "pdfplumber_lines")
        confidence: Extraction quality score (0.0-1.0)
    """

    page_num: int
    table_index: int
    row_count: int
    column_count: int
    has_header: bool = True
    caption: Optional[str] = None
    section_context: Optional[str] = None
    extraction_method: str = "pdfplumber_lines"
    confidence: float = 1.0

    def __post_init__(self):
        """Validate metadata fields."""
        if self.page_num < 0:
            raise ValueError("page_num must be >= 0")
        if self.table_index < 0:
            raise ValueError("table_index must be >= 0")
        if self.row_count < 0:
            raise ValueError("row_count must be >= 0")
        if self.column_count < 0:
            raise ValueError("column_count must be >= 0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class ExtractedTable:
    """Container for extracted table data and metadata.

    Attributes:
        data: pandas DataFrame containing table data
        metadata: TableMetadata object with extraction details
    """

    data: pd.DataFrame
    metadata: TableMetadata

    def __post_init__(self):
        """Validate extracted table."""
        if self.data is None:
            raise ValueError("data cannot be None")
        if self.metadata is None:
            raise ValueError("metadata cannot be None")


@dataclass
class TableExtractionResult:
    """Results from table extraction operation.

    Attributes:
        tables: List of successfully extracted tables
        failed_pages: List of page numbers where extraction failed
        detection_time_seconds: Time spent detecting table pages
        extraction_time_seconds: Time spent extracting tables
        total_pages_detected: Number of pages with detected tables
        total_tables_extracted: Number of successfully extracted tables
    """

    tables: List[ExtractedTable] = field(default_factory=list)
    failed_pages: List[int] = field(default_factory=list)
    detection_time_seconds: float = 0.0
    extraction_time_seconds: float = 0.0
    total_pages_detected: int = 0
    total_tables_extracted: int = 0

    def summary(self) -> str:
        """Generate human-readable summary of extraction results.

        Returns:
            Formatted summary string
        """
        return (
            f"Table Extraction Summary:\n"
            f"  Pages with tables: {self.total_pages_detected}\n"
            f"  Tables extracted: {self.total_tables_extracted}\n"
            f"  Failed pages: {len(self.failed_pages)}\n"
            f"  Detection time: {self.detection_time_seconds:.2f}s\n"
            f"  Extraction time: {self.extraction_time_seconds:.2f}s\n"
            f"  Total time: {self.detection_time_seconds + self.extraction_time_seconds:.2f}s"
        )


# =============================================================================
# Table Detection
# =============================================================================


def detect_table_pages(
    pdf_doc: fitz.Document,
    horizontal_line_threshold: int = 10,
    vertical_line_threshold: int = 5,
    min_line_length: float = 20.0,
    enable_text_detection: bool = True,
) -> List[int]:
    """Detect pages containing tables using hybrid detection approach.

    Uses two detection methods:
    1. Line-based detection: Analyzes page drawings for horizontal/vertical lines
    2. Text-based detection (fallback): Searches for table indicators like "TABLE 1"

    The text-based detection is especially useful for borderless tables commonly
    found in technical standards (ASTM, ISO, etc.) where tables are formatted
    with spacing rather than visible borders.

    Args:
        pdf_doc: Opened PyMuPDF Document object
        horizontal_line_threshold: Minimum horizontal lines to classify as table page
        vertical_line_threshold: Minimum vertical lines to classify as table page
        min_line_length: Minimum line length in points to count (filters noise)
        enable_text_detection: Enable text-based detection as fallback

    Returns:
        List of page numbers (0-indexed) containing detected tables

    Raises:
        TableDetectionError: If detection fails
        ValueError: If pdf_doc is invalid

    Examples:
        >>> import pymupdf as fitz
        >>> pdf_doc = fitz.open("document.pdf")
        >>> table_pages = detect_table_pages(pdf_doc)
        >>> print(f"Found tables on {len(table_pages)} pages: {table_pages}")
        Found tables on 3 pages: [5, 8, 12]

        >>> # Disable text detection for PDFs with bordered tables only
        >>> table_pages = detect_table_pages(pdf_doc, enable_text_detection=False)
    """
    if pdf_doc is None:
        raise ValueError("pdf_doc cannot be None")

    if pdf_doc.page_count == 0:
        logger.warning("PDF has no pages to detect tables")
        return []

    try:
        start_time = time.time()
        table_pages: List[int] = []
        total_pages = pdf_doc.page_count

        logger.info(
            f"Starting hybrid table detection on {total_pages} pages "
            f"(line-based: H≥{horizontal_line_threshold}, V≥{vertical_line_threshold}, "
            f"text-based: {'enabled' if enable_text_detection else 'disabled'})"
        )

        for page_num in range(total_pages):
            page = pdf_doc[page_num]

            # Get all drawings (lines, rectangles, etc.) from page
            drawings = page.get_drawings()

            # Count horizontal and vertical lines
            horizontal_lines = 0
            vertical_lines = 0

            for drawing in drawings:
                # Each drawing has a "rect" (bounding box) and "items" (path commands)
                for item in drawing.get("items", []):
                    # item is a tuple: (type, *coordinates)
                    # type 'l' = line, 're' = rectangle
                    if not item or len(item) < 1:
                        continue

                    item_type = item[0]

                    if item_type == "l":  # Line
                        # Line coordinates: (x0, y0, x1, y1)
                        if len(item) < 5:
                            continue

                        x0, y0, x1, y1 = item[1], item[2], item[3], item[4]

                        # Calculate line length
                        length = max(abs(x1 - x0), abs(y1 - y0))

                        if length < min_line_length:
                            continue  # Ignore short lines (noise)

                        # Classify as horizontal or vertical
                        if abs(y1 - y0) < 2:  # Nearly horizontal
                            horizontal_lines += 1
                        elif abs(x1 - x0) < 2:  # Nearly vertical
                            vertical_lines += 1

                    elif item_type == "re":  # Rectangle (has 4 lines)
                        # Rectangles contribute to both horizontal and vertical counts
                        if len(item) < 5:
                            continue

                        x0, y0, x1, y1 = item[1], item[2], item[3], item[4]
                        width = abs(x1 - x0)
                        height = abs(y1 - y0)

                        if width >= min_line_length:
                            horizontal_lines += 2  # Top and bottom
                        if height >= min_line_length:
                            vertical_lines += 2  # Left and right

            # Check if page meets line-based criteria
            has_table_lines = (
                horizontal_lines >= horizontal_line_threshold
                and vertical_lines >= vertical_line_threshold
            )

            if has_table_lines:
                table_pages.append(page_num)
                logger.debug(
                    f"Page {page_num + 1}: Table detected via lines "
                    f"(H={horizontal_lines}, V={vertical_lines})"
                )

        # Fallback: Text-based detection for borderless tables
        if enable_text_detection:
            import re

            table_patterns = [
                r'TABLE\s+\d+',   # "TABLE 1", "TABLE 2" (normal)
                r'Table\s+\d+',   # "Table 1", "Table 2" (normal)
                r'FIG\.\s*\d+',   # "FIG. 1" (sometimes includes tables)
                # OCR corruption patterns (common with corrupted fonts)
                r'[ÌT][ßA][ÞB][ÔL][ÛE]\s+[\dï¹²³´µ]+',  # Corrupted "TABLE #"
                r'[Tt]¿¾´»\s+\d+',                      # Corrupted "table"
            ]

            for page_num in range(total_pages):
                # Skip if already detected via lines
                if page_num in table_pages:
                    continue

                page = pdf_doc[page_num]
                text = page.get_text("text")

                # Check for table indicators
                for pattern in table_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        table_pages.append(page_num)
                        logger.debug(
                            f"Page {page_num + 1}: Table detected via text pattern '{pattern}'"
                        )
                        break  # Found table, no need to check other patterns

        # Sort pages and remove duplicates
        table_pages = sorted(set(table_pages))

        detection_time = time.time() - start_time

        logger.info(
            f"Hybrid table detection complete: {len(table_pages)} pages with tables "
            f"in {detection_time:.2f}s"
        )

        return table_pages

    except Exception as e:
        error_msg = f"Table detection failed: {str(e)}"
        logger.error(error_msg)
        raise TableDetectionError(error_msg) from e


# =============================================================================
# Table Extraction
# =============================================================================


def extract_tables(
    pdf_path: str,
    table_pages: List[int],
    section_context: Optional[Dict[int, str]] = None,
) -> TableExtractionResult:
    """Extract tables from specified pages using pdfplumber with hybrid strategies.

    Opens PDF with pdfplumber only for pages with detected tables.
    Uses multiple extraction strategies automatically:
    1. Default pdfplumber settings (for tables with visible borders)
    2. Text-based strategies (fallback for borderless tables)

    Converts raw table data to pandas DataFrames with rich metadata.

    Args:
        pdf_path: Path to PDF file
        table_pages: List of page numbers (0-indexed) to extract tables from
        section_context: Optional dict mapping page_num -> section_id

    Returns:
        TableExtractionResult with extracted tables and metadata

    Raises:
        TableExtractionError: If extraction fails
        FileNotFoundError: If pdf_path doesn't exist

    Examples:
        >>> table_pages = [5, 8, 12]
        >>> result = extract_tables("document.pdf", table_pages)
        >>> print(result.summary())
        >>> for table in result.tables:
        ...     print(f"Page {table.metadata.page_num + 1}: {table.data.shape}")
    """
    pdf_path_obj = Path(pdf_path)
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not table_pages:
        logger.warning("No table pages provided for extraction")
        return TableExtractionResult()

    try:
        start_time = time.time()
        result = TableExtractionResult()
        result.total_pages_detected = len(table_pages)

        logger.info(
            f"Starting hybrid table extraction from {len(table_pages)} pages "
            f"(default + text-based strategies)"
        )

        # Open PDF with pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in table_pages:
                try:
                    # pdfplumber uses 0-indexed pages
                    page = pdf.pages[page_num]

                    # Try to extract tables with default settings first
                    raw_tables = page.extract_tables()

                    # If no tables found and page was detected via text pattern,
                    # try with more aggressive settings for borderless tables
                    if not raw_tables:
                        try:
                            raw_tables = page.extract_tables(
                                table_settings={
                                    "vertical_strategy": "text",
                                    "horizontal_strategy": "text",
                                    "intersection_tolerance": 5,
                                }
                            )
                        except Exception as e:
                            logger.debug(f"Page {page_num + 1}: Alternative extraction failed - {e}")

                    if not raw_tables:
                        logger.debug(f"Page {page_num + 1}: No tables found")
                        continue

                    # Get section context for this page
                    section_id = section_context.get(page_num) if section_context else None

                    # Convert each raw table to DataFrame with metadata
                    for table_index, raw_table in enumerate(raw_tables):
                        extracted_table = _convert_to_dataframe(
                            raw_table=raw_table,
                            page_num=page_num,
                            table_index=table_index,
                            section_context=section_id,
                            extraction_method="pdfplumber_hybrid",
                        )

                        if extracted_table:
                            result.tables.append(extracted_table)
                            result.total_tables_extracted += 1
                            logger.debug(
                                f"Page {page_num + 1}: Extracted table {table_index} "
                                f"({extracted_table.data.shape[0]}x{extracted_table.data.shape[1]})"
                            )

                except Exception as e:
                    logger.warning(f"Page {page_num + 1}: Extraction failed - {str(e)}")
                    result.failed_pages.append(page_num)

        extraction_time = time.time() - start_time
        result.extraction_time_seconds = extraction_time

        logger.info(
            f"Table extraction complete: {result.total_tables_extracted} tables "
            f"from {result.total_pages_detected} pages in {extraction_time:.2f}s"
        )

        return result

    except Exception as e:
        error_msg = f"Table extraction failed: {str(e)}"
        logger.error(error_msg)
        raise TableExtractionError(error_msg) from e


# =============================================================================
# Helper Functions
# =============================================================================


def _convert_to_dataframe(
    raw_table: List[List[str]],
    page_num: int,
    table_index: int,
    section_context: Optional[str] = None,
    extraction_method: str = "pdfplumber_lines",
) -> Optional[ExtractedTable]:
    """Convert raw pdfplumber table to pandas DataFrame with metadata.

    Args:
        raw_table: Raw table data from pdfplumber (list of lists)
        page_num: Page number where table was found (0-indexed)
        table_index: Index of table on the page (0-indexed)
        section_context: Section ID where table appears
        extraction_method: Method used for extraction

    Returns:
        ExtractedTable object or None if conversion fails
    """
    try:
        if not raw_table or len(raw_table) == 0:
            logger.debug(f"Page {page_num + 1}, Table {table_index}: Empty table")
            return None

        # Detect if first row is header
        first_row = raw_table[0]
        has_header = _detect_header_row(first_row)

        # Create DataFrame
        if has_header:
            # Use first row as column names (strip whitespace from headers)
            clean_headers = [h.strip() if isinstance(h, str) else str(h) for h in raw_table[0]]
            df = pd.DataFrame(raw_table[1:], columns=clean_headers)
        else:
            # Generate column names: Col_0, Col_1, etc.
            num_cols = len(raw_table[0])
            df = pd.DataFrame(raw_table, columns=[f"Col_{i}" for i in range(num_cols)])

        # Clean data: strip whitespace, replace None with empty string
        df = df.map(lambda x: x.strip() if isinstance(x, str) else ("" if x is None else x))

        # Calculate confidence score
        confidence = _calculate_table_confidence(df)

        # Create metadata
        metadata = TableMetadata(
            page_num=page_num,
            table_index=table_index,
            row_count=len(df),
            column_count=len(df.columns),
            has_header=has_header,
            section_context=section_context,
            extraction_method=extraction_method,
            confidence=confidence,
        )

        return ExtractedTable(data=df, metadata=metadata)

    except Exception as e:
        logger.warning(
            f"Page {page_num + 1}, Table {table_index}: Conversion failed - {str(e)}"
        )
        return None


def _detect_header_row(first_row: List[str]) -> bool:
    """Detect if first row is header (text) or data (numbers).

    Uses heuristic: If >50% of cells are numeric, treat as data row (no header).

    Args:
        first_row: First row of table

    Returns:
        True if row appears to be a header, False if data
    """
    if not first_row:
        return False

    # Count numeric cells
    numeric_count = 0
    total_cells = len(first_row)

    for cell in first_row:
        if cell is None or cell == "":
            continue

        # Try to parse as number
        try:
            float(str(cell).replace(",", "").strip())
            numeric_count += 1
        except ValueError:
            pass  # Not numeric

    # If >50% numeric, treat as data row
    numeric_ratio = numeric_count / total_cells if total_cells > 0 else 0

    return numeric_ratio <= 0.5


def _calculate_table_confidence(df: pd.DataFrame) -> float:
    """Calculate confidence score for extracted table quality.

    Factors:
    - Empty cell ratio (more empty cells = lower confidence)
    - Table size (very small tables may be noise)

    Args:
        df: pandas DataFrame to analyze

    Returns:
        Confidence score (0.0-1.0)
    """
    if df.empty:
        return 0.0

    # Factor 1: Empty cell ratio
    total_cells = df.shape[0] * df.shape[1]
    empty_cells = df.map(lambda x: x == "" or pd.isna(x)).sum().sum()
    empty_ratio = empty_cells / total_cells if total_cells > 0 else 1.0

    # Empty penalty: 0% empty = 1.0, 100% empty = 0.0
    empty_score = 1.0 - empty_ratio

    # Factor 2: Size penalty (tables <2x2 are suspicious)
    min_rows = 2
    min_cols = 2
    size_score = 1.0

    if df.shape[0] < min_rows or df.shape[1] < min_cols:
        size_score = 0.0  # Very strong penalty for tiny tables

    # Combine factors (equal weighting)
    confidence = 0.5 * empty_score + 0.5 * size_score

    return max(0.0, min(1.0, confidence))

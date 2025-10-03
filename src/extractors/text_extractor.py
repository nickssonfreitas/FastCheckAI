"""
Text Extraction Module for FastCheckAI

This module handles text extraction from PDF documents, section hierarchy parsing,
and metadata extraction. It uses PyMuPDF for fast text extraction and regex-based
parsing for section structure identification.

Example:
    >>> from src.pdf_loader import load_pdf
    >>> from src.text_extractor import extract_text, parse_section_hierarchy
    >>> pdf_doc = load_pdf("document.pdf")
    >>> text = extract_text(pdf_doc)
    >>> sections = parse_section_hierarchy(text)
    >>> print(f"Extracted {len(sections)} top-level sections")
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pymupdf as fitz
import pytesseract
from PIL import Image

from src import config

logger = logging.getLogger(__name__)


class TextExtractionError(Exception):
    """Base exception for text extraction errors."""

    pass


class SectionParsingError(TextExtractionError):
    """Raised when section hierarchy parsing fails."""

    pass


def extract_text(
    pdf_doc: fitz.Document,
    include_page_markers: bool = True,
    enable_ocr: bool | None = None,
    corruption_threshold: float | None = None,
    ocr_dpi: int | None = None,
) -> str:
    """
    Extract complete text from PDF document with automatic OCR fallback.

    Uses hybrid extraction strategy:
    1. Attempts fast PyMuPDF extraction (page.get_text("text"))
    2. Detects corrupted text (broken Unicode mappings)
    3. Falls back to OCR (pytesseract) for corrupted pages

    This solves issues with PDFs using custom fonts with missing ToUnicode CMap,
    which cause PyMuPDF to extract gibberish characters.

    Args:
        pdf_doc: Opened PyMuPDF Document object
        include_page_markers: If True, adds "--- PAGE N ---" markers between pages
        enable_ocr: If True, enables automatic OCR fallback for corrupted pages (default: True)
        corruption_threshold: Max ratio of special chars before triggering OCR (default: 0.30)
        ocr_dpi: Resolution for OCR rendering in DPI (default: 300, higher = better quality)

    Returns:
        Complete text content as string

    Raises:
        TextExtractionError: If extraction fails
        ValueError: If pdf_doc is invalid or has no pages

    Examples:
        >>> import pymupdf as fitz
        >>> pdf_doc = fitz.open("document.pdf")
        >>> text = extract_text(pdf_doc)  # Automatic OCR fallback
        >>> print(f"Extracted {len(text)} characters")
        >>> pdf_doc.close()

        >>> # Disable OCR fallback (fast but may have corrupted text)
        >>> text = extract_text(pdf_doc, enable_ocr=False)

        >>> # Custom OCR settings
        >>> text = extract_text(pdf_doc, corruption_threshold=0.40, ocr_dpi=600)
    """
    if pdf_doc is None:
        raise ValueError("pdf_doc cannot be None")

    if pdf_doc.page_count == 0:
        logger.warning("PDF has no pages to extract")
        return ""

    # Use config defaults if not provided
    if enable_ocr is None:
        enable_ocr = config.ENABLE_OCR
    if corruption_threshold is None:
        corruption_threshold = config.OCR_CORRUPTION_THRESHOLD
    if ocr_dpi is None:
        ocr_dpi = config.OCR_DPI

    try:
        extracted_text: List[str] = []
        total_pages = pdf_doc.page_count
        ocr_pages_count = 0

        logger.info(
            f"Starting hybrid text extraction from {total_pages} pages "
            f"(OCR: {'enabled' if enable_ocr else 'disabled'})"
        )

        for page_num in range(total_pages):
            # Extract text from current page
            page = pdf_doc[page_num]
            page_text = page.get_text("text")

            # Check for corruption and apply OCR fallback if needed
            if enable_ocr and is_text_corrupted(page_text, corruption_threshold):
                logger.info(
                    f"Page {page_num + 1}: Corrupted text detected, using OCR fallback"
                )
                page_text = _extract_page_with_ocr(page, dpi=ocr_dpi)
                ocr_pages_count += 1

            # Add page marker if requested
            if include_page_markers:
                marker = f"\n--- PAGE {page_num + 1} ---\n"
                extracted_text.append(marker)

            extracted_text.append(page_text)

            # Log progress every 10 pages
            if (page_num + 1) % 10 == 0 or (page_num + 1) == total_pages:
                logger.info(f"Extracted page {page_num + 1}/{total_pages}")

        # Concatenate all text
        complete_text = "".join(extracted_text)
        char_count = len(complete_text)

        logger.info(
            f"Text extraction complete: {char_count} characters from {total_pages} pages "
            f"({ocr_pages_count} pages used OCR fallback)"
        )

        return complete_text

    except Exception as e:
        error_msg = f"Failed to extract text from PDF: {str(e)}"
        logger.error(error_msg)
        raise TextExtractionError(error_msg) from e


def is_text_corrupted(text: str, threshold: float = 0.30) -> bool:
    """
    Detect if extracted text has excessive special characters indicating corruption.

    Analyzes the ratio of non-ASCII characters (ord > 127) to identify text
    extracted from PDFs with broken Unicode mappings. Used to trigger OCR fallback.

    Args:
        text: Extracted text to analyze
        threshold: Maximum acceptable ratio of special characters (default: 0.30)

    Returns:
        True if text appears corrupted (>threshold special chars), False otherwise

    Examples:
        >>> text_good = "This is normal ASCII text"
        >>> is_text_corrupted(text_good)
        False

        >>> text_bad = "Ü»­·¹²¿¬·±²æ ßîçñßîçÓ"  # Corrupted Unicode
        >>> is_text_corrupted(text_bad)
        True
    """
    if not text or len(text.strip()) == 0:
        return False

    # Count non-ASCII characters (potential corruption indicators)
    special_char_count = sum(1 for c in text if ord(c) > 127)
    total_chars = len(text)

    # Calculate ratio
    corruption_ratio = special_char_count / total_chars if total_chars > 0 else 0

    logger.debug(
        f"Corruption check: {special_char_count}/{total_chars} "
        f"special chars ({corruption_ratio:.2%}), threshold: {threshold:.0%}"
    )

    return corruption_ratio > threshold


def _extract_page_with_ocr(page: fitz.Page, dpi: int = 300) -> str:
    """
    Extract text from PDF page using OCR (Optical Character Recognition).

    Used as fallback when PyMuPDF extraction produces corrupted text due to
    broken font encodings. Renders page to image and applies Tesseract OCR.

    Args:
        page: PyMuPDF Page object to extract text from
        dpi: Resolution for page rendering (default: 300, higher = better quality)

    Returns:
        OCR-extracted text as string

    Raises:
        TextExtractionError: If OCR extraction fails

    Examples:
        >>> import pymupdf as fitz
        >>> pdf_doc = fitz.open("corrupted.pdf")
        >>> page = pdf_doc[0]
        >>> text = _extract_page_with_ocr(page)
        >>> print(f"Extracted {len(text)} characters via OCR")
    """
    try:
        logger.debug(f"Starting OCR extraction for page at {dpi} DPI")

        # Render page to pixmap (image) at specified DPI
        # matrix scales the page: dpi/72 (72 is PDF's base DPI)
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)

        # Convert PyMuPDF pixmap to PIL Image
        # pixmap.samples is raw RGB bytes
        img = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

        # Run Tesseract OCR on image
        ocr_text = pytesseract.image_to_string(img, lang="eng")

        logger.debug(f"OCR extracted {len(ocr_text)} characters")

        return ocr_text

    except Exception as e:
        error_msg = f"OCR extraction failed: {str(e)}"
        logger.error(error_msg)
        raise TextExtractionError(error_msg) from e


def parse_section_hierarchy(
    text: str, section_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
    """
    Parse section hierarchy from extracted text using regex patterns.

    Detects numbered sections (1, 1.1, 1.2.3) and creates nested dictionary
    structure preserving hierarchy levels. Captures section titles and content.

    Default pattern matches: "1.2 Section Title" or "1.2.3 Subsection Title"
    where section numbers are followed by space and capitalized text.

    Args:
        text: Extracted text from PDF
        section_pattern: Custom regex pattern (default: r"^\\s*(\\d+(?:\\.\\d+)*)\\s+([A-Z][^\\n]+)")

    Returns:
        Nested dictionary with structure:
        {
            "1": {
                "id": "1",
                "title": "Scope",
                "level": 1,
                "content": "Section content...",
                "subsections": {
                    "1.1": {...},
                    "1.2": {...}
                }
            },
            "2": {...}
        }

    Raises:
        SectionParsingError: If parsing fails or no sections found
        ValueError: If text is empty or None

    Examples:
        >>> text = "1 Scope\\nThis standard covers...\\n2 References\\n..."
        >>> sections = parse_section_hierarchy(text)
        >>> print(sections["1"]["title"])
        'Scope'
        >>> print(list(sections.keys()))
        ['1', '2']
    """
    if not text:
        raise ValueError("Text cannot be empty or None")

    # Default regex pattern for section detection
    if section_pattern is None:
        # Matches: "1.2.3 Title" or "1 Title" (numbers, dot-separated, space, capitalized text)
        section_pattern = r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][^\n]+)"

    try:
        # Find all section matches with line numbers
        pattern = re.compile(section_pattern, re.MULTILINE)
        matches = list(pattern.finditer(text))

        if not matches:
            logger.warning("No sections found in text with default pattern")
            return {}

        logger.info(f"Found {len(matches)} section headers")

        # Build flat list of sections with positions
        sections_flat: List[Dict[str, Any]] = []

        for i, match in enumerate(matches):
            section_id = match.group(1)
            section_title = match.group(2).strip()
            start_pos = match.start()

            # Content is from current match end to next match start (or end of text)
            content_start = match.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[content_start:content_end].strip()

            # Calculate section level (count dots + 1)
            level = section_id.count(".") + 1

            sections_flat.append(
                {
                    "id": section_id,
                    "title": section_title,
                    "level": level,
                    "content": content,
                    "position": start_pos,
                    "subsections": {},
                }
            )

        # Build hierarchical structure
        hierarchy = _build_hierarchy(sections_flat)

        # Log summary
        level_counts = {}
        for section in sections_flat:
            level = section["level"]
            level_counts[level] = level_counts.get(level, 0) + 1

        logger.info(f"Section hierarchy parsed: {level_counts}")

        return hierarchy

    except Exception as e:
        error_msg = f"Failed to parse section hierarchy: {str(e)}"
        logger.error(error_msg)
        raise SectionParsingError(error_msg) from e


def _build_hierarchy(sections_flat: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build nested hierarchy from flat section list.

    Args:
        sections_flat: Flat list of sections with id, level, and content

    Returns:
        Nested dictionary with top-level sections as keys
    """
    hierarchy: Dict[str, Any] = {}

    # Track parent sections at each level for efficient lookup
    parents: Dict[int, Dict[str, Any]] = {}

    for section in sections_flat:
        section_id = section["id"]
        level = section["level"]

        # Create section dict (without position, as it's internal)
        section_dict = {
            "id": section_id,
            "title": section["title"],
            "level": level,
            "content": section["content"],
            "subsections": {},
        }

        if level == 1:
            # Top-level section
            hierarchy[section_id] = section_dict
            parents[1] = section_dict
        else:
            # Find parent (previous level)
            parent_level = level - 1
            if parent_level in parents:
                parent = parents[parent_level]
                parent["subsections"][section_id] = section_dict
            else:
                # Orphaned section - add to root with warning
                logger.warning(f"Orphaned section {section_id} at level {level}")
                hierarchy[section_id] = section_dict

        # Update parent tracker for this level
        parents[level] = section_dict

        # Clear deeper levels (they're no longer relevant)
        for deeper_level in list(parents.keys()):
            if deeper_level > level:
                del parents[deeper_level]

    return hierarchy


def extract_metadata(pdf_doc: fitz.Document) -> Dict[str, Any]:
    """
    Extract metadata from PDF document.

    Retrieves standard metadata fields: page count, title, author, creation date.
    Returns "N/A" for fields not available in the PDF.

    Args:
        pdf_doc: Opened PyMuPDF Document object

    Returns:
        Dictionary with metadata fields:
        {
            "page_count": int,
            "title": str,
            "author": str,
            "creation_date": str (ISO 8601),
            "subject": str,
            "keywords": str,
            "creator": str,
            "producer": str,
            "format": str (e.g., "PDF 1.4")
        }

    Raises:
        ValueError: If pdf_doc is None or invalid

    Examples:
        >>> import pymupdf as fitz
        >>> pdf_doc = fitz.open("document.pdf")
        >>> metadata = extract_metadata(pdf_doc)
        >>> print(f"Title: {metadata['title']}")
        >>> print(f"Pages: {metadata['page_count']}")
        >>> pdf_doc.close()
    """
    if pdf_doc is None:
        raise ValueError("pdf_doc cannot be None")

    try:
        # Basic document info
        metadata = {
            "page_count": pdf_doc.page_count,
            "format": pdf_doc.metadata.get("format", "N/A"),
        }

        # Extract metadata from document
        doc_metadata = pdf_doc.metadata

        # Standard fields with fallback to "N/A"
        metadata["title"] = doc_metadata.get("title", "N/A").strip() or "N/A"
        metadata["author"] = doc_metadata.get("author", "N/A").strip() or "N/A"
        metadata["subject"] = doc_metadata.get("subject", "N/A").strip() or "N/A"
        metadata["keywords"] = doc_metadata.get("keywords", "N/A").strip() or "N/A"
        metadata["creator"] = doc_metadata.get("creator", "N/A").strip() or "N/A"
        metadata["producer"] = doc_metadata.get("producer", "N/A").strip() or "N/A"

        # Parse creation date (PyMuPDF format: "D:YYYYMMDDHHmmSS")
        creation_date_raw = doc_metadata.get("creationDate", "")
        metadata["creation_date"] = _parse_pdf_date(creation_date_raw)

        logger.info(f"Metadata extracted: {metadata['page_count']} pages, title: {metadata['title']}")

        return metadata

    except Exception as e:
        logger.warning(f"Failed to extract some metadata: {str(e)}")
        # Return minimal metadata on error
        return {
            "page_count": pdf_doc.page_count if pdf_doc else 0,
            "title": "N/A",
            "author": "N/A",
            "creation_date": "N/A",
            "subject": "N/A",
            "keywords": "N/A",
            "creator": "N/A",
            "producer": "N/A",
            "format": "N/A",
        }


def _parse_pdf_date(date_str: str) -> str:
    """
    Parse PDF date string to ISO 8601 format.

    PDF dates format: "D:YYYYMMDDHHmmSS+HH'mm'" or similar variants.

    Args:
        date_str: PDF date string

    Returns:
        ISO 8601 formatted date (YYYY-MM-DD) or "N/A" if parsing fails
    """
    if not date_str:
        return "N/A"

    try:
        # Remove "D:" prefix if present
        if date_str.startswith("D:"):
            date_str = date_str[2:]

        # Extract date components (YYYYMMDD)
        if len(date_str) >= 8:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]

            # Validate and format
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d")

        return "N/A"

    except (ValueError, IndexError):
        logger.debug(f"Could not parse date: {date_str}")
        return "N/A"

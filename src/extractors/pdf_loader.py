"""
PDF Loader Module for FastCheckAI

This module handles loading, validation, and type detection of PDF documents.
It provides robust error handling and clear error messages for common PDF issues.

Example:
    >>> from src.pdf_loader import load_pdf, detect_pdf_type
    >>> pdf_doc = load_pdf("data/inputs/document.pdf")
    >>> pdf_type = detect_pdf_type(pdf_doc)
    >>> print(f"PDF has {pdf_doc.page_count} pages, is_native: {pdf_type['is_native']}")
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pymupdf as fitz

from src.core.config import MAX_PDF_SIZE_MB

logger = logging.getLogger(__name__)


class PDFLoaderError(Exception):
    """Base exception for PDF loading errors."""

    pass


class PDFSizeError(PDFLoaderError):
    """PDF file exceeds maximum allowed size."""

    pass


class PDFCorruptedError(PDFLoaderError):
    """PDF file is corrupted or unreadable."""

    pass


def validate_pdf_size(path: Path, max_mb: int = MAX_PDF_SIZE_MB) -> float:
    """
    Validate that PDF file does not exceed maximum size.

    Args:
        path: Path to the PDF file
        max_mb: Maximum allowed size in megabytes (default from config)

    Returns:
        File size in megabytes (rounded to 1 decimal place)

    Raises:
        FileNotFoundError: If file does not exist
        PDFSizeError: If file exceeds maximum size

    Examples:
        >>> from pathlib import Path
        >>> size = validate_pdf_size(Path("document.pdf"), max_mb=25)
        >>> print(f"PDF size: {size}MB")
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Calculate file size in MB with 1 decimal place
    size_bytes = os.path.getsize(path)
    size_mb = round(size_bytes / (1024 * 1024), 1)

    logger.info(f"Validating PDF size: {path.name} ({size_mb}MB)")

    if size_mb > max_mb:
        error_msg = f"PDF exceeds {max_mb}MB: {path.name} ({size_mb}MB)"
        logger.error(error_msg)
        raise PDFSizeError(error_msg)

    return size_mb


def detect_pdf_type(
    pdf_doc: fitz.Document, char_threshold: int = 50
) -> Dict[str, Any]:
    """
    Detect if PDF is native (text-extractable) or scanned (requires OCR).

    Uses a heuristic: if first page has fewer than `char_threshold` extractable
    characters, the PDF is considered scanned.

    Args:
        pdf_doc: Opened PyMuPDF document
        char_threshold: Minimum characters to consider native (default: 50)

    Returns:
        Dictionary with:
            - is_native (bool): True if PDF has extractable text
            - requires_ocr (bool): True if PDF appears to be scanned
            - char_count (int): Number of characters found on first page

    Examples:
        >>> import pymupdf as fitz
        >>> doc = fitz.open("document.pdf")
        >>> pdf_type = detect_pdf_type(doc)
        >>> if pdf_type['requires_ocr']:
        ...     print("This PDF needs OCR processing")
        >>> doc.close()
    """
    if pdf_doc.page_count == 0:
        logger.warning("PDF has no pages")
        return {"is_native": False, "requires_ocr": True, "char_count": 0}

    # Extract text from first page
    first_page = pdf_doc[0]
    text = first_page.get_text()
    char_count = len(text.strip())

    # Determine PDF type based on character count
    is_native = char_count >= char_threshold
    requires_ocr = not is_native

    pdf_type = "Nativo (extração direta)" if is_native else "Escaneado (OCR necessário)"
    logger.info(f"PDF type detected: {pdf_type} ({char_count} characters on page 1)")

    return {
        "is_native": is_native,
        "requires_ocr": requires_ocr,
        "char_count": char_count,
    }


def load_pdf(path: str, validate_size: bool = True) -> fitz.Document:
    """
    Load PDF document with validation and robust error handling.

    This function:
    1. Resolves absolute/relative paths
    2. Validates file existence
    3. Validates file size (optional)
    4. Opens PDF with PyMuPDF
    5. Provides clear error messages for common issues

    Args:
        path: Path to PDF file (absolute or relative)
        validate_size: If True, validates file size before opening (default: True)

    Returns:
        Opened PyMuPDF Document object

    Raises:
        FileNotFoundError: If PDF file does not exist
        PDFSizeError: If PDF exceeds maximum size (when validate_size=True)
        PDFCorruptedError: If PDF is corrupted, password-protected, or invalid

    Examples:
        >>> pdf_doc = load_pdf("data/inputs/document.pdf")
        >>> print(f"Loaded PDF with {pdf_doc.page_count} pages")
        >>> pdf_doc.close()

        >>> # Load without size validation
        >>> large_pdf = load_pdf("large_document.pdf", validate_size=False)
        >>> large_pdf.close()
    """
    # 1. Resolve path (handles both absolute and relative paths)
    pdf_path = Path(path).resolve()

    # 2. Validate file exists
    if not pdf_path.exists():
        error_msg = f"PDF file not found: {pdf_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # 3. Validate file size (if enabled)
    if validate_size:
        try:
            file_size = validate_pdf_size(pdf_path)
        except PDFSizeError as e:
            # Re-raise with original exception
            raise e

    # 4. Attempt to open PDF with error handling
    try:
        pdf_doc = fitz.open(str(pdf_path))

        # 5. Log successful load
        logger.info(
            f"PDF carregado: {pdf_path.name} ({pdf_doc.page_count} páginas, "
            f"{file_size if validate_size else '?'}MB)"
        )

        return pdf_doc

    except RuntimeError as e:
        # Handle corrupted PDFs, password-protected PDFs, invalid format
        error_msg = (
            f"ERRO ao carregar PDF: {pdf_path.name} está corrompido, "
            f"protegido por senha, ou não é um PDF válido"
        )
        logger.error(f"{error_msg} | Details: {str(e)}")
        raise PDFCorruptedError(error_msg) from e

    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = f"Erro inesperado ao carregar PDF: {pdf_path.name}"
        logger.error(f"{error_msg} | Details: {str(e)}")
        raise PDFLoaderError(error_msg) from e

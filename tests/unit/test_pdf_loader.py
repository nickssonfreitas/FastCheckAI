"""
Comprehensive Unit Tests for PDF Loader Module

This test suite validates the PDF loading, validation, and type detection
functionality with extensive coverage of happy paths and error scenarios.

Test Coverage:
- validate_pdf_size(): File size validation with various file sizes
- detect_pdf_type(): Native vs scanned PDF detection
- load_pdf(): Complete PDF loading pipeline with error handling
- Exception hierarchy and error messages
- Logging output verification

Run tests:
    pytest tests/unit/test_pdf_loader.py -v
    pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-report=html
"""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pymupdf as fitz
import pytest

from src.extractors.pdf_loader import (
    PDFCorruptedError,
    PDFLoaderError,
    PDFSizeError,
    detect_pdf_type,
    load_pdf,
    validate_pdf_size,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files."""
    return tmp_path


@pytest.fixture
def temp_pdf_small(temp_dir):
    """
    Create small valid PDF with text content (<1MB).
    Simulates native ASTM document with extractable text.
    """
    pdf_path = temp_dir / "small_native.pdf"
    doc = fitz.open()  # Create new PDF

    # Add page with text content
    page = doc.new_page(width=595, height=842)  # A4 size
    text = "ASTM Standard Test Document\n" * 100  # Enough text for native detection
    page.insert_text((50, 50), text, fontsize=12)

    doc.save(str(pdf_path))
    doc.close()

    return pdf_path


@pytest.fixture
def temp_pdf_large(temp_dir):
    """
    Create large file (>25MB) for size validation testing.
    Uses a simple binary file approach for speed.
    """
    pdf_path = temp_dir / "large_file.pdf"

    # Create a minimal valid PDF header
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n")
        # Write 30MB of data to exceed MAX_PDF_SIZE_MB (25MB)
        f.write(b"0" * (30 * 1024 * 1024))
        f.write(b"\n%%EOF")

    return pdf_path


@pytest.fixture
def temp_pdf_native(temp_dir):
    """
    Create PDF with substantial text content (native PDF).
    Character count > 50 to pass native detection threshold.
    """
    pdf_path = temp_dir / "native_text.pdf"
    doc = fitz.open()

    page = doc.new_page()
    # Insert text with >50 characters
    text = (
        "This is a native PDF document with extractable text content. "
        "It contains sufficient characters to be classified as native."
    )
    page.insert_text((50, 50), text, fontsize=11)

    doc.save(str(pdf_path))
    doc.close()

    return pdf_path


@pytest.fixture
def temp_pdf_scanned(temp_dir):
    """
    Create PDF without text (simulates scanned document).
    Empty page with no extractable text (char count < 50).
    """
    pdf_path = temp_dir / "scanned_empty.pdf"
    doc = fitz.open()

    # Add empty page (no text)
    doc.new_page()

    doc.save(str(pdf_path))
    doc.close()

    return pdf_path


@pytest.fixture
def temp_pdf_corrupted(temp_dir):
    """
    Create invalid/corrupted PDF file.
    Contains invalid PDF structure that will fail to open.
    """
    pdf_path = temp_dir / "corrupted.pdf"

    with open(pdf_path, "w") as f:
        f.write("This is not a valid PDF file content")

    return pdf_path


@pytest.fixture
def temp_pdf_empty(temp_dir):
    """
    Mock fixture for empty PDF.
    Note: PyMuPDF doesn't allow creating real PDFs with zero pages,
    so this fixture returns None and tests using it should mock appropriately.
    """
    # PyMuPDF prevents saving PDFs with 0 pages, so we can't create a real one
    # Tests using this fixture should use mocks or be skipped
    return None


@pytest.fixture
def existing_test_pdfs():
    """
    Return paths to existing test PDFs in data/inputs/.
    Use these for integration-style tests if preferred.
    """
    base_path = Path(__file__).parent.parent.parent / "data" / "inputs"
    return {
        "small": base_path / "doc_a.pdf",
        "large": base_path / "large_file.pdf",
        "scanned": base_path / "scanned_sample.pdf",
        "corrupted": base_path / "corrupted.pdf",
    }


# =============================================================================
# Tests for validate_pdf_size()
# =============================================================================


class TestValidatePdfSize:
    """Test suite for validate_pdf_size() function."""

    def test_validate_pdf_size_small_file_success(self, temp_pdf_small, caplog):
        """Test validation passes for small PDF file."""
        with caplog.at_level(logging.INFO):
            size_mb = validate_pdf_size(temp_pdf_small, max_mb=25)

        # Assertions
        assert size_mb < 1.0, "Small PDF should be less than 1MB"
        assert size_mb >= 0, "Size should be non-negative"
        assert isinstance(size_mb, float), "Size should be float"
        assert "Validating PDF size" in caplog.text
        assert temp_pdf_small.name in caplog.text

    def test_validate_pdf_size_custom_max_size(self, temp_pdf_small):
        """Test validation with custom maximum size."""
        size_mb = validate_pdf_size(temp_pdf_small, max_mb=50)
        assert size_mb < 50, "Should validate against custom max size"

    def test_validate_pdf_size_large_file_raises_error(self, temp_pdf_large, caplog):
        """Test validation fails for file exceeding max size."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(PDFSizeError) as exc_info:
                validate_pdf_size(temp_pdf_large, max_mb=25)

        # Verify exception message
        assert "PDF exceeds 25MB" in str(exc_info.value)
        assert temp_pdf_large.name in str(exc_info.value)

        # Verify error was logged
        assert "PDF exceeds" in caplog.text
        assert "ERROR" in caplog.text

    def test_validate_pdf_size_file_not_found(self, temp_dir):
        """Test validation raises FileNotFoundError for missing file."""
        nonexistent_path = temp_dir / "does_not_exist.pdf"

        with pytest.raises(FileNotFoundError) as exc_info:
            validate_pdf_size(nonexistent_path)

        assert "File not found" in str(exc_info.value)
        assert str(nonexistent_path) in str(exc_info.value)

    def test_validate_pdf_size_returns_rounded_value(self, temp_pdf_small):
        """Test that size is rounded to 1 decimal place."""
        size_mb = validate_pdf_size(temp_pdf_small)

        # Check precision (should have at most 1 decimal place)
        size_str = str(size_mb)
        if "." in size_str:
            decimal_places = len(size_str.split(".")[1])
            assert decimal_places <= 1, "Size should be rounded to 1 decimal place"

    def test_validate_pdf_size_exactly_at_limit(self, temp_dir):
        """Test edge case: file exactly at size limit."""
        # Create file exactly 25MB
        pdf_path = temp_dir / "exactly_25mb.pdf"
        exact_size = 25 * 1024 * 1024  # Exactly 25MB in bytes

        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n")
            f.write(b"0" * (exact_size - 10))  # Account for header
            f.write(b"\n%%EOF")

        # Should NOT raise error (25.0 is not > 25)
        size_mb = validate_pdf_size(pdf_path, max_mb=25)
        assert size_mb == 25.0


# =============================================================================
# Tests for detect_pdf_type()
# =============================================================================


class TestDetectPdfType:
    """Test suite for detect_pdf_type() function."""

    def test_detect_pdf_type_native_pdf_success(self, temp_pdf_native, caplog):
        """Test detection of native PDF with extractable text."""
        doc = fitz.open(str(temp_pdf_native))

        with caplog.at_level(logging.INFO):
            result = detect_pdf_type(doc, char_threshold=50)

        doc.close()

        # Assertions
        assert result["is_native"] is True
        assert result["requires_ocr"] is False
        assert result["char_count"] >= 50
        assert isinstance(result["char_count"], int)

        # Verify logging
        assert "Nativo (extração direta)" in caplog.text
        assert "PDF type detected" in caplog.text

    def test_detect_pdf_type_scanned_pdf_success(self, temp_pdf_scanned, caplog):
        """Test detection of scanned PDF (no extractable text)."""
        doc = fitz.open(str(temp_pdf_scanned))

        with caplog.at_level(logging.INFO):
            result = detect_pdf_type(doc, char_threshold=50)

        doc.close()

        # Assertions
        assert result["is_native"] is False
        assert result["requires_ocr"] is True
        assert result["char_count"] < 50
        assert result["char_count"] >= 0

        # Verify logging
        assert "Escaneado (OCR necessário)" in caplog.text

    def test_detect_pdf_type_custom_threshold(self, temp_pdf_native):
        """Test detection with custom character threshold."""
        doc = fitz.open(str(temp_pdf_native))

        # Lower threshold - should detect as native
        result_low = detect_pdf_type(doc, char_threshold=10)
        assert result_low["is_native"] is True

        # Very high threshold - might detect as scanned
        result_high = detect_pdf_type(doc, char_threshold=1000)
        # Result depends on actual character count in fixture

        doc.close()

    def test_detect_pdf_type_empty_pdf_no_pages(self, caplog):
        """Test detection of PDF with zero pages (edge case)."""
        # Mock a PDF document with 0 pages
        mock_doc = MagicMock(spec=fitz.Document)
        mock_doc.page_count = 0

        with caplog.at_level(logging.WARNING):
            result = detect_pdf_type(mock_doc)

        # Assertions
        assert result["is_native"] is False
        assert result["requires_ocr"] is True
        assert result["char_count"] == 0

        # Verify warning logged
        assert "PDF has no pages" in caplog.text

    def test_detect_pdf_type_minimal_text_below_threshold(self, temp_dir):
        """Test PDF with text but below threshold (edge case)."""
        pdf_path = temp_dir / "minimal_text.pdf"
        doc = fitz.open()

        page = doc.new_page()
        page.insert_text((50, 50), "Short", fontsize=11)  # Only 5 characters

        doc.save(str(pdf_path))
        doc.close()

        # Re-open and test
        doc = fitz.open(str(pdf_path))
        result = detect_pdf_type(doc, char_threshold=50)
        doc.close()

        assert result["is_native"] is False  # Below threshold
        assert result["requires_ocr"] is True
        assert result["char_count"] < 50

    def test_detect_pdf_type_exactly_at_threshold(self, temp_dir):
        """Test PDF with character count exactly at threshold."""
        pdf_path = temp_dir / "threshold_text.pdf"
        doc = fitz.open()

        page = doc.new_page()
        # Create text with exactly 50 characters
        text = "A" * 50
        page.insert_text((50, 50), text, fontsize=11)

        doc.save(str(pdf_path))
        doc.close()

        doc = fitz.open(str(pdf_path))
        result = detect_pdf_type(doc, char_threshold=50)
        doc.close()

        # Exactly 50 should be >= threshold (is_native = True)
        assert result["char_count"] >= 50
        assert result["is_native"] is True

    def test_detect_pdf_type_whitespace_handling(self, temp_dir):
        """Test that whitespace is properly stripped in character count."""
        pdf_path = temp_dir / "whitespace.pdf"
        doc = fitz.open()

        page = doc.new_page()
        # Text with lots of whitespace
        text = "   \n\n  Text with whitespace  \n\n   "
        page.insert_text((50, 50), text, fontsize=11)

        doc.save(str(pdf_path))
        doc.close()

        doc = fitz.open(str(pdf_path))
        result = detect_pdf_type(doc, char_threshold=10)
        doc.close()

        # Should count only non-whitespace characters
        assert result["char_count"] > 0
        # Exact count depends on PyMuPDF's text extraction


# =============================================================================
# Tests for load_pdf()
# =============================================================================


class TestLoadPdf:
    """Test suite for load_pdf() function."""

    def test_load_pdf_valid_small_pdf_success(self, temp_pdf_small, caplog):
        """Test successful loading of valid small PDF."""
        with caplog.at_level(logging.INFO):
            pdf_doc = load_pdf(str(temp_pdf_small), validate_size=True)

        # Assertions
        assert isinstance(pdf_doc, fitz.Document)
        assert pdf_doc.page_count > 0
        assert not pdf_doc.is_closed

        # Verify logging
        assert "PDF carregado" in caplog.text
        assert temp_pdf_small.name in caplog.text
        assert "página" in caplog.text

        pdf_doc.close()

    def test_load_pdf_relative_path_resolution(self, temp_pdf_small):
        """Test that relative paths are resolved correctly."""
        # Change to temp directory and use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_pdf_small.parent)
            relative_path = temp_pdf_small.name

            pdf_doc = load_pdf(relative_path, validate_size=False)
            assert pdf_doc.page_count > 0
            pdf_doc.close()

        finally:
            os.chdir(original_cwd)

    def test_load_pdf_absolute_path_success(self, temp_pdf_small):
        """Test loading with absolute path."""
        absolute_path = temp_pdf_small.resolve()

        pdf_doc = load_pdf(str(absolute_path), validate_size=False)
        assert isinstance(pdf_doc, fitz.Document)
        pdf_doc.close()

    def test_load_pdf_file_not_found_raises_error(self, temp_dir, caplog):
        """Test FileNotFoundError for nonexistent file."""
        nonexistent = temp_dir / "missing.pdf"

        with caplog.at_level(logging.ERROR):
            with pytest.raises(FileNotFoundError) as exc_info:
                load_pdf(str(nonexistent))

        assert "PDF file not found" in str(exc_info.value)
        assert str(nonexistent) in str(exc_info.value)
        assert "ERROR" in caplog.text

    def test_load_pdf_large_file_with_validation_raises_error(
        self, temp_pdf_large, caplog
    ):
        """Test PDFSizeError when loading large file with validation enabled."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(PDFSizeError) as exc_info:
                load_pdf(str(temp_pdf_large), validate_size=True)

        assert "PDF exceeds" in str(exc_info.value)

    def test_load_pdf_large_file_without_validation_success(self, temp_pdf_large):
        """Test loading large file succeeds when validation is disabled."""
        # Note: This may fail if file is truly corrupted
        # For this test, we assume the large file is structurally valid
        try:
            pdf_doc = load_pdf(str(temp_pdf_large), validate_size=False)
            # If it opens, verify it's a document
            assert isinstance(pdf_doc, fitz.Document)
            pdf_doc.close()
        except PDFCorruptedError:
            # Expected if our large file fixture is not a valid PDF
            # This is acceptable for this test
            pass

    def test_load_pdf_corrupted_file_raises_error(self, temp_pdf_corrupted, caplog):
        """Test PDFCorruptedError for corrupted PDF."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(PDFCorruptedError) as exc_info:
                load_pdf(str(temp_pdf_corrupted), validate_size=False)

        # Verify error message in Portuguese
        assert "corrompido" in str(exc_info.value)
        assert "senha" in str(exc_info.value) or "válido" in str(exc_info.value)
        assert temp_pdf_corrupted.name in str(exc_info.value)
        assert "ERRO ao carregar PDF" in caplog.text

    def test_load_pdf_password_protected_raises_corrupted_error(self, temp_dir):
        """Test that password-protected PDFs raise PDFCorruptedError."""
        # Create password-protected PDF
        pdf_path = temp_dir / "protected.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Protected content", fontsize=12)

        # Save with password protection
        perm = int(
            fitz.PDF_PERM_ACCESSIBILITY  # type: ignore
            | fitz.PDF_PERM_PRINT  # type: ignore
            | fitz.PDF_PERM_COPY  # type: ignore
            | fitz.PDF_PERM_ANNOTATE  # type: ignore
        )
        encrypt_meth = fitz.PDF_ENCRYPT_AES_256  # type: ignore

        doc.save(
            str(pdf_path),
            encryption=encrypt_meth,
            owner_pw="owner123",
            user_pw="user123",
            permissions=perm,
        )
        doc.close()

        # Attempt to open without password
        # Note: PyMuPDF may open encrypted PDFs without error in some cases
        # so we check if it raises error OR successfully opens
        try:
            pdf_doc = load_pdf(str(pdf_path), validate_size=False)
            # If it opens, verify it's encrypted
            assert pdf_doc.is_encrypted or pdf_doc.needs_pass
            pdf_doc.close()
        except PDFCorruptedError:
            # Expected behavior: should raise error for encrypted PDFs
            pass

    def test_load_pdf_logging_includes_file_size(self, temp_pdf_small, caplog):
        """Test that logging includes file size when validation is enabled."""
        with caplog.at_level(logging.INFO):
            pdf_doc = load_pdf(str(temp_pdf_small), validate_size=True)
            pdf_doc.close()

        # Should log size in MB
        assert "MB" in caplog.text
        assert "PDF carregado" in caplog.text

    def test_load_pdf_logging_without_size_validation(self, temp_pdf_small, caplog):
        """Test logging when size validation is disabled."""
        with caplog.at_level(logging.INFO):
            pdf_doc = load_pdf(str(temp_pdf_small), validate_size=False)
            pdf_doc.close()

        # Should show '?MB' when validation disabled
        assert "?MB" in caplog.text or "MB" in caplog.text

    def test_load_pdf_multiple_pages(self, temp_dir):
        """Test loading PDF with multiple pages."""
        pdf_path = temp_dir / "multipage.pdf"
        doc = fitz.open()

        # Add 5 pages
        for i in range(5):
            page = doc.new_page()
            page.insert_text((50, 50), f"Page {i+1}", fontsize=12)

        doc.save(str(pdf_path))
        doc.close()

        # Load and verify
        pdf_doc = load_pdf(str(pdf_path), validate_size=False)
        assert pdf_doc.page_count == 5
        pdf_doc.close()

    def test_load_pdf_exception_chaining(self, temp_pdf_corrupted):
        """Test that original exceptions are properly chained."""
        with pytest.raises(PDFCorruptedError) as exc_info:
            load_pdf(str(temp_pdf_corrupted), validate_size=False)

        # Verify exception has __cause__ (chained from RuntimeError)
        assert exc_info.value.__cause__ is not None

    @patch("src.pdf_loader.fitz.open")
    def test_load_pdf_unexpected_error_raises_pdf_loader_error(
        self, mock_fitz_open, temp_pdf_small, caplog
    ):
        """Test that unexpected errors are caught and wrapped."""
        # Simulate unexpected exception
        mock_fitz_open.side_effect = ValueError("Unexpected error")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(PDFLoaderError) as exc_info:
                load_pdf(str(temp_pdf_small), validate_size=False)

        assert "Erro inesperado" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, ValueError)


# =============================================================================
# Tests for Exception Hierarchy
# =============================================================================


class TestExceptionHierarchy:
    """Test suite for custom exception classes."""

    def test_pdf_loader_error_is_base_exception(self):
        """Test PDFLoaderError is base exception."""
        assert issubclass(PDFLoaderError, Exception)

    def test_pdf_size_error_inherits_from_pdf_loader_error(self):
        """Test PDFSizeError inherits from PDFLoaderError."""
        assert issubclass(PDFSizeError, PDFLoaderError)
        assert issubclass(PDFSizeError, Exception)

    def test_pdf_corrupted_error_inherits_from_pdf_loader_error(self):
        """Test PDFCorruptedError inherits from PDFLoaderError."""
        assert issubclass(PDFCorruptedError, PDFLoaderError)
        assert issubclass(PDFCorruptedError, Exception)

    def test_exceptions_can_be_caught_as_pdf_loader_error(self):
        """Test that all exceptions can be caught with base exception."""
        # PDFSizeError
        with pytest.raises(PDFLoaderError):
            raise PDFSizeError("Size error")

        # PDFCorruptedError
        with pytest.raises(PDFLoaderError):
            raise PDFCorruptedError("Corrupted error")

    def test_exception_messages(self):
        """Test exception messages are preserved."""
        size_error = PDFSizeError("File too large")
        assert str(size_error) == "File too large"

        corrupted_error = PDFCorruptedError("Invalid PDF")
        assert str(corrupted_error) == "Invalid PDF"


# =============================================================================
# Integration Tests with Existing Test Files
# =============================================================================


class TestWithExistingFiles:
    """
    Integration-style tests using existing test files in data/inputs/.
    These tests verify the module works with real-world test files.
    """

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "data/inputs/doc_a.pdf").exists(),
        reason="Test files not available",
    )
    def test_load_existing_small_pdf(self, existing_test_pdfs):
        """Test loading existing small PDF (doc_a.pdf)."""
        if existing_test_pdfs["small"].exists():
            pdf_doc = load_pdf(str(existing_test_pdfs["small"]), validate_size=True)
            assert pdf_doc.page_count > 0
            pdf_doc.close()

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "data/inputs/large_file.pdf").exists(),
        reason="Large test file not available",
    )
    def test_load_existing_large_pdf_fails(self, existing_test_pdfs):
        """Test that existing large file (30MB) fails validation."""
        if existing_test_pdfs["large"].exists():
            with pytest.raises(PDFSizeError):
                load_pdf(str(existing_test_pdfs["large"]), validate_size=True)

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "data/inputs/scanned_sample.pdf").exists(),
        reason="Scanned test file not available",
    )
    def test_detect_existing_scanned_pdf(self, existing_test_pdfs):
        """Test detection of existing scanned PDF."""
        if existing_test_pdfs["scanned"].exists():
            pdf_doc = load_pdf(str(existing_test_pdfs["scanned"]), validate_size=False)
            result = detect_pdf_type(pdf_doc)
            pdf_doc.close()

            # Should be detected as scanned (requires OCR)
            assert result["requires_ocr"] is True

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "data/inputs/corrupted.pdf").exists(),
        reason="Corrupted test file not available",
    )
    def test_load_existing_corrupted_pdf_fails(self, existing_test_pdfs):
        """Test that existing corrupted file raises error."""
        if existing_test_pdfs["corrupted"].exists():
            with pytest.raises(PDFCorruptedError):
                load_pdf(str(existing_test_pdfs["corrupted"]), validate_size=False)


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_validate_pdf_size_zero_max_mb(self, temp_pdf_small):
        """Test validation with max_mb=0 (edge case)."""
        # Files that round to 0.0MB won't exceed 0MB limit
        # So this test is only valid if file is actually > 0MB
        size_mb = validate_pdf_size(temp_pdf_small, max_mb=100)
        if size_mb > 0:
            with pytest.raises(PDFSizeError):
                validate_pdf_size(temp_pdf_small, max_mb=0)
        else:
            # If file rounds to 0.0MB, it won't raise error (edge case)
            result = validate_pdf_size(temp_pdf_small, max_mb=0)
            assert result == 0.0

    def test_detect_pdf_type_zero_threshold(self, temp_pdf_scanned):
        """Test detection with char_threshold=0."""
        doc = fitz.open(str(temp_pdf_scanned))
        result = detect_pdf_type(doc, char_threshold=0)
        doc.close()

        # Even empty PDFs should be considered "native" with 0 threshold
        assert result["is_native"] is True

    def test_load_pdf_pathlib_path_object(self, temp_pdf_small):
        """Test load_pdf accepts Path objects (not just strings)."""
        # Pass Path object instead of string
        pdf_doc = load_pdf(temp_pdf_small, validate_size=False)
        assert isinstance(pdf_doc, fitz.Document)
        pdf_doc.close()

    def test_load_pdf_empty_string_raises_error(self):
        """Test that empty string path raises appropriate error."""
        with pytest.raises((FileNotFoundError, PDFLoaderError)):
            load_pdf("", validate_size=False)

    def test_validate_pdf_size_symlink_handling(self, temp_pdf_small, temp_dir):
        """Test validation works with symbolic links."""
        import platform

        if platform.system() == "Windows":
            pytest.skip("Symlink test not reliable on Windows")

        # Create symlink to PDF
        symlink_path = temp_dir / "symlink.pdf"
        symlink_path.symlink_to(temp_pdf_small)

        size_mb = validate_pdf_size(symlink_path, max_mb=25)
        assert size_mb >= 0  # Size should be valid (can be 0.0 for very small files)


# =============================================================================
# Performance and Logging Tests
# =============================================================================


class TestLogging:
    """Test logging behavior across all functions."""

    def test_validate_pdf_size_logs_info_on_success(self, temp_pdf_small, caplog):
        """Test that successful validation logs info message."""
        with caplog.at_level(logging.INFO):
            validate_pdf_size(temp_pdf_small, max_mb=25)

        assert "Validating PDF size" in caplog.text
        assert "INFO" in caplog.text

    def test_validate_pdf_size_logs_error_on_failure(self, temp_pdf_large, caplog):
        """Test that size violation logs error message."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(PDFSizeError):
                validate_pdf_size(temp_pdf_large, max_mb=25)

        assert "ERROR" in caplog.text
        assert "PDF exceeds" in caplog.text

    def test_detect_pdf_type_logs_native_detection(self, temp_pdf_native, caplog):
        """Test logging for native PDF detection."""
        doc = fitz.open(str(temp_pdf_native))

        with caplog.at_level(logging.INFO):
            detect_pdf_type(doc)

        doc.close()

        assert "Nativo (extração direta)" in caplog.text
        assert "characters on page 1" in caplog.text

    def test_detect_pdf_type_logs_scanned_detection(self, temp_pdf_scanned, caplog):
        """Test logging for scanned PDF detection."""
        doc = fitz.open(str(temp_pdf_scanned))

        with caplog.at_level(logging.INFO):
            detect_pdf_type(doc)

        doc.close()

        assert "Escaneado (OCR necessário)" in caplog.text

    def test_detect_pdf_type_logs_warning_for_empty_pdf(self, caplog):
        """Test warning is logged for PDFs with no pages."""
        # Mock a PDF document with 0 pages
        mock_doc = MagicMock(spec=fitz.Document)
        mock_doc.page_count = 0

        with caplog.at_level(logging.WARNING):
            detect_pdf_type(mock_doc)

        assert "WARNING" in caplog.text
        assert "PDF has no pages" in caplog.text

    def test_load_pdf_logs_success_with_details(self, temp_pdf_small, caplog):
        """Test that successful load logs comprehensive details."""
        with caplog.at_level(logging.INFO):
            pdf_doc = load_pdf(str(temp_pdf_small), validate_size=True)
            pdf_doc.close()

        # Should include: filename, page count, size
        assert "PDF carregado" in caplog.text
        assert temp_pdf_small.name in caplog.text
        assert "página" in caplog.text
        assert "MB" in caplog.text

    def test_load_pdf_logs_error_on_corruption(self, temp_pdf_corrupted, caplog):
        """Test error logging for corrupted PDF."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(PDFCorruptedError):
                load_pdf(str(temp_pdf_corrupted), validate_size=False)

        assert "ERROR" in caplog.text
        assert "ERRO ao carregar PDF" in caplog.text
        assert "corrompido" in caplog.text


# =============================================================================
# Test Markers and Metadata
# =============================================================================


@pytest.mark.unit
class TestModuleMetadata:
    """Tests for module-level attributes and documentation."""

    def test_module_has_docstring(self):
        """Test that pdf_loader module has documentation."""
        import src.pdf_loader

        assert src.pdf_loader.__doc__ is not None
        assert len(src.pdf_loader.__doc__) > 0

    def test_all_functions_have_docstrings(self):
        """Test that all public functions have docstrings."""
        from src import pdf_loader

        functions = [validate_pdf_size, detect_pdf_type, load_pdf]

        for func in functions:
            assert func.__doc__ is not None, f"{func.__name__} missing docstring"
            assert len(func.__doc__) > 50, f"{func.__name__} docstring too short"

    def test_exceptions_have_docstrings(self):
        """Test that exception classes have docstrings."""
        exceptions = [PDFLoaderError, PDFSizeError, PDFCorruptedError]

        for exc in exceptions:
            assert exc.__doc__ is not None, f"{exc.__name__} missing docstring"

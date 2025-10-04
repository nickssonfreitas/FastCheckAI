"""Extractors module - PDF loading and content extraction."""

from src.extractors.pdf_loader import load_pdf, validate_pdf_size
from src.extractors.table_extractor import detect_table_pages, extract_tables
from src.extractors.text_extractor import (
    extract_text,
    is_text_corrupted,
    parse_section_hierarchy,
)

__all__ = [
    "load_pdf",
    "validate_pdf_size",
    "extract_text",
    "parse_section_hierarchy",
    "is_text_corrupted",
    "extract_tables",
    "detect_table_pages",
]

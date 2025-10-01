#!/usr/bin/env python3
"""
Test script to inspect PyMuPDF metadata extraction from ASTM PDFs.
"""
import pymupdf as fitz

def inspect_pdf_metadata(pdf_path):
    """Inspect all metadata from a PDF file."""
    print('='*60)
    print(f'PDF: {pdf_path}')
    print('='*60)

    pdf_doc = fitz.open(pdf_path)

    # Basic info
    print(f"Page count: {pdf_doc.page_count}")

    # Check for pdf_version attribute
    print(f"\nHas pdf_version attribute? {hasattr(pdf_doc, 'pdf_version')}")
    if hasattr(pdf_doc, 'pdf_version'):
        print(f"  pdf_doc.pdf_version: {pdf_doc.pdf_version}")

    # Check for version attribute
    if hasattr(pdf_doc, 'version'):
        print(f"Has version attribute? True")
        print(f"  pdf_doc.version: {pdf_doc.version}")
    else:
        print(f"Has version attribute? False")

    # Raw metadata
    print(f"\nMetadata keys: {list(pdf_doc.metadata.keys())}")
    print(f"\nMetadata raw:")
    for key, value in pdf_doc.metadata.items():
        print(f"  {key}: {repr(value)}")

    # Test case sensitivity
    print(f"\nCase sensitivity test:")
    test_keys = ['title', 'Title', 'TITLE', 'author', 'Author', 'creator', 'Creator', 'format']
    for key in test_keys:
        value = pdf_doc.metadata.get(key, 'KEY_NOT_FOUND')
        if value != 'KEY_NOT_FOUND':
            print(f"  metadata.get('{key}'): {repr(value)}")

    # Test empty vs missing
    print(f"\nEmpty string behavior:")
    test_value = pdf_doc.metadata.get('title', 'N/A')
    print(f"  Original: {repr(test_value)}")
    print(f"  After .strip(): {repr(test_value.strip())}")
    print(f"  After .strip() or 'N/A': {repr(test_value.strip() or 'N/A')}")

    pdf_doc.close()
    print()

if __name__ == "__main__":
    # Test both PDFs
    inspect_pdf_metadata("data/ASTM_A29_A29M_Rev.00'2015.pdf")
    inspect_pdf_metadata("data/ASTM_A29_A29M_Rev.00'2016.pdf")

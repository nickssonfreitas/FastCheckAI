#!/usr/bin/env python3
"""
Quick test script to verify extraction fixes without full OCR.

Tests:
1. Bug #1 fix: Metadata format field
2. Corruption detection function
3. Hybrid extraction (will warn about missing Tesseract)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_loader import load_pdf
from src.text_extractor import extract_metadata, extract_text, is_text_corrupted

def test_metadata_fix():
    """Test that metadata format field is correctly extracted."""
    print("=" * 60)
    print("TEST 1: Metadata Format Field Fix")
    print("=" * 60)

    pdf_path = "data/ASTM_A29_A29M_Rev.00'2015.pdf"
    print(f"Loading: {pdf_path}")

    pdf_doc = load_pdf(pdf_path)
    metadata = extract_metadata(pdf_doc)

    print(f"\nMetadata extracted:")
    print(f"  - Format: {metadata['format']}")
    print(f"  - Title: {metadata['title']}")
    print(f"  - Pages: {metadata['page_count']}")

    if metadata['format'] != "PDF N/A":
        print("\n✓ Bug #1 FIXED: Format field working correctly")
    else:
        print("\n✗ Bug #1 NOT FIXED: Still returning 'PDF N/A'")

    pdf_doc.close()
    return metadata['format'] != "PDF N/A"


def test_corruption_detection():
    """Test corruption detection function."""
    print("\n" + "=" * 60)
    print("TEST 2: Corruption Detection")
    print("=" * 60)

    # Normal ASCII text (should NOT be corrupted)
    text_good = "Designation: A29/A29M Standard Specification"
    corrupted_good = is_text_corrupted(text_good)
    print(f"\nNormal text: '{text_good[:50]}'")
    print(f"  Corrupted: {corrupted_good}")

    # Corrupted Unicode text (SHOULD be corrupted)
    text_bad = "Ü»­·¹²¿¬·±²æ ßîçñßîçÓ ͬ¿²¼¿®¼"
    corrupted_bad = is_text_corrupted(text_bad)
    print(f"\nCorrupted text: '{text_bad[:50]}'")
    print(f"  Corrupted: {corrupted_bad}")

    if not corrupted_good and corrupted_bad:
        print("\n✓ Corruption detection WORKING correctly")
        return True
    else:
        print("\n✗ Corruption detection NOT working")
        return False


def test_hybrid_extraction():
    """Test hybrid extraction (will fail without Tesseract but should detect corruption)."""
    print("\n" + "=" * 60)
    print("TEST 3: Hybrid Extraction (Corruption Detection)")
    print("=" * 60)

    pdf_path = "data/ASTM_A29_A29M_Rev.00'2015.pdf"
    print(f"Loading: {pdf_path}")

    pdf_doc = load_pdf(pdf_path)

    print("\nExtracting text with OCR disabled (fast mode)...")
    text_no_ocr = extract_text(pdf_doc, enable_ocr=False)

    # Check page 2 text for corruption
    lines = text_no_ocr.split('\n')
    page_2_start = None
    for i, line in enumerate(lines):
        if '--- PAGE 2 ---' in line:
            page_2_start = i
            break

    if page_2_start:
        page_2_text = '\n'.join(lines[page_2_start:page_2_start+10])
        print(f"\nPage 2 sample (first 10 lines):")
        print(page_2_text[:200])

        is_corrupted = is_text_corrupted(page_2_text)
        print(f"\nPage 2 corruption detected: {is_corrupted}")

        if is_corrupted:
            print("\n✓ Corruption correctly detected on page 2")
            print("⚠ OCR fallback would activate here (requires Tesseract)")
            return True
        else:
            print("\n? Page 2 appears clean (unexpected)")
            return False
    else:
        print("\n✗ Could not find page 2 marker")
        return False

    pdf_doc.close()


if __name__ == "__main__":
    print("FastCheckAI - Extraction Fixes Test Suite")
    print("=" * 60)

    results = []

    try:
        results.append(("Metadata Fix", test_metadata_fix()))
    except Exception as e:
        print(f"\n✗ Metadata test FAILED: {e}")
        results.append(("Metadata Fix", False))

    try:
        results.append(("Corruption Detection", test_corruption_detection()))
    except Exception as e:
        print(f"\n✗ Corruption detection FAILED: {e}")
        results.append(("Corruption Detection", False))

    try:
        results.append(("Hybrid Extraction", test_hybrid_extraction()))
    except Exception as e:
        print(f"\n✗ Hybrid extraction test FAILED: {e}")
        results.append(("Hybrid Extraction", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. To enable OCR fallback, install Tesseract OCR:")
    print("   sudo apt-get update")
    print("   sudo apt-get install tesseract-ocr tesseract-ocr-eng")
    print("\n2. After Tesseract is installed, re-test with:")
    print("   python scripts/test_extraction_fix.py")

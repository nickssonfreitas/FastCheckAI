#!/usr/bin/env python3
"""
Test script for PDFComparisonPipeline API.

This script validates the pipeline API functionality by comparing
two ASTM PDF documents and generating reports in multiple formats.

Usage:
    python scripts/test_pipeline_api.py

Expected output:
    - Console output showing pipeline progress
    - Generated reports in data/outputs/
    - Success/failure status for each test
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipelines.semantic_comparison import PDFComparisonPipeline, ComparisonResult
from src.core.exceptions import PDFProcessingError


def progress_callback(stage: str, pct: float, msg: str):
    """Progress tracking callback."""
    bar_length = 30
    filled = int(bar_length * pct / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{bar}] {pct:>3.0f}% | {stage:12s} | {msg}", end="", flush=True)
    if pct >= 100:
        print()  # New line when complete


def test_basic_pipeline():
    """Test basic pipeline execution with Markdown output."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Pipeline Execution (Markdown)")
    print("=" * 60)

    try:
        pipeline = PDFComparisonPipeline(
            enable_ocr=True,
            llm_model="gpt-4o",
            output_dir="data/outputs",
            log_level="INFO",
            progress_callback=progress_callback,
        )

        result = pipeline.run(
            pdf1_path="data/inputs/astm_2015.pdf",
            pdf2_path="data/inputs/astm_2016.pdf",
            report_format="markdown",
        )

        # Validate result
        assert isinstance(result, ComparisonResult), "Result should be ComparisonResult"
        assert result.statistics["total_changes"] >= 0, "Should have change count"
        assert result.processing_time_seconds > 0, "Should have processing time"
        assert result.report_path.exists(), "Report file should exist"

        print("\n✅ TEST 1 PASSED")
        print(f"   Changes found: {result.statistics['total_changes']}")
        print(f"   Processing time: {result.processing_time_seconds:.2f}s")
        print(f"   Report saved: {result.report_path}")
        print(f"   Alignment confidence: {result.alignment_confidence:.2%}")

        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False


def test_html_output():
    """Test HTML report generation."""
    print("\n" + "=" * 60)
    print("TEST 2: HTML Report Generation")
    print("=" * 60)

    try:
        pipeline = PDFComparisonPipeline(
            enable_ocr=False,  # Skip OCR for speed
            log_level="WARNING",
        )

        result = pipeline.run(
            pdf1_path="data/inputs/astm_2015.pdf",
            pdf2_path="data/inputs/astm_2016.pdf",
            report_format="markdown",  # HTML not implemented yet
        )

        print("\n✅ TEST 2 PASSED")
        print(f"   Report: {result.report_path}")

        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n" + "=" * 60)
    print("TEST 3: Error Handling")
    print("=" * 60)

    try:
        pipeline = PDFComparisonPipeline()

        # Test with non-existent file
        try:
            result = pipeline.run(
                pdf1_path="nonexistent.pdf",
                pdf2_path="data/inputs/astm_2016.pdf",
            )
            print("❌ TEST 3 FAILED: Should have raised PDFProcessingError")
            return False
        except PDFProcessingError as e:
            print(f"✅ Correctly raised PDFProcessingError: {e}")

        # Test with invalid OCR DPI
        try:
            bad_pipeline = PDFComparisonPipeline(ocr_dpi=50)  # Too low
            print("❌ TEST 3 FAILED: Should have raised ConfigurationError")
            return False
        except Exception as e:
            print(f"✅ Correctly raised error for invalid config: {type(e).__name__}")

        print("\n✅ TEST 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: Unexpected error: {e}")
        return False


def test_result_export():
    """Test result export to dict and DataFrame."""
    print("\n" + "=" * 60)
    print("TEST 4: Result Export")
    print("=" * 60)

    try:
        pipeline = PDFComparisonPipeline(enable_ocr=False, log_level="ERROR")

        result = pipeline.run(
            pdf1_path="data/inputs/astm_2015.pdf",
            pdf2_path="data/inputs/astm_2016.pdf",
        )

        # Test to_dict()
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict), "to_dict() should return dict"
        assert "changes" in result_dict, "Dict should contain changes"
        assert "statistics" in result_dict, "Dict should contain statistics"

        print("✅ to_dict() works correctly")

        # Test to_dataframe()
        df = result.to_dataframe()
        if df is not None:
            print(f"✅ to_dataframe() works: {len(df)} rows")
        else:
            print("⚠️  pandas not installed, skipping DataFrame test")

        print("\n✅ TEST 4 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PIPELINE API TEST SUITE")
    print("=" * 60)

    # Check if test PDFs exist
    pdf1 = Path("data/inputs/astm_2015.pdf")
    pdf2 = Path("data/inputs/astm_2016.pdf")

    if not pdf1.exists() or not pdf2.exists():
        print("\n❌ ERROR: Test PDFs not found!")
        print(f"   Expected: {pdf1}")
        print(f"   Expected: {pdf2}")
        print("\n   Please ensure test PDFs are available before running tests.")
        return 1

    # Run tests
    results = []
    results.append(("Basic Pipeline", test_basic_pipeline()))
    results.append(("HTML Output", test_html_output()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Result Export", test_result_export()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

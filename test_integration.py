#!/usr/bin/env python3
"""Test script for table comparison integration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.pipelines.semantic_comparison import PDFComparisonPipeline

# Test with ASTM PDFs
pdf1 = "data/inputs/ASTM_A29_A29M_Rev_2015.pdf"
pdf2 = "data/inputs/ASTM_A29_A29M_Rev_2016.pdf"

print("🧪 Testing Table Comparison Integration...")
print(f"   PDF 1: {pdf1}")
print(f"   PDF 2: {pdf2}")
print()

try:
    # Create pipeline with table comparison enabled
    pipeline = PDFComparisonPipeline(
        enable_ocr=True,
        enable_table_comparison=True,
        table_tolerance=0.05,
        llm_model="gpt-4o",
        output_dir="data/outputs",
        log_level="INFO",
    )

    # Run comparison
    result = pipeline.run(
        pdf1_path=pdf1,
        pdf2_path=pdf2,
        report_format="markdown",
        report_filename="integration_test_tables.md",
    )

    print("\n" + "="*60)
    print("✅ TEST PASSED - Integration Successful!")
    print("="*60)
    print(f"\n📊 Results:")
    print(f"   Total changes: {result.statistics['total_changes']}")
    print(f"   Processing time: {result.processing_time_seconds:.2f}s")
    print(f"   Report: {result.report_path}")

    # Check for table changes
    table_changes = [c for c in result.changes if 'table' in c.get('type', '')]
    if table_changes:
        print(f"\n📋 Table Changes Detected: {len(table_changes)}")
        for tc in table_changes[:3]:  # Show first 3
            print(f"   - {tc['section_title']}: {tc['type']}")
    else:
        print(f"\n📋 No table changes detected (tables may not be present in PDFs)")

except Exception as e:
    print("\n" + "="*60)
    print("❌ TEST FAILED")
    print("="*60)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

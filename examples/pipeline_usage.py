#!/usr/bin/env python3
"""
Pipeline API Usage Examples

This file demonstrates common usage patterns for the PDFComparisonPipeline API.
"""

import sys
from pathlib import Path

# Add project root to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import PDFComparisonPipeline


# =============================================================================
# Example 1: Basic Usage
# =============================================================================


def example_basic():
    """
    Simplest possible usage - compare two PDFs and generate Markdown report.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)

    # Create pipeline with default settings
    pipeline = PDFComparisonPipeline()

    # Run comparison
    result = pipeline.run(
        pdf1_path="data/inputs/astm_2015.pdf",
        pdf2_path="data/inputs/astm_2016.pdf",
    )

    # Display results
    print(f"\n✅ Comparison complete!")
    print(f"   Changes found: {result.statistics['total_changes']}")
    print(f"   Critical changes: {result.statistics['severity_breakdown'].get('CRITICAL', 0)}")
    print(f"   Processing time: {result.processing_time_seconds:.2f}s")
    print(f"   Report saved to: {result.report_path}")


# =============================================================================
# Example 2: Custom Configuration
# =============================================================================


def example_custom_config():
    """
    Configure pipeline for specific use cases.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Configuration")
    print("=" * 60)

    # High-accuracy mode (slower but more thorough)
    pipeline_accurate = PDFComparisonPipeline(
        enable_ocr=True,
        ocr_dpi=600,  # High quality OCR
        llm_model="gpt-4o",  # Best semantic analysis
        fuzzy_match_threshold=0.9,  # Stricter alignment
        output_dir="outputs/high_accuracy/",
    )

    # Fast mode (for testing or draft comparisons)
    pipeline_fast = PDFComparisonPipeline(
        enable_ocr=False,  # Skip OCR
        llm_model="gpt-4o-mini",  # Faster, cheaper model
        use_llm_alignment=False,  # Heuristic alignment only
        output_dir="outputs/fast_mode/",
    )

    print("✅ Created two pipelines with different configs:")
    print("   - pipeline_accurate: High quality, slower")
    print("   - pipeline_fast: Quick results, lower accuracy")


# =============================================================================
# Example 3: Progress Tracking
# =============================================================================


def example_progress_tracking():
    """
    Track pipeline progress with custom callback.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Progress Tracking")
    print("=" * 60)

    def my_progress_handler(stage: str, progress: float, message: str):
        """Custom progress callback."""
        # Simple progress bar
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r[{bar}] {progress:>3.0f}% | {stage:12s} | {message[:40]}", end="")
        if progress >= 100:
            print()  # New line when done

    pipeline = PDFComparisonPipeline(
        progress_callback=my_progress_handler,
        log_level="WARNING",  # Reduce console clutter
    )

    print("\nRunning pipeline with progress tracking...\n")
    result = pipeline.run(
        pdf1_path="data/inputs/astm_2015.pdf",
        pdf2_path="data/inputs/astm_2016.pdf",
    )

    print(f"\n✅ Complete! Found {result.statistics['total_changes']} changes")


# =============================================================================
# Example 4: Error Handling
# =============================================================================


def example_error_handling():
    """
    Robust error handling for production use.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Error Handling")
    print("=" * 60)

    from src.pipeline import PDFProcessingError, AlignmentError, LLMError

    pipeline = PDFComparisonPipeline()

    try:
        result = pipeline.run(
            pdf1_path="data/inputs/astm_2015.pdf",
            pdf2_path="data/inputs/astm_2016.pdf",
        )
        print(f"✅ Success! Report: {result.report_path}")

    except PDFProcessingError as e:
        print(f"❌ PDF processing failed: {e}")
        # Handle PDF-specific errors (e.g., corrupted file, missing pages)

    except AlignmentError as e:
        print(f"⚠️  Section alignment confidence too low: {e}")
        # Maybe try again with different settings or manual review

    except LLMError as e:
        print(f"⚠️  LLM semantic analysis failed: {e}")
        # Fallback to basic text comparison without semantic analysis

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        # Log error and notify admin


# =============================================================================
# Example 5: Working with Results
# =============================================================================


def example_result_analysis():
    """
    Analyze and export comparison results.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Result Analysis")
    print("=" * 60)

    pipeline = PDFComparisonPipeline(log_level="ERROR")  # Quiet mode

    result = pipeline.run(
        pdf1_path="data/inputs/astm_2015.pdf",
        pdf2_path="data/inputs/astm_2016.pdf",
    )

    # 1. Access statistics
    print("\n📊 Statistics:")
    print(f"   Total changes: {result.statistics['total_changes']}")
    print(f"   Additions: {result.statistics['additions']}")
    print(f"   Deletions: {result.statistics['deletions']}")
    print(f"   Modifications: {result.statistics['modifications']}")

    # 2. Severity breakdown
    print("\n⚠️  Severity breakdown:")
    for severity, count in result.statistics["severity_breakdown"].items():
        print(f"   {severity}: {count}")

    # 3. Export to dict (for JSON)
    result_dict = result.to_dict()
    print(f"\n📝 Exported to dict: {len(result_dict)} keys")

    # 4. Convert to DataFrame (if pandas installed)
    df = result.to_dataframe()
    if df is not None:
        print(f"\n📊 DataFrame created: {len(df)} rows x {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns[:5])}...")

        # Example: Filter critical changes
        critical = df[df["severity"] == "CRITICAL"]
        print(f"   Critical changes: {len(critical)}")
    else:
        print("\n⚠️  pandas not installed (DataFrame export unavailable)")

    # 5. Access individual changes
    print(f"\n🔍 First 3 changes:")
    for idx, change in enumerate(result.changes[:3], 1):
        print(f"\n   {idx}. Section: {change['section_id']}")
        print(f"      Type: {change['type']}")
        print(f"      Severity: {change['severity']}")


# =============================================================================
# Example 6: Batch Processing
# =============================================================================


def example_batch_processing():
    """
    Process multiple PDF pairs in sequence.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Batch Processing")
    print("=" * 60)

    # Define PDF pairs to compare
    pdf_pairs = [
        ("data/inputs/astm_2015.pdf", "data/inputs/astm_2016.pdf", "2015_vs_2016"),
        # Add more pairs as needed
    ]

    pipeline = PDFComparisonPipeline(
        output_dir="outputs/batch/",
        log_level="WARNING",
    )

    results = []
    for pdf1, pdf2, name in pdf_pairs:
        print(f"\nProcessing: {name}...")

        try:
            result = pipeline.run(
                pdf1_path=pdf1,
                pdf2_path=pdf2,
                report_filename=f"{name}_report.md",
            )
            results.append((name, result))
            print(f"✅ {name}: {result.statistics['total_changes']} changes")

        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append((name, None))

    # Summary
    print(f"\n📊 Batch processing complete:")
    print(f"   Successful: {sum(1 for _, r in results if r is not None)}/{len(pdf_pairs)}")


# =============================================================================
# Example 7: Integration with Other Systems
# =============================================================================


def example_integration():
    """
    Example integration patterns for automation systems.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Integration Patterns")
    print("=" * 60)

    # Pattern 1: Airflow task
    def airflow_task_example():
        """Example Airflow task function."""
        pipeline = PDFComparisonPipeline(output_dir="/mnt/airflow/outputs/")

        result = pipeline.run(
            pdf1_path="/mnt/data/standards/baseline.pdf",
            pdf2_path="/mnt/data/standards/latest.pdf",
        )

        # Return XCom data for downstream tasks
        return {
            "total_changes": result.statistics["total_changes"],
            "critical_count": result.statistics["severity_breakdown"].get("CRITICAL", 0),
            "report_path": str(result.report_path),
        }

    # Pattern 2: API endpoint (FastAPI example)
    def fastapi_endpoint_example():
        """Example FastAPI endpoint."""
        from fastapi import UploadFile

        async def compare_pdfs(pdf1: UploadFile, pdf2: UploadFile):
            # Save uploaded files temporarily
            pdf1_path = f"/tmp/{pdf1.filename}"
            pdf2_path = f"/tmp/{pdf2.filename}"

            # Run comparison
            pipeline = PDFComparisonPipeline()
            result = pipeline.run(pdf1_path, pdf2_path)

            # Return JSON response
            return result.to_dict()

    # Pattern 3: Command-line script
    def cli_script_example():
        """Example CLI script."""
        import argparse

        parser = argparse.ArgumentParser(description="Compare two PDF documents")
        parser.add_argument("pdf1", help="Path to first PDF")
        parser.add_argument("pdf2", help="Path to second PDF")
        parser.add_argument("--format", choices=["markdown", "html", "json"], default="markdown")
        parser.add_argument("--output", help="Output directory")

        args = parser.parse_args()

        pipeline = PDFComparisonPipeline(output_dir=args.output or "outputs/")
        result = pipeline.run(args.pdf1, args.pdf2, report_format=args.format)

        print(f"Report saved to: {result.report_path}")

    print("✅ Integration examples defined (see source code for details)")


# =============================================================================
# Main - Run All Examples
# =============================================================================


def main():
    """Run all examples (or select specific ones)."""
    print("\n" + "=" * 60)
    print("FASTCHECKAI PIPELINE API - USAGE EXAMPLES")
    print("=" * 60)

    examples = [
        ("Basic Usage", example_basic),
        ("Custom Configuration", example_custom_config),
        ("Progress Tracking", example_progress_tracking),
        ("Error Handling", example_error_handling),
        ("Result Analysis", example_result_analysis),
        ("Batch Processing", example_batch_processing),
        ("Integration Patterns", example_integration),
    ]

    print("\nAvailable examples:")
    for idx, (name, _) in enumerate(examples, 1):
        print(f"  {idx}. {name}")

    print("\nTo run a specific example, uncomment it in the main() function.")
    print("For demonstration, running Example 2 (Custom Configuration)...\n")

    # Run one example as demonstration
    example_custom_config()

    print("\n" + "=" * 60)
    print("To run other examples, edit examples/pipeline_usage.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

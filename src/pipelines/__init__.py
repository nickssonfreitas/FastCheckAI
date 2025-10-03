"""Pipelines module - Complete PDF comparison pipeline."""

from src.pipelines.semantic_comparison import (
    PDFComparisonPipeline,
    ComparisonResult,
)

__all__ = [
    "PDFComparisonPipeline",
    "ComparisonResult",
]

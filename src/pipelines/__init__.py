"""Pipelines module - Complete PDF comparison pipeline."""

from src.pipelines.semantic_comparison import (
    ComparisonResult,
    PDFComparisonPipeline,
)

__all__ = [
    "PDFComparisonPipeline",
    "ComparisonResult",
]

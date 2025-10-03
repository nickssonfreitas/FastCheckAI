"""Comparators module - Text and semantic comparison."""

from src.comparators.text_comparator import compare_text
from src.comparators.semantic_comparator import (
    classify_semantic_significance,
    create_semantic_agent,
    get_semantic_stats,
)

__all__ = [
    "compare_text",
    "classify_semantic_significance",
    "create_semantic_agent",
    "get_semantic_stats",
]

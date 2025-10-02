"""
Text Comparison Module for FastCheckAI

This module handles text comparison between aligned sections, using difflib
for diff detection, normalizing text to filter trivial changes, and highlighting
numeric/critical term changes for prioritization.

Example:
    >>> from src.text_comparator import compare_text
    >>> text_a = "tensile strength ≥ 500 MPa"
    >>> text_b = "tensile strength ≥ 550 MPa"
    >>> diffs = compare_text(text_a, text_b)
    >>> print(f"Found {len(diffs['modifications'])} modifications")
"""

import difflib
import logging
import re
import time
from typing import Dict, List

from src import config

logger = logging.getLogger(__name__)


class TextComparisonError(Exception):
    """Base exception for text comparison errors."""

    pass


def normalize_text(text: str) -> str:
    """
    Normalize text to remove trivial formatting differences.

    Removes multiple spaces, normalizes line breaks, and trims whitespace
    to ensure that only semantically significant differences are detected.

    Parameters
    ----------
    text : str
        Text to normalize

    Returns
    -------
    str
        Normalized text

    Examples
    --------
    >>> normalize_text("Test  method\\r\\n")
    'Test method'
    >>> normalize_text("  Multiple   spaces  ")
    'Multiple spaces'
    """
    if not text:
        return ""

    # Convert Windows line breaks to Unix
    text = text.replace("\r\n", "\n")

    # Replace multiple whitespace with single space
    text = re.sub(r"\s+", " ", text)

    # Trim leading/trailing whitespace
    text = text.strip()

    return text


def is_trivial_change(diff: Dict) -> bool:
    """
    Check if a diff represents a trivial change (whitespace-only).

    Parameters
    ----------
    diff : dict
        Diff item with 'original' and 'content' keys

    Returns
    -------
    bool
        True if change is only whitespace formatting

    Examples
    --------
    >>> diff = {"original": "Test  method", "content": "Test method"}
    >>> is_trivial_change(diff)
    True
    >>> diff = {"original": "Test", "content": "Testing"}
    >>> is_trivial_change(diff)
    False
    """
    original = diff.get("original", "")
    content = diff.get("content", "")

    # Normalize both texts
    normalized_original = normalize_text(original)
    normalized_content = normalize_text(content)

    # If normalized texts are identical, it's trivial
    return normalized_original == normalized_content


def contains_numeric_change(diff: Dict) -> bool:
    """
    Check if diff contains numeric values or measurements.

    Detects numbers with optional units (MPa, %, mm, kg, °C, etc.)
    to flag technically significant changes.

    Parameters
    ----------
    diff : dict
        Diff item with 'original' and 'content' keys

    Returns
    -------
    bool
        True if numeric change detected

    Examples
    --------
    >>> diff = {"original": "500 MPa", "content": "550 MPa"}
    >>> contains_numeric_change(diff)
    True
    >>> diff = {"original": "Test", "content": "Testing"}
    >>> contains_numeric_change(diff)
    False
    """
    # Regex for numeric values with context symbols and units
    # Requires context (≥, ≤, ±, =, :) OR units to avoid section ID false positives
    # Supports ASTM Unicode symbols and common engineering units
    numeric_pattern = r"(?:[≥≤±=:]|^)\s*\d+(\.\d+)?(?:\s*[×]?\s*(MPa|%|mm|kg|°C|ksi|psi|°F|GPa|kN|m|cm|in|MPa|GPa))?"

    original = diff.get("original", "")
    content = diff.get("content", "")

    # Check if either text contains numeric values
    has_numeric_original = bool(re.search(numeric_pattern, original))
    has_numeric_content = bool(re.search(numeric_pattern, content))

    # Return True if numbers appear in either version
    return has_numeric_original or has_numeric_content


def contains_critical_term(diff: Dict) -> bool:
    """
    Check if diff contains critical technical terms.

    Uses configurable list of critical terms from config.CRITICAL_TERMS
    to identify changes in mandatory requirements or key specifications.

    Parameters
    ----------
    diff : dict
        Diff item with 'original' and 'content' keys

    Returns
    -------
    bool
        True if critical term found

    Examples
    --------
    >>> diff = {"original": "optional", "content": "mandatory"}
    >>> contains_critical_term(diff)
    True
    >>> diff = {"original": "test", "content": "testing"}
    >>> contains_critical_term(diff)
    False
    """
    # Get critical terms from config (convert to lowercase once)
    critical_terms = [term.lower() for term in getattr(config, "CRITICAL_TERMS", [])]

    original = diff.get("original", "").lower()
    content = diff.get("content", "").lower()

    # Check if any critical term appears in either text
    for term in critical_terms:
        if term in original or term in content:
            return True

    return False


def compare_text(text_a: str, text_b: str) -> Dict[str, List[Dict]]:
    """
    Compare two texts and categorize differences.

    Uses difflib.SequenceMatcher to detect additions, removals, and modifications.
    Normalizes text to filter trivial changes and flags numeric/critical changes
    for prioritization.

    Parameters
    ----------
    text_a : str
        Original text (baseline version)
    text_b : str
        Modified text (new version)

    Returns
    -------
    dict
        Dictionary with categorized differences:
        {
            "additions": [...],
            "removals": [...],
            "modifications": [...]
        }
        Each item contains: type, line, original, content, and optional flags
        (contains_numeric_change, contains_critical_term)

    Raises
    ------
    TextComparisonError
        If comparison fails

    Examples
    --------
    >>> text_a = "This standard covers carbon steel bars"
    >>> text_b = "This standard covers carbon and alloy steel bars"
    >>> diffs = compare_text(text_a, text_b)
    >>> print(f"Modifications: {len(diffs['modifications'])}")
    Modifications: 1

    >>> text_a = "tensile strength ≥ 500 MPa"
    >>> text_b = "tensile strength ≥ 550 MPa"
    >>> diffs = compare_text(text_a, text_b)
    >>> print(diffs["modifications"][0]["contains_numeric_change"])
    True
    """
    start_time = time.time()

    try:
        # Normalize texts before comparison
        normalized_a = normalize_text(text_a)
        normalized_b = normalize_text(text_b)

        # Initialize result structure
        result: Dict[str, List[Dict]] = {"additions": [], "removals": [], "modifications": []}

        # Use SequenceMatcher for diff detection
        matcher = difflib.SequenceMatcher(None, normalized_a, normalized_b, autojunk=False)
        opcodes = matcher.get_opcodes()

        trivial_count = 0
        line_num = 0

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                # No change, skip
                continue

            line_num += 1

            # Extract content
            original_content = normalized_a[i1:i2]
            new_content = normalized_b[j1:j2]

            diff_item = {
                "type": "",
                "line": line_num,
                "original": original_content,
                "content": new_content,
            }

            # Categorize by opcode type
            if tag == "insert":
                diff_item["type"] = "addition"
                diff_item["original"] = ""
            elif tag == "delete":
                diff_item["type"] = "removal"
                diff_item["content"] = ""
            elif tag == "replace":
                diff_item["type"] = "modification"

            # Check if change is trivial (whitespace-only)
            if is_trivial_change(diff_item):
                trivial_count += 1
                continue

            # Add flags for important changes
            if contains_numeric_change(diff_item):
                diff_item["contains_numeric_change"] = True

            if contains_critical_term(diff_item):
                diff_item["contains_critical_term"] = True

            # Append to appropriate category
            if diff_item["type"] == "addition":
                result["additions"].append(diff_item)
            elif diff_item["type"] == "removal":
                result["removals"].append(diff_item)
            elif diff_item["type"] == "modification":
                result["modifications"].append(diff_item)

        # Sort each category: flagged items first
        for category in result.values():
            category.sort(
                key=lambda x: (
                    not x.get("contains_numeric_change", False),
                    not x.get("contains_critical_term", False),
                ),
            )

        # Calculate total differences
        total_diffs = sum(len(v) for v in result.values())

        # Calculate elapsed time
        elapsed = time.time() - start_time

        # Log summary with performance metrics
        logger.info(
            f"Text comparison complete: {total_diffs} differences found "
            f"({trivial_count} trivial ignored) | "
            f"Time: {elapsed:.3f}s for {len(normalized_a)} chars"
        )
        logger.debug(
            f"Breakdown: {len(result['additions'])} additions, "
            f"{len(result['removals'])} removals, "
            f"{len(result['modifications'])} modifications"
        )

        # Warn if performance threshold exceeded
        if elapsed > 5.0:
            logger.warning(
                f"Performance threshold exceeded: {elapsed:.2f}s > 5.0s "
                f"(text length: {len(normalized_a)} chars)"
            )

        return result

    except Exception as e:
        logger.error(f"Text comparison failed: {e}")
        raise TextComparisonError(f"Failed to compare texts: {e}") from e

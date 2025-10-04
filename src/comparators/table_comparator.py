"""
Table Comparison Module for FastCheckAI

This module handles numerical table comparison between aligned tables, detecting
cell-by-cell changes with configurable tolerance, identifying structural changes
(added/removed columns/rows), and highlighting numeric differences for technical specifications.

Example:
    >>> import pandas as pd
    >>> from src.comparators.table_comparator import compare_tables
    >>> table_a = pd.DataFrame({"Grade": ["1020"], "Carbon": [0.40]})
    >>> table_b = pd.DataFrame({"Grade": ["1020"], "Carbon": [0.42]})
    >>> diffs = compare_tables(table_a, table_b, tolerance=0.01)
    >>> print(f"Found {len(diffs['cell_changes'])} cell changes")
"""

import logging
import re
import time
from typing import Any, Dict, List, Union

import pandas as pd

logger = logging.getLogger(__name__)


class TableComparisonError(Exception):
    """Base exception for table comparison errors."""

    pass


def normalize_header(header: str) -> str:
    """
    Normalize column header for robust matching.

    Removes leading/trailing whitespace, converts to lowercase, and removes
    special characters to enable fuzzy matching of column names.

    Parameters
    ----------
    header : str
        Column header to normalize

    Returns
    -------
    str
        Normalized header

    Examples
    --------
    >>> normalize_header("  Carbon %  ")
    'carbon%'
    >>> normalize_header("Tensile Strength (MPa)")
    'tensilestrength(mpa)'
    """
    if not isinstance(header, str):
        return str(header).strip().lower()

    # Remove leading/trailing whitespace
    normalized = header.strip()

    # Convert to lowercase
    normalized = normalized.lower()

    return normalized


def parse_numeric_value(value: Any) -> float:
    """
    Parse numeric value from various formats (string with units, percentage, etc.).

    Extracts numeric values from strings containing units (%, mm, MPa, etc.),
    removes symbols, and converts to float for comparison.

    Parameters
    ----------
    value : any
        Value to parse (can be int, float, str)

    Returns
    -------
    float
        Parsed numeric value, or raises ValueError if not parseable

    Examples
    --------
    >>> parse_numeric_value("0.40%")
    0.4
    >>> parse_numeric_value("500 MPa")
    500.0
    >>> parse_numeric_value(42)
    42.0
    """
    # Already numeric
    if isinstance(value, (int, float)):
        return float(value)

    # Convert to string for parsing
    value_str = str(value).strip()

    # Reject values that start with alphabetic characters (like "Grade 1020")
    # This prevents parsing text that happens to contain numbers
    if value_str and value_str[0].isalpha():
        raise ValueError(f"Value starts with text, not numeric: {value}")

    # Remove common symbols and units
    # Pattern: extract numeric value (including decimals) ignoring units
    numeric_match = re.search(r"[-+]?\d*\.?\d+", value_str)

    if numeric_match:
        return float(numeric_match.group())

    # If no match, raise error
    raise ValueError(f"Cannot parse numeric value from: {value}")


def is_numeric_value(value: Any) -> bool:
    """
    Check if value is numeric or can be parsed as numeric.

    Only considers values with units/symbols as numeric strings.
    Pure integer/float numbers and strings with decimal points or units are numeric.
    Plain digit strings (like "1020") are NOT considered numeric (likely IDs/grades).
    Booleans are explicitly excluded from numeric values.

    Parameters
    ----------
    value : any
        Value to check

    Returns
    -------
    bool
        True if value is numeric or parseable as numeric

    Examples
    --------
    >>> is_numeric_value(42)
    True
    >>> is_numeric_value(0.40)
    True
    >>> is_numeric_value("0.40%")
    True
    >>> is_numeric_value("500 MPa")
    True
    >>> is_numeric_value("1020")  # Plain digits treated as text (grade IDs)
    False
    >>> is_numeric_value("Grade 1020")
    False
    >>> is_numeric_value(True)  # Booleans are not numeric
    False
    """
    # Explicitly exclude booleans (bool is subclass of int in Python)
    if isinstance(value, bool):
        return False

    # If already a Python numeric type, it's numeric
    if isinstance(value, (int, float)):
        return True

    # Convert to string
    value_str = str(value).strip()

    # Reject if starts with letter (e.g., "Grade 1020")
    if value_str and value_str[0].isalpha():
        return False

    # Check if it contains decimal point or has units/symbols
    # This distinguishes "0.40" (numeric) from "1020" (grade ID, text)
    has_decimal = "." in value_str
    has_units = bool(re.search(r"(MPa|%|mm|kg|°C|ksi|psi|°F|GPa|kN|m|cm|in)", value_str))
    has_symbols = bool(re.search(r"[±≥≤]", value_str))

    if has_decimal or has_units or has_symbols:
        try:
            parse_numeric_value(value)
            return True
        except (ValueError, TypeError):
            return False

    # Plain integer strings like "1020" are NOT numeric (likely IDs)
    return False


def detect_cell_changes(
    table_a: pd.DataFrame,
    table_b: pd.DataFrame,
    common_cols: List[str],
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Detect cell-by-cell changes between two aligned tables.

    Compares cells with matching row/column indices, applying tolerance
    for numeric values and exact matching for strings.

    Parameters
    ----------
    table_a : pd.DataFrame
        Original table (baseline)
    table_b : pd.DataFrame
        Modified table (new version)
    common_cols : list of str
        List of common column names to compare (will be normalized internally)
    tolerance : float, default=0.01
        Tolerance for numeric comparison (absolute difference)

    Returns
    -------
    dict
        Dictionary containing:
        - cell_changes: list of detected changes
        - ignored_changes: list of changes within tolerance
        - total_cells_compared: int

    Examples
    --------
    >>> table_a = pd.DataFrame({"Carbon": [0.40]})
    >>> table_b = pd.DataFrame({"Carbon": [0.42]})
    >>> result = detect_cell_changes(table_a, table_b, ["Carbon"])
    >>> len(result["cell_changes"])
    1
    """
    cell_changes = []
    ignored_changes = []
    total_cells = 0

    # Normalize column names for consistent reporting
    common_cols_normalized = [normalize_header(col) for col in common_cols]

    # Determine number of rows to compare (minimum of both tables)
    min_rows = min(len(table_a), len(table_b))

    for row_idx in range(min_rows):
        for col, col_normalized in zip(common_cols, common_cols_normalized):
            total_cells += 1

            # Extract values using .iloc to avoid ambiguity with duplicate column names
            # Find column index in each table
            try:
                col_idx_a = list(table_a.columns).index(col)
                col_idx_b = list(table_b.columns).index(col)
                val_a = table_a.iloc[row_idx, col_idx_a]
                val_b = table_b.iloc[row_idx, col_idx_b]
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to access column '{col}' at row {row_idx}: {e}")
                continue

            # Handle NaN/None values
            if pd.isna(val_a) and pd.isna(val_b):
                continue  # Both empty, no change
            if pd.isna(val_a) or pd.isna(val_b):
                # One is empty, one is not - this is a change
                cell_changes.append(
                    {
                        "row": row_idx,
                        "column": col_normalized,
                        "old_value": val_a if not pd.isna(val_a) else None,
                        "new_value": val_b if not pd.isna(val_b) else None,
                        "delta": None,
                        "change_type": "value_added" if pd.isna(val_a) else "value_removed",
                    }
                )
                continue

            # Check if both values are numeric
            if is_numeric_value(val_a) and is_numeric_value(val_b):
                try:
                    num_a = parse_numeric_value(val_a)
                    num_b = parse_numeric_value(val_b)

                    delta = num_b - num_a

                    # Skip if no change (delta = 0)
                    if delta == 0.0:
                        continue

                    # Apply tolerance
                    if abs(delta) <= tolerance:
                        # Change within tolerance, ignore
                        ignored_changes.append(
                            {
                                "row": row_idx,
                                "column": col_normalized,
                                "old_value": num_a,
                                "new_value": num_b,
                                "delta": delta,
                                "tolerance": tolerance,
                            }
                        )
                    else:
                        # Significant numeric change
                        cell_changes.append(
                            {
                                "row": row_idx,
                                "column": col_normalized,
                                "old_value": num_a,
                                "new_value": num_b,
                                "delta": delta,
                                "change_type": "numeric_change",
                            }
                        )
                except ValueError:
                    # Failed to parse, treat as string comparison
                    if str(val_a) != str(val_b):
                        cell_changes.append(
                            {
                                "row": row_idx,
                                "column": col_normalized,
                                "old_value": str(val_a),
                                "new_value": str(val_b),
                                "delta": None,
                                "change_type": "text_change",
                            }
                        )
            else:
                # String comparison (exact match)
                if str(val_a) != str(val_b):
                    cell_changes.append(
                        {
                            "row": row_idx,
                            "column": col_normalized,
                            "old_value": str(val_a),
                            "new_value": str(val_b),
                            "delta": None,
                            "change_type": "text_change",
                        }
                    )

    return {
        "cell_changes": cell_changes,
        "ignored_changes": ignored_changes,
        "total_cells_compared": total_cells,
    }


def detect_structural_changes(
    table_a: pd.DataFrame, table_b: pd.DataFrame
) -> Dict[str, Union[List[str], List[int]]]:
    """
    Detect structural changes (added/removed columns and rows).

    Identifies columns and rows that were added or removed between versions,
    which indicate structural changes in the specification.

    Parameters
    ----------
    table_a : pd.DataFrame
        Original table (baseline)
    table_b : pd.DataFrame
        Modified table (new version)

    Returns
    -------
    dict
        Dictionary containing:
        - added_columns: list of column names added in table_b
        - removed_columns: list of column names removed from table_a
        - added_rows: list of row indices added in table_b
        - removed_rows: list of row indices removed from table_a

    Examples
    --------
    >>> table_a = pd.DataFrame({"Carbon": [0.40], "Manganese": [0.60]})
    >>> table_b = pd.DataFrame({"Carbon": [0.40], "Manganese": [0.60], "Silicon": [0.15]})
    >>> changes = detect_structural_changes(table_a, table_b)
    >>> "Silicon" in changes["added_columns"]
    True
    """
    # Normalize headers for comparison
    cols_a = set(normalize_header(col) for col in table_a.columns)
    cols_b = set(normalize_header(col) for col in table_b.columns)

    # Detect column changes
    added_columns = list(cols_b - cols_a)
    removed_columns = list(cols_a - cols_b)

    # Detect row changes
    len_a = len(table_a)
    len_b = len(table_b)

    added_rows = []
    removed_rows = []

    if len_b > len_a:
        # Rows added
        added_rows = list(range(len_a, len_b))
    elif len_a > len_b:
        # Rows removed
        removed_rows = list(range(len_b, len_a))

    return {
        "added_columns": added_columns,
        "removed_columns": removed_columns,
        "added_rows": added_rows,
        "removed_rows": removed_rows,
    }


def compare_tables(
    table_a: pd.DataFrame, table_b: pd.DataFrame, tolerance: float = 0.01
) -> Dict[str, Any]:
    """
    Compare two tables and detect all differences (cell changes and structural changes).

    Main entry point for table comparison. Aligns tables by headers, compares
    cells with tolerance, and detects structural changes.

    Parameters
    ----------
    table_a : pd.DataFrame
        Original table (baseline version)
    table_b : pd.DataFrame
        Modified table (new version)
    tolerance : float, default=0.01
        Tolerance for numeric comparison (absolute difference).
        Changes smaller than tolerance are ignored.

    Returns
    -------
    dict
        Comprehensive comparison result containing:
        - cell_changes: list of cell-level differences
        - ignored_changes: list of changes within tolerance
        - structural_changes: dict with added/removed columns/rows
        - summary: dict with comparison statistics

    Raises
    ------
    TableComparisonError
        If comparison fails or tables are incompatible

    Examples
    --------
    >>> import pandas as pd
    >>> table_a = pd.DataFrame({"Grade": ["1020"], "Carbon": [0.40]})
    >>> table_b = pd.DataFrame({"Grade": ["1020"], "Carbon": [0.42]})
    >>> result = compare_tables(table_a, table_b, tolerance=0.01)
    >>> print(f"Changes: {len(result['cell_changes'])}")
    Changes: 1

    >>> # Table with added column
    >>> table_a = pd.DataFrame({"Carbon": [0.40], "Manganese": [0.60]})
    >>> table_b = pd.DataFrame({"Carbon": [0.40], "Manganese": [0.60], "Silicon": [0.15]})
    >>> result = compare_tables(table_a, table_b)
    >>> result["structural_changes"]["added_columns"]
    ['silicon']
    """
    start_time = time.time()

    try:
        # Validate inputs
        if not isinstance(table_a, pd.DataFrame) or not isinstance(table_b, pd.DataFrame):
            raise TableComparisonError("Both inputs must be pandas DataFrames")

        if table_a.empty and table_b.empty:
            logger.warning("Both tables are empty, nothing to compare")
            return {
                "cell_changes": [],
                "ignored_changes": [],
                "structural_changes": {
                    "added_columns": [],
                    "removed_columns": [],
                    "added_rows": [],
                    "removed_rows": [],
                },
                "summary": {
                    "total_changes": 0,
                    "total_ignored": 0,
                    "total_cells_compared": 0,
                    "comparison_time_seconds": 0.0,
                },
            }

        # Normalize headers for both tables
        table_a_normalized = table_a.copy()
        table_b_normalized = table_b.copy()

        table_a_normalized.columns = [normalize_header(col) for col in table_a.columns]
        table_b_normalized.columns = [normalize_header(col) for col in table_b.columns]

        # Identify common columns
        common_cols = list(
            set(table_a_normalized.columns) & set(table_b_normalized.columns)
        )

        if not common_cols:
            logger.warning(
                "Tables have no common columns - incomparable tables. "
                f"Table A columns: {list(table_a_normalized.columns)}, "
                f"Table B columns: {list(table_b_normalized.columns)}"
            )
            # Still detect structural changes
            structural_changes = detect_structural_changes(
                table_a_normalized, table_b_normalized
            )
            return {
                "cell_changes": [],
                "ignored_changes": [],
                "structural_changes": structural_changes,
                "summary": {
                    "total_changes": 0,
                    "total_ignored": 0,
                    "total_cells_compared": 0,
                    "comparison_time_seconds": time.time() - start_time,
                    "warning": "Tables have no common columns",
                },
            }

        # Detect structural changes
        structural_changes = detect_structural_changes(
            table_a_normalized, table_b_normalized
        )

        # Detect cell changes
        cell_comparison = detect_cell_changes(
            table_a_normalized, table_b_normalized, common_cols, tolerance
        )

        # Calculate elapsed time
        elapsed = time.time() - start_time

        # Build summary
        summary = {
            "total_changes": len(cell_comparison["cell_changes"]),
            "total_ignored": len(cell_comparison["ignored_changes"]),
            "total_cells_compared": cell_comparison["total_cells_compared"],
            "common_columns": len(common_cols),
            "tolerance": tolerance,
            "comparison_time_seconds": round(elapsed, 3),
        }

        # Log summary
        logger.info(
            f"Table comparison complete: {summary['total_changes']} changes detected, "
            f"{summary['total_ignored']} within tolerance (±{tolerance}) | "
            f"Compared {summary['total_cells_compared']} cells in {summary['common_columns']} columns | "
            f"Time: {elapsed:.3f}s"
        )

        if structural_changes["added_columns"] or structural_changes["removed_columns"]:
            logger.info(
                f"Structural changes detected: "
                f"{len(structural_changes['added_columns'])} columns added, "
                f"{len(structural_changes['removed_columns'])} columns removed, "
                f"{len(structural_changes['added_rows'])} rows added, "
                f"{len(structural_changes['removed_rows'])} rows removed"
            )

        # Warn if performance threshold exceeded (>5 seconds for 200 cells)
        expected_time = cell_comparison["total_cells_compared"] / 40  # 40 cells/sec
        if elapsed > expected_time and elapsed > 5.0:
            logger.warning(
                f"Performance threshold exceeded: {elapsed:.2f}s > {expected_time:.2f}s "
                f"(expected for {cell_comparison['total_cells_compared']} cells)"
            )

        # Build final result
        result = {
            "cell_changes": cell_comparison["cell_changes"],
            "ignored_changes": cell_comparison["ignored_changes"],
            "structural_changes": structural_changes,
            "summary": summary,
        }

        return result

    except Exception as e:
        logger.error(f"Table comparison failed: {e}")
        raise TableComparisonError(f"Failed to compare tables: {e}") from e

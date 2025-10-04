"""
Unit Tests for Table Comparator Module (src/comparators/table_comparator.py)

This test suite provides comprehensive coverage for the table comparison module,
including cell-by-cell comparison, tolerance-based numeric comparison, structural
change detection, and header normalization.

Test Strategy:
    - Unit tests for each function (normalize_header, parse_numeric_value, etc.)
    - Edge case testing: empty tables, incompatible tables, tolerance edge cases
    - Integration tests for complete table comparison workflow
    - Performance tests for large tables (20x10 = 200 cells)
    - Test coverage target: ≥85%

Linked User Stories:
    - US-024: Cell-by-cell comparison
    - US-025: Tolerance for numeric values
    - US-026: Detection of added/removed columns and rows

Test Execution:
    pytest tests/unit/test_table_comparator.py -v --cov=src.comparators.table_comparator --cov-report=term-missing

Author: QA Automation Specialist
"""

import sys
import time
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.comparators.table_comparator import (
    TableComparisonError,
    compare_tables,
    detect_cell_changes,
    detect_structural_changes,
    is_numeric_value,
    normalize_header,
    parse_numeric_value,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def simple_table_a() -> pd.DataFrame:
    """Fixture for simple table A (baseline)."""
    return pd.DataFrame(
        {"Grade": ["1020", "1040"], "Carbon": [0.40, 0.60], "Manganese": [0.60, 0.80]}
    )


@pytest.fixture
def simple_table_b() -> pd.DataFrame:
    """Fixture for simple table B (with numeric change)."""
    return pd.DataFrame(
        {"Grade": ["1020", "1040"], "Carbon": [0.42, 0.60], "Manganese": [0.60, 0.80]}
    )


@pytest.fixture
def table_with_added_column() -> pd.DataFrame:
    """Fixture for table with added column."""
    return pd.DataFrame(
        {
            "Grade": ["1020", "1040"],
            "Carbon": [0.40, 0.60],
            "Manganese": [0.60, 0.80],
            "Silicon": [0.15, 0.20],
        }
    )


@pytest.fixture
def table_with_added_row() -> pd.DataFrame:
    """Fixture for table with added row."""
    return pd.DataFrame(
        {
            "Grade": ["1020", "1040", "1060"],
            "Carbon": [0.40, 0.60, 0.80],
            "Manganese": [0.60, 0.80, 1.00],
        }
    )


@pytest.fixture
def table_with_units() -> pd.DataFrame:
    """Fixture for table with numeric values containing units."""
    return pd.DataFrame(
        {
            "Property": ["Tensile Strength", "Yield Strength"],
            "Value": ["500 MPa", "350 MPa"],
        }
    )


@pytest.fixture
def table_with_percentages() -> pd.DataFrame:
    """Fixture for table with percentage values."""
    return pd.DataFrame({"Element": ["Carbon", "Manganese"], "Percentage": ["0.40%", "0.60%"]})


@pytest.fixture
def large_table() -> pd.DataFrame:
    """Fixture for performance testing (20x10 = 200 cells)."""
    return pd.DataFrame(np.random.rand(20, 10), columns=[f"Col_{i}" for i in range(10)])


# =============================================================================
# Test normalize_header()
# =============================================================================


def test_normalize_header_basic():
    """Test basic header normalization."""
    assert normalize_header("Carbon") == "carbon"
    assert normalize_header("  Carbon  ") == "carbon"
    assert normalize_header("CARBON") == "carbon"


def test_normalize_header_with_symbols():
    """Test header normalization with symbols."""
    assert normalize_header("Carbon %") == "carbon %"
    assert normalize_header("Tensile Strength (MPa)") == "tensile strength (mpa)"


def test_normalize_header_empty():
    """Test empty header."""
    assert normalize_header("") == ""
    assert normalize_header("   ") == ""


def test_normalize_header_non_string():
    """Test non-string header (converts to string)."""
    assert normalize_header(123) == "123"


# =============================================================================
# Test parse_numeric_value()
# =============================================================================


def test_parse_numeric_value_int():
    """Test parsing integer."""
    assert parse_numeric_value(42) == 42.0


def test_parse_numeric_value_float():
    """Test parsing float."""
    assert parse_numeric_value(3.14) == 3.14


def test_parse_numeric_value_string_plain():
    """Test parsing plain numeric string."""
    assert parse_numeric_value("42") == 42.0
    assert parse_numeric_value("3.14") == 3.14


def test_parse_numeric_value_string_with_units():
    """Test parsing numeric string with units."""
    assert parse_numeric_value("500 MPa") == 500.0
    assert parse_numeric_value("350 ksi") == 350.0
    assert parse_numeric_value("0.40%") == 0.40


def test_parse_numeric_value_string_with_symbols():
    """Test parsing numeric string with symbols."""
    assert parse_numeric_value("±25 MPa") == 25.0
    assert parse_numeric_value("≥500") == 500.0


def test_parse_numeric_value_invalid():
    """Test parsing invalid value."""
    with pytest.raises(ValueError):
        parse_numeric_value("Grade 1020")

    with pytest.raises(ValueError):
        parse_numeric_value("N/A")


# =============================================================================
# Test is_numeric_value()
# =============================================================================


def test_is_numeric_value_numbers():
    """Test numeric check for actual numbers."""
    assert is_numeric_value(42) is True
    assert is_numeric_value(3.14) is True


def test_is_numeric_value_strings():
    """Test numeric check for numeric strings."""
    assert is_numeric_value("0.42") is True  # Decimal = numeric
    assert is_numeric_value("500 MPa") is True  # With units = numeric
    assert is_numeric_value("0.40%") is True  # With symbol = numeric


def test_is_numeric_value_non_numeric():
    """Test numeric check for non-numeric strings."""
    assert is_numeric_value("Grade 1020") is False
    assert is_numeric_value("N/A") is False


def test_is_numeric_value_none():
    """Test numeric check for None."""
    assert is_numeric_value(None) is False


# =============================================================================
# Test detect_structural_changes()
# =============================================================================


def test_detect_structural_changes_no_changes(simple_table_a):
    """Test no structural changes."""
    result = detect_structural_changes(simple_table_a, simple_table_a)
    assert result["added_columns"] == []
    assert result["removed_columns"] == []
    assert result["added_rows"] == []
    assert result["removed_rows"] == []


def test_detect_structural_changes_added_column(simple_table_a, table_with_added_column):
    """Test detection of added column."""
    result = detect_structural_changes(simple_table_a, table_with_added_column)
    assert "silicon" in result["added_columns"]
    assert result["removed_columns"] == []


def test_detect_structural_changes_removed_column(table_with_added_column, simple_table_a):
    """Test detection of removed column."""
    result = detect_structural_changes(table_with_added_column, simple_table_a)
    assert "silicon" in result["removed_columns"]
    assert result["added_columns"] == []


def test_detect_structural_changes_added_row(simple_table_a, table_with_added_row):
    """Test detection of added row."""
    result = detect_structural_changes(simple_table_a, table_with_added_row)
    assert result["added_rows"] == [2]  # Row index 2 was added


def test_detect_structural_changes_removed_row(table_with_added_row, simple_table_a):
    """Test detection of removed row."""
    result = detect_structural_changes(table_with_added_row, simple_table_a)
    assert result["removed_rows"] == [2]  # Row index 2 was removed


# =============================================================================
# Test detect_cell_changes()
# =============================================================================


def test_detect_cell_changes_no_changes(simple_table_a):
    """Test no cell changes."""
    common_cols = list(simple_table_a.columns)
    result = detect_cell_changes(simple_table_a, simple_table_a, common_cols)
    assert len(result["cell_changes"]) == 0
    assert result["total_cells_compared"] == 6  # 2 rows × 3 columns


def test_detect_cell_changes_numeric_change(simple_table_a, simple_table_b):
    """Test numeric cell change detection."""
    common_cols = ["Grade", "Carbon", "Manganese"]
    result = detect_cell_changes(simple_table_a, simple_table_b, common_cols, tolerance=0.01)

    # Should detect 1 change: Carbon 0.40 → 0.42 (delta=0.02 > tolerance=0.01)
    assert len(result["cell_changes"]) == 1

    change = result["cell_changes"][0]
    assert change["column"] == "carbon"
    assert change["old_value"] == 0.40
    assert change["new_value"] == 0.42
    assert change["delta"] == pytest.approx(0.02)


def test_detect_cell_changes_within_tolerance(simple_table_a, simple_table_b):
    """Test change within tolerance is ignored."""
    common_cols = ["Grade", "Carbon", "Manganese"]
    result = detect_cell_changes(simple_table_a, simple_table_b, common_cols, tolerance=0.05)

    # Change is 0.02, within tolerance 0.05, should be ignored
    assert len(result["cell_changes"]) == 0
    assert len(result["ignored_changes"]) == 1


def test_detect_cell_changes_text_change():
    """Test text cell change detection."""
    table_a = pd.DataFrame({"Grade": ["1020"]})
    table_b = pd.DataFrame({"Grade": ["1040"]})

    result = detect_cell_changes(table_a, table_b, ["Grade"])

    assert len(result["cell_changes"]) == 1
    assert result["cell_changes"][0]["change_type"] == "text_change"


def test_detect_cell_changes_nan_values():
    """Test handling of NaN values."""
    table_a = pd.DataFrame({"Value": [1.0, np.nan]})
    table_b = pd.DataFrame({"Value": [1.0, 2.0]})

    result = detect_cell_changes(table_a, table_b, ["Value"])

    # Should detect 1 change: NaN → 2.0
    assert len(result["cell_changes"]) == 1
    assert result["cell_changes"][0]["change_type"] == "value_added"


# =============================================================================
# Test compare_tables() - Main Function
# =============================================================================


def test_compare_tables_basic(simple_table_a, simple_table_b):
    """Test basic table comparison."""
    result = compare_tables(simple_table_a, simple_table_b, tolerance=0.01)

    # Should detect 1 change
    assert result["summary"]["total_changes"] == 1
    assert result["summary"]["tolerance"] == 0.01
    assert len(result["cell_changes"]) == 1


def test_compare_tables_identical(simple_table_a):
    """Test comparison of identical tables."""
    result = compare_tables(simple_table_a, simple_table_a)

    assert result["summary"]["total_changes"] == 0
    assert len(result["cell_changes"]) == 0


def test_compare_tables_with_structural_changes(simple_table_a, table_with_added_column):
    """Test table comparison with structural changes."""
    result = compare_tables(simple_table_a, table_with_added_column)

    # Should detect added column
    assert len(result["structural_changes"]["added_columns"]) == 1
    assert "silicon" in result["structural_changes"]["added_columns"]


def test_compare_tables_no_common_columns():
    """Test comparison of tables with no common columns."""
    table_a = pd.DataFrame({"ColA": [1, 2]})
    table_b = pd.DataFrame({"ColB": [3, 4]})

    result = compare_tables(table_a, table_b)

    assert "warning" in result["summary"]
    assert result["summary"]["total_changes"] == 0


def test_compare_tables_empty_tables():
    """Test comparison of empty tables."""
    table_a = pd.DataFrame()
    table_b = pd.DataFrame()

    result = compare_tables(table_a, table_b)

    assert result["summary"]["total_changes"] == 0


def test_compare_tables_invalid_input():
    """Test comparison with invalid input."""
    with pytest.raises(TableComparisonError):
        compare_tables("not a dataframe", pd.DataFrame())

    with pytest.raises(TableComparisonError):
        compare_tables(pd.DataFrame(), "not a dataframe")


def test_compare_tables_tolerance_parameter(simple_table_a):
    """Test different tolerance values."""
    # Create table with small change
    table_b = simple_table_a.copy()
    table_b.loc[0, "Carbon"] = 0.41  # Change from 0.40 to 0.41 (delta=0.01)

    # With tolerance 0.01, should be ignored
    result_strict = compare_tables(simple_table_a, table_b, tolerance=0.01)
    assert result_strict["summary"]["total_changes"] == 0

    # With tolerance 0.005, should be detected
    result_loose = compare_tables(simple_table_a, table_b, tolerance=0.005)
    assert result_loose["summary"]["total_changes"] == 1


# =============================================================================
# Test Real-World Scenarios (ASTM Standards)
# =============================================================================


def test_astm_composition_table():
    """Test comparison of ASTM chemical composition table."""
    # ASTM 2015
    table_2015 = pd.DataFrame(
        {
            "Grade": ["1020", "1040", "1060"],
            "Carbon": [0.40, 0.60, 0.80],
            "Manganese": [0.60, 0.80, 1.00],
        }
    )

    # ASTM 2016 with change in Carbon for Grade 1020
    table_2016 = pd.DataFrame(
        {
            "Grade": ["1020", "1040", "1060"],
            "Carbon": [0.42, 0.60, 0.80],  # Changed
            "Manganese": [0.60, 0.80, 1.00],
        }
    )

    result = compare_tables(table_2015, table_2016, tolerance=0.01)

    assert result["summary"]["total_changes"] == 1
    assert result["cell_changes"][0]["column"] == "carbon"
    assert result["cell_changes"][0]["row"] == 0


def test_astm_table_with_added_element():
    """Test ASTM table with added chemical element."""
    # ASTM 2015
    table_2015 = pd.DataFrame(
        {"Grade": ["1020"], "Carbon": [0.40], "Manganese": [0.60]}
    )

    # ASTM 2016 with Silicon added
    table_2016 = pd.DataFrame(
        {"Grade": ["1020"], "Carbon": [0.40], "Manganese": [0.60], "Silicon": [0.15]}
    )

    result = compare_tables(table_2015, table_2016)

    assert len(result["structural_changes"]["added_columns"]) == 1
    assert "silicon" in result["structural_changes"]["added_columns"]


def test_table_with_unit_strings(table_with_units):
    """Test comparison of tables with numeric values containing units."""
    # Create modified version with changed value
    table_modified = table_with_units.copy()
    table_modified.loc[0, "Value"] = "550 MPa"  # Changed from 500 MPa

    result = compare_tables(table_with_units, table_modified, tolerance=10.0)

    # Should detect change: 500 → 550 (delta=50 > tolerance=10)
    assert result["summary"]["total_changes"] == 1


# =============================================================================
# Performance Tests
# =============================================================================


def test_compare_tables_performance_200_cells(large_table):
    """Test performance for 20x10 table (200 cells) - should be <5 seconds."""
    # Create modified version with 5 changes
    table_modified = large_table.copy()
    for i in range(5):
        table_modified.iloc[i, 0] += 0.1

    start_time = time.time()
    result = compare_tables(large_table, table_modified, tolerance=0.01)
    elapsed = time.time() - start_time

    # Should complete in <5 seconds
    assert elapsed < 5.0

    # Should detect 5 changes
    assert result["summary"]["total_changes"] == 5


def test_compare_tables_logging(simple_table_a, simple_table_b, caplog):
    """Test that comparison logs summary information."""
    import logging

    with caplog.at_level(logging.INFO):
        compare_tables(simple_table_a, simple_table_b, tolerance=0.01)

    # Check that log contains summary
    assert "Table comparison complete" in caplog.text
    assert "changes detected" in caplog.text


# =============================================================================
# Edge Cases
# =============================================================================


def test_compare_tables_single_cell():
    """Test comparison of single-cell tables."""
    table_a = pd.DataFrame({"Value": [42]})
    table_b = pd.DataFrame({"Value": [43]})

    result = compare_tables(table_a, table_b, tolerance=0.5)

    assert result["summary"]["total_changes"] == 1


def test_compare_tables_case_insensitive_headers():
    """Test that header comparison is case-insensitive."""
    table_a = pd.DataFrame({"Carbon": [0.40], "MANGANESE": [0.60]})
    table_b = pd.DataFrame({"carbon": [0.40], "Manganese": [0.60]})

    result = compare_tables(table_a, table_b)

    # Should recognize both columns as common despite different casing
    assert result["summary"]["common_columns"] == 2
    assert result["summary"]["total_changes"] == 0


def test_compare_tables_different_row_counts():
    """Test comparison of tables with different row counts."""
    table_a = pd.DataFrame({"Value": [1, 2]})
    table_b = pd.DataFrame({"Value": [1, 2, 3]})

    result = compare_tables(table_a, table_b)

    # Should only compare first 2 rows (min)
    assert result["summary"]["total_cells_compared"] == 2

    # Should detect 1 added row
    assert result["structural_changes"]["added_rows"] == [2]

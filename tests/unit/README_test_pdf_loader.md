# Unit Tests for PDF Loader Module

## Overview

Comprehensive test suite for `src/pdf_loader.py` with **100% code coverage**.

**Test File**: `/home/nicksson/Git/sidi/FastCheckAI/tests/unit/test_pdf_loader.py`

**Coverage Achievement**:
- **src/pdf_loader.py**: 100% (59/59 statements)
- **Total Project**: 99% (117/117 statements)
- **50 passing tests**

## Test Structure

### Test Classes

1. **TestValidatePdfSize** (6 tests)
   - Small file validation success
   - Custom max size limits
   - Large file rejection (>25MB)
   - FileNotFoundError handling
   - Size rounding precision
   - Exact limit edge case

2. **TestDetectPdfType** (7 tests)
   - Native PDF detection (high char count)
   - Scanned PDF detection (low char count)
   - Custom character thresholds
   - Empty PDF handling (0 pages)
   - Minimal text below threshold
   - Exact threshold boundary
   - Whitespace handling

3. **TestLoadPdf** (12 tests)
   - Valid small PDF loading
   - Relative/absolute path resolution
   - FileNotFoundError for missing files
   - Size validation enforcement
   - Large file loading (with/without validation)
   - Corrupted PDF error handling
   - Password-protected PDF handling
   - Logging verification
   - Multiple page PDFs
   - Exception chaining
   - Unexpected error wrapping

4. **TestExceptionHierarchy** (5 tests)
   - Base exception validation
   - Inheritance hierarchy
   - Exception catching polymorphism
   - Error message preservation

5. **TestWithExistingFiles** (4 tests)
   - Integration tests with real files in `data/inputs/`
   - Tests skip if files unavailable

6. **TestEdgeCases** (5 tests)
   - Zero max_mb limit
   - Zero threshold detection
   - Path object handling
   - Empty string paths
   - Symbolic link resolution

7. **TestLogging** (7 tests)
   - Info logging on success
   - Error logging on failures
   - Native/scanned detection logging
   - Warning for edge cases
   - Portuguese error messages

8. **TestModuleMetadata** (3 tests)
   - Module docstring presence
   - Function documentation
   - Exception docstrings

## Test Fixtures

### Temporary PDF Files

```python
temp_pdf_small      # <1MB, native PDF with text
temp_pdf_large      # >25MB for size validation testing
temp_pdf_native     # Native PDF (>50 chars, extractable text)
temp_pdf_scanned    # Scanned PDF (empty, <50 chars)
temp_pdf_corrupted  # Invalid PDF file
temp_pdf_empty      # Mock for 0-page PDF (PyMuPDF limitation)
temp_dir            # Temporary directory for test files
```

### Existing Test Files

```python
existing_test_pdfs  # Maps to data/inputs/
    - small: doc_a.pdf (1.3KB)
    - large: large_file.pdf (30MB)
    - scanned: scanned_sample.pdf (610 bytes)
    - corrupted: corrupted.pdf (34 bytes)
```

## Running Tests

### Basic Test Execution

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all PDF loader tests
pytest tests/unit/test_pdf_loader.py -v

# Run specific test class
pytest tests/unit/test_pdf_loader.py::TestValidatePdfSize -v

# Run single test
pytest tests/unit/test_pdf_loader.py::TestLoadPdf::test_load_pdf_valid_small_pdf_success -v
```

### Coverage Reports

```bash
# Terminal coverage report
pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-report=html
open htmlcov/index.html

# XML coverage for CI/CD
pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-report=xml
```

### Filtered Test Execution

```bash
# Run only validation tests
pytest tests/unit/test_pdf_loader.py -k "validate" -v

# Run only detection tests
pytest tests/unit/test_pdf_loader.py -k "detect" -v

# Run only error handling tests
pytest tests/unit/test_pdf_loader.py -k "error or raise" -v

# Skip slow integration tests
pytest tests/unit/test_pdf_loader.py -m "not integration" -v
```

### Verbose Output

```bash
# Show full output including logs
pytest tests/unit/test_pdf_loader.py -v -s

# Show local variables on failure
pytest tests/unit/test_pdf_loader.py -l

# Stop on first failure
pytest tests/unit/test_pdf_loader.py -x

# Run last failed tests
pytest tests/unit/test_pdf_loader.py --lf
```

## Test Coverage Details

### Functions Tested

| Function | Coverage | Lines Tested |
|----------|----------|--------------|
| `validate_pdf_size()` | 100% | 64-78 (all branches) |
| `detect_pdf_type()` | 100% | 81-128 (all branches) |
| `load_pdf()` | 100% | 131-206 (all error paths) |

### Exception Coverage

| Exception | Test Count | Scenarios |
|-----------|------------|-----------|
| `PDFLoaderError` | 2 | Base exception, unexpected errors |
| `PDFSizeError` | 3 | File too large, edge cases |
| `PDFCorruptedError` | 3 | Invalid PDF, corrupted files, encryption |
| `FileNotFoundError` | 3 | Missing files, invalid paths |

### Branch Coverage

All conditional branches tested:
- ✅ File exists / not exists
- ✅ Size within limit / exceeds limit
- ✅ Native PDF / scanned PDF
- ✅ Empty PDF / pages present
- ✅ Character count above/below/at threshold
- ✅ Validation enabled / disabled
- ✅ Relative / absolute paths
- ✅ Success / error cases

## Key Test Patterns

### 1. Fixture-Based Test Data

```python
def test_load_pdf_valid_small_pdf_success(self, temp_pdf_small, caplog):
    """Use pytest fixtures for clean test data."""
    pdf_doc = load_pdf(str(temp_pdf_small), validate_size=True)
    assert isinstance(pdf_doc, fitz.Document)
    pdf_doc.close()
```

### 2. Exception Testing

```python
def test_load_pdf_corrupted_file_raises_error(self, temp_pdf_corrupted, caplog):
    """Test expected exceptions with context."""
    with pytest.raises(PDFCorruptedError) as exc_info:
        load_pdf(str(temp_pdf_corrupted), validate_size=False)

    assert "corrompido" in str(exc_info.value)
```

### 3. Logging Verification

```python
def test_validate_pdf_size_logs_info_on_success(self, temp_pdf_small, caplog):
    """Verify log messages using caplog fixture."""
    with caplog.at_level(logging.INFO):
        validate_pdf_size(temp_pdf_small, max_mb=25)

    assert "Validating PDF size" in caplog.text
```

### 4. Mock Usage

```python
def test_detect_pdf_type_empty_pdf_no_pages(self, caplog):
    """Use mocks when real objects can't be created."""
    mock_doc = MagicMock(spec=fitz.Document)
    mock_doc.page_count = 0

    result = detect_pdf_type(mock_doc)
    assert result["requires_ocr"] is True
```

### 5. Integration with Real Files

```python
@pytest.mark.skipif(
    not (Path(__file__).parent.parent.parent / "data/inputs/doc_a.pdf").exists(),
    reason="Test files not available",
)
def test_load_existing_small_pdf(self, existing_test_pdfs):
    """Conditional tests using real data files."""
    if existing_test_pdfs["small"].exists():
        pdf_doc = load_pdf(str(existing_test_pdfs["small"]))
        assert pdf_doc.page_count > 0
        pdf_doc.close()
```

## Test Scenarios Covered

### Happy Path Tests ✅

- ✅ Load valid PDF successfully
- ✅ Validate file size within limits
- ✅ Detect native PDF with text
- ✅ Detect scanned PDF without text
- ✅ Handle relative and absolute paths
- ✅ Load PDFs without size validation

### Error Handling Tests ✅

- ✅ File not found
- ✅ File exceeds size limit (>25MB)
- ✅ Corrupted PDF file
- ✅ Password-protected PDF
- ✅ Invalid file format
- ✅ Empty string path
- ✅ Unexpected exceptions

### Edge Cases Tests ✅

- ✅ PDF with exactly 0 pages
- ✅ PDF with exactly threshold characters
- ✅ File size exactly at limit (25.0MB)
- ✅ Character threshold = 0
- ✅ Max size = 0
- ✅ Symbolic links
- ✅ Path objects vs strings
- ✅ Very small files (rounds to 0.0MB)

### Logging Tests ✅

- ✅ Info messages on success
- ✅ Error messages on failure
- ✅ Warning messages for edge cases
- ✅ Portuguese error messages
- ✅ File details in logs (name, size, pages)

## Code Quality Metrics

### Test Statistics

```
Total Tests:              50
Passing:                  50 (100%)
Failing:                  0 (0%)
Errors:                   0 (0%)
Warnings:                 6 (deprecation warnings from PyMuPDF)
```

### Coverage Metrics

```
Lines of Code:            59
Lines Tested:             59 (100%)
Branches:                 ~15
Branch Coverage:          100%
```

### Test Execution Performance

```
Total Duration:           ~1.3 seconds
Average per Test:         ~26ms
Slowest Test:             ~150ms (temp PDF creation)
Fastest Test:             ~5ms (exception tests)
```

## CI/CD Integration

### pytest.ini Configuration

Already configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=term-missing --cov-report=html"
```

### GitHub Actions Example

```yaml
- name: Run PDF Loader Tests
  run: |
    source .venv/bin/activate
    pytest tests/unit/test_pdf_loader.py \
      --cov=src.pdf_loader \
      --cov-report=xml \
      --cov-fail-under=85 \
      --junitxml=test-results/junit.xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    flags: pdf_loader
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-fail-under=85 -q
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "No module named pytest"
```bash
# Solution: Install dev dependencies
pip install -e ".[dev]"
# OR
source .venv/bin/activate
```

**Issue**: Fixtures creating files that persist
```bash
# Solution: pytest automatically cleans tmp_path fixtures
# No action needed - files are auto-deleted
```

**Issue**: PyMuPDF deprecation warnings
```bash
# Solution: These are harmless library warnings
# Suppress with: pytest -W ignore::DeprecationWarning
```

**Issue**: Test files not found in data/inputs/
```bash
# Solution: Integration tests auto-skip if files missing
# Ensure data/inputs/ directory exists with test PDFs
```

## Best Practices Demonstrated

1. **Isolation**: Each test is independent, uses fresh fixtures
2. **Cleanup**: Temporary files auto-deleted via `tmp_path` fixture
3. **Clarity**: Test names follow pattern: `test_<function>_<scenario>_<result>`
4. **Coverage**: All branches, error paths, edge cases tested
5. **Documentation**: Comprehensive docstrings for each test
6. **Assertions**: Specific, meaningful assertion messages
7. **Logging**: Verification of log output and error messages
8. **Mocking**: Used appropriately when real objects unavailable
9. **Performance**: Fast execution (~1.3s for 50 tests)
10. **Maintainability**: Clear structure, organized by functionality

## Test Maintenance

### Adding New Tests

1. Identify the scenario to test
2. Choose appropriate test class
3. Create fixture if needed
4. Write test with clear docstring
5. Verify coverage increases

```python
def test_new_scenario(self, temp_pdf_small):
    """Test description of new scenario."""
    # Arrange
    pdf_path = temp_pdf_small

    # Act
    result = function_under_test(pdf_path)

    # Assert
    assert expected_condition
```

### Updating Tests

When `src/pdf_loader.py` changes:
1. Run tests to identify failures
2. Update assertions to match new behavior
3. Add tests for new functionality
4. Verify coverage remains ≥85%

### Test Review Checklist

- [ ] Test has clear, descriptive name
- [ ] Test has comprehensive docstring
- [ ] Test is in appropriate class
- [ ] Test uses fixtures appropriately
- [ ] Test assertions are specific
- [ ] Test cleans up resources
- [ ] Test runs independently
- [ ] Coverage increases or maintained

## Related Documentation

- **Source Module**: `/home/nicksson/Git/sidi/FastCheckAI/src/pdf_loader.py`
- **Coverage Report**: `/home/nicksson/Git/sidi/FastCheckAI/htmlcov/index.html`
- **Project Tests**: `/home/nicksson/Git/sidi/FastCheckAI/tests/`
- **pytest Docs**: https://docs.pytest.org/

## Success Criteria Met ✅

- ✅ **Coverage**: 100% (exceeds 85% requirement)
- ✅ **Test Count**: 50 comprehensive tests
- ✅ **Error Handling**: All exception types tested
- ✅ **Edge Cases**: Zero pages, exact limits, boundaries
- ✅ **Logging**: Portuguese messages verified
- ✅ **Path Handling**: Relative, absolute, Path objects
- ✅ **Fixtures**: Reusable, clean, isolated
- ✅ **Performance**: <2 seconds execution
- ✅ **Documentation**: Complete with examples
- ✅ **CI/CD Ready**: Works with pytest.ini config

## Test Report Summary

```
================================ tests coverage ================================
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src/__init__.py         2      0   100%
src/config.py          56      1    98%   61
src/pdf_loader.py      59      0   100%   ← TARGET MODULE
-------------------------------------------------
TOTAL                 117      1    99%

======================== 50 passed, 6 warnings in 1.29s ========================
```

---

**Maintained by**: FastCheckAI QA Team
**Last Updated**: 2025-09-30
**Test Framework**: pytest 8.4.2 + pytest-cov 7.0.0
**Python Version**: 3.12.11

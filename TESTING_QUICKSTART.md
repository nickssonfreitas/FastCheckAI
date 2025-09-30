# Testing Quick Start Guide

## PDF Loader Unit Tests

### Quick Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all PDF loader tests with coverage
pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-report=term-missing

# View HTML coverage report
pytest tests/unit/test_pdf_loader.py --cov=src.pdf_loader --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Results

✅ **50 passing tests**
✅ **100% code coverage** of `src/pdf_loader.py`
✅ **All critical paths tested**

### Test Organization

```
tests/unit/test_pdf_loader.py
├── TestValidatePdfSize (6 tests)
├── TestDetectPdfType (7 tests)
├── TestLoadPdf (12 tests)
├── TestExceptionHierarchy (5 tests)
├── TestWithExistingFiles (4 tests)
├── TestEdgeCases (5 tests)
├── TestLogging (7 tests)
└── TestModuleMetadata (3 tests)
```

### Coverage Report

```
Name                Stmts   Miss  Cover
-----------------------------------------
src/pdf_loader.py      59      0   100%
```

### Run Specific Tests

```bash
# Test validation only
pytest tests/unit/test_pdf_loader.py::TestValidatePdfSize -v

# Test error handling
pytest tests/unit/test_pdf_loader.py -k "error or raise" -v

# Stop on first failure
pytest tests/unit/test_pdf_loader.py -x
```

### Full Documentation

See `/home/nicksson/Git/sidi/FastCheckAI/tests/unit/README_test_pdf_loader.md`

---

**Author**: FastCheckAI Development Team
**Date**: 2025-09-30

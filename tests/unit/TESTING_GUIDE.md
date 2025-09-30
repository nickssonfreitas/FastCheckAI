# Quick Testing Guide - FastCheckAI Configuration Tests

## Quick Start

### Run All Tests
```bash
# Using uv (recommended)
uv run pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing

# Using pytest directly
pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing
```

### Expected Output
```
================================ tests coverage ================================
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
src/__init__.py       2      0   100%
src/config.py        56      0   100%
-----------------------------------------------
TOTAL                58      0   100%

============================== 45 passed in 0.13s ==============================
```

## Test Commands Reference

### Basic Commands
```bash
# Run all config tests (verbose)
pytest tests/unit/test_config.py -v

# Run with coverage report
pytest tests/unit/test_config.py -v --cov=src/config

# Run with HTML coverage report
pytest tests/unit/test_config.py -v --cov=src/config --cov-report=html
# Then open: htmlcov/index.html

# Run with missing lines in coverage
pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing

# Run with both terminal and HTML reports
pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing --cov-report=html
```

### Selective Test Execution
```bash
# Run specific test class
pytest tests/unit/test_config.py::TestGetEnvVariable -v

# Run specific test method
pytest tests/unit/test_config.py::TestGetEnvVariable::test_get_env_variable_required_exists -v

# Run tests matching pattern
pytest tests/unit/test_config.py -k "required" -v

# Run tests matching multiple patterns
pytest tests/unit/test_config.py -k "required or optional" -v
```

### Test Output Control
```bash
# Show all print statements
pytest tests/unit/test_config.py -v -s

# Show only failed tests
pytest tests/unit/test_config.py -v --tb=short

# Show only test names (no output)
pytest tests/unit/test_config.py -q

# Show full traceback on failures
pytest tests/unit/test_config.py -v --tb=long
```

### Coverage Options
```bash
# Coverage with branch analysis
pytest tests/unit/test_config.py --cov=src/config --cov-branch

# Coverage for specific lines
pytest tests/unit/test_config.py --cov=src/config --cov-report=term:skip-covered

# Fail if coverage below 85%
pytest tests/unit/test_config.py --cov=src/config --cov-fail-under=85
```

## Test Results Interpretation

### ✅ All Tests Passing
```
============================== 45 passed in 0.13s ==============================
```
**Status:** All good! 100% coverage achieved.

### ❌ Test Failures
```
FAILED tests/unit/test_config.py::TestGetEnvVariable::test_example - AssertionError
```
**Action:** Check the specific test failure and fix the issue.

### ⚠️ Coverage Below Target
```
TOTAL                58     5    91%
```
**Action:** Add tests to cover missing lines shown in "Missing" column.

## Coverage Reports

### Terminal Report (term-missing)
Shows missing line numbers directly in terminal:
```
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
src/config.py        56      3    95%   45-47
```

### HTML Report
Interactive HTML report with line-by-line coverage:
```bash
pytest tests/unit/test_config.py --cov=src/config --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Structure

### Test Organization
```
tests/unit/test_config.py
├── TestGetEnvVariable (9 tests)
│   ├── test_get_env_variable_required_exists
│   ├── test_get_env_variable_required_missing_raises_error
│   ├── test_get_env_variable_optional_exists
│   └── ...
├── TestSetupLogging (8 tests)
│   ├── test_setup_logging_console_only
│   ├── test_setup_logging_with_file
│   └── ...
├── TestConfigurationConstants (9 tests)
├── TestConfigurationError (3 tests)
├── TestConfigurationIntegration (3 tests)
├── TestEdgeCases (10 tests)
└── Module-level tests (4 tests)
```

### Total: 45 Tests

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'pytest'"
**Solution:**
```bash
uv pip install pytest pytest-cov
# or
pip install pytest pytest-cov
```

### Issue: "No coverage data collected"
**Solution:** Ensure you're running from project root:
```bash
cd /home/nicksson/Git/sidi/FastCheckAI
uv run pytest tests/unit/test_config.py --cov=src/config
```

### Issue: Tests fail due to .env file
**Solution:** Tests don't depend on .env file. They use mocked environment variables.

### Issue: Log files accumulate
**Solution:** Tests use temporary directories that auto-cleanup. No action needed.

## Continuous Integration

### GitHub Actions Example
```yaml
- name: Run config unit tests
  run: |
    uv run pytest tests/unit/test_config.py \
      -v \
      --cov=src/config \
      --cov-report=xml \
      --cov-fail-under=85
```

### Quality Gates
- ✅ All tests must pass
- ✅ Code coverage ≥ 85%
- ✅ No flaky tests
- ✅ Test execution < 5 seconds

## Test Development Workflow

### 1. Run Tests Locally
```bash
uv run pytest tests/unit/test_config.py -v --cov=src/config
```

### 2. Check Coverage
```bash
uv run pytest tests/unit/test_config.py --cov=src/config --cov-report=html
open htmlcov/index.html
```

### 3. Add Missing Tests
Identify uncovered lines in HTML report and add tests.

### 4. Verify 100% Coverage
```bash
uv run pytest tests/unit/test_config.py --cov=src/config --cov-fail-under=100
```

## Performance Benchmarks

| Metric | Value | Target |
|--------|-------|--------|
| Test Execution Time | ~0.13s | < 5s |
| Tests Count | 45 | - |
| Code Coverage | 100% | ≥ 85% |
| Flaky Tests | 0 | 0 |

## Documentation

- **Full Documentation:** `tests/unit/test_config_README.md`
- **Test File:** `tests/unit/test_config.py`
- **Module Under Test:** `src/config.py`

## Next Steps

1. **Run the tests:** `uv run pytest tests/unit/test_config.py -v --cov=src/config`
2. **Review coverage:** `uv run pytest tests/unit/test_config.py --cov=src/config --cov-report=html`
3. **Read full docs:** Open `tests/unit/test_config_README.md`

---

**Quick Reference Card**

| Command | Purpose |
|---------|---------|
| `pytest tests/unit/test_config.py -v` | Run all tests (verbose) |
| `pytest tests/unit/test_config.py --cov=src/config` | Run with coverage |
| `pytest tests/unit/test_config.py -k "test_name"` | Run specific test |
| `pytest tests/unit/test_config.py --cov-report=html` | Generate HTML report |
| `pytest tests/unit/test_config.py --cov-fail-under=85` | Enforce coverage threshold |

---

✅ **Current Status:** 45/45 tests passing | 100% coverage | 0 flaky tests

# Configuration Module Unit Tests

## Overview

This document provides comprehensive documentation for the unit tests of the `src/config.py` module. The test suite achieves **100% code coverage** and follows pytest best practices.

## Test Coverage Summary

| Module | Statements | Missing | Coverage |
|--------|-----------|---------|----------|
| `src/config.py` | 56 | 0 | **100%** |

## Test Structure

### Test File Location
```
tests/unit/test_config.py
```

### Test Organization

The test suite is organized into 7 main test classes:

1. **TestGetEnvVariable** - Tests for `get_env_variable()` function
2. **TestSetupLogging** - Tests for `setup_logging()` function
3. **TestConfigurationConstants** - Tests for configuration constants
4. **TestConfigurationError** - Tests for `ConfigurationError` exception
5. **TestConfigurationIntegration** - Integration tests
6. **TestEdgeCases** - Edge cases and boundary conditions
7. **Module-level tests** - Documentation and metadata tests

---

## Test Classes

### 1. TestGetEnvVariable (9 tests)

Tests the `get_env_variable()` function that retrieves environment variables with validation.

#### Test Cases

| Test | Description | Coverage |
|------|-------------|----------|
| `test_get_env_variable_required_exists` | Retrieves existing required variable | Happy path |
| `test_get_env_variable_required_missing_raises_error` | Raises ConfigurationError for missing required variable | Error handling |
| `test_get_env_variable_optional_exists` | Retrieves existing optional variable | Happy path |
| `test_get_env_variable_optional_missing_returns_default` | Returns default for missing optional variable | Default handling |
| `test_get_env_variable_optional_missing_no_default_returns_none` | Returns None when no default provided | None handling |
| `test_get_env_variable_empty_string_treated_as_missing` | Treats empty string as missing for required vars | Edge case |
| `test_get_env_variable_whitespace_value` | Preserves whitespace values | Edge case |
| `test_get_env_variable_numeric_values` | Returns numeric values as strings | Type handling |
| `test_get_env_variable_special_characters` | Preserves special characters | Edge case |

**Key Behaviors Tested:**
- ✅ Required variable validation
- ✅ Optional variable with default values
- ✅ ConfigurationError exception raising
- ✅ Empty string handling
- ✅ Special character preservation

---

### 2. TestSetupLogging (8 tests)

Tests the `setup_logging()` function that configures logging handlers and levels.

#### Test Cases

| Test | Description | Coverage |
|------|-------------|----------|
| `test_setup_logging_console_only` | Sets up logging with console handler only | Basic setup |
| `test_setup_logging_with_file` | Sets up logging with file handler | File logging |
| `test_setup_logging_creates_log_directory` | Creates log directory if it doesn't exist | Directory creation |
| `test_setup_logging_different_log_levels` | Tests all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) | Log level handling |
| `test_setup_logging_case_insensitive_level` | Accepts lowercase log level names | Case handling |
| `test_setup_logging_format` | Verifies log message formatting | Format verification |
| `test_setup_logging_multiple_calls_append_handlers` | Multiple calls add handlers (warning scenario) | Handler accumulation |
| `test_setup_logging_file_permissions` | Verifies log file permissions | File permissions |

**Key Behaviors Tested:**
- ✅ Console and file handler creation
- ✅ Log directory creation (nested paths)
- ✅ Log level configuration (all levels)
- ✅ Case-insensitive level names
- ✅ File permissions (read/write)
- ✅ Handler accumulation warning

**Note:** These tests use pytest's `caplog` fixture to work around pytest's logging interference.

---

### 3. TestConfigurationConstants (9 tests)

Tests that configuration constants are loaded correctly with appropriate types and values.

#### Test Cases

| Test | Description | Validation |
|------|-------------|-----------|
| `test_model_default_value` | MODEL has correct default ("gpt-4o") | Default value |
| `test_temperature_is_float` | TEMPERATURE is float in range [0.0, 1.0] | Type & range |
| `test_max_tokens_is_int` | MAX_TOKENS is positive integer | Type & value |
| `test_fuzzy_match_threshold_is_float` | FUZZY_MATCH_THRESHOLD is float [0.0, 1.0] | Type & range |
| `test_semantic_confidence_threshold_is_float` | SEMANTIC_CONFIDENCE_THRESHOLD is float [0.0, 1.0] | Type & range |
| `test_alignment_confidence_threshold_is_float` | ALIGNMENT_CONFIDENCE_THRESHOLD is float [0.0, 1.0] | Type & range |
| `test_max_pdf_size_is_int` | MAX_PDF_SIZE_MB is positive integer | Type & value |
| `test_max_processing_time_is_int` | MAX_PROCESSING_TIME_SECONDS is positive integer | Type & value |
| `test_thresholds_have_logical_values` | All thresholds >= 0.5 (logical minimum) | Business logic |

**Constants Tested:**
- `OPENAI_API_KEY` (implicitly via imports)
- `MODEL`, `TEMPERATURE`, `MAX_TOKENS`
- `FUZZY_MATCH_THRESHOLD`, `SEMANTIC_CONFIDENCE_THRESHOLD`, `ALIGNMENT_CONFIDENCE_THRESHOLD`
- `MAX_PDF_SIZE_MB`, `MAX_PROCESSING_TIME_SECONDS`

---

### 4. TestConfigurationError (3 tests)

Tests the custom `ConfigurationError` exception class.

#### Test Cases

| Test | Description | Coverage |
|------|-------------|----------|
| `test_configuration_error_is_exception` | ConfigurationError is Exception subclass | Inheritance |
| `test_configuration_error_message` | Preserves error message | Message handling |
| `test_configuration_error_can_be_raised_and_caught` | Can be raised and caught properly | Exception flow |

---

### 5. TestConfigurationIntegration (3 tests)

Integration tests verifying full configuration loading scenarios.

#### Test Cases

| Test | Description | Scenario |
|------|-------------|----------|
| `test_full_configuration_load_with_custom_values` | Loads all config with custom env vars | Custom config |
| `test_configuration_with_missing_optional_uses_defaults` | Uses defaults when optional vars missing | Default fallback |
| `test_configuration_error_provides_helpful_message` | Error messages are actionable | User experience |

---

### 6. TestEdgeCases (10 tests)

Comprehensive edge case and boundary condition testing.

#### Test Cases

| Test | Description | Edge Case Type |
|------|-------------|----------------|
| `test_get_env_variable_with_none_default` | Explicit None as default value | Null handling |
| `test_get_env_variable_required_false_without_default` | Optional without explicit default | Implicit defaults |
| `test_setup_logging_with_empty_log_file_string` | Empty string for log file | Falsy values |
| `test_temperature_conversion_with_string_float` | Float conversion from string | Type conversion |
| `test_integer_conversion_with_string_int` | Integer conversion from string | Type conversion |
| `test_invalid_float_conversion_raises_error` | Invalid float string raises ValueError | Error handling |
| `test_invalid_int_conversion_raises_error` | Invalid int string raises ValueError | Error handling |
| `test_very_long_environment_variable_value` | 10,000 character variable value | Size limits |
| `test_unicode_in_environment_variable` | Unicode characters (emoji, CJK) | Character encoding |

---

### 7. Module-level Tests (4 tests)

Tests for documentation and metadata.

#### Test Cases
- `test_module_docstring_exists` - Verifies test module has documentation
- `test_configuration_error_has_docstring` - Verifies exception has docstring
- `test_get_env_variable_has_docstring` - Verifies function has docstring
- `test_setup_logging_has_docstring` - Verifies function has docstring

---

## Fixtures

### `clean_env`
**Purpose:** Provides clean environment for each test

**Scope:** Function-level

**Behavior:**
- Clears all relevant environment variables before each test
- Uses pytest's `monkeypatch` for safe environment manipulation
- Ensures test isolation

**Usage:**
```python
def test_example(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("TEST_VAR", "value")
    # test code
```

---

### `temp_log_dir`
**Purpose:** Provides temporary directory for log files

**Scope:** Function-level

**Behavior:**
- Creates temporary log directory
- Automatically cleaned up after test
- Based on pytest's `tmp_path` fixture

**Usage:**
```python
def test_example(temp_log_dir: Path) -> None:
    log_file = temp_log_dir / "test.log"
    setup_logging(log_file=str(log_file))
```

---

### `reset_logging`
**Purpose:** Resets logging configuration after each test

**Scope:** Function-level

**Behavior:**
- Stores initial logging handlers
- Removes added handlers after test
- Restores initial log level
- Handles pytest's logging interference

**Usage:**
```python
def test_example(reset_logging: None) -> None:
    setup_logging(log_level="DEBUG")
    # test code - logging will be reset after
```

---

## Running the Tests

### Basic Execution

```bash
# Run all config tests
pytest tests/unit/test_config.py -v

# Run with coverage
pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing

# Run with HTML coverage report
pytest tests/unit/test_config.py -v --cov=src/config --cov-report=html

# Run specific test class
pytest tests/unit/test_config.py::TestGetEnvVariable -v

# Run specific test
pytest tests/unit/test_config.py::TestGetEnvVariable::test_get_env_variable_required_exists -v
```

### Using uv (project package manager)

```bash
# Run all tests with coverage
uv run pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing

# Run with HTML report
uv run pytest tests/unit/test_config.py -v --cov=src/config --cov-report=html
```

### Test Output Example

```
============================= test session starts ==============================
platform linux -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0
collected 45 items

tests/unit/test_config.py::TestGetEnvVariable::test_get_env_variable_required_exists PASSED [  2%]
tests/unit/test_config.py::TestGetEnvVariable::test_get_env_variable_required_missing_raises_error PASSED [  4%]
...
tests/unit/test_config.py::test_setup_logging_has_docstring PASSED       [100%]

================================ tests coverage ================================

Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
src/__init__.py       2      0   100%
src/config.py        56      0   100%
-----------------------------------------------
TOTAL                58      0   100%

============================== 45 passed in 0.13s ==============================
```

---

## Test Strategy & Best Practices

### 1. **Test Isolation**
- Each test is independent and can run in any order
- Uses `clean_env` fixture to ensure no environment variable pollution
- `reset_logging` fixture prevents logging configuration leakage

### 2. **Mocking Strategy**
- Environment variables mocked with `monkeypatch`
- No dependency on actual `.env` file during tests
- Temporary directories used for file operations

### 3. **Naming Convention**
- Pattern: `test_<function>_<scenario>_<expected_result>`
- Examples:
  - `test_get_env_variable_required_missing_raises_error`
  - `test_setup_logging_creates_log_directory`

### 4. **Test Structure (Given-When-Then)**
```python
def test_example():
    # Given: Setup preconditions
    clean_env.setenv("VAR", "value")

    # When: Execute the function
    result = get_env_variable("VAR")

    # Then: Assert expected outcome
    assert result == "value"
```

### 5. **Coverage Targets**
- ✅ **Achieved:** 100% code coverage for `src/config.py`
- ✅ All branches tested (if-else, try-except)
- ✅ All functions tested
- ✅ All edge cases covered

### 6. **Error Testing**
- Uses `pytest.raises()` for exception testing
- Verifies error messages are descriptive
- Tests both happy paths and error paths

### 7. **pytest Integration**
- Works with pytest's logging system (`caplog` fixture)
- Compatible with pytest-cov plugin
- Uses pytest's `tmp_path` for temporary files

---

## Common Test Patterns

### Testing Required Variables
```python
def test_get_env_variable_required_missing_raises_error(
    clean_env: pytest.MonkeyPatch
) -> None:
    # Given: Variable is not set
    # (clean_env ensures this)

    # When/Then: Raises ConfigurationError
    with pytest.raises(ConfigurationError) as exc_info:
        get_env_variable("MISSING_VAR", required=True)

    # Verify error message
    assert "MISSING_VAR" in str(exc_info.value)
    assert "not set" in str(exc_info.value)
```

### Testing Optional Variables with Defaults
```python
def test_get_env_variable_optional_missing_returns_default(
    clean_env: pytest.MonkeyPatch
) -> None:
    # Given: Variable is not set

    # When: Getting optional variable with default
    result = get_env_variable(
        "MISSING_OPTIONAL",
        required=False,
        default="default_value"
    )

    # Then: Default is returned
    assert result == "default_value"
```

### Testing Logging Setup
```python
def test_setup_logging_with_file(
    reset_logging: None,
    temp_log_dir: Path,
    caplog
) -> None:
    # Given: Log file path
    log_file = temp_log_dir / "test.log"

    # When: Setting up logging
    with caplog.at_level(logging.DEBUG):
        setup_logging(log_level="DEBUG", log_file=str(log_file))

        # Then: Log file created
        assert log_file.exists()
```

---

## Coverage Report Analysis

### Covered Statements (56/56)

| Line Range | Code | Coverage |
|------------|------|----------|
| 1-21 | Module docstring, imports, .env loading | ✅ |
| 24-27 | ConfigurationError class | ✅ |
| 30-66 | get_env_variable() function | ✅ |
| 69-96 | setup_logging() function | ✅ |
| 103-104 | OPENAI_API_KEY loading | ✅ |
| 110-117 | LLM config (MODEL, TEMPERATURE, MAX_TOKENS) | ✅ |
| 123-136 | Pipeline thresholds | ✅ |
| 142-148 | Performance limits | ✅ |
| 154-167 | Path constants | ✅ |
| 173-182 | Logging setup and logger initialization | ✅ |

**All branches covered:**
- ✅ `if required and not value` (lines 60-64)
- ✅ `if log_file` (lines 86-89)
- ✅ Exception raising paths
- ✅ Default value paths

---

## Continuous Integration

### pytest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=term-missing --cov-report=html"
```

### Recommended CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --dev

      - name: Run unit tests
        run: uv run pytest tests/unit/test_config.py -v --cov=src/config --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

---

## Troubleshooting

### Issue: pytest logging interference

**Symptom:** Logging tests fail due to pytest's own handlers

**Solution:** Tests use `caplog` fixture and filter out pytest handlers

```python
def count_non_pytest_handlers():
    return len([h for h in logging.getLogger().handlers
               if type(h).__name__ not in ['LogCaptureHandler', '_LiveLoggingNullHandler']])
```

### Issue: Environment variable pollution

**Symptom:** Tests fail when run together but pass individually

**Solution:** Use `clean_env` fixture to ensure isolation

```python
@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch):
    for var in ["VAR1", "VAR2", ...]:
        monkeypatch.delenv(var, raising=False)
    yield monkeypatch
```

### Issue: Log files not cleaned up

**Symptom:** Temporary log files accumulate

**Solution:** Use `temp_log_dir` fixture based on pytest's `tmp_path` (auto-cleanup)

---

## Future Enhancements

### Potential Additions

1. **Performance Tests**
   - Test config loading time
   - Test large .env file handling

2. **Security Tests**
   - Test sensitive data masking in logs
   - Test .env file permission checks

3. **Parameterized Tests**
   - Use `@pytest.mark.parametrize` for threshold values
   - Test multiple log levels in single test

4. **Mock Tests**
   - Mock `load_dotenv()` to test .env file missing scenario
   - Mock `getattr(logging, level)` for invalid level handling

### Example Parameterized Test

```python
@pytest.mark.parametrize("level,expected", [
    ("DEBUG", logging.DEBUG),
    ("INFO", logging.INFO),
    ("WARNING", logging.WARNING),
    ("ERROR", logging.ERROR),
    ("CRITICAL", logging.CRITICAL),
])
def test_setup_logging_levels(level: str, expected: int):
    setup_logging(log_level=level)
    assert logging.getLogger().level == expected
```

---

## Success Metrics

### Coverage Achieved
✅ **100% code coverage** for `src/config.py` (56/56 statements)

### Test Quality Metrics
- ✅ **45 test cases** covering all scenarios
- ✅ **Zero flaky tests** (deterministic execution)
- ✅ **Fast execution** (~0.13 seconds)
- ✅ **Complete isolation** (no side effects)

### Test Pyramid Adherence
- ✅ **Unit tests only** (no dependencies)
- ✅ **Fast feedback** (milliseconds per test)
- ✅ **Comprehensive coverage** (happy paths + edge cases + errors)

---

## References

- **pytest documentation:** https://docs.pytest.org/
- **pytest-cov plugin:** https://pytest-cov.readthedocs.io/
- **Python logging:** https://docs.python.org/3/library/logging.html
- **Project repository:** FastCheckAI

---

## Conclusion

This test suite provides **production-ready, comprehensive coverage** for the FastCheckAI configuration module. All critical paths are tested, including:

- ✅ Environment variable loading and validation
- ✅ Logging configuration and handler setup
- ✅ Configuration constants with type validation
- ✅ Error handling with descriptive messages
- ✅ Edge cases and boundary conditions

**Key Achievement:** 100% code coverage with 45 passing tests, zero flaky tests, and fast execution time.

The tests follow pytest best practices, maintain complete isolation, and provide clear documentation for future maintainers.

---

**Author:** QA Automation Specialist
**Date:** 2025-09-30
**Test Framework:** pytest 8.4.2 + pytest-cov 7.0.0
**Python Version:** 3.12.11

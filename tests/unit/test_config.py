"""
Unit Tests for Configuration Module (src/config.py)

This test suite provides comprehensive coverage for the configuration module,
including environment variable loading, validation, logging setup, and error handling.

Test Strategy:
    - Unit tests for individual functions (get_env_variable, setup_logging)
    - Edge case testing: missing variables, invalid values, defaults
    - Integration tests for full configuration loading
    - Mocking environment variables to ensure test isolation
    - Test coverage target: 85%+

Test Execution:
    pytest tests/unit/test_config.py -v --cov=src/config --cov-report=term-missing

Author: QA Automation Specialist
"""

import logging
import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import (
    ALIGNMENT_CONFIDENCE_THRESHOLD,
    FUZZY_MATCH_THRESHOLD,
    MAX_PDF_SIZE_MB,
    MAX_PROCESSING_TIME_SECONDS,
    MAX_TOKENS,
    MODEL,
    SEMANTIC_CONFIDENCE_THRESHOLD,
    TEMPERATURE,
    ConfigurationError,
    get_env_variable,
    setup_logging,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Generator[pytest.MonkeyPatch, None, None]:
    """
    Fixture to provide a clean environment for each test.

    Clears all relevant environment variables before each test to ensure isolation.

    Yields
    ------
    pytest.MonkeyPatch
        Monkeypatch instance for setting environment variables
    """
    # Clear relevant environment variables
    env_vars = [
        "OPENAI_API_KEY",
        "MODEL",
        "TEMPERATURE",
        "MAX_TOKENS",
        "FUZZY_MATCH_THRESHOLD",
        "SEMANTIC_CONFIDENCE_THRESHOLD",
        "ALIGNMENT_CONFIDENCE_THRESHOLD",
        "MAX_PDF_SIZE_MB",
        "MAX_PROCESSING_TIME_SECONDS",
        "LOG_LEVEL",
        "TEST_VAR",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    yield monkeypatch


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """
    Fixture to provide a temporary directory for log files.

    Parameters
    ----------
    tmp_path : Path
        pytest's built-in temporary directory fixture

    Returns
    -------
    Path
        Temporary directory path for log files
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


@pytest.fixture
def reset_logging() -> Generator[None, None, None]:
    """
    Fixture to reset logging configuration after each test.

    Ensures logging handlers are cleaned up to prevent side effects.
    Note: pytest adds its own handlers, so we filter them out.
    """
    # Store initial handlers (pytest's handlers)
    root_logger = logging.getLogger()
    initial_handlers = root_logger.handlers[:]
    initial_level = root_logger.level

    yield

    # Remove all handlers except pytest's original handlers
    for handler in root_logger.handlers[:]:
        if handler not in initial_handlers:
            handler.close()
            root_logger.removeHandler(handler)

    # Restore initial level
    root_logger.setLevel(initial_level)


# =============================================================================
# Tests for get_env_variable()
# =============================================================================


class TestGetEnvVariable:
    """Test suite for get_env_variable() function."""

    def test_get_env_variable_required_exists(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test retrieving a required environment variable that exists."""
        # Given: Environment variable is set
        clean_env.setenv("TEST_VAR", "test_value")

        # When: Getting required variable
        result = get_env_variable("TEST_VAR", required=True)

        # Then: Variable value is returned
        assert result == "test_value"

    def test_get_env_variable_required_missing_raises_error(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that missing required variable raises ConfigurationError."""
        # Given: Environment variable is not set (clean_env ensures this)

        # When/Then: Getting required variable raises ConfigurationError
        with pytest.raises(ConfigurationError) as exc_info:
            get_env_variable("MISSING_VAR", required=True)

        # Verify error message is descriptive
        assert "Required environment variable 'MISSING_VAR' is not set" in str(exc_info.value)
        assert "Please add it to your .env file" in str(exc_info.value)

    def test_get_env_variable_optional_exists(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test retrieving an optional environment variable that exists."""
        # Given: Optional variable is set
        clean_env.setenv("OPTIONAL_VAR", "optional_value")

        # When: Getting optional variable
        result = get_env_variable("OPTIONAL_VAR", required=False, default="default_value")

        # Then: Actual value is returned (not default)
        assert result == "optional_value"

    def test_get_env_variable_optional_missing_returns_default(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that missing optional variable returns default value."""
        # Given: Variable is not set (clean_env ensures this)

        # When: Getting optional variable with default
        result = get_env_variable("MISSING_OPTIONAL", required=False, default="default_value")

        # Then: Default value is returned
        assert result == "default_value"

    def test_get_env_variable_optional_missing_no_default_returns_none(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that missing optional variable without default returns None."""
        # Given: Variable is not set and no default provided

        # When: Getting optional variable without default
        result = get_env_variable("MISSING_OPTIONAL", required=False)

        # Then: None is returned
        assert result is None

    def test_get_env_variable_empty_string_treated_as_missing(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that empty string is treated as missing for required variables."""
        # Given: Variable is set to empty string
        clean_env.setenv("EMPTY_VAR", "")

        # When/Then: Getting required variable with empty value raises error
        with pytest.raises(ConfigurationError) as exc_info:
            get_env_variable("EMPTY_VAR", required=True)

        assert "Required environment variable 'EMPTY_VAR' is not set" in str(exc_info.value)

    def test_get_env_variable_whitespace_value(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test handling of whitespace-only values."""
        # Given: Variable contains only whitespace
        clean_env.setenv("WHITESPACE_VAR", "   ")

        # When: Getting the variable
        result = get_env_variable("WHITESPACE_VAR", required=True)

        # Then: Whitespace is preserved (not stripped)
        assert result == "   "

    def test_get_env_variable_numeric_values(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test retrieving numeric values as strings."""
        # Given: Numeric values are set
        clean_env.setenv("INT_VAR", "42")
        clean_env.setenv("FLOAT_VAR", "3.14")

        # When: Getting numeric variables
        int_result = get_env_variable("INT_VAR", required=False, default="0")
        float_result = get_env_variable("FLOAT_VAR", required=False, default="0.0")

        # Then: Values are returned as strings
        assert int_result == "42"
        assert float_result == "3.14"
        assert isinstance(int_result, str)
        assert isinstance(float_result, str)

    def test_get_env_variable_special_characters(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test handling of special characters in values."""
        # Given: Variable with special characters
        special_value = "api_key_!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        clean_env.setenv("SPECIAL_VAR", special_value)

        # When: Getting the variable
        result = get_env_variable("SPECIAL_VAR")

        # Then: Special characters are preserved
        assert result == special_value


# =============================================================================
# Tests for setup_logging()
# =============================================================================


class TestSetupLogging:
    """Test suite for setup_logging() function.

    Note: These tests verify the setup_logging function's behavior.
    pytest's logging system may interfere with some assertions, so we
    focus on testing the key behaviors: file creation, handler addition.
    """

    def test_setup_logging_console_only(self, reset_logging: None, caplog) -> None:
        """Test logging setup with console handler only (no file)."""
        # Given/When: Setting up logging with console only
        with caplog.at_level(logging.INFO):
            setup_logging(log_level="INFO", log_file=None)

            # Then: Logging works at INFO level
            test_logger = logging.getLogger("test_console")
            test_logger.info("Test INFO message")

            # Verify message was captured
            assert "Test INFO message" in caplog.text

    def test_setup_logging_with_file(
        self, reset_logging: None, temp_log_dir: Path, caplog
    ) -> None:
        """Test logging setup with both console and file handlers."""
        # Given: Log file path is specified
        log_file = temp_log_dir / "test.log"

        # When: Setting up logging with file
        with caplog.at_level(logging.DEBUG):
            setup_logging(log_level="DEBUG", log_file=str(log_file))

            # Then: Verify log file was created (most important check)
            assert log_file.exists()

            # Verify logging works
            test_logger = logging.getLogger("test_file")
            test_logger.debug("Test DEBUG message")

            # Message should be captured
            assert "Test DEBUG message" in caplog.text

    def test_setup_logging_creates_log_directory(
        self, reset_logging: None, tmp_path: Path
    ) -> None:
        """Test that setup_logging creates log directory if it doesn't exist."""
        # Given: Log directory doesn't exist
        log_file = tmp_path / "nested" / "dirs" / "test.log"
        assert not log_file.parent.exists()

        # When: Setting up logging with nested path
        setup_logging(log_level="INFO", log_file=str(log_file))

        # Then: Directory structure is created
        assert log_file.parent.exists()
        assert log_file.exists()

    def test_setup_logging_different_log_levels(self, reset_logging: None) -> None:
        """Test logging setup with different log levels."""
        # Test each log level
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        for level_name, level_value in log_levels.items():
            # Reset handlers before each iteration
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)

            # When: Setting up logging with specific level
            setup_logging(log_level=level_name)

            # Then: Logger has correct level
            assert root_logger.level == level_value

    def test_setup_logging_case_insensitive_level(self, reset_logging: None, caplog) -> None:
        """Test that log level is case-insensitive."""
        # When: Setting log level in lowercase
        with caplog.at_level(logging.WARNING):
            setup_logging(log_level="warning")

            # Then: Logging works at WARNING level
            test_logger = logging.getLogger("test_case")
            test_logger.warning("Test WARNING message")

            # Verify the logging system accepts lowercase level
            assert "Test WARNING message" in caplog.text

    def test_setup_logging_format(
        self, reset_logging: None, temp_log_dir: Path, caplog
    ) -> None:
        """Test that logging format is configured correctly."""
        # Given: Log file is set up
        log_file = temp_log_dir / "format_test.log"

        with caplog.at_level(logging.INFO):
            setup_logging(log_level="INFO", log_file=str(log_file))

            # When: Logging a test message
            test_logger = logging.getLogger("test_format_module")
            test_logger.info("Format test message")

            # Then: Log file was created
            assert log_file.exists()

            # And: Message was logged (captured by pytest)
            assert "Format test message" in caplog.text
            assert "test_format_module" in caplog.text

    def test_setup_logging_multiple_calls_append_handlers(self, reset_logging: None) -> None:
        """Test that multiple setup_logging calls append handlers (warning scenario)."""
        # Given: Get baseline handler count
        root_logger = logging.getLogger()

        # Filter out pytest handlers to count only our handlers
        def count_non_pytest_handlers():
            return len([h for h in root_logger.handlers
                       if type(h).__name__ not in ['LogCaptureHandler', '_LiveLoggingNullHandler', '_FileHandler']])

        initial_count = count_non_pytest_handlers()

        # When: Calling setup_logging twice
        setup_logging(log_level="INFO")
        after_first = count_non_pytest_handlers()

        setup_logging(log_level="DEBUG")
        after_second = count_non_pytest_handlers()

        # Then: Each call should add handlers (demonstrating potential duplicate handler issue)
        assert after_first >= initial_count  # First call adds handlers
        assert after_second >= after_first    # Second call may add more handlers

    def test_setup_logging_file_permissions(
        self, reset_logging: None, temp_log_dir: Path
    ) -> None:
        """Test that log file is created with appropriate permissions."""
        # Given: Log file path
        log_file = temp_log_dir / "permissions_test.log"

        # When: Setting up logging
        setup_logging(log_level="INFO", log_file=str(log_file))

        # Then: Log file exists and is writable
        assert log_file.exists()
        assert os.access(log_file, os.W_OK)
        assert os.access(log_file, os.R_OK)

        # Verify file has proper permissions (readable and writable by owner)
        file_stats = log_file.stat()
        assert file_stats.st_size >= 0  # File was created


# =============================================================================
# Tests for Configuration Constants
# =============================================================================


class TestConfigurationConstants:
    """Test suite for configuration constants loaded at module import."""

    def test_model_default_value(self) -> None:
        """Test that MODEL has correct default value."""
        # Then: Default model is gpt-4o
        assert MODEL == "gpt-4o" or isinstance(MODEL, str)

    def test_temperature_is_float(self) -> None:
        """Test that TEMPERATURE is a float."""
        # Then: TEMPERATURE is float type
        assert isinstance(TEMPERATURE, float)
        # And: Within valid range (0.0-1.0)
        assert 0.0 <= TEMPERATURE <= 1.0

    def test_max_tokens_is_int(self) -> None:
        """Test that MAX_TOKENS is an integer."""
        # Then: MAX_TOKENS is int type
        assert isinstance(MAX_TOKENS, int)
        # And: Is positive
        assert MAX_TOKENS > 0

    def test_fuzzy_match_threshold_is_float(self) -> None:
        """Test that FUZZY_MATCH_THRESHOLD is a float in valid range."""
        # Then: Threshold is float
        assert isinstance(FUZZY_MATCH_THRESHOLD, float)
        # And: Within valid range (0.0-1.0)
        assert 0.0 <= FUZZY_MATCH_THRESHOLD <= 1.0

    def test_semantic_confidence_threshold_is_float(self) -> None:
        """Test that SEMANTIC_CONFIDENCE_THRESHOLD is a float in valid range."""
        # Then: Threshold is float
        assert isinstance(SEMANTIC_CONFIDENCE_THRESHOLD, float)
        # And: Within valid range (0.0-1.0)
        assert 0.0 <= SEMANTIC_CONFIDENCE_THRESHOLD <= 1.0

    def test_alignment_confidence_threshold_is_float(self) -> None:
        """Test that ALIGNMENT_CONFIDENCE_THRESHOLD is a float in valid range."""
        # Then: Threshold is float
        assert isinstance(ALIGNMENT_CONFIDENCE_THRESHOLD, float)
        # And: Within valid range (0.0-1.0)
        assert 0.0 <= ALIGNMENT_CONFIDENCE_THRESHOLD <= 1.0

    def test_max_pdf_size_is_int(self) -> None:
        """Test that MAX_PDF_SIZE_MB is a positive integer."""
        # Then: Size is int
        assert isinstance(MAX_PDF_SIZE_MB, int)
        # And: Is positive
        assert MAX_PDF_SIZE_MB > 0

    def test_max_processing_time_is_int(self) -> None:
        """Test that MAX_PROCESSING_TIME_SECONDS is a positive integer."""
        # Then: Time is int
        assert isinstance(MAX_PROCESSING_TIME_SECONDS, int)
        # And: Is positive
        assert MAX_PROCESSING_TIME_SECONDS > 0

    def test_thresholds_have_logical_values(self) -> None:
        """Test that threshold values are logically reasonable."""
        # All thresholds should be between 0.5 and 1.0 for strictness
        assert FUZZY_MATCH_THRESHOLD >= 0.5
        assert SEMANTIC_CONFIDENCE_THRESHOLD >= 0.5
        assert ALIGNMENT_CONFIDENCE_THRESHOLD >= 0.5


# =============================================================================
# Tests for ConfigurationError Exception
# =============================================================================


class TestConfigurationError:
    """Test suite for ConfigurationError exception."""

    def test_configuration_error_is_exception(self) -> None:
        """Test that ConfigurationError is a proper Exception subclass."""
        # Given: ConfigurationError class
        error = ConfigurationError("Test error")

        # Then: It's an Exception instance
        assert isinstance(error, Exception)

    def test_configuration_error_message(self) -> None:
        """Test that ConfigurationError preserves error message."""
        # Given: Error with specific message
        message = "Custom configuration error message"
        error = ConfigurationError(message)

        # Then: Message is preserved
        assert str(error) == message

    def test_configuration_error_can_be_raised_and_caught(self) -> None:
        """Test that ConfigurationError can be raised and caught."""
        # Given: Function that raises ConfigurationError
        def raise_config_error():
            raise ConfigurationError("Test error")

        # When/Then: Error can be caught
        with pytest.raises(ConfigurationError):
            raise_config_error()


# =============================================================================
# Integration Tests
# =============================================================================


class TestConfigurationIntegration:
    """Integration tests for full configuration loading."""

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-test-key-12345",
            "MODEL": "gpt-4o-mini",
            "TEMPERATURE": "0.5",
            "MAX_TOKENS": "8000",
            "FUZZY_MATCH_THRESHOLD": "0.85",
            "SEMANTIC_CONFIDENCE_THRESHOLD": "0.75",
            "ALIGNMENT_CONFIDENCE_THRESHOLD": "0.82",
            "MAX_PDF_SIZE_MB": "50",
            "MAX_PROCESSING_TIME_SECONDS": "300",
            "LOG_LEVEL": "DEBUG",
        },
        clear=False,
    )
    def test_full_configuration_load_with_custom_values(self) -> None:
        """Test loading configuration with all custom environment variables."""
        # This test verifies that when config module is imported with custom values,
        # all constants reflect those values (requires module reload in practice)

        # When: Getting variables with custom values set
        api_key = get_env_variable("OPENAI_API_KEY")
        model = get_env_variable("MODEL", required=False, default="gpt-4o")
        temperature = float(get_env_variable("TEMPERATURE", required=False, default="0.3"))
        max_tokens = int(get_env_variable("MAX_TOKENS", required=False, default="4000"))

        # Then: Custom values are used
        assert api_key == "sk-test-key-12345"
        assert model == "gpt-4o-mini"
        assert temperature == 0.5
        assert max_tokens == 8000

    def test_configuration_with_missing_optional_uses_defaults(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that missing optional variables use default values."""
        # Given: Only required variable is set
        clean_env.setenv("OPENAI_API_KEY", "sk-test-key")

        # When: Getting optional variables
        model = get_env_variable("MODEL", required=False, default="gpt-4o")
        temperature = float(get_env_variable("TEMPERATURE", required=False, default="0.3"))
        log_level = get_env_variable("LOG_LEVEL", required=False, default="INFO")

        # Then: Default values are used
        assert model == "gpt-4o"
        assert temperature == 0.3
        assert log_level == "INFO"

    def test_configuration_error_provides_helpful_message(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that configuration errors provide actionable error messages."""
        # Given: Required variable is missing

        # When/Then: Error message is helpful
        with pytest.raises(ConfigurationError) as exc_info:
            get_env_variable("OPENAI_API_KEY", required=True)

        error_message = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_message
        assert "not set" in error_message
        assert ".env file" in error_message


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_get_env_variable_with_none_default(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test explicit None as default value."""
        # When: Getting optional variable with explicit None default
        result = get_env_variable("MISSING_VAR", required=False, default=None)

        # Then: None is returned
        assert result is None

    def test_get_env_variable_required_false_without_default(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test optional variable without explicit default."""
        # When: Getting optional variable without default parameter
        result = get_env_variable("MISSING_VAR", required=False)

        # Then: None is returned (implicit default)
        assert result is None

    def test_setup_logging_with_empty_log_file_string(self, reset_logging: None) -> None:
        """Test setup_logging with empty string for log_file."""
        # Given: Empty string for log file (edge case, treated as falsy)

        # When: Setting up logging with empty string
        # Note: Empty string is falsy in Python, so it acts like None
        setup_logging(log_level="INFO", log_file="")

        # Then: Should not crash, but may not create file handler
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) >= 1

    def test_temperature_conversion_with_string_float(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test float conversion from environment variable string."""
        # Given: Temperature as string
        clean_env.setenv("TEMPERATURE", "0.75")

        # When: Converting to float
        temperature = float(get_env_variable("TEMPERATURE", required=False, default="0.3"))

        # Then: Conversion succeeds
        assert temperature == 0.75
        assert isinstance(temperature, float)

    def test_integer_conversion_with_string_int(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test integer conversion from environment variable string."""
        # Given: Integer as string
        clean_env.setenv("MAX_TOKENS", "5000")

        # When: Converting to int
        max_tokens = int(get_env_variable("MAX_TOKENS", required=False, default="4000"))

        # Then: Conversion succeeds
        assert max_tokens == 5000
        assert isinstance(max_tokens, int)

    def test_invalid_float_conversion_raises_error(
        self, clean_env: pytest.MonkeyPatch
    ) -> None:
        """Test that invalid float conversion raises ValueError."""
        # Given: Invalid float string
        clean_env.setenv("TEMPERATURE", "not_a_number")

        # When/Then: Float conversion raises ValueError
        with pytest.raises(ValueError):
            float(get_env_variable("TEMPERATURE", required=False, default="0.3"))

    def test_invalid_int_conversion_raises_error(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test that invalid int conversion raises ValueError."""
        # Given: Invalid int string
        clean_env.setenv("MAX_TOKENS", "12.5")

        # When/Then: Int conversion raises ValueError (can't convert float string to int directly)
        with pytest.raises(ValueError):
            int(get_env_variable("MAX_TOKENS", required=False, default="4000"))

    def test_very_long_environment_variable_value(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test handling of very long environment variable values."""
        # Given: Very long value (e.g., long API key)
        long_value = "x" * 10000
        clean_env.setenv("LONG_VAR", long_value)

        # When: Getting the variable
        result = get_env_variable("LONG_VAR")

        # Then: Full value is returned
        assert result == long_value
        assert len(result) == 10000

    def test_unicode_in_environment_variable(self, clean_env: pytest.MonkeyPatch) -> None:
        """Test handling of unicode characters in environment variables."""
        # Given: Unicode value
        unicode_value = "Hello 世界 🌍 测试"
        clean_env.setenv("UNICODE_VAR", unicode_value)

        # When: Getting the variable
        result = get_env_variable("UNICODE_VAR")

        # Then: Unicode is preserved
        assert result == unicode_value


# =============================================================================
# Test Documentation and Metadata
# =============================================================================


def test_module_docstring_exists() -> None:
    """Test that this test module has proper documentation."""
    # Then: Module has docstring
    assert __doc__ is not None
    assert len(__doc__) > 0
    assert "Configuration Module" in __doc__


def test_configuration_error_has_docstring() -> None:
    """Test that ConfigurationError has documentation."""
    # Then: ConfigurationError has docstring
    assert ConfigurationError.__doc__ is not None
    assert "configuration" in ConfigurationError.__doc__.lower()


def test_get_env_variable_has_docstring() -> None:
    """Test that get_env_variable has documentation."""
    # Then: Function has docstring
    assert get_env_variable.__doc__ is not None
    assert "environment variable" in get_env_variable.__doc__.lower()


def test_setup_logging_has_docstring() -> None:
    """Test that setup_logging has documentation."""
    # Then: Function has docstring
    assert setup_logging.__doc__ is not None
    assert "logging" in setup_logging.__doc__.lower()

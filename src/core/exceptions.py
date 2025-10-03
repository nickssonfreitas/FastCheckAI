"""
Custom exceptions for FastCheckAI.

This module defines the exception hierarchy used throughout the application
for better error handling and reporting.
"""


class FastCheckAIError(Exception):
    """Base exception for all FastCheckAI errors."""

    pass


class ConfigurationError(FastCheckAIError):
    """Raised when configuration is invalid or missing."""

    pass


class PDFProcessingError(FastCheckAIError):
    """Raised when PDF processing fails (loading, validation, extraction)."""

    pass


class AlignmentError(FastCheckAIError):
    """Raised when section alignment fails or confidence is too low."""

    pass


class LLMError(FastCheckAIError):
    """Raised when LLM API calls fail (OpenAI, Agno framework)."""

    pass


class ReportGenerationError(FastCheckAIError):
    """Raised when report generation fails."""

    pass

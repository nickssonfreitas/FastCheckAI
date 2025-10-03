"""Core module - Configuration and exceptions."""

# Import config as namespace module
from src.core import config
from src.core.exceptions import (
    FastCheckAIError,
    ConfigurationError,
    PDFProcessingError,
    AlignmentError,
    LLMError,
    ReportGenerationError,
)

__all__ = [
    # Config module
    "config",
    # Exceptions
    "FastCheckAIError",
    "ConfigurationError",
    "PDFProcessingError",
    "AlignmentError",
    "LLMError",
    "ReportGenerationError",
]

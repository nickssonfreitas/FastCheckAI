"""
Configuration Module for FastCheckAI

This module handles loading and validation of environment variables,
centralized configuration constants, and logging setup.

Example:
    >>> from src.config import OPENAI_API_KEY, MODEL, TEMPERATURE
    >>> print(f"Using model: {MODEL} with temperature: {TEMPERATURE}")
"""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


def get_env_variable(var_name: str, required: bool = True, default: Optional[str] = None) -> str:
    """
    Get environment variable with validation.

    Parameters
    ----------
    var_name : str
        Name of the environment variable
    required : bool, default=True
        Whether this variable is required
    default : str, optional
        Default value if variable is not found (only used if required=False)

    Returns
    -------
    str
        Value of the environment variable

    Raises
    ------
    ConfigurationError
        If required variable is not found

    Examples
    --------
    >>> api_key = get_env_variable("OPENAI_API_KEY")
    >>> log_level = get_env_variable("LOG_LEVEL", required=False, default="INFO")
    """
    value = os.getenv(var_name, default)

    if required and not value:
        raise ConfigurationError(
            f"Required environment variable '{var_name}' is not set. "
            f"Please add it to your .env file."
        )

    return value


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application.

    Parameters
    ----------
    log_level : str, default="INFO"
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file : str, optional
        Path to log file. If None, logs only to console.

    Examples
    --------
    >>> setup_logging(log_level="DEBUG", log_file="logs/fastcheckai.log")
    """
    handlers: list = [logging.StreamHandler()]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


# =============================================================================
# API Configuration
# =============================================================================

OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY")
"""OpenAI API key for GPT-4o access."""

# =============================================================================
# LLM Model Configuration
# =============================================================================

MODEL: str = get_env_variable("MODEL", required=False, default="gpt-4o")
"""LLM model to use for semantic analysis."""

TEMPERATURE: float = float(get_env_variable("TEMPERATURE", required=False, default="0.3"))
"""Temperature for LLM responses (0.0-1.0). Lower = more deterministic."""

MAX_TOKENS: int = int(get_env_variable("MAX_TOKENS", required=False, default="4000"))
"""Maximum tokens per LLM request."""

# =============================================================================
# Pipeline Thresholds
# =============================================================================

FUZZY_MATCH_THRESHOLD: float = float(
    get_env_variable("FUZZY_MATCH_THRESHOLD", required=False, default="0.8")
)
"""Threshold for fuzzy matching section titles (0.0-1.0)."""

SEMANTIC_CONFIDENCE_THRESHOLD: float = float(
    get_env_variable("SEMANTIC_CONFIDENCE_THRESHOLD", required=False, default="0.7")
)
"""Minimum confidence for semantic classification (0.0-1.0)."""

ALIGNMENT_CONFIDENCE_THRESHOLD: float = float(
    get_env_variable("ALIGNMENT_CONFIDENCE_THRESHOLD", required=False, default="0.8")
)
"""Minimum average confidence to accept heuristic alignment (0.0-1.0)."""

# =============================================================================
# Performance Limits
# =============================================================================

MAX_PDF_SIZE_MB: int = int(get_env_variable("MAX_PDF_SIZE_MB", required=False, default="25"))
"""Maximum PDF file size in megabytes."""

MAX_PROCESSING_TIME_SECONDS: int = int(
    get_env_variable("MAX_PROCESSING_TIME_SECONDS", required=False, default="180")
)
"""Maximum processing time for end-to-end pipeline (seconds)."""

# =============================================================================
# OCR Configuration (Feature 3)
# =============================================================================

ENABLE_OCR: bool = get_env_variable("ENABLE_OCR", required=False, default="true").lower() == "true"
"""Enable automatic OCR fallback for corrupted PDFs (requires Tesseract)."""

OCR_CORRUPTION_THRESHOLD: float = float(
    get_env_variable("OCR_CORRUPTION_THRESHOLD", required=False, default="0.30")
)
"""Corruption detection threshold (0.0-1.0). Higher = less sensitive.
Default 0.30 means OCR triggers when >30% of characters are non-ASCII."""

OCR_DPI: int = int(get_env_variable("OCR_DPI", required=False, default="300"))
"""OCR rendering resolution in DPI. Higher = better quality but slower.
Recommended: 300 (standard), 600 (high quality), 150 (fast)."""

# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT: Path = Path(__file__).parent.parent
"""Root directory of the project."""

DATA_DIR: Path = PROJECT_ROOT / "data"
"""Data directory for inputs and outputs."""

INPUT_DIR: Path = DATA_DIR / "inputs"
"""Directory for input PDF files."""

OUTPUT_DIR: Path = DATA_DIR / "outputs"
"""Directory for output results."""

LOGS_DIR: Path = PROJECT_ROOT / "logs"
"""Directory for log files."""

# =============================================================================
# Logging Setup
# =============================================================================

LOG_LEVEL: str = get_env_variable("LOG_LEVEL", required=False, default="INFO")
"""Logging level."""

setup_logging(log_level=LOG_LEVEL, log_file=str(LOGS_DIR / "fastcheckai.log"))

logger = logging.getLogger(__name__)
logger.info("Configuration loaded successfully")
logger.info(f"Model: {MODEL} | Temperature: {TEMPERATURE}")
logger.info(f"Fuzzy Match Threshold: {FUZZY_MATCH_THRESHOLD}")

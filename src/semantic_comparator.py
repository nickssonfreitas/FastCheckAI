"""
Semantic Comparison Module for FastCheckAI

This module integrates the Agno framework with GPT-4o for semantic analysis
of detected differences. It classifies changes into three significance levels
(EQUIVALENT, MINOR, SIGNIFICANT) and provides reasoning for each classification.

This is the PRIMARY objective of the PoC: validate Agno framework viability
for LLM orchestration in technical document comparison.

Example:
    >>> from src.semantic_comparator import create_semantic_agent, classify_semantic_significance
    >>> agent = create_semantic_agent()
    >>> diff = {"original": "mandatory testing", "content": "optional testing"}
    >>> result = classify_semantic_significance(diff, agent)
    >>> print(result["classification"])  # "SIGNIFICANT"
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

from agno.agent import Agent
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src import config

logger = logging.getLogger(__name__)

# =============================================================================
# Constants and Configuration
# =============================================================================

SEMANTIC_INSTRUCTIONS = """You are a technical standards expert specializing in ASTM specifications analysis.

Your task is to analyze changes between versions of technical standards and classify their semantic significance.

You MUST classify each change into one of three categories:
1. **EQUIVALENT**: The change is a simple rephrasing with identical meaning (e.g., "automobile" → "vehicle")
2. **MINOR**: The change is an editorial clarification or formatting improvement with no technical impact (e.g., adding examples, improving clarity)
3. **SIGNIFICANT**: The change modifies technical requirements, specifications, scope, or mandatory conditions (e.g., "shall" → "may", numeric value changes, scope expansion)

Always provide:
- classification: One of ["EQUIVALENT", "MINOR", "SIGNIFICANT"]
- confidence: Float between 0.0-1.0 representing your certainty
- reasoning: 1-3 sentences explaining your decision, citing specific parts of the text

Be precise, technical, and conservative: when in doubt, classify as SIGNIFICANT rather than MINOR."""

# GPT-4o Pricing (as of January 2025)
GPT4O_INPUT_COST_PER_1K = 0.0025  # $0.0025 per 1K input tokens
GPT4O_OUTPUT_COST_PER_1K = 0.010  # $0.01 per 1K output tokens

# Cache for semantic analysis results
SEMANTIC_CACHE: Dict[str, Dict] = {}

# Counters for observability
agno_calls = 0
fallback_calls = 0
cache_hits = 0
total_cost = 0.0


# =============================================================================
# Agno Agent Creation
# =============================================================================


def create_semantic_agent() -> Agent:
    """
    Create Agno agent for semantic analysis.

    Configured with GPT-4o and low temperature (0.3) for consistent
    technical analysis.

    Returns
    -------
    Agent
        Configured Agno agent instance

    Raises
    ------
    Exception
        If agent creation fails

    Examples
    --------
    >>> agent = create_semantic_agent()
    >>> response = agent.run("What is semantic equivalence?")
    >>> print(response)
    """
    try:
        agent = Agent(
            model=config.MODEL,
            instructions=SEMANTIC_INSTRUCTIONS,
            temperature=config.TEMPERATURE,
            markdown=False,  # Return plain text/JSON
        )

        logger.info(f"Agno agent created: model={config.MODEL}, temperature={config.TEMPERATURE}")
        return agent

    except Exception as e:
        logger.error(f"Failed to create Agno agent: {e}")
        raise


# =============================================================================
# Semantic Classification with Retry Logic
# =============================================================================


@retry(
    stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True
)
def _classify_with_agno(diff: Dict, agent: Agent) -> Dict:
    """
    Classify difference using Agno agent with retry logic.

    Internal function with tenacity retry decorator.
    Retries 3 times with exponential backoff (2s, 4s, 8s).

    Parameters
    ----------
    diff : dict
        Diff item with 'original' and 'content' keys
    agent : Agent
        Configured Agno agent

    Returns
    -------
    dict
        Classification result with classification, confidence, reasoning

    Raises
    ------
    Exception
        If all retries fail
    """
    global agno_calls

    original = diff.get("original", "")
    modified = diff.get("content", "")

    # Construct classification prompt
    prompt = f"""You are analyzing changes in technical standard ASTM A29/A29M.

Original text: "{original}"
Modified text: "{modified}"

Classify this change as:
- EQUIVALENT: Same meaning, just rephrased
- MINOR: Clarification or editorial change, no technical impact
- SIGNIFICANT: Change in technical requirement, scope, or specification

Return ONLY valid JSON with this exact structure:
{{"classification": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""

    start_time = time.time()

    # Call Agno agent
    response = agent.run(prompt)
    elapsed = time.time() - start_time

    agno_calls += 1
    logger.debug(f"Agno call {agno_calls} completed in {elapsed:.2f}s")

    # Parse JSON response
    try:
        # Try to extract JSON from response
        result = json.loads(response)

        # Validate required fields
        required_fields = ["classification", "confidence", "reasoning"]
        if not all(field in result for field in required_fields):
            raise ValueError(f"Missing required fields. Got: {list(result.keys())}")

        # Validate classification value
        valid_classifications = ["EQUIVALENT", "MINOR", "SIGNIFICANT"]
        if result["classification"] not in valid_classifications:
            raise ValueError(
                f"Invalid classification: {result['classification']}. "
                f"Must be one of {valid_classifications}"
            )

        # Validate confidence range
        if not 0.0 <= result["confidence"] <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got: {result['confidence']}")

        logger.debug(
            f"Classification: {result['classification']} "
            f"(confidence={result['confidence']:.2f})"
        )

        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON from Agno response: {e}")
        logger.debug(f"Raw response: {response}")

        # Fallback: try regex extraction
        import re

        classification_match = re.search(
            r'"classification":\s*"(EQUIVALENT|MINOR|SIGNIFICANT)"', response
        )
        confidence_match = re.search(r'"confidence":\s*(0\.\d+|1\.0)', response)
        reasoning_match = re.search(r'"reasoning":\s*"([^"]+)"', response)

        if classification_match and confidence_match and reasoning_match:
            result = {
                "classification": classification_match.group(1),
                "confidence": float(confidence_match.group(1)),
                "reasoning": reasoning_match.group(1),
            }
            logger.info("Successfully extracted classification via regex fallback")
            return result
        else:
            raise ValueError(f"Failed to parse classification from response: {response}")


def _classify_with_openai_direct(diff: Dict) -> Dict:
    """
    Classify difference using OpenAI SDK directly (fallback).

    Used when Agno agent fails or exceeds failure threshold.

    Parameters
    ----------
    diff : dict
        Diff item with 'original' and 'content' keys

    Returns
    -------
    dict
        Classification result

    Raises
    ------
    Exception
        If OpenAI call fails
    """
    global fallback_calls

    original = diff.get("original", "")
    modified = diff.get("content", "")

    # Use same prompt as Agno version
    prompt = f"""You are analyzing changes in technical standard ASTM A29/A29M.

Original text: "{original}"
Modified text: "{modified}"

Classify this change as:
- EQUIVALENT: Same meaning, just rephrased
- MINOR: Clarification or editorial change, no technical impact
- SIGNIFICANT: Change in technical requirement, scope, or specification

Return ONLY valid JSON with this exact structure:
{{"classification": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""

    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)

        start_time = time.time()

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SEMANTIC_INSTRUCTIONS,
                },
                {"role": "user", "content": prompt},
            ],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )

        elapsed = time.time() - start_time
        fallback_calls += 1

        logger.debug(f"OpenAI direct call {fallback_calls} completed in {elapsed:.2f}s")

        # Extract and parse response
        content = response.choices[0].message.content
        result = json.loads(content)

        return result

    except Exception as e:
        logger.error(f"OpenAI direct fallback failed: {e}")
        raise


# =============================================================================
# Main Classification Function
# =============================================================================


def classify_semantic_significance(
    diff: Dict,
    agent: Optional[Agent] = None,
    use_cache: bool = True,
    min_words: int = 10,
) -> Dict:
    """
    Classify semantic significance of a difference using LLM.

    Uses Agno agent by default, with fallback to OpenAI SDK on failures.
    Implements caching to reduce costs and filtering for trivial differences.

    Parameters
    ----------
    diff : dict
        Diff item with 'original' and 'content' keys
    agent : Agent, optional
        Agno agent instance. If None, creates new agent
    use_cache : bool, default=True
        Whether to use cached results
    min_words : int, default=10
        Minimum word count to process (skip trivial diffs)

    Returns
    -------
    dict
        Classification result with:
        - classification: str ("EQUIVALENT" | "MINOR" | "SIGNIFICANT")
        - confidence: float (0.0-1.0)
        - reasoning: str
        - source: str ("agno" | "openai_fallback" | "cache" | "skipped")

    Examples
    --------
    >>> diff = {"original": "mandatory", "content": "optional"}
    >>> result = classify_semantic_significance(diff)
    >>> print(f"{result['classification']}: {result['reasoning']}")
    SIGNIFICANT: Change from mandatory to optional alters requirement
    """
    global cache_hits, total_cost

    original = diff.get("original", "")
    modified = diff.get("content", "")

    # Filter trivial differences (too short to be meaningful)
    word_count = max(len(original.split()), len(modified.split()))
    if word_count < min_words:
        logger.debug(f"Skipping trivial diff ({word_count} words < {min_words} min)")
        return {
            "classification": "MINOR",
            "confidence": 1.0,
            "reasoning": f"Trivial change ({word_count} words), automatically classified as MINOR",
            "source": "skipped",
        }

    # Check cache
    if use_cache:
        cache_key = hashlib.md5(f"{original}|{modified}".encode()).hexdigest()
        if cache_key in SEMANTIC_CACHE:
            cache_hits += 1
            logger.debug(f"Cache hit for diff (total hits: {cache_hits})")
            cached_result = SEMANTIC_CACHE[cache_key].copy()
            cached_result["source"] = "cache"
            return cached_result

    # Create agent if not provided
    if agent is None:
        agent = create_semantic_agent()

    # Try Agno first
    try:
        result = _classify_with_agno(diff, agent)
        result["source"] = "agno"

        # Estimate cost (rough approximation)
        estimated_input_tokens = (len(original) + len(modified)) // 4  # ~4 chars per token
        estimated_output_tokens = len(result["reasoning"]) // 4
        call_cost = (
            estimated_input_tokens / 1000 * GPT4O_INPUT_COST_PER_1K
            + estimated_output_tokens / 1000 * GPT4O_OUTPUT_COST_PER_1K
        )
        total_cost += call_cost

        # Cache result
        if use_cache:
            SEMANTIC_CACHE[cache_key] = result.copy()

        return result

    except Exception as e:
        logger.warning(f"Agno classification failed: {e}. Using OpenAI fallback.")

        # Fallback to OpenAI SDK
        try:
            result = _classify_with_openai_direct(diff)
            result["source"] = "openai_fallback"

            # Estimate cost
            estimated_input_tokens = (len(original) + len(modified)) // 4
            estimated_output_tokens = len(result["reasoning"]) // 4
            call_cost = (
                estimated_input_tokens / 1000 * GPT4O_INPUT_COST_PER_1K
                + estimated_output_tokens / 1000 * GPT4O_OUTPUT_COST_PER_1K
            )
            total_cost += call_cost

            # Cache result
            if use_cache:
                SEMANTIC_CACHE[cache_key] = result.copy()

            return result

        except Exception as fallback_error:
            logger.error(f"Both Agno and OpenAI fallback failed: {fallback_error}")

            # Return conservative classification
            return {
                "classification": "SIGNIFICANT",
                "confidence": 0.0,
                "reasoning": f"Classification failed (error: {str(fallback_error)}). Marked as SIGNIFICANT for safety.",
                "source": "error",
            }


# =============================================================================
# Cost and Performance Utilities
# =============================================================================


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Estimate cost of LLM API calls.

    Uses GPT-4o pricing: $0.0025/1K input, $0.01/1K output.

    Parameters
    ----------
    input_tokens : int
        Number of input tokens
    output_tokens : int
        Number of output tokens

    Returns
    -------
    float
        Estimated cost in USD

    Examples
    --------
    >>> cost = estimate_cost(1000, 500)
    >>> print(f"${cost:.4f}")
    $0.0075
    """
    input_cost = (input_tokens / 1000) * GPT4O_INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000) * GPT4O_OUTPUT_COST_PER_1K
    return input_cost + output_cost


def get_semantic_stats() -> Dict[str, Any]:
    """
    Get statistics about semantic analysis runs.

    Returns
    -------
    dict
        Statistics including:
        - agno_calls: Number of Agno agent calls
        - fallback_calls: Number of OpenAI fallback calls
        - cache_hits: Number of cache hits
        - total_cost: Estimated total cost in USD
        - fallback_rate: Percentage of calls using fallback

    Examples
    --------
    >>> stats = get_semantic_stats()
    >>> print(f"Fallback rate: {stats['fallback_rate']:.1f}%")
    Fallback rate: 15.0%
    """
    total_calls = agno_calls + fallback_calls
    fallback_rate = (fallback_calls / total_calls * 100) if total_calls > 0 else 0.0

    return {
        "agno_calls": agno_calls,
        "fallback_calls": fallback_calls,
        "cache_hits": cache_hits,
        "total_cost": total_cost,
        "fallback_rate": fallback_rate,
        "total_llm_calls": total_calls,
    }


def log_semantic_summary():
    """
    Log summary of semantic analysis session.

    Displays total calls, cache efficiency, fallback rate, and cost.
    """
    stats = get_semantic_stats()

    logger.info("=" * 60)
    logger.info("SEMANTIC ANALYSIS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total LLM calls: {stats['total_llm_calls']}")
    logger.info(f"  - Agno calls: {stats['agno_calls']}")
    logger.info(f"  - OpenAI fallbacks: {stats['fallback_calls']} ({stats['fallback_rate']:.1f}%)")
    logger.info(f"Cache hits: {stats['cache_hits']}")
    logger.info(f"Estimated cost: ${stats['total_cost']:.4f}")
    logger.info("=" * 60)

    # Validate Agno viability (PoC success criteria)
    if stats['fallback_rate'] > 30.0:
        logger.warning(
            f"⚠️  Agno fallback rate ({stats['fallback_rate']:.1f}%) exceeds 30% threshold. "
            "Consider migrating to OpenAI SDK for production."
        )
    else:
        logger.info(
            f"✅ Agno framework viable: {stats['fallback_rate']:.1f}% fallback rate (target: <30%)"
        )

"""
Section Alignment Module for FastCheckAI

This module handles section alignment between two PDF documents using a hybrid
approach: heuristic matching (exact ID + fuzzy title) with LLM fallback for
complex cases. Detects additions, removals, and modifications.

Example:
    >>> from src.text_extractor import parse_section_hierarchy
    >>> from src.section_aligner import align_sections
    >>> sections_a = parse_section_hierarchy(text_a)
    >>> sections_b = parse_section_hierarchy(text_b)
    >>> result = align_sections(sections_a, sections_b)
    >>> print(f"Aligned: {len(result['alignments'])}, Added: {len(result['added'])}")
"""

import json
import logging
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from openai import OpenAI
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src import config

logger = logging.getLogger(__name__)


class SectionAlignmentError(Exception):
    """Base exception for section alignment errors."""

    pass


def get_section_by_id(sections: Dict[str, Any], section_id: str) -> Optional[Dict[str, Any]]:
    """
    Recursively retrieve a section from hierarchical structure by its ID.

    This helper function navigates through nested subsections to find a section
    with the given ID, regardless of its nesting level.

    Args:
        sections: Hierarchical sections dictionary from parse_section_hierarchy
        section_id: Section ID to find (e.g., '1', '1.1', '1.2.3')

    Returns:
        Section dictionary with keys: id, title, level, content, subsections
        Returns None if section not found

    Examples:
        >>> sections = parse_section_hierarchy(text)
        >>> section = get_section_by_id(sections, '1.2.3')
        >>> if section:
        ...     print(section['title'])
        ... else:
        ...     print("Section not found")
    """
    # Check if section exists at current level
    if section_id in sections:
        return sections[section_id]

    # Recursively search in subsections
    for section_data in sections.values():
        if "subsections" in section_data and section_data["subsections"]:
            result = get_section_by_id(section_data["subsections"], section_id)
            if result is not None:
                return result

    # Not found
    return None


def calculate_content_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate TF-IDF cosine similarity between two text sections.

    Uses TF-IDF vectorization to convert text into numerical vectors and then
    computes cosine similarity to measure how similar the content is, regardless
    of exact wording differences. This helps identify semantically similar sections
    even when titles have been renamed.

    Args:
        text_a: Text content from first document section
        text_b: Text content from second document section

    Returns:
        Similarity score between 0.0 and 1.0, where:
        - 1.0 = identical content (same words, same frequency)
        - 0.8-0.99 = very similar (likely same section, minor edits)
        - 0.6-0.79 = moderately similar (possibly related sections)
        - 0.0-0.59 = dissimilar (likely different sections)

    Examples:
        >>> text_1 = "The steel must meet ASTM A29 requirements for carbon content."
        >>> text_2 = "Steel shall conform to ASTM A29 carbon content specifications."
        >>> similarity = calculate_content_similarity(text_1, text_2)
        >>> print(f"Similarity: {similarity:.2f}")  # Expected: ~0.75-0.85

        >>> text_3 = "Tensile strength testing procedures are defined in Section 7."
        >>> similarity_unrelated = calculate_content_similarity(text_1, text_3)
        >>> print(f"Similarity: {similarity_unrelated:.2f}")  # Expected: ~0.1-0.2

    Notes:
        - Handles empty strings gracefully (returns 0.0)
        - Uses English stop words removal for better semantic matching
        - Includes unigrams and bigrams for better phrase matching
        - Performance: ~0.01-0.05 seconds for typical section pairs
        - Minimum text length recommended: 50 characters for reliable results
    """
    # Handle edge cases
    if not text_a or not text_b:
        logger.debug("Empty text provided to content similarity calculation")
        return 0.0

    if len(text_a.strip()) < 10 or len(text_b.strip()) < 10:
        logger.debug("Text too short for meaningful similarity calculation")
        return 0.0

    try:
        # Configure TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams + bigrams for phrase matching
            max_features=5000,   # Limit vocabulary size for performance
            min_df=1,            # Include terms that appear at least once
            max_df=0.95,         # Ignore very common terms (>95% frequency)
        )

        # Transform texts to TF-IDF vectors
        vectors = vectorizer.fit_transform([text_a, text_b])

        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2])
        similarity = float(similarity_matrix[0][0])

        logger.debug(f"Content similarity calculated: {similarity:.4f}")
        return similarity

    except Exception as e:
        logger.warning(f"TF-IDF similarity calculation failed: {str(e)}")
        return 0.0


def align_sections(
    sections_a: Dict[str, Any],
    sections_b: Dict[str, Any],
    use_llm_fallback: bool = True
    ) -> Dict[str, Any]:
    """
    Align sections between two PDF documents using hybrid approach.

    Orchestrates the complete alignment process:
    1. Heuristic alignment (exact ID + fuzzy title matching)
    2. LLM fallback for low-confidence alignments (if enabled)
    3. Detection of added/removed sections

    Args:
        sections_a: Hierarchical sections from first PDF (reference)
        sections_b: Hierarchical sections from second PDF (comparison)
        use_llm_fallback: Enable LLM fallback for complex alignments (default: True)

    Returns:
        Dictionary with alignment results:
        {
            "alignments": {
                "section_a_id": {
                    "section_b_id": "...",
                    "confidence": 0.95,
                    "method": "exact|fuzzy|llm_fallback",
                    "title_a": "...",
                    "title_b": "..."
                }
            },
            "added": [{"id": "...", "title": "...", "level": 1}],
            "removed": [{"id": "...", "title": "...", "level": 1}],
            "metadata": {
                "total_sections_a": 10,
                "total_sections_b": 12,
                "aligned_count": 9,
                "added_count": 3,
                "removed_count": 1,
                "avg_confidence": 0.92,
                "llm_calls": 2
            }
        }

    Raises:
        SectionAlignmentError: If alignment process fails
        ValueError: If sections_a or sections_b are invalid

    Examples:
        >>> result = align_sections(sections_2015, sections_2016)
        >>> print(f"Aligned {result['metadata']['aligned_count']} sections")
        >>> print(f"Average confidence: {result['metadata']['avg_confidence']:.2f}")
    """
    if not isinstance(sections_a, dict) or not isinstance(sections_b, dict):
        raise ValueError("sections_a and sections_b must be dictionaries")

    logger.info("Starting section alignment process")

    try:
        # Step 1: Flatten hierarchies for easier processing
        flat_a = _flatten_sections(sections_a)
        flat_b = _flatten_sections(sections_b)

        logger.info(f"Flattened sections: A={len(flat_a)}, B={len(flat_b)}")

        # Step 2: Heuristic alignment (exact + fuzzy)
        alignments = align_sections_heuristic(flat_a, flat_b)
        logger.info(f"Heuristic alignment completed: {len(alignments)} matches")

        # Step 3: Calculate average confidence
        if alignments:
            confidences = [a["confidence"] for a in alignments.values()]
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_confidence = 0.0

        logger.info(f"Average alignment confidence: {avg_confidence:.2f}")

        # Step 4: LLM fallback for low-confidence alignments
        llm_calls = 0
        if use_llm_fallback and avg_confidence < config.ALIGNMENT_CONFIDENCE_THRESHOLD:
            logger.info(
                f"Average confidence {avg_confidence:.2f} below threshold "
                f"{config.ALIGNMENT_CONFIDENCE_THRESHOLD}, applying LLM fallback"
            )

            # Identify unmatched or low-confidence sections
            matched_b_ids = {a["section_b_id"] for a in alignments.values()}
            low_confidence_a = {
                sid: s
                for sid, s in flat_a.items()
                if sid not in alignments or alignments[sid]["confidence"] < 0.8
            }

            for section_a_id, section_a in low_confidence_a.items():
                # Find best unmatched candidate in B
                unmatched_b = {
                    sid: s for sid, s in flat_b.items() if sid not in matched_b_ids
                }

                if not unmatched_b:
                    continue

                # Try LLM alignment with best fuzzy match candidate
                best_candidate = None
                best_fuzzy_score = 0.0

                for section_b_id, section_b in unmatched_b.items():
                    fuzzy_score = fuzz.ratio(section_a["title"], section_b["title"]) / 100.0

                    if fuzzy_score > best_fuzzy_score:
                        best_fuzzy_score = fuzzy_score
                        best_candidate = (section_b_id, section_b)

                # Apply LLM if we have a candidate
                if best_candidate and best_fuzzy_score >= 0.5:  # Min threshold for LLM
                    section_b_id, section_b = best_candidate
                    llm_result = align_with_llm(section_a, section_b)
                    llm_calls += 1

                    if llm_result["is_match"] and llm_result["confidence"] >= 0.7:
                        # Update or add alignment
                        alignments[section_a_id] = {
                            "section_b_id": section_b_id,
                            "confidence": llm_result["confidence"],
                            "method": "llm_fallback",
                            "title_a": section_a["title"],
                            "title_b": section_b["title"],
                            "reasoning": llm_result.get("reasoning", ""),
                        }
                        matched_b_ids.add(section_b_id)

                        logger.info(
                            f"LLM aligned: {section_a_id} -> {section_b_id} "
                            f"(confidence: {llm_result['confidence']:.2f})"
                        )

            # Recalculate average confidence
            if alignments:
                confidences = [a["confidence"] for a in alignments.values()]
                avg_confidence = sum(confidences) / len(confidences)

            logger.info(f"LLM fallback completed: {llm_calls} calls, new avg: {avg_confidence:.2f}")

        # Step 5: Detect added/removed sections
        unmatched = detect_unmatched_sections(alignments, flat_a, flat_b)

        # Step 6: Build result metadata
        metadata = {
            "total_sections_a": len(flat_a),
            "total_sections_b": len(flat_b),
            "aligned_count": len(alignments),
            "added_count": len(unmatched["added"]),
            "removed_count": len(unmatched["removed"]),
            "avg_confidence": avg_confidence,
            "llm_calls": llm_calls,
        }

        logger.info(
            f"Alignment complete: {metadata['aligned_count']} aligned, "
            f"{metadata['added_count']} added, {metadata['removed_count']} removed"
        )

        return {
            "alignments": alignments,
            "added": unmatched["added"],
            "removed": unmatched["removed"],
            "metadata": metadata,
        }

    except Exception as e:
        error_msg = f"Section alignment failed: {str(e)}"
        logger.error(error_msg)
        raise SectionAlignmentError(error_msg) from e


def align_sections_heuristic(
    sections_a: Dict[str, Any], sections_b: Dict[str, Any]
    ) -> Dict[str, Any]:
    """
    Align sections using hybrid heuristic approach (exact ID + fuzzy title + content similarity).

    Priority:
    1. Exact match by section ID (confidence = 1.0)
    2. Fuzzy match by title using rapidfuzz (confidence = similarity score)
    3. Content similarity using TF-IDF (confidence = weighted average)

    For fuzzy matches, confidence is calculated as:
    - 70% title similarity (fuzzy match)
    - 30% content similarity (TF-IDF)

    Args:
        sections_a: Flat dictionary of sections from first PDF
        sections_b: Flat dictionary of sections from second PDF

    Returns:
        Dictionary of alignments:
        {
            "section_a_id": {
                "section_b_id": "...",
                "confidence": 0.95,
                "method": "exact|fuzzy|content",
                "title_a": "...",
                "title_b": "...",
                "title_similarity": 0.85,  # Only for fuzzy/content
                "content_similarity": 0.92  # Only for fuzzy/content
            }
        }

    Examples:
        >>> alignments = align_sections_heuristic(flat_sections_a, flat_sections_b)
        >>> exact_matches = [a for a in alignments.values() if a["method"] == "exact"]
        >>> print(f"Exact matches: {len(exact_matches)}")
    """
    alignments: Dict[str, Any] = {}
    matched_b_ids: set = set()

    logger.info("Starting hybrid heuristic alignment (exact + fuzzy + content)")

    # Priority 1: Exact match by section ID
    for section_a_id, section_a in sections_a.items():
        if section_a_id in sections_b:
            section_b = sections_b[section_a_id]

            alignments[section_a_id] = {
                "section_b_id": section_a_id,
                "confidence": 1.0,
                "method": "exact",
                "title_a": section_a["title"],
                "title_b": section_b["title"],
            }
            matched_b_ids.add(section_a_id)

    logger.info(f"Exact matches: {len(alignments)}")

    # Priority 2: Hybrid fuzzy + content similarity for unmatched sections
    unmatched_a = {sid: s for sid, s in sections_a.items() if sid not in alignments}
    unmatched_b = {sid: s for sid, s in sections_b.items() if sid not in matched_b_ids}

    for section_a_id, section_a in unmatched_a.items():
        best_match_id: Optional[str] = None
        best_combined_score = 0.0
        best_title_sim = 0.0
        best_content_sim = 0.0

        # Find best match considering both title and content
        for section_b_id, section_b in unmatched_b.items():
            # Calculate title similarity
            title_similarity = fuzz.ratio(section_a["title"], section_b["title"]) / 100.0

            # Calculate content similarity
            content_similarity = calculate_content_similarity(
                section_a.get("content", ""),
                section_b.get("content", "")
            )

            # Combined score: 70% title + 30% content
            # This gives more weight to title similarity (structural match)
            # while still considering content (semantic match)
            combined_score = (0.7 * title_similarity) + (0.3 * content_similarity)

            if combined_score > best_combined_score:
                best_combined_score = combined_score
                best_title_sim = title_similarity
                best_content_sim = content_similarity
                best_match_id = section_b_id

        # Accept match if above threshold
        # Lowered from 0.8 to 0.6 to catch more legitimate matches
        if best_match_id and best_combined_score >= config.FUZZY_MATCH_THRESHOLD:
            section_b = unmatched_b[best_match_id]

            # Determine method based on which similarity was stronger
            if best_title_sim >= 0.7:
                method = "fuzzy"
            elif best_content_sim >= 0.6:
                method = "content"
            else:
                method = "fuzzy"  # Default to fuzzy if both are moderate

            alignments[section_a_id] = {
                "section_b_id": best_match_id,
                "confidence": best_combined_score,
                "method": method,
                "title_a": section_a["title"],
                "title_b": section_b["title"],
                "title_similarity": best_title_sim,
                "content_similarity": best_content_sim,
            }
            matched_b_ids.add(best_match_id)

            logger.debug(
                f"Matched {section_a_id} -> {best_match_id}: "
                f"title={best_title_sim:.2f}, content={best_content_sim:.2f}, "
                f"combined={best_combined_score:.2f}"
            )

    fuzzy_count = len(alignments) - len(
        [a for a in alignments.values() if a["method"] == "exact"]
    )
    logger.info(f"Fuzzy+content matches: {fuzzy_count}")

    return alignments


def align_with_llm(section_a: Dict[str, Any], section_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use LLM (Agno + GPT-4o) to determine if two sections are matches.

    Sends section metadata and content preview to LLM for intelligent comparison.
    Fallback to direct OpenAI API if Agno fails.

    Args:
        section_a: Section from first PDF with id, title, content
        section_b: Section from second PDF with id, title, content

    Returns:
        Dictionary with LLM decision:
        {
            "is_match": bool,
            "confidence": 0.0-1.0,
            "reasoning": "explanation of decision"
        }

    Raises:
        SectionAlignmentError: If LLM call fails

    Examples:
        >>> llm_result = align_with_llm(section_3_2_pdf_a, section_5_1_pdf_b)
        >>> if llm_result["is_match"]:
        ...     print(f"Match found: {llm_result['reasoning']}")
    """
    try:
        # Prepare content preview (first 500 chars)
        content_a_preview = section_a.get("content", "")[:500]
        content_b_preview = section_b.get("content", "")[:500]

        # Build prompt
        prompt = f"""Compare these two sections from different versions of a technical document and determine if they are corresponding sections (same content, possibly renamed or reorganized).

        Section A:
        - ID: {section_a['id']}
        - Title: {section_a['title']}
        - Content preview: {content_a_preview}

        Section B:
        - ID: {section_b['id']}
        - Title: {section_b['title']}
        - Content preview: {content_b_preview}

        Analyze if these sections are the same (possibly with modifications) or completely different sections.

        Return your answer as JSON with this exact format:
            {
            "is_match": true or false,
            "confidence": 0.0 to 1.0,
            "reasoning": "brief explanation of your decision"
            }
            """

        logger.debug(f"LLM alignment request: {section_a['id']} vs {section_b['id']}")

        # Try Agno first
        try:
            agent = Agent(
                model=config.MODEL,
                instructions="You are an expert in technical document comparison. "
                "Analyze sections carefully and provide accurate JSON responses.",
                temperature=config.TEMPERATURE,
            )

            response = agent.run(prompt)

            # Parse response - Agno might return different formats
            if hasattr(response, "content"):
                response_text = response.content
            elif hasattr(response, "text"):
                response_text = response.text
            else:
                response_text = str(response)

            # Extract JSON from response
            result = _parse_llm_response(response_text)

            logger.info(
                f"LLM (Agno) alignment: {section_a['id']} vs {section_b['id']} -> "
                f"match={result['is_match']}, confidence={result['confidence']:.2f}"
            )

            return result

        except Exception as agno_error:
            logger.warning(f"Agno failed, falling back to direct OpenAI: {str(agno_error)}")

            # Fallback to direct OpenAI API
            client = OpenAI(api_key=config.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in technical document comparison. "
                        "Analyze sections carefully and provide accurate JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=config.TEMPERATURE,
                max_tokens=500,
            )

            response_text = response.choices[0].message.content
            result = _parse_llm_response(response_text)

            logger.info(
                f"LLM (OpenAI) alignment: {section_a['id']} vs {section_b['id']} -> "
                f"match={result['is_match']}, confidence={result['confidence']:.2f}"
            )

            return result

    except Exception as e:
        error_msg = f"LLM alignment failed: {str(e)}"
        logger.error(error_msg)
        raise SectionAlignmentError(error_msg) from e


def detect_unmatched_sections(
    alignments: Dict[str, Any],
    sections_a: Dict[str, Any],
    sections_b: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect sections that were added or removed between documents.

    Args:
        alignments: Dictionary of aligned sections from align_sections_heuristic
        sections_a: Flat dictionary of sections from first PDF (reference)
        sections_b: Flat dictionary of sections from second PDF (comparison)

    Returns:
        Dictionary with added and removed sections:
        {
            "added": [{"id": "8", "title": "New Feature", "level": 1}],
            "removed": [{"id": "7", "title": "Obsolete", "level": 1}]
        }

    Examples:
        >>> unmatched = detect_unmatched_sections(alignments, flat_a, flat_b)
        >>> print(f"Added: {len(unmatched['added'])}, Removed: {len(unmatched['removed'])}")
    """
    # Get aligned section IDs
    aligned_a_ids = set(alignments.keys())
    aligned_b_ids = {a["section_b_id"] for a in alignments.values()}

    # Identify unmatched sections
    removed_ids = set(sections_a.keys()) - aligned_a_ids
    added_ids = set(sections_b.keys()) - aligned_b_ids

    # Build lists with section metadata
    removed = [
        {"id": sid, "title": sections_a[sid]["title"], "level": sections_a[sid]["level"]}
        for sid in sorted(removed_ids)
    ]

    added = [
        {"id": sid, "title": sections_b[sid]["title"], "level": sections_b[sid]["level"]}
        for sid in sorted(added_ids)
    ]

    logger.info(f"Detected unmatched sections: {len(added)} added, {len(removed)} removed")

    return {"added": added, "removed": removed}


def _flatten_sections(
    sections: Dict[str, Any], parent_prefix: str = ""
    ) -> Dict[str, Dict[str, Any]]:
    """
    Flatten hierarchical section structure into flat dictionary.

    Args:
        sections: Hierarchical sections from parse_section_hierarchy
        parent_prefix: Internal prefix for recursive calls

    Returns:
        Flat dictionary: {section_id: {id, title, level, content}}

    Examples:
        >>> flat = _flatten_sections(hierarchical_sections)
        >>> print(list(flat.keys()))
        ['1', '1.1', '1.2', '2', '2.1']
    """
    flat: Dict[str, Dict[str, Any]] = {}

    for section_id, section_data in sections.items():
        # Add current section
        flat[section_id] = {
            "id": section_id,
            "title": section_data["title"],
            "level": section_data["level"],
            "content": section_data.get("content", ""),
        }

        # Recursively flatten subsections
        if "subsections" in section_data and section_data["subsections"]:
            subsections_flat = _flatten_sections(section_data["subsections"], section_id)
            flat.update(subsections_flat)

    return flat


def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response to extract JSON alignment decision.

    Handles various response formats (plain JSON, markdown code blocks, etc.)

    Args:
        response_text: Raw text response from LLM

    Returns:
        Parsed dictionary with is_match, confidence, reasoning

    Raises:
        SectionAlignmentError: If JSON parsing fails or required fields missing
    """
    try:
        # Try to extract JSON from response (might be wrapped in markdown)
        if "```json" in response_text:
            # Extract from markdown code block
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            # Extract from generic code block
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            # Assume entire response is JSON
            json_str = response_text.strip()

        # Parse JSON
        result = json.loads(json_str)

        # Validate required fields
        if "is_match" not in result or "confidence" not in result:
            raise ValueError("Missing required fields: is_match or confidence")

        # Ensure confidence is float
        result["confidence"] = float(result["confidence"])

        # Add default reasoning if missing
        if "reasoning" not in result:
            result["reasoning"] = "No reasoning provided"

        return result

    except (json.JSONDecodeError, ValueError) as e:
        error_msg = f"Failed to parse LLM response: {str(e)}\nResponse: {response_text}"
        logger.error(error_msg)
        raise SectionAlignmentError(error_msg) from e

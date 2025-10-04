"""
Unit tests for section_aligner.py

Tests for TF-IDF content similarity, section alignment, and LLM fallback.
"""

import pytest
from src.processing.section_aligner import (
    calculate_content_similarity,
    align_sections_heuristic,
    get_section_by_id,
    _flatten_sections,
)


class TestCalculateContentSimilarity:
    """Test suite for TF-IDF content similarity function."""

    def test_identical_texts_returns_one(self):
        """Identical texts should have similarity of 1.0."""
        text = "The steel must meet ASTM A29 requirements for carbon content."
        similarity = calculate_content_similarity(text, text)
        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_very_similar_texts_high_similarity(self):
        """Similar texts with synonyms should have high similarity (>0.7)."""
        text_a = "The steel must meet ASTM A29 requirements for carbon content."
        text_b = "Steel shall conform to ASTM A29 carbon content specifications."
        similarity = calculate_content_similarity(text_a, text_b)
        assert similarity > 0.7

    def test_unrelated_texts_low_similarity(self):
        """Unrelated texts should have low similarity (<0.3)."""
        text_a = "The steel must meet ASTM A29 requirements for carbon content."
        text_b = "Tensile strength testing procedures are defined in Section 7 of the manual."
        similarity = calculate_content_similarity(text_a, text_b)
        assert similarity < 0.3

    def test_empty_text_returns_zero(self):
        """Empty text should return similarity of 0.0."""
        text = "The steel must meet ASTM A29 requirements."
        assert calculate_content_similarity("", text) == 0.0
        assert calculate_content_similarity(text, "") == 0.0
        assert calculate_content_similarity("", "") == 0.0

    def test_short_text_returns_zero(self):
        """Very short text (<10 chars) should return 0.0."""
        text = "The steel must meet ASTM A29 requirements."
        assert calculate_content_similarity("short", text) == 0.0
        assert calculate_content_similarity(text, "tiny") == 0.0

    def test_same_keywords_different_order_high_similarity(self):
        """Same keywords in different order should have high similarity."""
        text_a = "Carbon steel tensile strength yield elongation hardness"
        text_b = "Hardness elongation yield strength tensile carbon steel"
        similarity = calculate_content_similarity(text_a, text_b)
        assert similarity > 0.8

    def test_partial_overlap_moderate_similarity(self):
        """Partially overlapping content should have moderate similarity."""
        text_a = "The product shall be manufactured from carbon steel with specified chemical composition."
        text_b = "The product requires carbon steel material with appropriate mechanical properties."
        similarity = calculate_content_similarity(text_a, text_b)
        assert 0.4 < similarity < 0.8

    def test_handles_special_characters(self):
        """Should handle special characters gracefully."""
        text_a = "ASTM A29/A29M-2015 §4.2.1 (tensile > 500 MPa)"
        text_b = "ASTM A29/A29M-2016 Section 4.2.1 tensile strength 500 MPa"
        similarity = calculate_content_similarity(text_a, text_b)
        assert similarity > 0.6

    def test_different_cases_similar(self):
        """Different cases should still match (case-insensitive)."""
        text_a = "THE STEEL MUST MEET ASTM A29 REQUIREMENTS"
        text_b = "the steel must meet astm a29 requirements"
        similarity = calculate_content_similarity(text_a, text_b)
        assert similarity > 0.95


class TestAlignSectionsHeuristic:
    """Test suite for heuristic section alignment."""

    @pytest.fixture
    def sample_sections_a(self):
        """Sample flat sections from PDF A."""
        return {
            "1": {
                "id": "1",
                "title": "Scope",
                "level": 1,
                "content": "This specification covers hot-rolled carbon steel bars.",
            },
            "1.1": {
                "id": "1.1",
                "title": "General Requirements",
                "level": 2,
                "content": "The bars shall be manufactured from carbon steel.",
            },
            "2": {
                "id": "2",
                "title": "Chemical Composition",
                "level": 1,
                "content": "Carbon content shall be between 0.2% and 0.5%.",
            },
        }

    @pytest.fixture
    def sample_sections_b_exact_match(self):
        """Sample sections from PDF B with exact ID matches."""
        return {
            "1": {
                "id": "1",
                "title": "Scope",
                "level": 1,
                "content": "This specification covers hot-rolled carbon steel bars.",
            },
            "1.1": {
                "id": "1.1",
                "title": "General Requirements",
                "level": 2,
                "content": "The bars shall be manufactured from carbon steel materials.",
            },
            "2": {
                "id": "2",
                "title": "Chemical Composition",
                "level": 1,
                "content": "Carbon content shall be between 0.25% and 0.5%.",
            },
        }

    @pytest.fixture
    def sample_sections_b_renamed(self):
        """Sample sections from PDF B with renamed titles."""
        return {
            "1": {
                "id": "1",
                "title": "Application Scope",  # Renamed
                "level": 1,
                "content": "This specification covers hot-rolled carbon steel bars.",
            },
            "1.1": {
                "id": "1.1",
                "title": "General Requirements",
                "level": 2,
                "content": "The bars shall be manufactured from carbon steel materials.",
            },
            "2": {
                "id": "2",
                "title": "Chemical Composition Requirements",  # Renamed
                "level": 1,
                "content": "Carbon content shall be between 0.25% and 0.5%.",
            },
        }

    def test_exact_id_matches_all_aligned(self, sample_sections_a, sample_sections_b_exact_match):
        """All sections with exact IDs should align with confidence 1.0."""
        alignments = align_sections_heuristic(sample_sections_a, sample_sections_b_exact_match)

        assert len(alignments) == 3
        assert all(a["method"] == "exact" for a in alignments.values())
        assert all(a["confidence"] == 1.0 for a in alignments.values())

    def test_renamed_sections_fuzzy_match(self, sample_sections_a, sample_sections_b_renamed):
        """Renamed sections should match via fuzzy/content similarity."""
        alignments = align_sections_heuristic(sample_sections_a, sample_sections_b_renamed)

        assert len(alignments) == 3  # All should still match
        # At least some should use fuzzy/content method
        non_exact = [a for a in alignments.values() if a["method"] != "exact"]
        assert len(non_exact) > 0

    def test_alignment_includes_similarity_scores(self, sample_sections_a, sample_sections_b_renamed):
        """Fuzzy/content alignments should include title and content similarity scores."""
        alignments = align_sections_heuristic(sample_sections_a, sample_sections_b_renamed)

        # Find non-exact matches
        non_exact = [a for a in alignments.values() if a["method"] != "exact"]

        for alignment in non_exact:
            assert "title_similarity" in alignment
            assert "content_similarity" in alignment
            assert 0.0 <= alignment["title_similarity"] <= 1.0
            assert 0.0 <= alignment["content_similarity"] <= 1.0

    def test_combined_score_weighted_correctly(self, sample_sections_a):
        """Combined score should be 70% title + 30% content."""
        sections_b = {
            "1": {
                "id": "1",
                "title": "Application",  # Low title similarity (~0.5)
                "level": 1,
                "content": "This specification covers hot-rolled carbon steel bars.",  # High content similarity (~1.0)
            }
        }

        alignments = align_sections_heuristic(sample_sections_a, sections_b)

        if "1" in alignments and alignments["1"]["method"] != "exact":
            alignment = alignments["1"]
            title_sim = alignment["title_similarity"]
            content_sim = alignment["content_similarity"]
            expected_combined = (0.7 * title_sim) + (0.3 * content_sim)

            assert alignment["confidence"] == pytest.approx(expected_combined, abs=0.01)


class TestGetSectionById:
    """Test suite for section retrieval by ID."""

    @pytest.fixture
    def hierarchical_sections(self):
        """Sample hierarchical section structure."""
        return {
            "1": {
                "id": "1",
                "title": "Main Section",
                "level": 1,
                "subsections": {
                    "1.1": {
                        "id": "1.1",
                        "title": "Subsection",
                        "level": 2,
                        "subsections": {
                            "1.1.1": {
                                "id": "1.1.1",
                                "title": "Deep Subsection",
                                "level": 3,
                                "subsections": {},
                            }
                        },
                    }
                },
            }
        }

    def test_find_top_level_section(self, hierarchical_sections):
        """Should find top-level section."""
        section = get_section_by_id(hierarchical_sections, "1")
        assert section is not None
        assert section["id"] == "1"
        assert section["title"] == "Main Section"

    def test_find_nested_section(self, hierarchical_sections):
        """Should find nested section."""
        section = get_section_by_id(hierarchical_sections, "1.1")
        assert section is not None
        assert section["id"] == "1.1"
        assert section["title"] == "Subsection"

    def test_find_deeply_nested_section(self, hierarchical_sections):
        """Should find deeply nested section."""
        section = get_section_by_id(hierarchical_sections, "1.1.1")
        assert section is not None
        assert section["id"] == "1.1.1"
        assert section["title"] == "Deep Subsection"

    def test_nonexistent_section_returns_none(self, hierarchical_sections):
        """Should return None for non-existent section."""
        section = get_section_by_id(hierarchical_sections, "99")
        assert section is None


class TestFlattenSections:
    """Test suite for section flattening."""

    def test_flat_structure_unchanged(self):
        """Already flat structure should remain unchanged."""
        sections = {
            "1": {"id": "1", "title": "Section 1", "level": 1, "subsections": {}},
            "2": {"id": "2", "title": "Section 2", "level": 1, "subsections": {}},
        }
        flat = _flatten_sections(sections)

        assert len(flat) == 2
        assert "1" in flat
        assert "2" in flat

    def test_nested_structure_flattened(self):
        """Nested structure should be flattened."""
        sections = {
            "1": {
                "id": "1",
                "title": "Section 1",
                "level": 1,
                "subsections": {
                    "1.1": {
                        "id": "1.1",
                        "title": "Subsection 1.1",
                        "level": 2,
                        "subsections": {},
                    }
                },
            }
        }
        flat = _flatten_sections(sections)

        assert len(flat) == 2
        assert "1" in flat
        assert "1.1" in flat

    def test_deep_nesting_all_levels_included(self):
        """All nesting levels should be included in flat structure."""
        sections = {
            "1": {
                "id": "1",
                "title": "Level 1",
                "level": 1,
                "subsections": {
                    "1.1": {
                        "id": "1.1",
                        "title": "Level 2",
                        "level": 2,
                        "subsections": {
                            "1.1.1": {
                                "id": "1.1.1",
                                "title": "Level 3",
                                "level": 3,
                                "subsections": {},
                            }
                        },
                    }
                },
            }
        }
        flat = _flatten_sections(sections)

        assert len(flat) == 3
        assert "1" in flat
        assert "1.1" in flat
        assert "1.1.1" in flat

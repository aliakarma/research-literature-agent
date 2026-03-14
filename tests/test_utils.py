"""
tests/test_utils.py
--------------------
Unit tests for utility helpers.
"""

import pytest
from pathlib import Path
import tempfile

from research_agent.utils import sanitise_filename, save_review, validate_papers


class TestSanitiseFilename:
    def test_spaces_become_underscores(self):
        assert "_" in sanitise_filename("hello world")

    def test_special_chars_removed(self):
        result = sanitise_filename("AI: Safety & Alignment!")
        assert ":" not in result
        assert "&" not in result
        assert "!" not in result

    def test_truncates_to_max_length(self):
        long = "a" * 100
        assert len(sanitise_filename(long, max_length=30)) <= 30

    def test_lowercase(self):
        assert sanitise_filename("UPPERCASE") == "uppercase"


class TestValidatePapers:
    def test_raises_on_empty_list(self):
        with pytest.raises(ValueError, match="No papers"):
            validate_papers([])

    def test_raises_on_single_paper(self):
        papers = [{"title": "Paper 1"}]
        with pytest.raises(ValueError, match="At least"):
            validate_papers(papers, min_count=2)

    def test_passes_with_sufficient_papers(self):
        papers = [{"title": "Paper 1"}, {"title": "Paper 2"}]
        validate_papers(papers, min_count=2)  # should not raise


class TestSaveReview:
    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_review("My review content", "test topic", tmpdir)
            assert Path(path).exists()

    def test_file_contains_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_review("My review content", "test topic", tmpdir)
            assert "My review content" in Path(path).read_text()

    def test_latex_extension(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_review("\\section{}", "topic", tmpdir, extension="tex")
            assert str(path).endswith(".tex")

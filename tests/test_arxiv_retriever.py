"""
tests/test_arxiv_retriever.py
------------------------------
Unit tests for the ArxivRetriever module.

Uses unittest.mock to patch the arxiv library so no real network
calls are made during testing. This keeps tests fast and repeatable.

Run with:
    pytest tests/ -v
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from research_agent.config import Config
from research_agent.arxiv_retriever import ArxivRetriever


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def config():
    """A minimal Config with a dummy API key for testing."""
    return Config(openai_api_key="sk-test-key")


def _make_mock_result(title: str = "Test Paper", abstract: str = "Test abstract."):
    """Create a mock arxiv.Result object with the minimum required attributes."""
    result = MagicMock()
    result.title = title
    result.summary = abstract
    result.authors = [MagicMock(__str__=lambda self: "Alice Smith")]
    result.published = MagicMock(date=lambda: date(2024, 6, 1))
    result.entry_id = "https://arxiv.org/abs/2406.00001"
    return result


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestArxivRetriever:

    @patch("research_agent.arxiv_retriever.arxiv.Search")
    def test_search_returns_list_of_dicts(self, mock_search_cls, config):
        """search() should return a list of dicts with required keys."""
        mock_result = _make_mock_result()
        mock_search_cls.return_value.results.return_value = [mock_result]

        retriever = ArxivRetriever(config)
        papers = retriever.search("test topic", max_results=1)

        assert isinstance(papers, list)
        assert len(papers) == 1
        paper = papers[0]
        for key in ("title", "authors", "abstract", "url", "date", "paper_id"):
            assert key in paper, f"Missing key: {key}"

    @patch("research_agent.arxiv_retriever.arxiv.Search")
    def test_search_correct_metadata(self, mock_search_cls, config):
        """Verify that metadata fields are correctly extracted from arxiv results."""
        mock_result = _make_mock_result(
            title="Agentic AI for Climate",
            abstract="We propose a new framework."
        )
        mock_search_cls.return_value.results.return_value = [mock_result]

        retriever = ArxivRetriever(config)
        papers = retriever.search("climate AI")

        assert papers[0]["title"] == "Agentic AI for Climate"
        assert papers[0]["abstract"] == "We propose a new framework."
        assert papers[0]["date"] == "2024-06-01"
        assert papers[0]["paper_id"] == "2406.00001"

    @patch("research_agent.arxiv_retriever.arxiv.Search")
    def test_search_returns_empty_on_no_results(self, mock_search_cls, config):
        """search() should return an empty list if arXiv has no results."""
        mock_search_cls.return_value.results.return_value = []
        retriever = ArxivRetriever(config)
        papers = retriever.search("xyzzy nonsense query")
        assert papers == []

    def test_to_plain_text_format(self, config):
        """to_plain_text() should include TITLE, AUTHORS, DATE, URL, ABSTRACT."""
        papers = [
            {
                "title":    "Test Paper",
                "authors":  ["Alice Smith", "Bob Jones"],
                "abstract": "This is the abstract.",
                "url":      "https://arxiv.org/abs/2406.00001",
                "date":     "2024-06-01",
                "paper_id": "2406.00001",
            }
        ]
        texts = ArxivRetriever.to_plain_text(papers)
        assert len(texts) == 1
        assert "TITLE: Test Paper" in texts[0]
        assert "AUTHORS: Alice Smith" in texts[0]
        assert "ABSTRACT: This is the abstract." in texts[0]

    def test_to_plain_text_truncates_long_author_list(self, config):
        """Author lists longer than 5 should be truncated with 'et al.'."""
        papers = [{
            "title":    "Big Collaboration Paper",
            "authors":  [f"Author {i}" for i in range(10)],
            "abstract": "Abstract.",
            "url":      "https://arxiv.org/abs/2406.00002",
            "date":     "2024-06-01",
            "paper_id": "2406.00002",
        }]
        texts = ArxivRetriever.to_plain_text(papers)
        assert "et al." in texts[0]

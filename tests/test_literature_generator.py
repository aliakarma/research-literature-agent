"""
tests/test_literature_generator.py
------------------------------------
Tests for output formatting in LiteratureGenerator.
No LLM calls are made here — we only test the formatting helpers.
"""

import pytest
from research_agent.literature_generator import LiteratureGenerator


SAMPLE_PAPERS = [
    {
        "title":    "Deep Learning for Weather Forecasting",
        "authors":  ["Alice Chen", "Bob Patel", "Carol Wang", "Dave Kim"],
        "abstract": "We present a transformer model for weather prediction.",
        "url":      "https://arxiv.org/abs/2401.00001",
        "date":     "2024-01-15",
        "paper_id": "2401.00001",
        "summary":  "Chen et al. propose a transformer model achieving state-of-the-art on ECMWF.",
    },
    {
        "title":    "Multi-Agent Climate Modeling",
        "authors":  ["Eve Liu"],
        "abstract": "A MARL framework for regional precipitation forecasting.",
        "url":      "https://arxiv.org/abs/2402.00001",
        "date":     "2024-02-20",
        "paper_id": "2402.00001",
        "summary":  "Liu proposes a MARL framework reducing MAE by 12% on ERA5.",
    },
]

SAMPLE_REVIEW = (
    "Recent work has converged on transformer-based approaches. "
    "Key contributions include novel attention mechanisms. "
    "Gaps remain in long-horizon prediction."
)


class TestFormatOutput:

    def test_contains_topic(self):
        out = LiteratureGenerator.format_output("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "climate AI" in out

    def test_contains_paper_count(self):
        out = LiteratureGenerator.format_output("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "2" in out

    def test_contains_review_text(self):
        out = LiteratureGenerator.format_output("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert SAMPLE_REVIEW in out

    def test_contains_references(self):
        out = LiteratureGenerator.format_output("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "Deep Learning for Weather Forecasting" in out
        assert "Multi-Agent Climate Modeling" in out

    def test_reference_has_url(self):
        out = LiteratureGenerator.format_output("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "arxiv.org" in out


class TestToLatex:

    def test_has_section_command(self):
        latex = LiteratureGenerator.to_latex("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "\\section{Related Work}" in latex

    def test_has_bibliography_env(self):
        latex = LiteratureGenerator.to_latex("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "\\begin{thebibliography}" in latex
        assert "\\end{thebibliography}" in latex

    def test_has_bibitem_entries(self):
        latex = LiteratureGenerator.to_latex("climate AI", SAMPLE_PAPERS, SAMPLE_REVIEW)
        assert "\\bibitem{ref1}" in latex
        assert "\\bibitem{ref2}" in latex

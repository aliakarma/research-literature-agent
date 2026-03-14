"""
research_agent
==============
A modular, LangChain-powered agent that automatically retrieves arXiv papers,
summarizes them, and synthesizes publication-quality literature reviews.

Public API
----------
>>> from research_agent import run_literature_review_agent
>>> review = run_literature_review_agent("agentic AI climate prediction", max_papers=8)

>>> from research_agent import ArxivRetriever, VectorStore, Summarizer, LiteratureGenerator
"""

from research_agent.arxiv_retriever import ArxivRetriever
from research_agent.vector_store import VectorStore
from research_agent.summarizer import Summarizer
from research_agent.literature_generator import LiteratureGenerator
from research_agent.agent import run_literature_review_agent
from research_agent.config import Config

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "run_literature_review_agent",
    "ArxivRetriever",
    "VectorStore",
    "Summarizer",
    "LiteratureGenerator",
    "Config",
]

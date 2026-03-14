"""
research_agent/arxiv_retriever.py
----------------------------------
Handles all communication with the arXiv API.

HOW IT WORKS
------------
The arXiv API is a public REST service provided by Cornell University.
This module wraps it using the `arxiv` Python library, which handles
rate limiting and pagination automatically.

When you call ArxivRetriever.search(), the library sends an HTTP request to:
  https://export.arxiv.org/api/query?search_query=...

Results are returned as Python objects with attributes like .title,
.authors, .summary (abstract), .published, and .entry_id.

We convert each result into a plain Python dict for portability — no
dependency on the arxiv library's internal objects elsewhere in the codebase.

SCALING NOTE
------------
arXiv imposes a soft rate limit of ~3 requests/second. For large-scale
scraping (>100 papers), add time.sleep(1) between batches. For this
agent's default of 5–15 papers, no throttling is needed.
"""

import arxiv
from typing import List, Dict
from research_agent.config import Config


class ArxivRetriever:
    """
    Searches arXiv for papers matching a topic query and returns
    structured metadata dictionaries.

    Parameters
    ----------
    config : Config
        Global agent configuration. Uses config.max_papers and
        config.arxiv_sort_by.

    Example
    -------
    >>> retriever = ArxivRetriever(config)
    >>> papers = retriever.search("multi-agent reinforcement learning", max_results=6)
    >>> print(papers[0]["title"])
    """

    # Map human-readable sort names to arxiv library constants
    SORT_OPTIONS = {
        "relevance":       arxiv.SortCriterion.Relevance,
        "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
        "submittedDate":   arxiv.SortCriterion.SubmittedDate,
    }

    def __init__(self, config: Config) -> None:
        self.config = config
        sort_key = config.arxiv_sort_by
        self.sort_criterion = self.SORT_OPTIONS.get(
            sort_key, arxiv.SortCriterion.Relevance
        )

    def search(self, query: str, max_results: int = None) -> List[Dict]:
        """
        Search arXiv and return a list of paper metadata dicts.

        Parameters
        ----------
        query       : Natural language research topic.
        max_results : Number of papers to fetch. Defaults to config.max_papers.

        Returns
        -------
        List of dicts with keys:
            title, authors, abstract, url, date, paper_id
        """
        if max_results is None:
            max_results = self.config.max_papers

        print(f"\n[ArxivRetriever] Searching: '{query}'  (max {max_results} papers)")

        search_obj = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=self.sort_criterion,
        )

        papers = []
        for result in search_obj.results():
            paper = {
                "title":    result.title,
                # Convert Author objects to plain strings
                "authors":  [str(a) for a in result.authors],
                # Flatten newlines so the text is one clean paragraph
                "abstract": result.summary.replace("\n", " ").strip(),
                "url":      result.entry_id,
                "date":     str(result.published.date()),
                # Extract just the numeric ID from the full URL
                "paper_id": result.entry_id.split("/abs/")[-1],
            }
            papers.append(paper)
            print(f"  ✓ {paper['title'][:80]}...")

        print(f"[ArxivRetriever] Retrieved {len(papers)} papers.\n")
        return papers

    @staticmethod
    def to_plain_text(papers: List[Dict]) -> List[str]:
        """
        Convert paper metadata dicts into plain-text strings.

        Each string includes title, authors, date, URL, and abstract —
        formatted so the LLM can read it naturally.

        Parameters
        ----------
        papers : Output of ArxivRetriever.search()

        Returns
        -------
        List of formatted strings, one per paper.
        """
        docs = []
        for p in papers:
            # Limit author list to first 5 to keep text concise
            author_list = p["authors"][:5]
            if len(p["authors"]) > 5:
                author_list.append("et al.")
            authors_str = ", ".join(author_list)

            text = (
                f"TITLE: {p['title']}\n"
                f"AUTHORS: {authors_str}\n"
                f"DATE: {p['date']}\n"
                f"URL: {p['url']}\n"
                f"ABSTRACT: {p['abstract']}"
            )
            docs.append(text)
        return docs

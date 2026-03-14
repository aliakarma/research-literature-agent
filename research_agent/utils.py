"""
research_agent/utils.py
------------------------
Shared utility functions used across the agent pipeline.

Contains helpers for:
  - Saving reviews to disk (plain text and LaTeX)
  - Pretty-printing pipeline progress
  - Sanitising strings for use as filenames
  - Timing pipeline stages
"""

import os
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import contextmanager


# ── File I/O ──────────────────────────────────────────────────────────────────

def save_review(
    content: str,
    topic: str,
    output_dir: Path,
    extension: str = "txt",
) -> Path:
    """
    Save a generated review to disk with a timestamp-based filename.

    Parameters
    ----------
    content    : Text content to write.
    topic      : Research topic (used in filename).
    output_dir : Directory to save into (created if it does not exist).
    extension  : File extension, e.g. "txt" or "tex".

    Returns
    -------
    Path to the saved file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_topic = sanitise_filename(topic, max_length=40)
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename   = output_dir / f"review_{safe_topic}_{timestamp}.{extension}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[Utils] Saved → {filename}")
    return filename


def sanitise_filename(text: str, max_length: int = 50) -> str:
    """
    Convert an arbitrary string into a safe, lowercase filename fragment.

    Replaces spaces with underscores, strips non-alphanumeric characters
    (except underscores and hyphens), and truncates to max_length.

    Examples
    --------
    >>> sanitise_filename("Agentic AI: Climate & Prediction!")
    'agentic_ai_climate__prediction'
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)      # remove special chars
    text = re.sub(r"[\s]+", "_", text)         # spaces → underscores
    return text[:max_length]


# ── Timing ────────────────────────────────────────────────────────────────────

@contextmanager
def timer(label: str):
    """
    Context manager that prints elapsed time for a code block.

    Usage
    -----
    >>> with timer("ArXiv retrieval"):
    ...     papers = retriever.search(topic)
    [Timer] ArXiv retrieval — 1.84s
    """
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[Timer] {label} — {elapsed:.2f}s")


# ── Display helpers ───────────────────────────────────────────────────────────

def print_banner(title: str, width: int = 60) -> None:
    """Print a formatted banner line for pipeline stage announcements."""
    border = "─" * width
    print(f"\n┌{border}┐")
    print(f"│  {title:<{width - 2}}│")
    print(f"└{border}┘")


def print_paper_table(papers: list) -> None:
    """
    Print a compact table of retrieved papers for quick review.

    Parameters
    ----------
    papers : List of paper dicts from ArxivRetriever.search()
    """
    print(f"\n{'#':<4} {'Date':<12} {'Title':<60}")
    print("─" * 78)
    for i, p in enumerate(papers, 1):
        title_short = p["title"][:58] + ".." if len(p["title"]) > 60 else p["title"]
        print(f"{i:<4} {p['date']:<12} {title_short}")
    print()


# ── Validation helpers ────────────────────────────────────────────────────────

def validate_papers(papers: list, min_count: int = 2) -> None:
    """
    Raise a clear error if the paper list is too small to synthesize from.

    Parameters
    ----------
    papers    : List of paper dicts.
    min_count : Minimum number of papers required (default: 2).
    """
    if not papers:
        raise ValueError(
            "No papers were retrieved. Try a broader search query, "
            "or check your internet connection."
        )
    if len(papers) < min_count:
        raise ValueError(
            f"Only {len(papers)} paper(s) retrieved. At least {min_count} are "
            "needed for a meaningful literature review. Increase max_papers or "
            "broaden the search topic."
        )

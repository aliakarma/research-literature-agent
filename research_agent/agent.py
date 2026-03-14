"""
research_agent/agent.py
------------------------
Top-level orchestration for the Literature Review Agent.

Ties all pipeline stages together in the correct order and exposes two
interfaces:

  1. Python API  — run_literature_review_agent()
     Import and call this from your own scripts or notebooks.

  2. CLI         — python -m research_agent.agent --topic "..." --max_papers 8
     Run directly from the terminal without writing any Python.

PIPELINE SUMMARY
----------------
  1. Config validation   — ensure API key is present
  2. ArXiv retrieval     — fetch papers by topic
  3. Vector store build  — embed and index all paper texts
  4. Summarization       — LLM summarizes each paper individually
  5. Synthesis           — LLM synthesizes all summaries into a review
  6. Output              — print, save as .txt, optionally export as .tex
"""

import argparse
from pathlib import Path
from typing import Optional

from research_agent.config import Config
from research_agent.arxiv_retriever import ArxivRetriever
from research_agent.vector_store import VectorStore
from research_agent.summarizer import Summarizer
from research_agent.literature_generator import LiteratureGenerator
from research_agent.utils import (
    save_review,
    print_banner,
    print_paper_table,
    validate_papers,
    timer,
)


def run_literature_review_agent(
    topic: str,
    max_papers: int = 8,
    openai_api_key: Optional[str] = None,
    save_txt: bool = True,
    save_latex: bool = False,
    output_dir: str = "outputs",
    config: Optional[Config] = None,
) -> str:
    """
    Run the full literature review pipeline.

    Parameters
    ----------
    topic         : Research topic to survey (natural language).
    max_papers    : Number of arXiv papers to retrieve (1–50).
    openai_api_key: Override the API key from environment variables.
    save_txt      : Save the plain-text review to outputs/.
    save_latex    : Also save a LaTeX (.tex) version for direct use in papers.
    output_dir    : Directory for saved files.
    config        : Optional pre-built Config object. If provided, all other
                    parameters except `topic` are ignored.

    Returns
    -------
    Formatted literature review string (the same text printed to console).

    Raises
    ------
    ValueError : If the API key is missing or max_papers is out of range.
    RuntimeError : If no papers are found for the given topic.

    Example
    -------
    >>> from research_agent import run_literature_review_agent
    >>> review = run_literature_review_agent(
    ...     "Agentic AI for climate prediction",
    ...     max_papers=8,
    ...     save_latex=True,
    ... )
    """

    # ── 0. Configuration ──────────────────────────────────────────────────────
    if config is None:
        config = Config(
            max_papers=max_papers,
            output_dir=Path(output_dir),
            save_output=save_txt,
        )
        if openai_api_key:
            config.openai_api_key = openai_api_key

    config.validate()   # raises if API key missing or params invalid

    # ── 1. Banner ─────────────────────────────────────────────────────────────
    print_banner(f"LITERATURE REVIEW AGENT  |  \"{topic}\"")

    # ── 2. Retrieve papers ────────────────────────────────────────────────────
    with timer("ArXiv retrieval"):
        retriever = ArxivRetriever(config)
        papers = retriever.search(topic, max_results=config.max_papers)

    validate_papers(papers, min_count=2)
    print_paper_table(papers)

    # ── 3. Build vector store ─────────────────────────────────────────────────
    # This step embeds all papers and loads them into FAISS.
    # It is not strictly required for small paper sets but makes the pipeline
    # scalable to hundreds of papers and enables future RAG-style retrieval.
    with timer("Embedding + indexing"):
        doc_texts = ArxivRetriever.to_plain_text(papers)
        vs = VectorStore(config)
        vs.build(doc_texts)

    # Retrieve the most relevant chunks as a sanity check
    top_chunks = vs.retrieve(topic)
    print(f"[Agent] Top {len(top_chunks)} chunks retrieved from vector store.\n")

    # ── 4. Summarize papers ───────────────────────────────────────────────────
    with timer("Summarization"):
        summarizer = Summarizer(config)
        papers = summarizer.summarize_all(papers)

    # ── 5. Synthesize literature review ──────────────────────────────────────
    with timer("Synthesis"):
        generator = LiteratureGenerator(config)
        review_text = generator.generate(topic, papers)

    # ── 6. Format output ──────────────────────────────────────────────────────
    final_output = LiteratureGenerator.format_output(topic, papers, review_text)
    print(final_output)

    # ── 7. Save outputs ───────────────────────────────────────────────────────
    if save_txt:
        save_review(final_output, topic, config.output_dir, extension="txt")

    if save_latex:
        latex_output = LiteratureGenerator.to_latex(topic, papers, review_text)
        save_review(latex_output, topic, config.output_dir, extension="tex")

    return final_output


# ── CLI entry point ───────────────────────────────────────────────────────────

def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-agent",
        description=(
            "Research Literature Review Agent\n"
            "Automatically generate a literature review from arXiv papers.\n\n"
            "Example:\n"
            "  python -m research_agent.agent --topic \"Agentic AI climate prediction\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help='Research topic, e.g. "multi-agent reinforcement learning"',
    )
    parser.add_argument(
        "--max_papers",
        type=int,
        default=8,
        metavar="N",
        help="Number of arXiv papers to retrieve (default: 8, max: 50)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="outputs",
        help="Directory to save output files (default: outputs/)",
    )
    parser.add_argument(
        "--no_save",
        action="store_true",
        help="Do not save output files to disk",
    )
    parser.add_argument(
        "--latex",
        action="store_true",
        help="Also export a LaTeX (.tex) version of the review",
    )
    return parser


if __name__ == "__main__":
    parser = _build_cli_parser()
    args = parser.parse_args()

    run_literature_review_agent(
        topic=args.topic,
        max_papers=args.max_papers,
        save_txt=not args.no_save,
        save_latex=args.latex,
        output_dir=args.output_dir,
    )

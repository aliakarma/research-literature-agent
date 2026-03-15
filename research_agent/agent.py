"""
research_agent/agent.py
------------------------
Pipeline orchestration.
"""
import argparse
from pathlib import Path
from typing import Optional

from research_agent.config import Config
from research_agent.arxiv_retriever import ArxivRetriever
from research_agent.vector_store import VectorStore
from research_agent.summarizer import Summarizer
from research_agent.literature_generator import LiteratureGenerator
from research_agent.utils import save_review, print_banner, print_paper_table, validate_papers, timer


def run_literature_review_agent(
    topic: str,
    max_papers: int = 8,
    openai_api_key: Optional[str] = None,
    save_txt: bool = True,
    save_latex: bool = False,
    output_dir: str = "outputs",
    config: Optional[Config] = None,
) -> str:
    if config is None:
        config = Config(max_papers=max_papers, output_dir=Path(output_dir), save_output=save_txt)
        if openai_api_key:
            config.openai_api_key = openai_api_key
    config.validate()

    print_banner(f"LITERATURE REVIEW AGENT  |  \"{topic}\"")

    with timer("ArXiv retrieval"):
        retriever = ArxivRetriever(config)
        papers = retriever.search(topic, max_results=config.max_papers)
    validate_papers(papers, min_count=2)
    print_paper_table(papers)

    with timer("Embedding + indexing"):
        doc_texts = ArxivRetriever.to_plain_text(papers)
        vs = VectorStore(config)
        vs.build(doc_texts)
    top_chunks = vs.retrieve(topic)
    print(f"[Agent] Top {len(top_chunks)} chunks retrieved.\n")

    with timer("Summarization"):
        summarizer = Summarizer(config)
        papers = summarizer.summarize_all(papers)

    with timer("Synthesis"):
        generator = LiteratureGenerator(config)
        review_text = generator.generate(topic, papers)

    final_output = LiteratureGenerator.format_output(topic, papers, review_text)
    print(final_output)

    if save_txt:
        save_review(final_output, topic, config.output_dir, extension="txt")
    if save_latex:
        latex_output = LiteratureGenerator.to_latex(topic, papers, review_text)
        save_review(latex_output, topic, config.output_dir, extension="tex")

    return final_output

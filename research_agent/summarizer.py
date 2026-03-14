"""
research_agent/summarizer.py
-----------------------------
Produces structured per-paper summaries using an LLM.

WHY SUMMARIZE BEFORE SYNTHESIS?
--------------------------------
The final literature review may need to synthesize 8–15 papers.
Passing all raw abstracts directly to the synthesis step risks:
  1. Exceeding the LLM's context window (~128k tokens for GPT-4o,
     but abstracts + metadata for 15 papers can still be noisy).
  2. Producing output dominated by whichever papers appear first
     ("primacy bias" in long-context LLMs).

Pre-summarizing forces each paper through the same structured template,
giving the synthesis step clean, comparable summaries of equal weight.

PROMPT ENGINEERING NOTES
-------------------------
The prompt template uses explicit section labels (Core Problem, Method,
Results, Limitations) rather than asking for "a summary". This produces
more reliable, consistently structured output. Low temperature (0.2) ensures
the LLM stays close to the source text rather than hallucinating details.
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from research_agent.config import Config


# ── Prompt template ───────────────────────────────────────────────────────────
# {title} and {abstract} are filled in at runtime for each paper.
SUMMARIZATION_PROMPT = PromptTemplate(
    input_variables=["title", "abstract"],
    template="""You are a research assistant writing structured summaries for an academic literature review.

Given the paper title and abstract below, write a concise 2–4 sentence summary that covers:
1. Core research problem or motivation
2. Proposed method, model, or framework
3. Key results or contributions
4. Limitations if explicitly mentioned (omit if not)

Rules:
- Use formal academic English
- Be precise and specific — include model names, dataset names, and metrics where present
- Do not pad with generic phrases like "This paper presents..."
- Write as flowing prose, not bullet points

TITLE: {title}
ABSTRACT: {abstract}

SUMMARY:""",
)


class Summarizer:
    """
    Uses an LLM to produce structured, one-paragraph summaries of research papers.

    Parameters
    ----------
    config : Config
        Uses config.summarization_model, config.summarization_temperature,
        and config.openai_api_key.

    Example
    -------
    >>> summarizer = Summarizer(config)
    >>> papers = summarizer.summarize_all(papers)
    >>> print(papers[0]["summary"])
    """

    def __init__(self, config: Config) -> None:
        self.config = config

        # Build the LLM — gpt-4o-mini by default for speed and low cost
        llm = ChatOpenAI(
            model=config.summarization_model,
            temperature=config.summarization_temperature,
            openai_api_key=config.openai_api_key,
        )

        # LLMChain binds the prompt template to the LLM.
        # Calling chain.invoke({"title": ..., "abstract": ...}) runs one inference.
        self._chain = LLMChain(llm=llm, prompt=SUMMARIZATION_PROMPT)

    def summarize_paper(self, paper: Dict) -> str:
        """
        Summarize a single paper.

        Parameters
        ----------
        paper : Paper dict with at least "title" and "abstract" keys.

        Returns
        -------
        Summary string.
        """
        result = self._chain.invoke({
            "title":    paper["title"],
            "abstract": paper["abstract"],
        })
        return result["text"].strip()

    def summarize_all(self, papers: List[Dict]) -> List[Dict]:
        """
        Summarize every paper in the list. Adds a "summary" key to each dict.

        Parameters
        ----------
        papers : List of paper dicts from ArxivRetriever.search()

        Returns
        -------
        Same list with "summary" key populated on every paper.
        """
        print(f"[Summarizer] Summarizing {len(papers)} papers...")
        total = len(papers)

        for i, paper in enumerate(papers, 1):
            print(f"  [{i}/{total}] {paper['title'][:70]}...")
            paper["summary"] = self.summarize_paper(paper)

        print("[Summarizer] Done.\n")
        return papers

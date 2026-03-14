"""
research_agent/literature_generator.py
----------------------------------------
Synthesizes individual per-paper summaries into a cohesive, multi-paragraph
literature review section suitable for inclusion in a research paper.

THE SYNTHESIS TASK
------------------
Summarization and synthesis are fundamentally different cognitive tasks:

  Summarization — understand one document in isolation.
  Synthesis     — read N documents together, identify patterns, contradictions,
                  and gaps, and produce a new unified narrative.

This module handles synthesis. It uses a stronger LLM (gpt-4o by default)
and a more complex prompt that instructs the model to reason across all papers
simultaneously and organise the output into three specific sections:

  Paragraph 1 — Research Trends & Context
  Paragraph 2 — Methods & Key Contributions
  Paragraph 3 — Research Gaps & Future Directions

OUTPUT FORMAT
-------------
The final output is a formatted block containing:
  - The three-paragraph literature review
  - A numbered reference list (Chicago-author-date style)
  - Paper count and topic header

This can be pasted directly into a LaTeX document's \\section{Related Work}.
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from research_agent.config import Config


# ── Synthesis prompt ──────────────────────────────────────────────────────────
SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["topic", "num_papers", "summaries"],
    template="""You are a senior AI researcher writing the literature review section of a research paper.

Research Topic: {topic}
Number of papers analyzed: {num_papers}

Below are structured summaries of each paper:

{summaries}

Write a literature review of exactly 3 paragraphs following this structure:

PARAGRAPH 1 — Research Trends & Context
Describe the overall research trajectory in this area. What paradigms or approaches have been dominant? How has the field evolved? Place the papers in historical and conceptual context.

PARAGRAPH 2 — Methods & Key Contributions
Synthesize the major methodological approaches, architectures, and frameworks used across the papers. Highlight landmark results and specific contributions. Reference papers by their title or lead author where appropriate (e.g., "Chen et al. proposed...").

PARAGRAPH 3 — Research Gaps & Future Directions
Identify what is missing, under-explored, or explicitly stated as a limitation across these papers. Frame these gaps to motivate future work. Be specific about what has NOT been done.

Formatting rules:
- Write in formal, academic English
- Use flowing paragraphs — no bullet points, no headings, no numbered lists in the output
- Be specific: name models, datasets, metrics, and methods when they appear in the summaries
- Do not use phrases like "The papers reviewed here..." or "In this literature review..."
- Do not include anything outside the three paragraphs

LITERATURE REVIEW:""",
)


class LiteratureGenerator:
    """
    Produces the final literature review from per-paper summaries.

    Parameters
    ----------
    config : Config
        Uses config.synthesis_model, config.synthesis_temperature,
        and config.openai_api_key.

    Example
    -------
    >>> gen = LiteratureGenerator(config)
    >>> review = gen.generate(topic, papers)
    >>> print(gen.format_output(topic, papers, review))
    """

    def __init__(self, config: Config) -> None:
        self.config = config

        # Use the more powerful synthesis model
        llm = ChatOpenAI(
            model=config.synthesis_model,
            temperature=config.synthesis_temperature,
            openai_api_key=config.openai_api_key,
        )
        self._chain = LLMChain(llm=llm, prompt=SYNTHESIS_PROMPT)

    def generate(self, topic: str, papers: List[Dict]) -> str:
        """
        Synthesize all paper summaries into a literature review.

        Parameters
        ----------
        topic  : The research topic (used in the prompt for context).
        papers : Papers with "summary" key populated by Summarizer.

        Returns
        -------
        Raw literature review string (three paragraphs).
        """
        print("[LiteratureGenerator] Synthesizing review...\n")

        # Build a numbered list of title + summary pairs
        summaries_block = ""
        for i, p in enumerate(papers, 1):
            summaries_block += f"[{i}] {p['title']}\n{p['summary']}\n\n"

        result = self._chain.invoke({
            "topic":      topic,
            "num_papers": str(len(papers)),
            "summaries":  summaries_block,
        })

        review = result["text"].strip()
        print("[LiteratureGenerator] Done.\n")
        return review

    # ── Output formatting ─────────────────────────────────────────────────────

    @staticmethod
    def format_output(topic: str, papers: List[Dict], review: str) -> str:
        """
        Wrap the review in a structured output block with a paper index.

        Parameters
        ----------
        topic  : Research topic string.
        papers : Full paper list (metadata + summaries).
        review : Synthesized review text from generate().

        Returns
        -------
        Formatted string ready for display or saving to file.
        """
        sep = "=" * 72

        # Build reference list
        refs = ""
        for i, p in enumerate(papers, 1):
            authors = p["authors"][:3]
            if len(p["authors"]) > 3:
                authors = authors + ["et al."]
            authors_str = ", ".join(authors)
            year = p["date"][:4]
            refs += f"  [{i}] {authors_str} ({year}). {p['title']}.\n       {p['url']}\n"

        output = (
            f"\n{sep}\n"
            f"  AUTOMATED LITERATURE REVIEW\n"
            f"  Topic    : {topic}\n"
            f"  Papers   : {len(papers)}\n"
            f"{sep}\n\n"
            f"{review}\n\n"
            f"{sep}\n"
            f"  REFERENCES\n"
            f"{sep}\n"
            f"{refs}"
            f"{sep}\n"
        )
        return output

    @staticmethod
    def to_latex(topic: str, papers: List[Dict], review: str) -> str:
        """
        Export the literature review as a LaTeX snippet.

        Returns a string you can paste directly into a .tex file's
        \\section{{Related Work}} block.

        Parameters
        ----------
        topic  : Research topic.
        papers : Full paper list.
        review : Synthesized review text.

        Returns
        -------
        LaTeX-formatted string.
        """
        # Escape special LaTeX characters in the review text
        escape_chars = {"&": r"\&", "%": r"\%", "$": r"\$",
                        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
                        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
        safe_review = review
        for char, replacement in escape_chars.items():
            safe_review = safe_review.replace(char, replacement)

        # Build \bibitem entries
        bibitems = ""
        for i, p in enumerate(papers, 1):
            first_author = p["authors"][0].split()[-1] if p["authors"] else "Unknown"
            year = p["date"][:4]
            bibitems += (
                f"\\bibitem{{ref{i}}}\n"
                f"  {', '.join(p['authors'][:3])} ({year}).\n"
                f"  \\textit{{{p['title']}}}.\n"
                f"  \\url{{{p['url']}}}\n\n"
            )

        latex = (
            f"% Literature review generated by Research Literature Review Agent\n"
            f"% Topic: {topic}\n\n"
            f"\\section{{Related Work}}\n\n"
            f"{safe_review}\n\n"
            f"\\begin{{thebibliography}}{{99}}\n"
            f"{bibitems}"
            f"\\end{{thebibliography}}\n"
        )
        return latex

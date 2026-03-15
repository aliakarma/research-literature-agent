"""
research_agent/summarizer.py
-----------------------------
Per-paper LLM summarization using the modern LangChain LCEL pipe syntax.
"""
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from research_agent.config import Config

SUMMARIZATION_PROMPT = PromptTemplate(
    input_variables=["title", "abstract"],
    template="""You are a research assistant writing structured summaries for an academic literature review.

Given the paper title and abstract below, write a concise 2-4 sentence summary that covers:
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
    """Uses an LLM to produce structured per-paper summaries."""

    def __init__(self, config: Config) -> None:
        self.config = config
        llm = ChatOpenAI(
            model=config.summarization_model,
            temperature=config.summarization_temperature,
            openai_api_key=config.openai_api_key,
        )
        # Modern LCEL chain: prompt | llm | output_parser
        self._chain = SUMMARIZATION_PROMPT | llm | StrOutputParser()

    def summarize_paper(self, paper: Dict) -> str:
        result = self._chain.invoke({
            "title":    paper["title"],
            "abstract": paper["abstract"],
        })
        return result.strip()

    def summarize_all(self, papers: List[Dict]) -> List[Dict]:
        print(f"[Summarizer] Summarizing {len(papers)} papers...")
        for i, paper in enumerate(papers, 1):
            print(f"  [{i}/{len(papers)}] {paper['title'][:70]}...")
            paper["summary"] = self.summarize_paper(paper)
        print("[Summarizer] Done.\n")
        return papers

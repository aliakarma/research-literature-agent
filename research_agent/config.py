"""
research_agent/config.py
------------------------
Centralised configuration for the Literature Review Agent.

All tuneable parameters (model names, chunk sizes, API keys, output paths)
live here so nothing is scattered across modules. Change behaviour by editing
this file or by passing a Config object directly to any pipeline component.

Environment variables always take precedence over default values.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (harmless if absent)
load_dotenv()


@dataclass
class Config:
    """
    Holds all runtime configuration for the agent.

    Attributes
    ----------
    openai_api_key : str
        Your OpenAI API key. Reads from OPENAI_API_KEY env var by default.
    summarization_model : str
        The LLM used for per-paper summarization.
        Default: "gpt-4o-mini" (fast and cost-efficient).
    synthesis_model : str
        The LLM used for the final literature review synthesis.
        Default: "gpt-4o" (higher quality for the critical final step).
    embedding_model : str
        OpenAI embedding model for vectorising paper text.
    max_papers : int
        Default number of arXiv papers to retrieve.
    chunk_size : int
        Character size of each text chunk before embedding.
    chunk_overlap : int
        Character overlap between adjacent chunks (preserves sentence continuity).
    retrieval_k : int
        Number of vector-store chunks returned per similarity query.
    summarization_temperature : float
        LLM temperature for summarization (lower = more factual).
    synthesis_temperature : float
        LLM temperature for synthesis (slightly higher for fluent prose).
    output_dir : Path
        Directory where generated reviews are saved.
    save_output : bool
        Whether to save the final review to disk automatically.
    arxiv_sort_by : str
        arXiv sort criterion: "relevance" | "lastUpdatedDate" | "submittedDate".
    """

    # ── API credentials ───────────────────────────────────────────────────────
    openai_api_key: str = field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")
    )

    # ── Model selection ───────────────────────────────────────────────────────
    summarization_model: str = field(
        default_factory=lambda: os.environ.get("SUMMARIZATION_MODEL", "gpt-4o-mini")
    )
    synthesis_model: str = field(
        default_factory=lambda: os.environ.get("SYNTHESIS_MODEL", "gpt-4o")
    )
    embedding_model: str = field(
        default_factory=lambda: os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    # ── Retrieval settings ────────────────────────────────────────────────────
    max_papers: int = field(
        default_factory=lambda: int(os.environ.get("MAX_PAPERS", "8"))
    )
    arxiv_sort_by: str = "relevance"

    # ── Chunking settings ─────────────────────────────────────────────────────
    chunk_size: int = 800
    chunk_overlap: int = 100

    # ── Vector store retrieval ────────────────────────────────────────────────
    retrieval_k: int = 6

    # ── LLM generation settings ───────────────────────────────────────────────
    summarization_temperature: float = 0.2
    synthesis_temperature: float = 0.3

    # ── Output settings ───────────────────────────────────────────────────────
    output_dir: Path = field(default_factory=lambda: Path("outputs"))
    save_output: bool = True

    def validate(self) -> None:
        """
        Raise a clear error if required configuration is missing.
        Call this at agent startup before any API calls are made.
        """
        if not self.openai_api_key:
            raise ValueError(
                "\n[Config] OpenAI API key is missing.\n"
                "  Set it with:  export OPENAI_API_KEY='sk-...'\n"
                "  Or create a .env file with OPENAI_API_KEY=sk-...\n"
                "  Or pass it directly: Config(openai_api_key='sk-...')"
            )
        if self.max_papers < 1 or self.max_papers > 50:
            raise ValueError("max_papers must be between 1 and 50.")
        if self.chunk_size < 200:
            raise ValueError("chunk_size must be at least 200 characters.")

    def __post_init__(self) -> None:
        """Ensure output_dir is always a Path object."""
        self.output_dir = Path(self.output_dir)

"""
examples/custom_config.py
--------------------------
Shows how to use a custom Config object to fine-tune the agent's behaviour:
  - Switch to a more powerful synthesis model
  - Increase paper count
  - Change chunk sizes for longer documents
  - Export LaTeX output

Run from the project root:
    python examples/custom_config.py
"""

from research_agent import run_literature_review_agent
from research_agent.config import Config

# ── Build a custom config ─────────────────────────────────────────────────────
config = Config(
    # API key from environment variable (default behaviour)
    # openai_api_key="sk-..."  # or set explicitly here

    # Model selection
    summarization_model="gpt-4o-mini",   # cost-efficient for per-paper step
    synthesis_model="gpt-4o",            # high quality for final synthesis

    # Retrieval
    max_papers=12,
    arxiv_sort_by="relevance",           # "relevance" | "submittedDate" | "lastUpdatedDate"

    # Chunking (increase chunk_size for longer documents like full PDFs)
    chunk_size=1000,
    chunk_overlap=150,

    # Output
    output_dir="outputs/custom",
    save_output=True,

    # LLM generation
    summarization_temperature=0.1,    # very factual summaries
    synthesis_temperature=0.4,        # slightly more creative synthesis
)

# Run the agent with the custom config
review = run_literature_review_agent(
    topic="large language models for scientific discovery",
    config=config,
    save_latex=True,   # also export a .tex file
)

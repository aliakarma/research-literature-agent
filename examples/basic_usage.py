"""
examples/basic_usage.py
------------------------
The simplest possible usage of the Literature Review Agent.

Run from the project root:
    python examples/basic_usage.py

Before running:
    export OPENAI_API_KEY="sk-..."
    pip install -r requirements.txt
"""

from research_agent import run_literature_review_agent

# ── Run the agent ─────────────────────────────────────────────────────────────
# This single function call runs the entire pipeline:
#   arXiv search → embedding → summarization → synthesis → output
review = run_literature_review_agent(
    topic="Agentic AI for climate prediction",
    max_papers=6,        # Start small to keep costs low
    save_txt=True,       # Save the review to outputs/
    save_latex=False,    # Set True if you want a .tex file
)

# The review string is also returned if you want to process it further
print("\nPipeline complete. Review has been printed above and saved to outputs/")

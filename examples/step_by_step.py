"""
examples/step_by_step.py
-------------------------
Runs the pipeline one stage at a time so you can inspect intermediate
results at each step. Useful for debugging or learning how the agent works.

Run from the project root:
    python examples/step_by_step.py
"""

import os
from research_agent.config import Config
from research_agent.arxiv_retriever import ArxivRetriever
from research_agent.vector_store import VectorStore
from research_agent.summarizer import Summarizer
from research_agent.literature_generator import LiteratureGenerator
from research_agent.utils import print_paper_table, print_banner, validate_papers

# ── Configuration ─────────────────────────────────────────────────────────────
config = Config(max_papers=5)   # API key read from OPENAI_API_KEY env var
config.validate()

TOPIC = "transformer models for protein structure prediction"

# ── STEP 1: Retrieve papers ───────────────────────────────────────────────────
print_banner("STEP 1: ArXiv Retrieval")
retriever = ArxivRetriever(config)
papers = retriever.search(TOPIC)
validate_papers(papers)
print_paper_table(papers)

# Show raw metadata for the first paper
print("First paper metadata:")
for key, val in papers[0].items():
    print(f"  {key}: {str(val)[:100]}")

input("\n[Press Enter to continue to Step 2]")

# ── STEP 2: Convert to text and build vector store ────────────────────────────
print_banner("STEP 2: Embedding + Vector Store")
doc_texts = ArxivRetriever.to_plain_text(papers)
print(f"\nExample document text (first 300 chars):\n{doc_texts[0][:300]}\n")

vs = VectorStore(config)
vs.build(doc_texts)

# Test similarity search
print("Semantic search test: 'attention mechanism protein folding'")
chunks = vs.retrieve("attention mechanism protein folding", k=2)
for i, c in enumerate(chunks, 1):
    print(f"\n  Chunk {i}:\n  {c[:200]}...")

input("\n[Press Enter to continue to Step 3]")

# ── STEP 3: Summarize papers ──────────────────────────────────────────────────
print_banner("STEP 3: LLM Summarization")
summarizer = Summarizer(config)
papers = summarizer.summarize_all(papers)

print("\nSummary for first paper:")
print(f"  TITLE  : {papers[0]['title']}")
print(f"  SUMMARY: {papers[0]['summary']}")

input("\n[Press Enter to continue to Step 4]")

# ── STEP 4: Synthesize literature review ─────────────────────────────────────
print_banner("STEP 4: Literature Synthesis")
generator = LiteratureGenerator(config)
review_text = generator.generate(TOPIC, papers)

print("\nGenerated review:\n")
print(review_text)

# ── STEP 5: Format and display ────────────────────────────────────────────────
print_banner("STEP 5: Final Formatted Output")
final = LiteratureGenerator.format_output(TOPIC, papers, review_text)
print(final)

print("\nDone! You can also export a LaTeX version with LiteratureGenerator.to_latex()")

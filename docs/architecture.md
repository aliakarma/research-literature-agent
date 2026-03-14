# System Architecture

This document explains every component of the Literature Review Agent pipeline
in detail, including design decisions and how to extend each part.

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RESEARCH LITERATURE REVIEW AGENT                        │
│                           v1.0.0 — Architecture                             │
└─────────────────────────────────────────────────────────────────────────────┘

  ╔══════════════╗
  ║  User Query  ║   e.g. "Agentic AI for climate prediction"
  ╚══════╤═══════╝
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │  1. Config & Validation                       │  config.py
  │     • Load API keys from environment          │
  │     • Validate all parameters                 │
  │     • Set model names, chunk sizes, etc.      │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  2. ArXiv Retrieval Agent                     │  arxiv_retriever.py
  │     • Query: arxiv.Search(topic, N)           │
  │     • Sort: by relevance                      │
  │     • Extract: title, abstract, authors,      │
  │       URL, date, paper_id                     │
  │     • Return: List[Dict]                      │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  3. Document Formatter                        │  arxiv_retriever.py
  │     • Convert Dict → plain text string        │
  │     • Format: TITLE / AUTHORS / DATE /        │
  │       URL / ABSTRACT                          │
  │     • Return: List[str]                       │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  4. Text Splitter                             │  vector_store.py
  │     • RecursiveCharacterTextSplitter          │
  │     • chunk_size=800, overlap=100             │
  │     • Splits at: paragraph → sentence → word  │
  │     • Return: List[Document] (LangChain)      │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  5. Embedding + Vector Store                  │  vector_store.py
  │     • Model: text-embedding-3-small (1536-D)  │
  │     • Store: FAISS flat index (exact search)  │
  │     • Exposes: .retrieve(query, k)            │
  │     • Optional: .save() / .load() to disk     │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  6. Summarization Agent                       │  summarizer.py
  │     • Model: gpt-4o-mini                      │
  │     • Temperature: 0.2 (factual)              │
  │     • Prompt: structured template             │
  │       → problem / method / results /          │
  │         limitations                           │
  │     • One LLM call per paper                  │
  │     • Adds paper["summary"] to each dict      │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  7. Literature Synthesis Agent                │  literature_generator.py
  │     • Model: gpt-4o                           │
  │     • Temperature: 0.3                        │
  │     • Input: all summaries concatenated       │
  │     • Output: 3-paragraph structured review   │
  │       → Trends / Methods / Gaps               │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │  8. Output Formatter                          │  literature_generator.py
  │     • Plain text block (print + .txt save)    │
  │     • LaTeX snippet (.tex export, optional)   │
  │     • Numbered reference list                 │
  └──────────────────────────────────────────────┘
```

---

## Component Details

### 1. Config (`config.py`)

A Python `@dataclass` that holds every tuneable parameter in one place.
Environment variables (from `.env` or shell) always take precedence over
defaults. Call `config.validate()` at startup to catch missing keys early.

**Why a dataclass?** It provides `__repr__` for free (useful for logging),
makes all fields inspectable, and is easy to pass between modules without
a global singleton or dependency injection framework.

---

### 2. ArxivRetriever (`arxiv_retriever.py`)

Wraps the `arxiv` Python library. The arXiv REST API accepts a query string
and returns metadata for matching papers. No authentication is required.

**Sort options:**
- `relevance` (default) — best for topic-based surveys
- `submittedDate` — best for tracking recent developments
- `lastUpdatedDate` — best for following ongoing work

**Scaling:** arXiv recommends staying under 3 requests/second for automated
clients. The `arxiv` library handles basic rate limiting internally.

---

### 3. VectorStore (`vector_store.py`)

**Why embed at all?** For 8 papers, you could pass all abstracts directly to
the LLM. But embeddings future-proof the system: when you add full-PDF
support (hundreds of pages per paper, dozens of papers), direct inclusion
becomes impossible. The vector store also enables semantic search — finding
the most relevant context for any query, not just keyword matching.

**FAISS flat index** performs exact nearest-neighbour search. For up to ~10,000
vectors (roughly 100 full papers split into chunks), this is the right choice.
For larger corpora, switch to `FAISS.IndexIVFFlat` or `IndexHNSWFlat`.

**Persistence:** `.save(path)` serialises the index to disk. This means you can
embed once and re-run synthesis without paying embedding API costs again.

---

### 4. Summarizer (`summarizer.py`)

**Why `gpt-4o-mini` here?** Summarization is a straightforward extraction task —
the model is reading one abstract and pulling out structured information.
The cheaper, faster model handles this reliably at ~$0.0001 per paper.

**Why low temperature (0.2)?** We want the summary to reflect what is actually
in the abstract, not the model's prior knowledge about the topic.

**Prompt design:** The template uses explicit output sections (problem, method,
results, limitations) rather than asking for "a summary". This produces
consistently structured output that the synthesis agent can reason across.

---

### 5. LiteratureGenerator (`literature_generator.py`)

**Why `gpt-4o` here?** Synthesis is cognitively harder than summarization.
The model must hold all papers in context simultaneously, identify patterns,
resolve tensions between studies, and produce a coherent narrative. The
stronger model produces noticeably better cross-paper reasoning.

**Three-paragraph structure** mirrors the conventional structure of Related Work
sections in AI/CS papers: situate the field (context), describe what has been
done (methods/contributions), then motivate the current work (gaps).

**LaTeX export** via `.to_latex()` produces a snippet with `\section{Related Work}`,
escaped special characters, and `\bibitem` entries — ready to paste into any
`.tex` file.

---

## Data Flow Summary

| Stage | Input | Output | Where |
|-------|-------|--------|-------|
| Retrieval | query string | `List[Dict]` | `ArxivRetriever.search()` |
| Formatting | `List[Dict]` | `List[str]` | `ArxivRetriever.to_plain_text()` |
| Chunking | `List[str]` | `List[Document]` | `VectorStore.build()` |
| Embedding | `List[Document]` | FAISS index | `VectorStore.build()` |
| Retrieval | query string | `List[str]` | `VectorStore.retrieve()` |
| Summarization | `List[Dict]` | `List[Dict]` + `summary` key | `Summarizer.summarize_all()` |
| Synthesis | `topic` + summaries | review paragraph string | `LiteratureGenerator.generate()` |
| Formatting | review + papers | formatted output string | `LiteratureGenerator.format_output()` |

---

## Extension Points

| Feature | Where to add | Notes |
|---------|-------------|-------|
| New paper source (Semantic Scholar) | New `semantic_scholar_retriever.py` | Match `ArxivRetriever` interface |
| New vector backend (ChromaDB) | New `chroma_store.py` | Match `VectorStore` interface |
| Full PDF parsing | `arxiv_retriever.py` | Use `arxiv` download + `PyMuPDF` |
| Citation extraction | New `citation_extractor.py` | Use GROBID or regex on PDF text |
| BibTeX export | `literature_generator.py` | Add `to_bibtex()` method |
| Streamlit UI | New `app.py` | Call `run_literature_review_agent()` |
| Multi-agent orchestration | `agent.py` | Use LangGraph for branching / parallel agents |

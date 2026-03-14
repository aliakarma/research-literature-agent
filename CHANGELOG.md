# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025-01-01

### Added
- Initial release of the Research Literature Review Agent
- `ArxivRetriever` — arXiv paper search and metadata extraction
- `VectorStore` — OpenAI embeddings + FAISS similarity index with `.save()` / `.load()`
- `Summarizer` — per-paper LLM summarization using `gpt-4o-mini`
- `LiteratureGenerator` — multi-paper synthesis using `gpt-4o` with LaTeX export
- `Config` dataclass with environment-variable overrides and validation
- `utils.py` — shared helpers: `timer()`, `save_review()`, `sanitise_filename()`,
  `print_paper_table()`, `validate_papers()`
- `agent.py` — full pipeline orchestration with Python API and CLI
- Google Colab-compatible `demo.ipynb` notebook
- Unit tests for all modules (no real API calls required)
- GitHub Actions CI workflow (Python 3.10, 3.11, 3.12)
- `pyproject.toml` with Ruff, Black, mypy, and pytest configuration

---

## [Unreleased]

### Planned
- ChromaDB backend as alternative to FAISS
- Semantic Scholar and PubMed retrieval alongside arXiv
- Full-text PDF parsing via PyMuPDF (currently abstract-only)
- BibTeX `.bib` file export
- Multi-agent orchestration with LangGraph
- Knowledge graph construction with NetworkX
- Citation network visualisation
- Streamlit web interface

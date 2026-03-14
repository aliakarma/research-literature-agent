# Contributing to Research Literature Review Agent

Thank you for your interest in contributing! This document explains how to set up
a development environment, run tests, and submit changes.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Adding a New Feature](#adding-a-new-feature)
- [Reporting Bugs](#reporting-bugs)

---

## Development Setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/research-literature-agent.git
cd research-literature-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"
# or equivalently:
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .

# 4. Create your .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

---

## Project Structure

```
research-literature-agent/
│
├── research_agent/           # Source package (all business logic lives here)
│   ├── __init__.py           # Public API
│   ├── config.py             # Centralised configuration
│   ├── arxiv_retriever.py    # arXiv paper fetching
│   ├── vector_store.py       # Embedding + FAISS indexing
│   ├── summarizer.py         # Per-paper LLM summarization
│   ├── literature_generator.py  # Multi-paper synthesis + formatting
│   ├── agent.py              # Pipeline orchestration + CLI
│   └── utils.py              # Shared helpers
│
├── tests/                    # Pytest unit tests (no real API calls)
├── examples/                 # Runnable usage examples
├── docs/                     # Extended documentation
├── .github/workflows/        # GitHub Actions CI
│
├── demo.ipynb                # Google Colab notebook
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Dev/test dependencies
├── pyproject.toml            # Package config + tool settings
└── README.md
```

---

## Running Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=research_agent --cov-report=term-missing

# Run only a specific test file
pytest tests/test_arxiv_retriever.py -v

# Run integration tests (requires real OPENAI_API_KEY — costs money)
pytest tests/ -m integration -v
```

Unit tests are in `tests/` and use `unittest.mock` to avoid real API calls.
They run in <10 seconds and cost nothing.

Integration tests (marked `@pytest.mark.integration`) make real API calls.
They are excluded from CI and should be run manually before submitting a PR
that changes core LLM logic.

---

## Code Style

This project uses **Black** for formatting and **Ruff** for linting.

```bash
# Format all files
black research_agent/ tests/ examples/

# Lint and auto-fix
ruff check research_agent/ tests/ --fix

# Type check
mypy research_agent/
```

The CI pipeline enforces these on every push. Your PR will fail CI if it
introduces linting errors or formatting inconsistencies.

Key conventions:
- **Docstrings**: All public classes and functions must have docstrings.
  Use the NumPy docstring format (Parameters / Returns / Example sections).
- **Type hints**: All function signatures must include type hints.
- **Comments**: Explain *why*, not *what*. Complex logic should have an
  explanatory comment above it, not just an inline comment re-stating the code.

---

## Submitting a Pull Request

1. **Create a branch** for your change:
   ```bash
   git checkout -b feature/my-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Write tests** for any new behaviour. PRs without tests for new features
   will be asked to add them before merging.

3. **Run the full test suite** and ensure it passes:
   ```bash
   pytest tests/ -m "not integration"
   black --check research_agent/ tests/
   ruff check research_agent/ tests/
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add ChromaDB backend as alternative to FAISS"
   git commit -m "fix: handle empty author list in ArxivRetriever"
   git commit -m "docs: add step-by-step tutorial to README"
   ```
   We follow [Conventional Commits](https://www.conventionalcommits.org/) loosely.

5. **Push and open a PR** against the `main` branch. Fill in the PR template
   describing what the change does and why.

---

## Adding a New Feature

### Example: Adding a new vector store backend (ChromaDB)

1. Create `research_agent/chroma_store.py` implementing the same interface as
   `VectorStore` (`.build()`, `.retrieve()`, `.save()`, `.load()`).
2. Add `chromadb` to `requirements.txt` as an optional dependency.
3. Add a `vector_backend: str` field to `Config` (`"faiss"` | `"chroma"`).
4. Update `agent.py` to select the backend based on `config.vector_backend`.
5. Add tests in `tests/test_chroma_store.py`.
6. Add an example in `examples/use_chromadb.py`.
7. Update README with instructions and a comparison table.

### Example: Adding a new paper source (Semantic Scholar)

1. Create `research_agent/semantic_scholar_retriever.py` implementing the same
   interface as `ArxivRetriever` (`.search()` returning the same dict format).
2. Add `source: str` to `Config` (`"arxiv"` | `"semantic_scholar"`).
3. Update `agent.py` to select the retriever.
4. Add tests and an example.

The modular design means adding a new component rarely requires changing
existing modules.

---

## Reporting Bugs

Please open a GitHub Issue with:

- **Python version** and OS
- **Package versions**: `pip freeze | grep -E "langchain|openai|arxiv|faiss"`
- **Minimal reproducible example** (the smallest code that triggers the bug)
- **Full traceback** if applicable
- **Expected vs actual behaviour**

---

## Questions?

Open a GitHub Discussion or file an Issue tagged `question`.

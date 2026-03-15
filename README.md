# 📚 Research Literature Review Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/LangChain-0.2+-1C3C3C?logo=chainlink&logoColor=white" alt="LangChain"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white" alt="arXiv"/>
  <img src="https://img.shields.io/badge/FAISS-Vector_Store-0467DF" alt="FAISS"/>
  <img src="https://img.shields.io/badge/CI-Passing-22c55e?logo=githubactions&logoColor=white" alt="CI"/>
  <img src="https://img.shields.io/badge/License-MIT-94a3b8" alt="MIT License"/>
</p>

<p align="center">
  <b>Automatically generate publication-quality literature reviews from arXiv papers.</b><br/>
  Powered by LangChain · OpenAI GPT-4o · FAISS · arXiv API
</p>

---

## What It Does

Writing a literature review means reading dozens of papers, identifying patterns,
and synthesising findings into a coherent academic narrative. This agent automates
the entire workflow:

1. You provide a **research topic** (one line of text)
2. The agent **retrieves the most relevant papers** from arXiv
3. Each paper is **individually summarised** by an LLM
4. All summaries are **synthesised** into a 3-paragraph literature review covering:
   - Research trends and context
   - Methods and key contributions
   - Research gaps and future directions
5. Output is printed, saved as `.txt`, and optionally exported as **LaTeX** (`.tex`)
   ready to paste into your paper's `\section{Related Work}`

---

## Example

**Input:**
```
"Agentic AI for climate prediction"
```

**Output (excerpt):**
```
Recent research at the intersection of agentic AI and climate prediction has
coalesced around two dominant paradigms: model-based reinforcement learning
agents trained on ERA5 reanalysis datasets, and multi-agent cooperative
frameworks that partition atmospheric prediction across spatial scales.
Foundational contributions by Chen et al. established transformer-based
architectures as competitive baselines for short-range forecasting, while
subsequent work demonstrated that hierarchical agent designs can reduce
prediction error by up to 18% relative on standard benchmarks...

Significant methodological diversity characterises the field. Liu et al.
proposed a Lagrangian constraint approach that enforces physical conservation
laws as hard regularisers within a multi-agent training loop...

Despite these advances, substantial gaps remain. Fewer than half of reviewed
studies benchmark against a common held-out test set, making cross-study
comparison unreliable. Long-horizon prediction beyond five days remains
largely unexplored in the agentic setting...
```

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                  RESEARCH LITERATURE REVIEW AGENT                 │
└───────────────────────────────────────────────────────────────────┘

  User Query: "Agentic AI for climate prediction"
       │
       ▼
  ┌─────────────────────────────┐
  │  1. ArXiv Retrieval         │  arxiv_retriever.py
  │     arxiv.Search(topic, N)  │  → List[Dict]  (title, abstract, authors…)
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │  2. Text Chunking           │  vector_store.py
  │     RecursiveCharSplitter   │  → List[Document] (800-char chunks)
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │  3. Embedding + FAISS Index │  vector_store.py
  │     text-embedding-3-small  │  → Semantic similarity search
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │  4. Summarization Agent     │  summarizer.py
  │     gpt-4o-mini × N papers  │  → paper["summary"] per paper
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │  5. Synthesis Agent         │  literature_generator.py
  │     gpt-4o                  │  → 3-paragraph literature review
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │  6. Output                  │  agent.py
  │     .txt  /  .tex  /  CLI   │  → Saved file + console print
  └─────────────────────────────┘
```

**Full architecture docs:** [`docs/architecture.md`](docs/architecture.md)

---

## Repository Structure

```
research-literature-agent/
│
├── research_agent/               # Source package
│   ├── __init__.py               # Public API exports
│   ├── config.py                 # Centralised configuration + validation
│   ├── arxiv_retriever.py        # arXiv search and metadata extraction
│   ├── vector_store.py           # Text embedding + FAISS index
│   ├── summarizer.py             # Per-paper LLM summarization
│   ├── literature_generator.py   # Multi-paper synthesis + LaTeX export
│   ├── agent.py                  # Pipeline orchestration + CLI entry point
│   └── utils.py                  # Shared helpers (timer, save, validate…)
│
├── tests/                        # Unit tests (no real API calls)
│   ├── __init__.py
│   ├── test_arxiv_retriever.py
│   ├── test_config.py
│   ├── test_literature_generator.py
│   └── test_utils.py
│
├── examples/                     # Runnable usage examples
│   ├── basic_usage.py            # Minimal single-function example
│   ├── custom_config.py          # Using a custom Config object
│   └── step_by_step.py           # Inspect each pipeline stage interactively
│
├── docs/                         # Extended documentation
│   ├── architecture.md           # Component-by-component architecture guide
│   ├── api_reference.md          # Full API reference for all classes
│   └── research_potential.md     # How to extend this into a publishable paper
│
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions: lint + test on Python 3.10/11/12
│
├── demo.ipynb                    # Google Colab notebook (zero local setup)
├── pyproject.toml                # Package config + Black / Ruff / mypy / pytest
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Dev/test dependencies
├── .env.example                  # API key template (copy to .env)
├── .gitignore
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE                       # MIT
```

---

## Installation

### Option A — Google Colab (no local setup required)

Open [`demo.ipynb`](demo.ipynb) in Google Colab:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aliakarma/research-literature-agent/blob/main/demo.ipynb)

1. Click the 🔑 **Secrets** icon in the left sidebar
2. Add a secret: **Name** = `OPENAI_API_KEY`, **Value** = `sk-...`
3. Run all cells in order

---

### Option B — Local Environment

**Prerequisites:** Python 3.10+, an [OpenAI API key](https://platform.openai.com/api-keys)

```bash
# 1. Clone
git clone https://github.com/aliakarma/research-literature-agent.git
cd research-literature-agent

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

---

## Usage

### Command Line

```bash
# Basic usage
python -m research_agent.agent --topic "Agentic AI for climate prediction"

# More papers, with LaTeX export
python -m research_agent.agent \
  --topic "multi-agent reinforcement learning for robotics" \
  --max_papers 12 \
  --latex

# All options
python -m research_agent.agent --help
```

```
usage: research-agent [-h] --topic TOPIC [--max_papers N]
                      [--output_dir OUTPUT_DIR] [--no_save] [--latex]

options:
  --topic TOPIC           Research topic (required)
  --max_papers N          Papers to retrieve, default 8
  --output_dir OUTPUT_DIR Save directory, default outputs/
  --no_save               Do not write output files
  --latex                 Also export a .tex file
```

---

### Python API

```python
from research_agent import run_literature_review_agent

# Minimal — reads OPENAI_API_KEY from environment
review = run_literature_review_agent("trustworthy machine learning")

# Full control
review = run_literature_review_agent(
    topic="federated learning for healthcare",
    max_papers=10,
    save_txt=True,
    save_latex=True,
    output_dir="outputs/healthcare",
)
```

---

### Advanced: Custom Configuration

```python
from research_agent import run_literature_review_agent
from research_agent.config import Config

config = Config(
    summarization_model="gpt-4o-mini",
    synthesis_model="gpt-4o",
    max_papers=15,
    chunk_size=1000,          # larger chunks for full-PDF use cases
    summarization_temperature=0.1,
    synthesis_temperature=0.4,
    output_dir="outputs/my_project",
)

review = run_literature_review_agent(
    topic="knowledge graph completion with LLMs",
    config=config,
    save_latex=True,
)
```

---

### Advanced: Use Individual Pipeline Stages

```python
from research_agent.config import Config
from research_agent.arxiv_retriever import ArxivRetriever
from research_agent.vector_store import VectorStore
from research_agent.summarizer import Summarizer
from research_agent.literature_generator import LiteratureGenerator

config = Config()

# Retrieve
retriever = ArxivRetriever(config)
papers = retriever.search("explainable AI for medical diagnosis", max_results=8)

# Embed and index
doc_texts = ArxivRetriever.to_plain_text(papers)
vs = VectorStore(config)
vs.build(doc_texts)
vs.save("faiss_index/xai_medical")  # save for reuse

# Summarize
summarizer = Summarizer(config)
papers = summarizer.summarize_all(papers)
print(papers[0]["summary"])

# Synthesize
generator = LiteratureGenerator(config)
review = generator.generate("explainable AI for medical diagnosis", papers)

# Export LaTeX
latex = LiteratureGenerator.to_latex("explainable AI for medical diagnosis", papers, review)
with open("related_work.tex", "w") as f:
    f.write(latex)
```

---

## API Key Setup

**Never hardcode API keys in source files.** Use one of these approaches:

### `.env` file (recommended for local development)

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

The agent loads this automatically via `python-dotenv`.

### Google Colab Secrets

In Colab's left sidebar → 🔑 Secrets → Add:
- Name: `OPENAI_API_KEY`
- Value: `sk-...`
- Enable access for this notebook: ✓

Then in your notebook:
```python
from google.colab import userdata
import os
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
```

### Shell environment variable

```bash
export OPENAI_API_KEY="sk-your-key-here"   # Linux/macOS
set OPENAI_API_KEY=sk-your-key-here        # Windows CMD
```

---

## Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all unit tests (no API calls, no cost)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=research_agent --cov-report=term-missing

# Run a specific file
pytest tests/test_arxiv_retriever.py -v
```

Unit tests use `unittest.mock` to patch the arXiv API and LLM calls.
They run in under 10 seconds and require no API key.

---

## Estimated API Cost

| Configuration | Papers | Approx. cost |
|--------------|--------|-------------|
| 5 papers, mini synthesis | 5 | ~$0.01 |
| 8 papers, gpt-4o synthesis | 8 | ~$0.05 |
| 15 papers, gpt-4o synthesis | 15 | ~$0.15 |
| 50 papers, gpt-4o synthesis | 50 | ~$0.60 |

*Costs depend on abstract length and current OpenAI pricing.*
*Embeddings (text-embedding-3-small) cost ~$0.02 per 1M tokens — negligible here.*

---

## Future Roadmap

| Feature | Status |
|---------|--------|
| Full PDF parsing (PyMuPDF) | Planned |
| ChromaDB vector backend | Planned |
| Semantic Scholar + PubMed retrieval | Planned |
| BibTeX `.bib` file export | Planned |
| Multi-agent orchestration (LangGraph) | Planned |
| Citation network graph (NetworkX) | Planned |
| Streamlit web interface | Planned |
| Research trend analysis over time | Planned |
| Multilingual support | Planned |

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style (Black + Ruff)
- How to write tests
- PR workflow

---


## Documentation Index

| Document | Contents |
|----------|---------|
| [Architecture Guide](docs/architecture.md) | Component diagrams, design decisions, extension points |
| [API Reference](docs/api_reference.md) | Full reference for every class and function |
| [Research Potential](docs/research_potential.md) | How to extend this into a publishable paper |
| [Contributing Guide](CONTRIBUTING.md) | Dev setup, test guide, PR workflow |
| [Changelog](CHANGELOG.md) | Version history |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with <a href="https://langchain.com">LangChain</a> · <a href="https://openai.com">OpenAI</a> · <a href="https://arxiv.org">arXiv</a> · <a href="https://github.com/facebookresearch/faiss">FAISS</a></p>

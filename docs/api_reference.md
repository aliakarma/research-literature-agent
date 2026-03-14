# API Reference

Complete reference for all public classes and functions.

---

## `run_literature_review_agent` (Top-Level Function)

```python
from research_agent import run_literature_review_agent
```

The single entry point for running the full pipeline.

### Signature

```python
def run_literature_review_agent(
    topic: str,
    max_papers: int = 8,
    openai_api_key: Optional[str] = None,
    save_txt: bool = True,
    save_latex: bool = False,
    output_dir: str = "outputs",
    config: Optional[Config] = None,
) -> str
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | `str` | required | Natural language research topic |
| `max_papers` | `int` | `8` | Papers to retrieve from arXiv (1–50) |
| `openai_api_key` | `str` | `None` | API key; reads `OPENAI_API_KEY` if `None` |
| `save_txt` | `bool` | `True` | Save plain-text review to `output_dir/` |
| `save_latex` | `bool` | `False` | Also save a `.tex` export |
| `output_dir` | `str` | `"outputs"` | Directory for saved files |
| `config` | `Config` | `None` | Pre-built config; overrides all other params |

### Returns

`str` — The formatted literature review (also printed to stdout).

### Raises

| Exception | When |
|-----------|------|
| `ValueError` | API key missing or `max_papers` out of range |
| `RuntimeError` | No papers found for the topic |

### Example

```python
review = run_literature_review_agent(
    topic="transformer models for protein folding",
    max_papers=10,
    save_latex=True,
)
```

---

## `Config`

```python
from research_agent import Config
```

Centralised configuration dataclass. All fields have sensible defaults.
Environment variables always override defaults.

### Fields

| Field | Type | Default | Env var |
|-------|------|---------|---------|
| `openai_api_key` | `str` | `""` | `OPENAI_API_KEY` |
| `summarization_model` | `str` | `"gpt-4o-mini"` | `SUMMARIZATION_MODEL` |
| `synthesis_model` | `str` | `"gpt-4o"` | `SYNTHESIS_MODEL` |
| `embedding_model` | `str` | `"text-embedding-3-small"` | `EMBEDDING_MODEL` |
| `max_papers` | `int` | `8` | `MAX_PAPERS` |
| `arxiv_sort_by` | `str` | `"relevance"` | — |
| `chunk_size` | `int` | `800` | — |
| `chunk_overlap` | `int` | `100` | — |
| `retrieval_k` | `int` | `6` | — |
| `summarization_temperature` | `float` | `0.2` | — |
| `synthesis_temperature` | `float` | `0.3` | — |
| `output_dir` | `Path` | `Path("outputs")` | — |
| `save_output` | `bool` | `True` | — |

### Methods

#### `Config.validate() -> None`

Raises `ValueError` if required configuration is missing or invalid.
Call this before making any API calls.

---

## `ArxivRetriever`

```python
from research_agent import ArxivRetriever
```

### Constructor

```python
ArxivRetriever(config: Config)
```

### Methods

#### `search(query, max_results=None) -> List[Dict]`

Search arXiv. Returns a list of paper dicts with keys:
`title`, `authors`, `abstract`, `url`, `date`, `paper_id`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Natural language search topic |
| `max_results` | `int` | Override `config.max_papers` |

#### `to_plain_text(papers) -> List[str]` *(static)*

Convert paper dicts to formatted plain-text strings for embedding.

---

## `VectorStore`

```python
from research_agent import VectorStore
```

### Constructor

```python
VectorStore(config: Config)
```

### Methods

#### `build(texts: List[str]) -> None`

Chunk, embed, and index a list of paper text strings. Must be called
before `retrieve()`.

#### `retrieve(query, k=None) -> List[str]`

Return the `k` most semantically similar text chunks.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |
| `k` | `int` | Number of results; defaults to `config.retrieval_k` |

#### `save(path: str) -> None`

Persist the FAISS index to disk.

#### `load(path: str) -> None`

Load a previously saved index from disk.

---

## `Summarizer`

```python
from research_agent import Summarizer
```

### Constructor

```python
Summarizer(config: Config)
```

### Methods

#### `summarize_paper(paper: Dict) -> str`

Summarize a single paper. Returns a 2–4 sentence summary string.

#### `summarize_all(papers: List[Dict]) -> List[Dict]`

Summarize all papers. Adds `paper["summary"]` to each dict in place.
Returns the modified list.

---

## `LiteratureGenerator`

```python
from research_agent import LiteratureGenerator
```

### Constructor

```python
LiteratureGenerator(config: Config)
```

### Methods

#### `generate(topic, papers) -> str`

Synthesize all paper summaries into a 3-paragraph literature review.

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | `str` | Research topic (used as context in prompt) |
| `papers` | `List[Dict]` | Papers with `"summary"` key populated |

#### `format_output(topic, papers, review) -> str` *(static)*

Wrap the review in a structured output block with a reference list.

#### `to_latex(topic, papers, review) -> str` *(static)*

Export as a LaTeX snippet with `\section{Related Work}` and `\bibitem` entries.

---

## Utility Functions (`utils.py`)

```python
from research_agent.utils import save_review, sanitise_filename, timer, print_paper_table, validate_papers
```

### `save_review(content, topic, output_dir, extension="txt") -> Path`

Save a string to a timestamped file. Creates `output_dir` if it does not exist.

### `sanitise_filename(text, max_length=50) -> str`

Convert an arbitrary string to a safe, lowercase filename fragment.

### `timer(label)` *(context manager)*

Print elapsed time for a code block.

```python
with timer("Retrieval"):
    papers = retriever.search(topic)
# prints: [Timer] Retrieval — 1.84s
```

### `print_paper_table(papers) -> None`

Print a compact table of paper titles and dates to stdout.

### `validate_papers(papers, min_count=2) -> None`

Raise `ValueError` if the paper list is too small to synthesize from.

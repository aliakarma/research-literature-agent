"""
research_agent/vector_store.py
-------------------------------
Converts paper text into dense vector embeddings and stores them in a
FAISS in-memory index for fast semantic similarity search.

WHAT IS AN EMBEDDING?
---------------------
An embedding model takes a piece of text and outputs a list of numbers
(a "vector"). Similar texts produce vectors that are numerically close.
For example, "weather forecasting with neural networks" and "deep learning
for atmospheric prediction" will have very similar vectors even though they
share no exact words.

WHAT IS FAISS?
--------------
FAISS (Facebook AI Similarity Search) is a library that stores millions of
vectors and finds the closest ones to a query vector in milliseconds. It is
used here in "flat" (exact search) mode since our dataset is small (<200 chunks).
For larger datasets, switch to an IVF or HNSW index.

WHAT IS TEXT SPLITTING?
-----------------------
LLMs and embedding models have maximum input lengths (context windows).
A paper abstract + title might be ~500 words — fine on its own. But to
handle longer PDFs in the future, we split every document into overlapping
chunks of `chunk_size` characters with `chunk_overlap` characters of overlap.
The overlap ensures no sentence is cut off at a boundary without its neighbour.

PIPELINE
--------
  List[str] (paper texts)
      → RecursiveCharacterTextSplitter → List[Document] (chunks)
      → OpenAIEmbeddings                → List[List[float]] (vectors)
      → FAISS.from_documents            → FAISS index
      → similarity_search(query, k)     → List[Document] (most relevant chunks)
"""

from typing import List
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from research_agent.config import Config


class VectorStore:
    """
    Wraps the full embedding + FAISS pipeline into a single reusable object.

    Parameters
    ----------
    config : Config
        Uses config.embedding_model, config.chunk_size,
        config.chunk_overlap, config.retrieval_k, config.openai_api_key.

    Example
    -------
    >>> vs = VectorStore(config)
    >>> vs.build(doc_texts)
    >>> chunks = vs.retrieve("deep learning precipitation", k=5)
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self._index: FAISS = None  # populated by .build()

        # ── Embedding model ──────────────────────────────────────────────────
        # text-embedding-3-small: 1536-dimensional vectors, fast, low cost.
        # text-embedding-3-large: higher quality, 3072-dimensional, ~6× more expensive.
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model,
            openai_api_key=config.openai_api_key,
        )

        # ── Text splitter ────────────────────────────────────────────────────
        # RecursiveCharacterTextSplitter tries to split at paragraph → sentence
        # → word boundaries in that order, so splits are semantically cleaner
        # than a naive fixed-character split.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
        )

    # ── Public methods ────────────────────────────────────────────────────────

    def build(self, texts: List[str]) -> None:
        """
        Chunk, embed, and index a list of plain-text paper strings.

        Parameters
        ----------
        texts : Output of ArxivRetriever.to_plain_text()
        """
        # Wrap each text string in a LangChain Document object.
        # Document pairs text with optional metadata (source, page, etc).
        documents = [Document(page_content=t) for t in texts]

        # Split into chunks
        chunks = self.splitter.split_documents(documents)
        print(f"[VectorStore] {len(documents)} documents → {len(chunks)} chunks.")

        # Embed and index — this makes one OpenAI API call per batch of chunks
        self._index = FAISS.from_documents(chunks, self.embeddings)
        print(f"[VectorStore] FAISS index ready.\n")

    def retrieve(self, query: str, k: int = None) -> List[str]:
        """
        Return the k most semantically similar chunks to a query string.

        Parameters
        ----------
        query : The search query (typically the research topic).
        k     : Number of chunks to return. Defaults to config.retrieval_k.

        Returns
        -------
        List of raw text strings from the most relevant chunks.
        """
        if self._index is None:
            raise RuntimeError("Call VectorStore.build() before retrieve().")
        if k is None:
            k = self.config.retrieval_k

        results = self._index.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def save(self, path: str) -> None:
        """Persist the FAISS index to disk for reuse across sessions."""
        if self._index is None:
            raise RuntimeError("No index to save. Call build() first.")
        self._index.save_local(path)
        print(f"[VectorStore] Index saved to: {path}")

    def load(self, path: str) -> None:
        """Load a previously saved FAISS index from disk."""
        self._index = FAISS.load_local(
            path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        print(f"[VectorStore] Index loaded from: {path}")

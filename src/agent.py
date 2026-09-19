from typing import Any, Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(
        self,
        question: str,
        top_k: int = 3,
        metadata_filter: dict[str, Any] | None = None,
    ) -> str:
        """Answer a question, optionally restricting retrieval by metadata."""
        results = self.store.search_with_filter(
            question, top_k=top_k, metadata_filter=metadata_filter
        )
        context = "\n\n".join(
            f"[{index}] {result['content']}"
            for index, result in enumerate(results, start=1)
        )
        prompt = (
            "Answer the question using only the provided context. "
            "If the context is insufficient, say so.\n\n"
            f"Context:\n{context or '(No relevant context found.)'}\n\n"
            f"Question: {question}\nAnswer:"
        )
        return self.llm_fn(prompt)

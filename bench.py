"""Run the group's benchmark queries against the local university corpus.

Set EMBEDDING_PROVIDER=gemini to run the same benchmark with Gemini embeddings.
Without that setting, it defaults to MockEmbedder for the required classroom
configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from src import (
    Document,
    EMBEDDING_PROVIDER_ENV,
    EmbeddingStore,
    FixedSizeChunker,
    GeminiEmbedder,
    KnowledgeBaseAgent,
    LocalEmbedder,
    MockEmbedder,
    RecursiveChunker,
    SentenceChunker,
    compute_similarity,
)


CORPUS_DIR = Path("data/university")
OUTPUT_PATH = Path("ket_qua_benchmark.txt")
SKIP_FILES = {"BENCHMARK.md", "MANIFEST.md", "README.md"}
SIMILARITY_PAIRS = [
    (
        "Làm thế nào để đăng ký thêm một học phần?",
        "Tôi muốn bổ sung môn học vào kế hoạch học kỳ.",
        "cao",
    ),
    (
        "Điều kiện xét tốt nghiệp gồm những gì?",
        "Quy trình phân công cán bộ coi thi ra sao?",
        "thấp",
    ),
    (
        "Cách tính điểm trung bình học kỳ như thế nào?",
        "Công thức tính ĐTBHK là gì?",
        "cao",
    ),
    (
        "Người học sử dụng hệ thống dạy học trực tuyến như thế nào?",
        "Khi nào văn bằng hoặc chứng chỉ bị thu hồi?",
        "thấp",
    ),
    (
        "Giảng viên cần đáp ứng tiêu chuẩn nào để dạy môn học?",
        "Yêu cầu đối với trợ giảng môn học là gì?",
        "cao",
    ),
]


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    """Return simple YAML front matter and cleaned body for one Markdown file."""
    raw = path.read_text(encoding="utf-8")
    if not raw.lstrip().startswith("---") or raw.count("---") < 2:
        raise ValueError(f"Missing YAML front matter: {path}")
    _, frontmatter, body = raw.split("---", 2)
    metadata = dict(re.findall(r"^(\w+):\s*\"?(.+?)\"?\s*$", frontmatter, re.M))
    return metadata, body.strip()


def load_chunked_documents(
    chunker, allowed_doc_ids: set[str] | None = None
) -> list[Document]:
    """Load each corpus document and create one Document per retrieval chunk."""
    chunked_documents: list[Document] = []

    for path in sorted(CORPUS_DIR.glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        try:
            metadata, body = parse_frontmatter(path)
        except ValueError as error:
            print(f"Skipping {path.name}: {error}")
            continue
        if allowed_doc_ids is not None and metadata.get("doc_id") not in allowed_doc_ids:
            continue
        doc_id = metadata["doc_id"]
        for index, chunk in enumerate(chunker.chunk(body), start=1):
            chunked_documents.append(
                Document(
                    id=f"{doc_id}-chunk-{index}",
                    content=chunk,
                    metadata={**metadata, "doc_id": doc_id, "chunk_index": index},
                )
            )
    return chunked_documents


def load_benchmarks() -> list[dict[str, object]]:
    """Parse the five Markdown-table queries in BENCHMARK.md."""
    benchmarks: list[dict[str, object]] = []
    for line in (CORPUS_DIR / "BENCHMARK.md").read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        benchmarks.append(
            {
                "number": int(cells[0]),
                "audience": cells[1].strip("`"),
                "query": cells[2],
                "gold_answer": cells[3],
                "expected_doc": cells[4].strip("`"),
                "metadata_filter": json.loads(cells[5].strip("`")),
            }
        )
    return benchmarks


def extractive_llm(prompt: str) -> str:
    """Offline fallback: return the first retrieved chunk instead of inventing text."""
    context = prompt.split("Context:\n", 1)[1].split("\n\nQuestion:", 1)[0]
    return context.removeprefix("[1] ").strip()


def build_embedder(
    provider_override: str | None = None, local_model: str | None = None
):
    """Select the optional Gemini backend, or the default mock backend."""
    provider = (provider_override or os.getenv(EMBEDDING_PROVIDER_ENV, "mock")).strip().lower()
    if provider == "gemini":
        return provider, GeminiEmbedder()
    if provider == "local":
        return provider, LocalEmbedder(model_name=local_model) if local_model else LocalEmbedder()
    if provider in {"", "mock"}:
        return "mock", MockEmbedder()
    raise ValueError(
        f"Unsupported {EMBEDDING_PROVIDER_ENV}={provider!r}. "
        "Use 'mock', 'local', or 'gemini'."
    )


def similarity_lines(embedder) -> list[str]:
    """Calculate the five report-prediction scores with the selected backend."""
    backend_name = getattr(embedder, "_backend_name", type(embedder).__name__)
    lines = [f"Similarity predictions ({backend_name})", ""]
    for number, (sentence_a, sentence_b, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        # This threshold is only a reporting convention; mock vectors have no semantics.
        observed = "cao" if score >= 0.20 else "thấp"
        lines.extend(
            [
                f"Pair {number}: prediction={prediction}; observed={observed}; score={score:.4f}",
                f"  A: {sentence_a}",
                f"  B: {sentence_b}",
            ]
        )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("mock", "local", "gemini"))
    parser.add_argument(
        "--strategy", choices=("sentence", "fixed", "recursive"), default="sentence"
    )
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument("--sentences-per-chunk", type=int, default=3)
    parser.add_argument(
        "--doc-ids",
        help="Comma-separated doc_id values to index; defaults to the full corpus.",
    )
    parser.add_argument(
        "--local-model",
        help="Hugging Face model ID used only with --provider local.",
    )
    args = parser.parse_args()
    # A benchmark run should use the key currently saved in .env.  This avoids
    # accidentally retaining an older GEMINI_API_KEY from a PowerShell session.
    load_dotenv(dotenv_path=Path(".env"), override=True)
    if args.strategy == "fixed":
        chunker = FixedSizeChunker(chunk_size=args.chunk_size, overlap=args.overlap)
        strategy_label = (
            f"FixedSizeChunker(chunk_size={args.chunk_size}, overlap={args.overlap})"
        )
    elif args.strategy == "recursive":
        chunker = RecursiveChunker(chunk_size=args.chunk_size)
        strategy_label = f"RecursiveChunker(chunk_size={args.chunk_size})"
    else:
        chunker = SentenceChunker(max_sentences_per_chunk=args.sentences_per_chunk)
        strategy_label = (
            f"SentenceChunker(max_sentences_per_chunk={args.sentences_per_chunk})"
        )
    allowed_doc_ids = (
        {doc_id.strip() for doc_id in args.doc_ids.split(",") if doc_id.strip()}
        if args.doc_ids
        else None
    )
    documents = load_chunked_documents(chunker, allowed_doc_ids)
    if not documents:
        raise ValueError("No documents were loaded; check --doc-ids against front-matter doc_id.")
    provider, embedder = build_embedder(args.provider, args.local_model)
    store = EmbeddingStore(f"university-benchmark-{provider}", embedding_fn=embedder)
    store.add_documents(documents)
    agent = KnowledgeBaseAgent(store=store, llm_fn=extractive_llm)

    lines = similarity_lines(embedder) + [
        "",
        f"Benchmark: {getattr(embedder, '_backend_name', provider)} + {strategy_label}",
        f"Corpus documents: {len({doc.metadata['doc_id'] for doc in documents})}",
        f"Stored chunks: {store.get_collection_size()}",
        "",
    ]
    top3_hits = 0
    answer_hits = 0
    fully_correct = 0

    for benchmark in load_benchmarks():
        results = store.search_with_filter(
            benchmark["query"],
            top_k=3,
            metadata_filter=benchmark["metadata_filter"],
        )
        retrieved_doc_ids = [result["metadata"].get("doc_id") for result in results]
        hit = benchmark["expected_doc"] in retrieved_doc_ids
        agent_answer = agent.answer(
            benchmark["query"],
            top_k=3,
            metadata_filter=benchmark["metadata_filter"],
        )
        answer_has_gold = benchmark["gold_answer"].lower() in agent_answer.lower()
        top3_hits += int(hit)
        answer_hits += int(answer_has_gold)
        fully_correct += int(hit and answer_has_gold)

        lines.extend(
            [
                f"Query {benchmark['number']}: {benchmark['query']}",
                f"Audience: {benchmark['audience']}",
                f"Filter: {benchmark['metadata_filter']}",
                f"Expected document: {benchmark['expected_doc']}",
                f"Top-3 document IDs: {retrieved_doc_ids}",
                f"Top-3 hit: {'YES' if hit else 'NO'}",
                f"Agent extractive answer contains gold answer: {'YES' if answer_has_gold else 'NO'}",
                f"Agent answer preview: {agent_answer.replace(chr(10), ' ')[:240]}",
            ]
        )
        for rank, result in enumerate(results, start=1):
            preview = result["content"].replace("\n", " ")[:240]
            lines.append(
                f"  {rank}. score={result['score']:.4f}; "
                f"doc_id={result['metadata'].get('doc_id')}; preview={preview}"
            )
        lines.append("")

    lines.extend(
        [
            "Tổng kết benchmark",
            f"- Top-3 có đúng tài liệu nguồn: {top3_hits} / 5",
            f"- Câu trả lời chứa đáp án vàng: {answer_hits} / 5",
            f"- Đúng cả truy xuất và đáp án: {fully_correct} / 5",
        ]
    )

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

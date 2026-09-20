"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
    5. Nếu fallback lỗi, trả hybrid results thay vì crash.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


def _read_score_threshold() -> float:
    """Read a valid threshold, falling back safely when env is empty/invalid."""
    raw_value = os.getenv("SCORE_THRESHOLD", "0.35").strip()
    try:
        value = float(raw_value) if raw_value else 0.35
    except ValueError:
        value = 0.35
    return min(max(value, 0.0), 1.0)


SCORE_THRESHOLD = _read_score_threshold()
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult tuân thủ 3 quy tắc bắt buộc."""
    # 1. Lấy kết quả từ dense semantic search và lexical BM25
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    # 2. Quy tắc 1: rerank_rrf() chỉ gọi đúng một lần trong retrieve()
    hybrid = (
        rerank_rrf([dense, sparse], top_k=top_k)
        if use_reranking
        else dense[:top_k]
    )

    # 3. Quy tắc 2: Threshold so với cosine gốc của dense, KHÔNG phải điểm RRF
    best_dense_score = float(dense[0]["score"]) if dense else 0.0

    # 4. Nếu best cosine score < threshold -> kích hoạt fallback
    if best_dense_score < score_threshold:
        # Quy tắc 3: pageindex_search() bọc trong try/except, lỗi không crash và rơi về hybrid
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback
        except Exception as error:
            print(f"Fallback failed, reverting to hybrid: {error}")

    return hybrid[:top_k]


if __name__ == "__main__":
    in_domain_query = "cách viết mở bài và tổng quan cho IELTS Writing Task 1"
    print(f"Testing in-domain retrieval for: '{in_domain_query}'")
    results = retrieve(in_domain_query, top_k=3, score_threshold=0.3)
    for r in results:
        print(f"- [{r['retrieval_method'].upper()} | {r['score']:.4f}] {r['id']} ({r['metadata']['title']})")

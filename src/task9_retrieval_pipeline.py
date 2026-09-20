"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
    5. Nếu fallback lỗi hoặc rỗng, trả hybrid results thay vì crash.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


SCORE_THRESHOLD = 0.4
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
    # 1. Truy xuất danh sách ứng viên từ dense và lexical search
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    # 2. Fuse hai danh sách bằng RRF đúng MỘT lần
    if use_reranking:
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        hybrid = dense[:top_k]

    # 3. Lấy best cosine score gốc từ dense results để so sánh với threshold
    best_dense_score = dense[0]["score"] if dense else 0.0

    # 4. Nếu best cosine score gốc < threshold, kích hoạt fallback PageIndex
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
        except Exception:
            # Fallback provider lỗi không được làm crash UI, an toàn rơi về hybrid
            pass

    # 5. Mặc định trả về hybrid results
    return hybrid[:top_k]


if __name__ == "__main__":
    for res in retrieve("IELTS Writing Task 1 band descriptors", top_k=3):
        print(res)

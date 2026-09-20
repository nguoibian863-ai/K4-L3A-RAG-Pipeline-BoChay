# Individual contribution report

```text
reports/2A202602900-PhamQuangHuy.md
```

---

## Thông tin

- Họ và tên: Phạm Quang Huy
- Mã học viên: 2A202602900
- Nhóm: K4-Day08 (K4-Day08-BoChay)
- Repository/branch: nguoibian863-ai/K4-Day08-BoChay / main (và branch Huy)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 7 — Reranking với Reciprocal Rank Fusion (RRF) | Triển khai thuật toán RRF theo công thức chuẩn $RRF(d) = \sum \frac{1}{k + rank}$ (rank bắt đầu từ 1, $k=60$). Gộp 2 bảng xếp hạng dense và BM25, bảo tồn metadata, gán `retrieval_method="hybrid"`, sắp xếp giảm dần theo điểm RRF. | `src/task7_reranking.py`, commit `4fd3c33` | Done |
| Task 8 — PageIndex Vectorless Fallback | Thiết kế module fallback vectorless với PageIndex. Xử lý bọc lỗi `try...except` an toàn tuyệt đối, đảm bảo khi provider gặp sự cố mạng hoặc hết hạn ngạch API thì hệ thống không crash mà an toàn rơi về hybrid results. | `src/task8_pageindex_vectorless.py`, commit `4fd3c33` | Done |
| Task 9 — Retrieval Pipeline & Threshold Calibration | Tích hợp toàn bộ luồng `retrieve()`: gọi dense + BM25, gọi `rerank_rrf()` đúng duy nhất 1 lần, so sánh ngưỡng fallback với cosine score gốc của dense (`dense[0]["score"]`). Calibrate `SCORE_THRESHOLD = 0.40` trên câu hỏi in-domain và out-of-domain. | `src/task9_retrieval_pipeline.py`, `group_project/evaluation/RESULT.md`, commit `f6167b2` | Done |
| Task 4 — Pipeline Indexing vào ChromaDB | Chạy và giám sát quá trình chunking (1,213 chunks), embedding bằng mô hình `BAAI/bge-m3` và lưu trữ toàn bộ vector vào cơ sở dữ liệu `chroma_db/` (cosine distance). | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| Contract Testing & Quality Gate (Tasks 7–9) | Viết và chạy kiểm thử hợp đồng cho RRF, Fallback, tính duy nhất của RRF và khả năng sống sót khi provider lỗi. Đạt 100% test pass. | `tests/test_contracts.py` (4/4 passed), `tests/test_acceptance.py` (5/5 passed) | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng cosine similarity gốc của dense search (`dense[0]["score"]`) làm tiêu chí kích hoạt fallback thay vì dùng điểm số sau RRF.  
   **Lý do/evidence:** Điểm số RRF là hàm nghịch đảo thứ hạng $1/(k + rank)$ mang tính chất phân vị tương đối và giá trị luôn rất nhỏ ($\approx 0.01 - 0.03$), không phản ánh được mức độ tương đồng ngữ nghĩa thực sự với câu truy vấn. Trong khi đó, cosine score gốc ($0.0 - 1.0$) phân biệt rất rõ nét giữa câu hỏi đúng domain ($\approx 0.65 - 0.85$) và câu hỏi ngoài domain ($< 0.30$). Việc so sánh với cosine gốc giúp hệ thống đưa ra quyết định fallback chính xác tuyệt đối.  
   **Trade-off:** Cần lưu giữ và truyền giá trị cosine score ban đầu song song với quá trình tính toán RRF, tăng nhẹ kích thước dữ liệu xử lý trong bộ nhớ nhưng đổi lại là logic phân luồng chuẩn xác 100%.

2. **Quyết định:** Triển khai cơ chế Fail-Safe Resilient Fallback bọc kín `try...except` quanh `pageindex_search()`.  
   **Lý do/evidence:** PageIndex là dịch vụ API đám mây bên thứ ba có thể bị nghẽn mạng, timeout hoặc hết hạn ngạch truy vấn. Nếu để exception ném ra ngoài, toàn bộ ứng dụng chatbot Streamlit sẽ bị crash và ngắt quãng trải nghiệm người dùng. Khi bắt lỗi và rơi về hybrid, hệ thống duy trì được tính sẵn sàng cao (High Availability).  
   **Trade-off:** Trong tình huống API PageIndex bị lỗi, người dùng nhận được câu trả lời từ tài liệu có sẵn trong hệ thống (dù độ liên quan có thể thấp hơn) thay vì nhận thông báo lỗi hệ thống, nhưng đảm bảo giao diện luôn phản hồi liền mạch.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - Kiểm thử unit & demo Task 7: `python -m src.task7_reranking`
  - Kiểm thử hợp đồng RRF và Pipeline: `python -m pytest tests/test_contracts.py -k "rrf or retrieve" -v`
  - Kiểm thử toàn bộ tiêu chí chấp nhận: `python -m pytest tests/test_acceptance.py -v`
  - Query hiệu chuẩn ngưỡng:
    - In-domain: *"What are the 4 assessment criteria for IELTS Writing Task 1?"* $\rightarrow$ dense score $\approx 0.72 \ge 0.40$ (sử dụng hybrid kết hợp).
    - Out-of-domain: *"Công thức nấu phở bò Hà Nội truyền thống"* $\rightarrow$ dense score $\approx 0.24 < 0.40$ (kích hoạt fallback PageIndex).
- Kết quả trước/sau nếu có:
  - Trước: Module `task7_reranking.py` và `task9_retrieval_pipeline.py` ném lỗi `NotImplementedError`, các bài test hợp đồng `test_rrf_uses_rank_deduplicates_and_marks_hybrid`, `test_retrieve_uses_dense_score_for_fallback`, `test_retrieve_fuses_once_when_dense_is_confident`, `test_retrieve_survives_fallback_provider_error` đều thất bại.
  - Sau: Toàn bộ 4 test contracts liên quan đều PASSED 100%. Điểm RRF tính toán khớp chính xác công thức toán học (`1/62 + 1/61`), `rerank_rrf` được gọi duy nhất 1 lần, fallback an toàn tuyệt đối.
- Lỗi đã phát hiện và cách xử lý:
  - Phát hiện nguy cơ lặp lại tính toán RRF nhiều lần nếu luồng fallback không được bố trí hợp lý: Đã thiết kế cấu trúc luồng tuần tự: dense + BM25 $\rightarrow$ gọi `rerank_rrf()` 1 lần $\rightarrow$ kiểm tra cosine gốc $\rightarrow$ fallback nếu cần.
  - Phát hiện xung đột kiểu dữ liệu score giữa BM25 (thang điểm không giới hạn) và dense (thang điểm 0–1): RRF đã giải quyết triệt để vấn đề này bằng cách chỉ xếp hạng vị trí (rank) thay vì cộng gộp điểm số trực tiếp.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Hằng số làm mượt $k=60$ trong công thức RRF hiện đang được đặt cố định cho mọi loại truy vấn, chưa tự động điều chỉnh linh hoạt theo độ dài câu hỏi (ví dụ: câu hỏi từ khóa ngắn vs câu hỏi ngữ cảnh dài).
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Triển khai Weighted RRF kết hợp cơ chế phân loại truy vấn (Query Classifier), cho phép ưu tiên trọng số BM25 cho các truy vấn tra cứu định danh/con số chính xác và ưu tiên dense search cho các câu hỏi suy luận ngữ nghĩa mở rộng.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Phạm Quang Huy

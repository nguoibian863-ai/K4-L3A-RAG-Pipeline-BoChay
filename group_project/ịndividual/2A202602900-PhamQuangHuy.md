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
| Task 7 — Reranking với Reciprocal Rank Fusion (RRF) | Cài đặt thuật toán Reciprocal Rank Fusion theo công thức chuẩn $RRF(d) = \sum \frac{1}{k + rank}$ (với $k=60$, $rank \ge 1$). Hợp nhất các danh sách xếp hạng từ Dense và BM25 search, khử trùng lặp theo `id`, tính tổng điểm phân rã, bảo toàn metadata, chuẩn hóa `retrieval_method="hybrid"` và sắp xếp giảm dần để trả về top_k kết quả. | `src/task7_reranking.py`, commit `4251cc1` | Done |
| Task 8 — PageIndex Vectorless Fallback | Thiết kế và hiện thực module fallback tìm kiếm vectorless với PageIndex. Xây dựng hàm `upload_documents()` quản lý tải tài liệu và lưu cache ID (`data/pageindex_cache.json`), hàm `pageindex_search()` truy vấn vectorless fallback. Xử lý bọc lỗi `try...except` và kiểm tra `PAGEINDEX_API_KEY`, đảm bảo hệ thống không crash khi thiếu key hoặc provider gặp sự cố mạng, duy trì chuẩn đầu ra `SearchResult` với `retrieval_method="pageindex"`. | `src/task8_pageindex_vectorless.py`, commit `4251cc1` | Done |
| Contract Testing & Quality Gate (Tasks 7 & 8) | Kiểm thử đảm bảo module Task 7 và Task 8 tuân thủ chặt chẽ contract hệ thống: xác thực công thức RRF tính đúng theo thứ vị, kiểm tra tính toàn vẹn chữ ký hàm (`rerank_rrf`, `pageindex_search`) và khả năng chịu lỗi (graceful degradation) của module fallback khi có sự cố. | `tests/test_contracts.py` (`test_rrf_uses_rank_deduplicates_and_marks_hybrid`, `test_public_function_signatures_are_stable`) | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng thuật toán Reciprocal Rank Fusion (RRF) dựa trên thứ hạng vị trí với hệ số làm mượt $k=60$ để hợp nhất Dense và BM25 thay vì dùng chuẩn hóa điểm số tuyến tính (Score Normalization / Min-Max Scaler).  
   **Lý do/evidence:** Điểm số của Dense Search (Cosine Similarity trong đoạn $[0, 1]$) và BM25 Search (điểm số lexical không bị chặn trên $[0, +\infty)$, biến thiên mạnh theo độ dài tài liệu và tần suất từ) có bản chất toán học và phân phối hoàn toàn khác nhau. Việc chuẩn hóa trực tiếp (Min-Max hoặc Z-score) rất dễ bị méo mó bởi các giá trị ngoại lai (outliers) hoặc các câu truy vấn có độ dài không đồng đều. RRF giải quyết triệt để vấn đề này bằng cách quy đổi hoàn toàn điểm số thành thứ vị ($rank$), áp dụng hàm nghịch đảo $1/(k + rank)$ giúp dung hòa khách quan 2 bảng xếp hạng mà không phụ thuộc vào phân phối điểm số tuyệt đối.  
   **Trade-off:** Phương pháp RRF thuần túy bỏ qua biên độ chênh lệch điểm số thực tế giữa các thứ hạng liền kề (ví dụ: rank 1 có độ tự tin vượt trội hơn rank 2 thì khoảng cách RRF vẫn là cố định theo vị trí). Tuy nhiên, trade-off này hoàn toàn xứng đáng vì mang lại độ ổn định cao (robustness) và không đòi hỏi tinh chỉnh trọng số thủ công cho từng loại câu hỏi.

2. **Quyết định:** Thiết kế cơ chế Graceful Degradation & Fail-Safe Resilient Fallback bọc kín `try...except` quanh `pageindex_search()` và kiểm tra an toàn biến môi trường `PAGEINDEX_API_KEY`.  
   **Lý do/evidence:** PageIndex là một dịch vụ tìm kiếm vectorless đám mây bên thứ ba, phụ thuộc vào kết nối mạng bên ngoài, độ trễ và quota hạn mức của API key. Trong một kiến trúc RAG tích hợp nhóm, module fallback tuyệt đối không được phép trở thành điểm gây nghẽn chết (single point of failure). Bằng cách bọc try-except bắt toàn bộ ngoại lệ và chủ động kiểm tra guard clause khi thiếu key, module luôn trả về kết quả rỗng `[]` an toàn kèm log cảnh báo, cho phép luồng retrieval của nhóm hạ cấp một cách êm thuận (graceful fallback) mà không làm sập (crash) giao diện Chatbot Streamlit của người dùng cuối.  
   **Trade-off:** Khi API PageIndex gặp sự cố hoặc người dùng chưa cấu hình API key, chatbot sẽ không hiển thị thông báo lỗi hệ thống mà tận dụng kết quả tìm kiếm sẵn có trong kho tài liệu nội bộ; điều này có thể dẫn đến việc câu trả lời cho các câu hỏi ngoài phạm vi hẹp hơn, nhưng đổi lại hệ thống luôn đạt độ sẵn sàng cao (High Availability) và trải nghiệm không bị gián đoạn.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - Kiểm thử trực tiếp thuật toán và kết quả gộp RRF: `python -m src.task7_reranking`
  - Kiểm thử cơ chế khởi tạo và bắt lỗi an toàn của PageIndex: `python -m src.task8_pageindex_vectorless`
  - Kiểm thử hợp đồng cho Task 7: `python -m pytest tests/test_contracts.py -k "rrf" -v`
  - Kiểm thử tính toàn vẹn và khử trùng lặp: `python -m pytest tests/test_contracts.py -k "test_rrf_uses_rank_deduplicates_and_marks_hybrid" -v`
- Kết quả trước/sau nếu có:
  - Trước: Module `src/task7_reranking.py` chưa triển khai logic tính toán RRF; `src/task8_pageindex_vectorless.py` chưa có cấu trúc xử lý lỗi và fallback an toàn; test `test_rrf_uses_rank_deduplicates_and_marks_hybrid` không đạt.
  - Sau: Bài test `test_rrf_uses_rank_deduplicates_and_marks_hybrid` PASSED 100%. Điểm số RRF tính toán khớp chính xác công thức toán học ($1/(60+1) + 1/(60+2) \approx 0.032522$), metadata của tài liệu được bảo toàn nguyên vẹn, thuộc tính `retrieval_method` được gán chuẩn `"hybrid"`. Module PageIndex an toàn khi thiếu key hoặc gặp lỗi ngoại lệ, in log thông báo rõ ràng mà không làm gián đoạn chương trình.
- Lỗi đã phát hiện và cách xử lý:
  - Xử lý trùng lặp văn bản giữa hai luồng tìm kiếm: Khi một chunk xuất hiện đồng thời trong cả Dense search và BM25 search, nếu chỉ append đơn thuần sẽ gây trùng lặp và sai lệch số lượng top_k. Đã xử lý bằng cách dùng từ điển `scores` để cộng dồn điểm RRF $1/(k + rank)$ và từ điển `items` để lưu trữ object document, sau đó sắp xếp giảm dần theo điểm tích lũy trước khi trích xuất top_k.
  - Xử lý thiếu `PAGEINDEX_API_KEY`: Thêm kiểm tra điều kiện ngay đầu hàm, nếu không có key sẽ log cảnh báo và return ngay danh sách rỗng `[]`, tránh phát sinh request lỗi hoặc gây timeout kết nối.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Hằng số làm mượt $k=60$ trong RRF đang được đặt cố định và tỷ lệ trọng số giữa Dense và BM25 đang là 1:1, chưa cho phép tùy chỉnh trọng số theo đặc thù câu hỏi (ví dụ: câu hỏi tra cứu từ khóa chính xác vs câu hỏi ngữ nghĩa khái niệm mở rộng); Module PageIndex hiện mới dừng ở mức cấu trúc API fallback và xử lý an toàn lỗi kết nối, chưa tích hợp deep document parsing SDK nâng cao.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Triển khai Weighted RRF ($\alpha \cdot RRF_{dense} + (1-\alpha) \cdot RRF_{bm25}$) kết hợp bộ phân loại câu hỏi (Query Classifier) để tự động điều chỉnh tỷ trọng $\alpha$ linh hoạt theo từng loại câu truy vấn, đồng thời hoàn thiện cơ chế background index sync cho PageIndex cache.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Phạm Quang Huy

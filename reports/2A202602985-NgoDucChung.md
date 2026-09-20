# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên: Ngô Đức Chung
- Mã học viên: 2A202602985
- Nhóm: BoChay
- Repository/branch:https://github.com/nguoibian863-ai/K4-L3A-RAG-Pipeline-BoChay/tree/Chung

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 — Index pipeline | Chunking, embedding, upsert ChromaDB | `src/task4_chunking_indexing.py` | Done |
| Task 5 — Semantic search | Dense search qua ChromaDB | `src/task5_semantic_search.py` | Done |
| Task 6 — Lexical search | BM25 search cùng corpus Task 4 | `src/task6_lexical_search.py` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Chỉ tạo model embedding (`BAAI/bge-m3`) một lần rồi dùng lại cho mọi lần gọi `embed_texts`, thay vì load model mới mỗi lần.
   **Lý do/evidence:** Task 4 và Task 5 phải dùng chung một hàm `embed_texts` để model lúc index và lúc query luôn giống nhau. Load model mất vài giây, load lại nhiều lần sẽ làm search chậm không cần thiết.
   **Trade-off:** Model chiếm RAM trong suốt thời gian chạy chương trình, đổi lại các lần gọi sau nhanh hơn hẳn.

2. **Quyết định:** Task 6 tự tạo lại corpus bằng cách gọi `chunk_documents(load_documents())`, không đọc chunk từ ChromaDB.
   **Lý do/evidence:** Cách này giữ đúng `id` và `chunk_index` giống hệt Task 4 và Task 5, nên so sánh kết quả dense với BM25 không bị lệch dữ liệu.
   **Trade-off:** Phải chunk lại toàn bộ tài liệu mỗi lần build BM25 index. Chấp nhận được vì corpus hiện tại chỉ khoảng 1200 chunk, tính lại không tốn nhiều thời gian.

## Kiểm thử và kết quả

- Test đã chạy:
  - `python -m src.task4_chunking_indexing`
  - `python -m src.task5_semantic_search` (query "test query")
  - `python -m src.task6_lexical_search` (query "IELTS Writing")
  - `pytest -q` (toàn bộ test suite)
- Kết quả:
  - Task 4: index thành công 1213 chunk từ 8 tài liệu vào ChromaDB.
  - Task 5: trả kết quả đúng schema `SearchResult`, score giảm dần.
  - Task 6: trả kết quả BM25 đúng schema, score giảm dần (query "IELTS Writing" → top score 5.19).
  - `pytest -q`: 13 test pass, đều liên quan Task 4–6. 7 test fail thuộc Task 7–9 (`rerank_rrf`, `retrieve`) — chưa làm, không thuộc phần việc của tôi.
- Lỗi đã phát hiện và cách xử lý: in tiếng Việt ra console Windows bị lỗi `UnicodeEncodeError` (không phải lỗi logic, do console dùng bảng mã cp1252). Khắc phục bằng cách chạy lệnh với `PYTHONIOENCODING=utf-8`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Task 6 build lại BM25 index từ đầu mỗi lần gọi `lexical_search`, không cache — sẽ chậm nếu corpus lớn hơn nhiều.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: cache BM25 index cùng với `CORPUS` (chỉ rebuild khi dữ liệu đổi), sau đó làm Task 7 (`rerank_rrf`) vì Task 9 (`retrieve`) đang cần nó để chạy.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20-09-2026
- Tên thành viên: Ngô Đức Chung

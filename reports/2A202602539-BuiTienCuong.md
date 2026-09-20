# Individual contribution report

```text
reports/2A202602539-BuiTienCuong.md
```

---

## Thông tin

- Họ và tên: Bùi Tiến Cường
- Mã học viên: 2A202602539
- Nhóm: Bochay
- Repository/branch: cuong

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 9 — retrieval pipeline | Kết nối semantic search và lexical search; hợp nhất kết quả bằng RRF khi bật reranking; dùng điểm dense gốc để kích hoạt PageIndex fallback; giữ kết quả hybrid nếu fallback không trả kết quả hoặc phát sinh lỗi. | `src/task9_retrieval_pipeline.py`, commit `257a204` (`Complete retrieval generation flow`) | Done |
| Task 10 — generation context preparation | Hoàn thiện reorder chunks theo kiểu đưa các chunk xen kẽ về đầu/cuối context và format context kèm title/source để chuẩn bị citation; bảo đảm thứ tự sources trùng với thứ tự Document trong context để citation không trỏ nhầm nguồn. | `src/task10_generation.py`, commit `257a204` và phần sửa citation ordering | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng điểm cosine gốc của dense search để quyết định có chạy PageIndex fallback hay không.
   **Lý do/evidence:** Contract yêu cầu không dùng RRF score để so sánh threshold vì hai loại điểm ở hai thang đo khác nhau.
   **Trade-off:** Cách này đúng contract hơn, nhưng cần hiệu chỉnh threshold theo dữ liệu thực tế.

2. **Quyết định:** Khi PageIndex lỗi hoặc không trả kết quả, giữ lại kết quả hybrid thay vì làm pipeline bị dừng.
   **Lý do/evidence:** Giúp chatbot vẫn có thể sử dụng dense và BM25 khi fallback không khả dụng.
   **Trade-off:** Kết quả có thể kém phù hợp hơn trong một số query ngoài domain.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: Chạy `pytest tests/test_contracts.py -q`, `pytest tests/test_acceptance.py -q` và `pytest -q`.
- Kết quả trước/sau nếu có: Sau khi sửa lỗi, contract tests đạt 15/15, acceptance tests đạt 5/5 và toàn bộ test đạt 20/20.
- Lỗi đã phát hiện và cách xử lý: Đã sửa lỗi đọc `SCORE_THRESHOLD` rỗng trong `.env` và lỗi thụt lề `IndentationError` trong Task 10. Các test đã chạy pass; còn một cảnh báo không ghi được `.pytest_cache` do quyền thư mục.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Phần tôi phụ trách chủ yếu là retrieval và chuẩn bị context; việc kiểm tra chất lượng câu trả lời thực tế vẫn cần thêm query đúng domain và query ngoài domain.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung nhiều query đánh giá hơn để hiệu chỉnh threshold và kiểm tra citation trong các trường hợp thiếu evidence.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Bùi Tiến Cường

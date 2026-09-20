# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | Ragas 0.4.3 / ChromaDB 0.4.24 / LangChain 0.1.x |
| Evaluator model                    | gpt-4o-mini |
| Generator model                    | gpt-4o-mini |
| Embedding model                    | all-MiniLM-L6-v2 (ONNX local, dimension 384) |
| Corpus version/commit              | 54091c9 |
| Golden dataset size                | 15 grounded cases |
| `top_k`                            | 5 |
| Fallback threshold and calibration | SCORE_THRESHOLD = 0.35 (calibrated on dense cosine similarity: in-domain IELTS queries score 0.53 - 0.70, out-of-domain queries score < 0.25; falls back to PageIndex vectorless search when max score < 0.35) |

## Configurations

- **Config A — dense-only:** Retrieval thuần vector sử dụng ChromaDB với mô hình embedding `all-MiniLM-L6-v2` (cosine similarity distance), lấy `top_k=5` chunks có điểm tương đồng cao nhất.
- **Config B — hybrid + RRF:** Retrieval kết hợp dense semantic search (`all-MiniLM-L6-v2`) và lexical search (`BM25Okapi` với tokenizer bảo tồn từ khóa/chỉ số), hợp nhất kết quả bằng thuật toán Reciprocal Rank Fusion (`rerank_rrf` với hằng số $k=60$) để trích xuất `top_k=5` chunks tối ưu nhất.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.89 |     0.96 |     +0.07 |
| Answer relevance  |     0.86 |     0.94 |     +0.08 |
| Context recall    |     0.81 |     0.93 |     +0.12 |
| Context precision |     0.79 |     0.91 |     +0.12 |
| **Average**       | **0.838**| **0.935**| **+0.097**|

## A/B comparison

- **Cấu hình tốt hơn:** Config B (Hybrid + RRF) vượt trội rõ rệt trên tất cả 4 khía cạnh đánh giá của Ragas, đạt điểm trung bình 0.935 so với 0.838 của Config A (+0.097 điểm tổng thể).
- **Evidence:**
  - **Context Recall tăng mạnh nhất (+0.12, từ 0.81 lên 0.93):** Nhờ BM25 bắt chính xác các thực thể định danh, số liệu và từ viết tắt đặc thù (ví dụ: "L.I.M Framework", "mô hình TREE", "116 phút", "1.450 SAT"). Trong Config A, dense embedding thuần có xu hướng bị phân tán bởi các chunk có ngữ cảnh chung về học tiếng Anh nhưng thiếu số liệu cụ thể.
  - **Context Precision tăng từ 0.79 lên 0.91 (+0.12):** Do thuật toán RRF đưa các chunk được cả hai phương thức xếp hạng cao lên vị trí ưu tiên, loại bỏ hiệu quả các chunk nhiễu chỉ tương đồng về mặt từ vựng bề mặt hoặc ngữ nghĩa mờ.
  - **Faithfulness đạt 0.96 (+0.07) và Answer Relevance đạt 0.94 (+0.08):** Bộ tạo (generator) nhận được ngữ cảnh giàu bằng chứng thực tế và được sắp xếp tối ưu (reorder_for_llm), triệt tiêu hiện tượng hallucination và safe refusal chính xác khi thiếu bằng chứng.
- **Trade-off về latency/cost:**
  - **Cost (Token LLM):** Tương đương nhau giữa hai cấu hình vì đều giới hạn nghiêm ngặt `top_k=5` chunks đầu vào cho generator prompt.
  - **Latency:** Config A đạt tốc độ truy xuất trung bình ~38ms. Config B mất ~52ms (tăng thêm ~14ms cho BM25 scoring và RRF reciprocal merge). Mức tăng latency 14ms hoàn toàn không đáng kể trong hệ thống tương tác người dùng (<100ms) nhưng mang lại bước nhảy vọt về chất lượng phản hồi (+9.7%).

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Cơ chế thi thích ứng (adaptive testing) mới của bài thi TOEFL hoạt động như thế nào? | Config A | 0.78 | 0.82 | 0.70 | 0.68 | retrieval | Từ khóa chuyên ngành "adaptive testing" và "thích ứng" trong ngữ cảnh tiếng Việt bị các chunk về phương pháp học tiếng Anh nói chung làm loãng điểm cosine embedding, khiến chunk chứa nội dung thay đổi độ khó Đọc/Nghe bị xếp ngoài top 5. |
|   2 | Trong bài mẫu phân tích thay đổi dân số New York từ thế kỷ 19 đến 21, dân số New York đã thay đổi như thế nào sau 200 năm? | Config A | 0.82 | 0.85 | 0.72 | 0.71 | retrieval | Các mốc con số ("79 nghìn", "3.4 triệu", "8 triệu") không có trọng số embedding đặc thù cao trong không gian vector dày đặc, dẫn đến việc lấy nhầm chunk phân tích chi tiết quận Manhattan thay vì bức tranh toàn thể 200 năm. |
|   3 | Trong IELTS Writing, hai phần bắt buộc phải có lần lượt đối với Task 1 và Task 2 là gì? | Config B | 0.90 | 0.88 | 0.84 | 0.86 | generation | Thông tin về overview (Task 1) và conclusion (Task 2) nằm rải rác trong một đoạn trích phỏng vấn chuyên gia ngắn. Generator tóm tắt có phần dài dòng trước khi nêu trực tiếp hai khái niệm cốt lõi, làm giảm nhẹ điểm Answer Relevance. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Chuyển sang Semantic Chunking kết hợp Markdown Heading Splitter | Nhiều thông tin cốt lõi (như cặp Task 1 overview / Task 2 conclusion hay số liệu dân số New York) nằm sát ranh giới giữa hai chunk cắt cố định 500 ký tự | Tăng Context Precision lên >0.94 và Context Recall lên >0.96, bảo toàn trọn vẹn ngữ cảnh cấu trúc tài liệu | Đánh giá lại 15 test cases trong `golden_dataset.json` với chunking mới và đo delta Context Recall/Precision |
|        2 | Bổ sung Cross-Encoder Reranker giai đoạn 2 sau RRF | RRF xếp hạng tuyến tính dựa trên vị trí rank mà chưa tính toán trực tiếp tương quan chéo giữa query và toàn văn chunk | Đưa chunk liên quan nhất trực tiếp lên Rank 1, nâng cao Faithfulness từ 0.96 lên >0.98 | Tích hợp cross-encoder cho top 10 trước khi lấy top 5, đo lường MRR và Hit Rate@3 |
|        3 | Nâng cấp PageIndex Fallback hỗ trợ tra cứu theo cấu trúc bảng mục lục (TOC Tree) | Khi truy vấn mang tính phân loại tổng thể bài thi, PageIndex dạng chuỗi tuyến tính quét toàn văn chưa tối ưu bằng cấu trúc cây danh mục | Cải thiện độ chính xác và giảm 50% thời gian xử lý khi hệ thống rơi vào chế độ vectorless fallback | Kiểm thử trên bộ câu hỏi phân loại dạng bài tổng quan và đo tỷ lệ fallback thành công |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Tinh chỉnh hằng số RRF $k=20$ thay vì $k=60$ | Config B ($k=60$) | Context Precision +0.02, Faithfulness +0.01 | Không thay đổi latency/cost (0ms delta) | Giá trị $k=20$ giúp khuếch đại khoảng cách thứ hạng của các chunk xuất hiện ở vị trí đầu của cả hai bộ xếp hạng, lọc bỏ chunk nhiễu hiệu quả hơn. |
| Áp dụng Reordering giảm Lost-in-the-Middle | Config B giữ nguyên thứ tự giảm dần | Faithfulness +0.04, Answer Relevance +0.03 | 0ms overhead | Đặt các chunk điểm cao nhất ở đầu và cuối ngữ cảnh giúp LLM tận dụng tối đa attention span, triệt tiêu việc bỏ sót chi tiết ở giữa ngữ cảnh. |

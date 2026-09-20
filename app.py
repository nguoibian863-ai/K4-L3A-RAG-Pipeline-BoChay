import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="IELTS RAG Chatbot",
    page_icon="📚",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("📚 IELTS RAG Assistant")
    st.caption("Trợ lý tra cứu cẩm nang luyện thi IELTS Writing & tin tức giáo dục")
    st.divider()
    top_k = st.slider("Số lượng chunks retrieved (top_k)", min_value=1, max_value=10, value=5)
    
    st.markdown("### Thông tin Pipeline")
    st.markdown("- **Embedding:** ONNX `all-MiniLM-L6-v2` (Local)")
    st.markdown("- **Retrieval:** Hybrid (Dense + BM25 + RRF)")
    st.markdown("- **Fallback:** PageIndex Vectorless")
    st.markdown("- **LLM:** OpenAI `gpt-4o-mini`")
    
    st.divider()
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("🎓 IELTS Writing & Education RAG Chatbot")
st.caption("Hệ thống chatbot trả lời câu hỏi dựa trên bộ tài liệu IELTS Writing và bài viết giáo dục, trích dẫn nguồn đối chiếu chính xác.")

# Hiển thị lịch sử tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            method = message.get("retrieval_source", "hybrid")
            with st.expander(f"📌 Nguồn trích dẫn ({len(message['sources'])} tài liệu | Phương thức: {method})", expanded=False):
                for i, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(f"**[{i}] {meta.get('title', 'Tài liệu')}**")
                    st.caption(
                        f"📁 **Source:** `{meta.get('source', 'N/A')}` | "
                        f"🎯 **Score:** `{src.get('score', 0):.4f}` | "
                        f"⚙️ **Method:** `{src.get('retrieval_method', 'N/A')}`"
                    )
                    if meta.get("url"):
                        st.markdown(f"🔗 [Xem bài viết gốc]({meta['url']})")
                    content_preview = src.get("content", "").strip()
                    if len(content_preview) > 300:
                        content_preview = content_preview[:300] + "..."
                    st.text(content_preview)
                    st.divider()

# Gợi ý câu hỏi mẫu nhanh
st.markdown("##### 💡 Gợi ý câu hỏi mẫu (Click để hỏi nhanh):")
col1, col2, col3 = st.columns(3)
selected_prompt = None
with col1:
    if st.button("🌱 Mô hình TREE trong IELTS Speaking là gì?", use_container_width=True):
        selected_prompt = "Mô hình TREE trong IELTS Speaking Part 3 là gì và các chữ cái đại diện cho điều gì?"
    if st.button("📊 Task 1 & Task 2 cần phần bắt buộc nào?", use_container_width=True):
        selected_prompt = "Trong IELTS Writing, hai phần bắt buộc phải có lần lượt đối với Task 1 và Task 2 là gì?"
with col2:
    if st.button("🧩 Mô hình L.I.M Framework gồm bước nào?", use_container_width=True):
        selected_prompt = "Mô hình L.I.M Framework của The IELTS Workshop gồm những bước nào?"
    if st.button("🎯 SAT & TOEFL có giá trị bao lâu?", use_container_width=True):
        selected_prompt = "Kết quả bài thi SAT và TOEFL có giá trị trong bao lâu?"
with col3:
    if st.button("🎓 IELTS được cộng bao nhiêu điểm ĐH?", use_container_width=True):
        selected_prompt = "Theo quy định của Bộ Giáo dục và Đào tạo, thí sinh có chứng chỉ IELTS được cộng tối đa bao nhiêu điểm khi xét tuyển đại học?"
    if st.button("⛅ Thời tiết hôm nay thế nào? (Safe Refusal)", use_container_width=True):
        selected_prompt = "Thời tiết hôm nay ở Hà Nội thế nào?"

# Xử lý câu hỏi người dùng
chat_input = st.chat_input("Nhập câu hỏi về IELTS Writing hoặc kinh nghiệm học thi...")
query = selected_prompt or chat_input

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời có trích dẫn..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result.get("sources", [])
            retrieval_source = result.get("retrieval_source", "none")

        st.markdown(answer)

        if sources:
            with st.expander(f"📌 Nguồn trích dẫn ({len(sources)} tài liệu | Phương thức: {retrieval_source})", expanded=True):
                for i, src in enumerate(sources, 1):
                    meta = src.get("metadata", {})
                    st.markdown(f"**[{i}] {meta.get('title', 'Tài liệu')}**")
                    st.caption(
                        f"📁 **Source:** `{meta.get('source', 'N/A')}` | "
                        f"🎯 **Score:** `{src.get('score', 0):.4f}` | "
                        f"⚙️ **Method:** `{src.get('retrieval_method', 'N/A')}`"
                    )
                    if meta.get("url"):
                        st.markdown(f"🔗 [Xem bài viết gốc]({meta['url']})")
                    content_preview = src.get("content", "").strip()
                    if len(content_preview) > 300:
                        content_preview = content_preview[:300] + "..."
                    st.text(content_preview)
                    st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })

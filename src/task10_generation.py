"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve

load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

SYSTEM_PROMPT = f"""Bạn là trợ lý RAG chuyên gia về luyện thi và chính sách chứng chỉ IELTS.
Quy tắc trả lời:
1. Chỉ sử dụng thông tin có trong phần Context được cung cấp.
2. Mỗi luận điểm hoặc câu trả lời phải trích dẫn rõ nguồn tương ứng (ví dụ: [Tài liệu 1], [Nguồn 2]).
3. Tuyệt đối không suy đoán hoặc bịa đặt thông tin ngoài Context.
4. Nếu Context không chứa đủ thông tin để trả lời câu hỏi (câu hỏi ngoài domain hoặc không có bằng chứng), bạn BẮT BUỘC phải từ chối xác minh bằng đúng câu: '{SAFE_REFUSAL}'."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để giảm hiện tượng lost-in-the-middle.
    
    Hàm này không làm thay đổi danh sách truyền vào (non-mutating) và giữ nguyên id chunk.
    """
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label phục vụ citation đối chiếu."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Tài liệu")
        source = metadata.get("source", "N/A")
        content = chunk.get("content", "").strip()
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{content}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model_name = os.getenv("LLM_MODEL", "")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY chưa được cấu hình.")
        import openai

        client = openai.OpenAI(api_key=api_key)
        model = model_name or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content.strip()

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY chưa được cấu hình.")
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            model = model_name or "gemini-1.5-flash"
            resp = client.models.generate_content(
                model=model,
                contents=f"{system_prompt}\n\n{user_message}",
            )
            return resp.text.strip()
        except Exception:
            import google.generativeai as gai

            gai.configure(api_key=api_key)
            model = gai.GenerativeModel(model_name or "gemini-1.5-flash")
            resp = model.generate_content(f"{system_prompt}\n\n{user_message}")
            return resp.text.strip()

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY chưa được cấu hình.")
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        model = model_name or "claude-3-5-sonnet-20241022"
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
        )
        return response.content[0].text.strip()

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult gồm answer, sources và retrieval_source."""
    if not query or not query.strip():
        return {
            "answer": SAFE_REFUSAL,
            "sources": [],
            "retrieval_source": "none",
        }

    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": SAFE_REFUSAL,
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
        if not answer or not answer.strip():
            answer = SAFE_REFUSAL
    except Exception as error:
        print(f"Lỗi khi gọi LLM: {error}")
        answer = SAFE_REFUSAL

    retrieval_source = chunks[0]["retrieval_method"] if chunks else "none"
    if retrieval_source not in {"hybrid", "pageindex", "none"}:
        retrieval_source = "hybrid"

    return {
        "answer": answer,
        "sources": reordered,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    test_query = "Chuyên gia gợi ý mẹo gì để đạt 7.0 IELTS Writing?"
    print(f"Testing generation for query: '{test_query}'\n")
    result = generate_with_citation(test_query, top_k=3)
    print("ANSWER:\n", result["answer"])
    print("\nRETRIEVAL SOURCE:", result["retrieval_source"])
    print(f"SOURCES COUNT: {len(result['sources'])}")

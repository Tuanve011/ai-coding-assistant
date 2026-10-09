# services/ai_service.py
# ==============================================================================
# Service giao tiếp với AI (Groq API) và xử lý phân tích mã nguồn cho Phase 4
# - Quản lý an toàn API Key qua Streamlit secrets (st.secrets)
# - Tuyệt đối KHÔNG hardcode API Key trong mã nguồn
# - Che giấu và khử trùng (sanitize) API Key trong mọi thông báo lỗi và log
# - Cung cấp các tác vụ chuyên sâu: Explain Code, Find Bugs, Fix Code,
#   Optimize Code, Generate Code
# - Tuyệt đối KHÔNG thực thi (run/eval/exec) mã nguồn do người dùng cung cấp
# ==============================================================================

import os
import re
import streamlit as st
from groq import (
    Groq,
    APIConnectionError,
    APIStatusError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    BadRequestError,
)


# ── Model mặc định và ánh xạ từ tên UI sang Groq Model ID ──────────────────
DEFAULT_MODEL = "openai/gpt-oss-20b"

MODEL_MAPPING = {
    # Groq native models
    "GPT-OSS 20B":             "openai/gpt-oss-20b",
    "Llama 3.3 70B":           "llama-3.3-70b-versatile",
    "Llama 3.1 8B":            "llama-3.1-8b-instant",
    "Mixtral 8x7B":            "mixtral-8x7b-32768",
    "Gemma 2 9B":              "gemma2-9b-it",
    # Ánh xạ trực tiếp ID
    "openai/gpt-oss-20b":      "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant":    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768":      "mixtral-8x7b-32768",
    "gemma2-9b-it":            "gemma2-9b-it",
}

# Ánh xạ ngôn ngữ chuẩn sang mã tô màu cú pháp Markdown / Streamlit
LANGUAGE_CODE_MAP = {
    "c++": "cpp",
    "cpp": "cpp",
    "python": "python",
    "py": "python",
    "java": "java",
    "javascript": "javascript",
    "js": "javascript",
}


def get_api_key() -> str | None:
    """
    Đọc Groq API Key từ Streamlit secrets hoặc biến môi trường.
    Tuyệt đối không lưu trữ API Key trong mã nguồn.

    Trả về:
        str: API Key hợp lệ nếu tìm thấy.
        None: Nếu chưa cấu hình hoặc key vẫn là placeholder mặc định.
    """
    # 1. Ưu tiên đọc từ Streamlit secrets (.streamlit/secrets.toml)
    try:
        if "GROQ_API_KEY" in st.secrets:
            key = str(st.secrets["GROQ_API_KEY"]).strip()
            if key and key not in ("YOUR_GROQ_API_KEY_HERE", "YOUR_API_KEY_HERE", ""):
                return key
    except Exception:
        pass

    # 2. Fallback: kiểm tra biến môi trường hệ thống
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key and env_key not in ("YOUR_GROQ_API_KEY_HERE", "YOUR_API_KEY_HERE", ""):
        return env_key

    return None


def sanitize_error(error_message: str, api_key: str | None = None) -> str:
    """
    Khử trùng thông báo lỗi để đảm bảo không bao giờ để lộ API Key trong log hay UI.
    """
    if not error_message:
        return ""

    sanitized = str(error_message)

    # Nếu biết API key hiện tại, thay thế bằng chuỗi an toàn
    if api_key and api_key in sanitized:
        sanitized = sanitized.replace(api_key, "[REDACTED_API_KEY]")

    # Lọc mẫu ký tự API Key điển hình của Groq (bắt đầu bằng gsk_...)
    sanitized = re.sub(r"gsk_[0-9A-Za-z]{40,}", "[REDACTED_API_KEY]", sanitized)

    # Lọc key dạng Google cũ nếu còn sót (bắt đầu bằng AIza...)
    sanitized = re.sub(r"AIza[0-9A-Za-z\-_]{30,}", "[REDACTED_API_KEY]", sanitized)

    # Lọc key trong URL query params (?key=... hoặc &key=...)
    sanitized = re.sub(r"(key=)[a-zA-Z0-9_\-]+", r"\1[REDACTED_API_KEY]", sanitized)

    return sanitized


def extract_code_snippet(markdown_text: str) -> str:
    """
    Trích xuất nội dung code bên trong khối code Markdown đầu tiên.
    Hỗ trợ các khối ```language ... ``` hoặc ``` ... ```.
    """
    if not markdown_text:
        return ""

    # Tìm khối code có chỉ định ngôn ngữ hoặc không
    match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", markdown_text)
    if match:
        return match.group(1).strip()
    return ""


def check_api_connection() -> tuple[bool, str]:
    """
    Kiểm tra trạng thái kết nối tới Groq API bằng một yêu cầu ping nhỏ.

    Trả về:
        tuple (bool, str): (Trạng thái thành công, Thông điệp chi tiết đã sanitize)
    """
    api_key = get_api_key()
    if not api_key:
        return False, "Chưa cấu hình GROQ_API_KEY trong .streamlit/secrets.toml"

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        if response and response.choices and response.choices[0].message.content:
            return True, "Kết nối Groq API thành công!"
        return False, "Không nhận được phản hồi từ Groq API."
    except AuthenticationError:
        return False, "Lỗi xác thực (Authentication Error): GROQ_API_KEY không hợp lệ hoặc đã hết hạn."
    except RateLimitError:
        return False, "Vượt quá giới hạn sử dụng (Rate Limit / Quota Exceeded). Vui lòng thử lại sau."
    except (NotFoundError, BadRequestError) as e:
        safe_msg = sanitize_error(str(e), api_key)
        return False, f"Lỗi mô hình hoặc tham số (Model Error): {safe_msg}"
    except APIConnectionError as e:
        safe_msg = sanitize_error(str(e), api_key)
        return False, f"Lỗi kết nối mạng: {safe_msg}"
    except APIStatusError as e:
        safe_msg = sanitize_error(e.message if hasattr(e, "message") else str(e), api_key)
        return False, f"Lỗi Groq API (Mã: {e.status_code}): {safe_msg}"
    except Exception as e:
        safe_msg = sanitize_error(str(e), api_key)
        return False, f"Lỗi không xác định: {safe_msg}"


# ==============================================================================
# HÀM CHO TÍNH NĂNG CHAT (PHASE 2 & 3)
# ==============================================================================
def send_message(
    prompt: str,
    chat_history: list[dict] | None = None,
    model_name: str | None = None,
    temperature: float = 0.7,
    programming_language: str = "python",
) -> dict:
    """
    Gửi câu hỏi và ngữ cảnh hội thoại tới Groq API và nhận phản hồi dạng chat.
    """
    api_key = get_api_key()

    if not api_key:
        return {
            "role": "assistant",
            "content": (
                "⚠️ **Chưa tìm thấy Groq API Key!**\n\n"
                "Để trò chuyện trực tiếp với AI thông minh, bạn hãy làm theo các bước sau:\n\n"
                "1. Mở file `.streamlit/secrets.toml` trong thư mục dự án.\n"
                "2. Cập nhật khóa bí mật của bạn:\n"
                "```toml\n"
                'GROQ_API_KEY = "your_groq_api_key_here"\n'
                "```\n"
                "3. *Chưa có khóa?* Nhận miễn phí tại: [Groq Console](https://console.groq.com/keys).\n\n"
                "*(Lưu ý: File `.streamlit/secrets.toml` đã được chặn trong `.gitignore` nên tuyệt đối an toàn)*"
            ),
            "code": "# Vui lòng thêm GROQ_API_KEY vào .streamlit/secrets.toml\n# Sau đó thử gửi lại câu hỏi của bạn!",
            "is_error": True,
            "error_type": "MISSING_KEY",
        }

    target_model = MODEL_MAPPING.get(model_name, DEFAULT_MODEL) if model_name else DEFAULT_MODEL

    system_instruction = (
        "Bạn là một Trợ lý Lập trình AI chuyên nghiệp, nhiệt tình và thân thiện dành cho sinh viên "
        "và các lập trình viên. Nhiệm vụ của bạn là:\n"
        "- Giải thích chi tiết, dễ hiểu, logic từng bước.\n"
        "- Phát hiện lỗi và đề xuất phương án sửa tối ưu.\n"
        f"- Viết mã nguồn minh họa chất lượng cao, ưu tiên ngôn ngữ {programming_language} "
        "(hoặc ngôn ngữ theo yêu cầu trong câu hỏi).\n"
        "- Mọi đoạn mã nguồn PHẢI được bọc trong khối code Markdown có tên ngôn ngữ "
        "(ví dụ ```python ... ```).\n"
        "- Trả lời bằng tiếng Việt lịch sự, rõ ràng, sư phạm."
    )

    try:
        client = Groq(api_key=api_key)
        messages = [{"role": "system", "content": system_instruction}]

        if chat_history:
            for msg in chat_history:
                role = msg.get("role")
                content = msg.get("content", "")
                if not content or msg.get("is_error"):
                    continue
                if role == "user":
                    messages.append({"role": "user", "content": content})
                elif role == "assistant":
                    if len(messages) > 1:
                        messages.append({"role": "assistant", "content": content})

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=float(temperature),
        )

        ai_text = response.choices[0].message.content or "Không nhận được phản hồi từ AI."
        code_snippet = extract_code_snippet(ai_text)

        return {
            "role": "assistant",
            "content": ai_text,
            "code": code_snippet,
            "is_error": False,
            "error_type": None,
        }

    except AuthenticationError as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "role": "assistant",
            "content": (
                "🔑 **Lỗi xác thực (Authentication Error - Mã 401):**\n\n"
                "Khóa `GROQ_API_KEY` của bạn không hợp lệ hoặc đã hết hạn. "
                "Vui lòng kiểm tra lại giá trị trong `.streamlit/secrets.toml`.\n\n"
                f"*Chi tiết:* `{safe_msg}`"
            ),
            "code": "# Lỗi API Key. Vui lòng kiểm tra GROQ_API_KEY trong secrets.toml",
            "is_error": True,
            "error_type": "AUTHENTICATION_ERROR",
        }
    except RateLimitError:
        return {
            "role": "assistant",
            "content": (
                "⏳ **Vượt quá giới hạn sử dụng (Rate Limit - Mã 429):**\n\n"
                "Bạn đã gửi quá nhiều yêu cầu trong thời gian ngắn hoặc vượt hạn mức của tài khoản Groq. "
                "Vui lòng đợi vài giây và thử lại."
            ),
            "code": "",
            "is_error": True,
            "error_type": "RATE_LIMIT_ERROR",
        }
    except (NotFoundError, BadRequestError) as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "role": "assistant",
            "content": (
                "❌ **Lỗi mô hình (Model Error):**\n\n"
                f"Mô hình `{target_model}` không tồn tại hoặc không được hỗ trợ trên Groq API.\n\n"
                f"*Chi tiết:* `{safe_msg}`\n\n"
                "Vui lòng chọn model Groq khác trong thanh Sidebar."
            ),
            "code": "",
            "is_error": True,
            "error_type": "MODEL_ERROR",
        }
    except APIConnectionError as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "role": "assistant",
            "content": (
                "🌐 **Lỗi kết nối mạng:**\n\n"
                f"Không thể kết nối tới Groq API. Chi tiết lỗi:\n`{safe_msg}`"
            ),
            "code": "",
            "is_error": True,
            "error_type": "CONNECTION_ERROR",
        }
    except APIStatusError as e:
        safe_msg = sanitize_error(e.message if hasattr(e, "message") else str(e), api_key)
        return {
            "role": "assistant",
            "content": f"❌ **Lỗi yêu cầu (Mã {getattr(e, 'status_code', 500)}):**\n\n`{safe_msg}`",
            "code": "",
            "is_error": True,
            "error_type": f"API_ERROR_{getattr(e, 'status_code', 500)}",
        }
    except Exception as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "role": "assistant",
            "content": f"🌐 **Lỗi không xác định:**\n\n`{safe_msg}`",
            "code": "",
            "is_error": True,
            "error_type": "UNKNOWN_ERROR",
        }


# ==============================================================================
# HÀM CHO PHASE 4: AI CODING ASSISTANT (TÁC VỤ CODE CHUYÊN SÂU)
# ==============================================================================

def build_coding_prompt(code: str, language: str, action: str) -> tuple[str, str]:
    """
    Xây dựng System Instruction và User Prompt theo từng chức năng của Phase 4.
    Yêu cầu AI trả lời bằng tiếng Việt và tuân thủ đúng cấu trúc 5 phần:
    1. Analysis
    2. Problems
    3. Explanation
    4. Suggested Fix
    5. Improved Code (bắt buộc trong code block)

    Tham số:
        code (str): Mã nguồn hoặc mô tả người dùng nhập vào.
        language (str): Ngôn ngữ lập trình (C++, Python, Java, JavaScript).
        action (str): Tác vụ (Explain Code, Find Bugs, Fix Code, Optimize Code, Generate Code).

    Trả về:
        tuple[str, str]: (system_instruction, user_prompt)
    """
    lang_code = LANGUAGE_CODE_MAP.get(language.lower(), "text")

    action_guidelines = {
        "Explain Code": (
            "- Tập trung giải thích kiến trúc tổng thể, luồng thực thi và mục đích của mã nguồn.\n"
            "- Trong mục Problems: Chỉ ra các điểm hạn chế về cách viết hoặc lưu ý cần quan tâm (nếu không có lỗi nghiêm trọng thì ghi rõ).\n"
            "- Trong mục Explanation: Diễn giải chi tiết từng khối logic một cách sư phạm, dễ hiểu cho sinh viên.\n"
            "- Trong mục Suggested Fix: Gợi ý các chuẩn viết code sạch (clean code conventions) hoặc tài liệu hóa.\n"
            "- Trong mục Improved Code: Cung cấp mã nguồn hoàn chỉnh có chú thích rõ ràng, định dạng chuẩn."
        ),
        "Find Bugs": (
            "- Rà soát tĩnh toàn diện để phát hiện lỗi cú pháp, lỗi logic, rủi ro runtime, tràn bộ nhớ, con trỏ null, chia cho 0.\n"
            "- Trong mục Problems: Liệt kê chi tiết từng lỗi phát hiện kèm dòng/vị trí xảy ra.\n"
            "- Trong mục Explanation: Phân tích sâu nguyên nhân gốc rễ (root cause) của từng lỗi.\n"
            "- Trong mục Suggested Fix: Đưa ra giải pháp kỹ thuật cụ thể để khắc phục triệt để.\n"
            "- Trong mục Improved Code: Cung cấp toàn bộ mã nguồn sau khi đã loại bỏ sạch các lỗi."
        ),
        "Fix Code": (
            "- Sửa toàn bộ lỗi trong mã nguồn và hoàn thiện chương trình chạy ổn định.\n"
            "- Trong mục Problems: Tóm lược các lỗi hoặc thiếu sót cần được sửa.\n"
            "- Trong mục Explanation: Giải thích từng thay đổi đã thực hiện và lý do tại sao sửa như vậy.\n"
            "- Trong mục Suggested Fix: Hướng dẫn người dùng cách kiểm thử lại sau khi áp dụng bản sửa.\n"
            "- Trong mục Improved Code: Mã nguồn đã được sửa lỗi hoàn chỉnh 100%, sẵn sàng chạy."
        ),
        "Optimize Code": (
            "- Đánh giá độ phức tạp thuật toán (Time Complexity O(...) và Space Complexity O(...)).\n"
            "- Trong mục Problems: Chỉ ra các điểm nghẽn hiệu năng (bottlenecks), thao tác dư thừa, cấp phát bộ nhớ lãng phí.\n"
            "- Trong mục Explanation: Giải thích cơ chế thuật toán hoặc cấu trúc dữ liệu tối ưu hơn.\n"
            "- Trong mục Suggested Fix: Đề xuất các kỹ thuật tối ưu (bảng băm, hai con trỏ, quy hoạch động, tránh sao chép dữ liệu...).\n"
            "- Trong mục Improved Code: Mã nguồn đã được tối ưu đạt hiệu năng cao nhất."
        ),
        "Generate Code": (
            "- Tạo mã nguồn hoàn chỉnh dựa trên bài toán hoặc mô tả yêu cầu của người dùng.\n"
            "- Trong mục Analysis: Phân tích bài toán, xác định đầu vào/đầu ra và các yêu cầu kỹ thuật.\n"
            "- Trong mục Problems: Xác định các trường hợp biên (edge cases) và ngoại lệ cần xử lý an toàn.\n"
            "- Trong mục Explanation: Giải thích thiết kế giải thuật và cấu trúc của chương trình.\n"
            "- Trong mục Suggested Fix: Hướng dẫn mở rộng hoặc tích hợp vào hệ thống lớn hơn.\n"
            "- Trong mục Improved Code: Mã nguồn hoàn chỉnh, có hàm kiểm thử mẫu (hàm main hoặc ví dụ chạy thử)."
        ),
    }

    selected_guideline = action_guidelines.get(
        action,
        "- Phân tích và xử lý mã nguồn theo yêu cầu của lập trình viên một cách chi tiết."
    )

    system_instruction = (
        "Bạn là một Trợ lý Lập trình AI (AI Coding Assistant) chuyên nghiệp, giàu kinh nghiệm sư phạm "
        "dành cho sinh viên ngành Khoa học Máy tính và Công nghệ Thông tin.\n\n"
        "QUY TẮC AN TOÀN BẮT BUỘC:\n"
        "1. TUYỆT ĐỐI KHÔNG thực thi mã nguồn. Bạn chỉ phân tích tĩnh qua văn bản.\n"
        "2. Không tạo mã nguồn độc hại, khai thác bảo mật hoặc phá hoại hệ thống.\n\n"
        "HƯỚNG DẪN TÁC VỤ HIỆN TẠI:\n"
        f"{selected_guideline}\n\n"
        "QUY TẮC ĐỊNH DẠNG ĐẦU RA (BẮT BUỘC TUÂN THỦ NGHIÊM NGẶT):\n"
        "Câu trả lời của bạn BẮT BUỘC phải chia thành đúng 5 mục tiêu đề Markdown sau:\n"
        "### 1. Analysis\n"
        "(Nội dung phân tích tổng quan cấu trúc, ý nghĩa và kiến trúc)\n\n"
        "### 2. Problems\n"
        "(Nội dung các vấn đề, lỗi phát hiện hoặc điểm cần chú ý)\n\n"
        "### 3. Explanation\n"
        "(Nội dung giải thích chi tiết, từng bước dễ hiểu cho sinh viên)\n\n"
        "### 4. Suggested Fix\n"
        "(Nội dung đề xuất giải pháp khắc phục hoặc hướng tối ưu)\n\n"
        "### 5. Improved Code\n"
        f"```{lang_code}\n"
        f"// Mã nguồn {language} hoàn chỉnh ở đây\n"
        "```\n\n"
        "LƯU Ý QUAN TRỌNG VỀ CODE:\n"
        f"- Toàn bộ mã nguồn trong mục 'Improved Code' PHẢI được bọc trong khối code Markdown có chỉ định rõ ngôn ngữ: ```{lang_code} ... ```.\n"
        "- Trình bày bằng tiếng Việt mạch lạc, chuẩn mực sư phạm, truyền cảm hứng học tập."
    )

    user_prompt = (
        f"Ngôn ngữ lập trình: {language}\n"
        f"Chức năng yêu cầu: {action}\n\n"
        "Nội dung mã nguồn / Yêu cầu đầu vào:\n"
        f"```{lang_code}\n"
        f"{code}\n"
        "```\n\n"
        f"Hãy thực hiện chức năng '{action}' cho đoạn mã / yêu cầu trên và trình bày đầy đủ đúng 5 mục tiêu đề Markdown:\n"
        "### 1. Analysis\n"
        "### 2. Problems\n"
        "### 3. Explanation\n"
        "### 4. Suggested Fix\n"
        "### 5. Improved Code"
    )

    return system_instruction, user_prompt


def parse_analysis_response(raw_text: str, language: str = "Python") -> dict:
    """
    Bóc tách phản hồi từ AI thành 5 phần cấu trúc riêng biệt:
    1. Analysis
    2. Problems
    3. Explanation
    4. Suggested Fix
    5. Improved Code (kèm khối code trích xuất)

    Hàm có cơ chế fallback thông minh để luôn đảm bảo có đủ 5 phần, không bao giờ gây lỗi giao diện.
    """
    if not raw_text:
        return {
            "analysis": "Chưa có nội dung phân tích.",
            "problems": "Không phát hiện lỗi.",
            "explanation": "Chưa có nội dung giải thích.",
            "suggested_fix": "Không có đề xuất.",
            "improved_code": "",
            "raw_content": "",
        }

    lang_code = LANGUAGE_CODE_MAP.get(language.lower(), "text")

    # 1. Trích xuất mã code từ toàn bộ văn bản (hoặc từ phần Improved Code)
    extracted_code = extract_code_snippet(raw_text)

    # 2. Các mẫu Regex tìm vị trí 5 tiêu đề
    # Mẫu hỗ trợ: ### 1. Analysis, ### Analysis, ## 1. Analysis, **Analysis**...
    patterns = [
        ("analysis", r"(?:^|\n)#{1,4}\s*(?:1\.?\s*)?(?:Analysis|Phân tích)[^\n]*\n([\s\S]*?)(?=(?:^|\n)#{1,4}\s*(?:2\.?\s*)?(?:Problems|Vấn đề)|$)"),
        ("problems", r"(?:^|\n)#{1,4}\s*(?:2\.?\s*)?(?:Problems|Vấn đề|Lỗi phát hiện)[^\n]*\n([\s\S]*?)(?=(?:^|\n)#{1,4}\s*(?:3\.?\s*)?(?:Explanation|Giải thích)|$)"),
        ("explanation", r"(?:^|\n)#{1,4}\s*(?:3\.?\s*)?(?:Explanation|Giải thích)[^\n]*\n([\s\S]*?)(?=(?:^|\n)#{1,4}\s*(?:4\.?\s*)?(?:Suggested Fix|Đề xuất)|$)"),
        ("suggested_fix", r"(?:^|\n)#{1,4}\s*(?:4\.?\s*)?(?:Suggested Fix|Đề xuất sửa|Đề xuất khắc phục)[^\n]*\n([\s\S]*?)(?=(?:^|\n)#{1,4}\s*(?:5\.?\s*)?(?:Improved Code|Mã nguồn cải tiến)|$)"),
        ("improved_code_section", r"(?:^|\n)#{1,4}\s*(?:5\.?\s*)?(?:Improved Code|Mã nguồn cải tiến|Mã nguồn hoàn chỉnh)[^\n]*\n([\s\S]*?)$"),
    ]

    parsed_sections = {}
    for key, regex in patterns:
        match = re.search(regex, raw_text, re.IGNORECASE)
        if match:
            parsed_sections[key] = match.group(1).strip()
        else:
            parsed_sections[key] = ""

    # Nếu phần Improved Code có chứa khối code riêng, ưu tiên trích xuất từ đó
    if parsed_sections.get("improved_code_section"):
        code_in_sec = extract_code_snippet(parsed_sections["improved_code_section"])
        if code_in_sec:
            extracted_code = code_in_sec

    # 3. Fallback giá trị mặc định có ý nghĩa nếu model không tuân thủ hoàn toàn header
    analysis = (
        parsed_sections.get("analysis")
        or "Mã nguồn đã được tiếp nhận và phân tích tĩnh thành công bằng mô hình AI."
    )
    problems = (
        parsed_sections.get("problems")
        or "Không ghi nhận lỗi cú pháp nghiêm trọng trong phạm vi phân tích."
    )
    explanation = (
        parsed_sections.get("explanation")
        or (raw_text if not extracted_code else "Vui lòng xem chi tiết mã nguồn cải tiến bên dưới.")
    )
    suggested_fix = (
        parsed_sections.get("suggested_fix")
        or "Áp dụng cấu trúc mã nguồn chuẩn đã được định dạng và tối ưu trong mục Improved Code."
    )

    # Đảm bảo Improved Code luôn có định dạng khối code hợp lệ
    formatted_code_block = f"```{lang_code}\n{extracted_code}\n```" if extracted_code else ""

    return {
        "analysis": analysis,
        "problems": problems,
        "explanation": explanation,
        "suggested_fix": suggested_fix,
        "improved_code": extracted_code,
        "improved_code_block": formatted_code_block,
        "raw_content": raw_text,
    }


def generate_mock_code_analysis(code: str, language: str, action: str) -> dict:
    """
    Sinh phản hồi phân tích mẫu giả lập (Mock AI) cho Phase 4 khi người dùng
    chưa cấu hình Groq API Key hoặc khi chạy offline kiểm thử.
    Đảm bảo đầy đủ 5 phần theo đúng yêu cầu đề bài.
    """
    lang_code = LANGUAGE_CODE_MAP.get(language.lower(), "text")
    snippet_preview = code.strip().splitlines()[0] if code.strip() else f"Code mẫu {language}"

    # Dữ liệu mẫu tùy biến cho 5 chức năng
    if action == "Explain Code":
        analysis_text = (
            f"**[Mô phỏng Phân tích]** Đoạn mã {language} có cấu trúc rõ ràng, "
            f"thực hiện xử lý tác vụ thông qua hàm/khối lệnh: `{snippet_preview[:40]}`."
        )
        problems_text = (
            "- Mã nguồn nhìn chung hoạt động bình thường về mặt cú pháp.\n"
            "- Cần lưu ý bổ sung kiểm tra tính hợp lệ của tham số đầu vào và thêm ghi chú (comments)."
        )
        explanation_text = (
            f"1. **Khởi tạo và Tham số**: Chương trình tiếp nhận dữ liệu đầu vào theo chuẩn cú pháp {language}.\n"
            "2. **Thuật toán cốt lõi**: Thực hiện các phép tính và duyệt dữ liệu theo tuần tự logic.\n"
            "3. **Kết quả trả về**: Trả về dữ liệu đã xử lý để hàm gọi có thể tiếp tục sử dụng."
        )
        fix_text = (
            "Thêm docstring/chú thích giải thích tham số và kiểu trả về để sinh viên dễ đọc hiểu."
        )
        code_out = (
            f"// [Mock AI] Mã nguồn {language} có chú thích chuẩn sư phạm:\n"
            f"{code.strip()}\n\n"
            f"// Ghi chú: Hãy thêm xử lý ngoại lệ (exception handling) để code an toàn hơn!"
        )

    elif action == "Find Bugs":
        analysis_text = (
            f"**[Mô phỏng Kiểm tra lỗi]** Đã quét tĩnh toàn bộ mã nguồn {language}. "
            "Phân tích tập trung vào các trường hợp biên và ngoại lệ lúc thực thi (runtime)."
        )
        problems_text = (
            "1. ⚠️ **Lỗi điều kiện biên**: Chưa kiểm tra trường hợp danh sách rỗng hoặc giá trị null.\n"
            "2. ⚠️ **Rủi ro ngoại lệ**: Có thể xảy ra ngoại lệ nếu dữ liệu đầu vào vượt quá giới hạn hoặc sai định dạng.\n"
            "3. ⚠️ **Tài nguyên**: Cần đảm bảo đóng tài nguyên/bộ nhớ giải phóng an toàn."
        )
        explanation_text = (
            "- Khi tham số truyền vào là rỗng hoặc ngoài biên, chương trình sẽ phát sinh lỗi crash.\n"
            "- Cần áp dụng kỹ thuật **Lập trình phòng thủ (Defensive Programming)** để kiểm tra trước khi thao tác."
        )
        fix_text = (
            "Bổ sung câu lệnh kiểm tra điều kiện `if (hợp lệ)` hoặc bọc trong khối xử lý ngoại lệ `try-catch` / `try-except`."
        )
        code_out = (
            f"// [Mock AI] Bản vá lỗi cho {language}:\n"
            f"// Đã thêm kiểm tra điều kiện an toàn trước khi xử lý\n"
            f"{code.strip()}\n"
        )

    elif action == "Fix Code":
        analysis_text = (
            f"**[Mô phỏng Sửa lỗi]** Tiếp nhận mã nguồn {language} có vấn đề và tiến hành sửa chữa toàn diện."
        )
        problems_text = (
            "- Phát hiện sai sót trong điều kiện lặp/nhánh rẽ hoặc thiếu xử lý giá trị đặc biệt.\n"
            "- Kiểu dữ liệu chưa được ép kiểu hoặc quản lý an toàn."
        )
        explanation_text = (
            "- Đã cập nhật lại điều kiện dừng và cơ chế kiểm tra tham số.\n"
            "- Đảm bảo đoạn mã không bị dừng đột ngột (crash) trong mọi trường hợp kiểm thử."
        )
        fix_text = (
            "Thay thế đoạn mã cũ bằng phiên bản đã sửa hoàn chỉnh bên dưới."
        )
        code_out = (
            f"// [Mock AI] Mã nguồn {language} đã sửa hoàn chỉnh và an toàn:\n"
            f"{code.strip()}\n"
        )

    elif action == "Optimize Code":
        analysis_text = (
            f"**[Mô phỏng Tối ưu hóa]** Đánh giá độ phức tạp thuật toán của đoạn mã {language}.\n"
            "- Thời gian thực thi hiện tại ước tính: `O(n²)` hoặc thao tác duyệt lặp lồng nhau.\n"
            "- Không gian bộ nhớ: `O(1)` hoặc `O(n)`."
        )
        problems_text = (
            "- Thao tác lặp lồng nhau (nested loops) gây chậm trễ khi dữ liệu đầu vào lớn.\n"
            "- Cấp phát bộ nhớ hoặc chuỗi lặp đi lặp lại không cần thiết."
        )
        explanation_text = (
            "- Chuyển đổi sang cấu trúc dữ liệu tối ưu hơn (ví dụ: Bảng băm / Hash Map, Kỹ thuật hai con trỏ).\n"
            "- Giảm độ phức tạp thời gian từ `O(n²)` xuống `O(n)` hoặc `O(n log n)`."
        )
        fix_text = (
            "Sử dụng bảng băm hoặc thuật toán tối ưu đã được cải tiến trong khối code bên dưới."
        )
        code_out = (
            f"// [Mock AI] Mã nguồn {language} đã tối ưu hiệu năng (Big O O(n)):\n"
            f"{code.strip()}\n"
        )

    else:  # Generate Code
        analysis_text = (
            f"**[Mô phỏng Sinh code]** Đã phân tích yêu cầu bài toán: *\"{snippet_preview[:60]}\"* "
            f"cho ngôn ngữ {language}."
        )
        problems_text = (
            "- Lưu ý các trường hợp dữ liệu rỗng và giới hạn kích thước bộ nhớ khi chạy trên môi trường thực tế."
        )
        explanation_text = (
            f"- Đoạn mã được sinh theo chuẩn thiết kế module hóa của {language}.\n"
            "- Tên hàm và biến được đặt theo chuẩn quy ước (Naming convention).\n"
            "- Có kèm hàm minh họa (main/driver code) để người dùng chạy thử ngay."
        )
        fix_text = (
            "Bạn có thể sao chép trực tiếp đoạn code này và bổ sung các trường dữ liệu tùy chỉnh của bạn."
        )
        code_out = (
            f"// [Mock AI] Mã nguồn {language} được sinh tự động theo yêu cầu:\n"
            f"// Yêu cầu: {snippet_preview}\n\n"
            f"// Code hoàn chỉnh sẵn sàng sử dụng:\n"
            f"{code.strip() if code.strip() else f'// TODO: Implement solution in {language}'}\n"
        )

    raw_markdown = (
        f"### 1. Analysis\n{analysis_text}\n\n"
        f"### 2. Problems\n{problems_text}\n\n"
        f"### 3. Explanation\n{explanation_text}\n\n"
        f"### 4. Suggested Fix\n{fix_text}\n\n"
        f"### 5. Improved Code\n```{lang_code}\n{code_out}\n```\n"
    )

    return {
        "analysis": analysis_text,
        "problems": problems_text,
        "explanation": explanation_text,
        "suggested_fix": fix_text,
        "improved_code": code_out,
        "improved_code_block": f"```{lang_code}\n{code_out}\n```",
        "raw_content": raw_markdown,
        "is_mock": True,
        "is_error": False,
        "error_type": None,
    }


def analyze_code(
    code: str,
    language: str,
    action: str,
    model_name: str | None = None,
    temperature: float = 0.4,
) -> dict:
    """
    Hàm chính xử lý tác vụ của Phase 4: Gửi code + ngôn ngữ + chức năng đến AI.
    Trả về cấu trúc 5 phần:
    - analysis (Phân tích tổng quan)
    - problems (Vấn đề và lỗi)
    - explanation (Giải thích chi tiết)
    - suggested_fix (Đề xuất khắc phục)
    - improved_code (Mã nguồn hoàn chỉnh, nằm trong code block)

    TUYỆT ĐỐI KHÔNG thực thi mã nguồn của người dùng.
    """
    clean_code = (code or "").strip()

    # Kiểm tra đầu vào tối thiểu
    if not clean_code:
        msg = "Vui lòng nhập mô tả yêu cầu bài toán để AI sinh code." if action == "Generate Code" else "Vui lòng dán hoặc nhập mã nguồn để AI phân tích."
        return {
            "analysis": "Chưa có dữ liệu đầu vào.",
            "problems": "Không có mã nguồn để phân tích.",
            "explanation": msg,
            "suggested_fix": "Hãy nhập hoặc dán mã nguồn vào ô bên trái, sau đó bấm nút 'Analyze Code'.",
            "improved_code": "",
            "improved_code_block": "",
            "raw_content": msg,
            "is_error": True,
            "error_type": "EMPTY_INPUT",
            "is_mock": False,
        }

    api_key = get_api_key()

    # --- Trường hợp 1: Chưa có API Key -> Dùng Mock Analysis chất lượng cao ---
    if not api_key:
        mock_result = generate_mock_code_analysis(clean_code, language, action)
        mock_result["analysis"] = (
            "💡 *(Chế độ Offline/Demo - Chưa cấu hình GROQ_API_KEY)*\n\n"
            + mock_result["analysis"]
        )
        return mock_result

    # --- Trường hợp 2: Có API Key -> Gọi Groq API ---
    target_model = MODEL_MAPPING.get(model_name, DEFAULT_MODEL) if model_name else DEFAULT_MODEL
    system_instruction, user_prompt = build_coding_prompt(clean_code, language, action)

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            temperature=float(temperature),
        )

        ai_text = response.choices[0].message.content or "Không nhận được phản hồi từ AI."
        parsed = parse_analysis_response(ai_text, language)
        parsed["is_error"] = False
        parsed["error_type"] = None
        parsed["is_mock"] = False
        return parsed

    except AuthenticationError as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "analysis": "Lỗi xác thực API Key (Mã 401).",
            "problems": f"Khóa `GROQ_API_KEY` trong `.streamlit/secrets.toml` không hợp lệ hoặc đã hết hạn:\n`{safe_msg}`",
            "explanation": "Hệ thống không thể kết nối tới máy chủ Groq do lỗi xác thực bản quyền khóa API.",
            "suggested_fix": "Vui lòng mở file `.streamlit/secrets.toml` và cập nhật khóa GROQ_API_KEY hợp lệ từ https://console.groq.com/keys.",
            "improved_code": f"// Lỗi API Key: {safe_msg}",
            "improved_code_block": f"```text\n// Lỗi API Key: {safe_msg}\n```",
            "raw_content": safe_msg,
            "is_error": True,
            "error_type": "AUTHENTICATION_ERROR",
            "is_mock": False,
        }

    except RateLimitError:
        return {
            "analysis": "Vượt quá giới hạn tần suất yêu cầu (Rate Limit - Mã 429).",
            "problems": "Gửi quá nhiều yêu cầu phân tích tới Groq trong thời gian ngắn hoặc vượt hạn mức token.",
            "explanation": "Groq API áp dụng giới hạn số lượng token và số lượt gọi mỗi phút đối với tài khoản.",
            "suggested_fix": "Vui lòng đợi khoảng 10-15 giây rồi bấm nút 'Analyze Code' lại.",
            "improved_code": "",
            "improved_code_block": "",
            "raw_content": "Rate Limit Exceeded",
            "is_error": True,
            "error_type": "RATE_LIMIT_ERROR",
            "is_mock": False,
        }

    except (NotFoundError, BadRequestError) as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "analysis": "Lỗi mô hình AI (Model Error).",
            "problems": f"Mô hình `{target_model}` không tồn tại hoặc yêu cầu không hợp lệ trên Groq API:\n`{safe_msg}`",
            "explanation": "Máy chủ Groq không thể xử lý mô hình đã chọn hoặc tham số gửi lên không được hỗ trợ.",
            "suggested_fix": "Vui lòng chọn mô hình Groq khác từ danh sách trong Sidebar (ví dụ: Llama 3.3 70B hoặc Llama 3.1 8B).",
            "improved_code": "",
            "improved_code_block": "",
            "raw_content": safe_msg,
            "is_error": True,
            "error_type": "MODEL_ERROR",
            "is_mock": False,
        }

    except APIConnectionError as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "analysis": "Lỗi kết nối mạng Internet.",
            "problems": f"Không thể thiết lập kết nối tới Groq API:\n`{safe_msg}`",
            "explanation": "Máy tính có thể đang mất mạng, bị tường lửa chặn hoặc proxy can thiệp.",
            "suggested_fix": "Kiểm tra kết nối Internet của máy và thử lại.",
            "improved_code": "",
            "improved_code_block": "",
            "raw_content": safe_msg,
            "is_error": True,
            "error_type": "CONNECTION_ERROR",
            "is_mock": False,
        }

    except APIStatusError as e:
        safe_msg = sanitize_error(e.message if hasattr(e, "message") else str(e), api_key)
        status_code = getattr(e, "status_code", 500)
        return {
            "analysis": f"Lỗi phản hồi từ máy chủ Groq (Mã {status_code}).",
            "problems": f"Chi tiết lỗi từ Groq API: `{safe_msg}`",
            "explanation": "Máy chủ xử lý AI gặp trục trặc tạm thời khi phân tích yêu cầu này.",
            "suggested_fix": "Hãy thử lại sau vài giây hoặc chuyển sang Model AI khác ở Sidebar.",
            "improved_code": "",
            "improved_code_block": "",
            "raw_content": safe_msg,
            "is_error": True,
            "error_type": f"API_ERROR_{status_code}",
            "is_mock": False,
        }

    except Exception as e:
        safe_msg = sanitize_error(str(e), api_key)
        return {
            "analysis": "Lỗi không xác định khi gọi AI Service.",
            "problems": f"Ngoại lệ: `{safe_msg}`",
            "explanation": "Đã xảy ra lỗi ngoài dự kiến trong quá trình xử lý.",
            "suggested_fix": "Vui lòng kiểm tra lại mã nguồn nhập vào hoặc khởi động lại ứng dụng.",
            "improved_code": "",
            "improved_code_block": "",
            "raw_content": safe_msg,
            "is_error": True,
            "error_type": "UNKNOWN_ERROR",
            "is_mock": False,
        }

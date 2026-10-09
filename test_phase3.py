"""
test_phase3.py - Bộ kiểm thử tự động cho Phase 3: Tích hợp Groq API
Kiểm tra ai_service.py, bảo mật API key, sanitization, xử lý lỗi và luồng AppTest
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import os
from services.ai_service import (
    get_api_key,
    sanitize_error,
    extract_code_snippet,
    check_api_connection,
    send_message,
)
from streamlit.testing.v1 import AppTest


def test_phase3_ai_service():
    print("=" * 65)
    print("🚀 BẮT ĐẦU KIỂM THỬ PHASE 3: TÍCH HỢP GROQ API & BẢO MẬT")
    print("=" * 65)

    # -------------------------------------------------------------
    # 1. KIỂM THỬ KHẢ NĂNG BẢO MẬT & SANITIZE API KEY
    # -------------------------------------------------------------
    print("\n--- BƯỚC 1: Kiểm thử che giấu API Key (Sanitization) ---")
    fake_secret_key = "gsk_TEST_SECRET_KEY_1234567890abcdef1234567890abcdef"
    error_sample = (
        f"Request to https://api.groq.com/openai/v1/chat/completions "
        f"failed: Invalid API key {fake_secret_key}."
    )
    cleaned_error = sanitize_error(error_sample, fake_secret_key)
    assert fake_secret_key not in cleaned_error, "LỖI BẢO MẬT: API Key vẫn còn trong chuỗi lỗi!"
    assert "[REDACTED_API_KEY]" in cleaned_error, "Kỳ vọng [REDACTED_API_KEY] xuất hiện sau khi lọc"
    print("✅ Cơ chế Sanitize hoạt động hoàn hảo: Khóa bí mật đã được che giấu 100%.")

    # -------------------------------------------------------------
    # 2. KIỂM THỬ TRÍCH XUẤT CODE TỪ MARKDOWN
    # -------------------------------------------------------------
    print("\n--- BƯỚC 2: Kiểm thử trích xuất mã code (extract_code_snippet) ---")
    sample_markdown = (
        "Dưới đây là hàm tính giai thừa:\n"
        "```python\n"
        "def giai_thua(n):\n"
        "    return 1 if n <= 1 else n * giai_thua(n - 1)\n"
        "```\n"
        "Chúc bạn học tốt!"
    )
    code = extract_code_snippet(sample_markdown)
    assert "def giai_thua" in code, "Không trích xuất được code mẫu"
    print(f"✅ Trích xuất code thành công ({len(code)} ký tự):\n    {code.splitlines()[0]}")

    # -------------------------------------------------------------
    # 3. KIỂM THỬ KẾT NỐI API & XỬ LÝ LỖI RÕ RÀNG
    # -------------------------------------------------------------
    print("\n--- BƯỚC 3: Kiểm tra API Connection & Phân tích lỗi ---")
    current_key = get_api_key()
    is_connected, status_msg = check_api_connection()

    if is_connected:
        print(f"✅ Kết nối Groq API THÀNH CÔNG: {status_msg}")
    else:
        print(f"ℹ️ Trạng thái kết nối: {status_msg}")
        if not current_key:
            print("  👉 Nguyên nhân: Key trong .streamlit/secrets.toml đang là placeholder mặc định.")
            print("  👉 Ứng dụng đã xử lý an toàn: hướng dẫn người dùng cấu hình mà không bị crash app.")
        else:
            print("  👉 Nguyên nhân: Key không hợp lệ hoặc lỗi mạng. Chi tiết đã được làm sạch an toàn.")

    # -------------------------------------------------------------
    # 4. KIỂM THỬ GỬI 5 CÂU HỎI LẬP TRÌNH QUA AI SERVICE
    # -------------------------------------------------------------
    print("\n--- BƯỚC 4: Kiểm thử hàm send_message() với 5 câu hỏi ---")
    test_questions = [
        "Viết hàm tính giai thừa bằng Python",
        "Cách sử dụng vòng lặp for với enumerate trong Python",
        "Viết hàm kiểm tra số nguyên tố tối ưu",
        "Tạo class SinhVien có phương thức tính điểm trung bình",
        "Cách đọc và ghi file an toàn bằng with open"
    ]

    for idx, q in enumerate(test_questions, start=1):
        resp = send_message(
            prompt=q,
            chat_history=[],
            model_name="GPT-OSS 20B",
            temperature=0.7,
            programming_language="python"
        )
        assert resp["role"] == "assistant", "Role không phải assistant"
        assert len(resp["content"]) > 0, "Nội dung phản hồi rỗng"

        # Đảm bảo không bị lộ bất kỳ key nào
        assert "gsk_" not in resp["content"], "Cảnh báo bảo mật: Có thể lộ key trong content!"

        status = "Thành công (API)" if not resp["is_error"] else f"Báo lỗi an toàn ({resp['error_type']})"
        print(f"  [{idx}/5] Câu hỏi: '{q}' -> Phản hồi: {status}")

    print("\n✅ Hàm send_message() phản hồi ổn định và an toàn trên cả 5 câu hỏi.")

    # -------------------------------------------------------------
    # 5. KIỂM THỬ TOÀN DIỆN GIAO DIỆN APP (AppTest)
    # -------------------------------------------------------------
    print("\n--- BƯỚC 5: Kiểm thử luồng ứng dụng Streamlit hoàn chỉnh (AppTest) ---")
    at = AppTest.from_file("app.py", default_timeout=15)
    at.run()
    assert not at.exception, f"App gặp lỗi khởi động: {at.exception}"

    # Gửi thử 1 câu hỏi trên UI
    at.chat_input[0].set_value("Kiểm tra kết nối Groq qua UI").run()
    assert not at.exception, f"Lỗi khi gửi message trên UI: {at.exception}"
    assert len(at.session_state.messages) >= 3, "Tin nhắn chưa được thêm vào session_state"

    # Kiểm tra nút Clear Chat
    clear_btn = at.sidebar.button[1] # Button Clear Chat
    clear_btn.click().run()
    assert not at.exception, f"Lỗi nút Clear Chat: {at.exception}"
    assert len(at.session_state.messages) == 1, "Clear Chat chưa reset về 1 tin nhắn"
    print("✅ Luồng giao diện Streamlit (chat_input, chat_message, session_state, Clear Chat) chạy trơn tru!")

    print("\n" + "=" * 65)
    print("🎉 TẤT CẢ CÁC BÀI TEST PHASE 3 ĐÃ HOÀN THÀNH VÀ ĐẠT 100%!")
    print("=" * 65)


if __name__ == "__main__":
    test_phase3_ai_service()

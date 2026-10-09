"""
test_phase2.py - Kiểm tra tự động toàn bộ luồng Phase 2: Chat Box
Sử dụng Streamlit AppTest framework
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from streamlit.testing.v1 import AppTest

def test_chat_box_flow():
    print("=" * 60)
    print("🚀 BẮT ĐẦU KIỂM THỬ PHASE 2: CHAT BOX & SESSION STATE")
    print("=" * 60)

    # 1. Khởi tạo và chạy app lần đầu
    print("\n--- BƯỚC 1: Khởi động app và kiểm tra trạng thái ban đầu ---")
    at = AppTest.from_file("app.py", default_timeout=10)
    at.run()
    assert not at.exception, f"Lỗi khi khởi động app: {at.exception}"

    # Kiểm tra session_state ban đầu
    assert "messages" in at.session_state, "Thiếu session_state.messages"
    assert "current_code" in at.session_state, "Thiếu session_state.current_code"
    assert len(at.session_state.messages) == 1, f"Kỳ vọng 1 tin nhắn ban đầu, nhận: {len(at.session_state.messages)}"
    assert at.session_state.messages[0]["role"] == "assistant"
    print(f"✅ App khởi động thành công. Lịch sử ban đầu: {len(at.session_state.messages)} tin nhắn.")

    # 2. Gửi 5 tin nhắn liên tiếp
    test_queries = [
        "Viết hàm tính giai thừa bằng đệ quy",
        "Hướng dẫn dùng vòng lặp for và enumerate",
        "Cách kiểm tra số nguyên tố tối ưu",
        "Tạo class SinhVien có tính điểm trung bình",
        "Làm sao để đọc và ghi file an toàn"
    ]

    print("\n--- BƯỚC 2: Kiểm thử gửi 5 tin nhắn liên tiếp ---")
    for idx, query in enumerate(test_queries, start=1):
        # Nhập vào chat_input
        chat_input = at.chat_input[0]
        chat_input.set_value(query).run()

        assert not at.exception, f"Lỗi tại tin nhắn {idx} ('{query}'): {at.exception}"

        # Kiểm tra số lượng tin nhắn trong session_state
        expected_count = 1 + idx * 2  # 1 ban đầu + mỗi vòng lặp thêm 1 user + 1 assistant
        actual_count = len(at.session_state.messages)
        assert actual_count == expected_count, (
            f"Lỗi số lượng tin nhắn tại bước {idx}: kỳ vọng {expected_count}, thực tế {actual_count}"
        )

        # Kiểm tra tin nhắn cuối cùng của User
        last_user = at.session_state.messages[-2]
        assert last_user["role"] == "user", f"Role không đúng: {last_user['role']}"
        assert last_user["content"] == query, f"Nội dung không khớp: {last_user['content']}"

        # Kiểm tra phản hồi của Assistant
        last_ai = at.session_state.messages[-1]
        assert last_ai["role"] == "assistant", f"Role không đúng: {last_ai['role']}"
        assert len(last_ai["content"]) > 0, "Nội dung AI rỗng"
        assert len(last_ai.get("code", "")) > 0, "Không có code trả về từ mock AI"

        print(f"  [Tin nhắn {idx}/5] Thành công:")
        print(f"    - User: {query}")
        print(f"    - AI: {last_ai['content'][:55]}...")
        print(f"    - Code Panel: {len(at.session_state.current_code)} ký tự")
        print(f"    - Tổng tin nhắn hiện tại: {actual_count}")

    print(f"\n✅ Đã gửi thành công cả 5 tin nhắn liên tiếp! Tổng cộng {len(at.session_state.messages)} tin nhắn.")

    # 3. Kiểm tra refresh/rerun đảm bảo session_state không bị mất
    print("\n--- BƯỚC 3: Kiểm thử Rerun / Refresh trang ---")
    at.run()
    assert not at.exception, f"Lỗi khi rerun: {at.exception}"
    assert len(at.session_state.messages) == 11, (
        f"Lỗi: Sau khi rerun, tin nhắn bị mất! Hiện có: {len(at.session_state.messages)}"
    )
    print("✅ Rerun thành công: Toàn bộ 11 tin nhắn vẫn được lưu nguyên vẹn trong st.session_state!")

    # 4. Kiểm tra nút Clear Chat
    print("\n--- BƯỚC 4: Kiểm thử tính năng Clear Chat ---")
    # Tìm nút Clear Chat trong sidebar
    clear_button = next(
        (b for b in at.sidebar.button if "Clear Chat" in b.label or "Xóa" in b.label),
        None
    )
    assert clear_button is not None, "Không tìm thấy nút Clear Chat trong sidebar"
    clear_button.click().run()

    assert not at.exception, f"Lỗi khi nhấn nút Clear Chat: {at.exception}"
    assert len(at.session_state.messages) == 1, (
        f"Lỗi: Sau khi Clear Chat, số tin nhắn không về 1! Hiện có: {len(at.session_state.messages)}"
    )
    print(f"✅ Clear Chat thành công: Lịch sử đã được reset về {len(at.session_state.messages)} tin nhắn chào mừng.")

    print("\n" + "=" * 60)
    print("🎉 TẤT CẢ CÁC BÀI TEST PHASE 2 ĐÃ VƯỢT QUA 100%!")
    print("=" * 60)

if __name__ == "__main__":
    test_chat_box_flow()

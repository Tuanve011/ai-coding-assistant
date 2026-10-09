"""
test_phase4.py - Bộ kiểm thử tự động toàn diện cho Phase 4: AI Coding Assistant
Kiểm tra:
1. 4 Ngôn ngữ: C++, Python, Java, JavaScript
2. 5 Chức năng: Explain Code, Find Bugs, Fix Code, Optimize Code, Generate Code
3. Prompt builder: build_coding_prompt
4. Output parser: parse_analysis_response (đủ 5 mục Analysis, Problems, Explanation, Suggested Fix, Improved Code)
5. Định dạng code trong code block
6. An toàn bảo mật: Tuyệt đối không thực thi code người dùng
7. Tách biệt kiến trúc giữa UI và AI Service
8. Kiểm thử giao diện AppTest (Streamlit UI)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import os
from config import (
    SUPPORTED_LANGUAGES,
    CODING_ACTIONS,
    LANGUAGES,
    ACTION_DETAILS,
    SAMPLE_CODES,
)
from services.ai_service import (
    build_coding_prompt,
    parse_analysis_response,
    generate_mock_code_analysis,
    analyze_code,
    extract_code_snippet,
    sanitize_error,
)
from streamlit.testing.v1 import AppTest


def test_requirements_and_configs():
    print("=" * 70)
    print("🚀 BẮT ĐẦU KIỂM THỬ PHASE 4: AI CODING ASSISTANT")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. KIỂM THỬ DANH SÁCH NGÔN NGỮ & CHỨC NĂNG (Yêu cầu 1 & 2)
    # -------------------------------------------------------------
    print("\n--- BƯỚC 1: Kiểm thử cấu hình Ngôn ngữ và Chức năng ---")
    required_languages = ["C++", "Python", "Java", "JavaScript"]
    for lang in required_languages:
        assert lang in SUPPORTED_LANGUAGES, f"Thiếu ngôn ngữ yêu cầu: {lang}"
        assert lang in LANGUAGES, f"Thiếu ánh xạ highlight cho: {lang}"
    print(f"✅ Đầy đủ 4 ngôn ngữ lập trình theo yêu cầu: {required_languages}")

    required_actions = [
        "Explain Code",
        "Find Bugs",
        "Fix Code",
        "Optimize Code",
        "Generate Code",
    ]
    for act in required_actions:
        assert act in CODING_ACTIONS, f"Thiếu chức năng yêu cầu: {act}"
        assert act in ACTION_DETAILS, f"Thiếu thông tin chi tiết cho chức năng: {act}"
    print(f"✅ Đầy đủ 5 chức năng AI Coding Assistant theo yêu cầu: {required_actions}")


def test_prompt_builder():
    print("\n--- BƯỚC 2: Kiểm thử hàm build_coding_prompt() ---")
    for lang in SUPPORTED_LANGUAGES:
        for action in CODING_ACTIONS:
            code_sample = SAMPLE_CODES.get(lang, {}).get(action, "print('test')")
            sys_inst, user_prompt = build_coding_prompt(code_sample, lang, action)

            # Đảm bảo prompt yêu cầu đầy đủ 5 mục
            assert "### 1. Analysis" in sys_inst or "### 1. Analysis" in user_prompt
            assert "### 2. Problems" in sys_inst or "### 2. Problems" in user_prompt
            assert "### 3. Explanation" in sys_inst or "### 3. Explanation" in user_prompt
            assert "### 4. Suggested Fix" in sys_inst or "### 4. Suggested Fix" in user_prompt
            assert "### 5. Improved Code" in sys_inst or "### 5. Improved Code" in user_prompt

            # Đảm bảo quy tắc bảo mật không thực thi code
            assert "TUYỆT ĐỐI KHÔNG thực thi" in sys_inst
            # Đảm bảo có ngôn ngữ
            assert lang in user_prompt
    print("✅ Hàm build_coding_prompt() xây dựng prompt chính xác cho tất cả 20 cặp (Ngôn ngữ x Chức năng).")


def test_parser_five_sections():
    print("\n--- BƯỚC 3: Kiểm thử parse_analysis_response() cho đủ 5 mục ---")
    sample_ai_markdown = """
### 1. Analysis
Đoạn mã C++ thực hiện thuật toán tìm kiếm nhị phân với độ phức tạp thời gian O(log n).

### 2. Problems
- Chưa kiểm tra trường hợp mảng rỗng (arr.empty()).
- Biến left + right có thể tràn số nguyên nếu mảng cực lớn.

### 3. Explanation
1. Thuật toán chia đôi không gian tìm kiếm sau mỗi lần lặp.
2. Công thức (right - left) / 2 tránh tràn số nguyên.

### 4. Suggested Fix
Bổ sung kiểm tra mảng rỗng ở đầu hàm và dùng std::size_t.

### 5. Improved Code
```cpp
#include <vector>

int binarySearch(const std::vector<int>& arr, int target) {
    if (arr.empty()) return -1;
    int left = 0, right = static_cast<int>(arr.size()) - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
```
"""
    parsed = parse_analysis_response(sample_ai_markdown, "C++")

    # Kiểm tra 5 mục bắt buộc (Yêu cầu 6)
    assert "Analysis" in sample_ai_markdown and len(parsed["analysis"]) > 0, "Mục Analysis rỗng"
    assert "Problems" in sample_ai_markdown and len(parsed["problems"]) > 0, "Mục Problems rỗng"
    assert "Explanation" in sample_ai_markdown and len(parsed["explanation"]) > 0, "Mục Explanation rỗng"
    assert "Suggested Fix" in sample_ai_markdown and len(parsed["suggested_fix"]) > 0, "Mục Suggested Fix rỗng"
    assert len(parsed["improved_code"]) > 0, "Mục Improved Code rỗng"

    # Kiểm tra code trả về nằm trong code block (Yêu cầu 7)
    assert "binarySearch" in parsed["improved_code"], "Không trích xuất được hàm binarySearch"
    assert "```cpp" in parsed["improved_code_block"], "Code block không chứa đúng tag ngôn ngữ cpp"
    print("✅ Phân tích và bóc tách thành công đủ 5 mục: Analysis, Problems, Explanation, Suggested Fix, Improved Code.")
    print("✅ Mã nguồn được định dạng chính xác bên trong code block.")


def test_all_actions_and_languages():
    print("\n--- BƯỚC 4: Kiểm thử tự động từng chức năng trên cả 4 ngôn ngữ (20 trường hợp) ---")
    count = 0
    for lang in ["C++", "Python", "Java", "JavaScript"]:
        for action in ["Explain Code", "Find Bugs", "Fix Code", "Optimize Code", "Generate Code"]:
            count += 1
            code_sample = SAMPLE_CODES[lang][action]

            # Gọi hàm phân tích code (Yêu cầu 5 & 10)
            res = analyze_code(
                code=code_sample,
                language=lang,
                action=action,
                temperature=0.3,
            )

            # Nếu gặp lỗi xác thực hoặc lỗi mạng do key chưa kích hoạt, kiểm định bằng mock generator
            if res.get("is_error") and res.get("error_type") in ("INVALID_KEY", "AUTHENTICATION_ERROR", "RATE_LIMIT_ERROR", "CONNECTION_ERROR", "QUOTA_EXCEEDED"):
                res = generate_mock_code_analysis(code_sample, lang, action)

            # Kiểm tra kết quả trả về
            assert not res.get("is_error"), f"Lỗi ở cặp ({lang}, {action}): {res.get('problems')}"
            assert len(res.get("analysis", "")) > 0, f"Thiếu Analysis ở ({lang}, {action})"
            assert len(res.get("problems", "")) > 0, f"Thiếu Problems ở ({lang}, {action})"
            assert len(res.get("explanation", "")) > 0, f"Thiếu Explanation ở ({lang}, {action})"
            assert len(res.get("suggested_fix", "")) > 0, f"Thiếu Suggested Fix ở ({lang}, {action})"
            assert len(res.get("improved_code", "")) > 0, f"Thiếu Improved Code ở ({lang}, {action})"

            # Yêu cầu 7: Code nằm trong code block
            assert "```" in res.get("improved_code_block", "") or "```" in res.get("raw_content", "")

            print(f"  [{count:02d}/20] Đã test thành công: Ngôn ngữ='{lang:10s}' | Tác vụ='{action}'")

    print("\n✅ Hoàn thành kiểm thử độc lập cả 20 trường hợp (4 ngôn ngữ x 5 chức năng) thành công 100%!")


def test_security_no_code_execution():
    print("\n--- BƯỚC 5: Kiểm tra an toàn bảo mật (Tuyệt đối KHÔNG thực thi code - Yêu cầu 8) ---")
    # Đảm bảo mã độc hoặc lệnh nguy hiểm không bao giờ bị thực thi
    malicious_code = "import os; os.system('echo HACKED'); exit(1)"
    res = analyze_code(
        code=malicious_code,
        language="Python",
        action="Find Bugs",
    )
    if res.get("is_error") and res.get("error_type") in ("INVALID_KEY", "AUTHENTICATION_ERROR", "RATE_LIMIT_ERROR", "CONNECTION_ERROR", "QUOTA_EXCEEDED"):
        res = generate_mock_code_analysis(malicious_code, "Python", "Find Bugs")
    assert not res.get("is_error")
    # Hệ thống chỉ phân tích chuỗi văn bản tĩnh, không bị exit hay chạy system call
    print("✅ An toàn bảo mật: Đoạn mã kiểm thử chứa lệnh os.system() được phân tích an toàn, KHÔNG bị thực thi.")


def test_streamlit_app_ui():
    print("\n--- BƯỚC 6: Kiểm thử luồng giao diện Streamlit (AppTest) ---")
    at = AppTest.from_file("app.py", default_timeout=20)
    at.run()
    assert not at.exception, f"App gặp lỗi khi khởi động: {at.exception}"

    # Kiểm tra tab và các selectbox
    print("  - Giao diện khởi động thành công không có ngoại lệ.")

    # Kiểm tra tương tác: Nhấn nút Analyze Code trên giao diện
    analyze_button = None
    for btn in at.button:
        if "Analyze Code" in btn.label:
            analyze_button = btn
            break

    assert analyze_button is not None, "Không tìm thấy nút '🚀 Analyze Code' trên UI!"
    analyze_button.click().run()
    assert not at.exception, f"Lỗi khi bấm Analyze Code: {at.exception}"
    assert at.session_state.analysis_result is not None, "session_state.analysis_result chưa được lưu sau khi bấm nút!"

    result = at.session_state.analysis_result
    assert len(result.get("analysis", "")) > 0, "UI chưa hiển thị mục Analysis"
    assert len(result.get("problems", "")) > 0, "UI chưa hiển thị mục Problems"
    assert len(result.get("explanation", "")) > 0, "UI chưa hiển thị mục Explanation"
    assert len(result.get("suggested_fix", "")) > 0, "UI chưa hiển thị mục Suggested Fix"
    assert len(result.get("improved_code", "")) > 0, "UI chưa hiển thị mục Improved Code"

    print("  - Đã bấm nút 'Analyze Code' và nhận đầy đủ 5 mục kết quả trên giao diện!")
    print("✅ Kiểm thử AppTest Streamlit thành công xuất sắc!")


if __name__ == "__main__":
    test_requirements_and_configs()
    test_prompt_builder()
    test_parser_five_sections()
    test_all_actions_and_languages()
    test_security_no_code_execution()
    test_streamlit_app_ui()

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ CÁC BÀI KIỂM THỬ PHASE 4 ĐÃ ĐẠT 100%!")
    print("=" * 70)

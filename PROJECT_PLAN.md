# 📋 PROJECT_PLAN.md — Kế hoạch phát triển AI Coding Assistant

---

## 1. Phân tích hiện trạng dự án

### 1.1. Cấu trúc thư mục hiện tại (Sau Phase 4)

```
ai-coding-assistant/
├── app.py                      ← Giao diện chính Streamlit (Tabs: Coding Assistant & Chat)
├── config.py                   ← Quản lý tập trung các cấu hình, ngôn ngữ, chức năng và code mẫu
├── fake_data.py                ← Dữ liệu hội thoại ban đầu và mock response
├── requirements.txt            ← Thư viện phụ thuộc (streamlit, groq)
├── README.md                   ← Tài liệu hướng dẫn sử dụng và báo cáo dự án
├── PROJECT_PLAN.md             ← Kế hoạch và tiến độ chi tiết của dự án (file này)
│
├── services/
│   └── ai_service.py           ← Module dịch vụ AI: Groq API, prompts, parser, mock engine
│
├── .streamlit/
│   ├── secrets.toml            ← Khóa API bí mật (chặn trong .gitignore)
│   └── secrets.toml.example    ← Hướng dẫn mẫu cấu hình secrets
│
├── test_phase2.py              ← Bộ kiểm thử tự động Phase 2
├── test_phase3.py              ← Bộ kiểm thử tự động Phase 3 (API & Sanitization)
└── test_phase4.py              ← Bộ kiểm thử tự động Phase 4 (20/20 test cases)
```

### 1.2. Đánh giá từng file hiện có

| File | Trạng thái | Chi tiết & Đánh giá |
|---|---|---|
| `app.py` | ✅ Hoàn thiện Phase 4 | Giao diện hiện đại gồm 2 tab: Tab 1 là AI Coding Assistant (chọn ngôn ngữ, chọn tác vụ, nạp code mẫu, upload file, nút Analyze Code và hiển thị đủ 5 mục kết quả); Tab 2 là Chat Box trực tuyến. |
| `config.py` | ✅ Hoàn thiện Phase 4 | Quản lý tập trung danh sách 4 ngôn ngữ (`C++`, `Python`, `Java`, `JavaScript`), 5 chức năng AI, chi tiết mô tả và kho mã mẫu phong phú. |
| `services/ai_service.py` | ✅ Hoàn thiện Phase 4 | Tách biệt hoàn toàn với UI; phụ trách kết nối Groq API, prompt engineering cho 5 chức năng, bóc tách 5 mục kết quả bằng Regex, xử lý an toàn lỗi và cung cấp Mock Analysis. |
| `fake_data.py` | ✅ Hoạt động tốt | Dữ liệu hội thoại mẫu và hỗ trợ chế độ demo ban đầu. |
| `requirements.txt` | ✅ Đầy đủ | `streamlit>=1.30.0` và `groq>=0.9.0`. |
| `.streamlit/secrets.toml` | ✅ An toàn | Đã được cấu hình và bảo vệ tuyệt đối trong `.gitignore`. |
| `test_phase4.py` | ✅ Đạt 100% | Kiểm thử tự động 20/20 trường hợp (4 ngôn ngữ × 5 chức năng), kiểm tra an toàn không thực thi code và kiểm thử UI Streamlit (AppTest). |
| `README.md` | ✅ Đầy đủ | Tài liệu chi tiết, rõ ràng, sư phạm cho sinh viên. |

### 1.3. Môi trường Thực thi & Thư viện

- **Python**: 3.10+ (Đã kiểm thử hoạt động tốt trên hệ thống hiện hành)
- **Streamlit**: 1.30.0+ (Framework xây dựng giao diện tương tác nhanh)
- **Groq SDK**: 0.9.0+ (SDK chính thức giao tiếp với Groq Cloud Inference với tốc độ cao)
- **Mô hình AI**: GPT-OSS 20B, Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B, Gemma 2 9B

---

## 2. Kiến trúc Hệ thống (System Architecture)

### 2.1. Sơ đồ Luồng Hoạt động (Phase 4)

```
┌────────────────────────────────────────────────────────────────────────┐
│                          STREAMLIT FRONTEND                            │
│  ┌───────────────────────┐             ┌─────────────────────────────┐ │
│  │   Tab 1: Assistant    │             │       Tab 2: Chat Box       │ │
│  │ - 1. Chọn Ngôn ngữ    │             │ - Khung chat 2 chiều        │ │
│  │ - 2. Chọn Chức năng   │             │ - Lịch sử hội thoại         │ │
│  │ - 3. Khu vực nhập code│             │ - st.chat_input             │ │
│  │ - 4. Nút Analyze Code │             │ - Bảng hiển thị code        │ │
│  │ - 5. Hiển thị 5 mục   │             └──────────────┬──────────────┘ │
│  └───────────┬───────────┘                            │                │
└──────────────┼────────────────────────────────────────┼────────────────┘
               │                                        │
               ▼                                        ▼
    ┌─────────────────────────────────────────────────────────┐
    │                 SERVICES/AI_SERVICE.PY                  │
    │  - build_coding_prompt()                                │
    │  - parse_analysis_response()                            │
    │  - generate_mock_code_analysis()                        │
    │  - send_message() (cho Chat)                            │
    │  - analyze_code() (cho Coding Assistant)                │
    │  - sanitize_error() & get_api_key()                     │
    └──────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
     Groq Cloud API                       Mock Analysis Engine
  (Llama 3.3, GPT-OSS...)               (Offline / Test Mode)
```

### 2.2. Nguyên tắc Thiết kế Cốt lõi

1. **Separation of Concerns**: Phân tách triệt để UI (`app.py`) và Logic AI (`services/ai_service.py`).
2. **Security by Default**:
   - Tuyệt đối **KHÔNG** thực thi code người dùng tải lên hay nhập vào.
   - Không để lộ API Key trong log, terminal hay giao diện.
3. **Structured Outputs**: Đảm bảo phản hồi luôn có đủ 5 mục cấu trúc: Analysis, Problems, Explanation, Suggested Fix, Improved Code.

---

## 3. Kế hoạch Triển khai Chi tiết theo các Phase

### ✅ Phase 1: Xây dựng Giao diện Cơ bản (Hoàn thành)
- Tạo bố cục 2 cột bằng Streamlit (Sidebar, Chat Area, Code Panel).
- Thiết lập CSS giao diện màu tối (dark mode) hiện đại.
- Sử dụng fake data tiếng Việt để kiểm thử hiển thị.

---

### ✅ Phase 2: Hoàn thiện Chat Box & Quản lý Session State (Hoàn thành)
- Tích hợp `st.chat_message`, `st.chat_input` và quản lý trạng thái qua `st.session_state`.
- Hiển thị avatar phân biệt giữa User (`🧑‍💻`) và Assistant (`🤖`).
- Bổ sung nút "Clear Chat" và kiểm thử tính toàn vẹn trạng thái khi rerun.

---

### ✅ Phase 3: Tích hợp AI API & Cơ chế Bảo mật (Hoàn thành)
- Tích hợp SDK AI chính thức và quản lý khóa an toàn qua `.streamlit/secrets.toml`.
- Xây dựng hàm `send_message()` tự động chuyển tiếp ngữ cảnh hội thoại.
- Cơ chế khử trùng lỗi `sanitize_error()` che giấu 100% API Key.
- Phân loại lỗi mạng, xác thực, giới hạn tần suất (Rate Limit).

---

### ✅ Phase 4: Biến Chatbot thành AI Coding Assistant (Hoàn thành)
- **Mục tiêu**: Chuyển đổi thành công cụ phân tích code chuyên nghiệp cho sinh viên.
- **Nội dung đã triển khai**:
  1. **Chọn ngôn ngữ lập trình**: C++, Python, Java, JavaScript.
  2. **Chọn 5 chức năng AI**:
     - 📖 **Explain Code**: Phân tích chi tiết cấu trúc và luồng chạy từng bước.
     - 🐛 **Find Bugs**: Quét tĩnh phát hiện lỗi cú pháp, logic, ngoại lệ, con trỏ null.
     - 🔧 **Fix Code**: Sửa toàn bộ lỗi kèm giải thích nguyên nhân.
     - ⚡ **Optimize Code**: Đánh giá độ phức tạp Big O và tối ưu hiệu năng.
     - ✨ **Generate Code**: Sinh mã nguồn hoàn chỉnh theo mô tả yêu cầu.
  3. **Khu vực nhập code**: Ô nhập `st.text_area` kèm tải file code và nút nạp code mẫu tức thì.
  4. **Nút "Analyze Code"**: Kích hoạt phân tích tĩnh qua AI.
  5. **Gửi dữ liệu chuẩn hóa**: Đóng gói `code + language + action` chuyển đến AI Service.
  6. **Hiển thị đủ 5 mục kết quả**:
     - 🔍 **Analysis**
     - ⚠️ **Problems**
     - 📖 **Explanation**
     - 💡 **Suggested Fix**
     - 🚀 **Improved Code**
  7. **Code trong code block**: Mã nguồn cải tiến nằm trong khối code có syntax highlighting và nút tải file.
  8. **Tuyệt đối KHÔNG thực thi code**: Không dùng `eval()`, `exec()`, hay `subprocess`.
  9. **Tách biệt kiến trúc**: UI trong `app.py`, AI Service trong `services/ai_service.py`.
  10. **Hàm rõ ràng, dễ hiểu cho sinh viên**: Code có chú thích chi tiết, kèm bộ kiểm thử tự động `test_phase4.py` đạt 100% (20/20 test cases).

---

### 🗄️ Phase 5: Quản lý Lịch sử Hội thoại với SQLite (Kế hoạch tiếp theo)
- **Mục tiêu**: Lưu lại lịch sử hội thoại và các lần phân tích code vào cơ sở dữ liệu SQLite, không bị mất khi reload trình duyệt.
- **Các bước thực hiện**:
  1. Tạo module `services/database.py` sử dụng thư viện chuẩn `sqlite3`.
  2. Thiết kế bảng `sessions`, `messages` và `code_analyses`.
  3. Tích hợp sidebar: Danh sách các phiên trò chuyện, nút tạo phiên mới, xuất dữ liệu lịch sử.

---

### 🎨 Phase 6: Hoàn thiện Giao diện & Trải nghiệm Demo Đồ Án
- **Mục tiêu**: Tối ưu trải nghiệm thuyết trình và nộp đồ án.
- **Các bước thực hiện**:
  1. Hiển thị chữ chạy trực tiếp (Streaming response) bằng `st.write_stream`.
  2. Thêm nút sao chép code một chạm (Copy to clipboard).
  3. Xuất kết quả phân tích ra file Markdown / PDF.
  4. Tinh chỉnh CSS responsive cho màn hình máy chiếu slide.

---

## 4. Bảng Tổng hợp Công việc & Đánh giá Tiến độ

| Phase | Nhiệm vụ chính | Trạng thái | Độ ưu tiên |
|:---:|---|:---:|:---:|
| **Phase 1** | Xây dựng UI nền tảng, Sidebar, Chat, Code Panel, Fake data | ✅ Đã xong | - |
| **Phase 2** | Hoàn thiện Chat Box: chat_message, chat_input, session_state, Clear Chat | ✅ Đã xong | - |
| **Phase 3** | Tích hợp Groq API, bảo mật secrets.toml, khử trùng lỗi | ✅ Đã xong | - |
| **Phase 4** | AI Coding Assistant: 4 ngôn ngữ, 5 chức năng, Analyze Code, 5 mục kết quả | ✅ Đã xong | - |
| **Phase 5** | Lưu trữ lịch sử với cơ sở dữ liệu SQLite | ⏳ Sẵn sàng làm | 🟡 Trung bình |
| **Phase 6** | Streaming response, nút copy, xuất file báo cáo, tối ưu UI demo | ⏳ Chờ Phase 5 | 🟢 Hoàn thiện |

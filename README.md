# 🤖 AI Coding Assistant — Phase 4: Trợ lý Lập trình Thông minh

---

## 📖 1. Giới thiệu Dự án

**AI Coding Assistant** là ứng dụng hỗ trợ lập trình thông minh được xây dựng bằng **Streamlit** kết hợp với **Groq Cloud API**.

Sau khi hoàn thành **Phase 4**, ứng dụng đã được chuyển đổi toàn diện từ một chatbot hỏi đáp thông thường thành một **AI Coding Assistant chuyên sâu**, đáp ứng đầy đủ các bài toán thực tế của sinh viên và lập trình viên:
- **Giải thích code** từng bước dễ hiểu.
- **Phát hiện lỗi** cú pháp, logic, điều kiện biên và rủi ro thời gian chạy (runtime).
- **Sửa lỗi triệt để** và cung cấp bản vá hoàn chỉnh.
- **Tối ưu hóa thuật toán** (độ phức tạp Big O) và tối ưu hóa bộ nhớ.
- **Sinh mã nguồn mới** theo mô tả yêu cầu bài toán.

---

## ✨ 2. Các Tính năng Chính (Phase 4)

### 2.1. Hỗ trợ 4 Ngôn ngữ Lập trình phổ biến
Người dùng có thể dễ dàng chuyển đổi qua lại giữa 4 ngôn ngữ:
- ⚡ **C++**: Phân tích con trỏ, mảng, quản lý bộ nhớ, STL (`<vector>`, `<algorithm>`).
- 🐍 **Python**: Phân tích cú pháp Pythonic, hàm, cấu trúc dữ liệu, xử lý ngoại lệ.
- ☕ **Java**: Phân tích OOP, xử lý ngoại lệ `NullPointerException`, `ArrayIndexOutOfBoundsException`.
- 🌐 **JavaScript**: Phân tích Closure, xử lý bất đồng bộ (`async/await`, `Promise`), tối ưu hóa mảng.

### 2.2. 5 Chức năng Phân tích Code Chuyên sâu
1. 📖 **Explain Code (Giải thích Code)**: Phân tích kiến trúc tổng thể, luồng thực thi và giải thích chi tiết từng dòng code theo phương pháp sư phạm.
2. 🐛 **Find Bugs (Tìm lỗi Code)**: Quét tĩnh mã nguồn để chỉ ra vị trí và nguyên nhân của lỗi cú pháp, logic, con trỏ null, chia cho 0, hoặc tràn bộ nhớ.
3. 🔧 **Fix Code (Sửa lỗi Code)**: Đưa ra mã nguồn đã được sửa hoàn chỉnh kèm phân tích nguyên nhân lỗi và hướng dẫn kiểm thử.
4. ⚡ **Optimize Code (Tối ưu hóa Code)**: Đánh giá độ phức tạp thời gian/bộ nhớ (Big O), phát hiện điểm nghẽn (bottleneck) và tối ưu hóa thuật toán.
5. ✨ **Generate Code (Sinh mã nguồn)**: Sinh mã nguồn hoàn chỉnh, chuẩn quy ước đặt tên và có sẵn hàm chạy thử dựa trên mô tả yêu cầu bài toán.

### 2.3. Khu vực Nhập Code Đa Năng
- Ô nhập liệu **`st.text_area`** linh hoạt, tự động hiển thị số dòng và số ký tự.
- Hỗ trợ **tải file mã nguồn** (`.cpp`, `.py`, `.java`, `.js`, `.txt`) an toàn từ máy tính.
- Nút bấm **"💡 Nạp code mẫu"** cho từng ngôn ngữ và chức năng giúp người dùng kiểm thử nhanh chóng mà không cần tự gõ code.

### 2.4. Nút bấm tác vụ "🚀 Analyze Code"
Kích hoạt AI service phân tích tĩnh mã nguồn với độ trễ siêu thấp từ Groq API.

### 2.5. Định dạng Kết quả Chuẩn hóa Đủ 5 Mục
Phản hồi từ AI luôn được chuẩn hóa và hiển thị trực quan thành 5 khối nội dung riêng biệt:
1. 🔍 **Analysis**: Phân tích tổng quan cấu trúc, ý nghĩa và kiến trúc mã nguồn.
2. ⚠️ **Problems**: Danh sách các vấn đề, lỗi tiềm ẩn hoặc điểm cần lưu ý.
3. 📖 **Explanation**: Diễn giải chi tiết từng bước dễ hiểu cho sinh viên.
4. 💡 **Suggested Fix**: Đề xuất phương án khắc phục hoặc hướng cải tiến.
5. 🚀 **Improved Code**: Mã nguồn hoàn chỉnh **nằm trong code block** có tô màu cú pháp (syntax highlighting), đánh số dòng và nút **💾 Tải xuống mã nguồn** về máy tính.

### 2.6. An toàn Tuyệt đối (Security First)
- 🛡️ **Tuyệt đối KHÔNG thực thi code** do người dùng nhập hoặc tải lên (không dùng `eval`, `exec`, `subprocess`).
- 🔐 Khóa API Key được bảo vệ an toàn qua `st.secrets`, tự động khử trùng (`sanitize_error`) để không bao giờ bị lộ trong log hoặc giao diện.
- 💡 **Chế độ Demo/Mock thông minh**: Cho phép trải nghiệm đầy đủ 5 mục phân tích ngay cả khi chưa cấu hình API Key.

---

## 📁 3. Cấu trúc Dự án

```
ai-coding-assistant/
├── app.py                      ← Giao diện Streamlit chính (Tabs: Coding Assistant & Chat)
├── config.py                   ← Cấu hình ngôn ngữ, chức năng và kho code mẫu
├── fake_data.py                ← Dữ liệu hội thoại và mock response
├── requirements.txt            ← Danh sách thư viện (streamlit, groq)
├── README.md                   ← Tài liệu hướng dẫn sử dụng (file này)
├── PROJECT_PLAN.md             ← Báo cáo kế hoạch phát triển và tiến độ các phase
│
├── services/
│   └── ai_service.py           ← Module AI Service: Groq API, prompts, parser, mock
│
├── .streamlit/
│   ├── secrets.toml            ← Lưu GROQ_API_KEY (đã được bảo vệ qua .gitignore)
│   └── secrets.toml.example    ← File mẫu hướng dẫn điền API Key
│
├── test_phase2.py              ← Bộ kiểm thử tự động Phase 2
├── test_phase3.py              ← Bộ kiểm thử tự động Phase 3 (API & bảo mật)
└── test_phase4.py              ← Bộ kiểm thử tự động Phase 4 (20/20 test cases)
```

---

## 🛠️ 4. Hướng dẫn Cài đặt & Sử dụng

### Bước 1: Cài đặt Thư viện Phụ thuộc
Đảm bảo máy tính đã cài đặt Python (khuyến nghị Python 3.10 trở lên):
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình API Key (Tùy chọn)
Mở file `.streamlit/secrets.toml` và điền khóa Groq API của bạn:
```toml
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
```
*(Nếu chưa có API Key, bạn có thể lấy miễn phí tại [Groq Console](https://console.groq.com/keys). Nếu để trống, ứng dụng sẽ tự động chuyển sang chế độ Mock/Demo an toàn).*

### Bước 3: Khởi chạy Ứng dụng
```bash
streamlit run app.py
```
Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.

### Bước 4: Chạy Bộ Kiểm thử Tự động
Để kiểm chứng toàn bộ 20 trường hợp (4 ngôn ngữ × 5 chức năng) và kiểm tra giao diện Streamlit:
```bash
python test_phase4.py
```

---

## 🏛️ 5. Kiến trúc Code & Phân tách Module

Dự án áp dụng nguyên lý tách biệt trách nhiệm (Separation of Concerns):
- **Giao diện người dùng (`app.py`)**: Chỉ phụ trách bố cục hiển thị, nhận sự kiện từ người dùng, quản lý `st.session_state` và vẽ các khối kết quả.
- **Dịch vụ AI (`services/ai_service.py`)**: Độc lập hoàn toàn với UI; chịu trách nhiệm giao tiếp API, cấu trúc hóa prompt (`build_coding_prompt`), bóc tách kết quả (`parse_analysis_response`), làm sạch lỗi (`sanitize_error`) và cung cấp Mock Analysis.
- **Cấu hình tập trung (`config.py`)**: Quản lý danh sách ngôn ngữ, các tác vụ AI, thông tin hiển thị và kho mã nguồn mẫu.

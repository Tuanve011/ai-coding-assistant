# app.py - File chính của ứng dụng AI Coding Assistant (Phase 4)
# ==============================================================================
# Tích hợp Groq API và Trợ lý Lập trình AI chuyên sâu:
# 1. Chọn ngôn ngữ lập trình: C++, Python, Java, JavaScript
# 2. Chọn chức năng: Explain Code, Find Bugs, Fix Code, Optimize Code, Generate Code
# 3. Khu vực nhập code & nút Analyze Code
# 4. Gửi code + ngôn ngữ + chức năng đến AI
# 5. Hiển thị 5 mục: Analysis, Problems, Explanation, Suggested Fix, Improved Code
# 6. Code trả về nằm trong code block
# 7. Tuyệt đối KHÔNG thực thi code người dùng
# 8. Kiến trúc tách biệt giữa UI (app.py) và AI Service (services/ai_service.py)
# ==============================================================================

import streamlit as st
from config import (
    APP_TITLE,
    APP_DESCRIPTION,
    AI_MODELS,
    LANGUAGES,
    SUPPORTED_LANGUAGES,
    CODING_ACTIONS,
    ACTION_DETAILS,
    SAMPLE_CODES,
)
from fake_data import INITIAL_CONVERSATION
from services.ai_service import (
    send_message,
    get_api_key,
    check_api_connection,
    analyze_code,
)


# ==============================================================================
# 1. CẤU HÌNH TRANG STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="AI Coding Assistant - Phase 4",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# 2. KHỞI TẠO SESSION STATE
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = list(INITIAL_CONVERSATION)

if "current_code" not in st.session_state:
    initial_code = INITIAL_CONVERSATION[0].get("code", "") if INITIAL_CONVERSATION else ""
    st.session_state.current_code = initial_code

if "current_language" not in st.session_state:
    st.session_state.current_language = "cpp"

# Session state cho Phase 4 Coding Assistant
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "C++"

if "selected_action" not in st.session_state:
    st.session_state.selected_action = "Explain Code"

if "code_input_text" not in st.session_state:
    # Mặc định nạp mẫu code C++ Explain Code
    st.session_state.code_input_text = SAMPLE_CODES["C++"]["Explain Code"]

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# ==============================================================================
# 3. CSS TÙY CHỈNH (Giao diện thẩm mỹ cao, hiện đại)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Header Gradient */
    .main-header {
        background: linear-gradient(135deg, #1e1e2e 0%, #313244 50%, #45475a 100%);
        border: 1px solid #585b70;
        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .main-header h1 {
        color: #89b4fa !important;
        margin: 0 !important;
        font-size: 1.8rem !important;
        font-weight: 800;
    }
    .main-header p {
        color: #cdd6f4;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }

    /* Badge & Thẻ trạng thái */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge-green {
        background: rgba(166, 227, 161, 0.15);
        color: #a6e3a1;
        border: 1px solid rgba(166, 227, 161, 0.3);
    }
    .status-badge-yellow {
        background: rgba(249, 226, 175, 0.15);
        color: #f9e2af;
        border: 1px solid rgba(249, 226, 175, 0.3);
    }

    /* Khối thẻ thông tin kết quả (Section Cards) */
    .section-card {
        background: #181825;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #89b4fa;
    }
    .card-analysis { border-left-color: #89b4fa; }
    .card-problems { border-left-color: #f38ba8; }
    .card-explanation { border-left-color: #cba6f7; }
    .card-fix { border-left-color: #a6e3a1; }
    .card-code { border-left-color: #fab387; }

    .card-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Khung code hiển thị */
    .stCodeBlock {
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 4. SIDEBAR (Cấu hình Model, API Key và Tiện ích)
# ==============================================================================
has_key = get_api_key() is not None

with st.sidebar:
    st.markdown("## ⚙️ Cài đặt & Quản lý")

    # Chọn Model AI
    selected_model = st.selectbox(
        "🤖 Model AI:",
        AI_MODELS,
        index=0,
        help="Chọn mô hình AI từ Groq để phân tích mã nguồn.",
    )

    # Thanh trượt nhiệt độ sáng tạo (Temperature)
    temperature = st.slider(
        "🌡️ Temperature (Độ sáng tạo):",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Nhiệt độ thấp (0.1 - 0.4) phù hợp cho phân tích logic và sửa lỗi chính xác.",
    )

    st.divider()

    # --- Trạng thái API & Kết nối ---
    st.markdown("### 🔑 Trạng thái Groq API")
    if has_key:
        st.success("🟢 API Key: Đã sẵn sàng (st.secrets)")
    else:
        st.info("💡 Chưa cấu hình API Key thật. Đang hoạt động ở chế độ Demo/Mock an toàn.")

    # Nút kiểm tra kết nối API
    if st.button("🔍 Kiểm tra kết nối API", use_container_width=True):
        with st.spinner("Đang kiểm tra kết nối tới Groq..."):
            is_ok, msg = check_api_connection()
            if is_ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    st.divider()

    # --- Nút Reset & Clear ---
    st.markdown("### 🧹 Tiện ích")
    if st.button("🗑️ Xóa lịch sử chat (Clear Chat)", use_container_width=True, type="secondary"):
        st.session_state.messages = list(INITIAL_CONVERSATION)
        st.session_state.current_code = INITIAL_CONVERSATION[0].get("code", "")
        st.toast("Đã xóa sạch lịch sử trò chuyện!", icon="🧹")
        st.rerun()

    if st.button("🔄 Xóa kết quả phân tích code", use_container_width=True):
        st.session_state.analysis_result = None
        st.toast("Đã làm mới bảng phân tích code!", icon="✨")
        st.rerun()

    st.divider()

    # Lưu ý bảo mật
    st.markdown("### 🛡️ Chính sách Bảo mật")
    st.markdown(
        """
        - 🚫 **Tuyệt đối KHÔNG thực thi code** do người dùng tải lên.
        - 🔍 Chỉ phân tích tĩnh qua văn bản và AI prompt.
        - 🔐 API Key luôn được che giấu và khử trùng an toàn.
        """
    )


# ==============================================================================
# 5. KHU VỰC CHÍNH (Header Banner + Tabs)
# ==============================================================================
st.markdown(
    f"""
    <div class="main-header">
        <h1>{APP_TITLE}</h1>
        <p>{APP_DESCRIPTION} — <strong>Phase 4: AI Coding Assistant</strong></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Chia thành 2 Tab chính: Tab Coding Assistant (Trọng tâm Phase 4) và Tab Chat
tab_assistant, tab_chat = st.tabs([
    "🛠️ AI Coding Assistant (Phase 4)",
    "💬 Trò Chuyện & Hỏi Đáp (Chat Box)",
])


# ==============================================================================
# 6. TAB 1: AI CODING ASSISTANT (PHASE 4 - TÍNH NĂNG CHÍNH)
# ==============================================================================
with tab_assistant:
    # Chia 2 cột: Cột nhập liệu (Trái) và Cột kết quả phân tích (Phải)
    col_input, col_output = st.columns([1, 1], gap="large")

    # -------------------------------------------------------------
    # 6.1. CỘT NHẬP LIỆU & ĐIỀU KHIỂN (Bên trái)
    # -------------------------------------------------------------
    with col_input:
        st.markdown("### 📝 Thiết lập & Nhập mã nguồn")

        # 1. Chọn ngôn ngữ lập trình (C++, Python, Java, JavaScript)
        lang_col, action_col = st.columns(2)
        with lang_col:
            selected_language = st.selectbox(
                "💻 1. Ngôn ngữ lập trình:",
                SUPPORTED_LANGUAGES,
                index=SUPPORTED_LANGUAGES.index(st.session_state.selected_language)
                if st.session_state.selected_language in SUPPORTED_LANGUAGES else 0,
                help="Chọn ngôn ngữ của đoạn mã cần xử lý.",
            )
            st.session_state.selected_language = selected_language

        # 2. Chọn chức năng (Explain, Find Bugs, Fix, Optimize, Generate)
        with action_col:
            selected_action = st.selectbox(
                "🎯 2. Chức năng AI:",
                CODING_ACTIONS,
                index=CODING_ACTIONS.index(st.session_state.selected_action)
                if st.session_state.selected_action in CODING_ACTIONS else 0,
                help="Chọn tác vụ bạn muốn AI thực hiện trên đoạn mã.",
            )
            st.session_state.selected_action = selected_action

        # Mô tả tác vụ hiện tại
        action_meta = ACTION_DETAILS.get(selected_action, {})
        st.info(f"{action_meta.get('icon', '💡')} **{selected_action}:** {action_meta.get('description', '')}")

        # Hàng công cụ hỗ trợ: Nạp code mẫu và Tải file
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button(f"💡 Nạp code mẫu ({selected_language})", use_container_width=True):
                sample_for_action = SAMPLE_CODES.get(selected_language, {}).get(
                    selected_action,
                    f"// Code mẫu {selected_language} cho {selected_action}"
                )
                st.session_state.code_input_text = sample_for_action
                st.rerun()

        with btn_col2:
            if st.button("🧹 Xóa trắng ô nhập", use_container_width=True):
                st.session_state.code_input_text = ""
                st.rerun()

        # 3. Tùy chọn tải lên file mã nguồn (An toàn: Chỉ đọc văn bản, KHÔNG thực thi)
        uploaded_file = st.file_uploader(
            "📂 Tải file code (.cpp, .py, .java, .js, .txt):",
            type=["cpp", "c", "py", "java", "js", "txt"],
            help="Tải file từ máy tính để phân tích. Hệ thống chỉ đọc văn bản, tuyệt đối không chạy code.",
        )
        if uploaded_file is not None:
            try:
                uploaded_content = uploaded_file.read().decode("utf-8", errors="replace")
                if uploaded_content != st.session_state.code_input_text:
                    st.session_state.code_input_text = uploaded_content
                    st.success(f"Đã nạp file: `{uploaded_file.name}` ({len(uploaded_content)} ký tự)")
            except Exception as e:
                st.error(f"Lỗi khi đọc file: {e}")

        # 4. Khu vực nhập code (st.text_area)
        input_label = action_meta.get("input_label", "Khu vực nhập mã nguồn:")
        code_input = st.text_area(
            label=input_label,
            value=st.session_state.code_input_text,
            height=300,
            placeholder=action_meta.get("placeholder", "// Nhập code tại đây..."),
            help="Dán hoặc viết code cần phân tích tại đây.",
            key="input_area_widget",
        )
        # Đồng bộ ngược giá trị gõ tay vào session_state
        st.session_state.code_input_text = code_input

        # Đếm số dòng và số ký tự
        lines_count = len(code_input.splitlines()) if code_input else 0
        chars_count = len(code_input) if code_input else 0
        st.caption(f"📏 Thống kê đầu vào: `{lines_count}` dòng | `{chars_count}` ký tự")

        # Cảnh báo an toàn (Yêu cầu số 8)
        st.caption("🛡️ **An toàn tuyệt đối**: Hệ thống chỉ phân tích tĩnh qua văn bản, tuyệt đối KHÔNG thực thi mã nguồn.")

        # 5. Nút Analyze Code (Yêu cầu số 4)
        analyze_clicked = st.button(
            "🚀 Analyze Code",
            type="primary",
            use_container_width=True,
            help="Gửi mã nguồn, ngôn ngữ và chức năng đến AI để phân tích.",
        )

        if analyze_clicked:
            if not code_input.strip():
                st.warning("⚠️ Vui lòng nhập hoặc nạp mã nguồn trước khi bấm Analyze Code!")
            else:
                with st.spinner(f"🤖 Đang thực hiện tác vụ '{selected_action}' ({selected_language})..."):
                    # Gửi code + programming language + selected action đến AI (Yêu cầu số 5)
                    result = analyze_code(
                        code=code_input,
                        language=selected_language,
                        action=selected_action,
                        model_name=selected_model,
                        temperature=temperature,
                    )
                    st.session_state.analysis_result = result

                    # Đồng bộ sang current_code để dùng ở các nơi khác
                    if result.get("improved_code"):
                        st.session_state.current_code = result["improved_code"]
                        st.session_state.current_language = LANGUAGES.get(selected_language, "text")

                st.rerun()

    # -------------------------------------------------------------
    # 6.2. CỘT HIỂN THỊ KẾT QUẢ PHÂN TÍCH (Bên phải)
    # -------------------------------------------------------------
    with col_output:
        st.markdown("### 📊 Kết quả Phân tích từ AI")

        analysis_res = st.session_state.analysis_result

        if not analysis_res:
            # Giao diện chào mừng khi chưa chạy phân tích
            st.markdown(
                """
                <div class="section-card card-analysis" style="text-align: center; padding: 2.5rem 1.5rem;">
                    <div style="font-size: 3rem; margin-bottom: 0.8rem;">🚀</div>
                    <h3 style="color: #89b4fa; margin-bottom: 0.5rem;">Sẵn sàng Phân tích Code</h3>
                    <p style="color: #a6adc8; font-size: 0.95rem; line-height: 1.6;">
                        1. Chọn <strong>Ngôn ngữ lập trình</strong> (C++, Python, Java, JavaScript)<br>
                        2. Chọn <strong>Chức năng</strong> (Explain, Find Bugs, Fix, Optimize, Generate)<br>
                        3. Nhập code hoặc bấm <strong>"Nạp code mẫu"</strong><br>
                        4. Bấm <strong>"Analyze Code"</strong> để nhận kết quả 5 phần chi tiết!
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Thông báo trạng thái (Mock mode hoặc Live API)
            if analysis_res.get("is_mock"):
                st.info("💡 **Chế độ Demo/Mock**: Hiển thị kết quả mô phỏng cấu trúc 5 phần chuẩn sư phạm.")
            elif analysis_res.get("is_error"):
                st.error("⚠️ Phân tích gặp sự cố. Chi tiết xem bên dưới.")

            # Ngôn ngữ hiển thị cho code block
            display_lang = LANGUAGES.get(selected_language, "text")

            # ---------------------------------------------------------
            # HIỂN THỊ ĐỦ 5 MỤC THEO YÊU CẦU ĐỀ BÀI (Yêu cầu số 6)
            # ---------------------------------------------------------

            # Mục 1: Analysis (Phân tích tổng quan)
            with st.container():
                st.markdown(
                    """
                    <div class="card-title" style="color: #89b4fa;">
                        🔍 1. Analysis (Phân tích tổng quan)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(analysis_res.get("analysis", "Chưa có thông tin."))

            st.divider()

            # Mục 2: Problems (Vấn đề và lỗi phát hiện)
            with st.container():
                st.markdown(
                    """
                    <div class="card-title" style="color: #f38ba8;">
                        ⚠️ 2. Problems (Vấn đề & Lỗi phát hiện)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(analysis_res.get("problems", "Không phát hiện lỗi."))

            st.divider()

            # Mục 3: Explanation (Giải thích chi tiết)
            with st.container():
                st.markdown(
                    """
                    <div class="card-title" style="color: #cba6f7;">
                        📖 3. Explanation (Giải thích chi tiết)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(analysis_res.get("explanation", "Chưa có giải thích."))

            st.divider()

            # Mục 4: Suggested Fix (Đề xuất khắc phục)
            with st.container():
                st.markdown(
                    """
                    <div class="card-title" style="color: #a6e3a1;">
                        💡 4. Suggested Fix (Đề xuất khắc phục)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(analysis_res.get("suggested_fix", "Không có đề xuất."))

            st.divider()

            # Mục 5: Improved Code (Mã nguồn đã cải tiến) - NẰM TRONG CODE BLOCK (Yêu cầu số 7)
            with st.container():
                st.markdown(
                    """
                    <div class="card-title" style="color: #fab387;">
                        🚀 5. Improved Code (Mã nguồn cải tiến / Hoàn thiện)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                improved_code = analysis_res.get("improved_code", "")
                if improved_code:
                    # Hiển thị trong code block có syntax highlighting và line numbers
                    st.code(
                        improved_code,
                        language=display_lang,
                        line_numbers=True,
                    )

                    # Nút tải mã nguồn về máy
                    file_ext_map = {"cpp": "cpp", "python": "py", "java": "java", "javascript": "js"}
                    ext = file_ext_map.get(display_lang, "txt")
                    st.download_button(
                        label=f"💾 Tải xuống mã nguồn ({selected_language})",
                        data=improved_code,
                        file_name=f"improved_code.{ext}",
                        mime="text/plain",
                        use_container_width=True,
                    )
                else:
                    st.info("Không có mã nguồn bổ sung cho tác vụ này.")

            # Tùy chọn xem toàn bộ phản hồi Markdown gốc
            with st.expander("📄 Xem phản hồi Markdown đầy đủ từ AI"):
                st.markdown(analysis_res.get("raw_content", ""))


# ==============================================================================
# 7. TAB 2: CHATBOT LẬP TRÌNH (GIỮ NGUYÊN TÍNH NĂNG TỪ PHASE 2 & 3)
# ==============================================================================
with tab_chat:
    col_chat, col_side_code = st.columns([3, 2], gap="large")

    with col_chat:
        st.markdown("### 💬 Khung Chat Trực Tuyến")

        # Container cuộn cho lịch sử chat
        chat_container = st.container(height=480)
        with chat_container:
            for message in st.session_state.messages:
                role = message.get("role", "user")
                if role == "user":
                    with st.chat_message("user", avatar="🧑‍💻"):
                        st.markdown("**Bạn:**")
                        st.markdown(message.get("content", ""))
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f"**Trợ lý AI ({selected_model}):**")
                        st.markdown(message.get("content", ""))
                        if "code" in message and message["code"] and "```" not in message.get("content", ""):
                            st.code(message["code"], language=st.session_state.current_language)

        # Ô nhập chat_input
        user_input = st.chat_input("💬 Nhập câu hỏi lập trình cần AI giải đáp...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("🤖 Trợ lý AI đang suy nghĩ..."):
                ai_response = send_message(
                    prompt=user_input,
                    chat_history=st.session_state.messages[:-1],
                    model_name=selected_model,
                    temperature=temperature,
                    programming_language=st.session_state.selected_language,
                )

            st.session_state.messages.append(ai_response)
            if ai_response.get("code"):
                st.session_state.current_code = ai_response["code"]
                st.session_state.current_language = LANGUAGES.get(st.session_state.selected_language, "text")

            st.rerun()

    with col_side_code:
        st.markdown("### 💻 Bảng Code Chi Tiết")
        if st.session_state.current_code:
            st.code(
                st.session_state.current_code,
                language=st.session_state.current_language,
                line_numbers=True,
            )
            st.info("💡 Bấm biểu tượng 📋 ở góc trên bên phải khung code để sao chép nhanh!")
        else:
            st.info("Chưa có code nào. Code giải pháp sẽ tự động xuất hiện tại đây khi bạn trò chuyện.")

        total_msgs = len(st.session_state.messages)
        user_msgs = sum(1 for m in st.session_state.messages if m.get("role") == "user")
        ai_msgs = sum(1 for m in st.session_state.messages if m.get("role") == "assistant")
        st.markdown("---")
        st.caption(f"📊 **Thống kê:** Tổng tin nhắn: `{total_msgs}` | User: `{user_msgs}` | AI: `{ai_msgs}`")

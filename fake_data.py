# fake_data.py - Dữ liệu giả lập để kiểm tra tính năng Chat Box (Phase 2)
# =======================================================================
# File này chứa các hội thoại mẫu và hàm tạo phản hồi giả lập (Mock AI).
# Ở Phase sau sẽ kết nối API thực tế (Groq API).

INITIAL_CONVERSATION = [
    {
        "role": "assistant",
        "content": (
            "Xin chào! 👋 Tôi là **AI Coding Assistant** (Mock Mode - Phase 2).\n\n"
            "Tôi đã sẵn sàng hỗ trợ bạn kiểm tra luồng Chat Box!\n"
            "Hãy thử nhập các câu hỏi mẫu như:\n"
            "- *Hàm tính giai thừa*\n"
            "- *Vòng lặp for*\n"
            "- *Kiểm tra số nguyên tố*\n"
            "- *Tạo class sinh viên*\n"
            "- *Tính tổng hai số*\n"
            "- *Đọc và ghi file*"
        ),
        "code": "# Chào mừng bạn đến với Phase 2: Chat Box!\ndef chao_mung(ten='Developer'):\n    return f'Xin chao {ten}! Chuc ban hoc code vui ve.'\n\nprint(chao_mung())",
    },
]

# Backward compatibility alias
FAKE_CONVERSATIONS = INITIAL_CONVERSATION


MOCK_TOPICS = {
    "giai_thua": {
        "keywords": ["giai thừa", "giai thua", "factorial"],
        "content": "📝 **[Mock AI]** Đây là cách viết **hàm tính giai thừa** bằng phương pháp đệ quy trong Python:",
        "code": (
            "def giai_thua(n):\n"
            '    """Tính giai thừa của số nguyên dương n bằng đệ quy."""\n'
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * giai_thua(n - 1)\n"
            "\n"
            "# Kiểm tra hàm\n"
            "n = 5\n"
            'print(f"{n}! = {giai_thua(n)}")  # Kết quả: 5! = 120\n'
        ),
    },
    "vong_lap": {
        "keywords": ["vòng lặp", "vong lap", "loop", "for", "while"],
        "content": "🔄 **[Mock AI]** Dưới đây là ví dụ minh họa **vòng lặp `for` và `enumerate`** trong Python:",
        "code": (
            'frameworks = ["Streamlit", "FastAPI", "React", "Vue"]\n'
            "\n"
            "# Duyệt qua danh sách kèm số thứ tự\n"
            "for index, item in enumerate(frameworks, start=1):\n"
            '    print(f"{index}. Công nghệ: {item}")\n'
        ),
    },
    "so_nguyen_to": {
        "keywords": ["nguyên tố", "nguyen to", "prime"],
        "content": "🧮 **[Mock AI]** Thuật toán tối ưu để **kiểm tra số nguyên tố**:",
        "code": (
            "def la_so_nguyen_to(n):\n"
            '    """Kiểm tra n có phải số nguyên tố hay không."""\n'
            "    if n < 2:\n"
            "        return False\n"
            "    for i in range(2, int(n**0.5) + 1):\n"
            "        if n % i == 0:\n"
            "            return False\n"
            "    return True\n"
            "\n"
            "# In các số nguyên tố nhỏ hơn 30\n"
            "primes = [x for x in range(30) if la_so_nguyen_to(x)]\n"
            'print("Các số nguyên tố < 30:", primes)\n'
        ),
    },
    "class_oop": {
        "keywords": ["class", "lớp", "lop", "oop", "đối tượng", "doi tuong"],
        "content": "🎨 **[Mock AI]** Hướng dẫn tạo **Class & Object (Lập trình hướng đối tượng)**:",
        "code": (
            "class SinhVien:\n"
            "    def __init__(self, ho_ten: str, ma_sv: str):\n"
            "        self.ho_ten = ho_ten\n"
            "        self.ma_sv = ma_sv\n"
            "        self.diem_so = []\n"
            "\n"
            "    def them_diem(self, diem: float):\n"
            "        self.diem_so.append(diem)\n"
            "\n"
            "    def diem_trung_binh(self) -> float:\n"
            "        return sum(self.diem_so) / len(self.diem_so) if self.diem_so else 0.0\n"
            "\n"
            'sv = SinhVien("Nguyễn Văn An", "B21DCCN001")\n'
            "sv.them_diem(8.5)\n"
            "sv.them_diem(9.0)\n"
            'print(f"Sinh viên: {sv.ho_ten} - ĐTB: {sv.diem_trung_binh():.2f}")\n'
        ),
    },
    "tinh_tong": {
        "keywords": ["tổng", "tong", "sum", "cộng", "cong"],
        "content": "➕ **[Mock AI]** Đây là hàm **tính tổng danh sách số** sử dụng Python:",
        "code": (
            "def tinh_tong(*args):\n"
            '    """Tính tổng các tham số truyền vào."""\n'
            "    return sum(args)\n"
            "\n"
            "ket_qua = tinh_tong(10, 20, 30, 40)\n"
            'print(f"Tổng các số là: {ket_qua}")  # Kết quả: 100\n'
        ),
    },
    "file_io": {
        "keywords": ["file", "tệp", "tep", "đọc", "doc", "ghi"],
        "content": "📁 **[Mock AI]** Mẫu code **đọc và ghi file an toàn** bằng context manager `with`:",
        "code": (
            "# Ghi dữ liệu vào file\n"
            'with open("sample.txt", "w", encoding="utf-8") as f:\n'
            '    f.write("Dòng 1: Trợ lý AI Coding Assistant\\n")\n'
            '    f.write("Dòng 2: Hoàn thành Phase 2 Chat Box!\\n")\n'
            "\n"
            "# Đọc dữ liệu từ file\n"
            'with open("sample.txt", "r", encoding="utf-8") as f:\n'
            "    content = f.read()\n"
            'print("Nội dung file:\\n" + content)\n'
        ),
    },
}


def generate_fake_response(user_input: str) -> dict:
    """
    Tạo phản hồi giả lập (Mock AI) tương ứng với nội dung câu hỏi của người dùng.
    Dùng để kiểm thử toàn diện luồng hội thoại mà không cần gọi AI API thật.
    """
    user_lower = user_input.lower().strip()

    # Tìm chủ đề phù hợp dựa vào từ khóa
    for topic_key, topic_data in MOCK_TOPICS.items():
        if any(keyword in user_lower for keyword in topic_data["keywords"]):
            return {
                "role": "assistant",
                "content": topic_data["content"],
                "code": topic_data["code"],
            }

    # Phản hồi mặc định nếu không khớp từ khóa cụ thể
    sample_code = (
        f"# Mock AI Response cho câu hỏi: '{user_input}'\n"
        "def xu_ly_yeu_cau(prompt: str):\n"
        "    print(f'Đang xử lý: {prompt}')\n"
        "    return 'Hoàn thành thành công!'\n"
        "\n"
        f"ket_qua = xu_ly_yeu_cau('{user_input}')\n"
        "print(ket_qua)\n"
    )

    return {
        "role": "assistant",
        "content": (
            f"💡 **[Mock AI]** Cảm ơn bạn đã hỏi về: *\"{user_input}\"*.\n\n"
            "Hệ thống đã nhận yêu cầu và tạo một đoạn mã giải pháp mẫu bên dưới. "
            "Bạn có thể sao chép đoạn code này từ Bảng Code bên phải hoặc ngay trong ô chat!"
        ),
        "code": sample_code,
    }


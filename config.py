# config.py - File cấu hình cho ứng dụng AI Coding Assistant (Phase 4)
# ==============================================================================
# Quản lý tập trung các hằng số, danh sách ngôn ngữ lập trình, chức năng và code mẫu.
# ==============================================================================

# --- Thông tin ứng dụng ---
APP_TITLE = "🤖 AI Coding Assistant"
APP_DESCRIPTION = "Trợ lý lập trình thông minh: Giải thích, Tìm lỗi, Sửa lỗi, Tối ưu và Sinh code"

# --- Danh sách Model AI (Groq) ---
AI_MODELS = [
    "GPT-OSS 20B",       # Model OpenAI OSS trên Groq (openai/gpt-oss-20b)
    "Llama 3.3 70B",     # Model Llama 3.3 70B mạnh nhất (llama-3.3-70b-versatile)
    "Llama 3.1 8B",      # Model Llama 3.1 8B siêu nhanh (llama-3.1-8b-instant)
    "Mixtral 8x7B",      # Model Mixtral 8x7B (mixtral-8x7b-32768)
    "Gemma 2 9B",        # Model Gemma 2 9B (gemma2-9b-it)
]

# --- 1. Danh sách ngôn ngữ lập trình hỗ trợ (Phase 4) ---
# Key: Tên hiển thị trên giao diện (C++, Python, Java, JavaScript)
# Value: Mã ngôn ngữ cho syntax highlighting (Streamlit st.code / markdown)
LANGUAGES = {
    "C++": "cpp",
    "Python": "python",
    "Java": "java",
    "JavaScript": "javascript",
}

# Danh sách tên ngôn ngữ
SUPPORTED_LANGUAGES = list(LANGUAGES.keys())

# --- 2. Danh sách chức năng AI Coding Assistant (Phase 4) ---
CODING_ACTIONS = [
    "Explain Code",
    "Find Bugs",
    "Fix Code",
    "Optimize Code",
    "Generate Code",
]

# Chi tiết và mô tả cho từng chức năng
ACTION_DETAILS = {
    "Explain Code": {
        "icon": "📖",
        "title": "Giải thích Code",
        "description": "Phân tích chi tiết cấu trúc, luồng thực thi và giải thích từng bước cho sinh viên.",
        "input_label": "Dán hoặc viết mã nguồn cần giải thích:",
        "placeholder": "// Nhập hoặc dán mã nguồn cần giải thích tại đây...",
    },
    "Find Bugs": {
        "icon": "🐛",
        "title": "Tìm lỗi Code",
        "description": "Phát hiện lỗi cú pháp, lỗi logic, rủi ro runtime, tràn bộ nhớ hoặc rò rỉ tài nguyên.",
        "input_label": "Dán hoặc viết mã nguồn cần tìm lỗi:",
        "placeholder": "// Nhập hoặc dán mã nguồn cần kiểm tra lỗi tại đây...",
    },
    "Fix Code": {
        "icon": "🔧",
        "title": "Sửa lỗi Code",
        "description": "Sửa toàn bộ các lỗi tìm thấy và cung cấp mã nguồn hoàn chỉnh đã được khắc phục.",
        "input_label": "Dán hoặc viết mã nguồn cần sửa lỗi:",
        "placeholder": "// Nhập hoặc dán mã nguồn cần sửa tại đây...",
    },
    "Optimize Code": {
        "icon": "⚡",
        "title": "Tối ưu hóa Code",
        "description": "Đánh giá độ phức tạp thuật toán (Big O), tối ưu hóa thời gian chạy và bộ nhớ.",
        "input_label": "Dán hoặc viết mã nguồn cần tối ưu:",
        "placeholder": "// Nhập hoặc dán mã nguồn cần tối ưu hóa tại đây...",
    },
    "Generate Code": {
        "icon": "✨",
        "title": "Sinh mã nguồn",
        "description": "Tạo mã nguồn hoàn chỉnh theo mô tả yêu cầu bài toán hoặc thuật toán của bạn.",
        "input_label": "Nhập mô tả yêu cầu bài toán cần sinh code:",
        "placeholder": "Ví dụ: Viết thuật toán tìm kiếm nhị phân có xử lý ngoại lệ và hàm main kiểm thử...",
    },
}

# --- 3. Kho mã nguồn mẫu (Sample Code) cho từng ngôn ngữ & chức năng ---
SAMPLE_CODES = {
    "C++": {
        "Explain Code": (
            "#include <iostream>\n"
            "#include <vector>\n\n"
            "// Hàm tìm kiếm nhị phân trên mảng đã sắp xếp\n"
            "int binarySearch(const std::vector<int>& arr, int target) {\n"
            "    int left = 0, right = arr.size() - 1;\n"
            "    while (left <= right) {\n"
            "        int mid = left + (right - left) / 2;\n"
            "        if (arr[mid] == target) return mid;\n"
            "        if (arr[mid] < target) left = mid + 1;\n"
            "        else right = mid - 1;\n"
            "    }\n"
            "    return -1;\n"
            "}\n"
        ),
        "Find Bugs": (
            "#include <iostream>\n\n"
            "int main() {\n"
            "    // Lỗi 1: Giải tham chiếu con trỏ null\n"
            "    int* ptr = nullptr;\n"
            "    std::cout << *ptr << std::endl;\n\n"
            "    // Lỗi 2: Truy cập phần tử ngoài biên mảng\n"
            "    int arr[5] = {1, 2, 3, 4, 5};\n"
            "    std::cout << arr[10] << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        "Fix Code": (
            "#include <iostream>\n\n"
            "// Lỗi: Chưa xử lý trường hợp chia cho 0\n"
            "double divide(double a, double b) {\n"
            "    return a / b;\n"
            "}\n\n"
            "int main() {\n"
            "    std::cout << divide(10.0, 0.0) << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        "Optimize Code": (
            "#include <iostream>\n"
            "#include <vector>\n\n"
            "// Thuật toán O(n^2) kiểm tra cặp số có tổng bằng target\n"
            "bool hasPairWithSum(const std::vector<int>& arr, int target) {\n"
            "    for (size_t i = 0; i < arr.size(); ++i) {\n"
            "        for (size_t j = i + 1; j < arr.size(); ++j) {\n"
            "            if (arr[i] + arr[j] == target) return true;\n"
            "        }\n"
            "    }\n"
            "    return false;\n"
            "}\n"
        ),
        "Generate Code": (
            "Viết thuật toán QuickSort (sắp xếp nhanh) cho mảng số nguyên trong C++ "
            "kèm hàm main minh họa và giải thích độ phức tạp Big O."
        ),
    },
    "Python": {
        "Explain Code": (
            "def quicksort(arr):\n"
            '    """Sắp xếp danh sách số theo thuật toán QuickSort."""\n'
            "    if len(arr) <= 1:\n"
            "        return arr\n"
            "    pivot = arr[len(arr) // 2]\n"
            "    left = [x for x in arr if x < pivot]\n"
            "    middle = [x for x in arr if x == pivot]\n"
            "    right = [x for x in arr if x > pivot]\n"
            "    return quicksort(left) + middle + quicksort(right)\n\n"
            "# Kiểm thử\n"
            "numbers = [3, 6, 8, 10, 1, 2, 1]\n"
            "print('Sorted:', quicksort(numbers))\n"
        ),
        "Find Bugs": (
            "def tinh_trung_binh(danh_sach):\n"
            "    # Lỗi tiềm ẩn: danh sách rỗng gây ZeroDivisionError\n"
            "    tong = sum(danh_sach)\n"
            "    return tong / len(danh_sach)\n\n"
            "# Gọi hàm với danh sách rỗng\n"
            "diem_so = []\n"
            "print('Diem TB:', tinh_trung_binh(diem_so))\n"
        ),
        "Fix Code": (
            "def doc_va_in_file(ten_file):\n"
            "    # Lỗi: Không dùng context manager 'with open' và không bắt FileNotFoundError\n"
            "    f = open(ten_file, 'r')\n"
            "    noi_dung = f.read()\n"
            "    return noi_dung\n\n"
            "print(doc_va_in_file('khong_ton_tai.txt'))\n"
        ),
        "Optimize Code": (
            "# Tìm phần tử chung giữa 2 danh sách với độ phức tạp O(n * m)\n"
            "def tim_phan_tu_chung(list_a, list_b):\n"
            "    chung = []\n"
            "    for a in list_a:\n"
            "        for b in list_b:\n"
            "            if a == b and a not in chung:\n"
            "                chung.append(a)\n"
            "    return chung\n"
        ),
        "Generate Code": (
            "Viết hàm Python đọc file JSON danh sách sinh viên, lọc sinh viên có điểm >= 8.0 "
            "và lưu kết quả ra file CSV với xử lý ngoại lệ đầy đủ."
        ),
    },
    "Java": {
        "Explain Code": (
            "public class Singleton {\n"
            "    // Khởi tạo Singleton theo phương pháp Double-Checked Locking\n"
            "    private static volatile Singleton instance;\n"
            "    private Singleton() {}\n\n"
            "    public static Singleton getInstance() {\n"
            "        if (instance == null) {\n"
            "            synchronized (Singleton.class) {\n"
            "                if (instance == null) {\n"
            "                    instance = new Singleton();\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "        return instance;\n"
            "    }\n"
            "}\n"
        ),
        "Find Bugs": (
            "public class UserService {\n"
            "    public static void main(String[] args) {\n"
            "        String username = null;\n"
            "        // Lỗi: NullPointerException khi gọi equals trên biến null\n"
            "        if (username.equals(\"admin\")) {\n"
            "            System.out.println(\"Chào mừng Admin!\");\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "Fix Code": (
            "public class LoopBug {\n"
            "    public static void printArray(int[] nums) {\n"
            "        // Lỗi: ArrayIndexOutOfBoundsException vì điều kiện i <= nums.length\n"
            "        for (int i = 0; i <= nums.length; i++) {\n"
            "            System.out.println(nums[i]);\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        "Optimize Code": (
            "// Nối chuỗi bằng toán tử + trong vòng lặp gây tiêu hao bộ nhớ\n"
            "public class StringReport {\n"
            "    public static String createReport(int count) {\n"
            "        String report = \"\";\n"
            "        for (int i = 0; i < count; i++) {\n"
            "            report += \"Mục \" + i + \": Thành công\\n\";\n"
            "        }\n"
            "        return report;\n"
            "    }\n"
            "}\n"
        ),
        "Generate Code": (
            "Tạo một lớp SinhVien trong Java gồm mã SV, họ tên, điểm trung bình "
            "với đầy đủ Constructor, Getter/Setter và phương thức xếp loại học lực."
        ),
    },
    "JavaScript": {
        "Explain Code": (
            "// Hàm Debounce giới hạn tần suất gọi hàm (ví dụ ô tìm kiếm gợi ý)\n"
            "function debounce(func, delay = 300) {\n"
            "    let timer;\n"
            "    return function (...args) {\n"
            "        clearTimeout(timer);\n"
            "        timer = setTimeout(() => {\n"
            "            func.apply(this, args);\n"
            "        }, delay);\n"
            "    };\n"
            "}\n"
        ),
        "Find Bugs": (
            "// Lỗi Closure kinh điển với từ khóa 'var' trong vòng lặp bất đồng bộ\n"
            "for (var i = 0; i < 3; i++) {\n"
            "    setTimeout(function() {\n"
            "        console.log(i); // In ra 3 ba lần thay vì 0, 1, 2\n"
            "    }, 100);\n"
            "}\n"
        ),
        "Fix Code": (
            "// Lỗi: Chưa bắt lỗi (try/catch) cho API call bất đồng bộ\n"
            "async function fetchUserData(userId) {\n"
            "    const res = await fetch(`https://api.example.com/users/${userId}`);\n"
            "    const data = await res.json();\n"
            "    return data.profile.name;\n"
            "}\n"
        ),
        "Optimize Code": (
            "// Tìm kiếm phần tử trùng lặp với độ phức tạp O(n^2)\n"
            "function hasDuplicateItems(items) {\n"
            "    for (let i = 0; i < items.length; i++) {\n"
            "        for (let j = i + 1; j < items.length; j++) {\n"
            "            if (items[i] === items[j]) return true;\n"
            "        }\n"
            "    }\n"
            "    return false;\n"
            "}\n"
        ),
        "Generate Code": (
            "Viết hàm JavaScript tính toán phân trang (pagination) nhận vào: "
            "danh sách mảng, số trang hiện tại (page) và số phần tử mỗi trang (pageSize)."
        ),
    },
}

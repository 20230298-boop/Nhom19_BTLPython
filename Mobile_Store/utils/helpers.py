"""
helpers.py
─────────────────────────────────────────
Các hàm tiện ích dùng chung trong toàn bộ ứng dụng.
"""

import re
import hashlib
from datetime import datetime



def check_dependencies():
    """In trạng thái các thư viện optional ra console."""
    libs = {
        "matplotlib": "pip install matplotlib",
        "PIL":        "pip install pillow",
        "reportlab":  "pip install reportlab",
        "openpyxl":   "pip install openpyxl",
    }
    for lib, install_cmd in libs.items():
        try:
            __import__(lib)
            print(f"  ✅ {lib}")
        except ImportError:
            print(f"  ❌ {lib}  →  {install_cmd}")


def is_available(lib_name: str) -> bool:
    """Trả về True nếu thư viện có thể import được."""
    try:
        __import__(lib_name)
        return True
    except ImportError:
        return False



def format_currency(amount) -> str:
    """Định dạng số tiền Việt Nam: 1.500.000 ₫"""
    if amount is None:
        return "0 ₫"
    return f"{int(amount):,} ₫".replace(",", ".")


def format_number(n) -> str:
    """Định dạng số nguyên có dấu phân cách nghìn."""
    if n is None:
        return "0"
    return f"{int(n):,}".replace(",", ".")


def parse_currency(s) -> float:
    """Chuyển chuỗi tiền tệ (có thể chứa ký tự) về float."""
    try:
        return float(re.sub(r"[^\d.]", "", str(s)))
    except (ValueError, TypeError):
        return 0.0


def generate_code(prefix: str, last_id: int) -> str:
    """Sinh mã tự động: KH000001, HD000042, ..."""
    return f"{prefix}{str(last_id).zfill(6)}"



def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed



def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def first_day_of_month() -> str:
    return datetime.now().strftime("%Y-%m-01")


def greeting() -> str:
    h = datetime.now().hour
    if h < 12:
        return "Chào buổi sáng"
    elif h < 18:
        return "Chào buổi chiều"
    return "Chào buổi tối"

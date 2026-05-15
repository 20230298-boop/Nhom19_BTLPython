"""
╔══════════════════════════════════════════════════════════════════╗
║       PHẦN MỀM QUẢN LÝ CỬA HÀNG THIẾT BỊ DI ĐỘNG               ║
║       Mobile Store Management System v1.0                        ║
╚══════════════════════════════════════════════════════════════════╝

Cài đặt thư viện:
    pip install customtkinter pillow reportlab openpyxl matplotlib

Chạy:
    python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from ui.login_window import LoginWindow
from utils.constants import APP_VERSION, DB_PATH
from utils.helpers import check_dependencies


def main():
    print("=" * 60)
    print(f"  MOBILE STORE PRO v{APP_VERSION} - Khởi động hệ thống...")
    print("=" * 60)
    check_dependencies()

    db = DatabaseManager(DB_PATH)
    print("  ✅ Database khởi tạo thành công!")
    print("  🚀 Đang mở cửa sổ đăng nhập...")
    print("=" * 60)

    app = LoginWindow(db)
    app.run()


if __name__ == "__main__":
    main()

# 📱 Mobile Store Pro — Phần mềm quản lý cửa hàng thiết bị di động

> Hệ thống quản lý cửa hàng điện thoại di động chuyên nghiệp  
> Giao diện dark-mode hiện đại · SQLite database · Python / CustomTkinter

---

## 🗂 Cấu trúc thư mục

```
Mobile_Store/
│
├── main.py                         # Điểm khởi động ứng dụng
├── requirements.txt                # Danh sách thư viện
├── README.md
│
├── database/
│   ├── __init__.py
│   └── db_manager.py               # Khởi tạo schema, CRUD, seed data
│
├── utils/
│   ├── __init__.py
│   ├── constants.py                # Màu sắc, font, hằng số toàn cục
│   └── helpers.py                  # Hàm tiện ích (format, hash, ...)
│
└── ui/
    ├── __init__.py
    ├── login_window.py             # Cửa sổ đăng nhập
    ├── main_window.py              # Cửa sổ chính + sidebar điều hướng
    │
    ├── widgets/
    │   ├── __init__.py
    │   └── base_widgets.py         # StyledButton, Card, StatCard, StyledTreeview
    │
    ├── pages/                      # Mỗi trang = 1 file
    │   ├── __init__.py
    │   ├── dashboard.py            # 🏠 Tổng quan & thống kê
    │   ├── pos.py                  # 🛒 Bán hàng (Point of Sale)
    │   ├── invoices.py             # 🧾 Quản lý hóa đơn
    │   ├── products.py             # 📦 Quản lý sản phẩm
    │   ├── inventory.py            # 📥 Nhập hàng
    │   ├── customers.py            # 👥 Quản lý khách hàng
    │   ├── warranties.py           # 🔧 Quản lý bảo hành
    │   ├── reports.py              # 📊 Báo cáo & thống kê
    │   ├── suppliers.py            # 🏭 Nhà cung cấp
    │   ├── categories.py           # 🗂  Danh mục sản phẩm
    │   ├── users.py                # 👤 Quản lý người dùng (admin)
    │   └── logs.py                 # 📋 Nhật ký hoạt động (admin)
    │
    └── dialogs/                    # Cửa sổ popup CRUD
        ├── __init__.py
        ├── product_dialog.py       # Thêm / sửa sản phẩm
        ├── customer_dialog.py      # Thêm / sửa khách hàng
        ├── customer_select.py      # Chọn khách hàng khi bán
        ├── customer_history.py     # Lịch sử mua hàng
        ├── invoice_detail.py       # Chi tiết hóa đơn
        ├── purchase_dialog.py      # Phiếu nhập hàng
        ├── warranty_dialog.py      # Phiếu bảo hành
        ├── supplier_dialog.py      # Thêm / sửa nhà cung cấp
        ├── category_dialog.py      # Thêm / sửa danh mục
        └── user_dialog.py          # Thêm / sửa người dùng
```

---

## 🚀 Hướng dẫn cài đặt & chạy

### 1. Cài thư viện

```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:

```bash
pip install customtkinter matplotlib pillow openpyxl reportlab
```

### 2. Chạy chương trình

```bash
python main.py
```

---

## 🔑 Tài khoản mặc định

| Tài khoản  | Mật khẩu  | Vai trò          |
|------------|-----------|------------------|
| `admin`    | `admin123`| 👑 Quản trị viên |
| `nhanvien` | `nv123`   | 👤 Nhân viên     |

---

## ✨ Chức năng chính

| Module           | Mô tả                                              |
|------------------|----------------------------------------------------|
| 🏠 Dashboard     | Thống kê, biểu đồ doanh thu, hàng sắp hết         |
| 🛒 POS           | Bán hàng nhanh, giỏ hàng, in/xuất hóa đơn        |
| 🧾 Hóa đơn       | Danh sách, lọc ngày, xem chi tiết, xóa            |
| 📦 Sản phẩm      | CRUD sản phẩm, lọc danh mục, xuất Excel           |
| 📥 Nhập hàng     | Tạo phiếu nhập, cảnh báo tồn kho thấp            |
| 👥 Khách hàng    | CRUD, tích điểm, phân loại VIP, lịch sử mua       |
| 🔧 Bảo hành      | Tiếp nhận, cập nhật trạng thái, theo dõi KTV      |
| 📊 Báo cáo       | Doanh thu, sản phẩm, khách hàng, lợi nhuận       |
| 🏭 Nhà cung cấp  | Quản lý danh sách, thông tin liên hệ              |
| 🗂 Danh mục      | Phân loại sản phẩm linh hoạt                      |
| 👤 Người dùng    | Phân quyền admin / nhân viên, khóa tài khoản     |
| 📋 Nhật ký       | Ghi lại mọi thao tác, lọc theo module            |

---

## 🗃 Database

File database SQLite tự động tạo tại thư mục gốc: `mobile_store.db`

Không cần cài đặt server database. Dữ liệu mẫu được seed tự động khi chạy lần đầu.

---

## 🛠 Yêu cầu hệ thống

- Python 3.10+
- Windows / macOS / Linux
- Độ phân giải màn hình tối thiểu: 1280 × 720

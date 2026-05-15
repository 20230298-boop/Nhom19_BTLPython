"""
db_manager.py
─────────────────────────────────────────
Quản lý kết nối SQLite, khởi tạo schema và seed dữ liệu mẫu.
"""

import sqlite3
from utils.helpers import hash_password


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.initialize()

    # ── Kết nối ─────────────────────────────────────────────────

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    # ── Khởi tạo schema ─────────────────────────────────────────

    def initialize(self):
        conn = self.get_connection()
        c = conn.cursor()
        self._create_tables(c)
        conn.commit()
        self._seed_default_data(conn, c)
        conn.close()

    def _create_tables(self, c):
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            full_name   TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'staff',
            email       TEXT,
            phone       TEXT,
            avatar      TEXT,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            last_login  TEXT
        );

        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    UNIQUE NOT NULL,
            description TEXT,
            icon        TEXT    DEFAULT '📱',
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS suppliers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            contact     TEXT,
            phone       TEXT,
            email       TEXT,
            address     TEXT,
            tax_code    TEXT,
            note        TEXT,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS products (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            code            TEXT    UNIQUE NOT NULL,
            name            TEXT    NOT NULL,
            category_id     INTEGER REFERENCES categories(id),
            supplier_id     INTEGER REFERENCES suppliers(id),
            brand           TEXT,
            model           TEXT,
            description     TEXT,
            import_price    REAL    DEFAULT 0,
            selling_price   REAL    DEFAULT 0,
            quantity        INTEGER DEFAULT 0,
            min_quantity    INTEGER DEFAULT 5,
            warranty_months INTEGER DEFAULT 12,
            color           TEXT,
            storage         TEXT,
            ram             TEXT,
            image_path      TEXT,
            is_active       INTEGER DEFAULT 1,
            created_at      TEXT    DEFAULT (datetime('now','localtime')),
            updated_at      TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS customers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            code          TEXT    UNIQUE NOT NULL,
            full_name     TEXT    NOT NULL,
            phone         TEXT,
            email         TEXT,
            address       TEXT,
            birthday      TEXT,
            gender        TEXT    DEFAULT 'Nam',
            id_card       TEXT,
            loyalty_pts   INTEGER DEFAULT 0,
            total_spent   REAL    DEFAULT 0,
            customer_type TEXT    DEFAULT 'Thường',
            note          TEXT,
            is_active     INTEGER DEFAULT 1,
            created_at    TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no      TEXT    UNIQUE NOT NULL,
            customer_id     INTEGER REFERENCES customers(id),
            user_id         INTEGER REFERENCES users(id),
            total_amount    REAL    DEFAULT 0,
            discount        REAL    DEFAULT 0,
            discount_type   TEXT    DEFAULT 'amount',
            final_amount    REAL    DEFAULT 0,
            paid_amount     REAL    DEFAULT 0,
            payment_method  TEXT    DEFAULT 'Tiền mặt',
            payment_status  TEXT    DEFAULT 'Đã thanh toán',
            note            TEXT,
            created_at      TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS invoice_details (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id  INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
            product_id  INTEGER NOT NULL REFERENCES products(id),
            quantity    INTEGER NOT NULL DEFAULT 1,
            unit_price  REAL    NOT NULL,
            discount    REAL    DEFAULT 0,
            subtotal    REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS purchase_orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no     TEXT    UNIQUE NOT NULL,
            supplier_id  INTEGER REFERENCES suppliers(id),
            user_id      INTEGER REFERENCES users(id),
            total_amount REAL    DEFAULT 0,
            status       TEXT    DEFAULT 'Đã nhập',
            note         TEXT,
            created_at   TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS purchase_details (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
            product_id  INTEGER NOT NULL REFERENCES products(id),
            quantity    INTEGER NOT NULL DEFAULT 1,
            unit_price  REAL    NOT NULL,
            subtotal    REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS warranties (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            warranty_no     TEXT    UNIQUE NOT NULL,
            customer_id     INTEGER REFERENCES customers(id),
            product_id      INTEGER REFERENCES products(id),
            invoice_id      INTEGER REFERENCES invoices(id),
            issue_desc      TEXT,
            status          TEXT    DEFAULT 'Đang xử lý',
            technician      TEXT,
            repair_cost     REAL    DEFAULT 0,
            received_date   TEXT    DEFAULT (datetime('now','localtime')),
            completed_date  TEXT,
            note            TEXT,
            created_at      TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER REFERENCES users(id),
            action      TEXT    NOT NULL,
            module      TEXT,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT    NOT NULL,
            category    TEXT,
            amount      REAL    NOT NULL,
            description TEXT,
            user_id     INTEGER REFERENCES users(id),
            ref_id      TEXT,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );
        """)

    # ── Seed dữ liệu mặc định ───────────────────────────────────

    def _seed_default_data(self, conn, c):
        # Tài khoản mặc định
        c.execute("SELECT id FROM users WHERE username='admin'")
        if c.fetchone():
            return  # Đã seed rồi

        c.executemany(
            "INSERT INTO users (username,password,full_name,role,email,phone) VALUES (?,?,?,?,?,?)",
            [
                ("admin",    hash_password("admin123"), "Quản trị viên", "admin",
                 "admin@mobilestore.vn",    "0901234567"),
                ("nhanvien", hash_password("nv123"),    "Nguyễn Văn A",  "staff",
                 "nhanvien@mobilestore.vn", "0987654321"),
            ]
        )

        # Danh mục
        c.executemany(
            "INSERT OR IGNORE INTO categories (name,description,icon) VALUES (?,?,?)",
            [
                ("Điện thoại",        "Các loại điện thoại di động",   "📱"),
                ("Máy tính bảng",     "Tablet, iPad",                  "💻"),
                ("Phụ kiện",          "Ốp lưng, tai nghe, sạc",        "🎧"),
                ("Đồng hồ thông minh","Smartwatch, fitness band",       "⌚"),
                ("Laptop",            "Máy tính xách tay",             "💻"),
                ("Thiết bị âm thanh", "Loa, tai nghe",                 "🔊"),
            ]
        )

        # Nhà cung cấp
        c.executemany(
            "INSERT OR IGNORE INTO suppliers (name,contact,phone,email,address,tax_code) VALUES (?,?,?,?,?,?)",
            [
                ("Apple Vietnam",   "Lê Văn B",    "0911222333", "apple@vn.com",   "TP.HCM",  "MST001"),
                ("Samsung Vietnam", "Trần Thị C",  "0922333444", "samsung@vn.com", "Hà Nội",  "MST002"),
                ("Xiaomi Vietnam",  "Phạm Văn D",  "0933444555", "xiaomi@vn.com",  "TP.HCM",  "MST003"),
                ("OPPO Vietnam",    "Nguyễn Thị E","0944555666", "oppo@vn.com",    "Đà Nẵng", "MST004"),
            ]
        )
        conn.commit()

        # Lấy id danh mục & nhà cung cấp vừa tạo
        def cid(name):
            r = c.execute("SELECT id FROM categories WHERE name=?", (name,)).fetchone()
            return r[0] if r else 1

        def sid(name):
            r = c.execute("SELECT id FROM suppliers WHERE name=?", (name,)).fetchone()
            return r[0] if r else 1

        products = [
            ("SP001","iPhone 15 Pro Max",  cid("Điện thoại"),    sid("Apple Vietnam"),   "Apple","A3293","Flagship Apple 2023",28_000_000,32_000_000,15,3,12,"Titan Đen","256GB","8GB"),
            ("SP002","iPhone 15",          cid("Điện thoại"),    sid("Apple Vietnam"),   "Apple","A3092","iPhone 15 tiêu chuẩn",20_000_000,23_000_000,20,3,12,"Hồng","128GB","6GB"),
            ("SP003","Samsung S24 Ultra",  cid("Điện thoại"),    sid("Samsung Vietnam"), "Samsung","SM-S928B","Flagship Samsung",27_000_000,31_000_000,12,3,12,"Titan Xám","512GB","12GB"),
            ("SP004","Samsung Galaxy A55", cid("Điện thoại"),    sid("Samsung Vietnam"), "Samsung","SM-A556B","Tầm trung cao cấp",8_500_000,10_500_000,30,5,12,"Xanh","256GB","8GB"),
            ("SP005","Xiaomi 14 Ultra",    cid("Điện thoại"),    sid("Xiaomi Vietnam"),  "Xiaomi","23116PN5BC","Flagship Xiaomi",20_000_000,24_000_000,10,3,12,"Trắng","512GB","16GB"),
            ("SP006","OPPO Find X7",       cid("Điện thoại"),    sid("OPPO Vietnam"),    "OPPO","CPH2599","OPPO cao cấp",18_000_000,22_000_000,8,3,12,"Xanh biển","256GB","12GB"),
            ("SP007","iPad Pro M4 11\"",   cid("Máy tính bảng"), sid("Apple Vietnam"),   "Apple","MVV43ZA","iPad Pro 2024",22_000_000,26_000_000,10,2,12,"Bạc","256GB","8GB"),
            ("SP008","Samsung Tab S9",     cid("Máy tính bảng"), sid("Samsung Vietnam"), "Samsung","SM-X710","Tablet cao cấp",16_000_000,19_000_000,8,2,12,"Đen","128GB","8GB"),
            ("SP009","AirPods Pro 2",      cid("Phụ kiện"),      sid("Apple Vietnam"),   "Apple","MTJV3ZA","Tai nghe ANC",5_500_000,6_500_000,25,5,12,"Trắng","",""),
            ("SP010","Ốp lưng iPhone 15",  cid("Phụ kiện"),      sid("Apple Vietnam"),   "Apple","MT1F3FE","Silicone chính hãng",500_000,800_000,50,10,0,"Đen","",""),
            ("SP011","Apple Watch S9",     cid("Đồng hồ thông minh"),sid("Apple Vietnam"),"Apple","MR9J3VN","Smartwatch Apple",9_000_000,11_000_000,15,3,12,"Nhôm Đen","",""),
            ("SP012","Cáp USB-C Apple 2m", cid("Phụ kiện"),      sid("Apple Vietnam"),   "Apple","MQKJ3ZM","Cáp sạc chính hãng",300_000,500_000,100,10,6,"Trắng","",""),
        ]
        c.executemany("""
            INSERT OR IGNORE INTO products
            (code,name,category_id,supplier_id,brand,model,description,
             import_price,selling_price,quantity,min_quantity,warranty_months,color,storage,ram)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", products)

        customers = [
            ("KH000001","Nguyễn Văn An",  "0901111111","an@email.com",   "Hà Nội",    "1990-05-15","Nam"),
            ("KH000002","Trần Thị Bình",  "0912222222","binh@email.com", "TP.HCM",    "1995-08-20","Nữ"),
            ("KH000003","Lê Văn Cường",   "0923333333","cuong@email.com","Đà Nẵng",   "1988-03-10","Nam"),
            ("KH000004","Phạm Thị Dung",  "0934444444","dung@email.com", "Hải Phòng", "1992-12-25","Nữ"),
            ("KH000005","Hoàng Văn Em",   "0945555555","em@email.com",   "Cần Thơ",   "1985-07-07","Nam"),
        ]
        c.executemany("""
            INSERT OR IGNORE INTO customers
            (code,full_name,phone,email,address,birthday,gender) VALUES (?,?,?,?,?,?,?)""",
            customers)

        conn.commit()

    # ── CRUD helpers ────────────────────────────────────────────

    def execute(self, query: str, params=()) -> int:
        conn = self.get_connection()
        try:
            c = conn.cursor()
            c.execute(query, params)
            conn.commit()
            return c.lastrowid
        finally:
            conn.close()

    def fetchall(self, query: str, params=()) -> list:
        conn = self.get_connection()
        try:
            c = conn.cursor()
            c.execute(query, params)
            return [dict(row) for row in c.fetchall()]
        finally:
            conn.close()

    def fetchone(self, query: str, params=()) -> dict | None:
        conn = self.get_connection()
        try:
            c = conn.cursor()
            c.execute(query, params)
            row = c.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def log_activity(self, user_id: int, action: str, module: str, description: str = ""):
        self.execute(
            "INSERT INTO activity_logs (user_id,action,module,description) VALUES (?,?,?,?)",
            (user_id, action, module, description)
        )

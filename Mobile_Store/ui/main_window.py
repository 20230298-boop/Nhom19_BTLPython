"""
main_window.py
─────────────────────────────────────────
Cửa sổ chính: sidebar điều hướng + khu vực nội dung.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from utils.constants import COLORS, FONT_FAMILY, MAIN_WINDOW_SIZE, MAIN_WINDOW_MIN


class MainWindow:
    def __init__(self, db, user: dict):
        self.db   = db
        self.user = user
        self.is_admin = (user["role"] == "admin")

        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.title(
            f"Mobile Store Pro  —  {user['full_name']}  ({user['role'].upper()})"
        )
        self.root.geometry(MAIN_WINDOW_SIZE)
        self.root.minsize(*MAIN_WINDOW_MIN)
        self.root.configure(fg_color=COLORS["bg"])
        self._center_window(1400, 850)

        self.current_page = None
        self.nav_buttons: dict = {}

        self._build_layout()
        self._navigate("dashboard")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self, w, h):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = max(0, (self.root.winfo_screenheight() - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")


    def _build_layout(self):
        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.root, width=240,
            fg_color=COLORS["sidebar"],
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(
            self.sidebar, fg_color=COLORS["dark2"],
            corner_radius=0, height=80,
        )
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(
            logo_frame, text="📱  Mobile Store",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLORS["primary"],
        ).pack(expand=True)

        uframe = ctk.CTkFrame(self.sidebar, fg_color=COLORS["card2"], corner_radius=8)
        uframe.pack(fill="x", padx=10, pady=10)
        icon = "👑" if self.is_admin else "👤"
        role_text = "Quản trị viên" if self.is_admin else "Nhân viên"
        ctk.CTkLabel(
            uframe, text=f"{icon}  {self.user['full_name']}",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        ).pack(pady=(8, 2), padx=10, anchor="w")
        ctk.CTkLabel(
            uframe, text=role_text,
            font=(FONT_FAMILY, 10),
            text_color=COLORS["primary"],
        ).pack(padx=10, anchor="w", pady=(0, 8))

        nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        nav_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        current_group = None
        for item in self._nav_items():
            if item.get("group") and item["group"] != current_group:
                current_group = item["group"]
                ctk.CTkLabel(
                    nav_scroll, text=current_group.upper(),
                    font=(FONT_FAMILY, 9, "bold"),
                    text_color=COLORS["text_muted"],
                ).pack(anchor="w", padx=15, pady=(12, 4))

            btn = ctk.CTkButton(
                nav_scroll,
                text=f"  {item['icon']}  {item['label']}",
                command=lambda p=item["page"]: self._navigate(p),
                width=220, height=40,
                font=(FONT_FAMILY, 12),
                fg_color="transparent",
                hover_color=COLORS["card2"],
                text_color=COLORS["text"],
                anchor="w",
                corner_radius=8,
            )
            btn.pack(fill="x", pady=1)
            self.nav_buttons[item["page"]] = btn

        ctk.CTkButton(
            self.sidebar, text="  🚪  Đăng xuất",
            command=self._logout,
            width=220, height=40,
            font=(FONT_FAMILY, 12),
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_dark"],
            text_color=COLORS["white"],
            corner_radius=8,
        ).pack(padx=10, pady=10, fill="x")

    def _build_content_area(self):
        content = ctk.CTkFrame(self.root, fg_color=COLORS["bg"], corner_radius=0)
        content.pack(side="left", fill="both", expand=True)

        topbar = ctk.CTkFrame(content, fg_color=COLORS["dark2"],
                              corner_radius=0, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.page_title_label = ctk.CTkLabel(
            topbar, text="Dashboard",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text"],
        )
        self.page_title_label.pack(side="left", padx=20, pady=15)

        self.clock_label = ctk.CTkLabel(
            topbar, text="",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
        )
        self.clock_label.pack(side="right", padx=20)
        self._update_clock()

        self.page_container = ctk.CTkFrame(
            content, fg_color=COLORS["bg"], corner_radius=0
        )
        self.page_container.pack(fill="both", expand=True)


    def _nav_items(self):
        items = [
            {"page": "dashboard",  "label": "Tổng quan",        "icon": "🏠", "group": "TỔNG QUAN"},
            {"page": "pos",        "label": "Bán hàng (POS)",    "icon": "🛒", "group": "BÁN HÀNG"},
            {"page": "invoices",   "label": "Hóa đơn",           "icon": "🧾", "group": "BÁN HÀNG"},
            {"page": "products",   "label": "Sản phẩm",          "icon": "📦", "group": "KHO HÀNG"},
            {"page": "inventory",  "label": "Nhập hàng",         "icon": "📥", "group": "KHO HÀNG"},
            {"page": "customers",  "label": "Khách hàng",        "icon": "👥", "group": "KHÁCH HÀNG"},
            {"page": "warranties", "label": "Bảo hành",          "icon": "🔧", "group": "DỊCH VỤ"},
        ]
        if self.is_admin:
            items += [
                {"page": "reports",    "label": "Báo cáo",           "icon": "📊", "group": "QUẢN LÝ"},
                {"page": "suppliers",  "label": "Nhà cung cấp",      "icon": "🏭", "group": "QUẢN LÝ"},
                {"page": "categories", "label": "Danh mục",          "icon": "🗂",  "group": "QUẢN LÝ"},
                {"page": "users",      "label": "Người dùng",        "icon": "👤", "group": "QUẢN LÝ"},
                {"page": "logs",       "label": "Nhật ký hoạt động", "icon": "📋", "group": "HỆ THỐNG"},
            ]
        return items

    PAGE_TITLES = {
        "dashboard":  "🏠  Tổng quan",
        "pos":        "🛒  Điểm bán hàng (POS)",
        "invoices":   "🧾  Quản lý hóa đơn",
        "products":   "📦  Quản lý sản phẩm",
        "inventory":  "📥  Nhập hàng",
        "customers":  "👥  Quản lý khách hàng",
        "warranties": "🔧  Quản lý bảo hành",
        "reports":    "📊  Báo cáo & Thống kê",
        "suppliers":  "🏭  Nhà cung cấp",
        "categories": "🗂   Danh mục sản phẩm",
        "users":      "👤  Quản lý người dùng",
        "logs":       "📋  Nhật ký hoạt động",
    }

    def _navigate(self, page_name: str):
        for name, btn in self.nav_buttons.items():
            btn.configure(
                fg_color=COLORS["primary"] if name == page_name else "transparent",
                text_color=COLORS["white"]  if name == page_name else COLORS["text"],
            )

        for w in self.page_container.winfo_children():
            w.destroy()

        self.page_title_label.configure(
            text=self.PAGE_TITLES.get(page_name, page_name)
        )

        page = self._create_page(page_name)
        if page:
            page.pack(fill="both", expand=True)
        self.current_page = page_name

    def _create_page(self, name: str):
        mapping = {
            "dashboard":  ("ui.pages.dashboard",  "DashboardPage"),
            "pos":        ("ui.pages.pos",         "POSPage"),
            "invoices":   ("ui.pages.invoices",    "InvoicesPage"),
            "products":   ("ui.pages.products",    "ProductsPage"),
            "inventory":  ("ui.pages.inventory",   "InventoryPage"),
            "customers":  ("ui.pages.customers",   "CustomersPage"),
            "warranties": ("ui.pages.warranties",  "WarrantyPage"),
            "reports":    ("ui.pages.reports",     "ReportsPage"),
            "suppliers":  ("ui.pages.suppliers",   "SuppliersPage"),
            "categories": ("ui.pages.categories",  "CategoriesPage"),
            "users":      ("ui.pages.users",       "UsersPage"),
            "logs":       ("ui.pages.logs",        "LogsPage"),
        }
        if name not in mapping:
            return None
        module_path, class_name = mapping[name]
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls(self.page_container, self.db, self.user)


    def _update_clock(self):
        now = datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y")
        self.clock_label.configure(text=f"🕐  {now}")
        self.root.after(1000, self._update_clock)


    def _logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đăng xuất?"):
            self.db.log_activity(self.user["id"], "LOGOUT", "Auth", "Đăng xuất hệ thống")
            self.root.destroy()
            from database.db_manager import DatabaseManager
            from ui.login_window import LoginWindow
            LoginWindow(DatabaseManager(self.db.db_path)).run()

    def _on_close(self):
        if messagebox.askyesno("Thoát", "Bạn có chắc muốn thoát chương trình?"):
            self.root.destroy()

    def run(self):
        self.root.mainloop()

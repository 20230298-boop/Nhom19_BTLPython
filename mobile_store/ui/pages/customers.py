"""
pages/customers.py  –  Quản lý khách hàng
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency, format_number
from ui.widgets import StyledButton, StyledTreeview


class CustomersPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db   = db
        self.user = user
        self._build()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=60)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        t = ctk.CTkFrame(bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=10)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(t, textvariable=self.search_var,
                     placeholder_text="🔍  Tìm theo tên, SĐT, mã KH...",
                     width=300, height=38,
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     font=(FONT_FAMILY, 12), text_color=COLORS["text"]).pack(side="left")
        self.search_var.trace("w", lambda *_: self._load())

        StyledButton(t, "Thêm KH",    self._add,     style="success", icon="➕").pack(side="left", padx=8)
        StyledButton(t, "Sửa",        self._edit,    style="warning", icon="✏️").pack(side="left", padx=4)
        StyledButton(t, "Lịch sử mua",self._history, style="info",    icon="📋").pack(side="left", padx=4)
        StyledButton(t, "Xóa",        self._delete,  style="danger",  icon="🗑").pack(side="left", padx=4)

        cols   = ("code","full_name","phone","email","gender","loyalty","total_spent","type","created")
        heads  = ("Mã KH","Tên khách hàng","Số điện thoại","Email","GT","Điểm TT","Tổng mua","Loại KH","Ngày tạo")
        widths = [90, 180, 120, 180, 60, 80, 140, 100, 110]
        self.tree = StyledTreeview(self, cols, heads, widths, height=25)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        self.status_var = ctk.StringVar()
        ctk.CTkLabel(self, textvariable=self.status_var, font=(FONT_FAMILY, 11),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=20, pady=(0, 8))
        self._load()

    def _load(self):
        self.tree.clear()
        kw = self.search_var.get().strip()
        q  = "SELECT * FROM customers WHERE is_active=1"
        p  = []
        if kw:
            q += " AND (full_name LIKE ? OR phone LIKE ? OR code LIKE ? OR email LIKE ?)"
            p  = [f"%{kw}%"] * 4
        q += " ORDER BY full_name"
        rows = self.db.fetchall(q, p)
        for r in rows:
            spent = r["total_spent"] or 0
            ctype = ("VIP 💎"        if spent >= 50_000_000 else
                     "Thân thiết ⭐" if spent >= 10_000_000 else "Thường")
            self.tree.insert_row((
                r["code"], r["full_name"], r["phone"] or "", r["email"] or "",
                r["gender"] or "", format_number(r["loyalty_pts"]),
                format_currency(spent), ctype,
                r["created_at"][:10] if r["created_at"] else "",
            ))
        self.status_var.set(f"Tổng: {len(rows)} khách hàng")

    def _add(self):
        from ui.dialogs.customer_dialog import CustomerDialog
        dlg = CustomerDialog(self, self.db)
        self.wait_window(dlg); self._load()

    def _edit(self):
        sel = self.tree.get_selected()
        if not sel:
            messagebox.showwarning("Thông báo", "Chọn khách hàng!"); return
        cust = self.db.fetchone("SELECT * FROM customers WHERE code=?", (sel[0],))
        if cust:
            from ui.dialogs.customer_dialog import CustomerDialog
            dlg = CustomerDialog(self, self.db, cust)
            self.wait_window(dlg); self._load()

    def _delete(self):
        sel = self.tree.get_selected()
        if not sel: return
        if messagebox.askyesno("Xác nhận", f"Ẩn khách hàng '{sel[1]}'?"):
            self.db.execute("UPDATE customers SET is_active=0 WHERE code=?", (sel[0],))
            self._load()

    def _history(self):
        sel = self.tree.get_selected()
        if not sel: return
        cust = self.db.fetchone("SELECT * FROM customers WHERE code=?", (sel[0],))
        if cust:
            from ui.dialogs.customer_history import CustomerHistoryDialog
            self.wait_window(CustomerHistoryDialog(self, self.db, cust))

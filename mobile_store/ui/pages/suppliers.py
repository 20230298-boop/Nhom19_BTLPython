"""
pages/suppliers.py  –  Quản lý nhà cung cấp
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY
from ui.widgets import StyledButton, StyledTreeview


class SuppliersPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db = db; self.user = user; self._build()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=60)
        bar.pack(fill="x"); bar.pack_propagate(False)
        t = ctk.CTkFrame(bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=10)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(t, textvariable=self.search_var,
                     placeholder_text="🔍  Tìm nhà cung cấp...",
                     width=280, height=38,
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     font=(FONT_FAMILY, 12), text_color=COLORS["text"]).pack(side="left")
        self.search_var.trace("w", lambda *_: self._load())

        StyledButton(t, "Thêm mới", self._add,    style="success", icon="➕").pack(side="left", padx=8)
        StyledButton(t, "Sửa",      self._edit,   style="warning", icon="✏️").pack(side="left", padx=4)
        StyledButton(t, "Xóa",      self._delete, style="danger",  icon="🗑").pack(side="left", padx=4)

        cols   = ("name", "contact", "phone", "email", "address", "tax_code", "status")
        heads  = ("Tên NCC", "Liên hệ", "SĐT", "Email", "Địa chỉ", "MST", "Trạng thái")
        widths = [180, 130, 120, 180, 200, 120, 100]
        self.tree = StyledTreeview(self, cols, heads, widths, height=25)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self._load()

    def _load(self):
        self.tree.clear()
        kw = self.search_var.get().strip()
        q  = "SELECT * FROM suppliers WHERE 1=1"
        p  = []
        if kw:
            q += " AND (name LIKE ? OR phone LIKE ? OR contact LIKE ?)"; p = [f"%{kw}%"] * 3
        q += " ORDER BY name"
        for r in self.db.fetchall(q, p):
            self.tree.insert_row((
                r["name"], r["contact"] or "", r["phone"] or "",
                r["email"] or "", r["address"] or "", r["tax_code"] or "",
                "✅ Hoạt động" if r["is_active"] else "❌ Ngừng",
            ))

    def _add(self):
        from ui.dialogs.supplier_dialog import SupplierDialog
        dlg = SupplierDialog(self, self.db); self.wait_window(dlg); self._load()

    def _edit(self):
        sel = self.tree.get_selected()
        if not sel: return
        sup = self.db.fetchone("SELECT * FROM suppliers WHERE name=?", (sel[0],))
        if sup:
            from ui.dialogs.supplier_dialog import SupplierDialog
            dlg = SupplierDialog(self, self.db, sup); self.wait_window(dlg); self._load()

    def _delete(self):
        sel = self.tree.get_selected()
        if not sel: return
        if messagebox.askyesno("Xác nhận", f"Ẩn nhà cung cấp '{sel[0]}'?"):
            self.db.execute("UPDATE suppliers SET is_active=0 WHERE name=?", (sel[0],))
            self._load()

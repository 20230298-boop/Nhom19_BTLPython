"""
dialogs/customer_select.py  –  Dialog chọn khách hàng khi bán hàng
"""

import customtkinter as ctk
from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency
from ui.widgets import StyledButton, StyledTreeview


class CustomerSelectDialog(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db     = db
        self.result = None
        self.title("Chọn khách hàng")
        self.geometry("620x460")
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Tìm khách hàng",
                     font=(FONT_FAMILY, 14, "bold"),
                     text_color=COLORS["text"]).pack(pady=(16, 8), padx=20, anchor="w")

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.search_var,
                     placeholder_text="🔍  Tên, số điện thoại, mã KH...",
                     height=38, font=(FONT_FAMILY, 12),
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     text_color=COLORS["text"]).pack(fill="x", padx=20, pady=(0, 8))
        self.search_var.trace("w", lambda *_: self._search())

        self.tree = StyledTreeview(self,
                                   ("code", "full_name", "phone", "total_spent"),
                                   ("Mã KH", "Tên khách", "SĐT", "Tổng mua"),
                                   [90, 200, 120, 140], height=11)
        self.tree.pack(fill="both", expand=True, padx=20)
        self.tree.tree.bind("<Double-1>", lambda _: self._select())

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=14, padx=20, fill="x")
        StyledButton(btns, "✅  Chọn",    self._select, style="primary", width=110).pack(side="left")
        StyledButton(btns, "👤  Khách lẻ",self._guest,  style="dark",    width=120).pack(side="left", padx=8)
        StyledButton(btns, "❌  Hủy",     self.destroy, style="danger",  width=100).pack(side="right")
        self._search()

    def _search(self):
        self.tree.clear()
        kw = self.search_var.get().strip()
        q  = "SELECT * FROM customers WHERE is_active=1"
        p  = []
        if kw:
            q += " AND (full_name LIKE ? OR phone LIKE ? OR code LIKE ?)"; p = [f"%{kw}%"] * 3
        q += " ORDER BY full_name LIMIT 60"
        for r in self.db.fetchall(q, p):
            self.tree.insert_row((r["code"], r["full_name"],
                                  r["phone"] or "", format_currency(r["total_spent"])))

    def _select(self):
        sel = self.tree.get_selected()
        if not sel: return
        self.result = self.db.fetchone("SELECT * FROM customers WHERE code=?", (sel[0],))
        self.destroy()

    def _guest(self):
        self.result = None
        self.destroy()

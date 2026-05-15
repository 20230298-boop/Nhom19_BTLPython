"""
pages/warranties.py  –  Quản lý bảo hành
"""

import customtkinter as ctk
from utils.constants import COLORS, FONT_FAMILY, WARRANTY_STATUSES
from utils.helpers import format_currency
from ui.widgets import StyledButton, StyledTreeview


class WarrantyPage(ctk.CTkFrame):
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
                     placeholder_text="🔍  Tìm số BH, khách hàng...",
                     width=260, height=38,
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     font=(FONT_FAMILY, 12), text_color=COLORS["text"]).pack(side="left")
        self.search_var.trace("w", lambda *_: self._load())

        self.status_filter = ctk.StringVar(value="Tất cả")
        ctk.CTkOptionMenu(t, variable=self.status_filter,
                          values=["Tất cả"] + WARRANTY_STATUSES,
                          command=lambda _: self._load(),
                          width=160, height=38,
                          fg_color=COLORS["card2"], button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 11)).pack(side="left", padx=8)

        StyledButton(t, "Tạo phiếu BH",  self._add,           style="success", icon="➕", width=140).pack(side="left")
        StyledButton(t, "Cập nhật trạng thái", self._update,   style="warning", icon="✏️", width=180).pack(side="left", padx=8)

        cols   = ("warranty_no","customer","product","issue","status","tech","cost","received","completed")
        heads  = ("Số BH","Khách hàng","Sản phẩm","Mô tả lỗi","Trạng thái","KT viên","Chi phí","Ngày nhận","Hoàn thành")
        widths = [110, 150, 150, 180, 120, 120, 100, 110, 110]
        self.tree = StyledTreeview(self, cols, heads, widths, height=25)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self._load()

    def _load(self):
        self.tree.clear()
        kw = self.search_var.get().strip()
        st = self.status_filter.get()
        q  = """SELECT w.*, c.full_name as cust_name, p.name as prod_name
                FROM warranties w
                LEFT JOIN customers c ON w.customer_id=c.id
                LEFT JOIN products  p ON w.product_id=p.id WHERE 1=1"""
        params = []
        if kw:
            q += " AND (w.warranty_no LIKE ? OR c.full_name LIKE ?)"; params += [f"%{kw}%"] * 2
        if st != "Tất cả":
            q += " AND w.status=?"; params.append(st)
        q += " ORDER BY w.created_at DESC"
        for r in self.db.fetchall(q, params):
            tags = ["pending"] if r["status"] == "Đang xử lý" else (["paid"] if r["status"] == "Hoàn thành" else [])
            self.tree.insert_row((
                r["warranty_no"], r["cust_name"] or "", r["prod_name"] or "",
                r["issue_desc"] or "", r["status"], r["technician"] or "",
                format_currency(r["repair_cost"]),
                r["received_date"][:10] if r["received_date"] else "",
                r["completed_date"][:10] if r["completed_date"] else "",
            ), tags=tags)

    def _add(self):
        from ui.dialogs.warranty_dialog import WarrantyDialog
        dlg = WarrantyDialog(self, self.db, self.user)
        self.wait_window(dlg); self._load()

    def _update(self):
        sel = self.tree.get_selected()
        if not sel: return
        w = self.db.fetchone("SELECT * FROM warranties WHERE warranty_no=?", (sel[0],))
        if w:
            from ui.dialogs.warranty_dialog import WarrantyUpdateDialog
            self.wait_window(WarrantyUpdateDialog(self, self.db, w))
            self._load()

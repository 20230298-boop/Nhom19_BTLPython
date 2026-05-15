"""
pages/logs.py  –  Nhật ký hoạt động hệ thống
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY
from ui.widgets import StyledButton, StyledTreeview


class LogsPage(ctk.CTkFrame):
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
                     placeholder_text="🔍  Tìm kiếm logs...",
                     width=250, height=38,
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     font=(FONT_FAMILY, 12), text_color=COLORS["text"]).pack(side="left")
        self.search_var.trace("w", lambda *_: self._load())

        self.module_var = ctk.StringVar(value="Tất cả")
        ctk.CTkOptionMenu(t, variable=self.module_var,
                          values=["Tất cả", "Auth", "POS", "Products", "Customers", "Inventory"],
                          command=lambda _: self._load(),
                          width=140, height=38,
                          fg_color=COLORS["card2"], button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 11)).pack(side="left", padx=8)

        StyledButton(t, "Xóa logs cũ (30 ngày)", self._clear_old,
                     style="danger", icon="🗑", width=210).pack(side="right")

        cols   = ("user", "action", "module", "description", "time")
        heads  = ("Người dùng", "Hành động", "Module", "Mô tả chi tiết", "Thời gian")
        widths = [140, 160, 110, 380, 150]
        self.tree = StyledTreeview(self, cols, heads, widths, height=28)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self._load()

    def _load(self):
        self.tree.clear()
        kw     = self.search_var.get().strip()
        module = self.module_var.get()
        q = """SELECT al.*, u.username FROM activity_logs al
               LEFT JOIN users u ON al.user_id=u.id WHERE 1=1"""
        params = []
        if kw:
            q += " AND (al.action LIKE ? OR al.description LIKE ?)"; params += [f"%{kw}%"] * 2
        if module != "Tất cả":
            q += " AND al.module=?"; params.append(module)
        q += " ORDER BY al.created_at DESC LIMIT 500"
        for r in self.db.fetchall(q, params):
            self.tree.insert_row((
                r["username"] or "N/A", r["action"], r["module"] or "",
                r["description"] or "",
                r["created_at"][:16] if r["created_at"] else "",
            ))

    def _clear_old(self):
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ logs cũ hơn 30 ngày?"):
            self.db.execute(
                "DELETE FROM activity_logs WHERE created_at < datetime('now','-30 days','localtime')")
            self._load()
            messagebox.showinfo("Thành công", "Đã xóa logs cũ!")

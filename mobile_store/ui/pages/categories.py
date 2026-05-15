"""
pages/categories.py  –  Quản lý danh mục sản phẩm
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY
from ui.widgets import StyledButton, StyledTreeview


class CategoriesPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db = db; self.user = user; self._build()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=60)
        bar.pack(fill="x"); bar.pack_propagate(False)
        t = ctk.CTkFrame(bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=10)

        StyledButton(t, "Thêm danh mục", self._add,    style="success", icon="➕", width=150).pack(side="left")
        StyledButton(t, "Sửa",           self._edit,   style="warning", icon="✏️").pack(side="left", padx=8)
        StyledButton(t, "Xóa",           self._delete, style="danger",  icon="🗑").pack(side="left", padx=4)

        cols   = ("icon", "name", "description", "product_count", "created")
        heads  = ("Icon", "Tên danh mục", "Mô tả", "Số sản phẩm", "Ngày tạo")
        widths = [60, 200, 320, 120, 130]
        self.tree = StyledTreeview(self, cols, heads, widths, height=25)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self._load()

    def _load(self):
        self.tree.clear()
        for r in self.db.fetchall("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM products p WHERE p.category_id=c.id AND p.is_active=1) as cnt
            FROM categories c ORDER BY c.name"""):
            self.tree.insert_row((
                r["icon"] or "📱", r["name"], r["description"] or "", r["cnt"],
                r["created_at"][:10] if r["created_at"] else "",
            ))

    def _add(self):
        from ui.dialogs.category_dialog import CategoryDialog
        dlg = CategoryDialog(self, self.db); self.wait_window(dlg); self._load()

    def _edit(self):
        sel = self.tree.get_selected()
        if not sel: return
        cat = self.db.fetchone("SELECT * FROM categories WHERE name=?", (sel[1],))
        if cat:
            from ui.dialogs.category_dialog import CategoryDialog
            dlg = CategoryDialog(self, self.db, cat); self.wait_window(dlg); self._load()

    def _delete(self):
        sel = self.tree.get_selected()
        if not sel: return
        if messagebox.askyesno("Xác nhận", f"Xóa danh mục '{sel[1]}'?"):
            self.db.execute("DELETE FROM categories WHERE name=?", (sel[1],))
            self._load()

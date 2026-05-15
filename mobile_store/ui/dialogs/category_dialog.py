"""
dialogs/category_dialog.py  –  Thêm / sửa danh mục
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY, DIALOG_SIZE_SM
from ui.widgets import StyledButton


class CategoryDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, category=None):
        super().__init__(parent)
        self.db       = db
        self.category = category
        self.title("Thêm danh mục" if not category else "Sửa danh mục")
        self.geometry(DIALOG_SIZE_SM)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        f = ctk.CTkFrame(self, fg_color=COLORS["bg"]); f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text="Thông tin danh mục",
                     font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        def row(label):
            r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", pady=5)
            ctk.CTkLabel(r, text=label, width=130, anchor="w",
                         font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            e = ctk.CTkEntry(r, height=36, font=(FONT_FAMILY, 12),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"])
            e.pack(side="left", fill="x", expand=True)
            return e

        self.e_name = row("Tên danh mục *")
        self.e_icon = row("Icon (emoji)")
        self.e_desc = row("Mô tả")

        if self.category:
            c = self.category
            for w, v in [(self.e_name, c["name"]), (self.e_icon, c["icon"]), (self.e_desc, c["description"])]:
                w.delete(0, "end"); w.insert(0, str(v or ""))
        else:
            self.e_icon.insert(0, "📱")

        btns = ctk.CTkFrame(f, fg_color="transparent"); btns.pack(pady=(16, 0))
        StyledButton(btns, "💾  Lưu", self._save,   style="success", width=130, height=40).pack(side="left")
        StyledButton(btns, "Hủy",     self.destroy, style="danger",  width=100, height=40).pack(side="left", padx=8)

    def _save(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên danh mục!"); return
        data = (name, self.e_icon.get().strip() or "📱", self.e_desc.get().strip())
        if self.category:
            self.db.execute("UPDATE categories SET name=?, icon=?, description=? WHERE id=?",
                            (*data, self.category["id"]))
        else:
            self.db.execute("INSERT INTO categories (name, icon, description) VALUES (?,?,?)", data)
        self.destroy()

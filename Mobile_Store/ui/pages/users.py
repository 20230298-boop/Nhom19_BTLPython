"""
pages/users.py  –  Quản lý người dùng (chỉ admin)
"""

import customtkinter as ctk
import hashlib
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY
from ui.widgets import StyledButton, StyledTreeview


class UsersPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db = db; self.current_user = user; self._build()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=60)
        bar.pack(fill="x"); bar.pack_propagate(False)
        t = ctk.CTkFrame(bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=10)

        StyledButton(t, "Thêm người dùng", self._add,           style="success", icon="➕", width=170).pack(side="left")
        StyledButton(t, "Sửa",             self._edit,          style="warning", icon="✏️").pack(side="left", padx=8)
        StyledButton(t, "Khóa / Mở",       self._toggle_active, style="info",    icon="🔒").pack(side="left", padx=4)
        StyledButton(t, "Đặt lại MK",      self._reset_pw,      style="purple",  icon="🔑").pack(side="left", padx=4)

        cols   = ("username", "full_name", "role", "email", "phone", "last_login", "status")
        heads  = ("Tên đăng nhập", "Họ tên", "Vai trò", "Email", "SĐT", "Đăng nhập cuối", "Trạng thái")
        widths = [130, 180, 120, 180, 120, 160, 110]
        self.tree = StyledTreeview(self, cols, heads, widths, height=25)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self._load()

    def _load(self):
        self.tree.clear()
        for r in self.db.fetchall("SELECT * FROM users ORDER BY role, full_name"):
            self.tree.insert_row((
                r["username"], r["full_name"],
                "👑 Admin" if r["role"] == "admin" else "👤 Nhân viên",
                r["email"] or "", r["phone"] or "",
                r["last_login"][:16] if r["last_login"] else "Chưa đăng nhập",
                "✅ Hoạt động" if r["is_active"] else "🔒 Bị khóa",
            ))

    def _add(self):
        from ui.dialogs.user_dialog import UserDialog
        dlg = UserDialog(self, self.db); self.wait_window(dlg); self._load()

    def _edit(self):
        sel = self.tree.get_selected()
        if not sel: return
        u = self.db.fetchone("SELECT * FROM users WHERE username=?", (sel[0],))
        if u:
            from ui.dialogs.user_dialog import UserDialog
            dlg = UserDialog(self, self.db, u); self.wait_window(dlg); self._load()

    def _toggle_active(self):
        sel = self.tree.get_selected()
        if not sel: return
        if sel[0] == self.current_user["username"]:
            messagebox.showwarning("Cảnh báo", "Không thể khóa tài khoản đang đăng nhập!"); return
        u = self.db.fetchone("SELECT id, is_active FROM users WHERE username=?", (sel[0],))
        if u:
            self.db.execute("UPDATE users SET is_active=? WHERE id=?",
                            (0 if u["is_active"] else 1, u["id"]))
            self._load()

    def _reset_pw(self):
        sel = self.tree.get_selected()
        if not sel: return
        new_pw = "123456"
        hashed = hashlib.sha256(new_pw.encode()).hexdigest()
        self.db.execute("UPDATE users SET password=? WHERE username=?", (hashed, sel[0]))
        messagebox.showinfo("Thành công",
                            f"Đặt lại mật khẩu cho '{sel[0]}' thành: {new_pw}")

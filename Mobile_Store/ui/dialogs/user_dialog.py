"""
dialogs/user_dialog.py  –  Thêm / sửa người dùng
"""

import customtkinter as ctk
import hashlib
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY, DIALOG_SIZE_MD
from ui.widgets import StyledButton


class UserDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, user=None):
        super().__init__(parent)
        self.db   = db
        self.user = user
        self.title("Thêm người dùng" if not user else "Sửa người dùng")
        self.geometry(DIALOG_SIZE_MD)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Thông tin người dùng",
                     font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        def row(label):
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=label, width=165, anchor="w",
                         font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            e = ctk.CTkEntry(f, height=36, font=(FONT_FAMILY, 12),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"])
            e.pack(side="left", fill="x", expand=True)
            return e

        self.e_username = row("Tên đăng nhập *")
        self.e_fullname = row("Họ và tên *")
        self.e_email    = row("Email")
        self.e_phone    = row("Số điện thoại")
        if not self.user:
            self.e_password = row("Mật khẩu *")

        rf = ctk.CTkFrame(scroll, fg_color="transparent"); rf.pack(fill="x", pady=5)
        ctk.CTkLabel(rf, text="Vai trò", width=165, anchor="w",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.v_role = ctk.StringVar(value="staff")
        ctk.CTkOptionMenu(rf, variable=self.v_role, values=["admin", "staff"],
                          width=160, height=36, fg_color=COLORS["card2"],
                          button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 12)).pack(side="left")

        if self.user:
            u = self.user
            for w, v in [(self.e_username, u["username"]), (self.e_fullname, u["full_name"]),
                         (self.e_email, u["email"]),       (self.e_phone,    u["phone"])]:
                w.delete(0, "end"); w.insert(0, str(v or ""))
            self.v_role.set(u["role"])

        btns = ctk.CTkFrame(scroll, fg_color="transparent"); btns.pack(fill="x", pady=(16, 0))
        StyledButton(btns, "💾  Lưu lại", self._save,   style="success", width=140, height=42).pack(side="left")
        StyledButton(btns, "❌  Hủy",     self.destroy, style="danger",  width=100, height=42).pack(side="left", padx=8)

    def _save(self):
        username = self.e_username.get().strip()
        fullname = self.e_fullname.get().strip()
        if not username or not fullname:
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!"); return
        if self.user:
            self.db.execute(
                "UPDATE users SET username=?, full_name=?, email=?, phone=?, role=? WHERE id=?",
                (username, fullname, self.e_email.get().strip(),
                 self.e_phone.get().strip(), self.v_role.get(), self.user["id"]))
        else:
            pw = self.e_password.get().strip()
            if not pw:
                messagebox.showwarning("Lỗi", "Vui lòng nhập mật khẩu!"); return
            hashed = hashlib.sha256(pw.encode()).hexdigest()
            self.db.execute(
                "INSERT INTO users (username,password,full_name,email,phone,role) VALUES (?,?,?,?,?,?)",
                (username, hashed, fullname, self.e_email.get().strip(),
                 self.e_phone.get().strip(), self.v_role.get()))
        self.destroy()

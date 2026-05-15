"""
login_window.py
─────────────────────────────────────────
Cửa sổ đăng nhập hệ thống.
"""

import customtkinter as ctk
from datetime import datetime

from utils.constants import COLORS, FONT_FAMILY, LOGIN_WINDOW_SIZE
from utils.helpers import verify_password


class LoginWindow:
    def __init__(self, db):
        self.db = db
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Đăng nhập - Mobile Store Pro")
        self.root.geometry(LOGIN_WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(fg_color=COLORS["bg"])
        self._center_window(500, 620)
        self._build_ui()

    def _center_window(self, w, h):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")


    def _build_ui(self):
        bg = ctk.CTkFrame(self.root, fg_color=COLORS["bg"], corner_radius=0)
        bg.pack(fill="both", expand=True)

        self._build_logo(bg)
        self._build_form(bg)
        self._build_info_bar(bg)

        self.root.bind("<Return>", lambda e: self._login())
        self.username_entry.focus()

    def _build_logo(self, parent):
        logo = ctk.CTkFrame(parent, fg_color=COLORS["dark2"],
                            corner_radius=0, height=180)
        logo.pack(fill="x")
        logo.pack_propagate(False)

        ctk.CTkLabel(logo, text="📱",
                     font=(FONT_FAMILY, 52)).pack(pady=(25, 5))
        ctk.CTkLabel(logo, text="MOBILE STORE PRO",
                     font=(FONT_FAMILY, 22, "bold"),
                     text_color=COLORS["primary"]).pack()
        ctk.CTkLabel(logo, text="Hệ thống quản lý cửa hàng thiết bị di động",
                     font=(FONT_FAMILY, 11),
                     text_color=COLORS["text_muted"]).pack(pady=(2, 0))

    def _build_form(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"],
                            corner_radius=16, border_width=1,
                            border_color=COLORS["border"])
        card.pack(padx=40, pady=30, fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=30)

        ctk.CTkLabel(inner, text="Đăng nhập hệ thống",
                     font=(FONT_FAMILY, 18, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(inner, text="👤  Tên đăng nhập",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        self.username_var = ctk.StringVar(value="admin")
        self.username_entry = ctk.CTkEntry(
            inner, textvariable=self.username_var,
            width=360, height=44, font=(FONT_FAMILY, 13),
            fg_color=COLORS["card2"], border_color=COLORS["border"],
            text_color=COLORS["text"], corner_radius=8,
        )
        self.username_entry.pack(pady=(4, 14))

        ctk.CTkLabel(inner, text="🔒  Mật khẩu",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        self.password_var = ctk.StringVar(value="admin123")
        self.password_entry = ctk.CTkEntry(
            inner, textvariable=self.password_var,
            width=360, height=44, show="●", font=(FONT_FAMILY, 13),
            fg_color=COLORS["card2"], border_color=COLORS["border"],
            text_color=COLORS["text"], corner_radius=8,
        )
        self.password_entry.pack(pady=(4, 8))

        self.show_pw = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            inner, text="Hiện mật khẩu",
            variable=self.show_pw,
            command=self._toggle_password,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["primary"],
            checkmark_color=COLORS["white"],
        ).pack(anchor="w", pady=(0, 20))

        self.error_label = ctk.CTkLabel(
            inner, text="", font=(FONT_FAMILY, 11),
            text_color=COLORS["danger"],
        )
        self.error_label.pack(pady=(0, 8))

        self.login_btn = ctk.CTkButton(
            inner, text="🚀  ĐĂNG NHẬP",
            command=self._login,
            width=360, height=46,
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            corner_radius=8,
        )
        self.login_btn.pack()

    def _build_info_bar(self, parent):
        info = ctk.CTkFrame(parent, fg_color=COLORS["dark2"], corner_radius=8)
        info.pack(padx=40, fill="x")
        ctk.CTkLabel(
            info,
            text="💡  Tài khoản demo: admin / admin123   |   nhanvien / nv123",
            font=(FONT_FAMILY, 10),
            text_color=COLORS["text_muted"],
        ).pack(pady=8)


    def _toggle_password(self):
        self.password_entry.configure(
            show="" if self.show_pw.get() else "●"
        )

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.error_label.configure(text="⚠  Vui lòng nhập đầy đủ thông tin!")
            return

        user = self.db.fetchone(
            "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
        )
        if not user:
            self.error_label.configure(text="❌  Tài khoản không tồn tại hoặc đã bị khóa!")
            return

        if not verify_password(password, user["password"]):
            self.error_label.configure(text="❌  Mật khẩu không đúng!")
            return

        self.db.execute(
            "UPDATE users SET last_login=datetime('now','localtime') WHERE id=?",
            (user["id"],),
        )
        self.db.log_activity(
            user["id"], "LOGIN", "Auth",
            f"Đăng nhập thành công lúc {datetime.now().strftime('%H:%M:%S')}",
        )

        self.error_label.configure(
            text="✅  Đăng nhập thành công!",
            text_color=COLORS["success"],
        )
        self.root.after(500, lambda: self._open_main(user))

    def _open_main(self, user):
        self.root.destroy()
        from ui.main_window import MainWindow
        MainWindow(self.db, user).run()

    def run(self):
        self.root.mainloop()

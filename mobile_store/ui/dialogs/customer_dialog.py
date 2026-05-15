"""
dialogs/customer_dialog.py  –  Dialog thêm / sửa khách hàng
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY, GENDERS, DIALOG_SIZE_MD
from utils.helpers import generate_code
from ui.widgets import StyledButton


class CustomerDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, customer=None):
        super().__init__(parent)
        self.db       = db
        self.customer = customer
        self.title("Thêm khách hàng" if not customer else "Sửa khách hàng")
        self.geometry(DIALOG_SIZE_MD)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Thông tin khách hàng",
                     font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        def entry_row(label):
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=label, width=165, anchor="w",
                         font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            e = ctk.CTkEntry(f, height=36, font=(FONT_FAMILY, 12),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"])
            e.pack(side="left", fill="x", expand=True)
            return e

        self.e_code  = entry_row("Mã khách hàng *")
        self.e_name  = entry_row("Họ và tên *")
        self.e_phone = entry_row("Số điện thoại")
        self.e_email = entry_row("Email")
        self.e_addr  = entry_row("Địa chỉ")
        self.e_birth = entry_row("Ngày sinh (YYYY-MM-DD)")
        self.e_card  = entry_row("CCCD / CMND")

        # Gender
        gf = ctk.CTkFrame(scroll, fg_color="transparent"); gf.pack(fill="x", pady=5)
        ctk.CTkLabel(gf, text="Giới tính", width=165, anchor="w",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.v_gender = ctk.StringVar(value="Nam")
        ctk.CTkOptionMenu(gf, variable=self.v_gender, values=GENDERS,
                          width=150, height=36, fg_color=COLORS["card2"],
                          button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 12)).pack(side="left")

        # Note
        nf = ctk.CTkFrame(scroll, fg_color="transparent"); nf.pack(fill="x", pady=5)
        ctk.CTkLabel(nf, text="Ghi chú", width=165, anchor="w",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left", anchor="n")
        self.e_note = ctk.CTkTextbox(nf, height=60, font=(FONT_FAMILY, 12),
                                      fg_color=COLORS["card2"], border_color=COLORS["border"],
                                      text_color=COLORS["text"])
        self.e_note.pack(side="left", fill="x", expand=True)

        # Fill existing
        if self.customer:
            c = self.customer
            for w, v in [(self.e_code,  c["code"]),   (self.e_name,  c["full_name"]),
                         (self.e_phone, c["phone"]),  (self.e_email, c["email"]),
                         (self.e_addr,  c["address"]),(self.e_birth, c["birthday"]),
                         (self.e_card,  c["id_card"])]:
                w.delete(0, "end"); w.insert(0, str(v or ""))
            self.v_gender.set(c["gender"] or "Nam")
            if c.get("note"): self.e_note.insert("1.0", c["note"])
        else:
            count = (self.db.fetchone("SELECT COUNT(*) as c FROM customers") or {}).get("c", 0)
            self.e_code.insert(0, generate_code("KH", count + 1))

        btns = ctk.CTkFrame(scroll, fg_color="transparent"); btns.pack(fill="x", pady=(16, 0))
        StyledButton(btns, "💾  Lưu lại", self._save,   style="success", width=140, height=42).pack(side="left")
        StyledButton(btns, "❌  Hủy",     self.destroy, style="danger",  width=100, height=42).pack(side="left", padx=8)

    def _save(self):
        code = self.e_code.get().strip()
        name = self.e_name.get().strip()
        if not code or not name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mã và tên khách hàng!"); return
        data = dict(code=code, full_name=name,
                    phone=self.e_phone.get().strip(), email=self.e_email.get().strip(),
                    address=self.e_addr.get().strip(), birthday=self.e_birth.get().strip(),
                    id_card=self.e_card.get().strip(), gender=self.v_gender.get(),
                    note=self.e_note.get("1.0", "end").strip())
        if self.customer:
            sets = ", ".join(f"{k}=?" for k in data if k != "code")
            vals = [v for k, v in data.items() if k != "code"] + [self.customer["id"]]
            self.db.execute(f"UPDATE customers SET {sets} WHERE id=?", vals)
        else:
            cols = ", ".join(data.keys())
            phs  = ", ".join("?" * len(data))
            self.db.execute(f"INSERT INTO customers ({cols}) VALUES ({phs})", list(data.values()))
        self.destroy()

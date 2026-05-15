"""
dialogs/supplier_dialog.py  –  Thêm / sửa nhà cung cấp
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY, DIALOG_SIZE_MD
from ui.widgets import StyledButton


class SupplierDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, supplier=None):
        super().__init__(parent)
        self.db       = db
        self.supplier = supplier
        self.title("Thêm nhà cung cấp" if not supplier else "Sửa nhà cung cấp")
        self.geometry(DIALOG_SIZE_MD)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Thông tin nhà cung cấp",
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

        self.e_name    = row("Tên nhà cung cấp *")
        self.e_contact = row("Người liên hệ")
        self.e_phone   = row("Số điện thoại")
        self.e_email   = row("Email")
        self.e_address = row("Địa chỉ")
        self.e_tax     = row("Mã số thuế")

        nf = ctk.CTkFrame(scroll, fg_color="transparent"); nf.pack(fill="x", pady=5)
        ctk.CTkLabel(nf, text="Ghi chú", width=165, anchor="w",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left", anchor="n")
        self.e_note = ctk.CTkTextbox(nf, height=80, font=(FONT_FAMILY, 12),
                                      fg_color=COLORS["card2"], border_color=COLORS["border"],
                                      text_color=COLORS["text"])
        self.e_note.pack(side="left", fill="x", expand=True)

        if self.supplier:
            s = self.supplier
            for w, v in [(self.e_name, s["name"]), (self.e_contact, s["contact"]),
                         (self.e_phone, s["phone"]), (self.e_email, s["email"]),
                         (self.e_address, s["address"]), (self.e_tax, s["tax_code"])]:
                w.delete(0, "end"); w.insert(0, str(v or ""))
            if s.get("note"): self.e_note.insert("1.0", s["note"])

        btns = ctk.CTkFrame(scroll, fg_color="transparent"); btns.pack(fill="x", pady=(16, 0))
        StyledButton(btns, "💾  Lưu lại", self._save,   style="success", width=140, height=42).pack(side="left")
        StyledButton(btns, "❌  Hủy",     self.destroy, style="danger",  width=100, height=42).pack(side="left", padx=8)

    def _save(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên nhà cung cấp!"); return
        data = dict(name=name, contact=self.e_contact.get().strip(),
                    phone=self.e_phone.get().strip(), email=self.e_email.get().strip(),
                    address=self.e_address.get().strip(), tax_code=self.e_tax.get().strip(),
                    note=self.e_note.get("1.0", "end").strip())
        if self.supplier:
            sets = ", ".join(f"{k}=?" for k in data if k != "name")
            vals = [v for k, v in data.items() if k != "name"] + [self.supplier["id"]]
            self.db.execute(f"UPDATE suppliers SET {sets} WHERE id=?", vals)
        else:
            cols = ", ".join(data.keys())
            phs  = ", ".join("?" * len(data))
            self.db.execute(f"INSERT INTO suppliers ({cols}) VALUES ({phs})", list(data.values()))
        self.destroy()

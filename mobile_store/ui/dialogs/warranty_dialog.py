"""
dialogs/warranty_dialog.py  –  Tạo phiếu bảo hành & cập nhật trạng thái
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from utils.constants import COLORS, FONT_FAMILY, WARRANTY_STATUSES, DIALOG_SIZE_MD
from utils.helpers import parse_currency, generate_code
from ui.widgets import StyledButton


class WarrantyDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, user):
        super().__init__(parent)
        self.db   = db
        self.user = user
        self.title("Tạo phiếu bảo hành")
        self.geometry(DIALOG_SIZE_MD)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Phiếu tiếp nhận bảo hành",
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

        self.e_cust  = row("Tên khách hàng")
        self.e_phone = row("Số điện thoại")
        self.e_prod  = row("Tên sản phẩm")
        self.e_issue = row("Mô tả sự cố")
        self.e_tech  = row("Kỹ thuật viên")
        self.e_cost  = row("Chi phí dự kiến")

        btns = ctk.CTkFrame(scroll, fg_color="transparent"); btns.pack(fill="x", pady=(16, 0))
        StyledButton(btns, "💾  Lưu", self._save,   style="success", width=130, height=42).pack(side="left")
        StyledButton(btns, "❌  Hủy", self.destroy, style="danger",  width=100, height=42).pack(side="left", padx=8)

    def _save(self):
        count      = (self.db.fetchone("SELECT COUNT(*) as c FROM warranties") or {}).get("c", 0)
        warranty_no = generate_code("BH", count + 1)
        phone = self.e_phone.get().strip()

        # Tìm hoặc tạo khách hàng
        cust = self.db.fetchone("SELECT id FROM customers WHERE phone=?", (phone,)) if phone else None
        if not cust and self.e_cust.get().strip():
            new_count = (self.db.fetchone("SELECT COUNT(*) as c FROM customers") or {}).get("c", 0)
            code = generate_code("KH", new_count + 1)
            cust_id = self.db.execute(
                "INSERT INTO customers (code, full_name, phone) VALUES (?,?,?)",
                (code, self.e_cust.get().strip(), phone))
        else:
            cust_id = cust["id"] if cust else None

        # Tìm sản phẩm
        prod = self.db.fetchone("SELECT id FROM products WHERE name LIKE ?",
                                (f"%{self.e_prod.get().strip()}%",))
        prod_id = prod["id"] if prod else None

        self.db.execute("""
            INSERT INTO warranties (warranty_no,customer_id,product_id,issue_desc,status,technician,repair_cost)
            VALUES (?,?,?,?,?,?,?)""",
            (warranty_no, cust_id, prod_id, self.e_issue.get().strip(),
             "Đang xử lý", self.e_tech.get().strip(),
             parse_currency(self.e_cost.get())))

        messagebox.showinfo("Thành công", f"✅  Tạo phiếu bảo hành {warranty_no} thành công!")
        self.destroy()


class WarrantyUpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, warranty: dict):
        super().__init__(parent)
        self.db       = db
        self.warranty = warranty
        self.title(f"Cập nhật bảo hành  –  {warranty['warranty_no']}")
        self.geometry("520x380")
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        f = ctk.CTkFrame(self, fg_color=COLORS["bg"]); f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text=f"Phiếu: {self.warranty['warranty_no']}",
                     font=(FONT_FAMILY, 14, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        def row(label, widget):
            r = ctk.CTkFrame(f, fg_color="transparent"); r.pack(fill="x", pady=6)
            ctk.CTkLabel(r, text=label, width=165, anchor="w",
                         font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            widget.pack(side="left", fill="x", expand=True)

        self.v_status = ctk.StringVar(value=self.warranty["status"] or "Đang xử lý")
        row("Trạng thái:", ctk.CTkOptionMenu(f, variable=self.v_status,
                                              values=WARRANTY_STATUSES,
                                              height=36, fg_color=COLORS["card2"],
                                              button_color=COLORS["primary"],
                                              font=(FONT_FAMILY, 12)))

        def entry_row(label, val=""):
            e = ctk.CTkEntry(f, height=36, font=(FONT_FAMILY, 12),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"])
            row(label, e); e.insert(0, str(val or "")); return e

        self.e_tech = entry_row("Kỹ thuật viên:", self.warranty["technician"])
        self.e_cost = entry_row("Chi phí:",        self.warranty["repair_cost"])
        self.e_note = entry_row("Ghi chú:",        self.warranty["note"])

        btns = ctk.CTkFrame(f, fg_color="transparent"); btns.pack(pady=(16, 0))
        StyledButton(btns, "💾  Lưu", self._save,   style="success", width=120).pack(side="left")
        StyledButton(btns, "Hủy",     self.destroy, style="danger",  width=100).pack(side="left", padx=8)

    def _save(self):
        status    = self.v_status.get()
        completed = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Hoàn thành" else None
        self.db.execute("""UPDATE warranties SET status=?, technician=?, repair_cost=?, note=?,
                           completed_date=? WHERE id=?""",
                        (status, self.e_tech.get(), parse_currency(self.e_cost.get()),
                         self.e_note.get(), completed, self.warranty["id"]))
        self.destroy()

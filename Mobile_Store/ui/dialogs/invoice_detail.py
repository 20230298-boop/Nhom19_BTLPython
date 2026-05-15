"""
dialogs/invoice_detail.py  –  Xem chi tiết hóa đơn
"""

import customtkinter as ctk
from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency
from ui.widgets import Card, StyledButton, StyledTreeview


class InvoiceDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, invoice: dict):
        super().__init__(parent)
        self.db      = db
        self.invoice = invoice
        self.title(f"Chi tiết hóa đơn  –  {invoice['invoice_no']}")
        self.geometry("720x620")
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        inv   = self.invoice
        cust  = (self.db.fetchone("SELECT * FROM customers WHERE id=?", (inv["customer_id"],))
                 if inv["customer_id"] else None)
        staff = (self.db.fetchone("SELECT full_name FROM users WHERE id=?", (inv["user_id"],))
                 if inv["user_id"] else None)

        header = Card(scroll)
        header.pack(fill="x", pady=(0, 16))
        h = ctk.CTkFrame(header, fg_color="transparent")
        h.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(h, text="HÓA ĐƠN BÁN HÀNG",
                     font=(FONT_FAMILY, 17, "bold"),
                     text_color=COLORS["primary"]).pack(anchor="w")
        ctk.CTkLabel(h,
                     text=f"Số HĐ: {inv['invoice_no']}   |   Ngày: {inv['created_at'][:16]}",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        ctk.CTkLabel(h,
                     text=(f"Khách hàng: {cust['full_name'] if cust else 'Khách lẻ'}   |   "
                           f"Nhân viên: {staff['full_name'] if staff else 'N/A'}"),
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(scroll, text="Chi tiết sản phẩm",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 8))

        tree = StyledTreeview(
            scroll,
            ("name", "qty", "price", "subtotal"),
            ("Sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"),
            [260, 100, 160, 160],
            height=8,
        )
        tree.pack(fill="x", pady=(0, 16))

        for d in self.db.fetchall(
            """SELECT p.name, id.quantity, id.unit_price, id.subtotal
               FROM invoice_details id JOIN products p ON id.product_id=p.id
               WHERE id.invoice_id=?""",
            (inv["id"],),
        ):
            tree.insert_row((d["name"], d["quantity"],
                             format_currency(d["unit_price"]),
                             format_currency(d["subtotal"])))

        summary = Card(scroll)
        summary.pack(fill="x")
        s = ctk.CTkFrame(summary, fg_color="transparent")
        s.pack(fill="x", padx=16, pady=16)

        rows = [
            ("Tổng tiền hàng :",  format_currency(inv["total_amount"])),
            ("Giảm giá :",        format_currency(inv["discount"])),
            ("Thành tiền :",      format_currency(inv["final_amount"])),
            ("Tiền khách đưa :",  format_currency(inv["paid_amount"])),
            ("Tiền thối :",       format_currency((inv["paid_amount"] or 0) - (inv["final_amount"] or 0))),
            ("Hình thức TT :",    inv["payment_method"]),
            ("Trạng thái :",      inv["payment_status"]),
        ]
        for label, val in rows:
            r = ctk.CTkFrame(s, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            ctk.CTkLabel(r, text=val, font=(FONT_FAMILY, 12, "bold"),
                         text_color=COLORS["text"]).pack(side="right")

        StyledButton(scroll, "Đóng", self.destroy, style="dark", width=100).pack(pady=16)

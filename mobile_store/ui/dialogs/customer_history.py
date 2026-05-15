"""
dialogs/customer_history.py  –  Lịch sử mua hàng của khách
"""

import customtkinter as ctk
from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency
from ui.widgets import Card, StyledButton, StyledTreeview


class CustomerHistoryDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, customer: dict):
        super().__init__(parent)
        self.db       = db
        self.customer = customer
        self.title(f"Lịch sử mua hàng  –  {customer['full_name']}")
        self.geometry("720x520")
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        # Info banner
        info = Card(self)
        info.pack(fill="x", padx=20, pady=(20, 10))
        c = self.customer
        ctk.CTkLabel(
            info,
            text=(f"👤  {c['full_name']}   |   📞 {c['phone'] or 'N/A'}   |   "
                  f"💰 Tổng mua: {format_currency(c['total_spent'])}   |   "
                  f"⭐ Điểm tích lũy: {c['loyalty_pts'] or 0}"),
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text"],
        ).pack(pady=12, padx=16, anchor="w")

        # Hóa đơn
        ctk.CTkLabel(self, text="Danh sách hóa đơn",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(0, 6))

        tree = StyledTreeview(
            self,
            ("invoice_no", "total", "discount", "final", "method", "date"),
            ("Số HĐ", "Tổng tiền", "Giảm giá", "Thành tiền", "Thanh toán", "Ngày"),
            [120, 130, 110, 130, 130, 140],
            height=12,
        )
        tree.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        for r in self.db.fetchall(
            """SELECT invoice_no, total_amount, discount, final_amount,
                      payment_method, created_at
               FROM invoices WHERE customer_id=? ORDER BY created_at DESC""",
            (self.customer["id"],),
        ):
            tree.insert_row((
                r["invoice_no"],
                format_currency(r["total_amount"]),
                format_currency(r["discount"]),
                format_currency(r["final_amount"]),
                r["payment_method"],
                r["created_at"][:16] if r["created_at"] else "",
            ))

        StyledButton(self, "Đóng", self.destroy, style="dark", width=100).pack(pady=(0, 16))

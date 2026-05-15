"""
pages/invoices.py  –  Quản lý hóa đơn bán hàng
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency, first_day_of_month, today_str
from ui.widgets import StyledButton, StyledTreeview


class InvoicesPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db   = db
        self.user = user
        self._build()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=60)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        t = ctk.CTkFrame(bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=10)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(t, textvariable=self.search_var,
                     placeholder_text="🔍  Tìm theo số HĐ, khách hàng...",
                     width=260, height=38,
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     font=(FONT_FAMILY, 12), text_color=COLORS["text"]).pack(side="left")
        self.search_var.trace("w", lambda *_: self._load())

        for label, attr, default in [("Từ:", "date_from", first_day_of_month()),
                                      ("Đến:", "date_to", today_str())]:
            ctk.CTkLabel(t, text=label, font=(FONT_FAMILY, 11),
                         text_color=COLORS["text_muted"]).pack(side="left", padx=(10, 4))
            e = ctk.CTkEntry(t, width=100, height=38, font=(FONT_FAMILY, 11),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"])
            e.pack(side="left")
            e.insert(0, default)
            setattr(self, attr, e)

        StyledButton(t, "Lọc",     self._load,        style="primary", icon="🔍", width=80).pack(side="left", padx=8)
        StyledButton(t, "Chi tiết",self._view_detail,  style="info",    icon="👁").pack(side="left", padx=4)
        if self.user["role"] == "admin":
            StyledButton(t, "Xóa HĐ", self._delete, style="danger", icon="🗑").pack(side="left", padx=4)

        sf = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=44)
        sf.pack(fill="x")
        sf.pack_propagate(False)
        self.stats_lbl = ctk.CTkLabel(sf, text="", font=(FONT_FAMILY, 12),
                                       text_color=COLORS["text"])
        self.stats_lbl.pack(expand=True)

        cols   = ("invoice_no","customer","user","total","discount","final","method","status","date")
        heads  = ("Số HĐ","Khách hàng","Nhân viên","Tổng tiền","Giảm giá","Thành tiền","Thanh toán","Trạng thái","Ngày tạo")
        widths = [110, 160, 130, 130, 100, 130, 110, 110, 130]
        self.tree = StyledTreeview(self, cols, heads, widths, height=24)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.tree.tree.bind("<Double-1>", lambda _: self._view_detail())
        self._load()

    def _load(self):
        self.tree.clear()
        kw     = self.search_var.get().strip()
        d_from = self.date_from.get().strip()
        d_to   = self.date_to.get().strip()
        q = """SELECT i.*, COALESCE(c.full_name,'Khách lẻ') as cust_name, u.full_name as user_name
               FROM invoices i
               LEFT JOIN customers c ON i.customer_id=c.id
               LEFT JOIN users u ON i.user_id=u.id WHERE 1=1"""
        params = []
        if kw:
            q += " AND (i.invoice_no LIKE ? OR c.full_name LIKE ?)"
            params += [f"%{kw}%"] * 2
        if d_from:
            q += " AND DATE(i.created_at)>=?"; params.append(d_from)
        if d_to:
            q += " AND DATE(i.created_at)<=?"; params.append(d_to)
        q += " ORDER BY i.created_at DESC LIMIT 500"
        rows = self.db.fetchall(q, params)
        total_rev = sum(r["final_amount"] or 0 for r in rows)
        for r in rows:
            self.tree.insert_row((
                r["invoice_no"], r["cust_name"], r["user_name"] or "",
                format_currency(r["total_amount"]), format_currency(r["discount"]),
                format_currency(r["final_amount"]), r["payment_method"],
                r["payment_status"],
                r["created_at"][:16] if r["created_at"] else "",
            ))
        self.stats_lbl.configure(
            text=f"📊  Tổng {len(rows)} hóa đơn  |  Doanh thu: {format_currency(total_rev)}")

    def _view_detail(self):
        sel = self.tree.get_selected()
        if not sel:
            return
        invoice = self.db.fetchone("SELECT * FROM invoices WHERE invoice_no=?", (sel[0],))
        if invoice:
            from ui.dialogs.invoice_detail import InvoiceDetailDialog
            self.wait_window(InvoiceDetailDialog(self, self.db, invoice))

    def _delete(self):
        sel = self.tree.get_selected()
        if not sel:
            return
        if messagebox.askyesno("Xác nhận", f"Xóa hóa đơn {sel[0]}? Thao tác không thể hoàn tác!"):
            inv = self.db.fetchone("SELECT id FROM invoices WHERE invoice_no=?", (sel[0],))
            if inv:
                for d in self.db.fetchall(
                    "SELECT product_id, quantity FROM invoice_details WHERE invoice_id=?", (inv["id"],)):
                    self.db.execute("UPDATE products SET quantity=quantity+? WHERE id=?",
                                    (d["quantity"], d["product_id"]))
                self.db.execute("DELETE FROM invoices WHERE id=?", (inv["id"],))
                self._load()

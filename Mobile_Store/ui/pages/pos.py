"""
pages/pos.py
─────────────────────────────────────────
Trang bán hàng (Point of Sale): tìm hàng, giỏ hàng, thanh toán.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from utils.constants import COLORS, FONT_FAMILY, PAYMENT_METHODS
from utils.helpers import format_currency, parse_currency, generate_code
from ui.widgets import StyledButton, Card, StyledTreeview


class POSPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db   = db
        self.user = user
        self.cart: list = []
        self.selected_customer: dict | None = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_product_panel()
        self._build_cart_panel()


    def _build_product_panel(self):
        left = Card(self)
        left.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        sf = ctk.CTkFrame(left, fg_color="transparent")
        sf.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        sf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(sf, text="🔍  Tìm sản phẩm",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, columnspan=2,
                                                     sticky="w", pady=(0, 6))

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(sf, textvariable=self.search_var,
                     placeholder_text="Nhập tên, mã sản phẩm...",
                     height=40, font=(FONT_FAMILY, 12),
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     text_color=COLORS["text"]).grid(row=1, column=0, sticky="ew")
        self.search_var.trace("w", lambda *_: self._search_products())

        cats = ["Tất cả"] + [c["name"] for c in
                              self.db.fetchall("SELECT name FROM categories ORDER BY name")]
        self.cat_var = ctk.StringVar(value="Tất cả")
        ctk.CTkOptionMenu(sf, variable=self.cat_var, values=cats,
                          command=lambda _: self._search_products(),
                          fg_color=COLORS["card2"], button_color=COLORS["primary"],
                          width=130, height=40,
                          font=(FONT_FAMILY, 11)).grid(row=1, column=1, padx=(8, 0))

        self.product_tree = StyledTreeview(
            left,
            ("code", "name", "price", "qty"),
            ("Mã SP", "Tên sản phẩm", "Giá bán", "Tồn kho"),
            [90, 250, 130, 80], height=16,
        )
        self.product_tree.grid(row=2, column=0, padx=16, pady=8, sticky="nsew")
        self.product_tree.tree.bind("<Double-1>", lambda _: self._add_to_cart())

        StyledButton(left, "Thêm vào giỏ", self._add_to_cart,
                     style="primary", icon="➕", width=200).grid(
            row=3, column=0, padx=16, pady=(0, 16))

        self._search_products()


    def _build_cart_panel(self):
        right = Card(self)
        right.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="🛒  Giỏ hàng",
                     font=(FONT_FAMILY, 14, "bold"),
                     text_color=COLORS["text"]).grid(
            row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        cf = ctk.CTkFrame(right, fg_color=COLORS["card2"], corner_radius=8)
        cf.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")
        ci = ctk.CTkFrame(cf, fg_color="transparent")
        ci.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(ci, text="👥  Khách:",
                     font=(FONT_FAMILY, 11),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.cust_label = ctk.CTkLabel(ci, text="Khách lẻ",
                                        font=(FONT_FAMILY, 11, "bold"),
                                        text_color=COLORS["text"])
        self.cust_label.pack(side="left", padx=8)
        StyledButton(ci, "Chọn KH", self._select_customer,
                     style="info", icon="🔍", width=100, height=30).pack(side="right")

        self.cart_tree = StyledTreeview(
            right,
            ("name", "qty", "price", "subtotal"),
            ("Sản phẩm", "SL", "Đơn giá", "Thành tiền"),
            [180, 50, 110, 110], height=10,
        )
        self.cart_tree.grid(row=3, column=0, padx=16, sticky="nsew")

        cb = ctk.CTkFrame(right, fg_color="transparent")
        cb.grid(row=4, column=0, padx=16, pady=8, sticky="ew")
        StyledButton(cb, "Xóa dòng",   self._remove_from_cart, style="danger",  icon="🗑",  width=110).pack(side="left")
        StyledButton(cb, "Xóa tất cả", self._clear_cart,       style="warning", icon="🧹", width=110).pack(side="left", padx=6)

        self._build_payment_summary(right)

        ctk.CTkButton(
            right, text="💳  THANH TOÁN",
            command=self._checkout,
            height=50, font=(FONT_FAMILY, 15, "bold"),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_dark"],
            corner_radius=8,
        ).grid(row=6, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _build_payment_summary(self, parent):
        pf = ctk.CTkFrame(parent, fg_color=COLORS["dark3"], corner_radius=8)
        pf.grid(row=5, column=0, padx=16, pady=(0, 8), sticky="ew")
        pi = ctk.CTkFrame(pf, fg_color="transparent")
        pi.pack(fill="x", padx=12, pady=10)

        def lbl_row(f, text, attr, bold=False):
            r = ctk.CTkFrame(f, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=text,
                         font=(FONT_FAMILY, 12 if not bold else 13),
                         text_color=COLORS["text_muted"]).pack(side="left")
            lbl = ctk.CTkLabel(r, text="0 ₫",
                               font=(FONT_FAMILY, 12 if not bold else 13, "bold"),
                               text_color=COLORS["primary"] if bold else COLORS["text"])
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        lbl_row(pi, "Tổng tiền hàng:", "total_lbl")

        dr = ctk.CTkFrame(pi, fg_color="transparent")
        dr.pack(fill="x", pady=2)
        ctk.CTkLabel(dr, text="Giảm giá:", font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.discount_entry = ctk.CTkEntry(dr, width=90, height=28,
                                            font=(FONT_FAMILY, 11),
                                            fg_color=COLORS["card2"],
                                            text_color=COLORS["text"],
                                            border_color=COLORS["border"])
        self.discount_entry.pack(side="right", padx=(0, 4))
        self.discount_entry.insert(0, "0")
        self.disc_type_var = ctk.StringVar(value="₫")
        ctk.CTkOptionMenu(dr, variable=self.disc_type_var, values=["₫", "%"],
                          width=55, height=28,
                          fg_color=COLORS["card2"],
                          button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 11)).pack(side="right")

        lbl_row(pi, "Thành tiền:", "final_lbl", bold=True)

        pr = ctk.CTkFrame(pi, fg_color="transparent")
        pr.pack(fill="x", pady=2)
        ctk.CTkLabel(pr, text="Tiền khách đưa:", font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.paid_entry = ctk.CTkEntry(pr, width=130, height=28,
                                        font=(FONT_FAMILY, 11),
                                        fg_color=COLORS["card2"],
                                        text_color=COLORS["text"],
                                        border_color=COLORS["border"])
        self.paid_entry.pack(side="right")

        mr = ctk.CTkFrame(pi, fg_color="transparent")
        mr.pack(fill="x", pady=2)
        ctk.CTkLabel(mr, text="Hình thức:", font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.pay_method_var = ctk.StringVar(value="Tiền mặt")
        ctk.CTkOptionMenu(mr, variable=self.pay_method_var,
                          values=PAYMENT_METHODS,
                          width=160, height=28,
                          fg_color=COLORS["card2"],
                          button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 11)).pack(side="right")

        self.discount_entry.bind("<KeyRelease>", lambda _: self._update_totals())


    def _search_products(self):
        self.product_tree.clear()
        kw  = self.search_var.get().strip()
        cat = self.cat_var.get()
        q   = """SELECT p.code, p.name, p.selling_price, p.quantity
                 FROM products p LEFT JOIN categories c ON p.category_id=c.id
                 WHERE p.is_active=1 AND p.quantity>0"""
        params = []
        if kw:
            q += " AND (p.name LIKE ? OR p.code LIKE ?)"
            params += [f"%{kw}%", f"%{kw}%"]
        if cat != "Tất cả":
            q += " AND c.name=?"
            params.append(cat)
        q += " ORDER BY p.name LIMIT 100"
        for r in self.db.fetchall(q, params):
            self.product_tree.insert_row((r["code"], r["name"],
                                          format_currency(r["selling_price"]),
                                          r["quantity"]))

    def _add_to_cart(self):
        sel = self.product_tree.get_selected()
        if not sel:
            messagebox.showwarning("Thông báo", "Vui lòng chọn sản phẩm!")
            return
        product = self.db.fetchone("SELECT * FROM products WHERE code=?", (sel[0],))
        if not product:
            return
        for item in self.cart:
            if item["id"] == product["id"]:
                if item["qty"] >= product["quantity"]:
                    messagebox.showwarning("Thông báo", "Không đủ tồn kho!")
                    return
                item["qty"] += 1
                self._refresh_cart()
                return
        self.cart.append({
            "id":    product["id"],
            "name":  product["name"],
            "price": product["selling_price"],
            "qty":   1,
            "stock": product["quantity"],
        })
        self._refresh_cart()

    def _remove_from_cart(self):
        sel = self.cart_tree.get_selected()
        if sel:
            self.cart = [i for i in self.cart if i["name"] != sel[0]]
            self._refresh_cart()

    def _clear_cart(self):
        if self.cart and messagebox.askyesno("Xác nhận", "Xóa toàn bộ giỏ hàng?"):
            self.cart = []
            self._refresh_cart()

    def _refresh_cart(self):
        self.cart_tree.clear()
        for item in self.cart:
            sub = item["price"] * item["qty"]
            self.cart_tree.insert_row((item["name"], item["qty"],
                                       format_currency(item["price"]),
                                       format_currency(sub)))
        self._update_totals()

    def _update_totals(self):
        total = sum(i["price"] * i["qty"] for i in self.cart)
        self.total_lbl.configure(text=format_currency(total))
        try:
            d_val  = float(self.discount_entry.get() or 0)
            d_type = self.disc_type_var.get()
            disc   = total * d_val / 100 if d_type == "%" else d_val
        except Exception:
            disc = 0
        self.final_lbl.configure(text=format_currency(max(0, total - disc)))

    def _select_customer(self):
        from ui.dialogs.customer_select import CustomerSelectDialog
        dlg = CustomerSelectDialog(self, self.db)
        self.wait_window(dlg)
        if dlg.result:
            self.selected_customer = dlg.result
            name  = dlg.result["full_name"]
            phone = dlg.result["phone"] or ""
            self.cust_label.configure(text=f"{name} ({phone})")

    def _checkout(self):
        if not self.cart:
            messagebox.showwarning("Thông báo", "Giỏ hàng trống!")
            return

        total = sum(i["price"] * i["qty"] for i in self.cart)
        try:
            d_val = float(self.discount_entry.get() or 0)
            disc  = total * d_val / 100 if self.disc_type_var.get() == "%" else d_val
        except Exception:
            disc = 0
        final = max(0, total - disc)

        paid_str = self.paid_entry.get().strip()
        paid     = parse_currency(paid_str) if paid_str else final

        if paid < final:
            messagebox.showwarning("Cảnh báo",
                f"Tiền khách đưa ({format_currency(paid)}) "
                f"ít hơn thành tiền ({format_currency(final)})!")
            return

        count      = (self.db.fetchone("SELECT COUNT(*) as c FROM invoices") or {}).get("c", 0)
        invoice_no = generate_code("HD", count + 1)

        conn = self.db.get_connection()
        try:
            c = conn.cursor()
            c.execute("""INSERT INTO invoices
                (invoice_no,customer_id,user_id,total_amount,discount,discount_type,
                 final_amount,paid_amount,payment_method,payment_status)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (invoice_no,
                 self.selected_customer["id"] if self.selected_customer else None,
                 self.user["id"], total, disc, self.disc_type_var.get(),
                 final, paid, self.pay_method_var.get(), "Đã thanh toán"))
            invoice_id = c.lastrowid
            for item in self.cart:
                sub = item["price"] * item["qty"]
                c.execute("""INSERT INTO invoice_details
                    (invoice_id,product_id,quantity,unit_price,subtotal) VALUES (?,?,?,?,?)""",
                    (invoice_id, item["id"], item["qty"], item["price"], sub))
                c.execute("UPDATE products SET quantity=quantity-? WHERE id=?",
                          (item["qty"], item["id"]))
            if self.selected_customer:
                c.execute("""UPDATE customers SET total_spent=total_spent+?,
                             loyalty_pts=loyalty_pts+? WHERE id=?""",
                          (final, int(final // 100_000), self.selected_customer["id"]))
            conn.commit()
        finally:
            conn.close()

        self.db.log_activity(self.user["id"], "CREATE_INVOICE", "POS",
                             f"Tạo hóa đơn {invoice_no}, giá trị {format_currency(final)}")

        messagebox.showinfo("Thanh toán thành công",
            f"✅  Tạo hóa đơn thành công!\n\n"
            f"Số HĐ      : {invoice_no}\n"
            f"Thành tiền : {format_currency(final)}\n"
            f"Tiền đưa   : {format_currency(paid)}\n"
            f"Tiền thối  : {format_currency(paid - final)}")

        self.cart = []
        self.selected_customer = None
        self.cust_label.configure(text="Khách lẻ")
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, "0")
        self.paid_entry.delete(0, "end")
        self._refresh_cart()
        self._search_products()

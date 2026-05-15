"""
dialogs/purchase_dialog.py  –  Tạo phiếu nhập hàng & xem chi tiết
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY, DIALOG_SIZE_XL
from utils.helpers import format_currency, parse_currency, generate_code
from ui.widgets import StyledButton, Card, StyledTreeview


class PurchaseOrderDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, user):
        super().__init__(parent)
        self.db    = db
        self.user  = user
        self.items: list = []
        self.title("Tạo phiếu nhập hàng")
        self.geometry(DIALOG_SIZE_XL)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_product_panel()
        self._build_order_panel()


    def _build_product_panel(self):
        left = Card(self)
        left.grid(row=0, column=0, padx=(16, 8), pady=16, sticky="nsew")
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Chọn sản phẩm nhập",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.search_e = ctk.CTkEntry(left, placeholder_text="🔍  Tìm sản phẩm...",
                                      height=38, font=(FONT_FAMILY, 12),
                                      fg_color=COLORS["card2"], border_color=COLORS["border"],
                                      text_color=COLORS["text"])
        self.search_e.grid(row=0, column=0, padx=16, pady=(54, 8), sticky="ew")
        self.search_e.bind("<KeyRelease>", lambda _: self._search())

        self.prod_tree = StyledTreeview(left, ("code", "name", "price", "qty"),
                                        ("Mã", "Tên sản phẩm", "Giá nhập", "Tồn"),
                                        [80, 210, 120, 70], height=14)
        self.prod_tree.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")
        self._search()

        qf = ctk.CTkFrame(left, fg_color="transparent")
        qf.grid(row=2, column=0, padx=16, pady=8, sticky="ew")
        for text, attr, w in [("Số lượng:", "qty_e", 80), ("Giá nhập:", "price_e", 130)]:
            ctk.CTkLabel(qf, text=text, font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            e = ctk.CTkEntry(qf, width=w, height=36, font=(FONT_FAMILY, 12),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"])
            e.pack(side="left", padx=6)
            setattr(self, attr, e)
        self.qty_e.insert(0, "1")
        StyledButton(qf, "Thêm", self._add_item, style="primary", icon="➕", width=90).pack(side="right")


    def _build_order_panel(self):
        right = Card(self)
        right.grid(row=0, column=1, padx=(0, 16), pady=16, sticky="nsew")
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Phiếu nhập hàng",
                     font=(FONT_FAMILY, 14, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        sups = self.db.fetchall("SELECT id, name FROM suppliers WHERE is_active=1")
        self._sup_ids = {s["name"]: s["id"] for s in sups}
        self.v_sup    = ctk.StringVar(value=sups[0]["name"] if sups else "")
        sf = ctk.CTkFrame(right, fg_color="transparent")
        sf.grid(row=1, column=0, padx=16, sticky="ew")
        ctk.CTkLabel(sf, text="Nhà cung cấp:", font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkOptionMenu(sf, variable=self.v_sup, values=[s["name"] for s in sups],
                          width=200, height=36, fg_color=COLORS["card2"],
                          button_color=COLORS["primary"],
                          font=(FONT_FAMILY, 11)).pack(side="right")

        self.items_tree = StyledTreeview(right,
                                          ("name", "qty", "price", "subtotal"),
                                          ("Sản phẩm", "SL", "Đơn giá", "T.tiền"),
                                          [170, 50, 110, 110], height=10)
        self.items_tree.grid(row=2, column=0, padx=16, pady=(12, 8), sticky="nsew")

        StyledButton(right, "Xóa dòng", self._remove_item, style="danger", icon="🗑", width=120).grid(
            row=3, column=0, padx=16, pady=4, sticky="w")

        self.total_lbl = ctk.CTkLabel(right, text="Tổng:  0 ₫",
                                       font=(FONT_FAMILY, 16, "bold"),
                                       text_color=COLORS["primary"])
        self.total_lbl.grid(row=4, column=0, padx=16, pady=8, sticky="e")

        ctk.CTkLabel(right, text="Ghi chú:", font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).grid(row=5, column=0, padx=16, sticky="w")
        self.note_e = ctk.CTkEntry(right, height=36, font=(FONT_FAMILY, 12),
                                    fg_color=COLORS["card2"], border_color=COLORS["border"],
                                    text_color=COLORS["text"])
        self.note_e.grid(row=6, column=0, padx=16, pady=(4, 8), sticky="ew")

        ctk.CTkButton(right, text="💾  LƯU PHIẾU NHẬP",
                      command=self._save,
                      height=44, font=(FONT_FAMILY, 13, "bold"),
                      fg_color=COLORS["secondary"], hover_color=COLORS["secondary_dark"],
                      corner_radius=8).grid(row=7, column=0, padx=16, pady=(0, 16), sticky="ew")


    def _search(self):
        self.prod_tree.clear()
        kw = self.search_e.get().strip()
        q  = "SELECT code, name, import_price, quantity FROM products WHERE is_active=1"
        p  = []
        if kw:
            q += " AND (name LIKE ? OR code LIKE ?)"; p = [f"%{kw}%"] * 2
        q += " ORDER BY name LIMIT 60"
        for r in self.db.fetchall(q, p):
            self.prod_tree.insert_row((r["code"], r["name"],
                                       format_currency(r["import_price"]), r["quantity"]))

    def _add_item(self):
        sel = self.prod_tree.get_selected()
        if not sel: return
        prod = self.db.fetchone("SELECT * FROM products WHERE code=?", (sel[0],))
        if not prod: return
        try:
            qty   = int(self.qty_e.get() or 1)
            price = parse_currency(self.price_e.get()) if self.price_e.get().strip() else prod["import_price"]
        except Exception:
            qty, price = 1, prod["import_price"]
        for item in self.items:
            if item["id"] == prod["id"]:
                item["qty"] += qty; item["price"] = price
                self._refresh_items(); return
        self.items.append({"id": prod["id"], "name": prod["name"], "qty": qty, "price": price})
        self._refresh_items()
        self.price_e.delete(0, "end")

    def _remove_item(self):
        sel = self.items_tree.get_selected()
        if sel:
            self.items = [i for i in self.items if i["name"] != sel[0]]
            self._refresh_items()

    def _refresh_items(self):
        self.items_tree.clear()
        total = 0
        for item in self.items:
            sub = item["qty"] * item["price"]; total += sub
            self.items_tree.insert_row((item["name"], item["qty"],
                                        format_currency(item["price"]),
                                        format_currency(sub)))
        self.total_lbl.configure(text=f"Tổng:  {format_currency(total)}")

    def _save(self):
        if not self.items:
            messagebox.showwarning("Thông báo", "Chưa có sản phẩm trong phiếu!"); return
        total     = sum(i["qty"] * i["price"] for i in self.items)
        count     = (self.db.fetchone("SELECT COUNT(*) as c FROM purchase_orders") or {}).get("c", 0)
        order_no  = generate_code("PN", count + 1)
        sup_id    = self._sup_ids.get(self.v_sup.get())
        conn = self.db.get_connection()
        try:
            c = conn.cursor()
            c.execute("""INSERT INTO purchase_orders (order_no,supplier_id,user_id,total_amount,status,note)
                VALUES (?,?,?,?,?,?)""",
                (order_no, sup_id, self.user["id"], total, "Đã nhập", self.note_e.get()))
            oid = c.lastrowid
            for item in self.items:
                sub = item["qty"] * item["price"]
                c.execute("""INSERT INTO purchase_details (order_id,product_id,quantity,unit_price,subtotal)
                    VALUES (?,?,?,?,?)""", (oid, item["id"], item["qty"], item["price"], sub))
                c.execute("UPDATE products SET quantity=quantity+?, import_price=? WHERE id=?",
                          (item["qty"], item["price"], item["id"]))
            conn.commit()
        finally:
            conn.close()
        messagebox.showinfo("Thành công",
                            f"✅  Tạo phiếu nhập {order_no} thành công!\n"
                            f"Tổng tiền: {format_currency(total)}")
        self.destroy()



class PurchaseDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, order: dict):
        super().__init__(parent)
        self.db    = db
        self.order = order
        self.title(f"Chi tiết phiếu nhập  –  {order['order_no']}")
        self.geometry("680x520")
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        o   = self.order
        sup = (self.db.fetchone("SELECT name FROM suppliers WHERE id=?", (o["supplier_id"],))
               if o["supplier_id"] else None)

        info = Card(self)
        info.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(info,
                     text=(f"📦  Phiếu: {o['order_no']}   |   "
                           f"NCC: {sup['name'] if sup else 'N/A'}   |   "
                           f"Tổng: {format_currency(o['total_amount'])}   |   "
                           f"{o['created_at'][:16]}"),
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text"]).pack(pady=12, padx=16, anchor="w")

        tree = StyledTreeview(self,
                               ("name", "qty", "price", "subtotal"),
                               ("Sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"),
                               [260, 100, 160, 160], height=12)
        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for d in self.db.fetchall(
            """SELECT p.name, pd.quantity, pd.unit_price, pd.subtotal
               FROM purchase_details pd JOIN products p ON pd.product_id=p.id
               WHERE pd.order_id=?""", (o["id"],)):
            tree.insert_row((d["name"], d["quantity"],
                             format_currency(d["unit_price"]),
                             format_currency(d["subtotal"])))

        StyledButton(self, "Đóng", self.destroy, style="dark", width=100).pack(pady=(0, 16))

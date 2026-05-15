"""
dialogs/product_dialog.py  –  Dialog thêm / sửa sản phẩm
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.constants import COLORS, FONT_FAMILY, DIALOG_SIZE_LG
from utils.helpers import parse_currency
from ui.widgets import StyledButton


class ProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, product=None):
        super().__init__(parent)
        self.db      = db
        self.product = product
        self.title("Thêm sản phẩm" if not product else "Sửa sản phẩm")
        self.geometry(DIALOG_SIZE_LG)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Thông tin sản phẩm",
                     font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        # ── Helpers ──────────────────────────────────────────────
        def entry_row(label, placeholder=""):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=label, width=165, anchor="w",
                         font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            e = ctk.CTkEntry(f, height=36, font=(FONT_FAMILY, 12),
                              fg_color=COLORS["card2"], border_color=COLORS["border"],
                              text_color=COLORS["text"],
                              placeholder_text=placeholder)
            e.pack(side="left", fill="x", expand=True)
            return e

        def option_row(label, var, values):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=label, width=165, anchor="w",
                         font=(FONT_FAMILY, 12),
                         text_color=COLORS["text_muted"]).pack(side="left")
            ctk.CTkOptionMenu(f, variable=var, values=values,
                              height=36, fg_color=COLORS["card2"],
                              button_color=COLORS["primary"],
                              font=(FONT_FAMILY, 12)).pack(side="left", fill="x", expand=True)

        # ── Fields ───────────────────────────────────────────────
        self.e_code    = entry_row("Mã sản phẩm *",   "VD: SP001")
        self.e_name    = entry_row("Tên sản phẩm *")
        self.e_brand   = entry_row("Thương hiệu")
        self.e_model   = entry_row("Model")
        self.e_color   = entry_row("Màu sắc")
        self.e_storage = entry_row("Bộ nhớ",          "VD: 256GB")
        self.e_ram     = entry_row("RAM",              "VD: 8GB")

        # Category dropdown
        cats = self.db.fetchall("SELECT id, name FROM categories ORDER BY name")
        self._cat_ids   = {c["name"]: c["id"] for c in cats}
        self.v_cat      = ctk.StringVar(value=cats[0]["name"] if cats else "")
        option_row("Danh mục", self.v_cat, [c["name"] for c in cats])

        # Supplier dropdown
        sups = self.db.fetchall("SELECT id, name FROM suppliers WHERE is_active=1")
        self._sup_ids   = {s["name"]: s["id"] for s in sups}
        self.v_sup      = ctk.StringVar(value=sups[0]["name"] if sups else "")
        option_row("Nhà cung cấp", self.v_sup, [s["name"] for s in sups])

        self.e_import  = entry_row("Giá nhập *",       "0")
        self.e_sell    = entry_row("Giá bán *",        "0")
        self.e_qty     = entry_row("Số lượng tồn",    "0")
        self.e_minqty  = entry_row("Tồn tối thiểu",   "5")
        self.e_wmonths = entry_row("Bảo hành (tháng)","12")

        # Description
        f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text="Mô tả", width=165, anchor="w",
                     font=(FONT_FAMILY, 12),
                     text_color=COLORS["text_muted"]).pack(side="left", anchor="n")
        self.e_desc = ctk.CTkTextbox(f, height=70, font=(FONT_FAMILY, 12),
                                      fg_color=COLORS["card2"], border_color=COLORS["border"],
                                      text_color=COLORS["text"])
        self.e_desc.pack(side="left", fill="x", expand=True)

        # Fill existing data
        if self.product:
            self._fill()

        # Buttons
        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=(16, 0))
        StyledButton(btns, "💾  Lưu lại", self._save,   style="success", width=140, height=42).pack(side="left")
        StyledButton(btns, "❌  Hủy",     self.destroy, style="danger",  width=100, height=42).pack(side="left", padx=8)

    def _fill(self):
        p = self.product
        pairs = [(self.e_code, p["code"]), (self.e_name, p["name"]),
                 (self.e_brand, p["brand"]), (self.e_model, p["model"]),
                 (self.e_color, p["color"]), (self.e_storage, p["storage"]),
                 (self.e_ram, p["ram"]), (self.e_import, p["import_price"]),
                 (self.e_sell, p["selling_price"]), (self.e_qty, p["quantity"]),
                 (self.e_minqty, p["min_quantity"]), (self.e_wmonths, p["warranty_months"])]
        for widget, val in pairs:
            widget.delete(0, "end"); widget.insert(0, str(val or ""))
        if p.get("description"):
            self.e_desc.insert("1.0", p["description"])
        cat = self.db.fetchone("SELECT name FROM categories WHERE id=?", (p.get("category_id"),))
        if cat: self.v_cat.set(cat["name"])
        sup = self.db.fetchone("SELECT name FROM suppliers WHERE id=?", (p.get("supplier_id"),))
        if sup: self.v_sup.set(sup["name"])

    def _save(self):
        code = self.e_code.get().strip()
        name = self.e_name.get().strip()
        if not code or not name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập mã và tên sản phẩm!"); return

        data = dict(
            code=code, name=name,
            brand=self.e_brand.get().strip(), model=self.e_model.get().strip(),
            color=self.e_color.get().strip(), storage=self.e_storage.get().strip(),
            ram=self.e_ram.get().strip(),
            category_id=self._cat_ids.get(self.v_cat.get()),
            supplier_id=self._sup_ids.get(self.v_sup.get()),
            import_price=parse_currency(self.e_import.get()),
            selling_price=parse_currency(self.e_sell.get()),
            quantity=int(self.e_qty.get() or 0),
            min_quantity=int(self.e_minqty.get() or 5),
            warranty_months=int(self.e_wmonths.get() or 12),
            description=self.e_desc.get("1.0", "end").strip(),
        )
        if self.product:
            sets = ", ".join(f"{k}=?" for k in data if k != "code")
            vals = [v for k, v in data.items() if k != "code"] + [self.product["id"]]
            self.db.execute(
                f"UPDATE products SET {sets}, updated_at=datetime('now','localtime') WHERE id=?", vals)
        else:
            cols = ", ".join(data.keys())
            phs  = ", ".join("?" * len(data))
            self.db.execute(f"INSERT INTO products ({cols}) VALUES ({phs})", list(data.values()))
        self.destroy()

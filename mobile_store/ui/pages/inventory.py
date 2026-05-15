"""
pages/inventory.py  –  Nhập hàng / quản lý tồn kho
"""

import customtkinter as ctk
from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency
from ui.widgets import StyledButton, StyledTreeview


class InventoryPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db = db; self.user = user; self._build()

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=60)
        bar.pack(fill="x"); bar.pack_propagate(False)
        t = ctk.CTkFrame(bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=10)

        StyledButton(t, "Tạo phiếu nhập", self._create,      style="success", icon="➕", width=160).pack(side="left")
        StyledButton(t, "Chi tiết",        self._view_detail, style="info",    icon="👁").pack(side="left", padx=8)

        low = (self.db.fetchone(
            "SELECT COUNT(*) as c FROM products WHERE quantity<=min_quantity AND is_active=1") or {}).get("c", 0)
        if low > 0:
            ctk.CTkLabel(t, text=f"⚠️  {low} sản phẩm sắp hết hàng!",
                         font=(FONT_FAMILY, 12, "bold"),
                         text_color=COLORS["danger"]).pack(side="right", padx=20)

        # Bảng phiếu nhập
        cols   = ("order_no","supplier","total","status","user","date")
        heads  = ("Số phiếu","Nhà cung cấp","Tổng tiền","Trạng thái","Người nhập","Ngày nhập")
        widths = [120, 200, 140, 120, 150, 130]
        self.tree = StyledTreeview(self, cols, heads, widths, height=14)
        self.tree.pack(fill="x", padx=20, pady=(10, 0))
        self.tree.tree.bind("<Double-1>", lambda _: self._view_detail())

        # Bảng hàng sắp hết
        ctk.CTkLabel(self, text="⚠️  Danh sách sản phẩm cần nhập thêm",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["warning"]).pack(anchor="w", padx=20, pady=(16, 6))

        cols2  = ("code","name","qty","min","diff")
        heads2 = ("Mã SP","Tên sản phẩm","Tồn kho","Tối thiểu","Cần nhập thêm")
        tree2  = StyledTreeview(self, cols2, heads2, [90, 240, 80, 80, 110], height=8)
        tree2.pack(fill="x", padx=20, pady=(0, 20))

        for r in self.db.fetchall("""
            SELECT code, name, quantity, min_quantity FROM products
            WHERE quantity<=min_quantity AND is_active=1 ORDER BY quantity ASC"""):
            tree2.insert_row((r["code"], r["name"], r["quantity"], r["min_quantity"],
                              max(0, r["min_quantity"] * 3 - r["quantity"])),
                             tags=["low_stock"] if r["quantity"] == 0 else [])
        self._load()

    def _load(self):
        self.tree.clear()
        for r in self.db.fetchall("""
            SELECT po.*, s.name as sup_name, u.full_name as user_name
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id=s.id
            LEFT JOIN users u ON po.user_id=u.id
            ORDER BY po.created_at DESC"""):
            self.tree.insert_row((
                r["order_no"], r["sup_name"] or "",
                format_currency(r["total_amount"]), r["status"],
                r["user_name"] or "",
                r["created_at"][:16] if r["created_at"] else "",
            ))

    def _create(self):
        from ui.dialogs.purchase_dialog import PurchaseOrderDialog
        dlg = PurchaseOrderDialog(self, self.db, self.user)
        self.wait_window(dlg); self._load()

    def _view_detail(self):
        sel = self.tree.get_selected()
        if not sel: return
        order = self.db.fetchone("SELECT * FROM purchase_orders WHERE order_no=?", (sel[0],))
        if order:
            from ui.dialogs.purchase_dialog import PurchaseDetailDialog
            self.wait_window(PurchaseDetailDialog(self, self.db, order))

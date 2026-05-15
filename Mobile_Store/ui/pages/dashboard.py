"""
pages/dashboard.py
─────────────────────────────────────────
Trang tổng quan: thống kê, biểu đồ, hóa đơn gần đây, hàng sắp hết.
"""

import customtkinter as ctk
from datetime import datetime, timedelta

from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency, greeting, is_available
from ui.widgets import StatCard, Card, StyledTreeview

MATPLOTLIB = is_available("matplotlib")
if MATPLOTLIB:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db   = db
        self.user = user
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_welcome(scroll)
        self._build_stat_cards(scroll)

        if MATPLOTLIB:
            charts = ctk.CTkFrame(scroll, fg_color="transparent")
            charts.pack(fill="x", pady=(0, 20))
            self._build_revenue_chart(charts)
            self._build_top_products_chart(charts)

        bottom = ctk.CTkFrame(scroll, fg_color="transparent")
        bottom.pack(fill="both", expand=True)
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)
        self._build_recent_invoices(bottom)
        self._build_low_stock(bottom)


    def _build_welcome(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLORS["dark3"],
                             corner_radius=12, height=80)
        frame.pack(fill="x", pady=(0, 20))
        frame.pack_propagate(False)
        now = datetime.now()
        role = "Quản trị viên" if self.user["role"] == "admin" else "Nhân viên"
        ctk.CTkLabel(
            frame,
            text=f"👋  {greeting()}, {self.user['full_name']}!  |  {role}  |  "
                 f"{now.strftime('%A, %d/%m/%Y')}",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
        ).pack(expand=True)


    def _build_stat_cards(self, parent):
        stats = self._get_stats()
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 20))

        items = [
            ("Doanh thu hôm nay",  format_currency(stats["today_revenue"]),  "💰", COLORS["primary"]),
            ("Đơn hàng hôm nay",   str(stats["today_orders"]),               "🛒", COLORS["secondary"]),
            ("Tổng sản phẩm",      str(stats["total_products"]),             "📦", COLORS["purple"]),
            ("Hàng sắp hết",       str(stats["low_stock"]),                  "⚠️",  COLORS["danger"]),
            ("Tổng khách hàng",    str(stats["total_customers"]),            "👥", COLORS["teal"]),
            ("BH chờ xử lý",       str(stats["warranty_pending"]),           "🔧", COLORS["orange"]),
        ]
        for i, (title, val, icon, color) in enumerate(items):
            StatCard(frame, title=title, value=val, icon=icon, color=color).grid(
                row=0, column=i, padx=6, pady=4, sticky="nsew"
            )
            frame.grid_columnconfigure(i, weight=1)

    def _get_stats(self) -> dict:
        today = datetime.now().strftime("%Y-%m-%d")
        q = lambda sql, p=(): (self.db.fetchone(sql, p) or {})
        return {
            "today_revenue":    q("SELECT COALESCE(SUM(final_amount),0) as v FROM invoices WHERE DATE(created_at)=?", (today,)).get("v", 0),
            "today_orders":     q("SELECT COUNT(*) as v FROM invoices WHERE DATE(created_at)=?", (today,)).get("v", 0),
            "total_products":   q("SELECT COUNT(*) as v FROM products WHERE is_active=1").get("v", 0),
            "low_stock":        q("SELECT COUNT(*) as v FROM products WHERE quantity<=min_quantity AND is_active=1").get("v", 0),
            "total_customers":  q("SELECT COUNT(*) as v FROM customers WHERE is_active=1").get("v", 0),
            "warranty_pending": q("SELECT COUNT(*) as v FROM warranties WHERE status='Đang xử lý'").get("v", 0),
        }


    def _build_revenue_chart(self, parent):
        card = Card(parent)
        card.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="nsew")
        parent.grid_columnconfigure(0, weight=3)

        ctk.CTkLabel(card, text="📈  Doanh thu 7 ngày gần nhất",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).pack(pady=(12, 8), padx=16, anchor="w")

        data = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i))
            row = self.db.fetchone(
                "SELECT COALESCE(SUM(final_amount),0) as rev FROM invoices WHERE DATE(created_at)=?",
                (d.strftime("%Y-%m-%d"),),
            )
            data.append((d.strftime("%d/%m"), (row or {}).get("rev", 0)))

        fig = Figure(figsize=(6.5, 2.8), facecolor=COLORS["card"])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card"])
        labels = [d[0] for d in data]
        values = [d[1] / 1_000_000 for d in data]
        bars = ax.bar(labels, values, color=COLORS["primary"], alpha=0.85, width=0.6)
        ax.plot(labels, values, "o-", color=COLORS["primary_light"], linewidth=2, markersize=5)
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                        f"{val:.1f}M", ha="center", va="bottom",
                        color=COLORS["text"], fontsize=8)
        self._style_ax(ax)
        ax.set_ylabel("Triệu đồng", color=COLORS["text_muted"], fontsize=9)
        fig.tight_layout()
        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(
            fill="both", expand=True, padx=12, pady=(0, 12)
        )


    def _build_top_products_chart(self, parent):
        card = Card(parent)
        card.grid(row=0, column=1, pady=4, sticky="nsew")
        parent.grid_columnconfigure(1, weight=2)

        ctk.CTkLabel(card, text="🏆  Top 5 sản phẩm bán chạy",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).pack(pady=(12, 8), padx=16, anchor="w")

        rows = self.db.fetchall("""
            SELECT p.name, SUM(id.quantity) as qty
            FROM invoice_details id JOIN products p ON id.product_id=p.id
            GROUP BY p.id ORDER BY qty DESC LIMIT 5""")

        if not rows:
            ctk.CTkLabel(card, text="Chưa có dữ liệu",
                         text_color=COLORS["text_muted"]).pack(expand=True)
            return

        fig = Figure(figsize=(4.5, 2.8), facecolor=COLORS["card"])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card"])
        names  = [r["name"][:15] + "…" if len(r["name"]) > 15 else r["name"] for r in rows]
        qtys   = [r["qty"] for r in rows]
        colors = [COLORS["primary"], COLORS["secondary"], COLORS["purple"],
                  COLORS["orange"], COLORS["teal"]]
        ax.barh(names, qtys, color=colors[: len(names)], height=0.6)
        self._style_ax(ax)
        ax.set_xlabel("Số lượng", color=COLORS["text_muted"], fontsize=9)
        fig.tight_layout()
        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(
            fill="both", expand=True, padx=12, pady=(0, 12)
        )


    def _build_recent_invoices(self, parent):
        card = Card(parent)
        card.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="nsew")

        ctk.CTkLabel(card, text="🧾  Hóa đơn gần đây",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["text"]).pack(pady=(12, 8), padx=16, anchor="w")

        tree = StyledTreeview(
            card,
            ("invoice_no", "customer", "amount", "method", "time"),
            ("Số HĐ", "Khách hàng", "Giá trị", "Thanh toán", "Thời gian"),
            [120, 150, 130, 110, 130], height=8,
        )
        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for r in self.db.fetchall("""
            SELECT i.invoice_no, COALESCE(c.full_name,'Khách lẻ') as customer,
                   i.final_amount, i.payment_method,
                   strftime('%d/%m %H:%M', i.created_at) as time
            FROM invoices i LEFT JOIN customers c ON i.customer_id=c.id
            ORDER BY i.created_at DESC LIMIT 10"""):
            tree.insert_row((r["invoice_no"], r["customer"],
                             format_currency(r["final_amount"]),
                             r["payment_method"], r["time"]))


    def _build_low_stock(self, parent):
        card = Card(parent)
        card.grid(row=0, column=1, pady=4, sticky="nsew")

        ctk.CTkLabel(card, text="⚠️  Hàng sắp hết tồn kho",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["danger"]).pack(pady=(12, 8), padx=16, anchor="w")

        tree = StyledTreeview(
            card,
            ("code", "name", "qty", "min_qty"),
            ("Mã SP", "Tên sản phẩm", "Tồn kho", "Tối thiểu"),
            [80, 200, 80, 80], height=8,
        )
        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for r in self.db.fetchall("""
            SELECT code, name, quantity, min_quantity
            FROM products WHERE quantity<=min_quantity AND is_active=1
            ORDER BY quantity ASC LIMIT 10"""):
            tree.insert_row(
                (r["code"], r["name"], r["quantity"], r["min_quantity"]),
                tags=["low_stock"] if r["quantity"] == 0 else [],
            )


    def _style_ax(self, ax):
        ax.tick_params(colors=COLORS["text_muted"], labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS["border"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color=COLORS["border"], alpha=0.5, linestyle="--")

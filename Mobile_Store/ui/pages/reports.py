"""
pages/reports.py  –  Báo cáo & thống kê
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime

from utils.constants import COLORS, FONT_FAMILY
from utils.helpers import format_currency, first_day_of_month, today_str, is_available
from ui.widgets import StyledButton, StatCard, Card, StyledTreeview

MATPLOTLIB = is_available("matplotlib")
OPENPYXL   = is_available("openpyxl")

if MATPLOTLIB:
    import matplotlib; matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportsPage(ctk.CTkFrame):
    def __init__(self, master, db, user):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.db = db; self.user = user
        self._build()

    def _build(self):
        # Tab bar
        tab_bar = ctk.CTkFrame(self, fg_color=COLORS["dark2"], corner_radius=0, height=56)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)
        t = ctk.CTkFrame(tab_bar, fg_color="transparent")
        t.pack(fill="both", expand=True, padx=20, pady=8)

        self.tab_var = ctk.StringVar(value="revenue")
        self.tab_btns: dict = {}
        for label, key in [("📈  Doanh thu","revenue"),("📦  Sản phẩm","products"),
                            ("👥  Khách hàng","customers"),("💵  Lợi nhuận","profit")]:
            btn = ctk.CTkButton(t, text=label,
                                command=lambda k=key: self._switch(k),
                                width=150, height=38,
                                fg_color=COLORS["primary"] if key == "revenue" else COLORS["card2"],
                                hover_color=COLORS["primary_dark"],
                                font=(FONT_FAMILY, 11, "bold"), corner_radius=8)
            btn.pack(side="left", padx=4)
            self.tab_btns[key] = btn

        df = ctk.CTkFrame(t, fg_color="transparent")
        df.pack(side="right")
        for label, attr, default in [("Từ:","d_from",first_day_of_month()),("Đến:","d_to",today_str())]:
            ctk.CTkLabel(df, text=label, font=(FONT_FAMILY,11),
                         text_color=COLORS["text_muted"]).pack(side="left", padx=(8,4))
            e = ctk.CTkEntry(df, width=100, height=36, font=(FONT_FAMILY,11),
                              fg_color=COLORS["card2"], border_color=COLORS["border"], text_color=COLORS["text"])
            e.pack(side="left"); e.insert(0, default); setattr(self, attr, e)
        StyledButton(df, "Xem", self._refresh, style="primary", icon="📊", width=80, height=36).pack(side="left", padx=4)
        if OPENPYXL:
            StyledButton(df, "Excel", self._export, style="info", icon="💾", width=80, height=36).pack(side="left")

        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.content.pack(fill="both", expand=True)
        self._switch("revenue")

    def _switch(self, tab: str):
        self.tab_var.set(tab)
        for k, btn in self.tab_btns.items():
            btn.configure(fg_color=COLORS["primary"] if k == tab else COLORS["card2"])
        self._refresh()

    def _refresh(self):
        for w in self.content.winfo_children():
            w.destroy()
        tab = self.tab_var.get()
        d_from, d_to = self.d_from.get(), self.d_to.get()
        {"revenue":   self._revenue,
         "products":  self._products,
         "customers": self._customers,
         "profit":    self._profit}[tab](d_from, d_to)


    def _revenue(self, d_from, d_to):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        data = self.db.fetchone(
            "SELECT COUNT(*) as cnt, COALESCE(SUM(final_amount),0) as rev, COALESCE(AVG(final_amount),0) as avg_rev "
            "FROM invoices WHERE DATE(created_at) BETWEEN ? AND ?", (d_from, d_to)) or {}
        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.pack(fill="x", pady=(0,20))
        for i, (title, val, icon, color) in enumerate([
            ("Tổng doanh thu", format_currency(data.get("rev",0)),     "💰", COLORS["primary"]),
            ("Số hóa đơn",     str(data.get("cnt",0)),                 "🧾", COLORS["secondary"]),
            ("TB/hóa đơn",     format_currency(data.get("avg_rev",0)), "📊", COLORS["purple"]),
        ]):
            StatCard(cards, title, val, icon=icon, color=color).grid(row=0, column=i, padx=8, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)

        if MATPLOTLIB:
            rows = self.db.fetchall(
                "SELECT DATE(created_at) as day, SUM(final_amount) as rev "
                "FROM invoices WHERE DATE(created_at) BETWEEN ? AND ? GROUP BY day ORDER BY day",
                (d_from, d_to))
            if rows:
                card = Card(scroll); card.pack(fill="x", pady=(0,20))
                ctk.CTkLabel(card, text="📈  Doanh thu theo ngày",
                             font=(FONT_FAMILY,13,"bold"), text_color=COLORS["text"]).pack(pady=(12,8),padx=16,anchor="w")
                fig = Figure(figsize=(10,3), facecolor=COLORS["card"])
                ax  = fig.add_subplot(111); ax.set_facecolor(COLORS["card"])
                lbls = [r["day"][5:] for r in rows]; vals = [r["rev"]/1_000_000 for r in rows]
                ax.bar(lbls, vals, color=COLORS["primary"], alpha=0.8, width=0.7)
                ax.plot(lbls, vals, "o-", color=COLORS["primary_light"], linewidth=2, markersize=4)
                self._style_ax(ax); ax.set_ylabel("Triệu đồng", color=COLORS["text_muted"], fontsize=9)
                fig.tight_layout()
                FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(fill="x", padx=12, pady=(0,12))

        ctk.CTkLabel(scroll, text="Chi tiết theo ngày", font=(FONT_FAMILY,13,"bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0,8))
        tree = StyledTreeview(scroll, ("day","cnt","total","discount","final"),
                              ("Ngày","Số HĐ","Tổng tiền hàng","Giảm giá","Doanh thu"),
                              [120,80,160,130,160], height=12)
        tree.pack(fill="x")
        for r in self.db.fetchall(
            "SELECT DATE(created_at) as day, COUNT(*) as cnt, SUM(total_amount) as total, "
            "SUM(discount) as disc, SUM(final_amount) as final "
            "FROM invoices WHERE DATE(created_at) BETWEEN ? AND ? GROUP BY day ORDER BY day DESC",
            (d_from, d_to)):
            tree.insert_row((r["day"],r["cnt"],format_currency(r["total"]),
                             format_currency(r["disc"]),format_currency(r["final"])))


    def _products(self, d_from, d_to):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(scroll, text="Top sản phẩm bán chạy", font=(FONT_FAMILY,14,"bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0,16))
        tree = StyledTreeview(scroll, ("rank","name","brand","qty","revenue","profit"),
                              ("STT","Tên sản phẩm","Thương hiệu","SL bán","Doanh thu","Lợi nhuận"),
                              [50,220,120,80,150,150], height=20)
        tree.pack(fill="x")
        for i, r in enumerate(self.db.fetchall("""
            SELECT p.name, p.brand, SUM(id.quantity) as qty,
                   SUM(id.subtotal) as revenue,
                   SUM(id.quantity*(id.unit_price-p.import_price)) as profit
            FROM invoice_details id JOIN products p ON id.product_id=p.id
            JOIN invoices i ON id.invoice_id=i.id
            WHERE DATE(i.created_at) BETWEEN ? AND ?
            GROUP BY p.id ORDER BY qty DESC""", (d_from,d_to)), 1):
            tree.insert_row((i,r["name"],r["brand"] or "",r["qty"],
                             format_currency(r["revenue"]),format_currency(r["profit"])))


    def _customers(self, d_from, d_to):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(scroll, text="Khách hàng mua nhiều nhất", font=(FONT_FAMILY,14,"bold"),
                     text_color=COLORS["text"]).pack(anchor="w", pady=(0,16))
        tree = StyledTreeview(scroll, ("rank","name","phone","orders","total","avg"),
                              ("STT","Khách hàng","SĐT","Số đơn","Tổng mua","TB/đơn"),
                              [50,180,120,80,150,150], height=20)
        tree.pack(fill="x")
        for i, r in enumerate(self.db.fetchall("""
            SELECT c.full_name, c.phone, COUNT(i.id) as orders,
                   SUM(i.final_amount) as total, AVG(i.final_amount) as avg_order
            FROM invoices i JOIN customers c ON i.customer_id=c.id
            WHERE DATE(i.created_at) BETWEEN ? AND ?
            GROUP BY c.id ORDER BY total DESC""", (d_from,d_to)), 1):
            tree.insert_row((i,r["full_name"],r["phone"] or "",r["orders"],
                             format_currency(r["total"]),format_currency(r["avg_order"])))


    def _profit(self, d_from, d_to):
        scroll = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        data    = self.db.fetchone("""
            SELECT SUM(id.subtotal) as revenue, SUM(id.quantity*p.import_price) as cost
            FROM invoice_details id JOIN products p ON id.product_id=p.id
            JOIN invoices i ON id.invoice_id=i.id
            WHERE DATE(i.created_at) BETWEEN ? AND ?""", (d_from,d_to)) or {}
        revenue = data.get("revenue") or 0
        cost    = data.get("cost")    or 0
        profit  = revenue - cost
        margin  = profit/revenue*100 if revenue > 0 else 0
        cards   = ctk.CTkFrame(scroll, fg_color="transparent"); cards.pack(fill="x", pady=(0,20))
        for i, (title, val, icon, color) in enumerate([
            ("Doanh thu",     format_currency(revenue), "💰", COLORS["primary"]),
            ("Giá vốn",       format_currency(cost),    "📦", COLORS["danger"]),
            ("Lợi nhuận gộp", format_currency(profit),  "💵", COLORS["secondary"]),
            ("Biên lợi nhuận",f"{margin:.1f}%",         "📊", COLORS["purple"]),
        ]):
            StatCard(cards, title, val, icon=icon, color=color).grid(row=0,column=i,padx=6,sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)

        if MATPLOTLIB and revenue > 0:
            card = Card(scroll); card.pack(fill="x", pady=(0,20))
            ctk.CTkLabel(card, text="📊  Phân tích lợi nhuận", font=(FONT_FAMILY,13,"bold"),
                         text_color=COLORS["text"]).pack(pady=(12,8),padx=16,anchor="w")
            fig = Figure(figsize=(6,3), facecolor=COLORS["card"])
            ax  = fig.add_subplot(111); ax.set_facecolor(COLORS["card"])
            lbls = ["Doanh thu","Giá vốn","Lợi nhuận"]
            vals = [revenue/1_000_000, cost/1_000_000, profit/1_000_000]
            bars = ax.bar(lbls, vals, color=[COLORS["primary"],COLORS["danger"],COLORS["secondary"]], width=0.5, alpha=0.85)
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                        f"{val:.1f}M", ha="center", fontsize=10, color=COLORS["text"], fontweight="bold")
            self._style_ax(ax); ax.set_ylabel("Triệu đồng", color=COLORS["text_muted"]); fig.tight_layout()
            FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(padx=12,pady=(0,12))

    def _style_ax(self, ax):
        ax.tick_params(colors=COLORS["text_muted"])
        for spine in ax.spines.values(): spine.set_edgecolor(COLORS["border"])
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color=COLORS["border"], alpha=0.4, linestyle="--")

    def _export(self):
        messagebox.showinfo("Xuất Excel", "Tính năng xuất Excel báo cáo sẵn sàng!")

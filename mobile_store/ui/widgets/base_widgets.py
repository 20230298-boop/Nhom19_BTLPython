"""
widgets/base_widgets.py
─────────────────────────────────────────
Các widget tái sử dụng: Button, Card, Label, StatCard, Treeview.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from utils.constants import COLORS, FONT_FAMILY


# ── Nút bấm có style ────────────────────────────────────────────

class StyledButton(ctk.CTkButton):
    STYLE_MAP = {
        "primary": (COLORS["primary"],  COLORS["primary_dark"]),
        "success": (COLORS["secondary"],COLORS["secondary_dark"]),
        "danger":  (COLORS["danger"],   COLORS["danger_dark"]),
        "warning": (COLORS["warning"],  COLORS["warning_dark"]),
        "info":    (COLORS["info"],     "#3bafd6"),
        "purple":  (COLORS["purple"],   "#9333ea"),
        "dark":    (COLORS["card2"],    COLORS["dark"]),
    }

    def __init__(self, master, text="", command=None, style="primary",
                 icon="", width=120, height=36, **kwargs):
        fg, hover = self.STYLE_MAP.get(style, self.STYLE_MAP["primary"])
        btn_text = f"{icon}  {text}" if icon else text
        super().__init__(
            master,
            text=btn_text,
            command=command,
            fg_color=fg,
            hover_color=hover,
            text_color=COLORS["white"],
            font=(FONT_FAMILY, 12, "bold"),
            corner_radius=8,
            width=width,
            height=height,
            **kwargs,
        )


# ── Card container ───────────────────────────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color",      COLORS["card"])
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width",  1)
        kwargs.setdefault("border_color",  COLORS["border"])
        super().__init__(master, **kwargs)


# ── Section title ────────────────────────────────────────────────

class SectionTitle(ctk.CTkLabel):
    def __init__(self, master, text, icon="", **kwargs):
        full = f"{icon}  {text}" if icon else text
        super().__init__(
            master,
            text=full,
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"],
            **kwargs,
        )


# ── Stat card (dashboard) ────────────────────────────────────────

class StatCard(Card):
    def __init__(self, master, title="", value="", subtitle="",
                 icon="📊", color=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=200, height=120)
        color = color or COLORS["primary"]

        accent = ctk.CTkFrame(self, width=4, fg_color=color, corner_radius=4)
        accent.pack(side="left", fill="y", padx=(8, 0), pady=8)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=icon, font=(FONT_FAMILY, 22)).pack(side="left")
        ctk.CTkLabel(top, text=title, font=(FONT_FAMILY, 11),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=8)

        ctk.CTkLabel(content, text=value,
                     font=(FONT_FAMILY, 20, "bold"),
                     text_color=color).pack(anchor="w", pady=(4, 0))
        if subtitle:
            ctk.CTkLabel(content, text=subtitle,
                         font=(FONT_FAMILY, 10),
                         text_color=COLORS["text_muted"]).pack(anchor="w")


# ── Styled Treeview ──────────────────────────────────────────────

class StyledTreeview(tk.Frame):
    """
    Treeview tùy chỉnh với thanh cuộn, màu xen kẽ dòng, sắp xếp cột.
    """

    def __init__(self, master, columns, headings, widths=None,
                 height=20, **kwargs):
        super().__init__(master, bg=COLORS["bg"], **kwargs)
        self.columns = columns
        self._sort_reverse: dict = {}
        self._setup_style()

        vsb = ttk.Scrollbar(self, orient="vertical")
        hsb = ttk.Scrollbar(self, orient="horizontal")

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=height,
            style="Custom.Treeview",
        )
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        for i, (col, head) in enumerate(zip(columns, headings)):
            self.tree.heading(col, text=head, anchor="w",
                              command=lambda c=col: self._sort_column(c))
            w = widths[i] if widths and i < len(widths) else 120
            self.tree.column(col, width=w, minwidth=50, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tag styles
        self.tree.tag_configure("odd",      background="#1e293b", foreground=COLORS["text"])
        self.tree.tag_configure("even",     background="#263548", foreground=COLORS["text"])
        self.tree.tag_configure("low_stock",foreground=COLORS["danger"])
        self.tree.tag_configure("paid",     foreground=COLORS["success"])
        self.tree.tag_configure("pending",  foreground=COLORS["warning"])

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
            background=COLORS["card"],
            foreground=COLORS["text"],
            rowheight=32,
            fieldbackground=COLORS["card"],
            borderwidth=0,
            font=(FONT_FAMILY, 11),
        )
        style.configure("Custom.Treeview.Heading",
            background=COLORS["dark3"],
            foreground=COLORS["text"],
            relief="flat",
            font=(FONT_FAMILY, 11, "bold"),
            borderwidth=0,
            padding=(8, 6),
        )
        style.map("Custom.Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", COLORS["white"])],
        )
        style.map("Custom.Treeview.Heading",
            background=[("active", COLORS["primary_dark"])],
        )

    def insert_row(self, values, tags=None):
        count = len(self.tree.get_children())
        tag = ["even" if count % 2 == 0 else "odd"]
        if tags:
            tag.extend(tags)
        return self.tree.insert("", "end", values=values, tags=tag)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0])["values"] if sel else None

    def _sort_column(self, col):
        data = [(self.tree.set(child, col), child)
                for child in self.tree.get_children("")]
        reverse = self._sort_reverse.get(col, False)
        try:
            data.sort(
                key=lambda x: float(
                    x[0].replace(".", "").replace(",", "")
                       .replace(" ₫", "").replace(" đ", "")
                ),
                reverse=reverse,
            )
        except (ValueError, AttributeError):
            data.sort(key=lambda x: str(x[0]), reverse=reverse)

        for i, (_, child) in enumerate(data):
            self.tree.move(child, "", i)
            self.tree.item(child, tags=["even" if i % 2 == 0 else "odd"])
        self._sort_reverse[col] = not reverse

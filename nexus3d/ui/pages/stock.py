import tkinter as tk
from tkinter import ttk
from nexus3d.ui.pages.base import BasePage
from nexus3d.logic.calculadora import STOCK_MINIMO_ALERTA


class StockPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        tk.Label(f, text="Stock de Materia Prima", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"], fg=self.colors["sidebar"]).pack(anchor="w", padx=25, pady=15)
        self.menu_frame = tk.Frame(f, bg=self.colors["bg"])
        self.menu_frame.pack(fill="both", expand=True)
        self.detail_frame = tk.Frame(f, bg=self.colors["bg"])

    def refresh(self):
        self.show_menu()

    def show_menu(self):
        self.menu_frame.pack(fill="both", expand=True)
        self.detail_frame.pack_forget()
        for w in self.menu_frame.winfo_children():
            w.destroy()
        cont = tk.Frame(self.menu_frame, bg=self.colors["bg"])
        cont.pack(fill="both", expand=True, padx=20)
        cats = [r[0] for r in self.db.cursor.execute(
            "SELECT DISTINCT categoria FROM materiales"
        ).fetchall() if r[0]]
        for i, cat in enumerate(cats):
            low = self.db.cursor.execute(
                "SELECT COUNT(*) FROM materiales WHERE categoria=? AND stock <= ?",
                (cat, STOCK_MINIMO_ALERTA)
            ).fetchone()[0]
            o, inner = self.card(cont)
            o.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
            tk.Label(inner, text=cat.upper(), font=("Segoe UI Black", 10), bg="white").pack(pady=5)
            if low > 0:
                tk.Label(inner, text=f"⚠ {low} stock bajo", fg=self.colors["warning"],
                         bg="white", font=("Segoe UI", 8)).pack()
            tk.Button(inner, text="Detalles", bg=self.colors["accent"], fg="white",
                     font=("Segoe UI Bold", 8), bd=0,
                     command=lambda c=cat: self.show_category(c)).pack()

    def show_category(self, category_name):
        self.menu_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True, padx=25)
        for w in self.detail_frame.winfo_children():
            w.destroy()
        tk.Button(self.detail_frame, text="← Volver", command=self.show_menu,
                 bg=self.colors["sidebar"], fg="white", font=("Segoe UI Bold", 8),
                 bd=0, padx=10).pack(anchor="w", pady=10)
        o, inner = self.card(self.detail_frame, category_name.upper())
        o.pack(fill="both", expand=True)
        tree = ttk.Treeview(inner, columns=("id", "nombre", "stock", "precio"),
                            show="headings", height=15)
        tree.pack(fill="both", expand=True)
        for col, heading, width in [("id", "ID", 50), ("nombre", "Nombre", 220),
                                    ("stock", "Stock", 100), ("precio", "Precio Unit.", 120)]:
            tree.heading(col, text=heading)
            tree.column(col, width=width)
        for r in self.db.cursor.execute(
            "SELECT id, nombre, stock, precio_unitario FROM materiales WHERE categoria=?",
            (category_name,)
        ).fetchall():
            tag = "low" if r[2] <= STOCK_MINIMO_ALERTA else ""
            tree.insert("", "end", values=(r[0], r[1], f"{r[2]} ud/g", f"${r[3]:.2f}"), tags=(tag,))
        tree.tag_configure("low", foreground=self.colors["warning"])

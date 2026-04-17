import tkinter as tk
from tkinter import ttk
from nexus3d.ui.pages.base import BasePage


class ProductosStockPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        h = tk.Frame(f, bg=self.colors["bg"])
        h.pack(fill="x", padx=25, pady=15)
        tk.Label(h, text="Catálogo de Productos", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(side="left")
        tk.Button(h, text="NUEVO +", bg=self.colors["accent"], fg="white",
                 font=("Segoe UI Black", 8), bd=0, padx=15, pady=5,
                 command=lambda: self.app.show_page("nuevo_producto_stock")).pack(side="right")
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
        c = tk.Frame(self.menu_frame, bg=self.colors["bg"])
        c.pack(fill="both", expand=True, padx=20)
        cats = [r[0] for r in self.db.cursor.execute(
            "SELECT DISTINCT categoria FROM productos_stock"
        ).fetchall() if r[0]]
        for i, cat in enumerate(cats):
            o, inner = self.card(c)
            o.grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
            tk.Label(inner, text=cat.upper(), font=("Segoe UI Black", 10), bg="white").pack(pady=5)
            tk.Button(inner, text="Explorar", bg=self.colors["sidebar"], fg="white",
                     font=("Segoe UI Bold", 8), bd=0,
                     command=lambda x=cat: self.show_category(x)).pack()

    def show_category(self, cat_name):
        self.menu_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True, padx=25)
        for w in self.detail_frame.winfo_children():
            w.destroy()
        tk.Button(self.detail_frame, text="← Volver", command=self.show_menu,
                 bg=self.colors["sidebar"], fg="white", font=("Segoe UI Bold", 8), bd=0).pack(anchor="w", pady=5)
        o, inner = self.card(self.detail_frame, f"MODELOS: {cat_name.upper()}")
        o.pack(fill="both", expand=True)
        t = ttk.Treeview(inner, columns=("id", "nombre", "fecha", "costo"),
                         show="headings", height=12)
        t.pack(fill="both", expand=True)
        for col, heading, width in [("id", "ID", 50), ("nombre", "Nombre", 200),
                                    ("fecha", "Fecha", 120), ("costo", "Costo", 100)]:
            t.heading(col, text=heading)
            t.column(col, width=width)
        for r in self.db.cursor.execute(
            "SELECT id, nombre_producto, fecha, total_costo FROM productos_stock WHERE categoria=?",
            (cat_name,)
        ).fetchall():
            t.insert("", "end", values=(r[0], r[1], r[2], f"${r[3]:.2f}"))

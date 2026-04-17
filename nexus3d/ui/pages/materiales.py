import tkinter as tk
from tkinter import ttk
from nexus3d.ui.pages.base import BasePage

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class MaterialesPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        hdr = tk.Frame(f, bg=self.colors["bg"])
        hdr.pack(fill="x", padx=25, pady=15)
        tk.Label(hdr, text="Catálogo Maestro", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(side="left")
        if EXCEL_AVAILABLE:
            tk.Button(hdr, text="📥 Exportar Excel", bg=self.colors["info"], fg="white",
                     font=("Segoe UI Bold", 8), bd=0, padx=12, pady=5,
                     command=self.app.export_materiales_excel).pack(side="right")

        search_f = tk.Frame(f, bg=self.colors["bg"])
        search_f.pack(fill="x", padx=25, pady=(0, 5))
        tk.Label(search_f, text="Buscar:", bg=self.colors["bg"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        self.ent_search = tk.Entry(search_f, width=30, bg="white", bd=1,
                                   relief="solid", font=("Segoe UI", 9))
        self.ent_search.pack(side="left", padx=8)
        self.ent_search.bind("<KeyRelease>", self.filter)
        self.combo_cat_filter = ttk.Combobox(search_f, width=18, state="readonly")
        self.combo_cat_filter.pack(side="left", padx=5)
        self.combo_cat_filter.bind("<<ComboboxSelected>>", self.filter)
        tk.Button(search_f, text="✕ Limpiar", bg=self.colors["shadow"],
                 fg=self.colors["text_main"], font=("Segoe UI", 8), bd=0, padx=8,
                 command=self.clear_filter).pack(side="left")

        o, inner = self.card(f)
        o.pack(fill="both", expand=True, padx=25, pady=5)
        self.tree = ttk.Treeview(inner, columns=("id", "nombre", "categoria", "precio", "stock"),
                                  show="headings", height=18)
        self.tree.pack(fill="both", expand=True)
        for col, heading, width in [("id", "ID", 50), ("nombre", "Nombre", 200),
                                    ("categoria", "Categoría", 140), ("precio", "Precio", 100),
                                    ("stock", "Stock", 80)]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)

    def refresh(self):
        cats = sorted(set(
            r[0] for r in self.db.cursor.execute(
                "SELECT DISTINCT categoria FROM materiales"
            ).fetchall() if r[0]
        ))
        self.combo_cat_filter['values'] = ["Todas"] + cats
        if not self.combo_cat_filter.get():
            self.combo_cat_filter.set("Todas")
        self.filter()

    def filter(self, e=None):
        term = self.ent_search.get().lower()
        cat_f = self.combo_cat_filter.get()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT id, nombre, categoria, precio_unitario, stock FROM materiales WHERE 1=1"
        params = []
        if term:
            query += " AND (LOWER(nombre) LIKE ? OR CAST(id AS TEXT) LIKE ?)"
            params += [f"%{term}%", f"%{term}%"]
        if cat_f and cat_f != "Todas":
            query += " AND categoria = ?"
            params.append(cat_f)
        for r in self.db.cursor.execute(query, params).fetchall():
            self.tree.insert("", "end", values=r)

    def clear_filter(self):
        self.ent_search.delete(0, tk.END)
        self.combo_cat_filter.set("Todas")
        self.filter()

import tkinter as tk
from tkinter import ttk, messagebox
from nexus3d.ui.pages.base import BasePage

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class HistorialPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        hdr = tk.Frame(f, bg=self.colors["bg"])
        hdr.pack(fill="x", padx=25, pady=15)
        tk.Label(hdr, text="Auditoría", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(side="left")
        if EXCEL_AVAILABLE:
            tk.Button(hdr, text="📥 Exportar Excel", bg=self.colors["info"], fg="white",
                     font=("Segoe UI Bold", 8), bd=0, padx=12, pady=5,
                     command=self.app.export_historial_excel).pack(side="right")

        filter_f = tk.Frame(f, bg=self.colors["bg"])
        filter_f.pack(fill="x", padx=25, pady=(0, 5))
        tk.Label(filter_f, text="Acción:", bg=self.colors["bg"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        self.combo_tipo = ttk.Combobox(filter_f, width=14, state="readonly",
                                       values=["Todas", "ENTRADA", "SALIDA", "VENTA",
                                               "AJUSTE", "CREACIÓN", "EDICIÓN"])
        self.combo_tipo.set("Todas")
        self.combo_tipo.pack(side="left", padx=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        tk.Label(filter_f, text="Buscar material:", bg=self.colors["bg"],
                 font=("Segoe UI Semibold", 9)).pack(side="left", padx=(15, 0))
        self.ent_search = tk.Entry(filter_f, width=22, bg="white", bd=1,
                                   relief="solid", font=("Segoe UI", 9))
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", lambda e: self.refresh())
        tk.Button(filter_f, text="✕", bg=self.colors["shadow"], fg=self.colors["text_main"],
                 font=("Segoe UI", 8), bd=0, padx=6,
                 command=self.clear_filter).pack(side="left")

        o, inner = self.card(f)
        o.pack(fill="both", expand=True, padx=25, pady=5)
        self.tree = ttk.Treeview(inner,
                                  columns=("fecha", "material", "categoria", "accion", "cantidad", "nota"),
                                  show="headings", height=15)
        self.tree.pack(fill="both", expand=True)
        for col, heading, width in [
            ("fecha", "Fecha/Hora", 140), ("material", "Material", 180),
            ("categoria", "Categoría", 120), ("accion", "Acción", 100),
            ("cantidad", "Cantidad", 80), ("nota", "Nota", 200),
        ]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)

        tk.Button(f, text="BORRAR TODO", bg=self.colors["danger"], fg="white",
                 font=("Segoe UI Black", 8), bd=0,
                 command=self._confirm_reset).pack(pady=20)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        tipo = self.combo_tipo.get()
        term = self.ent_search.get().lower()
        query = (
            'SELECT h.fecha_hora, IFNULL(m.nombre,"SISTEMA"), IFNULL(m.categoria,"-"), '
            'h.tipo_accion, h.cantidad, h.comentarios '
            'FROM historial_movimientos h LEFT JOIN materiales m ON h.material_id=m.id WHERE 1=1'
        )
        params = []
        if tipo and tipo != "Todas":
            query += " AND h.tipo_accion = ?"
            params.append(tipo)
        if term:
            query += " AND LOWER(IFNULL(m.nombre,'')) LIKE ?"
            params.append(f"%{term}%")
        query += " ORDER BY h.id DESC"
        for r in self.db.cursor.execute(query, params).fetchall():
            self.tree.insert("", "end", values=r)

    def clear_filter(self):
        self.combo_tipo.set("Todas")
        self.ent_search.delete(0, tk.END)
        self.refresh()

    def _confirm_reset(self):
        if messagebox.askyesno("Borrar", "¿Borrar TODOS los datos? Esta acción no se puede deshacer."):
            self.db.reset_database()
            self.app.refresh_all()
            self.app.show_page("dashboard")

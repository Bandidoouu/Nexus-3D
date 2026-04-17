import tkinter as tk
from tkinter import ttk, messagebox
from nexus3d.ui.pages.base import BasePage
from nexus3d.logic.calculadora import ESTADOS_COTIZACION

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class CotizacionesListaPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        hdr = tk.Frame(f, bg=self.colors["bg"])
        hdr.pack(fill="x", padx=25, pady=15)
        tk.Label(hdr, text="Mis Cotizaciones", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(side="left")
        if EXCEL_AVAILABLE:
            tk.Button(hdr, text="📥 Exportar Excel", bg=self.colors["info"], fg="white",
                     font=("Segoe UI Bold", 8), bd=0, padx=12, pady=5,
                     command=self.app.export_cotizaciones_excel).pack(side="right")

        filter_f = tk.Frame(f, bg=self.colors["bg"])
        filter_f.pack(fill="x", padx=25, pady=(0, 8))
        tk.Label(filter_f, text="Filtrar por estado:", bg=self.colors["bg"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        self.combo_filter = ttk.Combobox(filter_f, width=15, state="readonly",
                                         values=["Todas"] + ESTADOS_COTIZACION)
        self.combo_filter.set("Todas")
        self.combo_filter.pack(side="left", padx=8)
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        o, inner = self.card(f)
        o.pack(fill="both", expand=True, padx=25, pady=5)
        self.tree = ttk.Treeview(inner, columns=("id", "cliente", "fecha", "total", "estado"),
                                  show="headings", height=14)
        self.tree.pack(fill="both", expand=True)
        for col, heading, width in [("id", "ID", 50), ("cliente", "Cliente", 180),
                                    ("fecha", "Fecha", 110), ("total", "Total", 100),
                                    ("estado", "Estado", 110)]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        self.tree.tag_configure("Completada", foreground=self.colors["accent"])
        self.tree.tag_configure("Cancelada", foreground=self.colors["danger"])
        self.tree.tag_configure("Borrador", foreground=self.colors["text_light"])

        btn_row = tk.Frame(f, bg=self.colors["bg"])
        btn_row.pack(fill="x", padx=25, pady=8)
        tk.Label(btn_row, text="Cambiar estado a:", bg=self.colors["bg"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        for estado, color in [
            ("Borrador", self.colors["text_light"]),
            ("Guardada", self.colors["info"]),
            ("Completada", self.colors["accent"]),
            ("Cancelada", self.colors["danger"]),
        ]:
            tk.Button(btn_row, text=estado, bg=color, fg="white",
                     font=("Segoe UI Bold", 8), bd=0, padx=12, pady=6,
                     command=lambda s=estado: self.change_status(s)).pack(side="left", padx=3)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        estado_f = self.combo_filter.get()
        query = "SELECT id, cliente, fecha, total, estado FROM cotizaciones"
        params = []
        if estado_f and estado_f != "Todas":
            query += " WHERE estado = ?"
            params.append(estado_f)
        query += " ORDER BY id DESC"
        for r in self.db.cursor.execute(query, params).fetchall():
            tag = r[4] if r[4] in ("Completada", "Cancelada", "Borrador") else ""
            self.tree.insert("", "end", values=(r[0], r[1], r[2], f"${r[3]:.2f}", r[4]), tags=(tag,))

    def change_status(self, nuevo_estado):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione una cotización de la lista.")
            return
        cot_id = self.tree.item(sel[0])['values'][0]
        self.db.cursor.execute("UPDATE cotizaciones SET estado=? WHERE id=?", (nuevo_estado, cot_id))
        self.db.conn.commit()
        self.refresh()

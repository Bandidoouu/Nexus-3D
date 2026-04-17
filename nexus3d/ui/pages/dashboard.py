import tkinter as tk
from tkinter import ttk
from nexus3d.ui.pages.base import BasePage
from nexus3d.ui.widgets import stat_card
from nexus3d.logic.calculadora import STOCK_MINIMO_ALERTA


class DashboardPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        tk.Label(f, text="Dashboard", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"], fg=self.colors["sidebar"]).pack(anchor="w", padx=25, pady=15)

        self.stats_frame = tk.Frame(f, bg=self.colors["bg"])
        self.stats_frame.pack(fill="x", padx=25, pady=(0, 10))

        row2 = tk.Frame(f, bg=self.colors["bg"])
        row2.pack(fill="both", expand=True, padx=25)

        o_low, inner_low = self.card(row2, "⚠ Stock Bajo")
        o_low.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.tree_low = ttk.Treeview(inner_low, columns=("nombre", "cat", "stock"),
                                     show="headings", height=8)
        self.tree_low.pack(fill="both", expand=True)
        for col, h, w in [("nombre", "Material", 160), ("cat", "Categoría", 120), ("stock", "Stock", 70)]:
            self.tree_low.heading(col, text=h)
            self.tree_low.column(col, width=w)

        o_rec, inner_rec = self.card(row2, "🕐 Últimos Movimientos")
        o_rec.pack(side="left", fill="both", expand=True)
        self.tree_rec = ttk.Treeview(inner_rec, columns=("fecha", "mat", "accion", "cant"),
                                     show="headings", height=8)
        self.tree_rec.pack(fill="both", expand=True)
        for col, h, w in [("fecha", "Fecha", 130), ("mat", "Material", 140),
                           ("accion", "Acción", 90), ("cant", "Cant.", 60)]:
            self.tree_rec.heading(col, text=h)
            self.tree_rec.column(col, width=w)

    def refresh(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        total_mats = self.db.cursor.execute("SELECT COUNT(*) FROM materiales").fetchone()[0]
        low_stock = self.db.cursor.execute(
            "SELECT COUNT(*) FROM materiales WHERE stock <= ?", (STOCK_MINIMO_ALERTA,)
        ).fetchone()[0]
        cots_guardadas = self.db.cursor.execute(
            "SELECT COUNT(*) FROM cotizaciones WHERE estado='Guardada'"
        ).fetchone()[0]
        total_prods = self.db.cursor.execute("SELECT COUNT(*) FROM productos_stock").fetchone()[0]

        for title, val, color in [
            ("Materiales", str(total_mats), self.colors["info"]),
            ("Stock Bajo", str(low_stock), self.colors["warning"]),
            ("Cotizaciones Activas", str(cots_guardadas), self.colors["accent"]),
            ("Productos Catálogo", str(total_prods), self.colors["sidebar"]),
        ]:
            c = stat_card(self.stats_frame, title, val, color)
            c.pack(side="left", expand=True, fill="both", padx=5)

        for i in self.tree_low.get_children():
            self.tree_low.delete(i)
        for r in self.db.cursor.execute(
            "SELECT nombre, categoria, stock FROM materiales WHERE stock <= ? ORDER BY stock ASC LIMIT 15",
            (STOCK_MINIMO_ALERTA,)
        ).fetchall():
            self.tree_low.insert("", "end", values=(r[0], r[1] or "-", r[2]))

        for i in self.tree_rec.get_children():
            self.tree_rec.delete(i)
        for r in self.db.cursor.execute(
            'SELECT h.fecha_hora, IFNULL(m.nombre,"SISTEMA"), h.tipo_accion, h.cantidad '
            'FROM historial_movimientos h LEFT JOIN materiales m ON h.material_id=m.id '
            'ORDER BY h.id DESC LIMIT 15'
        ).fetchall():
            self.tree_rec.insert("", "end", values=r)

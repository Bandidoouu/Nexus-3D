import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from nexus3d.db.database import DatabaseManager
from nexus3d.ui.widgets import ScrollableFrame, HoverButton, build_logo_canvas
from nexus3d.ui.pages.dashboard import DashboardPage
from nexus3d.ui.pages.stock import StockPage
from nexus3d.ui.pages.materiales import MaterialesPage
from nexus3d.ui.pages.perfil import PerfilPage
from nexus3d.ui.pages.entradas import EntradasPage
from nexus3d.ui.pages.salidas import SalidasPage
from nexus3d.ui.pages.productos_stock import ProductosStockPage
from nexus3d.ui.pages.nuevo_producto_stock import NuevoProductoStockPage
from nexus3d.ui.pages.cotizacion import CotizacionPage
from nexus3d.ui.pages.cotizaciones_lista import CotizacionesListaPage
from nexus3d.ui.pages.historial import HistorialPage

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

MENU_ITEMS = [
    ("🏠  Dashboard",        "dashboard"),
    ("📦  Stock Actual",      "stock"),
    ("📂  Catálogo Maestro",  "materiales"),
    ("➕  Nuevo Perfil",      "perfil"),
    ("📥  Entradas",          "entradas"),
    ("📤  Salidas",           "salidas"),
    ("🏭  Productos Stock",   "productos_stock"),
    ("⚖️  Cotización",        "cotizacion"),
    ("📋  Mis Cotizaciones",  "cotizaciones_lista"),
    ("📊  Historial",         "historial"),
]

PAGE_CLASSES = {
    "dashboard":            DashboardPage,
    "stock":                StockPage,
    "materiales":           MaterialesPage,
    "perfil":               PerfilPage,
    "entradas":             EntradasPage,
    "salidas":              SalidasPage,
    "productos_stock":      ProductosStockPage,
    "nuevo_producto_stock": NuevoProductoStockPage,
    "cotizacion":           CotizacionPage,
    "cotizaciones_lista":   CotizacionesListaPage,
    "historial":            HistorialPage,
}

# sidebar hover color (slightly lighter than sidebar bg)
_SIDEBAR_HOVER = "#3d5166"


class InventoryApp:
    def __init__(self, root):
        self.db = DatabaseManager()
        self.root = root
        self.root.title("Nexus 3D — Pro System")
        self.root.geometry("1300x820")
        self.root.configure(bg="#2c3e50")
        self.root.minsize(1000, 640)

        self.colors = {
            "bg":         "#f5f6fa",
            "sidebar":    "#2c3e50",
            "accent":     "#1abc9c",
            "card":       "#ffffff",
            "shadow":     "#dcdde1",
            "text_main":  "#2f3542",
            "text_light": "#7f8c8d",
            "danger":     "#e74c3c",
            "warning":    "#f39c12",
            "info":       "#3498db",
        }

        self._active_page = None
        self._setup_styles()
        self._build_layout()
        self._init_pages()
        self.show_page("dashboard")

    # ── Styles ────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("Treeview", background="white",
                    foreground=self.colors["text_main"],
                    rowheight=26, fieldbackground="white",
                    font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background="#ecf0f1",
                    font=("Segoe UI Bold", 9), relief="flat")
        s.configure("TCombobox", fieldbackground="#f1f2f6", relief="flat")
        s.map("Treeview", background=[("selected", self.colors["accent"])])
        s.configure("Vertical.TScrollbar", background="#dcdde1",
                    troughcolor="#f5f6fa", relief="flat", arrowsize=12)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self):
        self._build_header()
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True)
        self._build_sidebar(main)
        self._build_content(main)
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=self.colors["sidebar"], height=58)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # cube logo
        logo_canvas = build_logo_canvas(hdr, self.colors["accent"], self.colors["sidebar"], size=34)
        logo_canvas.pack(side="left", padx=(16, 6), pady=10)

        # brand name
        brand = tk.Frame(hdr, bg=self.colors["sidebar"])
        brand.pack(side="left", pady=8)
        tk.Label(brand, text="NEXUS", fg=self.colors["accent"], bg=self.colors["sidebar"],
                 font=("Segoe UI Black", 17), pady=0).pack(anchor="sw", side="left")
        tk.Label(brand, text=" 3D", fg="white", bg=self.colors["sidebar"],
                 font=("Segoe UI Black", 17), pady=0).pack(anchor="sw", side="left")

        # right side: version + time
        right = tk.Frame(hdr, bg=self.colors["sidebar"])
        right.pack(side="right", padx=20)
        tk.Label(right, text="v2.0", fg=self.colors["text_light"], bg=self.colors["sidebar"],
                 font=("Segoe UI", 8)).pack(anchor="e")
        self._lbl_clock = tk.Label(right, fg=self.colors["text_light"],
                                   bg=self.colors["sidebar"], font=("Segoe UI", 8))
        self._lbl_clock.pack(anchor="e")
        self._tick_clock()

        # accent underline
        tk.Frame(self.root, bg=self.colors["accent"], height=2).pack(fill="x")

    def _tick_clock(self):
        self._lbl_clock.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.colors["sidebar"], width=230)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        # section label
        tk.Label(sidebar, text="NAVEGACIÓN", fg="#566b7d", bg=self.colors["sidebar"],
                 font=("Segoe UI Bold", 7), padx=20).pack(anchor="w", pady=(18, 4))

        self.nav_buttons = {}
        self._nav_indicators = {}

        for text, page_id in MENU_ITEMS:
            row = tk.Frame(sidebar, bg=self.colors["sidebar"])
            row.pack(fill="x")

            # left active indicator bar
            indicator = tk.Frame(row, bg=self.colors["sidebar"], width=3)
            indicator.pack(side="left", fill="y")
            self._nav_indicators[page_id] = indicator

            btn = HoverButton(
                row,
                normal_bg=self.colors["sidebar"],
                hover_bg=_SIDEBAR_HOVER,
                normal_fg="#bdc3c7",
                hover_fg="#ffffff",
                text=text,
                font=("Segoe UI Bold", 10),
                padx=16, pady=11,
                anchor="w",
                command=lambda p=page_id: self.show_page(p),
            )
            btn.pack(fill="x", expand=True)
            self.nav_buttons[page_id] = btn

        # bottom section: DB name
        tk.Frame(sidebar, bg="#1a252f", height=1).pack(fill="x", pady=(12, 0))
        tk.Label(sidebar, text="inventario_materiales.db", fg="#566b7d",
                 bg=self.colors["sidebar"], font=("Segoe UI", 7),
                 padx=20).pack(anchor="w", pady=8)

    def _build_content(self, parent):
        self.content_area = tk.Frame(parent, bg=self.colors["bg"])
        self.content_area.pack(fill="both", expand=True, side="right")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg="#1a252f", height=22)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self._lbl_status = tk.Label(bar, text="Listo", fg="#7f8c8d",
                                    bg="#1a252f", font=("Segoe UI", 8),
                                    padx=12)
        self._lbl_status.pack(side="left", fill="y")
        tk.Label(bar, text="Nexus 3D Pro  •  SQLite", fg="#566b7d",
                 bg="#1a252f", font=("Segoe UI", 8), padx=12).pack(side="right")

    # ── Pages ─────────────────────────────────────────────────────────────────

    def _init_pages(self):
        self.scroll_frames = {}
        self.page_objects = {}
        for page_id, PageClass in PAGE_CLASSES.items():
            sf = ScrollableFrame(self.content_area, bg=self.colors["bg"])
            sf.grid(row=0, column=0, sticky="nsew")
            self.scroll_frames[page_id] = sf
            self.page_objects[page_id] = PageClass(self, sf)

    def show_page(self, page_id):
        self.scroll_frames[page_id].tkraise()

        # reset all nav buttons
        for pid, btn in self.nav_buttons.items():
            btn.force_active(False)
            self._nav_indicators[pid].configure(bg=self.colors["sidebar"])

        active_nav = page_id if page_id in self.nav_buttons else "productos_stock"
        self.nav_buttons[active_nav].force_active(True)
        self._nav_indicators[active_nav].configure(bg=self.colors["accent"])

        self._active_page = page_id
        self.page_objects[page_id].refresh()

    def set_status(self, msg: str):
        try:
            self._lbl_status.configure(
                text=f"✓  {msg}  —  {datetime.now().strftime('%H:%M')}"
            )
        except tk.TclError:
            pass

    def refresh_all(self):
        for page in self.page_objects.values():
            page.refresh()

    # ── Excel exports ─────────────────────────────────────────────────────────

    def _excel_export(self, filename_default, build_fn):
        if not EXCEL_AVAILABLE:
            messagebox.showerror("Error", "Instala openpyxl: python -m pip install openpyxl")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=filename_default,
        )
        if not path:
            return
        wb = openpyxl.Workbook()
        build_fn(wb.active)
        wb.save(path)
        self.set_status(f"Exportado → {path}")
        messagebox.showinfo("Exportado", f"Archivo guardado en:\n{path}")

    def export_historial_excel(self):
        def build(ws):
            ws.title = "Historial"
            ws.append(["Fecha/Hora", "Material", "Categoría", "Acción", "Cantidad", "Nota"])
            for r in self.db.cursor.execute(
                'SELECT h.fecha_hora, IFNULL(m.nombre,"SISTEMA"), IFNULL(m.categoria,"-"), '
                'h.tipo_accion, h.cantidad, h.comentarios '
                'FROM historial_movimientos h LEFT JOIN materiales m ON h.material_id=m.id '
                'ORDER BY h.id DESC'
            ).fetchall():
                ws.append(list(r))
        self._excel_export("historial_nexus3d.xlsx", build)

    def export_materiales_excel(self):
        def build(ws):
            ws.title = "Catálogo"
            ws.append(["ID", "Nombre", "Categoría", "Precio Unit.", "Stock"])
            for r in self.db.cursor.execute(
                "SELECT id, nombre, categoria, precio_unitario, stock FROM materiales ORDER BY categoria, nombre"
            ).fetchall():
                ws.append(list(r))
        self._excel_export("catalogo_nexus3d.xlsx", build)

    def export_cotizaciones_excel(self):
        def build(ws):
            ws.title = "Cotizaciones"
            ws.append(["ID", "Cliente", "Fecha", "Total", "Estado"])
            for r in self.db.cursor.execute(
                "SELECT id, cliente, fecha, total, estado FROM cotizaciones ORDER BY id DESC"
            ).fetchall():
                ws.append(list(r))
        self._excel_export("cotizaciones_nexus3d.xlsx", build)

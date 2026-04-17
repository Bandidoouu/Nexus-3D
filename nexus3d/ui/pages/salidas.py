import tkinter as tk
from tkinter import ttk, messagebox
from nexus3d.ui.pages.base import BasePage
from nexus3d.ui.widgets import HoverButton


class SalidasPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self._build()

    def _build(self):
        f = self.frame
        tk.Label(f, text="Salidas de Stock", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(anchor="w", padx=25, pady=15)
        o, inner = self.card(f, "Registrar Consumo / Venta")
        o.pack(padx=25, pady=5, fill="x")
        grid = tk.Frame(inner, bg="white")
        grid.pack(fill="x")
        for i, (label, attr, kind) in enumerate([
            ("Material:", "combo_mat", "combo"),
            ("Cantidad:", "ent_cant", "entry"),
            ("Motivo:", "ent_nota", "entry"),
        ]):
            tk.Label(grid, text=label, bg="white",
                     font=("Segoe UI Semibold", 9)).grid(row=i, column=0, sticky="w", pady=8)
            if kind == "combo":
                w = ttk.Combobox(grid, width=40, state="readonly")
            else:
                w = tk.Entry(grid, width=43, bg="#f8f9fa", bd=0,
                             highlightthickness=1, font=("Segoe UI Bold", 9))
            w.grid(row=i, column=1, pady=8, padx=10)
            setattr(self, attr, w)

        tipo_f = tk.Frame(inner, bg="white")
        tipo_f.pack(fill="x", pady=(0, 5))
        tk.Label(tipo_f, text="Tipo:", bg="white", font=("Segoe UI Semibold", 9)).pack(side="left")
        self.combo_tipo = ttk.Combobox(tipo_f, width=20, state="readonly",
                                       values=["SALIDA", "VENTA", "AJUSTE"])
        self.combo_tipo.set("SALIDA")
        self.combo_tipo.pack(side="left", padx=10)

        HoverButton(inner, normal_bg=self.colors["danger"], hover_bg="#c0392b",
                    text="CONFIRMAR SALIDA", font=("Segoe UI Black", 10),
                    padx=30, pady=8, command=self.process).pack(pady=10)

    def refresh(self):
        mats = self.db.get_materiales()
        self.combo_mat['values'] = [f"{r[0]} | {r[1]}" for r in mats]

    def process(self):
        s = self.combo_mat.get()
        if not s:
            messagebox.showwarning("Validación", "Seleccione un material.")
            return
        try:
            qty = float(self.ent_cant.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido.")
            return
        if qty <= 0:
            messagebox.showwarning("Validación", "La cantidad debe ser mayor a 0.")
            return
        m_id = int(s.split(" | ")[0])
        stock_actual = self.db.get_stock(m_id)
        if qty > stock_actual:
            if not messagebox.askyesno("Stock insuficiente",
                                        f"Stock disponible: {stock_actual}. ¿Continuar de todas formas?"):
                return
        tipo = self.combo_tipo.get()
        nombre = s.split(" | ")[1]
        self.db.update_stock(m_id, -qty)
        self.db.registrar_movimiento(m_id, tipo, qty, self.ent_nota.get())
        self.ent_cant.delete(0, tk.END)
        self.ent_nota.delete(0, tk.END)
        self.app.set_status(f"{tipo} registrada: -{qty} de {nombre}")
        self.app.refresh_all()

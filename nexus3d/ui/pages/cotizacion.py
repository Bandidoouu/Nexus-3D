import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from nexus3d.ui.pages.base import BasePage
from nexus3d.logic.calculadora import calc_filament_cost, calc_piece_cost


class CotizacionPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self.temp_mats = []
        self.lines = []
        self.color_entries = []
        self._build()

    def _build(self):
        f = self.frame
        tk.Label(f, text="Nueva Cotización", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(anchor="w", padx=25, pady=10)

        row = tk.Frame(f, bg=self.colors["bg"])
        row.pack(fill="x", padx=25)

        o_p, i_p = self.card(row, "Params")
        o_p.pack(side="left", fill="both", expand=True)
        fields = [("Pieza:", "ent_piece"), ("Horas:", "ent_hours"),
                  ("Colores:", "ent_colors"), ("Lote:", "ent_batch"),
                  ("Ganancia x:", "ent_ganancia")]
        for i, (label, attr) in enumerate(fields):
            tk.Label(i_p, text=label, bg="white",
                     font=("Segoe UI Semibold", 8)).grid(row=i, column=0, sticky="w", pady=2)
            e = tk.Entry(i_p, width=17, bg="#f8f9fa", bd=0,
                         highlightthickness=1, font=("Segoe UI Bold", 8))
            e.grid(row=i, column=1, pady=2, padx=5, sticky="e")
            setattr(self, attr, e)
            if any(x in attr for x in ["hours", "batch", "colors"]):
                e.insert(0, "1")
            if "ganancia" in attr:
                e.insert(0, "3")
            if "colors" in attr:
                e.bind("<KeyRelease>", self._update_color_slots)

        tk.Label(i_p, text="Total g:", bg="white",
                 font=("Segoe UI Semibold", 8)).grid(row=len(fields), column=0, sticky="w")
        self.ent_filament_grams = tk.Entry(i_p, width=17, state="readonly", bg="#ecf0f1",
                                           bd=0, font=("Segoe UI Bold", 8), justify="center")
        self.ent_filament_grams.grid(row=len(fields), column=1, pady=5)

        o_c, i_c = self.card(row, "Filamentos")
        o_c.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.color_frame = tk.Frame(i_c, bg="white")
        self.color_frame.pack(fill="both", expand=True)
        self.lbl_total_g = tk.Label(i_c, text="TOTAL: 0g", font=("Segoe UI Black", 9),
                                    bg=self.colors["accent"], fg="white")
        self.lbl_total_g.pack(fill="x")

        o_m, i_m = self.card(f, "Materiales Extra")
        o_m.pack(fill="x", padx=25, pady=(5, 0))
        mat_row = tk.Frame(i_m, bg="white")
        mat_row.pack(fill="x")
        tk.Label(mat_row, text="Material:", bg="white", font=("Segoe UI Semibold", 8)).pack(side="left")
        self.combo_mat = ttk.Combobox(mat_row, width=25, state="readonly")
        self.combo_mat.pack(side="left", padx=5)
        tk.Label(mat_row, text="Qty:", bg="white", font=("Segoe UI Semibold", 8)).pack(side="left")
        self.ent_mat_qty = tk.Entry(mat_row, width=6, bg="#f8f9fa", bd=0,
                                    highlightthickness=1, font=("Segoe UI Bold", 8))
        self.ent_mat_qty.insert(0, "1")
        self.ent_mat_qty.pack(side="left", padx=5)
        tk.Button(mat_row, text="+ Agregar", bg=self.colors["info"], fg="white",
                 font=("Segoe UI Bold", 8), bd=0, padx=8, pady=3,
                 command=self._add_mat).pack(side="left")
        self.tree_temp_mats = ttk.Treeview(i_m, columns=("nombre", "cant", "costo"),
                                            show="headings", height=3)
        self.tree_temp_mats.pack(fill="x", pady=5)
        for col, heading, width in [("nombre", "Material", 180), ("cant", "Cantidad", 80), ("costo", "Costo", 80)]:
            self.tree_temp_mats.heading(col, text=heading)
            self.tree_temp_mats.column(col, width=width)

        tk.Button(f, text="⚡ CALCULAR Y AGREGAR", bg=self.colors["sidebar"],
                 fg=self.colors["accent"], font=("Segoe UI Black", 10), bd=0, pady=8,
                 command=self.calculate).pack(fill="x", padx=25, pady=5)

        t_row = tk.Frame(f, bg=self.colors["bg"])
        t_row.pack(fill="x", padx=25)
        self.tree_final = ttk.Treeview(t_row, columns=("pieza", "lote", "costo"),
                                       show="headings", height=4)
        self.tree_final.pack(fill="both", expand=True)
        for col, heading, width in [("pieza", "Pieza", 200), ("lote", "Lote", 80), ("costo", "Costo Lote", 120)]:
            self.tree_final.heading(col, text=heading)
            self.tree_final.column(col, width=width)

        o_f, i_f = self.card(f)
        o_f.pack(fill="x", padx=25, pady=10)
        tk.Label(i_f, text="Cliente:", bg="white", font=("Segoe UI Semibold", 8)).pack(side="left")
        self.ent_client = tk.Entry(i_f, width=20, font=("Segoe UI Bold", 9), bg="#f1f2f6", bd=0)
        self.ent_client.pack(side="left", padx=5)
        self.lbl_grand_total = tk.Label(i_f, text="TOTAL: $0.00", font=("Segoe UI Black", 12),
                                        bg="white", fg=self.colors["accent"])
        self.lbl_grand_total.pack(side="left", padx=15)
        tk.Button(i_f, text="🗑 Limpiar", bg=self.colors["danger"], fg="white",
                 font=("Segoe UI Black", 9), padx=15, pady=8,
                 command=self.clear).pack(side="right", padx=5)
        tk.Button(i_f, text="💾 GUARDAR COTIZACIÓN", bg=self.colors["sidebar"], fg="white",
                 font=("Segoe UI Black", 9), padx=20, pady=8,
                 command=self.save).pack(side="right")

        self._update_color_slots()

    def refresh(self):
        mats = self.db.get_materiales()
        filamentos = [f"{r[0]} | {r[1]}" for r in mats if r[2] and "filamento" in r[2].lower()]
        non_filament = [f"{r[0]} | {r[1]}" for r in mats if not r[2] or "filamento" not in r[2].lower()]
        self.combo_mat['values'] = non_filament
        for entry in self.color_entries:
            entry['combo']['values'] = filamentos

    def _update_color_slots(self, e=None):
        try:
            num = min(max(int(self.ent_colors.get() or 1), 1), 12)
        except ValueError:
            return
        for w in self.color_frame.winfo_children():
            w.destroy()
        mats = self.db.get_materiales()
        filamentos = [f"{r[0]} | {r[1]}" for r in mats if r[2] and "filamento" in r[2].lower()]
        self.color_entries = []
        for i in range(num):
            cell = tk.Frame(self.color_frame, bg="white")
            cell.grid(row=i // 2, column=i % 2, padx=2, pady=1)
            combo = ttk.Combobox(cell, width=10, state="readonly", values=filamentos)
            combo.pack(side="left")
            g = tk.Entry(cell, width=4, bd=0, highlightthickness=1)
            g.pack(side="left")
            g.insert(0, "0")
            g.bind("<KeyRelease>", self._update_total_g)
            self.color_entries.append({'gramos': g, 'combo': combo})
        self._update_total_g()

    def _update_total_g(self, e=None):
        try:
            t = sum(float(x['gramos'].get() or 0) for x in self.color_entries)
        except ValueError:
            t = 0
        self.lbl_total_g.config(text=f"TOTAL: {t:.1f}g")
        self.ent_filament_grams.config(state="normal")
        self.ent_filament_grams.delete(0, tk.END)
        self.ent_filament_grams.insert(0, f"{t:.1f}")
        self.ent_filament_grams.config(state="readonly")

    def _add_mat(self):
        s = self.combo_mat.get()
        if not s:
            return
        m_id = int(s.split(" | ")[0])
        try:
            qty = float(self.ent_mat_qty.get() or 1)
        except ValueError:
            qty = 1
        r = self.db.cursor.execute(
            "SELECT nombre, precio_unitario FROM materiales WHERE id=?", (m_id,)
        ).fetchone()
        if r:
            self.temp_mats.append({"id": m_id, "nombre": r[0], "cantidad": qty, "costo": r[1] * qty})
            self._refresh_temp_table()

    def _refresh_temp_table(self):
        for i in self.tree_temp_mats.get_children():
            self.tree_temp_mats.delete(i)
        for m in self.temp_mats:
            self.tree_temp_mats.insert("", "end", values=(m['nombre'], m['cantidad'], f"${m['costo']:.2f}"))

    def calculate(self):
        try:
            n = self.ent_piece.get() or "Pieza"
            h = float(self.ent_hours.get() or 0)
            l = int(self.ent_batch.get() or 1)
            m = float(self.ent_ganancia.get() or 1)
            c_f = calc_filament_cost(self.color_entries, self.db)
            extra = sum(x['costo'] for x in self.temp_mats)
            tot = calc_piece_cost(h, c_f, extra, m)
            self.lines.append({"nombre": n, "lote": l, "costo_lote": tot,
                                "mats": list(self.temp_mats)})
            self._refresh_final_table()
            self.temp_mats = []
            self._refresh_temp_table()
        except (ValueError, TypeError) as ex:
            messagebox.showerror("Error de cálculo", f"Verifique los valores ingresados: {ex}")

    def _refresh_final_table(self):
        for i in self.tree_final.get_children():
            self.tree_final.delete(i)
        gt = 0
        for p in self.lines:
            self.tree_final.insert("", "end", values=(p['nombre'], p['lote'], f"${p['costo_lote']:.2f}"))
            gt += p['costo_lote']
        self.lbl_grand_total.config(text=f"TOTAL: ${gt:.2f}")

    def clear(self):
        self.lines = []
        self.temp_mats = []
        self._refresh_final_table()
        self._refresh_temp_table()

    def save(self):
        if not self.lines:
            messagebox.showwarning("Vacío", "Agregue al menos una pieza a la cotización.")
            return
        total = sum(p['costo_lote'] for p in self.lines)
        self.db.cursor.execute(
            'INSERT INTO cotizaciones (cliente, fecha, total, estado) VALUES (?,?,?,?)',
            (self.ent_client.get() or "Sin nombre", datetime.now().strftime("%Y-%m-%d"),
             total, "Guardada")
        )
        q_id = self.db.cursor.lastrowid
        for p in self.lines:
            for mat in p['mats']:
                self.db.cursor.execute(
                    'INSERT INTO cotizacion_detalles (cotizacion_id, material_id, cantidad, costo_total) VALUES (?,?,?,?)',
                    (q_id, mat['id'], mat['cantidad'], mat['costo'])
                )
        self.db.conn.commit()
        self.clear()
        self.app.set_status(f"Cotización #{q_id} guardada — Total: ${total:.2f}")
        self.app.refresh_all()
        messagebox.showinfo("Guardado", f"Cotización #{q_id} guardada. Total: ${total:.2f}")

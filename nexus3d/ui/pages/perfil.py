import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from nexus3d.ui.pages.base import BasePage
from nexus3d.ui.widgets import HoverButton


class PerfilPage(BasePage):
    def __init__(self, app, scroll_frame):
        super().__init__(app, scroll_frame)
        self.editing_id = None
        self._build()

    def _build(self):
        f = self.frame
        tk.Label(f, text="Gestor de Perfiles", font=("Segoe UI Black", 16),
                 bg=self.colors["bg"]).pack(anchor="w", padx=25, pady=15)
        o, self.form_outer = self.card(f, "Registrar/Editar Material")
        o.pack(padx=25, pady=5, fill="x")

        mode_f = tk.Frame(self.form_outer, bg="white")
        mode_f.pack(anchor="w", pady=(0, 10))
        self.btn_create = tk.Button(mode_f, text="CREAR", bg=self.colors["accent"], fg="white",
                                    font=("Segoe UI Black", 9), bd=0, padx=15, pady=5,
                                    command=lambda: self.switch_mode("create"))
        self.btn_create.pack(side="left")
        self.btn_edit = tk.Button(mode_f, text="EDITAR", bg=self.colors["sidebar"], fg="#bdc3c7",
                                  font=("Segoe UI Black", 9), bd=0, padx=15, pady=5,
                                  command=lambda: self.switch_mode("edit"))
        self.btn_edit.pack(side="left", padx=5)
        tk.Button(mode_f, text="+ CAT", bg=self.colors["info"], fg="white",
                 font=("Segoe UI Black", 9), bd=0, padx=15, pady=5,
                 command=self.add_category_dialog).pack(side="left")

        self.lbl_select = tk.Label(self.form_outer, text="Seleccionar:", bg="white",
                                   font=("Segoe UI Bold", 8))
        self.combo_edit = ttk.Combobox(self.form_outer, width=50, state="readonly")
        self.combo_edit.bind("<<ComboboxSelected>>", self._load_for_edit)

        self.form_grid = tk.Frame(self.form_outer, bg="white")
        self.form_grid.pack(fill="x")
        for i, (label, attr, kind) in enumerate([
            ("Nombre:", "ent_nombre", "entry"),
            ("Categoría:", "ent_cat", "combo"),
            ("Precio:", "ent_precio", "entry"),
        ]):
            tk.Label(self.form_grid, text=label, bg="white",
                     font=("Segoe UI Semibold", 9)).grid(row=i, column=0, sticky="w", pady=4)
            if kind == "combo":
                w = ttk.Combobox(self.form_grid, width=38, state="readonly",
                                 font=("Segoe UI Bold", 9))
            else:
                w = tk.Entry(self.form_grid, width=40, bg="#f8f9fa", bd=0,
                             highlightthickness=1, font=("Segoe UI Bold", 9))
            w.grid(row=i, column=1, pady=4, padx=10, sticky="w")
            setattr(self, attr, w)

        tk.Label(self.form_grid, text="Notas:", bg="white",
                 font=("Segoe UI Semibold", 9)).grid(row=3, column=0, sticky="nw", pady=5)
        self.txt_desc = tk.Text(self.form_grid, width=50, height=3, bg="#f8f9fa", bd=0,
                                font=("Segoe UI Bold", 9))
        self.txt_desc.grid(row=3, column=1, pady=5, padx=10)

        self.btn_save = HoverButton(self.form_outer,
                                   normal_bg=self.colors["accent"], hover_bg="#16a085",
                                   text="GUARDAR", font=("Segoe UI Black", 10),
                                   padx=30, pady=8, command=self.save)
        self.btn_save.pack(anchor="e", pady=10)
        self.switch_mode("create")

    def refresh(self):
        mats = self.db.get_materiales()
        cats = sorted(set(r[2] for r in mats if r[2]))
        self.ent_cat['values'] = cats
        self.combo_edit['values'] = [f"{r[0]} | {r[1]}" for r in mats]

    def switch_mode(self, mode):
        self._clear_form()
        if mode == "create":
            self.btn_create.config(bg=self.colors["accent"], fg="white")
            self.btn_edit.config(bg=self.colors["sidebar"], fg="#bdc3c7")
            self.btn_save.config(text="CREAR", bg=self.colors["accent"])
            self.lbl_select.pack_forget()
            self.combo_edit.pack_forget()
        else:
            self.btn_create.config(bg=self.colors["sidebar"], fg="#bdc3c7")
            self.btn_edit.config(bg=self.colors["accent"], fg="white")
            self.btn_save.config(text="GUARDAR CAMBIOS", bg="#e67e22")
            self.lbl_select.pack(before=self.form_grid, anchor="w")
            self.combo_edit.pack(before=self.form_grid, anchor="w", pady=(0, 10))

    def add_category_dialog(self):
        n = simpledialog.askstring("Categoría", "Nombre:")
        if n:
            existing = list(self.ent_cat['values'])
            existing.append(n.capitalize())
            self.ent_cat['values'] = existing
            self.ent_cat.set(n.capitalize())

    def _load_for_edit(self, e=None):
        val = self.combo_edit.get()
        if not val:
            return
        m_id = int(val.split(" | ")[0])
        self.editing_id = m_id
        r = self.db.get_material_by_id(m_id)
        if r:
            self.ent_nombre.delete(0, tk.END)
            self.ent_nombre.insert(0, r[0])
            self.ent_cat.set(r[1])
            self.ent_precio.delete(0, tk.END)
            self.ent_precio.insert(0, str(r[2]))
            self.txt_desc.delete("1.0", tk.END)
            self.txt_desc.insert("1.0", r[3] or "")

    def save(self):
        n = self.ent_nombre.get().strip()
        c = self.ent_cat.get().strip()
        d = self.txt_desc.get("1.0", tk.END).strip()
        if not n or not c:
            messagebox.showwarning("Validación", "Nombre y Categoría son obligatorios.")
            return
        try:
            p = float(self.ent_precio.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido.")
            return
        if self.editing_id:
            self.db.cursor.execute(
                'UPDATE materiales SET nombre=?, categoria=?, descripcion=?, precio_unitario=? WHERE id=?',
                (n, c, d, p, self.editing_id)
            )
            self.db.registrar_movimiento(self.editing_id, "EDICIÓN", 0, n)
        else:
            self.db.cursor.execute(
                'INSERT INTO materiales (nombre, categoria, descripcion, precio_unitario, stock) VALUES (?,?,?,?,0)',
                (n, c, d, p)
            )
            self.db.registrar_movimiento(self.db.cursor.lastrowid, "CREACIÓN", 0, n)
        self.db.conn.commit()
        self._clear_form()
        self.app.set_status(f"Material '{n}' guardado correctamente")
        self.app.refresh_all()

    def _clear_form(self):
        self.ent_nombre.delete(0, tk.END)
        self.ent_cat.set('')
        self.ent_precio.delete(0, tk.END)
        self.txt_desc.delete("1.0", tk.END)
        self.combo_edit.set('')
        self.editing_id = None

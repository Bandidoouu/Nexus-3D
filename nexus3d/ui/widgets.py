import tkinter as tk
from tkinter import ttk


# ── Color utilities ──────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )


# ── Animated hover button ─────────────────────────────────────────────────────

class HoverButton(tk.Button):
    STEPS = 8
    DELAY = 12  # ms per frame

    def __init__(self, parent, normal_bg, hover_bg,
                 normal_fg="#ffffff", hover_fg="#ffffff", **kwargs):
        self._n_bg = normal_bg
        self._h_bg = hover_bg
        self._n_fg = normal_fg
        self._h_fg = hover_fg
        self._job = None
        self._t = 0.0
        super().__init__(parent, bg=normal_bg, fg=normal_fg,
                         relief="flat", bd=0, cursor="hand2",
                         activebackground=hover_bg, activeforeground=hover_fg,
                         **kwargs)
        self.bind("<Enter>", self._hover_in)
        self.bind("<Leave>", self._hover_out)

    def _cancel(self):
        if self._job:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    def _hover_in(self, _=None):
        self._cancel()
        self._animate(1)

    def _hover_out(self, _=None):
        self._cancel()
        self._animate(-1)

    def _animate(self, direction):
        self._t = max(0.0, min(1.0, self._t + direction / self.STEPS))
        try:
            self.configure(
                bg=lerp_color(self._n_bg, self._h_bg, self._t),
                fg=lerp_color(self._n_fg, self._h_fg, self._t),
            )
        except tk.TclError:
            return
        if (direction == 1 and self._t < 1.0) or (direction == -1 and self._t > 0.0):
            self._job = self.after(self.DELAY, lambda: self._animate(direction))

    def force_active(self, active: bool):
        self._cancel()
        self._t = 1.0 if active else 0.0
        try:
            self.configure(
                bg=self._h_bg if active else self._n_bg,
                fg=self._h_fg if active else self._n_fg,
            )
        except tk.TclError:
            pass


# ── Nexus 3D canvas logo ──────────────────────────────────────────────────────

def build_logo_canvas(parent, accent="#1abc9c", sidebar="#2c3e50", size=38):
    c = tk.Canvas(parent, width=size + 4, height=size + 4,
                  bg=sidebar, highlightthickness=0)
    cx, cy = (size + 4) / 2, (size + 4) / 2
    s = size * 0.38  # half-edge

    # isometric cube — 3 visible faces
    top  = [cx,        cy - s * 1.15,
            cx + s,    cy - s * 0.58,
            cx,        cy,
            cx - s,    cy - s * 0.58]
    right = [cx,       cy,
             cx + s,   cy - s * 0.58,
             cx + s,   cy + s * 0.58,
             cx,       cy + s * 1.15]
    left  = [cx - s,   cy - s * 0.58,
             cx,       cy,
             cx,       cy + s * 1.15,
             cx - s,   cy + s * 0.58]

    # lighter top, medium right, darker left
    top_col   = lerp_color(accent, "#ffffff", 0.35)
    right_col = accent
    left_col  = lerp_color(accent, "#000000", 0.28)

    c.create_polygon(top,   fill=top_col,   outline="")
    c.create_polygon(right, fill=right_col, outline="")
    c.create_polygon(left,  fill=left_col,  outline="")
    return c


# ── Scrollable frame ──────────────────────────────────────────────────────────

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg="#f5f6fa", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=bg)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind("<Enter>", lambda e: canvas.bind_all(
            "<MouseWheel>", lambda ev: canvas.yview_scroll(-1 * (ev.delta // 120), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))


# ── Shadow card ───────────────────────────────────────────────────────────────

def create_shadow_card(parent, colors, title=""):
    outer = tk.Frame(parent, bg=colors["shadow"], padx=1, pady=1)
    inner = tk.Frame(outer, bg="white", padx=12, pady=12)
    inner.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
    if title:
        lbl = tk.Label(inner, text=title, font=("Segoe UI Black", 11),
                       bg="white", fg=colors["sidebar"])
        lbl.pack(anchor="w", pady=(0, 8))
        outer.card_label = lbl
    content = tk.Frame(inner, bg="white")
    content.pack(fill="both", expand=True)
    # subtle hover border
    outer.bind("<Enter>", lambda e: outer.configure(bg=colors["accent"]))
    outer.bind("<Leave>", lambda e: outer.configure(bg=colors["shadow"]))
    return outer, content


# ── Stat card with count-up animation ────────────────────────────────────────

def stat_card(parent, title, value, color):
    f = tk.Frame(parent, bg=color, padx=18, pady=14)
    tk.Label(f, text=title, bg=color, fg="white",
             font=("Segoe UI Bold", 9)).pack(anchor="w")
    lbl_val = tk.Label(f, text="0", bg=color, fg="white",
                       font=("Segoe UI Black", 22))
    lbl_val.pack(anchor="w")
    # count-up if numeric
    try:
        target = int(value)
        _count_up(lbl_val, target, color)
    except (ValueError, TypeError):
        lbl_val.configure(text=value)
    return f


def _count_up(label, target, color, step=0, steps=18, delay=25):
    val = int(target * step / steps)
    try:
        label.configure(text=str(val))
    except tk.TclError:
        return
    if step < steps:
        label.after(delay, lambda: _count_up(label, target, color, step + 1, steps, delay))
    else:
        try:
            label.configure(text=str(target))
        except tk.TclError:
            pass

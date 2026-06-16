import tkinter as tk
from tkinter import ttk
import math

# ============================================================
# PEMBANGKITAN KURVA KONIK PARAMETRIK - PYTHON TKINTER
#
# Fitur:
# - Lingkaran, Elips, Parabola, Hiperbola
# - Animasi gambar bertahap, tidak langsung jadi
# - Proses Inisialisasi, Iterasi, Kalkulasi, Rendering
# - Panel "Proses Iterasi Saat Ini" yang berubah saat animasi berjalan
# - Tabel titik contoh dan detail perhitungan
# - Zoom, drag, reset, auto fit
# ============================================================


class Color:
    MIDNIGHT = "#212842"
    VANILLA = "#F0E7D5"
    VANILLA_LIGHT = "#FFF9EF"
    VANILLA_SOFT = "#F7F0E3"
    LINE = "#CDBFA8"
    GRID = "#DED2C0"
    MUTED = "#535D76"
    WHITE = "#FFFFFF"


def fmt(value):
    if abs(value) < 1e-10:
        value = 0
    return f"{value:.2f}"


def tick_fmt(value):
    if abs(value) < 1e-10:
        value = 0
    if abs(value) >= 100 or float(value).is_integer():
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def label_theta(theta):
    eps = 1e-8
    if abs(theta) < eps:
        return "0"
    if abs(theta - math.pi / 2) < eps:
        return "pi/2"
    if abs(theta - math.pi) < eps:
        return "pi"
    if abs(theta - 3 * math.pi / 2) < eps:
        return "3pi/2"
    if abs(theta - 2 * math.pi) < eps:
        return "2pi"
    return fmt(theta)


class CurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Animasi Kurva Konik Parametrik - Python")
        self.root.geometry("1360x820")
        self.root.minsize(1120, 700)
        self.root.configure(bg=Color.VANILLA)

        self.scale = 50.0
        self.center_x = 0.0
        self.center_y = 0.0
        self.drag_start = None

        self.animation_job = None
        self.animation_curves = []
        self.animation_curve_index = 0
        self.animation_point_index = 1
        self.animation_iteration = 0
        self.animation_speed = tk.IntVar(value=10)

        self.make_variables()
        self.make_layout()
        self.update_visible_inputs()
        self.refresh_text_and_table()
        self.root.after(200, self.first_run)

    def first_run(self):
        self.auto_fit()
        self.start_animation()

    # ========================================================
    # 1. INISIALISASI VARIABEL
    # ========================================================
    def make_variables(self):
        self.curve_type = tk.StringVar(value="Lingkaran")

        self.xc_var = tk.StringVar(value="0")
        self.yc_var = tk.StringVar(value="0")
        self.r_var = tk.StringVar(value="2")

        self.a_var = tk.StringVar(value="3")
        self.b_var = tk.StringVar(value="2")

        self.xp_var = tk.StringVar(value="0")
        self.yp_var = tk.StringVar(value="0")
        self.t1_var = tk.StringVar(value="-3")
        self.t2_var = tk.StringVar(value="3")

        self.step_var = tk.StringVar(value="0.02")

    # ========================================================
    # LAYOUT
    # ========================================================
    def make_layout(self):
        header = tk.Frame(self.root, bg=Color.MIDNIGHT, padx=22, pady=16)
        header.pack(fill="x", padx=20, pady=(20, 12))

        tk.Label(
            header,
            text="Pembangkitan Kurva Konik Parametrik",
            bg=Color.MIDNIGHT,
            fg=Color.VANILLA,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Kurva muncul bertahap dari proses iterasi, kalkulasi titik, lalu rendering garis.",
            bg=Color.MIDNIGHT,
            fg="#E7DCC7",
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(4, 0))

        main = tk.Frame(self.root, bg=Color.VANILLA)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.left_holder = tk.Frame(main, bg=Color.VANILLA, width=430)
        self.left_holder.pack(side="left", fill="y", padx=(0, 14))
        self.left_holder.pack_propagate(False)

        self.right = tk.Frame(main, bg=Color.VANILLA_LIGHT, highlightbackground=Color.LINE, highlightthickness=1)
        self.right.pack(side="right", fill="both", expand=True)

        self.make_scroll_sidebar()
        self.make_graph_area()

    def make_scroll_sidebar(self):
        self.left_canvas = tk.Canvas(self.left_holder, bg=Color.VANILLA, highlightthickness=0)
        self.left_scroll = ttk.Scrollbar(self.left_holder, orient="vertical", command=self.left_canvas.yview)
        self.sidebar = tk.Frame(self.left_canvas, bg=Color.VANILLA)

        self.sidebar.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )

        self.left_window = self.left_canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=410)
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)

        self.left_canvas.pack(side="left", fill="both", expand=True)
        self.left_scroll.pack(side="right", fill="y")

        self.left_canvas.bind("<Configure>", lambda e: self.left_canvas.itemconfig(self.left_window, width=e.width - 8))
        self.left_canvas.bind_all("<MouseWheel>", self.on_sidebar_scroll)

        self.make_sidebar()

    def on_sidebar_scroll(self, event):
        widget = self.root.focus_get()
        if widget is not None and str(widget).startswith(str(self.left_canvas)):
            self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def card(self, parent):
        frame = tk.Frame(
            parent,
            bg=Color.VANILLA_LIGHT,
            padx=16,
            pady=14,
            highlightbackground=Color.LINE,
            highlightthickness=1
        )
        frame.pack(fill="x", pady=(0, 12))
        return frame

    def title(self, parent, text):
        tk.Label(
            parent,
            text=text,
            bg=Color.VANILLA_LIGHT,
            fg=Color.MIDNIGHT,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 10))

    def make_sidebar(self):
        input_card = self.card(self.sidebar)
        self.title(input_card, "Input Kurva")

        tk.Label(
            input_card,
            text="Jenis Kurva",
            bg=Color.VANILLA_LIGHT,
            fg=Color.MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        self.combo = ttk.Combobox(
            input_card,
            textvariable=self.curve_type,
            values=["Lingkaran", "Elips", "Parabola", "Hiperbola"],
            state="readonly"
        )
        self.combo.pack(fill="x", pady=(4, 10))
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.on_curve_change())

        self.input_frame = tk.Frame(input_card, bg=Color.VANILLA_LIGHT)
        self.input_frame.pack(fill="x")

        self.input_rows = {}
        self.add_input("xc", "xc / pusat X", self.xc_var)
        self.add_input("yc", "yc / pusat Y", self.yc_var)
        self.add_input("r", "r / jari-jari", self.r_var)
        self.add_input("a", "a", self.a_var)
        self.add_input("b", "b", self.b_var)
        self.add_input("xp", "xp / puncak X", self.xp_var)
        self.add_input("yp", "yp / puncak Y", self.yp_var)
        self.add_input("t1", "t1", self.t1_var)
        self.add_input("t2", "t2", self.t2_var)
        self.add_input("step", "step / ketelitian", self.step_var)

        tk.Label(
            input_card,
            text="Kecepatan animasi",
            bg=Color.VANILLA_LIGHT,
            fg=Color.MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(6, 2))

        tk.Scale(
            input_card,
            from_=1,
            to=40,
            orient="horizontal",
            variable=self.animation_speed,
            bg=Color.VANILLA_LIGHT,
            fg=Color.MIDNIGHT,
            highlightthickness=0
        ).pack(fill="x")

        btn_frame = tk.Frame(input_card, bg=Color.VANILLA_LIGHT)
        btn_frame.pack(fill="x", pady=(10, 0))

        self.main_button(btn_frame, "Animasi Gambar", self.start_animation).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.secondary_button(btn_frame, "Stop", self.stop_animation).pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.secondary_button(input_card, "Tampilkan Langsung", self.draw_full_curve).pack(fill="x", pady=(8, 0))

        formula_card = self.card(self.sidebar)
        self.title(formula_card, "Rumus yang Digunakan")

        self.formula_x = tk.Label(formula_card, text="", bg=Color.VANILLA_SOFT, fg=Color.MIDNIGHT, font=("Consolas", 12), padx=10, pady=8)
        self.formula_x.pack(fill="x", pady=(0, 8))

        self.formula_y = tk.Label(formula_card, text="", bg=Color.VANILLA_SOFT, fg=Color.MIDNIGHT, font=("Consolas", 12), padx=10, pady=8)
        self.formula_y.pack(fill="x")

        process_card = self.card(self.sidebar)
        self.title(process_card, "Algoritma Implementasi Program")

        self.process_text = tk.Text(
            process_card,
            height=10,
            wrap="word",
            bg=Color.VANILLA_SOFT,
            fg=Color.MIDNIGHT,
            relief="flat",
            font=("Segoe UI", 10),
            padx=10,
            pady=8
        )
        self.process_text.pack(fill="x")
        self.process_text.configure(state="disabled")

        table_card = self.card(self.sidebar)
        self.title(table_card, "Tabel Perhitungan Titik")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=Color.VANILLA_LIGHT,
            foreground=Color.MIDNIGHT,
            fieldbackground=Color.VANILLA_LIGHT,
            rowheight=24,
            font=("Consolas", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=Color.MIDNIGHT,
            foreground=Color.VANILLA,
            font=("Segoe UI", 10, "bold")
        )

        self.table = ttk.Treeview(table_card, height=5, show="headings")
        self.table.pack(fill="x")

        detail_card = self.card(self.sidebar)
        self.title(detail_card, "Contoh Detail Perhitungan")

        self.detail_label = tk.Label(
            detail_card,
            text="",
            bg=Color.VANILLA_SOFT,
            fg=Color.MIDNIGHT,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=365,
            padx=10,
            pady=10
        )
        self.detail_label.pack(fill="x")

    def main_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=Color.MIDNIGHT,
            fg=Color.VANILLA,
            activebackground="#151B31",
            activeforeground=Color.VANILLA,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=9
        )

    def secondary_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#FFFDF9",
            fg=Color.MIDNIGHT,
            activebackground=Color.VANILLA_SOFT,
            activeforeground=Color.MIDNIGHT,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10),
            padx=10,
            pady=9
        )

    def add_input(self, key, label_text, var):
        row = tk.Frame(self.input_frame, bg=Color.VANILLA_LIGHT)

        tk.Label(
            row,
            text=label_text,
            bg=Color.VANILLA_LIGHT,
            fg=Color.MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        entry = tk.Entry(
            row,
            textvariable=var,
            bg="#FFFDF9",
            fg=Color.MIDNIGHT,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10)
        )
        entry.pack(fill="x", pady=(3, 7))
        entry.bind("<KeyRelease>", lambda e: self.on_input_change())

        self.input_rows[key] = row

    def make_graph_area(self):
        top = tk.Frame(self.right, bg=Color.VANILLA_LIGHT, padx=16, pady=14)
        top.pack(fill="x")

        title_frame = tk.Frame(top, bg=Color.VANILLA_LIGHT)
        title_frame.pack(side="left", anchor="w")

        tk.Label(
            title_frame,
            text="Animasi Gambar Kurva",
            bg=Color.VANILLA_LIGHT,
            fg=Color.MIDNIGHT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Setiap garis muncul dari hasil iterasi dan kalkulasi titik koordinat.",
            bg=Color.VANILLA_LIGHT,
            fg=Color.MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        tools = tk.Frame(top, bg=Color.VANILLA_LIGHT)
        tools.pack(side="right", anchor="e")

        self.tool_button(tools, "− Zoom Out", lambda: self.zoom(0.8))
        self.tool_button(tools, "+ Zoom In", lambda: self.zoom(1.25))
        self.tool_button(tools, "Auto Fit", self.auto_fit)
        self.tool_button(tools, "Reset", self.reset_view)

        self.badge = tk.Label(
            tools,
            text="Lingkaran • theta [0, 2pi]",
            bg=Color.MIDNIGHT,
            fg=Color.VANILLA,
            font=("Segoe UI", 10),
            padx=12,
            pady=8
        )
        self.badge.pack(side="left", padx=(8, 0))

        self.canvas = tk.Canvas(
            self.right,
            bg="#FBF7F0",
            highlightbackground=Color.LINE,
            highlightthickness=1
        )
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        current_card = tk.Frame(
            self.right,
            bg=Color.VANILLA_SOFT,
            highlightbackground=Color.LINE,
            highlightthickness=1,
            padx=14,
            pady=10
        )
        current_card.pack(fill="x", padx=16, pady=(0, 14))

        tk.Label(
            current_card,
            text="Proses Iterasi Saat Ini",
            bg=Color.VANILLA_SOFT,
            fg=Color.MIDNIGHT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        self.current_calc = tk.Label(
            current_card,
            text="Tekan tombol Animasi Gambar untuk melihat proses per titik.",
            bg=Color.VANILLA_SOFT,
            fg=Color.MIDNIGHT,
            font=("Consolas", 10),
            justify="left",
            anchor="w"
        )
        self.current_calc.pack(fill="x", pady=(6, 0))

        self.canvas.bind("<Configure>", lambda e: self.render_grid_only())
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.canvas.bind("<ButtonPress-1>", self.drag_start_event)
        self.canvas.bind("<B1-Motion>", self.drag_move_event)
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.drag_end_event())

    def tool_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg="#FFFDF9",
            fg=Color.MIDNIGHT,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10),
            padx=10,
            pady=7
        )
        btn.pack(side="left", padx=3)

    # ========================================================
    # DATA INPUT
    # ========================================================
    def get_number(self, var):
        return float(var.get().strip().replace(",", "."))

    def get_data(self):
        step = self.get_number(self.step_var)
        if step <= 0:
            step = 0.02

        return {
            "jenis": self.curve_type.get(),
            "xc": self.get_number(self.xc_var),
            "yc": self.get_number(self.yc_var),
            "r": self.get_number(self.r_var),
            "a": self.get_number(self.a_var),
            "b": self.get_number(self.b_var),
            "xp": self.get_number(self.xp_var),
            "yp": self.get_number(self.yp_var),
            "t1": self.get_number(self.t1_var),
            "t2": self.get_number(self.t2_var),
            "step": step
        }

    def on_curve_change(self):
        self.update_visible_inputs()
        self.refresh_text_and_table()
        self.auto_fit()
        self.start_animation()

    def on_input_change(self):
        self.refresh_text_and_table()
        self.render_grid_only()

    def update_visible_inputs(self):
        jenis = self.curve_type.get()

        visible = {
            "xc": jenis in ["Lingkaran", "Elips", "Hiperbola"],
            "yc": jenis in ["Lingkaran", "Elips", "Hiperbola"],
            "r": jenis == "Lingkaran",
            "a": jenis in ["Elips", "Parabola", "Hiperbola"],
            "b": jenis in ["Elips", "Hiperbola"],
            "xp": jenis == "Parabola",
            "yp": jenis == "Parabola",
            "t1": jenis == "Parabola",
            "t2": jenis == "Parabola",
            "step": True
        }

        for key, row in self.input_rows.items():
            row.pack_forget()
            if visible[key]:
                row.pack(fill="x")

    def refresh_text_and_table(self):
        try:
            self.data = self.get_data()
            self.update_formula()
            self.update_process()
            self.update_table()
            self.update_detail()
        except ValueError:
            pass

    # ========================================================
    # RUMUS, PROSES, TABEL
    # ========================================================
    def update_formula(self):
        jenis = self.data["jenis"]

        if jenis == "Lingkaran":
            self.formula_x.config(text="x = xc + r * cos(theta)")
            self.formula_y.config(text="y = yc + r * sin(theta)")
            self.badge.config(text="Lingkaran • theta [0, 2pi]")

        elif jenis == "Elips":
            self.formula_x.config(text="x = xc + a * cos(theta)")
            self.formula_y.config(text="y = yc + b * sin(theta)")
            self.badge.config(text="Elips • theta [0, 2pi]")

        elif jenis == "Parabola":
            self.formula_x.config(text="x = xp + a * t^2")
            self.formula_y.config(text="y = yp + 2 * a * t")
            self.badge.config(text="Parabola • t [t1, t2]")

        else:
            self.formula_x.config(text="x = xc + a * sec(theta)")
            self.formula_y.config(text="y = yc + b * tan(theta)")
            self.badge.config(text="Hiperbola • theta (-pi/2, pi/2)")

    def update_process(self):
        d = self.data
        jenis = d["jenis"]

        if jenis == "Lingkaran":
            init = f"Pusat=({fmt(d['xc'])}, {fmt(d['yc'])}), r={fmt(d['r'])}, step={fmt(d['step'])}"
            iterasi = "theta berjalan dari 0 sampai 2pi."
        elif jenis == "Elips":
            init = f"Pusat=({fmt(d['xc'])}, {fmt(d['yc'])}), a={fmt(d['a'])}, b={fmt(d['b'])}, step={fmt(d['step'])}"
            iterasi = "theta berjalan dari 0 sampai 2pi."
        elif jenis == "Parabola":
            init = f"Puncak=({fmt(d['xp'])}, {fmt(d['yp'])}), a={fmt(d['a'])}, t=[{fmt(d['t1'])}, {fmt(d['t2'])}]"
            iterasi = "t berjalan dari t1 sampai t2."
        else:
            init = f"Pusat=({fmt(d['xc'])}, {fmt(d['yc'])}), a={fmt(d['a'])}, b={fmt(d['b'])}, step={fmt(d['step'])}"
            iterasi = "theta berjalan dari -pi/2 + batas aman sampai pi/2 - batas aman."

        text = (
            "1. Inisialisasi\n"
            f"   {init}\n\n"
            "2. Iterasi\n"
            f"   {iterasi}\n\n"
            "3. Kalkulasi\n"
            "   Setiap nilai parameter dimasukkan ke rumus X dan Y.\n\n"
            "4. Rendering\n"
            "   Garis kurva digambar bertahap dari titik ke titik."
        )

        self.process_text.configure(state="normal")
        self.process_text.delete("1.0", "end")
        self.process_text.insert("1.0", text)
        self.process_text.configure(state="disabled")

    def update_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        jenis = self.data["jenis"]

        if jenis in ["Lingkaran", "Elips"]:
            cols = ("parameter", "cos", "sin", "x", "y")
            self.table["columns"] = cols
            for col in cols:
                self.table.heading(col, text=col)
                self.table.column(col, width=70, anchor="center")

            theta_values = [0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]

            for theta in theta_values:
                cos_v = math.cos(theta)
                sin_v = math.sin(theta)

                if jenis == "Lingkaran":
                    x = self.data["xc"] + self.data["r"] * cos_v
                    y = self.data["yc"] + self.data["r"] * sin_v
                else:
                    x = self.data["xc"] + self.data["a"] * cos_v
                    y = self.data["yc"] + self.data["b"] * sin_v

                self.table.insert("", "end", values=(label_theta(theta), fmt(cos_v), fmt(sin_v), fmt(x), fmt(y)))

        elif jenis == "Parabola":
            cols = ("t", "t^2", "x", "y")
            self.table["columns"] = cols
            for col in cols:
                self.table.heading(col, text=col)
                self.table.column(col, width=85, anchor="center")

            for t in [-2, -1, 0, 1, 2]:
                x = self.data["xp"] + self.data["a"] * t * t
                y = self.data["yp"] + 2 * self.data["a"] * t
                self.table.insert("", "end", values=(fmt(t), fmt(t * t), fmt(x), fmt(y)))

        else:
            cols = ("theta", "sec", "tan", "x", "y")
            self.table["columns"] = cols
            for col in cols:
                self.table.heading(col, text=col)
                self.table.column(col, width=70, anchor="center")

            for theta in [-0.8, -0.4, 0, 0.4, 0.8]:
                sec_v = 1 / math.cos(theta)
                tan_v = math.tan(theta)
                x = self.data["xc"] + self.data["a"] * sec_v
                y = self.data["yc"] + self.data["b"] * tan_v
                self.table.insert("", "end", values=(fmt(theta), fmt(sec_v), fmt(tan_v), fmt(x), fmt(y)))

    def update_detail(self):
        d = self.data
        jenis = d["jenis"]

        if jenis == "Lingkaran":
            text = (
                "Contoh perhitungan lingkaran pada theta = 0:\n\n"
                "x = xc + r * cos(theta)\n"
                f"x = {fmt(d['xc'])} + {fmt(d['r'])} * cos(0)\n"
                f"x = {fmt(d['xc'])} + {fmt(d['r'])} * 1\n"
                f"x = {fmt(d['xc'] + d['r'])}\n\n"
                "y = yc + r * sin(theta)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['r'])} * sin(0)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['r'])} * 0\n"
                f"y = {fmt(d['yc'])}\n\n"
                f"Titik awal: ({fmt(d['xc'] + d['r'])}, {fmt(d['yc'])})"
            )
        elif jenis == "Elips":
            text = (
                "Contoh perhitungan elips pada theta = 0:\n\n"
                "x = xc + a * cos(theta)\n"
                f"x = {fmt(d['xc'])} + {fmt(d['a'])} * 1 = {fmt(d['xc'] + d['a'])}\n\n"
                "y = yc + b * sin(theta)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['b'])} * 0 = {fmt(d['yc'])}\n\n"
                f"Titik awal: ({fmt(d['xc'] + d['a'])}, {fmt(d['yc'])})"
            )
        elif jenis == "Parabola":
            text = (
                "Contoh perhitungan parabola pada t = 1:\n\n"
                "x = xp + a * t^2\n"
                f"x = {fmt(d['xp'])} + {fmt(d['a'])} * 1^2 = {fmt(d['xp'] + d['a'])}\n\n"
                "y = yp + 2 * a * t\n"
                f"y = {fmt(d['yp'])} + 2 * {fmt(d['a'])} * 1 = {fmt(d['yp'] + 2 * d['a'])}\n\n"
                f"Titik contoh: ({fmt(d['xp'] + d['a'])}, {fmt(d['yp'] + 2 * d['a'])})"
            )
        else:
            text = (
                "Contoh perhitungan hiperbola pada theta = 0:\n\n"
                "sec(0) = 1 dan tan(0) = 0\n\n"
                "x = xc + a * sec(theta)\n"
                f"x = {fmt(d['xc'])} + {fmt(d['a'])} * 1 = {fmt(d['xc'] + d['a'])}\n\n"
                "y = yc + b * tan(theta)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['b'])} * 0 = {fmt(d['yc'])}\n\n"
                f"Titik cabang kanan: ({fmt(d['xc'] + d['a'])}, {fmt(d['yc'])})"
            )

        self.detail_label.config(text=text)

    # ========================================================
    # 2. ITERASI + 3. KALKULASI
    # ========================================================
    def make_points(self):
        d = self.data
        jenis = d["jenis"]

        if jenis == "Lingkaran":
            points = []
            theta = 0
            while theta <= 2 * math.pi + d["step"]:
                x = d["xc"] + d["r"] * math.cos(theta)
                y = d["yc"] + d["r"] * math.sin(theta)
                points.append((x, y, theta))
                theta += d["step"]
            return [points]

        if jenis == "Elips":
            points = []
            theta = 0
            while theta <= 2 * math.pi + d["step"]:
                x = d["xc"] + d["a"] * math.cos(theta)
                y = d["yc"] + d["b"] * math.sin(theta)
                points.append((x, y, theta))
                theta += d["step"]
            return [points]

        if jenis == "Parabola":
            points = []
            start = min(d["t1"], d["t2"])
            end = max(d["t1"], d["t2"])
            t = start
            while t <= end:
                x = d["xp"] + d["a"] * t * t
                y = d["yp"] + 2 * d["a"] * t
                points.append((x, y, t))
                t += d["step"]
            return [points]

        right = []
        left = []
        safe = 0.12
        theta = -math.pi / 2 + safe
        end = math.pi / 2 - safe

        while theta <= end:
            sec_v = 1 / math.cos(theta)
            tan_v = math.tan(theta)

            right.append((d["xc"] + d["a"] * sec_v, d["yc"] + d["b"] * tan_v, theta))
            left.append((d["xc"] - d["a"] * sec_v, d["yc"] + d["b"] * tan_v, theta))

            theta += d["step"]

        return [right, left]

    # ========================================================
    # 4. RENDERING + ANIMASI
    # ========================================================
    def render_grid_only(self):
        self.canvas.delete("all")
        self.draw_grid()

    def draw_full_curve(self):
        self.stop_animation()
        self.refresh_text_and_table()
        self.render_grid_only()

        try:
            for curve in self.make_points():
                self.draw_curve_full(curve)
            self.current_calc.config(text="Kurva ditampilkan langsung tanpa animasi.")
        except Exception:
            pass

    def start_animation(self):
        self.stop_animation()
        self.refresh_text_and_table()
        self.render_grid_only()

        try:
            self.animation_curves = self.make_points()
        except Exception:
            return

        self.animation_curve_index = 0
        self.animation_point_index = 1
        self.animation_iteration = 1

        self.current_calc.config(text="Animasi dimulai. Titik pertama sedang disiapkan.")
        self.animate_next_segment()

    def stop_animation(self):
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def animate_next_segment(self):
        if self.animation_curve_index >= len(self.animation_curves):
            self.animation_job = None
            self.current_calc.config(text="Animasi selesai. Kurva terbentuk dari kumpulan titik hasil kalkulasi.")
            return

        curve = self.animation_curves[self.animation_curve_index]

        if self.animation_point_index >= len(curve):
            self.animation_curve_index += 1
            self.animation_point_index = 1
            self.animation_job = self.root.after(self.animation_speed.get(), self.animate_next_segment)
            return

        p1 = curve[self.animation_point_index - 1]
        p2 = curve[self.animation_point_index]

        self.draw_segment(p1, p2)
        self.update_current_process(p1, p2, self.animation_iteration)

        self.animation_iteration += 1
        self.animation_point_index += 1
        self.animation_job = self.root.after(self.animation_speed.get(), self.animate_next_segment)

    def update_current_process(self, p1, p2, iteration):
        d = self.data
        jenis = d["jenis"]

        x1, y1, param1 = p1
        x2, y2, param2 = p2

        if jenis == "Lingkaran":
            cos_v = math.cos(param2)
            sin_v = math.sin(param2)
            text = (
                f"Iterasi ke-{iteration}\n"
                f"theta = {fmt(param2)}\n"
                f"cos(theta) = {fmt(cos_v)}, sin(theta) = {fmt(sin_v)}\n\n"
                "Kalkulasi:\n"
                f"x = xc + r * cos(theta)\n"
                f"x = {fmt(d['xc'])} + {fmt(d['r'])} * {fmt(cos_v)} = {fmt(x2)}\n"
                f"y = yc + r * sin(theta)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['r'])} * {fmt(sin_v)} = {fmt(y2)}\n\n"
                f"Rendering: hubungkan ({fmt(x1)}, {fmt(y1)}) ke ({fmt(x2)}, {fmt(y2)})"
            )

        elif jenis == "Elips":
            cos_v = math.cos(param2)
            sin_v = math.sin(param2)
            text = (
                f"Iterasi ke-{iteration}\n"
                f"theta = {fmt(param2)}\n"
                f"cos(theta) = {fmt(cos_v)}, sin(theta) = {fmt(sin_v)}\n\n"
                "Kalkulasi:\n"
                f"x = xc + a * cos(theta)\n"
                f"x = {fmt(d['xc'])} + {fmt(d['a'])} * {fmt(cos_v)} = {fmt(x2)}\n"
                f"y = yc + b * sin(theta)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['b'])} * {fmt(sin_v)} = {fmt(y2)}\n\n"
                f"Rendering: hubungkan ({fmt(x1)}, {fmt(y1)}) ke ({fmt(x2)}, {fmt(y2)})"
            )

        elif jenis == "Parabola":
            text = (
                f"Iterasi ke-{iteration}\n"
                f"t = {fmt(param2)}, t^2 = {fmt(param2 * param2)}\n\n"
                "Kalkulasi:\n"
                f"x = xp + a * t^2\n"
                f"x = {fmt(d['xp'])} + {fmt(d['a'])} * {fmt(param2 * param2)} = {fmt(x2)}\n"
                f"y = yp + 2 * a * t\n"
                f"y = {fmt(d['yp'])} + 2 * {fmt(d['a'])} * {fmt(param2)} = {fmt(y2)}\n\n"
                f"Rendering: hubungkan ({fmt(x1)}, {fmt(y1)}) ke ({fmt(x2)}, {fmt(y2)})"
            )

        else:
            sec_v = 1 / math.cos(param2)
            tan_v = math.tan(param2)
            text = (
                f"Iterasi ke-{iteration}\n"
                f"theta = {fmt(param2)}\n"
                f"sec(theta) = {fmt(sec_v)}, tan(theta) = {fmt(tan_v)}\n\n"
                "Kalkulasi:\n"
                f"x = xc +/- a * sec(theta)\n"
                f"x = {fmt(x2)}\n"
                f"y = yc + b * tan(theta)\n"
                f"y = {fmt(d['yc'])} + {fmt(d['b'])} * {fmt(tan_v)} = {fmt(y2)}\n\n"
                f"Rendering: hubungkan ({fmt(x1)}, {fmt(y1)}) ke ({fmt(x2)}, {fmt(y2)})"
            )

        self.current_calc.config(text=text)

    def draw_curve_full(self, curve):
        if len(curve) < 2:
            return

        screen_points = []
        for x, y, param in curve:
            sx, sy = self.world_to_screen(x, y)
            screen_points.extend([sx, sy])

        self.canvas.create_line(*screen_points, fill=Color.MIDNIGHT, width=3, smooth=False)

        for i in range(0, len(curve), max(1, len(curve) // 12)):
            x, y, param = curve[i]
            sx, sy = self.world_to_screen(x, y)
            self.canvas.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill=Color.MIDNIGHT, outline=Color.MIDNIGHT)

    def draw_segment(self, p1, p2):
        x1, y1, param1 = p1
        x2, y2, param2 = p2

        sx1, sy1 = self.world_to_screen(x1, y1)
        sx2, sy2 = self.world_to_screen(x2, y2)

        self.canvas.create_line(sx1, sy1, sx2, sy2, fill=Color.MIDNIGHT, width=3)
        self.canvas.create_oval(sx2 - 2, sy2 - 2, sx2 + 2, sy2 + 2, fill=Color.MIDNIGHT, outline=Color.MIDNIGHT)

    def world_to_screen(self, x, y):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        sx = width / 2 + (x - self.center_x) * self.scale
        sy = height / 2 - (y - self.center_y) * self.scale

        return sx, sy

    def screen_to_world(self, sx, sy):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        x = self.center_x + (sx - width / 2) / self.scale
        y = self.center_y - (sy - height / 2) / self.scale

        return x, y

    def nice_grid_step(self):
        min_pixels = 60
        raw = min_pixels / self.scale
        power = 10 ** math.floor(math.log10(raw))
        normalized = raw / power

        if normalized <= 1:
            nice = 1
        elif normalized <= 2:
            nice = 2
        elif normalized <= 5:
            nice = 5
        else:
            nice = 10

        return nice * power

    def draw_grid(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        step = self.nice_grid_step()

        left = self.center_x - width / 2 / self.scale
        right = self.center_x + width / 2 / self.scale
        top = self.center_y + height / 2 / self.scale
        bottom = self.center_y - height / 2 / self.scale

        start_x = math.floor(left / step) * step
        end_x = math.ceil(right / step) * step
        start_y = math.floor(bottom / step) * step
        end_y = math.ceil(top / step) * step

        x = start_x
        while x <= end_x:
            sx, _ = self.world_to_screen(x, 0)
            self.canvas.create_line(sx, 0, sx, height, fill=Color.GRID)
            x += step

        y = start_y
        while y <= end_y:
            _, sy = self.world_to_screen(0, y)
            self.canvas.create_line(0, sy, width, sy, fill=Color.GRID)
            y += step

        axis_x, axis_y = self.world_to_screen(0, 0)

        if 0 <= axis_y <= height:
            self.canvas.create_line(0, axis_y, width, axis_y, fill=Color.MIDNIGHT, width=2)

        if 0 <= axis_x <= width:
            self.canvas.create_line(axis_x, 0, axis_x, height, fill=Color.MIDNIGHT, width=2)

        x = start_x
        while x <= end_x:
            sx, _ = self.world_to_screen(x, 0)
            label_y = min(max(axis_y + 20, 20), height - 12)

            if 0 <= sx <= width:
                self.canvas.create_line(sx, label_y - 15, sx, label_y - 8, fill=Color.MIDNIGHT)
                self.canvas.create_text(sx, label_y, text=tick_fmt(x), fill=Color.MIDNIGHT, font=("Segoe UI", 9))

            x += step

        y = start_y
        while y <= end_y:
            _, sy = self.world_to_screen(0, y)
            label_x = min(max(axis_x + 18, 22), width - 30)

            if 0 <= sy <= height:
                self.canvas.create_line(label_x - 8, sy, label_x - 2, sy, fill=Color.MIDNIGHT)
                self.canvas.create_text(label_x + 10, sy, text=tick_fmt(y), fill=Color.MIDNIGHT, font=("Segoe UI", 9))

            y += step

        self.canvas.create_text(width - 20, min(max(axis_y - 14, 18), height - 18), text="X", fill=Color.MIDNIGHT, font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(min(max(axis_x + 14, 18), width - 20), 20, text="Y", fill=Color.MIDNIGHT, font=("Segoe UI", 11, "bold"))

        self.canvas.create_text(
            12,
            height - 16,
            anchor="w",
            text=f"Skala: {fmt(self.scale)} px / 1 satuan | Grid: {tick_fmt(step)} satuan",
            fill=Color.MUTED,
            font=("Segoe UI", 9)
        )

    # ========================================================
    # ZOOM, DRAG, AUTO FIT
    # ========================================================
    def zoom(self, factor, mouse_x=None, mouse_y=None):
        self.stop_animation()

        if mouse_x is None:
            mouse_x = self.canvas.winfo_width() / 2
        if mouse_y is None:
            mouse_y = self.canvas.winfo_height() / 2

        before_x, before_y = self.screen_to_world(mouse_x, mouse_y)

        self.scale *= factor
        self.scale = max(0.5, min(300, self.scale))

        after_x, after_y = self.screen_to_world(mouse_x, mouse_y)

        self.center_x += before_x - after_x
        self.center_y += before_y - after_y

        self.draw_full_curve()

    def mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom(1.12, event.x, event.y)
        else:
            self.zoom(0.88, event.x, event.y)

    def drag_start_event(self, event):
        self.stop_animation()
        self.drag_start = (event.x, event.y, self.center_x, self.center_y)

    def drag_move_event(self, event):
        if self.drag_start is None:
            return

        start_x, start_y, old_center_x, old_center_y = self.drag_start
        dx = event.x - start_x
        dy = event.y - start_y

        self.center_x = old_center_x - dx / self.scale
        self.center_y = old_center_y + dy / self.scale

        self.draw_full_curve()

    def drag_end_event(self):
        self.drag_start = None

    def reset_view(self):
        self.stop_animation()
        self.scale = 50
        self.center_x = 0
        self.center_y = 0
        self.draw_full_curve()

    def auto_fit(self):
        self.stop_animation()

        try:
            self.data = self.get_data()
            curves = self.make_points()
            points = [
                point
                for curve in curves
                for point in curve
                if math.isfinite(point[0]) and math.isfinite(point[1])
            ]

            if not points:
                return

            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)

            curve_width = max(max_x - min_x, 1)
            curve_height = max(max_y - min_y, 1)

            canvas_width = max(self.canvas.winfo_width(), 1)
            canvas_height = max(self.canvas.winfo_height(), 1)
            padding = 0.78

            self.center_x = (min_x + max_x) / 2
            self.center_y = (min_y + max_y) / 2
            self.scale = min(canvas_width * padding / curve_width, canvas_height * padding / curve_height)
            self.scale = max(0.5, min(300, self.scale))

            self.render_grid_only()

        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = CurveApp(root)
    root.mainloop()

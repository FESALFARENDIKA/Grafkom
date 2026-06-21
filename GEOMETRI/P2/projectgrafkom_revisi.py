import tkinter as tk
from tkinter import ttk, messagebox
import math


class KurvaKonikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafika Komputer - Kurva Konik")
        self.root.geometry("1200x720")
        self.root.minsize(1000, 620)

        # ==========================================================
        # DATA UTAMA
        # ==========================================================
        # frames menyimpan data per interval.
        # Lingkaran/elips/parabola: 1 frame = 1 titik.
        # Hiperbola: 1 frame = 2 titik, yaitu cabang kanan dan cabang kiri.
        #
        # visible_count = jumlah interval yang sudah tampil.
        # active_frame_index = interval yang sedang diberi tanda aktif.
        #
        # Saat tombol LEFT/HOME dipakai, visible_count tidak dikurangi.
        # Artinya titik interval dan grafik tetap ada, hanya tanda aktifnya
        # yang berpindah. Ini dibuat seperti permintaan revisi.
        self.frames = []
        self.visible_count = 0
        self.active_frame_index = None
        self.active_point_branch = None

        self.is_animating = False
        self.is_paused = False
        self.after_id = None

        # Tampilan koordinat.
        # Default dibuat seperti output referensi: r besar, scale kecil.
        self.scale = 3.0
        self.offset_x = 0
        self.offset_y = 0

        self.drag_start_x = None
        self.drag_start_y = None

        # ==========================================================
        # WARNA
        # ==========================================================
        self.bg_dark = "#212842"
        self.bg_soft = "#F0E7D5"
        self.panel_bg = "#F8F1E3"
        self.grid_color = "#D6CBB8"
        self.axis_color = "#111827"
        self.line_color = "#1D4ED8"
        self.point_color = "#E11D48"
        self.active_color = "#F59E0B"
        self.center_color = "#16A34A"
        self.purple = "#6D28D9"

        self.current_curve = tk.StringVar(value="Lingkaran")
        self.show_number = tk.BooleanVar(value=True)
        self.show_active_label = tk.BooleanVar(value=True)

        self.inputs = {}
        self.dynamic_form_frame = None

        self.build_ui()
        self.bind_keyboard()
        self.rebuild_parameter_form()
        self.draw_all()

    # ==========================================================
    # UI DESAIN PERTAMA
    # ==========================================================
    def build_ui(self):
        main = tk.Frame(self.root, bg=self.bg_dark)
        main.pack(fill="both", expand=True)

        left_panel = tk.Frame(main, bg=self.panel_bg, width=330)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(main, bg=self.bg_dark)
        right_panel.pack(side="right", fill="both", expand=True)

        self.left_panel = left_panel
        self.right_panel = right_panel

        title = tk.Label(
            left_panel,
            text="Kurva Konik",
            bg=self.panel_bg,
            fg=self.bg_dark,
            font=("Arial", 17, "bold")
        )
        title.pack(pady=(14, 3))

        subtitle = tk.Label(
            left_panel,
            text="Lingkaran • Elips • Parabola • Hiperbola",
            bg=self.panel_bg,
            fg="#374151",
            font=("Arial", 9)
        )
        subtitle.pack(pady=(0, 12))

        curve_frame = tk.Frame(left_panel, bg=self.panel_bg)
        curve_frame.pack(fill="x", padx=16)

        tk.Label(
            curve_frame,
            text="Jenis Kurva",
            bg=self.panel_bg,
            fg=self.bg_dark,
            anchor="w"
        ).pack(fill="x", pady=(4, 1))

        combo = ttk.Combobox(
            curve_frame,
            textvariable=self.current_curve,
            values=["Lingkaran", "Elips", "Parabola", "Hiperbola"],
            state="readonly"
        )
        combo.pack(fill="x", pady=(0, 6))
        combo.bind("<<ComboboxSelected>>", lambda event: self.change_curve(self.current_curve.get()))

        self.dynamic_form_frame = tk.Frame(left_panel, bg=self.panel_bg)
        self.dynamic_form_frame.pack(fill="x", padx=16)

        self.formula_title = tk.Label(
            left_panel,
            text="Rumus",
            bg=self.panel_bg,
            fg=self.bg_dark,
            font=("Arial", 10, "bold")
        )
        self.formula_title.pack(anchor="w", padx=18, pady=(8, 2))

        self.formula_label = tk.Label(
            left_panel,
            text="-",
            bg=self.panel_bg,
            fg="#111827",
            font=("Arial", 9),
            justify="left",
            wraplength=285
        )
        self.formula_label.pack(anchor="w", padx=18, pady=(0, 4))

        button_frame = tk.Frame(left_panel, bg=self.panel_bg)
        button_frame.pack(fill="x", padx=16, pady=6)

        self.draw_button = tk.Button(
            button_frame,
            text="Gambar Kurva",
            bg=self.bg_dark,
            fg="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            pady=8,
            command=self.generate_curve
        )
        self.draw_button.pack(fill="x", pady=3)

        row1 = tk.Frame(button_frame, bg=self.panel_bg)
        row1.pack(fill="x", pady=3)

        tk.Button(row1, text="Pause/Play", bg="#E5E7EB", relief="flat", pady=6, command=self.toggle_pause).pack(side="left", fill="x", expand=True, padx=(0, 3))
        tk.Button(row1, text="Selesai", bg="#E5E7EB", relief="flat", pady=6, command=self.finish_curve).pack(side="left", fill="x", expand=True, padx=(3, 0))

        row2 = tk.Frame(button_frame, bg=self.panel_bg)
        row2.pack(fill="x", pady=3)

        tk.Button(row2, text="Zoom In", bg="#E5E7EB", relief="flat", pady=6, command=self.zoom_in).pack(side="left", fill="x", expand=True, padx=(0, 3))
        tk.Button(row2, text="Zoom Out", bg="#E5E7EB", relief="flat", pady=6, command=self.zoom_out).pack(side="left", fill="x", expand=True, padx=(3, 0))

        tk.Button(
            button_frame,
            text="Reset",
            bg="#FCA5A5",
            fg="#7F1D1D",
            relief="flat",
            font=("Arial", 10, "bold"),
            pady=8,
            command=self.reset_all
        ).pack(fill="x", pady=3)

        # Tombol cepat untuk mode visualisasi sudut (klik 2 titik lalu tekan tombol ini)
        tk.Button(
            button_frame,
            text="Tampilkan Sudut (2 titik ke pusat)",
            bg="#E5E7EB",
            relief="flat",
            pady=6,
            command=self.show_angle_from_two_points
        ).pack(fill="x", pady=3)


        tk.Checkbutton(
            left_panel,
            text="Tampilkan nomor interval",
            variable=self.show_number,
            command=self.draw_all,
            bg=self.panel_bg,
            activebackground=self.panel_bg
        ).pack(anchor="w", padx=16, pady=(4, 0))

        tk.Checkbutton(
            left_panel,
            text="Tampilkan label titik aktif",
            variable=self.show_active_label,
            command=self.draw_all,
            bg=self.panel_bg,
            activebackground=self.panel_bg
        ).pack(anchor="w", padx=16, pady=(0, 6))

        self.status_label = tk.Label(
            left_panel,
            text="Status: PAUSE",
            bg=self.panel_bg,
            fg=self.point_color,
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(anchor="w", padx=18, pady=(4, 2))

        self.stat_label = tk.Label(
            left_panel,
            text="Interval tampil = 0\nTotal interval = 0",
            bg=self.panel_bg,
            fg="#111827",
            justify="left",
            font=("Arial", 9)
        )
        self.stat_label.pack(anchor="w", padx=18, pady=(0, 8))

        shortcut_title = tk.Label(
            left_panel,
            text="Shortcut Keyboard",
            bg=self.panel_bg,
            fg=self.bg_dark,
            font=("Arial", 10, "bold")
        )
        shortcut_title.pack(anchor="w", padx=18, pady=(4, 0))

        shortcut = tk.Label(
            left_panel,
            text=(
                "SPACE Play/Pause | RIGHT maju\n"
                "LEFT pindah tanda ke interval sebelumnya\n"
                "HOME tanda ke awal | END tampilkan semua\n"
                "R reset | UP/DOWN interval\n"
                "+/- zoom | W/A/S/D geser grafik"
            ),
            bg=self.panel_bg,
            fg="#374151",
            justify="left",
            font=("Arial", 8)
        )
        shortcut.pack(fill="x", padx=18, pady=(2, 8))

        info_title = tk.Label(
            left_panel,
            text="Info Titik Interval",
            bg=self.panel_bg,
            fg=self.bg_dark,
            font=("Arial", 11, "bold")
        )
        info_title.pack(anchor="w", padx=18, pady=(4, 2))

        self.point_info = tk.Label(
            left_panel,
            text="Klik titik merah pada kurva untuk melihat nilai t, x, dan y.",
            bg="#FFF7ED",
            fg="#111827",
            relief="solid",
            bd=1,
            padx=8,
            pady=8,
            justify="left",
            wraplength=285,
            font=("Consolas", 9)
        )
        self.point_info.pack(fill="x", padx=18, pady=(2, 8))

        # Canvas dan proses menggunakan desain pertama:
        # canvas besar di kanan, proses perhitungan di bawah canvas.
        canvas_wrap = tk.Frame(right_panel, bg=self.bg_dark)
        canvas_wrap.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        self.canvas = tk.Canvas(canvas_wrap, bg=self.bg_soft, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", lambda event: self.draw_all())
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_zoom)

        process_frame = tk.Frame(right_panel, bg=self.bg_dark)
        process_frame.pack(fill="x", padx=12, pady=(0, 12))

        process_label = tk.Label(
            process_frame,
            text="Proses Perhitungan",
            bg=self.bg_dark,
            fg="white",
            font=("Arial", 10, "bold")
        )
        process_label.pack(anchor="w")

        self.process_text = tk.Text(
            process_frame,
            height=8,
            bg="#111827",
            fg="#F9FAFB",
            insertbackground="white",
            font=("Consolas", 9),
            wrap="none"
        )
        self.process_text.pack(side="left", fill="x", expand=True)

        scroll = tk.Scrollbar(process_frame, command=self.process_text.yview)
        scroll.pack(side="right", fill="y")
        self.process_text.config(yscrollcommand=scroll.set)

    # ==========================================================
    # FORM DINAMIS SESUAI KURVA
    # ==========================================================
    def rebuild_parameter_form(self):
        for widget in self.dynamic_form_frame.winfo_children():
            widget.destroy()

        self.inputs.clear()
        curve = self.current_curve.get()

        # Semua kurva butuh pusat.
        self.add_entry("Pusat X / xc", "0")
        self.add_entry("Pusat Y / yc", "0")

        if curve == "Lingkaran":
            self.add_entry("Jari-jari r", "80")
            self.add_entry("Interval / step", "0.08")
            self.formula_label.config(
                text="x = xc + r cos(t)\ny = yc + r sin(t)\nt otomatis: 0 sampai 2π"
            )

        elif curve == "Elips":
            self.add_entry("Parameter a", "100")
            self.add_entry("Parameter b", "55")
            self.add_entry("Interval / step", "0.08")
            self.formula_label.config(
                text="x = xc + a cos(t)\ny = yc + b sin(t)\nt otomatis: 0 sampai 2π"
            )

        elif curve == "Parabola":
            self.add_entry("Parameter a", "0.025")
            self.add_entry("t awal", "-100")
            self.add_entry("t akhir", "100")
            self.add_entry("Interval / step", "2.5")
            self.formula_label.config(
                text="x = xc + t\ny = yc + a t²"
            )

        elif curve == "Hiperbola":
            self.add_entry("Parameter a", "45")
            self.add_entry("Parameter b", "35")
            self.add_entry("t awal", "-2")
            self.add_entry("t akhir", "2")
            self.add_entry("Interval / step", "0.05")
            self.formula_label.config(
                text=(
                    "Kanan: x = xc + a cosh(t)\n"
                    "Kiri : x = xc - a cosh(t)\n"
                    "y = yc + b sinh(t)\n"
                    "t=0 menunjukkan vertex pada setiap cabang"
                )
            )

        self.draw_all()

    def add_entry(self, label, default):
        row = tk.Frame(self.dynamic_form_frame, bg=self.panel_bg)
        row.pack(fill="x", pady=2)

        tk.Label(
            row,
            text=label,
            bg=self.panel_bg,
            fg=self.bg_dark,
            anchor="w",
            font=("Arial", 9)
        ).pack(side="left", fill="x", expand=True)

        entry = tk.Entry(row, width=10, font=("Arial", 9))
        entry.insert(0, default)
        entry.pack(side="right")
        self.inputs[label] = entry

    def change_curve(self, curve_name):
        self.stop_timer()
        self.current_curve.set(curve_name)
        self.reset_data_only()
        self.rebuild_parameter_form()
        self.process_text.delete("1.0", "end")
        self.add_process(f"Jenis kurva diganti menjadi {curve_name}.")
        self.add_process("Input parameter sudah disesuaikan dengan rumus kurva.")

    # ==========================================================
    # KEYBOARD
    # ==========================================================
    def is_form_input_focused(self):
        """
        Jika user sedang mengetik di kolom form (Entry/ComboBox),
        maka shortcut keyboard jangan memicu aksi apapun.
        """
        widget = self.root.focus_get()
        if widget is None:
            return False

        # Entry angka/teks
        if isinstance(widget, tk.Entry):
            return True

        # ttk/legacy Combobox / Spinbox (nama class biasanya mengandung string ini)
        cls = widget.__class__.__name__.lower()
        if "entry" in cls or "combobox" in cls or "spinbox" in cls:
            return True

        return False

    def run_shortcut_if_not_typing(self, fn):
        def _wrapped(event=None):
            if self.is_form_input_focused():
                return "break"
            fn()
        return _wrapped

    def bind_keyboard(self):
        # Tombol keyboard yang perlu jalan di banyak kondisi fokus/fokus widget
        self.root.bind_all("<space>", self.run_shortcut_if_not_typing(self.toggle_pause))

        self.root.bind_all("<Right>", self.run_shortcut_if_not_typing(self.next_interval))
        self.root.bind_all("<Left>", self.run_shortcut_if_not_typing(self.previous_interval))
        self.root.bind_all("<Home>", self.run_shortcut_if_not_typing(self.go_home))
        self.root.bind_all("<End>", self.run_shortcut_if_not_typing(self.finish_curve))

        self.root.bind_all("<r>", self.run_shortcut_if_not_typing(self.reset_all))
        self.root.bind_all("<R>", self.run_shortcut_if_not_typing(self.reset_all))

        self.root.bind_all("<Up>", self.run_shortcut_if_not_typing(self.increase_step))
        self.root.bind_all("<Down>", self.run_shortcut_if_not_typing(self.decrease_step))

        self.root.bind_all("1", self.run_shortcut_if_not_typing(lambda: self.change_curve("Lingkaran")))
        self.root.bind_all("2", self.run_shortcut_if_not_typing(lambda: self.change_curve("Elips")))
        self.root.bind_all("3", self.run_shortcut_if_not_typing(lambda: self.change_curve("Parabola")))
        self.root.bind_all("4", self.run_shortcut_if_not_typing(lambda: self.change_curve("Hiperbola")))

        # Zoom in/out: '+' dan '-' sering berbeda tergantung keyboard (termasuk numpad)
        self.root.bind_all("+", self.run_shortcut_if_not_typing(self.zoom_in))
        self.root.bind_all("=", self.run_shortcut_if_not_typing(self.zoom_in))
        self.root.bind_all("KP_Add", self.run_shortcut_if_not_typing(self.zoom_in))
        self.root.bind_all("<KP_Add>", self.run_shortcut_if_not_typing(self.zoom_in))

        self.root.bind_all("-", self.run_shortcut_if_not_typing(self.zoom_out))
        self.root.bind_all("<KP_Subtract>", self.run_shortcut_if_not_typing(self.zoom_out))
        self.root.bind_all("KP_Subtract", self.run_shortcut_if_not_typing(self.zoom_out))

        self.root.bind_all("<w>", self.run_shortcut_if_not_typing(lambda: self.pan(0, 25)))
        self.root.bind_all("<W>", self.run_shortcut_if_not_typing(lambda: self.pan(0, 25)))
        self.root.bind_all("<s>", self.run_shortcut_if_not_typing(lambda: self.pan(0, -25)))
        self.root.bind_all("<S>", self.run_shortcut_if_not_typing(lambda: self.pan(0, -25)))
        self.root.bind_all("<a>", self.run_shortcut_if_not_typing(lambda: self.pan(25, 0)))
        self.root.bind_all("<A>", self.run_shortcut_if_not_typing(lambda: self.pan(25, 0)))
        self.root.bind_all("<d>", self.run_shortcut_if_not_typing(lambda: self.pan(-25, 0)))
        self.root.bind_all("<D>", self.run_shortcut_if_not_typing(lambda: self.pan(-25, 0)))

    # ==========================================================
    # INPUT
    # ==========================================================
    def read_float(self, label):
        try:
            return float(self.inputs[label].get())
        except ValueError:
            raise ValueError(f"Input '{label}' harus berupa angka.")

    def get_value(self, label, default=None):
        if label in self.inputs:
            return self.read_float(label)
        return default

    def set_input(self, label, value):
        if label not in self.inputs:
            return

        entry = self.inputs[label]
        entry.delete(0, "end")
        entry.insert(0, value)

    # ==========================================================
    # RUMUS PARABOLA DAN HiPERBOLA MENYESUAIKAN DENGAN COMPT.
    # ==========================================================
    def calc_point(self, curve, t, xc, yc, r=None, a=None, b=None, branch="utama"):
        if curve == "Lingkaran":
            x = xc + r * math.cos(t)
            y = yc + r * math.sin(t)
            formula = f"x={xc}+{r}cos({t:.2f}), y={yc}+{r}sin({t:.2f})"

        elif curve == "Elips":
            x = xc + a * math.cos(t)
            y = yc + b * math.sin(t)
            formula = f"x={xc}+{a}cos({t:.2f}), y={yc}+{b}sin({t:.2f})"

        elif curve == "Parabola":
            x = xc + t
            y = yc + a * (t ** 2)
            formula = f"x={xc}+{t:.2f}, y={yc}+{a}({t:.2f})²"

        elif curve == "Hiperbola":
            y = yc + b * math.sinh(t)

            if branch == "kiri":
                x = xc - a * math.cosh(t)
                formula = f"x={xc}-{a}cosh({t:.2f}), y={yc}+{b}sinh({t:.2f})"
            else:
                x = xc + a * math.cosh(t)
                formula = f"x={xc}+{a}cosh({t:.2f}), y={yc}+{b}sinh({t:.2f})"

        else:
            x = 0
            y = 0
            formula = "-"

        return {
            "curve": curve,
            "branch": branch,
            "t": t,
            "x": x,
            "y": y,
            "formula": formula
        }

    def make_t_values(self, t_start, t_end, step, force_zero=False):
        values = []
        t = t_start

        while t <= t_end + 0.000001:
            if abs(t) < 0.000001:
                t = 0.0

            values.append(round(t, 10))
            t += step

        # Supaya hiperbola benar-benar punya t=0.
        if force_zero and t_start < 0 < t_end:
            if not any(abs(v) < 0.000001 for v in values):
                values.append(0.0)
                values.sort()

        # Supaya kurva tertutup seperti lingkaran/elips tetap sampai t akhir.
        if abs(values[-1] - t_end) > 0.000001:
            values.append(t_end)

        return values

    def generate_frames_from_input(self):
        curve = self.current_curve.get()

        xc = self.get_value("Pusat X / xc", 0)
        yc = self.get_value("Pusat Y / yc", 0)
        step = self.get_value("Interval / step", 0.1)

        if step <= 0:
            raise ValueError("Interval / step harus lebih dari 0.")

        r = None
        a = None
        b = None

        if curve == "Lingkaran":
            r = self.get_value("Jari-jari r", 80)
            if r <= 0:
                raise ValueError("Jari-jari r harus lebih dari 0.")

            t_start = 0
            t_end = 2 * math.pi

        elif curve == "Elips":
            a = self.get_value("Parameter a", 100)
            b = self.get_value("Parameter b", 55)
            if a <= 0 or b <= 0:
                raise ValueError("Parameter a dan b harus lebih dari 0.")

            t_start = 0
            t_end = 2 * math.pi

        elif curve == "Parabola":
            a = self.get_value("Parameter a", 0.025)
            t_start = self.get_value("t awal", -100)
            t_end = self.get_value("t akhir", 100)

        elif curve == "Hiperbola":
            a = self.get_value("Parameter a", 45)
            b = self.get_value("Parameter b", 35)
            t_start = self.get_value("t awal", -2)
            t_end = self.get_value("t akhir", 2)

            if a <= 0 or b <= 0:
                raise ValueError("Parameter a dan b harus lebih dari 0.")

        else:
            raise ValueError("Jenis kurva tidak valid.")

        if t_end <= t_start:
            raise ValueError("t akhir harus lebih besar dari t awal.")

        t_values = self.make_t_values(t_start, t_end, step, force_zero=(curve == "Hiperbola"))

        frames = []

        for i, t in enumerate(t_values, start=1):
            if curve == "Hiperbola":
                kanan = self.calc_point(curve, t, xc, yc, r, a, b, branch="kanan")
                kiri = self.calc_point(curve, t, xc, yc, r, a, b, branch="kiri")

                kanan["frame"] = i
                kiri["frame"] = i

                frames.append({
                    "frame": i,
                    "t": t,
                    "points": [kanan, kiri]
                })
            else:
                point = self.calc_point(curve, t, xc, yc, r, a, b, branch="utama")
                point["frame"] = i

                frames.append({
                    "frame": i,
                    "t": t,
                    "points": [point]
                })

        param = {
            "curve": curve,
            "xc": xc,
            "yc": yc,
            "r": r,
            "a": a,
            "b": b,
            "t_start": t_start,
            "t_end": t_end,
            "step": step
        }

        return frames, param

    # ==========================================================
    # PROSES UTAMA
    # ==========================================================
    def generate_curve(self):
        try:
            self.stop_timer()

            self.frames, param = self.generate_frames_from_input()
            self.visible_count = 0
            self.active_frame_index = None
            self.active_point_branch = None

            self.is_animating = True
            self.is_paused = False

            self.process_text.delete("1.0", "end")
            self.point_info.config(text="Klik titik merah pada kurva untuk melihat nilai t, x, dan y.")

            self.add_process("Tahap 1 - Inisialisasi")
            self.add_process(f"Kurva = {param['curve']}")
            self.add_process(f"xc={param['xc']}, yc={param['yc']}")

            if param["curve"] == "Lingkaran":
                self.add_process(f"r={param['r']}")
                self.add_process("t otomatis = 0 sampai 2π")
            elif param["curve"] == "Elips":
                self.add_process(f"a={param['a']}, b={param['b']}")
                self.add_process("t otomatis = 0 sampai 2π")
            elif param["curve"] == "Parabola":
                self.add_process(f"a={param['a']}")
                self.add_process(f"t awal={param['t_start']}, t akhir={param['t_end']}")
            elif param["curve"] == "Hiperbola":
                self.add_process(f"a={param['a']}, b={param['b']}")
                self.add_process(f"t awal={param['t_start']}, t akhir={param['t_end']}")
                self.add_process("1 interval = 2 titik, cabang kanan dan kiri.")
                self.add_process("Rumus memakai cosh(t)-1 agar bertemu di pusat saat t=0.")

            self.add_process(f"interval={param['step']}")
            self.add_process("")
            self.add_process("Tahap 2 - Iterasi")
            self.add_process("Nilai t bertambah sesuai interval.")
            self.add_process("")
            self.add_process("Tahap 3 - Kalkulasi")
            self.add_process("Setiap t dimasukkan ke rumus parametrik.")
            self.add_process("")
            self.add_process("Tahap 4 - Rendering")
            self.add_process("Titik interval digambar menjadi grafik.")
            self.add_process("")

            self.draw_all()
            self.animate_next_frame()

        except ValueError as e:
            messagebox.showerror("Input salah", str(e))

    def animate_next_frame(self):
        if not self.is_animating or self.is_paused:
            self.update_status()
            return

        if self.visible_count < len(self.frames):
            self.visible_count += 1
            self.active_frame_index = self.visible_count - 1
            frame = self.frames[self.active_frame_index]

            if self.current_curve.get() == "Hiperbola":
                kanan = frame["points"][0]
                kiri = frame["points"][1]
                self.add_process(
                    f"{frame['frame']:03d}. t={frame['t']:.2f} | "
                    f"kanan=({kanan['x']:.2f},{kanan['y']:.2f}) | "
                    f"kiri=({kiri['x']:.2f},{kiri['y']:.2f})"
                )
            else:
                p = frame["points"][0]
                self.add_process(
                    f"{frame['frame']:03d}. t={frame['t']:.2f} -> x={p['x']:.2f}, y={p['y']:.2f}"
                )

            self.draw_all()
            self.after_id = self.root.after(45, self.animate_next_frame)
        else:
            self.is_animating = False
            self.is_paused = False
            self.add_process("")
            self.add_process("Animasi selesai. Grafik dan proses tetap tampil.")
            self.draw_all()

    def toggle_pause(self):
        if not self.frames:
            self.generate_curve()
            return

        if self.visible_count >= len(self.frames) and not self.is_animating:
            self.add_process("SPACE ditekan, tetapi grafik sudah selesai.")
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.add_process("SPACE: animasi dijeda.")
        else:
            self.add_process("SPACE: animasi dilanjutkan.")
            self.is_animating = True
            self.animate_next_frame()

        self.draw_all()

    def prepare_frames_if_empty(self):
        if self.frames:
            return True

        try:
            self.frames, param = self.generate_frames_from_input()
            self.visible_count = 0
            self.active_frame_index = None
            self.process_text.delete("1.0", "end")
            self.add_process("Data kurva dibuat dari input.")
            return True
        except ValueError as e:
            messagebox.showerror("Input salah", str(e))
            return False

    def next_interval(self):
        if not self.prepare_frames_if_empty():
            return

        self.stop_timer()
        self.is_animating = False
        self.is_paused = True

        # RIGHT:
        # 1. Jika tanda aktif masih berada di titik lama, pindah tanda ke depan.
        # 2. Jika sudah di titik terakhir yang terlihat, tampilkan interval baru.
        if self.active_frame_index is None:
            self.active_frame_index = max(0, self.visible_count - 1)

        if self.active_frame_index < self.visible_count - 1:
            self.active_frame_index += 1
            frame = self.frames[self.active_frame_index]
            self.add_process(f"RIGHT: tanda aktif maju ke interval {frame['frame']}.")

        elif self.visible_count < len(self.frames):
            self.visible_count += 1
            self.active_frame_index = self.visible_count - 1
            frame = self.frames[self.active_frame_index]

            if self.current_curve.get() == "Hiperbola":
                self.add_process(f"RIGHT: interval {frame['frame']} kanan-kiri ditampilkan bersama.")
            else:
                self.add_process(f"RIGHT: interval {frame['frame']} ditampilkan.")
        else:
            frame = self.frames[self.active_frame_index]
            self.add_process("RIGHT: semua interval sudah tampil.")

        self.show_frame_info(frame)
        self.draw_all()

    def previous_interval(self):
        if not self.frames or self.visible_count == 0:
            return

        self.stop_timer()
        self.is_animating = False
        self.is_paused = True

        # LEFT tidak menghapus interval.
        # Grafik yang sudah tampil tetap ada.
        # Hanya penanda aktif yang mundur.
        if self.active_frame_index is None:
            self.active_frame_index = self.visible_count - 1
        else:
            self.active_frame_index = max(0, self.active_frame_index - 1)

        frame = self.frames[self.active_frame_index]

        if self.current_curve.get() == "Hiperbola":
            self.add_process(f"LEFT: tanda aktif kanan-kiri mundur ke interval {frame['frame']}.")
        else:
            self.add_process(f"LEFT: tanda aktif mundur ke interval {frame['frame']}.")

        self.show_frame_info(frame)
        self.draw_all()

    def go_home(self):
        if not self.prepare_frames_if_empty():
            return

        self.stop_timer()
        self.is_animating = False
        self.is_paused = True

        # HOME juga tidak menghapus interval.
        # Hanya tanda aktif yang dipindah ke awal.
        if self.visible_count == 0:
            self.visible_count = 1

        self.active_frame_index = 0
        frame = self.frames[0]

        self.add_process("HOME: tanda aktif kembali ke interval awal. Grafik tetap tampil.")
        self.show_frame_info(frame)
        self.draw_all()

    def finish_curve(self):
        if not self.prepare_frames_if_empty():
            return

        self.stop_timer()
        self.visible_count = len(self.frames)
        self.active_frame_index = len(self.frames) - 1
        self.is_animating = False
        self.is_paused = False

        frame = self.frames[self.active_frame_index]
        self.add_process("END: semua interval ditampilkan.")
        self.show_frame_info(frame)
        self.draw_all()

    def increase_step(self):
        try:
            step = self.read_float("Interval / step")
            if self.current_curve.get() == "Parabola":
                step += 0.5
            else:
                step += 0.01

            self.set_input("Interval / step", f"{step:.3f}")
            self.add_process(f"UP: interval menjadi {step:.3f}. Tekan Gambar untuk menerapkan.")
        except ValueError as e:
            messagebox.showerror("Input salah", str(e))

    def decrease_step(self):
        try:
            step = self.read_float("Interval / step")
            if self.current_curve.get() == "Parabola":
                step = max(0.5, step - 0.5)
            else:
                step = max(0.005, step - 0.01)

            self.set_input("Interval / step", f"{step:.3f}")
            self.add_process(f"DOWN: interval menjadi {step:.3f}. Tekan Gambar untuk menerapkan.")
        except ValueError as e:
            messagebox.showerror("Input salah", str(e))

    def reset_data_only(self):
        self.stop_timer()
        self.frames.clear()
        self.visible_count = 0
        self.active_frame_index = None
        self.active_point_branch = None
        self.is_animating = False
        self.is_paused = False
        self.point_info.config(text="Klik titik merah pada kurva untuk melihat nilai t, x, dan y.")
        if hasattr(self, "selected_points"):
            self.selected_points = []
        self.draw_all()

    def reset_all(self):
        self.reset_data_only()
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 3.0
        self.process_text.delete("1.0", "end")
        self.add_process("Reset selesai. Tekan Gambar untuk mulai lagi.")
        self.draw_all()

    def show_angle_from_two_points(self):
        """Tampilkan sudut dari 2 titik yang sudah diklik. Jika kurang 2 titik, tampilkan pesan."""
        if not hasattr(self, "selected_points") or not self.selected_points:
            messagebox.showinfo("Info", "Belum ada titik yang diklik.")
            return

        if len(self.selected_points) < 2:
            messagebox.showinfo("Info", "Klik dulu 2 titik merah agar sudut 2 titik ke pusat bisa ditampilkan.")
            return

        # Sudut sudah digambar otomatis pada draw_all(); tombol ini hanya memberi dorongan re-render + log proses.
        self.add_process("Tampilkan Sudut: menggunakan 2 titik terakhir yang dipilih.")
        self.draw_all()


    def stop_timer(self):
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    # ==========================================================
    # KOORDINAT
    # ==========================================================
    def center_x(self):
        return self.canvas.winfo_width() / 2 + self.offset_x

    def center_y(self):
        return self.canvas.winfo_height() / 2 + self.offset_y

    def world_to_screen(self, x, y):
        sx = self.center_x() + x * self.scale
        sy = self.center_y() - y * self.scale
        return sx, sy

    def visible_frames(self):
        return self.frames[:self.visible_count]

    # ==========================================================
    # GAMBAR
    # ==========================================================
    def draw_all(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_curve()
        self.draw_curve_helpers()
        self.draw_points()
        self.draw_center()
        self.draw_active_rays_and_angles()
        self.draw_title()
        self.update_status()


    def draw_grid(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w <= 1 or h <= 1:
            return

        cx = self.center_x()
        cy = self.center_y()
        grid_step = 50

        start_n = int((0 - cx) // grid_step) - 1
        end_n = int((w - cx) // grid_step) + 2

        for n in range(start_n, end_n):
            sx = cx + n * grid_step
            nilai_x = int((sx - cx) / self.scale)
            self.canvas.create_line(sx, 0, sx, h, fill=self.grid_color)

            if nilai_x != 0:
                self.canvas.create_text(
                    sx + 2,
                    cy + 8,
                    text=str(nilai_x),
                    fill="#111827",
                    anchor="nw",
                    font=("Arial", 8)
                )

        start_m = int((0 - cy) // grid_step) - 1
        end_m = int((h - cy) // grid_step) + 2

        for m in range(start_m, end_m):
            sy = cy + m * grid_step
            nilai_y = int((cy - sy) / self.scale)
            self.canvas.create_line(0, sy, w, sy, fill=self.grid_color)

            if nilai_y != 0:
                self.canvas.create_text(
                    cx + 6,
                    sy + 2,
                    text=str(nilai_y),
                    fill="#111827",
                    anchor="nw",
                    font=("Arial", 8)
                )

        self.canvas.create_line(0, cy, w, cy, fill=self.axis_color, width=2)
        self.canvas.create_line(cx, 0, cx, h, fill=self.axis_color, width=2)

        self.canvas.create_text(w - 22, cy + 14, text="X", fill=self.axis_color, font=("Arial", 10, "bold"))
        self.canvas.create_text(cx + 14, 18, text="Y", fill=self.axis_color, font=("Arial", 10, "bold"))
        self.canvas.create_text(cx + 6, cy + 6, text="0", fill=self.axis_color, anchor="nw", font=("Arial", 8, "bold"))

    def draw_curve(self):
        frames = self.visible_frames()
        curve = self.current_curve.get()

        if len(frames) < 2:
            return

        if curve == "Hiperbola":
            # Cabang kanan dan kiri digambar terpisah,
            # tetapi jumlah intervalnya sama karena 1 frame berisi 2 titik.
            for branch in ("kanan", "kiri"):
                branch_points = []

                for frame in frames:
                    for p in frame["points"]:
                        if p["branch"] == branch:
                            branch_points.append(p)

                for i in range(len(branch_points) - 1):
                    p1 = branch_points[i]
                    p2 = branch_points[i + 1]

                    x1, y1 = self.world_to_screen(p1["x"], p1["y"])
                    x2, y2 = self.world_to_screen(p2["x"], p2["y"])

                    self.canvas.create_line(x1, y1, x2, y2, fill=self.line_color, width=2)
        else:
            prev = None

            for frame in frames:
                p = frame["points"][0]

                if prev is not None:
                    x1, y1 = self.world_to_screen(prev["x"], prev["y"])
                    x2, y2 = self.world_to_screen(p["x"], p["y"])
                    self.canvas.create_line(x1, y1, x2, y2, fill=self.line_color, width=2)

                prev = p

    def draw_points(self):
        frames = self.visible_frames()

        for frame_index, frame in enumerate(frames):
            is_active_frame = frame_index == self.active_frame_index

            for p in frame["points"]:
                sx, sy = self.world_to_screen(p["x"], p["y"])

                radius = 7 if is_active_frame else 4
                color = self.active_color if is_active_frame else self.point_color

                dot = self.canvas.create_oval(
                    sx - radius,
                    sy - radius,
                    sx + radius,
                    sy + radius,
                    fill=color,
                    outline="white",
                    width=1
                )

                self.canvas.tag_bind(
                    dot,
                    "<Button-1>",
                    lambda event, fr=frame, idx=frame_index, point=p: self.click_point(fr, idx, point)
                )
                self.canvas.tag_bind(dot, "<Enter>", lambda event: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(dot, "<Leave>", lambda event: self.canvas.config(cursor=""))

                if self.show_number.get():
                    if frame["frame"] == 1 or frame["frame"] % 5 == 0 or is_active_frame:
                        self.canvas.create_text(
                            sx + 8,
                            sy - 8,
                            text=str(frame["frame"]),
                            fill=color,
                            anchor="w",
                            font=("Arial", 8, "bold")
                        )

        if self.show_active_label.get():
            self.draw_active_label()

    def draw_active_label(self):
        if self.active_frame_index is None:
            return

        frames = self.visible_frames()

        if not (0 <= self.active_frame_index < len(frames)):
            return

        frame = frames[self.active_frame_index]
        curve = self.current_curve.get()

        if curve == "Hiperbola":
            kanan = None
            kiri = None

            for p in frame["points"]:
                if p["branch"] == "kanan":
                    kanan = p
                elif p["branch"] == "kiri":
                    kiri = p

            if kanan is not None:
                sx, sy = self.world_to_screen(kanan["x"], kanan["y"])
                self.canvas.create_text(
                    sx + 14,
                    sy - 32,
                    text=f"t={frame['t']:.2f}\nKanan ({kanan['x']:.2f}, {kanan['y']:.2f})",
                    fill=self.purple,
                    anchor="w",
                    font=("Arial", 9, "bold")
                )

            if kiri is not None:
                sx, sy = self.world_to_screen(kiri["x"], kiri["y"])
                self.canvas.create_text(
                    sx + 14,
                    sy - 32,
                    text=f"t={frame['t']:.2f}\nKiri ({kiri['x']:.2f}, {kiri['y']:.2f})",
                    fill=self.purple,
                    anchor="w",
                    font=("Arial", 9, "bold")
                )

        else:
            p = frame["points"][0]
            sx, sy = self.world_to_screen(p["x"], p["y"])
            self.canvas.create_text(
                sx + 14,
                sy - 28,
                text=f"t={p['t']:.2f}\n({p['x']:.2f}, {p['y']:.2f})",
                fill=self.purple,
                anchor="w",
                font=("Arial", 9, "bold")
            )

    def draw_center(self):
        try:
            xc = self.get_value("Pusat X / xc", 0)
            yc = self.get_value("Pusat Y / yc", 0)
        except Exception:
            return

        sx, sy = self.world_to_screen(xc, yc)
        self.canvas.create_oval(sx - 6, sy - 6, sx + 6, sy + 6, fill=self.center_color, outline="white")
        self.canvas.create_text(sx + 10, sy + 10, text="Pusat", anchor="nw", fill=self.center_color, font=("Arial", 9, "bold"))

    def get_active_point(self):
        if self.active_frame_index is None:
            return None

        frames = self.visible_frames()
        if not (0 <= self.active_frame_index < len(frames)):
            return None

        frame = frames[self.active_frame_index]
        if self.current_curve.get() == "Hiperbola":
            if self.active_point_branch is not None:
                return next((p for p in frame["points"] if p.get("branch") == self.active_point_branch), None)
            return frame["points"][0]

        return frame["points"][0]

    def draw_curve_helpers(self):
        curve = self.current_curve.get()
        if curve in ("Lingkaran", "Elips"):
            self.draw_circle_ellipse_helpers()
        elif curve == "Parabola":
            self.draw_parabola_helpers()
        elif curve == "Hiperbola":
            self.draw_hyperbola_helpers()

    def draw_circle_ellipse_helpers(self):
        point = self.get_active_point()
        if point is None:
            return

        try:
            xc = self.get_value("Pusat X / xc", 0)
            yc = self.get_value("Pusat Y / yc", 0)
            if self.current_curve.get() == "Lingkaran":
                r = self.get_value("Jari-jari r", 80)
            else:
                r = None
            a = self.get_value("Parameter a", 100) if self.current_curve.get() == "Elips" else None
            b = self.get_value("Parameter b", 55) if self.current_curve.get() == "Elips" else None
        except Exception:
            return

        sx0, sy0 = self.world_to_screen(xc, yc)
        sx, sy = self.world_to_screen(point["x"], point["y"])
        sx_proj, sy_proj = self.world_to_screen(point["x"], yc)
        sx_vert, sy_vert = self.world_to_screen(xc, point["y"])

        self.canvas.create_line(sx0, sy0, sx_proj, sy_proj, fill="#2563EB", dash=(4, 4), width=2)
        self.canvas.create_line(sx_proj, sy_proj, sx, sy, fill="#2563EB", dash=(4, 4), width=2)
        self.canvas.create_line(sx0, sy0, sx_vert, sy_vert, fill="#2563EB", dash=(4, 4), width=2)
        self.canvas.create_line(sx_vert, sy_vert, sx, sy, fill="#2563EB", dash=(4, 4), width=2)

        if self.current_curve.get() == "Lingkaran":
            text_h = f"r cos t = {point['x'] - xc:.2f}"
            text_v = f"r sin t = {point['y'] - yc:.2f}"
        else:
            text_h = f"a cos t = {point['x'] - xc:.2f}"
            text_v = f"b sin t = {point['y'] - yc:.2f}"

        self.canvas.create_text(
            (sx0 + sx_proj) / 2,
            sy_proj - 14,
            text=text_h,
            fill="#1D4ED8",
            anchor="s",
            font=("Arial", 9, "bold")
        )
        self.canvas.create_text(
            sx_vert + 10,
            (sy0 + sy) / 2,
            text=text_v,
            fill="#1D4ED8",
            anchor="w",
            font=("Arial", 9, "bold")
        )

        cos_val = (point["x"] - xc) / (r if r else (a if a else 1)) if self.current_curve.get() != "Elips" or a else 0
        sin_val = (point["y"] - yc) / (r if r else (b if b else 1)) if self.current_curve.get() != "Elips" or b else 0
        self.canvas.create_text(
            sx0 + 10,
            sy0 - 16,
            text=f"cos t={cos_val:.2f}, sin t={sin_val:.2f}",
            fill="#1D4ED8",
            anchor="nw",
            font=("Arial", 8, "bold")
        )

    def draw_parabola_helpers(self):
        try:
            xc = self.get_value("Pusat X / xc", 0)
            yc = self.get_value("Pusat Y / yc", 0)
            a = self.get_value("Parameter a", 0.025)
        except Exception:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        x_left = (0 - self.center_x()) / self.scale
        x_right = (w - self.center_x()) / self.scale
        line_x = xc

        sx_line_x, _ = self.world_to_screen(line_x, yc)
        self.canvas.create_line(sx_line_x, 0, sx_line_x, h, fill="#9333EA", dash=(4, 4), width=2)
        self.canvas.create_text(sx_line_x + 6, 18, text="Axis Simetri", fill="#9333EA", anchor="nw", font=("Arial", 9, "bold"))

        vertex_sx, vertex_sy = self.world_to_screen(xc, yc)
        self.canvas.create_oval(vertex_sx - 6, vertex_sy - 6, vertex_sx + 6, vertex_sy + 6, outline="#9333EA", width=2)
        self.canvas.create_text(vertex_sx + 8, vertex_sy + 8, text="Vertex", fill="#9333EA", anchor="nw", font=("Arial", 9, "bold"))

        y_int_x = 0
        y_int_y = yc + a * (xc ** 2)
        sy_sx, sy_sy = self.world_to_screen(y_int_x, y_int_y)
        self.canvas.create_oval(sy_sx - 4, sy_sy - 4, sy_sx + 4, sy_sy + 4, fill="#9333EA", outline="")
        self.canvas.create_text(sy_sx + 8, sy_sy + 4, text="Y-intercept", fill="#9333EA", anchor="w", font=("Arial", 8, "bold"))

        if a != 0 and -yc / a >= 0:
            t_root = math.sqrt(-yc / a)
            for t_val in (-t_root, t_root):
                x_int = xc + t_val
                y_int = 0
                sx_int, sy_int = self.world_to_screen(x_int, y_int)
                self.canvas.create_oval(sx_int - 4, sy_int - 4, sx_int + 4, sy_int + 4, fill="#9333EA", outline="")
                self.canvas.create_text(sx_int + 8, sy_int + 4, text="X-intercept", fill="#9333EA", anchor="w", font=("Arial", 8, "bold"))

    def draw_hyperbola_helpers(self):
        try:
            xc = self.get_value("Pusat X / xc", 0)
            yc = self.get_value("Pusat Y / yc", 0)
            a = self.get_value("Parameter a", 45)
            b = self.get_value("Parameter b", 35)
        except Exception:
            return

        if a == 0:
            return

        c = math.sqrt(a * a + b * b)
        slope = b / a

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        x_min = (0 - self.center_x()) / self.scale
        x_max = (w - self.center_x()) / self.scale

        # Asimtot
        x1, y1 = x_min, yc + slope * (x_min - xc)
        x2, y2 = x_max, yc + slope * (x_max - xc)
        sx1, sy1 = self.world_to_screen(x1, y1)
        sx2, sy2 = self.world_to_screen(x2, y2)
        self.canvas.create_line(sx1, sy1, sx2, sy2, fill="#EF4444", dash=(6, 4), width=2)

        x1, y1 = x_min, yc - slope * (x_min - xc)
        x2, y2 = x_max, yc - slope * (x_max - xc)
        sx1, sy1 = self.world_to_screen(x1, y1)
        sx2, sy2 = self.world_to_screen(x2, y2)
        self.canvas.create_line(sx1, sy1, sx2, sy2, fill="#EF4444", dash=(6, 4), width=2)

        self.canvas.create_text(
            self.world_to_screen(x_max, yc + slope * (x_max - xc))[0] - 10,
            self.world_to_screen(x_max, yc + slope * (x_max - xc))[1] - 14,
            text="Asimtot +",
            fill="#EF4444",
            anchor="se",
            font=("Arial", 8, "bold")
        )
        self.canvas.create_text(
            self.world_to_screen(x_max, yc - slope * (x_max - xc))[0] - 10,
            self.world_to_screen(x_max, yc - slope * (x_max - xc))[1] + 14,
            text="Asimtot -",
            fill="#EF4444",
            anchor="se",
            font=("Arial", 8, "bold")
        )

        # Vertices
        for vx in (xc - a, xc + a):
            sxv, syv = self.world_to_screen(vx, yc)
            self.canvas.create_oval(sxv - 5, syv - 5, sxv + 5, syv + 5, outline="#EF4444", width=2)
            self.canvas.create_text(sxv + 8, syv + 8, text="Vertex", fill="#EF4444", anchor="nw", font=("Arial", 8, "bold"))

        # Foci
        for fx in (xc - c, xc + c):
            sxf, syf = self.world_to_screen(fx, yc)
            self.canvas.create_oval(sxf - 4, syf - 4, sxf + 4, syf + 4, fill="#EF4444", outline="")
            self.canvas.create_text(sxf + 8, syf - 10, text="Focus", fill="#EF4444", anchor="w", font=("Arial", 8, "bold"))

        # Rectangle for a and b
        top_left = self.world_to_screen(xc - a, yc + b)
        bottom_right = self.world_to_screen(xc + a, yc - b)
        self.canvas.create_rectangle(top_left[0], top_left[1], bottom_right[0], bottom_right[1], outline="#EF4444", dash=(3, 3), width=1)
        self.canvas.create_text(
            self.world_to_screen(xc + a, yc)[0] - 6,
            self.world_to_screen(xc + a, yc)[1] + 12,
            text="a",
            fill="#EF4444",
            anchor="ne",
            font=("Arial", 8, "bold")
        )
        self.canvas.create_text(
            self.world_to_screen(xc, yc + b)[0] + 6,
            self.world_to_screen(xc, yc + b)[1] + 6,
            text="b",
            fill="#EF4444",
            anchor="nw",
            font=("Arial", 8, "bold")
        )

        self.canvas.create_text(
            self.world_to_screen(xc, yc)[0] + 8,
            self.world_to_screen(xc, yc)[1] - 16,
            text="Center",
            fill="#EF4444",
            anchor="nw",
            font=("Arial", 8, "bold")
        )

    def draw_active_rays_and_angles(self):
        """Gambar ray + busur sudut dari pusat.

        Prioritas titik:
        1) selected_points (2 titik terakhir yang diklik)
        2) jika kosong: titik aktif berdasarkan active_frame_index
        """
        try:
            xc = self.get_value("Pusat X / xc", 0)
            yc = self.get_value("Pusat Y / yc", 0)
        except Exception:
            return

        if not hasattr(self, "selected_points"):
            self.selected_points = []

        if len(self.selected_points) >= 2:
            points = self.selected_points[-2:]
        else:
            point = self.get_active_point()
            points = [point] if point else []

        if not points:
            return

        sx0, sy0 = self.world_to_screen(xc, yc)
        angles = []

        for p in points:
            if p is None:
                continue
            dx = p["x"] - xc
            dy = p["y"] - yc
            theta = math.atan2(dy, dx)
            angles.append(theta)

            sx, sy = self.world_to_screen(p["x"], p["y"])
            self.canvas.create_line(sx0, sy0, sx, sy, fill=self.purple, width=3)
            self.canvas.create_text(sx + 10, sy - 10, text=f"θ={theta:.2f}", fill=self.purple, anchor="w", font=("Arial", 9, "bold"))

        if len(angles) == 2:
            theta1, theta2 = angles
            start = math.degrees(theta1)
            end = math.degrees(theta2)
            
            extent = end - start
            while extent <= -180:
                    extent += 360
                
            while extent > 180:
                    extent -= 360

            # Tkinter arc: extent positif menggambar searah jarum jam (default).
            # Logika sebelumnya membuatnya “terbalik”, jadi hapus negasi.
            arc_r = 70
            start_angle = start % 360
            self.canvas.create_arc(
                sx0 - arc_r,
                sy0 - arc_r,
                sx0 + arc_r,
                sy0 + arc_r,
                start=start_angle,
                extent=extent,
                style=tk.ARC,
                outline=self.purple,
                width=4
            )
            self.canvas.create_text(
                sx0 + arc_r + 25,
                sy0 - 25,
                text=f"Δθ={abs(extent):.2f}°",
                fill=self.purple,
                anchor="w",
                font=("Arial", 9, "bold")
            )

        elif len(angles) == 1:
            theta = angles[0]
            arc_r = 70
            # Konsisten dengan kasus 2 titik: hilangkan negasi pada start/extent
            start_angle = math.degrees(theta) % 360
            self.canvas.create_arc(
                sx0 - arc_r,
                sy0 - arc_r,
                sx0 + arc_r,
                sy0 + arc_r,
                start=start_angle,
                extent=math.degrees(theta),
                style=tk.ARC,
                outline=self.purple,
                width=4
            )
            deg = math.degrees(theta)

            self.canvas.create_text(
                    sx0 + arc_r + 12,
                    sy0 - 8,
                    text=f"{deg:.1f}°",
                    fill=self.purple,
                    anchor="w",
                    font=("Arial", 9, "bold")
                )

    def draw_title(self):
        self.canvas.create_text(
            self.canvas.winfo_width() / 2,
            28,
            text="REPRESENTASI PARAMETRIK KURVA KONIK",
            fill=self.bg_dark,
            font=("Arial", 15, "bold")
        )

    # INFO
    # ==========================================================
    def click_point(self, frame, frame_index, point):
        self.active_frame_index = frame_index
        self.active_point_branch = point.get("branch")

        # Simpan 2 titik terakhir yang diklik (untuk menampilkan sudut dari 2 titik ke pusat)
        if not hasattr(self, "selected_points"):
            self.selected_points = []
        self.selected_points.append(point)
        # simpan maksimal 2 titik
        if len(self.selected_points) > 2:
            self.selected_points = self.selected_points[-2:]

        self.show_point_info(point, frame)
        self.add_process(
            f"Klik interval {frame['frame']} | {point.get('branch', '')} | t={point['t']:.2f}, x={point['x']:.2f}, y={point['y']:.2f}"
        )
        self.draw_all()


    def show_frame_info(self, frame):
        if self.current_curve.get() == "Hiperbola":
            kanan = frame["points"][0]
            kiri = frame["points"][1]

            info = (
                f"Interval : {frame['frame']}\n"
                f"t        : {frame['t']:.4f}\n\n"
                f"Cabang kanan\n"
                f"x = {kanan['x']:.4f}\n"
                f"y = {kanan['y']:.4f}\n\n"
                f"Cabang kiri\n"
                f"x = {kiri['x']:.4f}\n"
                f"y = {kiri['y']:.4f}"
            )
            self.point_info.config(text=info)
        else:
            self.show_point_info(frame["points"][0], frame)

    def show_point_info(self, p, frame):
        extra = ""

        if p["curve"] == "Hiperbola":
            extra = f"Cabang : {p['branch']}\n"

        info = (
            f"Interval : {frame['frame']}\n"
            f"Kurva    : {p['curve']}\n"
            f"{extra}"
            f"t        : {p['t']:.4f}\n"
            f"x        : {p['x']:.4f}\n"
            f"y        : {p['y']:.4f}\n\n"
            f"{p['formula']}"
        )

        self.point_info.config(text=info)

    def update_status(self):
        status = "PLAY" if self.is_animating and not self.is_paused else "PAUSE"
        self.status_label.config(text=f"Status : {status}")

        current_t = "-"

        if self.active_frame_index is not None and self.active_frame_index < len(self.frames):
            current_t = f"{self.frames[self.active_frame_index]['t']:.3f}"

        total_points_visible = sum(len(frame["points"]) for frame in self.visible_frames())
        total_points = sum(len(frame["points"]) for frame in self.frames)

        self.stat_label.config(
            text=(
                f"t saat ini = {current_t}\n"
                f"Interval tampil = {self.visible_count}\n"
                f"Total interval = {len(self.frames)}\n"
                f"Titik tampil = {total_points_visible}\n"
                f"Total titik = {total_points}\n"
                f"Zoom scale = {self.scale:.2f}"
            )
        )

    def add_process(self, text):
        self.process_text.insert("end", text + "\n")
        self.process_text.see("end")

    # ==========================================================
    # ZOOM DAN GESER
    # ==========================================================
    def zoom_in(self):
        self.scale *= 1.15
        self.draw_all()

    def zoom_out(self):
        self.scale /= 1.15
        if self.scale < 0.5:
            self.scale = 0.5
        self.draw_all()

    def mouse_wheel_zoom(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def pan(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
        self.draw_all()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_canvas(self, event):
        if self.drag_start_x is None or self.drag_start_y is None:
            return

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        self.offset_x += dx
        self.offset_y += dy

        self.drag_start_x = event.x
        self.drag_start_y = event.y

        self.draw_all()

    def stop_drag(self, event):
        self.drag_start_x = None
        self.drag_start_y = None


if __name__ == "__main__":
    root = tk.Tk()
    app = KurvaKonikApp(root)
    root.mainloop()

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class KalkulusUMKMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kalkulus Optimasi UMKM Ketoprak - Proyek Akhir Kalkulus Dasar (UNSIL)")
        self.geometry("1300x820")
        self.minsize(1050, 700)

        self.presets = {
            "UMKM Ketoprak (Studi Kasus Laporan)": {
                "p": 15000.0,
                "c": 60000.0,
                "b": 8000.0,
                "a": 50.0,
                "q_max": 140
            },
            "UMKM Warung Nasi Goreng": {
                "p": 18000.0,
                "c": 90000.0,
                "b": 9500.0,
                "a": 35.0,
                "q_max": 180
            },
            "UMKM Kopi Susu Kekinian": {
                "p": 22000.0,
                "c": 120000.0,
                "b": 7500.0,
                "a": 65.0,
                "q_max": 150
            },
            "Kustom Parameter Sendiri": {
                "p": 15000.0,
                "c": 60000.0,
                "b": 8000.0,
                "a": 50.0,
                "q_max": 140
            }
        }

        self.p = 15000.0
        self.c = 60000.0
        self.b = 8000.0
        self.a = 50.0
        self.q_max = 140
        self.slider_q = 70.0
        self.sidebar_width = 380

        self.calc_results = {}
        self.hover_items = {}

        self._setup_layout()
        self._calculate_calculus_model()
        self._update_all_views()

    def _setup_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self._create_header()
        self._create_sidebar()
        self._create_splitter()
        self._create_main_content()

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color=("gray85", "#1e1e24"))
        self.header_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)

        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="SIMULASI KALKULUS: OPTIMASI KEUNTUNGAN UMKM",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            title_box,
            text="Proyek Akhir Kalkulus Dasar - Penerapan Turunan pada UMKM Ketoprak (Informatika - Universitas Siliwangi)",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70")
        )
        subtitle_lbl.pack(anchor="w")

        right_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_box.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        theme_lbl = ctk.CTkLabel(right_box, text="Mode Tema:", font=ctk.CTkFont(size=12))
        theme_lbl.pack(side="left", padx=(0, 8))

        self.theme_option = ctk.CTkOptionMenu(
            right_box,
            values=["Dark", "Light"],
            command=self._change_theme,
            width=90,
            height=28
        )
        self.theme_option.set("Dark")
        self.theme_option.pack(side="left")

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_propagate(False)

        self.side_scroll = ctk.CTkScrollableFrame(self.sidebar_frame, width=self.sidebar_width - 24, fg_color="transparent")
        self.side_scroll.pack(fill="both", expand=True, padx=8, pady=10)

        sb_title = ctk.CTkLabel(
            self.side_scroll,
            text="PARAMETER USAHA",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        sb_title.pack(anchor="w", pady=(0, 10))

        preset_lbl = ctk.CTkLabel(self.side_scroll, text="Pilih Contoh / Preset:", font=ctk.CTkFont(size=12, weight="bold"))
        preset_lbl.pack(anchor="w", pady=(0, 2))

        self.preset_menu = ctk.CTkOptionMenu(
            self.side_scroll,
            values=list(self.presets.keys()),
            command=self._apply_preset,
            font=ctk.CTkFont(size=11)
        )
        self.preset_menu.pack(fill="x", pady=(0, 12))

        self.entries = {}
        fields = [
            ("p", "Harga Jual (p)", "Rupiah per porsi", "15000"),
            ("c", "Biaya Tetap (c / FC)", "Sewa, listrik, gas (Rp/hari)", "60000"),
            ("b", "Biaya Var. Linier (b)", "Bahan baku dasar (Rp/porsi)", "8000"),
            ("a", "Koef. Kuadrat (a)", "Disekonomi biaya (Rp/porsi²)", "50"),
            ("q_max", "Batas Rentang Porsi", "Maksimal porsi di grafik", "140")
        ]

        for key, label_text, desc, default_val in fields:
            lbl = ctk.CTkLabel(self.side_scroll, text=label_text, font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(anchor="w", pady=(2, 0))

            sub = ctk.CTkLabel(self.side_scroll, text=desc, font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"))
            sub.pack(anchor="w", pady=(0, 2))

            entry = ctk.CTkEntry(self.side_scroll, height=32, font=ctk.CTkFont(size=12))
            entry.insert(0, default_val)
            entry.pack(fill="x", pady=(0, 8))
            self.entries[key] = entry

        btn_frame = ctk.CTkFrame(self.side_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(6, 15))

        calc_btn = ctk.CTkButton(
            btn_frame,
            text="Hitung & Perbarui",
            command=self._on_click_calculate,
            fg_color="#10b981",
            hover_color="#059669",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        calc_btn.pack(fill="x", pady=(0, 6))

        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Reset Kasus Ketoprak",
            command=lambda: self._apply_preset("UMKM Ketoprak (Studi Kasus Laporan)"),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            height=30,
            font=ctk.CTkFont(size=11)
        )
        reset_btn.pack(fill="x")

        sep = ctk.CTkFrame(self.side_scroll, height=2, fg_color=("gray70", "#334155"))
        sep.pack(fill="x", pady=12)

        slider_title = ctk.CTkLabel(
            self.side_scroll,
            text="SIMULASI INTERAKTIF PORSI (q)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        slider_title.pack(anchor="w", pady=(0, 4))

        self.slider_val_label = ctk.CTkLabel(
            self.side_scroll,
            text=f"Jumlah Porsi Terpilih: 70 porsi/hari",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.slider_val_label.pack(anchor="w", pady=(0, 2))

        self.q_slider = ctk.CTkSlider(
            self.side_scroll,
            from_=0,
            to=140,
            number_of_steps=140,
            command=self._on_slider_change
        )
        self.q_slider.set(70)
        self.q_slider.pack(fill="x", pady=(0, 10))

        self.live_card = ctk.CTkFrame(self.side_scroll, fg_color=("gray90", "#18181b"), corner_radius=8)
        self.live_card.pack(fill="x", pady=(0, 10), padx=2)

        calc_w = max(240, self.sidebar_width - 60)

        self.live_status_lbl = ctk.CTkLabel(
            self.live_card,
            text="Status: TITIK OPTIMUM",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10b981",
            wraplength=calc_w,
            justify="left"
        )
        self.live_status_lbl.pack(anchor="w", padx=10, pady=(8, 2))

        self.live_rev_lbl = ctk.CTkLabel(
            self.live_card,
            text="Pendapatan R(q): Rp 1.050.000",
            font=ctk.CTkFont(size=11),
            wraplength=calc_w,
            justify="left"
        )
        self.live_rev_lbl.pack(anchor="w", padx=10, pady=1)

        self.live_cost_lbl = ctk.CTkLabel(
            self.live_card,
            text="Biaya Total C(q): Rp 865.000",
            font=ctk.CTkFont(size=11),
            wraplength=calc_w,
            justify="left"
        )
        self.live_cost_lbl.pack(anchor="w", padx=10, pady=1)

        self.live_profit_lbl = ctk.CTkLabel(
            self.live_card,
            text="Keuntungan P(q): Rp 185.000",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            wraplength=calc_w,
            justify="left"
        )
        self.live_profit_lbl.pack(anchor="w", padx=10, pady=2)

        self.live_mp_lbl = ctk.CTkLabel(
            self.live_card,
            text="Laju Laba P'(q): Rp 0/porsi",
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray70"),
            wraplength=calc_w,
            justify="left"
        )
        self.live_mp_lbl.pack(anchor="w", padx=10, pady=(1, 8))

    def _create_splitter(self):
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        s_bg = "#334155" if is_dark else "#cbd5e1"
        self.splitter = tk.Frame(self, width=7, bg=s_bg, cursor="sb_h_double_arrow")
        self.splitter.grid(row=1, column=1, sticky="ns", padx=0, pady=0)

        self.splitter.bind("<ButtonPress-1>", self._on_splitter_press)
        self.splitter.bind("<B1-Motion>", self._on_splitter_drag)
        self.splitter.bind("<ButtonRelease-1>", self._on_splitter_release)
        self.splitter.bind("<Enter>", self._on_splitter_enter)
        self.splitter.bind("<Leave>", self._on_splitter_leave)

    def _on_splitter_press(self, event):
        self._drag_start_x = event.x_root
        self._start_sidebar_width = self.sidebar_frame.winfo_width()
        self.splitter.configure(bg="#2563eb")

    def _on_splitter_drag(self, event):
        delta = event.x_root - self._drag_start_x
        new_width = max(280, min(650, self._start_sidebar_width + delta))
        self.sidebar_width = new_width
        self.sidebar_frame.configure(width=new_width)
        self.side_scroll.configure(width=new_width - 24)

        calc_w = max(220, new_width - 60)
        self.live_status_lbl.configure(wraplength=calc_w)
        self.live_rev_lbl.configure(wraplength=calc_w)
        self.live_cost_lbl.configure(wraplength=calc_w)
        self.live_profit_lbl.configure(wraplength=calc_w)
        self.live_mp_lbl.configure(wraplength=calc_w)

    def _on_splitter_release(self, event):
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        self.splitter.configure(bg="#334155" if is_dark else "#cbd5e1")

    def _on_splitter_enter(self, event):
        self.splitter.configure(bg="#3b82f6")

    def _on_splitter_leave(self, event):
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        self.splitter.configure(bg="#334155" if is_dark else "#cbd5e1")

    def _create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=2, sticky="nsew", padx=12, pady=12)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._create_summary_bar()

        self.tabview = ctk.CTkTabview(self.main_frame, corner_radius=10)
        self.tabview.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.tab_grafik = self.tabview.add("Visualisasi Grafik")
        self.tab_kalkulus = self.tabview.add("Penurunan Rumus Kalkulus")
        self.tab_tabel = self.tabview.add("Tabel Data Simulasi")
        self.tab_laporan = self.tabview.add("Laporan & Analisis Proyek")

        self._configure_tabview_navbar()

        self._setup_tab_grafik()
        self._setup_tab_kalkulus()
        self._setup_tab_tabel()
        self._setup_tab_laporan()

    def _configure_tabview_navbar(self):
        self.tabview.grid_columnconfigure(0, weight=1)
        tab_sb = self.tabview._segmented_button
        tab_sb.grid_configure(sticky="ew", padx=20, pady=(4, 0))
        for i in range(len(tab_sb._value_list)):
            tab_sb.grid_columnconfigure(i, weight=1, uniform="main_tabs")

    def _create_summary_bar(self):
        self.summary_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.summary_bar.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            self.summary_bar.grid_columnconfigure(i, weight=1)

        self.card_q_opt = self._make_metric_card(self.summary_bar, 0, "Titik Kritis (qc)", "70 porsi", "Syarat Stasioner f'(q) = 0", "#3b82f6")
        self.card_profit_max = self._make_metric_card(self.summary_bar, 1, "Nilai Maksimum f(qc)", "Rp 185.000", "Laba harian puncak mutlak", "#10b981")
        self.card_bep = self._make_metric_card(self.summary_bar, 2, "Nilai Minimum & BEP", "-Rp 60.000", "Batas rentang laba f(q)>=0", "#f59e0b")
        self.card_test2 = self._make_metric_card(self.summary_bar, 3, "Uji Turunan Kedua", "f''(q) = -100 < 0", "Kurva Konkaf / Maks Mutlak", "#8b5cf6")

    def _make_metric_card(self, parent, col, title, value, subtitle, accent_color):
        card = ctk.CTkFrame(parent, fg_color=("gray90", "#1e1e24"), corner_radius=8, border_width=1, border_color=("gray75", "#334155"))
        card.grid(row=0, column=col, padx=5, pady=2, sticky="nsew")

        strip = ctk.CTkFrame(card, height=4, fg_color=accent_color, corner_radius=2)
        strip.pack(fill="x", side="top")

        t_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray30", "gray70"))
        t_lbl.pack(anchor="w", padx=10, pady=(6, 0))

        v_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=15, weight="bold"), text_color=accent_color)
        v_lbl.pack(anchor="w", padx=10, pady=(1, 0))

        s_lbl = ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(size=9), text_color=("gray40", "gray60"))
        s_lbl.pack(anchor="w", padx=10, pady=(0, 6))

        return {"card": card, "val_lbl": v_lbl, "sub_lbl": s_lbl}

    def _setup_tab_grafik(self):
        self.tab_grafik.grid_rowconfigure(1, weight=1)
        self.tab_grafik.grid_columnconfigure(0, weight=1)

        ctrl_bar = ctk.CTkFrame(self.tab_grafik, fg_color="transparent")
        ctrl_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 6))

        ctrl_bar.grid_columnconfigure(0, weight=0)
        ctrl_bar.grid_columnconfigure(1, weight=1)
        ctrl_bar.grid_columnconfigure(2, weight=0)

        mode_lbl = ctk.CTkLabel(ctrl_bar, text="Mode Tampilan Grafik:", font=ctk.CTkFont(size=12, weight="bold"))
        mode_lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.graph_mode = ctk.CTkSegmentedButton(
            ctrl_bar,
            values=[
                "Kurva Keuntungan P(q)",
                "Pendapatan R(q) vs Biaya C(q)",
                "Pendekatan Marjinal (MR vs MC)",
                "Multi-Grafik (3-in-1 Dashboard)"
            ],
            command=self._on_graph_mode_change
        )
        self.graph_mode.set("Kurva Keuntungan P(q)")
        self.graph_mode.grid(row=0, column=1, sticky="ew", padx=15)
        for i in range(4):
            self.graph_mode.grid_columnconfigure(i, weight=1, uniform="mode_tabs")

        save_fig_btn = ctk.CTkButton(
            ctrl_bar,
            text="Simpan Grafik (PNG)",
            command=self._save_graph_image,
            width=140,
            height=28,
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            font=ctk.CTkFont(size=11)
        )
        save_fig_btn.grid(row=0, column=2, sticky="e")

        self.plot_frame = ctk.CTkFrame(self.tab_grafik, fg_color=("gray95", "#18181b"), corner_radius=8)
        self.plot_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        self.canvas.mpl_connect("motion_notify_event", self._on_plot_hover)
        self.canvas.mpl_connect("axes_leave_event", self._on_plot_leave)

        self.toolbar_frame = ctk.CTkFrame(self.tab_grafik, fg_color="transparent", height=32)
        self.toolbar_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(2, 0))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def _setup_tab_kalkulus(self):
        self.tab_kalkulus.grid_rowconfigure(0, weight=1)
        self.tab_kalkulus.grid_columnconfigure(0, weight=1)

        self.calc_scroll = ctk.CTkScrollableFrame(self.tab_kalkulus)
        self.calc_scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.calc_text_label = ctk.CTkLabel(
            self.calc_scroll,
            text="",
            font=ctk.CTkFont(family="Consolas", size=12),
            justify="left",
            anchor="w"
        )
        self.calc_text_label.pack(fill="both", expand=True, padx=15, pady=15)

    def _setup_tab_tabel(self):
        self.tab_tabel.grid_rowconfigure(1, weight=1)
        self.tab_tabel.grid_columnconfigure(0, weight=1)

        t_ctrl = ctk.CTkFrame(self.tab_tabel, fg_color="transparent")
        t_ctrl.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 6))

        t_lbl = ctk.CTkLabel(
            t_ctrl,
            text="Data Komputasi Produksi Harian UMKM (Step: 5 Porsi + Titik Optimum & BEP)",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        t_lbl.pack(side="left")

        export_btn = ctk.CTkButton(
            t_ctrl,
            text="Ekspor ke CSV / Excel",
            command=self._export_table_csv,
            fg_color="#10b981",
            hover_color="#059669",
            height=28,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        export_btn.pack(side="right")

        tree_frame = ctk.CTkFrame(self.tab_tabel, corner_radius=8)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#242424",
            foreground="#f3f4f6",
            fieldbackground="#242424",
            font=("Segoe UI", 10),
            rowheight=24
        )
        style.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold")
        )
        style.map("Treeview", background=[("selected", "#2563eb")])

        cols = ("q", "R", "C", "P", "AC", "MR", "MC", "P_prime", "status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="extended")

        col_configs = [
            ("q", "Porsi (q)", 75, "center"),
            ("R", "Pendapatan R(q)", 125, "e"),
            ("C", "Total Biaya C(q)", 125, "e"),
            ("P", "Keuntungan P(q)", 125, "e"),
            ("AC", "Biaya Rata2/Porsi", 120, "e"),
            ("MR", "Marginal Rev (MR)", 115, "e"),
            ("MC", "Marginal Cost (MC)", 115, "e"),
            ("P_prime", "Laju Laba P'(q)", 115, "e"),
            ("status", "Status Finansial", 130, "center")
        ]

        for col_id, col_name, width, align in col_configs:
            self.tree.heading(col_id, text=col_name)
            self.tree.column(col_id, width=width, anchor=align)

        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.tag_configure("optimal", background="#064e3b", foreground="#a7f3d0")
        self.tree.tag_configure("loss", background="#450a0a", foreground="#fecaca")
        self.tree.tag_configure("bep", background="#78350f", foreground="#fde68a")

    def _setup_tab_laporan(self):
        self.tab_laporan.grid_rowconfigure(0, weight=1)
        self.tab_laporan.grid_columnconfigure(0, weight=1)

        self.lap_scroll = ctk.CTkScrollableFrame(self.tab_laporan)
        self.lap_scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        laporan_content = """
======================================================================================================
               LAPORAN ILMIAH PROYEK AKHIR MATA KULIAH KALKULUS DASAR
======================================================================================================

Judul Proyek:
PENERAPAN KONSEP TURUNAN DALAM MENENTUKAN KEUNTUNGAN MAKSIMUM PADA UMKM KETOPRAK

Institusi:
Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi (2026)

Format Proyek:
Team Project-Based Learning (Ujian Akhir Semester Kalkulus Dasar)
Topik Pilihan 1: Penerapan Turunan dalam Optimasi Keuntungan Usaha

------------------------------------------------------------------------------------------------------
1. ABSTRAK & LATAR BELAKANG
------------------------------------------------------------------------------------------------------
Usaha Mikro, Kecil, dan Menengah (UMKM) makanan menghadapi tantangan dalam menentukan jumlah porsi harian
yang paling menguntungkan. Menambah produksi memang berpotensi menaikkan pendapatan, namun di saat yang sama
akan memicu kenaikan biaya yang lebih cepat (disekonomi skala) akibat kelelahan kerja, lembur, dan pembelian
bahan baku pelengkap secara mendadak dengan harga eceran.

Studi ini memodelkan hubungan antara porsi produksi (q), fungsi pendapatan R(q), fungsi biaya C(q),
dan fungsi keuntungan P(q). Menggunakan metode kalkulus diferensial, turunan pertama digunakan untuk
menemukan titik kritis stasioner, sedangkan uji turunan kedua digunakan untuk memastikan titik maksimum mutlak.

------------------------------------------------------------------------------------------------------
2. PEMODELAN MATEMATIKA KALKULUS
------------------------------------------------------------------------------------------------------
- Variabel Keputusan : q (jumlah porsi ketoprak diproduksi & terjual per hari, q >= 0)
- Parameter Model     :
    * Harga jual (p)            : Rp 15.000 / porsi
    * Biaya tetap harian (c/FC) : Rp 60.000 (sewa tempat, gas, penyusutan alat gerobak)
    * Biaya variabel dasar (b)  : Rp 8.000 (tahu, lontong, bihun, tauge, kerupuk, bumbu kacang dasar)
    * Koefisien kuadrat (a)     : Rp 50/porsi^2 (faktor disekonomi skala / kenaikan biaya marjinal)

Fungsi yang Terbentuk:
1. Fungsi Pendapatan : R(q) = 15.000 q
2. Fungsi Biaya      : C(q) = 50 q^2 + 8.000 q + 60.000
3. Fungsi Keuntungan : f(q) = R(q) - C(q)
                     : f(q) = -50 q^2 + 7.000 q - 60.000

------------------------------------------------------------------------------------------------------
3. PENERAPAN KONSEP TURUNAN: TURUNAN PERTAMA, TITIK KRITIS, NILAI MAKSIMUM & MINIMUM
------------------------------------------------------------------------------------------------------
A. Konsep Turunan Pertama f'(q):
   Laju perubahan sesaat keuntungan terhadap jumlah porsi:
   f'(q) = d/dq [-50 q^2 + 7.000 q - 60.000]
   f'(q) = -100 q + 7.000
   Geometris: f'(q) adalah gradien garis singgung kurva laba f(q).
   Ekonomis : f'(q) adalah Laba Marjinal (Marginal Profit).

B. Konsep Titik Kritis (Critical Point):
   Titik kritis stasioner dicapai saat turunan pertama bernilai nol:
   f'(q) = 0
   -100 q + 7.000 = 0
   100 q = 7.000
   qc = 70 porsi / hari
   Kesimpulan: qc = 70 adalah satu-satunya titik kritis di dalam domain produksi.

C. Konsep Nilai Maksimum dan Nilai Minimum:
   1. Uji Turunan Pertama:
      - Untuk q < 70 : f'(q) > 0 (fungsi monoton naik).
      - Untuk q > 70 : f'(q) < 0 (fungsi monoton turun).
      Karena tanda f'(q) berganti dari positif ke negatif di qc = 70, maka f(70) adalah nilai maksimum lokal.
   2. Uji Turunan Kedua & Kecekungan:
      f''(q) = d/dq [-100 q + 7.000] = -100
      Karena f''(q) = -100 < 0 untuk seluruh q, kurva bersifat konkaf ke bawah (cekung ke bawah) secara global.
      Hal ini membuktikan qc = 70 adalah TITIK MAKSIMUM MUTLAK GLOBAL.
   3. Teorema Nilai Ekstrem pada Interval Tertutup [0, 140]:
      - Nilai Maksimum Mutlak : f(70) = Rp 185.000 / hari (pada omzet Rp 1.050.000 dan biaya Rp 865.000).
      - Nilai Minimum Mutlak : f(0) = -Rp 60.000 / hari (beban biaya tetap saat tidak memproduksi)
                               dan f(140) = -Rp 60.000 / hari (disekonomi biaya akibat beban kuadrat).

D. Konsep Aplikasi Turunan dalam Optimasi Nyata UMKM:
   1. Keseimbangan Ekonomi Marjinal (MR = MC):
      f'(q) = 0  <=>  R'(q) - C'(q) = 0  <=>  MR = MC
      MR(q) = Rp 15.000 / porsi
      MC(q) = 100 q + 8.000
      Pada qc = 70: MC(70) = 100(70) + 8.000 = Rp 15.000 (Keseimbangan tercapai).
   2. Analisis Titik Impas (Break-Even Point / BEP) saat f(q) = 0:
      -50 q^2 + 7.000 q - 60.000 = 0
      Diskriminan D = 7000^2 - 4(50)(60000) = 37.000.000
      q_BEP1 = 9,17 porsi (dibulatkan 10 porsi untuk mulai untung).
      q_BEP2 = 130,83 porsi (dibulatkan 130 porsi batas aman kapasitas).
      Rentang Usaha Menguntungkan: 10 <= q <= 130 porsi per hari.

------------------------------------------------------------------------------------------------------
4. INTERPRETASI EKONOMI MARJINAL (MICROECONOMICS INSIGHT)
------------------------------------------------------------------------------------------------------
Dalam teori ekonomi manajerial, keuntungan maksimal tercapai ketika Pendapatan Marjinal sama dengan
Biaya Marjinal:
   MR(q) = R'(q) = Rp 15.000
   MC(q) = C'(q) = 100 q + 8.000
   Kondisi MR = MC:
   15.000 = 100 q + 8.000  =>  100 q = 7.000  =>  q* = 70 porsi.

Penjelasan:
- Selama q < 70, MR > MC (tambahan pendapatan lebih besar daripada tambahan biaya). Memperbanyak porsi
  akan MENAMBAH keuntungan total.
- Saat q = 70, MR = MC (keuntungan berada di puncak optimal).
- Saat q > 70, MR < MC (tambahan biaya melebihi pendapatan). Memaksakan menambah porsi justru akan
  MENURUNKAN keuntungan total akibat biaya lembur/bahan mahal.

------------------------------------------------------------------------------------------------------
5. REKOMENDASI STRATEGIS UNTUK PELAKU UMKM
------------------------------------------------------------------------------------------------------
1. Target Produksi Harian Ideal:
   Pelaku usaha ketoprak sebaiknya menargetkan produksi di sekitar 70 porsi per hari untuk mendapatkan
   laba harian maksimal Rp 185.000 (sekitar Rp 5.550.000 / bulan).
2. Hindari Over-Produksi:
   Membuat lebih dari 100-130 porsi per hari dengan satu gerobak justru meningkatkan risiko kerugian karena
   kelelahan operasional dan bahan yang tidak habis terjual.
3. Catat Biaya Nyata (Full Costing):
   Penting untuk mencatat biaya tetap (sewa, listrik, gas) dan biaya variabel secara berkala untuk
   menyesuaikan harga jual apabila terjadi lonjakan inflasi bahan pangan.

------------------------------------------------------------------------------------------------------
6. KELOMPOK PROYEK & DAFTAR REFERENSI
------------------------------------------------------------------------------------------------------
Tim Penyusun (Informatika - Fakultas Teknik Universitas Siliwangi 2026):
1. [Nama Anggota 1] - [NPM] (Koordinator & Metodologi)
2. [Nama Anggota 2] - [NPM] (Landasan Teori Kalkulus & Ekonomi)
3. [Nama Anggota 3] - [NPM] (Pemodelan Matematika & Fungsi Biaya)
4. [Nama Anggota 4] - [NPM] (Perhitungan Turunan & Titik Kritis)
5. [Nama Anggota 5] - [NPM] (Pemrograman GUI Python & Visualisasi)
6. [Nama Anggota 6] - [NPM] (Analisis Hasil & Penyusunan Laporan)

Referensi Ilmiah:
1. Stewart, J. (2016). Calculus: Early Transcendentals (8th ed.). Cengage Learning.
2. Nurwahidah, N., & Mariani, A. (2021). Turunan (Derivatif): Sebuah pendekatan matematis dalam analisis
   keuntungan maksimum. Jurnal MSA, 9(1), 1-6.
3. Riani, A. C., Rukmana, A., Safira, N., & Purnamasari, P. (2025). Respon UMKM ketoprak terhadap kenaikan
   harga bahan baku: Implikasi terhadap minat beli konsumen. Jurnal Lentera Pengabdian, 3(3).
4. Azizah, S. U., & Cahyani, N. P. D. (2024). Analisis harga pokok produksi dengan metode full costing.
   Kompeten: Jurnal Ilmiah Ekonomi dan Bisnis, 2(5).
======================================================================================================
"""
        lap_lbl = ctk.CTkLabel(
            self.lap_scroll,
            text=laporan_content,
            font=ctk.CTkFont(family="Consolas", size=11),
            justify="left",
            anchor="w"
        )
        lap_lbl.pack(fill="both", expand=True, padx=15, pady=15)

    def _calculate_calculus_model(self):
        p = self.p
        c = self.c
        b = self.b
        a = self.a

        alpha = p - b

        if a > 0:
            q_opt = alpha / (2.0 * a)
            test2_val = -2.0 * a
            is_max = test2_val < 0
        else:
            q_opt = 0.0
            test2_val = 0.0
            is_max = False

        r_opt = p * q_opt
        c_opt = a * (q_opt ** 2) + b * q_opt + c
        p_opt = r_opt - c_opt
        ac_opt = (c_opt / q_opt) if q_opt > 0 else 0
        margin_pct = (p_opt / r_opt * 100.0) if r_opt > 0 else 0

        D = (alpha ** 2) - (4.0 * a * c)
        if D >= 0 and a > 0:
            sqrt_D = np.sqrt(D)
            q_bep1 = (alpha - sqrt_D) / (2.0 * a)
            q_bep2 = (alpha + sqrt_D) / (2.0 * a)
        else:
            q_bep1 = None
            q_bep2 = None

        self.calc_results = {
            "p": p, "c": c, "b": b, "a": a, "alpha": alpha,
            "q_opt": q_opt, "test2_val": test2_val, "is_max": is_max,
            "r_opt": r_opt, "c_opt": c_opt, "p_opt": p_opt,
            "ac_opt": ac_opt, "margin_pct": margin_pct,
            "D": D, "q_bep1": q_bep1, "q_bep2": q_bep2
        }

    def _apply_preset(self, preset_name):
        if preset_name in self.presets:
            data = self.presets[preset_name]
            self.entries["p"].delete(0, tk.END)
            self.entries["p"].insert(0, str(int(data["p"])))

            self.entries["c"].delete(0, tk.END)
            self.entries["c"].insert(0, str(int(data["c"])))

            self.entries["b"].delete(0, tk.END)
            self.entries["b"].insert(0, str(int(data["b"])))

            self.entries["a"].delete(0, tk.END)
            self.entries["a"].insert(0, str(data["a"]))

            self.entries["q_max"].delete(0, tk.END)
            self.entries["q_max"].insert(0, str(data["q_max"]))

            self._on_click_calculate()

    def _on_click_calculate(self):
        try:
            self.p = float(self.entries["p"].get())
            self.c = float(self.entries["c"].get())
            self.b = float(self.entries["b"].get())
            self.a = float(self.entries["a"].get())
            self.q_max = max(20, int(float(self.entries["q_max"].get())))

            if self.p <= 0 or self.a <= 0 or self.b < 0 or self.c < 0:
                messagebox.showerror("Kesalahan Input", "Parameter p dan a harus bernilai lebih besar dari 0, serta biaya tidak boleh negatif.")
                return

            self._calculate_calculus_model()

            self.q_slider.configure(to=self.q_max, number_of_steps=self.q_max)
            q_star = max(0, min(self.q_max, round(self.calc_results["q_opt"])))
            self.q_slider.set(q_star)
            self.slider_q = float(q_star)

            self._update_all_views()
        except ValueError:
            messagebox.showerror("Format Salah", "Mohon masukkan angka numerik yang valid pada seluruh kolom parameter.")

    def _on_slider_change(self, val):
        self.slider_q = float(val)
        self._update_live_card()
        self._redraw_graph()

    def _on_graph_mode_change(self, val):
        self._redraw_graph()

    def _change_theme(self, mode_str):
        ctk.set_appearance_mode(mode_str.lower())
        is_dark = mode_str.lower() == "dark"
        self.splitter.configure(bg="#334155" if is_dark else "#cbd5e1")
        self._redraw_graph()

    def _update_all_views(self):
        self._update_summary_cards()
        self._update_live_card()
        self._update_kalkulus_text()
        self._populate_table()
        self._redraw_graph()

    def _update_summary_cards(self):
        res = self.calc_results
        q_opt = res["q_opt"]
        p_opt = res["p_opt"]
        test2 = res["test2_val"]
        c = res["c"]

        self.card_q_opt["val_lbl"].configure(text=f"qc = {q_opt:.1f} porsi")
        self.card_profit_max["val_lbl"].configure(text=f"Rp {p_opt:,.0f}".replace(",", "."))

        if res["q_bep1"] is not None and res["q_bep2"] is not None:
            self.card_bep["val_lbl"].configure(text=f"-Rp {c:,.0f}".replace(",", "."))
            self.card_bep["sub_lbl"].configure(text=f"BEP: {res['q_bep1']:.1f} & {res['q_bep2']:.1f} porsi")
        else:
            self.card_bep["val_lbl"].configure(text=f"-Rp {c:,.0f}".replace(",", "."))
            self.card_bep["sub_lbl"].configure(text="Tidak ada BEP real")

        self.card_test2["val_lbl"].configure(text=f"f''(q) = {test2:.0f} < 0")

    def _update_live_card(self):
        q = self.slider_q
        p = self.p
        c = self.c
        b = self.b
        a = self.a

        r = p * q
        cost = a * (q ** 2) + b * q + c
        profit = r - cost
        p_prime = -2.0 * a * q + (p - b)

        self.slider_val_label.configure(text=f"Jumlah Porsi Terpilih: {q:.0f} porsi/hari")
        self.live_rev_lbl.configure(text=f"Pendapatan R(q): Rp {r:,.0f}".replace(",", "."))
        self.live_cost_lbl.configure(text=f"Biaya Total C(q): Rp {cost:,.0f}".replace(",", "."))

        p_str = f"Fungsi Laba f(q): Rp {profit:,.0f}".replace(",", ".")
        self.live_profit_lbl.configure(text=p_str)

        opt_q = self.calc_results["q_opt"]
        if abs(q - opt_q) < 0.5:
            self.live_status_lbl.configure(text="Status: TITIK KRITIS qc (NILAI MAKSIMUM)", text_color="#10b981")
            self.live_profit_lbl.configure(text_color="#10b981")
        elif q == 0:
            self.live_status_lbl.configure(text="Status: UJUNG DOMAIN q=0 (NILAI MINIMUM MUTLAK)", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")
        elif profit > 0:
            self.live_status_lbl.configure(text="Status: ZONA LABA POSITIF (f(q) > 0)", text_color="#3b82f6")
            self.live_profit_lbl.configure(text_color="#3b82f6")
        elif abs(profit) < 100:
            self.live_status_lbl.configure(text="Status: TITIK IMPAS BEP (f(q) = 0)", text_color="#f59e0b")
            self.live_profit_lbl.configure(text_color="#f59e0b")
        else:
            self.live_status_lbl.configure(text="Status: ZONA RUGI DEFISIT (f(q) < 0)", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")

        if p_prime > 50:
            laju_str = f"Turunan Pertama f'(q): +Rp {p_prime:,.0f} (f' > 0: kurva naik)"
        elif p_prime < -50:
            laju_str = f"Turunan Pertama f'(q): -Rp {abs(p_prime):,.0f} (f' < 0: kurva turun)"
        else:
            laju_str = f"Turunan Pertama f'(q): Rp 0 (Titik Kritis qc: f'(qc) = 0)"
        self.live_mp_lbl.configure(text=laju_str)

    def _update_kalkulus_text(self):
        res = self.calc_results
        p = res["p"]
        c = res["c"]
        b = res["b"]
        a = res["a"]
        alpha = res["alpha"]
        q_opt = res["q_opt"]
        p_opt = res["p_opt"]
        r_opt = res["r_opt"]
        c_opt = res["c_opt"]

        penjelasan = f"""
========================================================================================
    PENERAPAN KALKULUS DASAR: TURUNAN PERTAMA, TITIK KRITIS, NILAI MAKSIMUM & MINIMUM,
                    SERTA APLIKASI TURUNAN MENGGUNAKAN RUMUS f(q)
========================================================================================

I. FORMULASI FUNGSI TUJUAN KEUNTUNGAN f(q)
----------------------------------------------------------------------------------------
Dalam kalkulus diferensial, optimasi dimodelkan ke dalam fungsi objektif f(q):
Misalkan:
   q = Jumlah porsi ketoprak yang diproduksi dan terjual per hari (domain: 0 <= q <= {self.q_max}).

1. Fungsi Pendapatan Total (Total Revenue):
   R(q) = p * q
   R(q) = {p:,.0f} * q

2. Fungsi Biaya Total (Total Cost):
   C(q) = a * q^2 + b * q + c
   C(q) = {a} * q^2 + {b:,.0f} * q + {c:,.0f}
   * Konstanta c = Rp {c:,.0f} adalah Biaya Tetap (Fixed Cost) harian.
   * Koefisien b = Rp {b:,.0f} adalah Biaya Variabel Linier bahan baku per porsi.
   * Koefisien a = {a} adalah parameter kuadrat disekonomi skala kapasitas.

3. Fungsi Keuntungan Objektif f(q) = R(q) - C(q):
   f(q) = ({p:,.0f} * q) - ({a} * q^2 + {b:,.0f} * q + {c:,.0f})
   f(q) = -{a} * q^2 + ({p:,.0f} - {b:,.0f}) * q - {c:,.0f}
   f(q) = -{a} * q^2 + {alpha:,.0f} * q - {c:,.0f}

----------------------------------------------------------------------------------------
II. KONSEP TURUNAN PERTAMA f'(q)
----------------------------------------------------------------------------------------
Definisi Turunan Pertama:
   Laju perubahan sesaat dari nilai fungsi f(q) terhadap variabel bebas q.
   Berdasarkan Aturan Pangkat (Power Rule) d/dq [q^n] = n * q^(n-1):

   f'(q) = d/dq [ -{a} * q^2 + {alpha:,.0f} * q - {c:,.0f} ]
   f'(q) = -2 * ({a}) * q + {alpha:,.0f}
   f'(q) = -{2*a:.0f} * q + {alpha:,.0f}

Arti Fisis & Geometris:
   * f'(q) menyatakan kemiringan garis singgung kurva f(q) di setiap titik produksi q.
   * f'(q) menyatakan Laba Marjinal (Marginal Profit), yaitu tambahan keuntungan yang
     diperoleh pelaku usaha untuk setiap tambahan 1 porsi ketoprak yang diproduksi.

----------------------------------------------------------------------------------------
III. KONSEP TITIK KRITIS (CRITICAL POINT)
----------------------------------------------------------------------------------------
Definisi Matematis Titik Kritis:
   Titik kritis suatu fungsi f terjadi pada nilai q dalam domain di mana:
   1. f'(q) = 0 (Titik Stasioner), ATAU
   2. f'(q) tidak terdefinisi (Titik Singular).

Karena f(q) merupakan fungsi kuadrat polinomial yang kontinu dan dapat diturunkan di
seluruh bilangan real, titik kritis dicari dari syarat stasioner (First-Order Condition):
   f'(q) = 0
   -{2*a:.0f} * q + {alpha:,.0f} = 0
   {2*a:.0f} * q = {alpha:,.0f}
   q_c = {alpha:,.0f} / {2*a:.0f}
   q_c = {q_opt:.2f} porsi/hari  (dibulatkan: {round(q_opt)} porsi/hari)

Kesimpulan Titik Kritis:
   Satu-satunya titik kritis stasioner di dalam domain adalah qc = {q_opt:.2f} porsi/hari.

----------------------------------------------------------------------------------------
IV. KONSEP NILAI MAKSIMUM DAN NILAI MINIMUM
----------------------------------------------------------------------------------------
Untuk membuktikan jenis nilai ekstrem pada titik kritis qc serta mengevaluasi nilai
ekstrem mutlak pada domain tertutup [0, {self.q_max}], diterapkan prinsip-prinsip kalkulus:

1. UJI TURUNAN PERTAMA (FIRST DERIVATIVE TEST):
   Evaluasi tanda f'(q) di sekitar titik kritis qc = {q_opt:.2f}:
   * Pada interval 0 <= q < {q_opt:.2f} :
     f'(q) > 0  ==> Fungsi f(q) monoton NAIK (monotonically increasing).
   * Pada interval q > {q_opt:.2f} :
     f'(q) < 0  ==> Fungsi f(q) monoton TURUN (monotonically decreasing).
   Karena tanda f'(q) berubah dari POSITIF (+) menjadi NEGATIF (-) saat melintasi qc = {q_opt:.2f},
   maka f({q_opt:.2f}) terbukti merupakan NILAI MAKSIMUM LOKAL.

2. UJI TURUNAN KEDUA (SECOND DERIVATIVE TEST) & KECEKUNGAN (CONCAVITY):
   Turunan kedua menguji kelengkungan kurva fungsi keuntungan:
   f''(q) = d/dq [ f'(q) ]
   f''(q) = d/dq [ -{2*a:.0f} * q + {alpha:,.0f} ]
   f''(q) = -{2*a:.0f}

   Evaluasi pada titik kritis qc = {q_opt:.2f}:
   f''({q_opt:.2f}) = -{2*a:.0f} < 0
   Karena f''(q) bernilai NEGATIF konstan untuk seluruh q pada domain, kurva f(q)
   bersifat KONKAF KE BAWAH (cekung ke bawah) secara global.
   Hal ini membuktikan secara mutlak bahwa qc = {q_opt:.2f} adalah TITIK MAKSIMUM GLOBAL.

3. EVALUASI NILAI MAKSIMUM DAN MINIMUM PADA INTERVAL TERTUTUP [0, {self.q_max}]:
   Menurut Teorema Nilai Ekstrem (Extreme Value Theorem), fungsi kontinu pada interval tertutup
   pasti mencapai nilai maksimum mutlak dan nilai minimum mutlak pada titik kritis atau batas domain:

   a. Nilai pada batas domain awal (q = 0, Tanpa Produksi):
      f(0) = -{a}*(0)^2 + {alpha:,.0f}*(0) - {c:,.0f}
      f(0) = -Rp {c:,.0f}  <--- NILAI MINIMUM MUTLAK
      (Kerugian operasional terbesar akibat kewajiban membayar Biaya Tetap FC)

   b. Nilai pada titik kritis interior (qc = {q_opt:.2f}, Produksi Optimum):
      f({q_opt:.2f}) = -{a}*({q_opt:.2f})^2 + {alpha:,.0f}*({q_opt:.2f}) - {c:,.0f}
      f({q_opt:.2f}) = Rp {p_opt:,.0f} / hari  <--- NILAI MAKSIMUM MUTLAK
      (Keuntungan harian tertinggi yang dapat diraih pedagang ketoprak)

   c. Nilai pada batas domain akhir (q = {self.q_max}, Produksi Kapasitas Maksimal):
      f({self.q_max}) = -{a}*({self.q_max})^2 + {alpha:,.0f}*({self.q_max}) - {c:,.0f}
      f({self.q_max}) = Rp {(-a*(self.q_max**2) + alpha*self.q_max - c):,.0f}
      (Kerugian akibat lonjakan beban disekonomi kuadrat)

----------------------------------------------------------------------------------------
V. APLIKASI TURUNAN PADA OPTIMASI USAHA UMKM
----------------------------------------------------------------------------------------
Penerapan rumus f(q) dan metode diferensial memberikan solusi konkret bagi bisnis UMKM:

1. Keseimbangan Ekonomi Marjinal (MR = MC):
   Kondisi turunan pertama f'(q) = 0 setara secara matematis dengan:
   d/dq [R(q) - C(q)] = 0  <==>  R'(q) - C'(q) = 0  <==>  R'(q) = C'(q)  <==>  MR = MC
   * Pendapatan Marjinal : MR(q) = R'(q) = Rp {p:,.0f} / porsi
   * Biaya Marjinal      : MC(q) = C'(q) = {2*a:.0f} * q + {b:,.0f}
   Pada titik optimum qc = {q_opt:.2f}:
   MC({q_opt:.2f}) = {2*a:.0f} * ({q_opt:.2f}) + {b:,.0f} = Rp {p:,.0f}
   MR = MC = Rp {p:,.0f} (Keuntungan marjinal sama dengan nol).

2. Titik Impas (Break-Even Point / BEP) di mana f(q) = 0:
   -{a} * q^2 + {alpha:,.0f} * q - {c:,.0f} = 0
   Diskriminan D = ({alpha:,.0f})^2 - 4 * (-{a}) * (-{c:,.0f}) = {res['D']:,.0f}
"""
        if res["q_bep1"] is not None:
            penjelasan += f"""   * Titik Impas Bawah (BEP 1) : q1 = {res['q_bep1']:.2f} porsi/hari
   * Titik Impas Atas (BEP 2)  : q2 = {res['q_bep2']:.2f} porsi/hari
   Rentang Produksi Menguntungkan (f(q) > 0): ({res['q_bep1']:.2f} ; {res['q_bep2']:.2f}) porsi/hari.

3. Rekomendasi Manajerial Produksi:
   * Target Produksi Terbaik : Tepat {round(q_opt)} porsi/hari untuk mencapai laba maksimal Rp {p_opt:,.0f}.
   * Batas Aman Minimum      : Minimal {int(np.ceil(res['q_bep1']))} porsi/hari agar tidak mengalami kerugian.
   * Batas Maksimal Kapasitas: Jangan memaksakan melebihi {int(np.floor(res['q_bep2']))} porsi/hari karena disekonomi biaya.
"""
        else:
            penjelasan += "\n   Diskriminan negatif: Tidak ada titik impas real (usaha selalu rugi pada kombinasi parameter ini)."

        self.calc_text_label.configure(text=penjelasan)

    def _populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        p = self.p
        c = self.c
        b = self.b
        a = self.a
        q_opt = self.calc_results["q_opt"]
        q_bep1 = self.calc_results["q_bep1"]
        q_bep2 = self.calc_results["q_bep2"]

        q_steps = list(range(0, int(self.q_max) + 1, 5))
        special_pts = [round(q_opt, 1)]
        if q_bep1 and 0 <= q_bep1 <= self.q_max:
            special_pts.append(round(q_bep1, 1))
        if q_bep2 and 0 <= q_bep2 <= self.q_max:
            special_pts.append(round(q_bep2, 1))

        all_q = sorted(list(set(q_steps + special_pts)))

        self.table_data_rows = []
        for q in all_q:
            r = p * q
            cost = a * (q ** 2) + b * q + c
            profit = r - cost
            ac = (cost / q) if q > 0 else 0
            mr = p
            mc = 2.0 * a * q + b
            p_prime = -2.0 * a * q + (p - b)

            tag = "normal"
            if abs(q - q_opt) < 0.2:
                status = "Optimum Max"
                tag = "optimal"
            elif (q_bep1 and abs(q - q_bep1) < 0.2) or (q_bep2 and abs(q - q_bep2) < 0.2):
                status = "Titik Impas (BEP)"
                tag = "bep"
            elif profit > 0:
                status = "Laba"
                tag = "profit"
            else:
                status = "Rugi"
                tag = "loss"

            row_val = (
                f"{q:g}",
                f"Rp {r:,.0f}".replace(",", "."),
                f"Rp {cost:,.0f}".replace(",", "."),
                f"Rp {profit:,.0f}".replace(",", "."),
                f"Rp {ac:,.0f}".replace(",", "."),
                f"Rp {mr:,.0f}".replace(",", "."),
                f"Rp {mc:,.0f}".replace(",", "."),
                f"Rp {p_prime:,.0f}".replace(",", "."),
                status
            )
            self.table_data_rows.append({
                "Porsi (q)": q,
                "Pendapatan R(q)": r,
                "Biaya Total C(q)": cost,
                "Keuntungan P(q)": profit,
                "Biaya Rata-Rata": ac,
                "MR": mr,
                "MC": mc,
                "Turunan Pertama P'(q)": p_prime,
                "Status": status
            })
            self.tree.insert("", tk.END, values=row_val, tags=(tag,))

    def _export_table_csv(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV File", "*.csv"), ("Excel Spreadsheet", "*.xlsx"), ("All Files", "*.*")],
                title="Simpan Data Simulasi Kalkulus UMKM"
            )
            if file_path:
                df = pd.DataFrame(self.table_data_rows)
                if file_path.endswith(".xlsx"):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False)
                messagebox.showinfo("Berhasil", f"Data berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Gagal Ekspor", f"Terjadi kesalahan saat menyimpan file: {str(e)}")

    def _save_graph_image(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF Document", "*.pdf")],
                title="Simpan Grafik Simulasi"
            )
            if file_path:
                self.fig.savefig(file_path, dpi=300, bbox_inches="tight")
                messagebox.showinfo("Berhasil", f"Grafik berhasil disimpan ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Gagal Simpan", f"Terjadi kesalahan: {str(e)}")

    def _redraw_graph(self):
        self.fig.clear()
        self.hover_items = {}

        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg_color = "#18181b" if is_dark else "#ffffff"
        fig_bg = "#18181b" if is_dark else "#f8f9fa"
        text_color = "#f3f4f6" if is_dark else "#111827"
        grid_color = "#27272a" if is_dark else "#e5e7eb"
        spine_color = "#3f3f46" if is_dark else "#d1d5db"
        box_bg = "#242427" if is_dark else "#ffffff"

        self.fig.patch.set_facecolor(fig_bg)

        q_arr = np.linspace(0, self.q_max, 500)
        p = self.p
        c = self.c
        b = self.b
        a = self.a

        r_arr = p * q_arr
        c_arr = a * (q_arr ** 2) + b * q_arr + c
        profit_arr = r_arr - c_arr
        mr_arr = np.full_like(q_arr, p)
        mc_arr = 2.0 * a * q_arr + b

        res = self.calc_results
        q_opt = res["q_opt"]
        p_opt = res["p_opt"]
        r_opt = res["r_opt"]
        c_opt = res["c_opt"]
        q_bep1 = res["q_bep1"]
        q_bep2 = res["q_bep2"]

        slider_q = self.slider_q
        slider_p = -a * (slider_q**2) + (p - b)*slider_q - c

        mode = self.graph_mode.get()

        def style_axis(ax, title, xlabel, ylabel):
            ax.set_facecolor(bg_color)
            ax.set_title(title, fontsize=12, fontweight="bold", color=text_color, pad=10)
            ax.set_xlabel(xlabel, fontsize=10, color=text_color)
            ax.set_ylabel(ylabel, fontsize=10, color=text_color)
            ax.grid(True, linestyle="--", alpha=0.6, color=grid_color)
            ax.tick_params(colors=text_color, labelsize=9)
            for spine in ax.spines.values():
                spine.set_color(spine_color)

        def create_hover_elements(ax, plot_type):
            dot, = ax.plot([], [], "o", color="#3b82f6", markersize=8, zorder=16, visible=False)
            dot2, = ax.plot([], [], "o", color="#ef4444", markersize=8, zorder=16, visible=False)
            gap_line, = ax.plot([], [], "-", color="#10b981", linewidth=2.5, alpha=0.85, zorder=15, visible=False)
            vline = ax.axvline(0, linestyle=":", color="#3b82f6", alpha=0.7, zorder=14, visible=False)
            hline = ax.axhline(0, linestyle=":", color="#3b82f6", alpha=0.5, zorder=14, visible=False)
            annot = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(16, 16),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.55", facecolor=box_bg, edgecolor="#3b82f6", linewidth=1.5, alpha=0.96),
                color=text_color,
                fontsize=8.5,
                fontfamily="Consolas",
                zorder=20,
                visible=False
            )
            self.hover_items[ax] = {
                "dot": dot,
                "dot2": dot2,
                "gap_line": gap_line,
                "vline": vline,
                "hline": hline,
                "annot": annot,
                "type": plot_type
            }

        if mode == "Kurva Keuntungan P(q)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, f"Fungsi Keuntungan Objektif: f(q) = -{a}q² + {p-b:,.0f}q - {c:,.0f}",
                       "Jumlah Porsi Ketoprak per Hari (q)", "Nilai Fungsi Keuntungan f(q) (Rp)")

            ax.plot(q_arr, profit_arr, color="#10b981", linewidth=2.5, label="Fungsi Keuntungan f(q) = R(q) - C(q)")
            ax.axhline(0, color="#ef4444" if not is_dark else "#f87171", linestyle=":", linewidth=1.5, label="Garis Impas (f(q) = 0)")

            ax.fill_between(q_arr, profit_arr, 0, where=(profit_arr >= 0), color="#10b981", alpha=0.15, label="Zona Untung (f(q) >= 0)")
            ax.fill_between(q_arr, profit_arr, 0, where=(profit_arr < 0), color="#ef4444", alpha=0.15, label="Zona Rugi (f(q) < 0)")

            if 0 <= q_opt <= self.q_max:
                ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, alpha=0.8)
                ax.scatter([q_opt], [p_opt], color="#f59e0b", s=90, zorder=5, label=f"Titik Kritis qc: ({q_opt:.1f} porsi, f(qc)=Rp {p_opt:,.0f})")
                ax.annotate(
                    f"TITIK KRITIS (NILAI MAKSIMUM):\nqc = {q_opt:.1f} porsi | f'(qc) = 0\nf(qc) = Rp {p_opt:,.0f} (Maks Global)",
                    xy=(q_opt, p_opt),
                    xytext=(q_opt + 6, p_opt * 0.85),
                    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9, fontweight="bold", color=text_color,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#f59e0b", alpha=0.9)
                )

            ax.scatter([0], [-c], color="#ef4444", s=70, zorder=5, label=f"Nilai Min: (0, -Rp {c:,.0f})")
            ax.annotate(f"NILAI MINIMUM:\nf(0) = -Rp {c:,.0f}", xy=(0, -c), xytext=(3, -c * 0.80),
                        fontsize=8, color="#ef4444", fontweight="bold")

            if q_bep1 and 0 <= q_bep1 <= self.q_max:
                ax.scatter([q_bep1], [0], color="#60a5fa", s=60, zorder=5)
                ax.annotate(f"BEP 1: {q_bep1:.1f}\nf(q)=0", xy=(q_bep1, 0), xytext=(q_bep1 - 14, p_opt * 0.15),
                            fontsize=8, color="#60a5fa", fontweight="bold")
            if q_bep2 and 0 <= q_bep2 <= self.q_max:
                ax.scatter([q_bep2], [0], color="#60a5fa", s=60, zorder=5)
                ax.annotate(f"BEP 2: {q_bep2:.1f}\nf(q)=0", xy=(q_bep2, 0), xytext=(q_bep2 - 12, p_opt * 0.15),
                            fontsize=8, color="#60a5fa", fontweight="bold")

            ax.scatter([slider_q], [slider_p], color="#ec4899", s=70, zorder=6)
            ax.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1.2, alpha=0.7)

            ax.legend(loc="upper right", framealpha=0.85, facecolor=bg_color, labelcolor=text_color, fontsize=8)
            create_hover_elements(ax, "profit")

        elif mode == "Pendapatan R(q) vs Biaya C(q)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, "Perbandingan Pendapatan Total R(q) vs Total Biaya C(q)",
                       "Jumlah Porsi Ketoprak per Hari (q)", "Rupiah (Rp)")

            ax.plot(q_arr, r_arr, color="#3b82f6", linewidth=2.5, label=f"Pendapatan R(q) = {p:,.0f}q")
            ax.plot(q_arr, c_arr, color="#ef4444", linewidth=2.5, label=f"Biaya Total C(q) = {a}q² + {b:,.0f}q + {c:,.0f}")

            if 0 <= q_opt <= self.q_max:
                ax.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linestyle="-", linewidth=3,
                        label=f"Gap Keuntungan Max: Rp {p_opt:,.0f}")
                ax.scatter([q_opt, q_opt], [c_opt, r_opt], color="#10b981", s=60, zorder=5)
                ax.annotate(
                    f"JARAK MAKSIMAL (R - C):\nq* = {q_opt:.1f} porsi\nLaba = Rp {p_opt:,.0f}",
                    xy=(q_opt, (r_opt + c_opt) / 2),
                    xytext=(q_opt + 8, (r_opt + c_opt) / 2),
                    arrowprops=dict(facecolor="#10b981", shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9, fontweight="bold", color=text_color,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#10b981", alpha=0.9)
                )

            slider_r = p * slider_q
            slider_c = a * (slider_q**2) + b*slider_q + c
            ax.scatter([slider_q], [slider_r], color="#3b82f6", s=60, zorder=6)
            ax.scatter([slider_q], [slider_c], color="#ef4444", s=60, zorder=6)
            ax.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1.2, alpha=0.7)

            ax.legend(loc="upper left", framealpha=0.85, facecolor=bg_color, labelcolor=text_color, fontsize=8)
            create_hover_elements(ax, "rev_cost")

        elif mode == "Pendekatan Marjinal (MR vs MC)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, f"Optimasi Marjinal: Pendapatan Marjinal (MR) vs Biaya Marjinal (MC)",
                       "Jumlah Porsi Ketoprak per Hari (q)", "Rupiah per Porsi (Rp/porsi)")

            ax.plot(q_arr, mr_arr, color="#3b82f6", linewidth=2.5, label=f"Marginal Revenue: MR(q) = R'(q) = Rp {p:,.0f}")
            ax.plot(q_arr, mc_arr, color="#ef4444", linewidth=2.5, label=f"Marginal Cost: MC(q) = C'(q) = {2*a:.0f}q + {b:,.0f}")

            if 0 <= q_opt <= self.q_max:
                ax.scatter([q_opt], [p], color="#f59e0b", s=90, zorder=5, label=f"Titik MR = MC di q = {q_opt:.1f}")
                ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, alpha=0.8)
                ax.annotate(
                    f"KONDISI OPTIMUM (MR = MC):\nq* = {q_opt:.1f} porsi\nTarif Marjinal = Rp {p:,.0f}",
                    xy=(q_opt, p),
                    xytext=(q_opt + 6, p * 1.15),
                    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9, fontweight="bold", color=text_color,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#f59e0b", alpha=0.9)
                )

            ax.fill_between(q_arr, mr_arr, mc_arr, where=(q_arr <= q_opt), color="#10b981", alpha=0.15, label="MR > MC (Keuntungan Bertambah)")
            ax.fill_between(q_arr, mr_arr, mc_arr, where=(q_arr > q_opt), color="#ef4444", alpha=0.15, label="MR < MC (Keuntungan Berkurang)")

            ax.legend(loc="upper right", framealpha=0.85, facecolor=bg_color, labelcolor=text_color, fontsize=8)
            create_hover_elements(ax, "marginal")

        elif mode == "Multi-Grafik (3-in-1 Dashboard)":
            gs = self.fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25)
            ax1 = self.fig.add_subplot(gs[0, :])
            ax2 = self.fig.add_subplot(gs[1, 0])
            ax3 = self.fig.add_subplot(gs[1, 1])

            style_axis(ax1, "Kurva Keuntungan P(q)", "Porsi (q)", "Keuntungan (Rp)")
            ax1.plot(q_arr, profit_arr, color="#10b981", linewidth=2)
            ax1.axhline(0, color="#ef4444", linestyle=":", linewidth=1)
            if 0 <= q_opt <= self.q_max:
                ax1.scatter([q_opt], [p_opt], color="#f59e0b", s=60, zorder=5)
                ax1.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1)
            ax1.scatter([slider_q], [slider_p], color="#ec4899", s=50, zorder=6)
            create_hover_elements(ax1, "profit")

            style_axis(ax2, "Pendapatan R(q) vs Biaya C(q)", "Porsi (q)", "Rupiah (Rp)")
            ax2.plot(q_arr, r_arr, color="#3b82f6", linewidth=2, label="R(q)")
            ax2.plot(q_arr, c_arr, color="#ef4444", linewidth=2, label="C(q)")
            if 0 <= q_opt <= self.q_max:
                ax2.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linewidth=2)
            ax2.legend(loc="upper left", fontsize=7, facecolor=bg_color, labelcolor=text_color)
            create_hover_elements(ax2, "rev_cost")

            style_axis(ax3, "Marjinal MR vs MC", "Porsi (q)", "Rp/porsi")
            ax3.plot(q_arr, mr_arr, color="#3b82f6", linewidth=2, label="MR")
            ax3.plot(q_arr, mc_arr, color="#ef4444", linewidth=2, label="MC")
            if 0 <= q_opt <= self.q_max:
                ax3.scatter([q_opt], [p], color="#f59e0b", s=50, zorder=5)
            ax3.legend(loc="upper right", fontsize=7, facecolor=bg_color, labelcolor=text_color)
            create_hover_elements(ax3, "marginal")

        if mode == "Multi-Grafik (3-in-1 Dashboard)":
            self.fig.subplots_adjust(top=0.92, bottom=0.10, left=0.08, right=0.95, hspace=0.38, wspace=0.25)
        else:
            self.fig.tight_layout()
        self.canvas.draw()

    def _on_plot_hover(self, event):
        if not event.inaxes or event.inaxes not in self.hover_items or event.xdata is None:
            self._hide_hover_elements()
            return

        active_ax = event.inaxes
        items = self.hover_items[active_ax]
        q_raw = float(event.xdata)
        q = max(0.0, min(float(self.q_max), q_raw))

        if getattr(self, "_last_hover_q", None) is not None and abs(q - self._last_hover_q) < 0.2 and getattr(self, "_last_hover_ax", None) == active_ax:
            return
        self._last_hover_q = q
        self._last_hover_ax = active_ax

        p = self.p
        c = self.c
        b = self.b
        a = self.a

        res = self.calc_results
        q_opt = res["q_opt"]
        q_bep1 = res["q_bep1"]
        q_bep2 = res["q_bep2"]
        slider_q = self.slider_q

        snap_rad = max(2.0, self.q_max * 0.025)

        is_near_zero = abs(q - 0) <= snap_rad
        is_near_opt = abs(q - q_opt) <= snap_rad
        is_near_bep1 = q_bep1 is not None and abs(q - q_bep1) <= snap_rad
        is_near_bep2 = q_bep2 is not None and abs(q - q_bep2) <= snap_rad
        is_near_slider = abs(q - slider_q) <= (snap_rad * 0.8)

        if is_near_opt:
            q = q_opt
            label_tag = "TITIK KRITIS (NILAI MAKSIMUM MUTLAK)"
            accent_col = "#f59e0b"
        elif is_near_zero:
            q = 0.0
            label_tag = "TITIK UJUNG DOMAIN q=0 (NILAI MINIMUM MUTLAK)"
            accent_col = "#ef4444"
        elif is_near_bep1:
            q = q_bep1
            label_tag = "TITIK IMPAS BAWAH (BEP 1: f(q) = 0)"
            accent_col = "#60a5fa"
        elif is_near_bep2:
            q = q_bep2
            label_tag = "TITIK IMPAS ATAS (BEP 2: f(q) = 0)"
            accent_col = "#60a5fa"
        elif is_near_slider:
            q = slider_q
            label_tag = "TITIK PORSI SIMULASI AKTIF"
            accent_col = "#ec4899"
        else:
            label_tag = "TITIK PENELUSURAN KURVA f(q)"
            accent_col = "#3b82f6"

        r = p * q
        cost = a * (q ** 2) + b * q + c
        profit = r - cost
        p_prime = -2.0 * a * q + (p - b)
        ac = (cost / q) if q > 0 else 0
        mr = p
        mc = 2.0 * a * q + b

        dot = items["dot"]
        dot2 = items["dot2"]
        gap_line = items["gap_line"]
        vline = items["vline"]
        hline = items["hline"]
        annot = items["annot"]

        plot_type = items["type"]
        if plot_type == "profit":
            target_y = profit
            dot.set_data([q], [target_y])
            dot.set_color(accent_col)
            dot.set_visible(True)
            dot2.set_visible(False)
            gap_line.set_visible(False)

            vline.set_xdata([q, q])
            vline.set_color(accent_col)
            vline.set_visible(True)

            hline.set_ydata([target_y, target_y])
            hline.set_color(accent_col)
            hline.set_visible(True)

            if is_near_opt:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Titik Kritis qc: {q:.1f} porsi/hari (f'(qc) = 0)\n"
                    f"Nilai Maksimum f(qc): Rp {profit:,.0f}\n"
                    f"Fungsi Pendapatan R(qc): Rp {r:,.0f}\n"
                    f"Fungsi Biaya C(qc): Rp {cost:,.0f}\n"
                    f"Biaya Rata-Rata AC: Rp {ac:,.0f}/porsi\n"
                    f"Turunan Pertama f'(qc): Rp 0/porsi (Kondisi Stasioner)\n"
                    f"Turunan Kedua f''(qc): {-2.0*a:.0f} < 0 (Maks Mutlak Global)\n"
                    f"Nilai Minimum Global: f(0) = -Rp {c:,.0f}\n"
                    f"Status: Puncak Tertinggi Nilai Maksimum Global"
                ).replace(",", ".")
            elif is_near_zero:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (q): 0,0 porsi/hari\n"
                    f"Nilai Minimum f(0): -Rp {c:,.0f} (Defisit Biaya Tetap)\n"
                    f"Fungsi Pendapatan R(0): Rp 0\n"
                    f"Biaya Total C(0): Rp {c:,.0f} (Fixed Cost)\n"
                    f"Turunan Pertama f'(0): +Rp {p - b:,.0f}/porsi (f' > 0)\n"
                    f"Status: Nilai Minimum Mutlak pada Domain [0, {self.q_max}]"
                ).replace(",", ".")
            elif is_near_bep1 or is_near_bep2:
                bep_name = "BEP 1 (Bawah)" if is_near_bep1 else "BEP 2 (Atas)"
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Impas ({bep_name}): {q:.1f} porsi/hari\n"
                    f"Nilai Fungsi f(q): Rp 0 (Pulang Pokok)\n"
                    f"Pendapatan = Biaya: Rp {r:,.0f}\n"
                    f"Turunan Pertama f'(q): Rp {p_prime:,.0f}/porsi\n"
                    f"Status: Ambang Batas Wilayah Keuntungan (f(q) = 0)"
                ).replace(",", ".")
            elif is_near_slider:
                diff_s = q - q_opt
                s_note = f"+{diff_s:.1f} porsi dari opt" if diff_s > 0 else (f"{diff_s:.1f} porsi dari opt" if diff_s < 0 else "Tepat di optimum")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Terpilih: {q:.1f} porsi/hari ({s_note})\n"
                    f"Fungsi Keuntungan f(q): Rp {profit:,.0f}\n"
                    f"Pendapatan Total R: Rp {r:,.0f}\n"
                    f"Biaya Total C: Rp {cost:,.0f}\n"
                    f"Turunan Pertama f'(q): Rp {p_prime:,.0f}/porsi\n"
                    f"Status: Posisi Slider Simulasi Interaktif"
                ).replace(",", ".")
            else:
                st_txt = "Zona Laba Positif (f(q) > 0)" if profit > 0 else ("Titik Impas (f(q) = 0)" if abs(profit) < 1 else "Zona Rugi Defisit (f(q) < 0)")
                rec_txt = "Tambah porsi (f'(q) > 0)" if p_prime > 50 else ("Kurangi porsi (f'(q) < 0)" if p_prime < -50 else "Puncak laba (f'(q) = 0)")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (q): {q:.1f} porsi/hari\n"
                    f"Fungsi Keuntungan f(q): Rp {profit:,.0f}\n"
                    f"Pendapatan Total R(q): Rp {r:,.0f}\n"
                    f"Biaya Total C(q): Rp {cost:,.0f}\n"
                    f"Biaya Rata-Rata AC: Rp {ac:,.0f}/porsi\n"
                    f"Turunan Pertama f'(q): Rp {p_prime:,.0f}/porsi\n"
                    f"Turunan Kedua f''(q): {-2.0*a:.0f} (Konkaf)\n"
                    f"Titik Kritis qc: {q_opt:.1f} | Nilai Maks: Rp {p_opt:,.0f}\n"
                    f"Status: {st_txt} | {rec_txt}"
                ).replace(",", ".")

        elif plot_type == "rev_cost":
            target_y = r
            gap = r - cost

            dot.set_data([q], [r])
            dot.set_color("#3b82f6")
            dot.set_visible(True)

            dot2.set_data([q], [cost])
            dot2.set_color("#ef4444")
            dot2.set_visible(True)

            gap_col = "#10b981" if gap >= 0 else "#ef4444"
            gap_line.set_data([q, q], [min(r, cost), max(r, cost)])
            gap_line.set_color(gap_col)
            gap_line.set_visible(True)

            vline.set_xdata([q, q])
            vline.set_color(accent_col)
            vline.set_visible(True)

            hline.set_visible(False)

            if is_near_opt:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Optimum (q*): {q:.1f} porsi/hari\n"
                    f"Pendapatan Total R(q*): Rp {r:,.0f}\n"
                    f"Biaya Total C(q*): Rp {cost:,.0f}\n"
                    f"Gap Laba Maksimum (R - C): Rp {gap:,.0f}\n"
                    f"Kemiringan Kurva: R' = C' = Rp {p:,.0f}\n"
                    f"Biaya Tetap FC: Rp {c:,.0f}\n"
                    f"Biaya Variabel VC: Rp {a*(q**2) + b*q:,.0f}\n"
                    f"Status: Celah Vertikal R(q) - C(q) Terbesar"
                ).replace(",", ".")
            elif is_near_bep1 or is_near_bep2:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Impas (BEP): {q:.1f} porsi/hari\n"
                    f"Pendapatan = Biaya: Rp {r:,.0f}\n"
                    f"Gap Keuntungan: Rp 0 (Impas)\n"
                    f"Status: Titik Perpotongan Dua Kurva"
                ).replace(",", ".")
            elif is_near_slider:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Terpilih: {q:.1f} porsi/hari\n"
                    f"Pendapatan Total R: Rp {r:,.0f}\n"
                    f"Biaya Total C: Rp {cost:,.0f}\n"
                    f"Celah Keuntungan: Rp {gap:,.0f}\n"
                    f"Status: Posisi Slider Pada R(q) dan C(q)"
                ).replace(",", ".")
            else:
                st_rc = "Laba (R > C)" if gap > 0 else ("Impas (R = C)" if abs(gap) < 1 else "Rugi (C > R)")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (q): {q:.1f} porsi/hari\n"
                    f"Pendapatan R(q): Rp {r:,.0f}\n"
                    f"Biaya Total C(q): Rp {cost:,.0f}\n"
                    f"Celah Keuntungan: Rp {gap:,.0f}\n"
                    f"Biaya Tetap FC: Rp {c:,.0f}\n"
                    f"Biaya Variabel VC: Rp {a*(q**2) + b*q:,.0f}\n"
                    f"Status: {st_rc}"
                ).replace(",", ".")

        elif plot_type == "marginal":
            target_y = mc
            diff = mr - mc

            dot.set_data([q], [mr])
            dot.set_color("#3b82f6")
            dot.set_visible(True)

            dot2.set_data([q], [mc])
            dot2.set_color("#ef4444")
            dot2.set_visible(True)

            diff_col = "#10b981" if diff >= 0 else "#ef4444"
            gap_line.set_data([q, q], [min(mr, mc), max(mr, mc)])
            gap_line.set_color(diff_col)
            gap_line.set_visible(True)

            vline.set_xdata([q, q])
            vline.set_color(accent_col)
            vline.set_visible(True)

            hline.set_visible(False)

            if is_near_opt:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Optimum (q*): {q:.1f} porsi/hari\n"
                    f"Marginal Revenue MR: Rp {mr:,.0f}/porsi\n"
                    f"Marginal Cost MC: Rp {mc:,.0f}/porsi\n"
                    f"Laba Marjinal P'(q*): Rp 0/porsi\n"
                    f"Kondisi Stasioner: MR = MC Tercapai\n"
                    f"Status: Titik Balik Keuntungan Maksimal"
                ).replace(",", ".")
            elif is_near_slider:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Terpilih: {q:.1f} porsi/hari\n"
                    f"Marginal Revenue MR: Rp {mr:,.0f}/porsi\n"
                    f"Marginal Cost MC: Rp {mc:,.0f}/porsi\n"
                    f"Selisih MR - MC: Rp {diff:,.0f}/porsi\n"
                    f"Status: Evaluasi Marjinal Slider"
                ).replace(",", ".")
            else:
                if diff > 50:
                    st_mc = "MR > MC: Tambahan porsi menambah total laba"
                elif diff < -50:
                    st_mc = "MR < MC: Tambahan porsi mengurangi total laba"
                else:
                    st_mc = "MR = MC: Kondisi laba optimum"
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (q): {q:.1f} porsi/hari\n"
                    f"Marginal Revenue MR: Rp {mr:,.0f}/porsi\n"
                    f"Marginal Cost MC: Rp {mc:,.0f}/porsi\n"
                    f"Laju Laba P'(q): Rp {diff:,.0f}/porsi\n"
                    f"Interpretasi: {st_mc}"
                ).replace(",", ".")

        annot.xy = (q, target_y)
        annot.set_text(text_info)

        x_min, x_max = active_ax.get_xlim()
        y_min, y_max = active_ax.get_ylim()
        x_frac = (q - x_min) / max(1e-5, (x_max - x_min))
        y_frac = (target_y - y_min) / max(1e-5, (y_max - y_min))

        offset_x = -245 if x_frac > 0.52 else 18
        offset_y = -140 if y_frac > 0.50 else 18
        annot.set_position((offset_x, offset_y))

        annot.get_bbox_patch().set_edgecolor(accent_col)
        annot.set_visible(True)

        for other_ax, other_items in self.hover_items.items():
            if other_ax != active_ax:
                other_items["dot"].set_visible(False)
                other_items["dot2"].set_visible(False)
                other_items["gap_line"].set_visible(False)
                other_items["vline"].set_visible(False)
                other_items["hline"].set_visible(False)
                other_items["annot"].set_visible(False)

        self.canvas.draw_idle()

    def _on_plot_leave(self, event):
        self._hide_hover_elements()

    def _hide_hover_elements(self):
        self._last_hover_q = None
        self._last_hover_ax = None
        changed = False
        for items in self.hover_items.values():
            if items["dot"].get_visible():
                items["dot"].set_visible(False)
                items["dot2"].set_visible(False)
                items["gap_line"].set_visible(False)
                items["vline"].set_visible(False)
                items["hline"].set_visible(False)
                items["annot"].set_visible(False)
                changed = True
        if changed:
            self.canvas.draw_idle()


if __name__ == "__main__":
    app = KalkulusUMKMApp()
    app.mainloop()

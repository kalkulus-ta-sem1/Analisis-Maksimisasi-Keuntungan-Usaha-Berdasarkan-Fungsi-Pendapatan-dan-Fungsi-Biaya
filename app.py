import sys
import os
import math
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

from tasik_market_data import (
    KATALOG_KOMODITAS_TASIK,
    KONDISI_PASAR_CONFIG,
    WILAYAH_CONFIG,
    hitung_estimasi_umkm,
)
from kalkulus_integral import (
    daftar_soal_pdf,
    evaluasi_soal_pdf,
    hitung_integral_umkm,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class KalkulusUMKMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kalkulus Optimasi UMKM Ketoprak - Proyek Akhir Kalkulus Dasar (UNSIL)")
        self.geometry("1300x820")
        self.minsize(1050, 700)

        self.presets = {
            "UMKM Ketoprak (Harian Tasikmalaya)": {
                "p": 15000.0,
                "c": 33000.0,
                "b": 6700.0,
                "a": 60.0,
                "q_max": 140
            },
            "UMKM Warung Nasi Goreng": {
                "p": 18000.0,
                "c": 48000.0,
                "b": 8200.0,
                "a": 50.0,
                "q_max": 200
            },
            "UMKM Kopi Susu Kekinian": {
                "p": 22000.0,
                "c": 68000.0,
                "b": 6800.0,
                "a": 75.0,
                "q_max": 205
            },
            "UMKM Ketoprak (Studi Kasus Laporan UNSIL)": {
                "p": 15000.0,
                "c": 60000.0,
                "b": 8000.0,
                "a": 50.0,
                "q_max": 140,
                "static_report": True
            },
            "Kustom Parameter Sendiri": {
                "p": 15000.0,
                "c": 35000.0,
                "b": 6700.0,
                "a": 60.0,
                "q_max": 140
            }
        }

        self.p = 15000.0
        self.c = 33000.0
        self.b = 6700.0
        self.a = 60.0
        self.q_max = 140
        self.slider_q = 69.0
        self.sidebar_width = 380
        self._syncing_from_p = False
        self._last_p_text = "15000"
        self._price_debounce_id = None
        self._pending_price_autofill = False
        self._manual_override = False
        self.wilayah = "Kota Tasikmalaya (Pasar Cikurubuk)"
        self.kondisi_pasar = "Harga Normal Pasar (Rata-rata)"
        self.auto_tasik_var = tk.BooleanVar(value=True)
        self.tasik_breakdown = hitung_estimasi_umkm(
            self.p,
            "UMKM Ketoprak (Harian Tasikmalaya)",
            self.wilayah,
            self.kondisi_pasar,
        )

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
        self.preset_menu.pack(fill="x", pady=(0, 8))

        wil_lbl = ctk.CTkLabel(self.side_scroll, text="Acuan Harga Daerah:", font=ctk.CTkFont(size=12, weight="bold"))
        wil_lbl.pack(anchor="w", pady=(0, 2))

        self.wilayah_menu = ctk.CTkOptionMenu(
            self.side_scroll,
            values=list(WILAYAH_CONFIG.keys()),
            command=self._on_wilayah_change,
            font=ctk.CTkFont(size=11)
        )
        self.wilayah_menu.set(self.wilayah)
        self.wilayah_menu.pack(fill="x", pady=(0, 8))

        kondisi_lbl = ctk.CTkLabel(self.side_scroll, text="Kondisi Harga Pasar (Naik/Turun):", font=ctk.CTkFont(size=12, weight="bold"))
        kondisi_lbl.pack(anchor="w", pady=(0, 2))

        self.kondisi_menu = ctk.CTkOptionMenu(
            self.side_scroll,
            values=list(KONDISI_PASAR_CONFIG.keys()),
            command=self._on_kondisi_change,
            font=ctk.CTkFont(size=11)
        )
        self.kondisi_menu.set(self.kondisi_pasar)
        self.kondisi_menu.pack(fill="x", pady=(0, 8))

        self.auto_tasik_switch = ctk.CTkSwitch(
            self.side_scroll,
            text="Auto-Isi Modal Harian (Non-Borongan)",
            variable=self.auto_tasik_var,
            command=self._on_toggle_auto_tasik,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.auto_tasik_switch.pack(anchor="w", pady=(0, 10))

        self.entries = {}
        fields = [
            ("p", "Harga Jual (p)", "Rupiah per porsi (ketik harga, modal harian terisi)", "15000"),
            ("c", "Biaya Tetap Harian (c / FC)", "Sewa, pemakaian LPG, listrik & alat per hari", "33000"),
            ("b", "Modal Bahan / Porsi (b)", "Belanja harian non-borongan pasar Tasik (Rp/porsi)", "6700"),
            ("a", "Koef. Kuadrat (a)", "Disekonomi biaya (Rp/porsi²)", "60"),
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

        self.entries["p"].bind("<KeyRelease>", self._schedule_price_change)
        self.entries["p"].bind("<FocusOut>", lambda _e=None: self._on_price_change(immediate=True))
        self.entries["p"].bind("<Return>", lambda _e=None: self._on_price_change(immediate=True))
        for manual_key in ("c", "b", "a", "q_max"):
            self.entries[manual_key].bind("<KeyRelease>", self._on_manual_cost_edit)

        btn_frame = ctk.CTkFrame(self.side_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(6, 10))

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
            command=self._reset_ketoprak_default,
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            height=30,
            font=ctk.CTkFont(size=11)
        )
        reset_btn.pack(fill="x")

        calc_w = max(240, self.sidebar_width - 60)
        self.tasik_info_card = ctk.CTkFrame(
            self.side_scroll,
            fg_color=("gray90", "#18181b"),
            corner_radius=8,
            border_width=1,
            border_color=("gray75", "#334155")
        )
        self.tasik_info_card.pack(fill="x", pady=(0, 6), padx=2)

        self.tasik_segmen_lbl = ctk.CTkLabel(
            self.tasik_info_card,
            text="Basis Pasar: Tasikmalaya (Cikurubuk)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#047857", "#34d399"),
            wraplength=calc_w,
            justify="left"
        )
        self.tasik_segmen_lbl.pack(anchor="w", padx=10, pady=(8, 2))

        self.tasik_summary_lbl = ctk.CTkLabel(
            self.tasik_info_card,
            text="",
            font=ctk.CTkFont(size=10),
            wraplength=calc_w,
            justify="left"
        )
        self.tasik_summary_lbl.pack(anchor="w", padx=10, pady=1)

        self.tasik_note_lbl = ctk.CTkLabel(
            self.tasik_info_card,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray70"),
            wraplength=calc_w,
            justify="left"
        )
        self.tasik_note_lbl.pack(anchor="w", padx=10, pady=(1, 6))

        self.tasik_detail_btn = ctk.CTkButton(
            self.tasik_info_card,
            text="Lihat Rincian Harga Tasik ->",
            command=self._open_tasik_tab,
            height=26,
            fg_color=("#2563eb", "#1d4ed8"),
            hover_color=("#1d4ed8", "#1e40af"),
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.tasik_detail_btn.pack(fill="x", padx=10, pady=(0, 8))

        sep = ctk.CTkFrame(self.side_scroll, height=2, fg_color=("gray70", "#334155"))
        sep.pack(fill="x", pady=12)

        slider_title = ctk.CTkLabel(
            self.side_scroll,
            text="SIMULASI INTERAKTIF PORSI (x)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        slider_title.pack(anchor="w", pady=(0, 4))

        self.slider_val_label = ctk.CTkLabel(
            self.side_scroll,
            text=f"Jumlah Porsi Terpilih: 69 porsi/hari",
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
        self.q_slider.set(69)
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
            text="Pendapatan R(x): Rp 1.035.000",
            font=ctk.CTkFont(size=11),
            wraplength=calc_w,
            justify="left"
        )
        self.live_rev_lbl.pack(anchor="w", padx=10, pady=1)

        self.live_cost_lbl = ctk.CTkLabel(
            self.live_card,
            text="Biaya Total C(x): Rp 780.960",
            font=ctk.CTkFont(size=11),
            wraplength=calc_w,
            justify="left"
        )
        self.live_cost_lbl.pack(anchor="w", padx=10, pady=1)

        self.live_profit_lbl = ctk.CTkLabel(
            self.live_card,
            text="Fungsi Laba P(x): Rp 254.040",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            wraplength=calc_w,
            justify="left"
        )
        self.live_profit_lbl.pack(anchor="w", padx=10, pady=2)

        self.live_mp_lbl = ctk.CTkLabel(
            self.live_card,
            text="Laju Laba P'(x): Rp 0/porsi",
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
        self.tasik_segmen_lbl.configure(wraplength=calc_w)
        self.tasik_summary_lbl.configure(wraplength=calc_w)
        self.tasik_note_lbl.configure(wraplength=calc_w)

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
        self.tab_kalkulus = self.tabview.add("Rumus Kalkulus (PDF)")
        self.tab_integral = self.tabview.add("Integral (PDF)")
        self.tab_tabel = self.tabview.add("Tabel Simulasi")
        self.tab_tasik = self.tabview.add("Harga Tasik")
        self.tab_laporan = self.tabview.add("Laporan Proyek")

        self._configure_tabview_navbar()

        self._setup_tab_grafik()
        self._setup_tab_kalkulus()
        self._setup_tab_integral()
        self._setup_tab_tabel()
        self._setup_tab_tasik()
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

        self.card_q_opt = self._make_metric_card(self.summary_bar, 0, "Titik Kritis (x*)", "69,2 porsi", "Syarat Stasioner P'(x) = 0", "#3b82f6")
        self.card_profit_max = self._make_metric_card(self.summary_bar, 1, "Nilai Maksimum P(x*)", "Rp 254.042", "Laba harian puncak mutlak", "#10b981")
        self.card_bep = self._make_metric_card(self.summary_bar, 2, "Nilai Minimum & BEP", "-Rp 33.000", "Batas rentang laba P(x) >= 0", "#f59e0b")
        self.card_test1 = self._make_metric_card(self.summary_bar, 3, "Uji Turunan Pertama", "P'(x): (+) -> 0 -> (-)", "Kiri naik, kanan turun (Maks)", "#8b5cf6")

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
                "Kurva Keuntungan P(x)",
                "Pendapatan R(x) vs Biaya C(x)",
                "Pendekatan Marjinal (MR vs MC)",
                "Multi-Grafik (3-in-1 Dashboard)"
            ],
            command=self._on_graph_mode_change
        )
        self.graph_mode.set("Kurva Keuntungan P(x)")
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

    def _setup_tab_integral(self):
        self.tab_integral.grid_rowconfigure(1, weight=1)
        self.tab_integral.grid_columnconfigure(0, weight=1)

        ctrl_bar = ctk.CTkFrame(self.tab_integral, fg_color="transparent")
        ctrl_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 6))
        ctrl_bar.grid_columnconfigure(0, weight=1)

        self.int_submode = ctk.CTkSegmentedButton(
            ctrl_bar,
            values=[
                "Penerapan Integral di UMKM (Rumus PDF)",
                "Kalkulator 10 Soal Rumus PDF (A.1 - B.5)",
            ],
            command=self._on_integral_submode_change,
        )
        self.int_submode.set("Penerapan Integral di UMKM (Rumus PDF)")
        self.int_submode.grid(row=0, column=0, sticky="ew", padx=4)

        self.int_container = ctk.CTkFrame(self.tab_integral, fg_color="transparent")
        self.int_container.grid(row=1, column=0, sticky="nsew", padx=4, pady=2)
        self.int_container.grid_rowconfigure(0, weight=1)
        self.int_container.grid_columnconfigure(0, weight=1)

        # Panel 1: Penerapan Integral di UMKM mengikuti rumus PDF
        self.int_umkm_scroll = ctk.CTkScrollableFrame(self.int_container)
        self.int_umkm_scroll.grid(row=0, column=0, sticky="nsew")
        self.int_umkm_scroll.grid_columnconfigure(0, weight=1)

        umkm_plot_box = ctk.CTkFrame(self.int_umkm_scroll, fg_color=("gray95", "#18181b"), corner_radius=8)
        umkm_plot_box.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 8))
        umkm_plot_box.grid_columnconfigure(0, weight=1)

        self.int_umkm_fig = Figure(figsize=(8.6, 5.2), dpi=96)
        self.int_umkm_canvas = FigureCanvasTkAgg(self.int_umkm_fig, master=umkm_plot_box)
        self.int_umkm_canvas.get_tk_widget().grid(row=0, column=0, sticky="ew")

        self.int_umkm_text_lbl = ctk.CTkLabel(
            self.int_umkm_scroll,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            justify="left",
            anchor="w",
        )
        self.int_umkm_text_lbl.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 14))

        # Panel 2: Kalkulator & Verifikator 10 Soal Rumus PDF (A.1-A.5 & B.1-B.5)
        self.int_pdf_frame = ctk.CTkScrollableFrame(self.int_container)
        self.int_pdf_frame.grid(row=0, column=0, sticky="nsew")
        self.int_pdf_frame.grid_columnconfigure(0, weight=1)

        pdf_top = ctk.CTkFrame(self.int_pdf_frame, fg_color=("gray90", "#1e1e24"), corner_radius=8)
        pdf_top.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 8))
        pdf_top.grid_columnconfigure(1, weight=1)

        soal_lbl = ctk.CTkLabel(pdf_top, text="Pilih Rumus PDF:", font=ctk.CTkFont(size=12, weight="bold"))
        soal_lbl.grid(row=0, column=0, padx=(10, 6), pady=8, sticky="w")

        self._pdf_soal_list = daftar_soal_pdf()
        self._pdf_judul_to_kode = {it["judul"]: it["kode"] for it in self._pdf_soal_list}
        self.pdf_soal_menu = ctk.CTkOptionMenu(
            pdf_top,
            values=[it["judul"] for it in self._pdf_soal_list],
            command=lambda _v: self._update_pdf_solver(),
            font=ctk.CTkFont(size=11),
        )
        self.pdf_soal_menu.set(self._pdf_soal_list[8]["judul"])  # Default B.4 (nilai mutlak kuadrat)
        self.pdf_soal_menu.grid(row=0, column=1, padx=6, pady=8, sticky="ew")

        x_lbl = ctk.CTkLabel(pdf_top, text="x uji:", font=ctk.CTkFont(size=11, weight="bold"))
        x_lbl.grid(row=0, column=2, padx=(6, 4), pady=8)

        self.pdf_x_entry = ctk.CTkEntry(pdf_top, width=65, height=28, font=ctk.CTkFont(size=11))
        self.pdf_x_entry.insert(0, "2")
        self.pdf_x_entry.grid(row=0, column=3, padx=4, pady=8)
        self.pdf_x_entry.bind("<Return>", lambda _e=None: self._update_pdf_solver())

        ver_btn = ctk.CTkButton(
            pdf_top,
            text="Verifikasi",
            width=85,
            height=28,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._update_pdf_solver,
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        ver_btn.grid(row=0, column=4, padx=(4, 10), pady=8)

        self.pdf_result_lbl = ctk.CTkLabel(
            self.int_pdf_frame,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            justify="left",
            anchor="w",
        )
        self.pdf_result_lbl.grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 8))

        pdf_plot_box = ctk.CTkFrame(self.int_pdf_frame, fg_color=("gray95", "#18181b"), corner_radius=8)
        pdf_plot_box.grid(row=2, column=0, sticky="ew", padx=6, pady=(2, 10))
        pdf_plot_box.grid_columnconfigure(0, weight=1)

        self.int_pdf_fig = Figure(figsize=(8.4, 3.8), dpi=96)
        self.int_pdf_canvas = FigureCanvasTkAgg(self.int_pdf_fig, master=pdf_plot_box)
        self.int_pdf_canvas.get_tk_widget().grid(row=0, column=0, sticky="ew")

        self._on_integral_submode_change("Penerapan Integral di UMKM (Rumus PDF)")

    def _on_integral_submode_change(self, mode_val):
        if mode_val == "Penerapan Integral di UMKM (Rumus PDF)":
            self.int_pdf_frame.grid_remove()
            self.int_umkm_scroll.grid()
        else:
            self.int_umkm_scroll.grid_remove()
            self.int_pdf_frame.grid()
            self._update_pdf_solver()

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
            ("q", "Porsi (x)", 75, "center"),
            ("R", "Pendapatan R(x)", 125, "e"),
            ("C", "Total Biaya C(x)", 125, "e"),
            ("P", "Keuntungan P(x)", 125, "e"),
            ("AC", "Biaya Rata2 AC(x)", 120, "e"),
            ("MR", "Marginal Rev (MR)", 115, "e"),
            ("MC", "Marginal Cost (MC)", 115, "e"),
            ("P_prime", "Laju Laba P'(x)", 115, "e"),
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

Studi ini memodelkan hubungan antara porsi produksi (x), fungsi pendapatan R(x), fungsi biaya C(x),
dan fungsi keuntungan P(x), baik melalui turunan maupun penerapan integral (substitusi u, nilai mutlak,
pecah polinom ln|x|, integral trigonometri, dan Teorema Dasar Kalkulus I).

------------------------------------------------------------------------------------------------------
2. PEMODELAN MATEMATIKA KALKULUS (CONTOH STUDI KASUS AWAL 15RB)
------------------------------------------------------------------------------------------------------
- Variabel Keputusan : x (jumlah porsi ketoprak diproduksi & terjual per hari, x >= 0)
- Parameter Model     :
    * Harga jual (p)            : Rp 15.000 / porsi
    * Biaya tetap harian (c/FC) : Rp 60.000 (sewa tempat, gas, penyusutan alat gerobak)
    * Biaya variabel dasar (b)  : Rp 8.000 (tahu, lontong, bihun, tauge, kerupuk, bumbu kacang dasar)
    * Koefisien kuadrat (a)     : Rp 50/porsi^2 (faktor disekonomi skala / kenaikan biaya marjinal)

Fungsi yang Terbentuk (via FTC I: C(x) = c + int_0^x MC(t) dt dan P(x) = -c + int_0^x P'(t) dt):
1. Fungsi Pendapatan : R(x) = 15.000 x
2. Fungsi Biaya      : C(x) = 50 x^2 + 8.000 x + 60.000
3. Fungsi Keuntungan : P(x) = R(x) - C(x)
                     : P(x) = -50 x^2 + 7.000 x - 60.000

------------------------------------------------------------------------------------------------------
3. PENERAPAN KONSEP TURUNAN & INTEGRAL PADA FUNGSI P(x)
------------------------------------------------------------------------------------------------------
A. Konsep Turunan Pertama P'(x):
   Laju perubahan sesaat keuntungan terhadap jumlah porsi:
   P'(x) = d/dx [-50 x^2 + 7.000 x - 60.000]
   P'(x) = -100 x + 7.000
   Geometris: P'(x) adalah gradien garis singgung kurva laba P(x).
   Ekonomis : P'(x) adalah Laba Marjinal (Marginal Profit).

B. Konsep Titik Kritis (Critical Point):
   Titik kritis stasioner dicapai saat turunan pertama bernilai nol:
   P'(x) = 0
   -100 x + 7.000 = 0
   100 x = 7.000
   x* = 70 porsi / hari
   Kesimpulan: x* = 70 adalah satu-satunya titik kritis di dalam domain produksi.

C. Konsep Nilai Maksimum dan Nilai Minimum (Uji Turunan Pertama):
   1. Uji Turunan Pertama P'(x) di sekitar titik kritis x* = 70:
      - Untuk 0 <= x < 70 (titik uji x = 60): P'(60) = -100(60) + 7.000 = +1.000 > 0 (kurva NAIK).
      - Pada titik kritis x* = 70           : P'(70) = 0 (kondisi stasioner).
      - Untuk x > 70 (titik uji x = 80)     : P'(80) = -100(80) + 7.000 = -1.000 < 0 (kurva TURUN).
      Karena tanda P'(x) berubah dari POSITIF (+) ke NEGATIF (-) saat melewati x* = 70,
      berdasarkan Uji Turunan Pertama maka P(70) terbukti merupakan TITIK MAKSIMUM MUTLAK.
   2. Teorema Nilai Ekstrem pada Interval Tertutup [0, 140]:
      - Nilai Maksimum Mutlak : P(70) = Rp 185.000 / hari (pada omzet Rp 1.050.000 dan biaya Rp 865.000).
      - Nilai Minimum Mutlak : P(0) = -Rp 60.000 / hari (beban biaya tetap saat tidak memproduksi)
                               dan P(140) = -Rp 60.000 / hari (disekonomi biaya akibat beban kuadrat).

D. Konsep Aplikasi Turunan & Integral dalam Optimasi Nyata UMKM:
   1. Keseimbangan Ekonomi Marjinal (MR = MC):
      P'(x) = 0  <=>  R'(x) - C'(x) = 0  <=>  MR = MC
      MR(x) = Rp 15.000 / porsi
      MC(x) = 100 x + 8.000
      Pada x* = 70: MC(70) = 100(70) + 8.000 = Rp 15.000 (Keseimbangan tercapai).
   2. Analisis Titik Impas (Break-Even Point / BEP) saat P(x) = 0:
      -50 x^2 + 7.000 x - 60.000 = 0
      Diskriminan D = 7000^2 - 4(50)(60000) = 37.000.000
      x_BEP1 = 9,17 porsi (dibulatkan 10 porsi untuk mulai untung).
      x_BEP2 = 130,83 porsi (dibulatkan 130 porsi batas aman kapasitas).
      Rentang Usaha Menguntungkan: 10 <= x <= 130 porsi per hari.
   3. Penerapan Integral Mengikuti Rumus PDF (A.1-A.5 & B.1-B.5):
      - Integral nilai mutlak linier & kuadrat (int |P'(x)| dx dan int |P(x)| dx)
      - Integral biaya rata-rata AC(x) = (ax^2 + bx + c)/x dengan ln|x|
      - Substitusi u + ubah batas untuk menghitung VC(x*) = (p^2 - b^2)/(4a)
      - Integral trigonometri untuk proyeksi akumulasi laba bulanan 30 hari

------------------------------------------------------------------------------------------------------
4. INTERPRETASI EKONOMI MARJINAL (MICROECONOMICS INSIGHT)
------------------------------------------------------------------------------------------------------
Dalam teori ekonomi manajerial, keuntungan maksimal tercapai ketika Pendapatan Marjinal sama dengan
Biaya Marjinal:
   MR(x) = R'(x) = Rp 15.000
   MC(x) = C'(x) = 100 x + 8.000
   Kondisi MR = MC:
   15.000 = 100 x + 8.000  =>  100 x = 7.000  =>  x* = 70 porsi.

Penjelasan:
- Selama x < 70, MR > MC (tambahan pendapatan lebih besar daripada tambahan biaya). Memperbanyak porsi
  akan MENAMBAH keuntungan total.
- Saat x = 70, MR = MC (keuntungan berada di puncak optimal).
- Saat x > 70, MR < MC (tambahan biaya melebihi pendapatan). Memaksakan menambah porsi justru akan
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

    def _setup_tab_tasik(self):
        self.tab_tasik.grid_rowconfigure(0, weight=1)
        self.tab_tasik.grid_columnconfigure(0, weight=1)

        self.tasik_scroll = ctk.CTkScrollableFrame(self.tab_tasik)
        self.tasik_scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.tasik_scroll.grid_columnconfigure(0, weight=1)

        self.tasik_header_card = ctk.CTkFrame(
            self.tasik_scroll,
            fg_color=("gray90", "#1e1e24"),
            corner_radius=8,
            border_width=1,
            border_color=("gray75", "#334155")
        )
        self.tasik_header_card.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 10))

        header_title = ctk.CTkLabel(
            self.tasik_header_card,
            text="RINCIAN OTOMATIS MODAL & HARGA PASAR INDONESIA (BASIS TASIKMALAYA)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#047857", "#34d399")
        )
        header_title.pack(anchor="w", padx=12, pady=(10, 4))

        self.tasik_detail_lbl = ctk.CTkLabel(
            self.tasik_header_card,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
            wraplength=780
        )
        self.tasik_detail_lbl.pack(fill="x", padx=12, pady=(0, 10))
        self.tasik_header_card.bind(
            "<Configure>",
            lambda e: self.tasik_detail_lbl.configure(wraplength=max(420, e.width - 30))
        )

        # Section 1: Rincian Biaya Variabel (b) & Belanja Harian Non-Borongan
        var_title = ctk.CTkLabel(
            self.tasik_scroll,
            text="1. Rincian Modal Bahan Baku Harian per Porsi (b) & Estimasi Belanja Non-Borongan Hari Ini",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        var_title.grid(row=1, column=0, sticky="w", padx=8, pady=(2, 4))

        var_frame = ctk.CTkFrame(self.tasik_scroll, corner_radius=8)
        var_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 10))
        var_frame.grid_columnconfigure(0, weight=1)

        self.var_tree = ttk.Treeview(
            var_frame,
            columns=("komponen", "takaran", "subtotal", "rentang", "harian"),
            show="headings",
            height=8
        )
        for cid, cname, w, anc in [
            ("komponen", "Komponen Bahan / Kemasan", 205, "w"),
            ("takaran", "Takaran / Porsi", 185, "w"),
            ("subtotal", "Modal / Porsi", 105, "e"),
            ("rentang", "Naik-Turun (/Porsi)", 150, "center"),
            ("harian", "Belanja Harian (q*)", 165, "e"),
        ]:
            self.var_tree.heading(cid, text=cname)
            self.var_tree.column(cid, width=w, anchor=anc)
        var_xscroll = ttk.Scrollbar(var_frame, orient="horizontal", command=self.var_tree.xview)
        self.var_tree.configure(xscrollcommand=var_xscroll.set)
        self.var_tree.grid(row=0, column=0, sticky="ew")
        var_xscroll.grid(row=1, column=0, sticky="ew")
        self.var_tree.tag_configure("total_row", background="#064e3b", foreground="#a7f3d0")

        # Section 2: Rincian Biaya Tetap (c)
        fix_title = ctk.CTkLabel(
            self.tasik_scroll,
            text="2. Rincian Biaya Tetap Operasional per Hari (c / FC - Pemakaian Riil Harian)",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        fix_title.grid(row=3, column=0, sticky="w", padx=8, pady=(2, 4))

        fix_frame = ctk.CTkFrame(self.tasik_scroll, corner_radius=8)
        fix_frame.grid(row=4, column=0, sticky="ew", padx=6, pady=(0, 10))
        fix_frame.grid_columnconfigure(0, weight=1)

        self.fixed_tree = ttk.Treeview(
            fix_frame,
            columns=("komponen", "basis", "subtotal", "rentang", "sumber"),
            show="headings",
            height=7
        )
        for cid, cname, w, anc in [
            ("komponen", "Komponen Operasional Tetap", 200, "w"),
            ("basis", "Pemakaian Riil / Hari", 190, "w"),
            ("subtotal", "Biaya / Hari", 105, "e"),
            ("rentang", "Naik-Turun (/Hari)", 145, "center"),
            ("sumber", "Referensi Tarif Lokal", 185, "w"),
        ]:
            self.fixed_tree.heading(cid, text=cname)
            self.fixed_tree.column(cid, width=w, anchor=anc)
        fix_xscroll = ttk.Scrollbar(fix_frame, orient="horizontal", command=self.fixed_tree.xview)
        self.fixed_tree.configure(xscrollcommand=fix_xscroll.set)
        self.fixed_tree.grid(row=0, column=0, sticky="ew")
        fix_xscroll.grid(row=1, column=0, sticky="ew")
        self.fixed_tree.tag_configure("total_row", background="#064e3b", foreground="#a7f3d0")

        # Section 3: Simulasi Dampak Naik-Turunnya Harga Pasar
        fluk_title = ctk.CTkLabel(
            self.tasik_scroll,
            text="3. Simulasi Dampak Naik-Turunnya Harga Bahan di Pasar Terhadap Modal & Laba Harian",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        fluk_title.grid(row=5, column=0, sticky="w", padx=8, pady=(4, 4))

        fluk_frame = ctk.CTkFrame(self.tasik_scroll, corner_radius=8)
        fluk_frame.grid(row=6, column=0, sticky="ew", padx=6, pady=(0, 10))
        fluk_frame.grid_columnconfigure(0, weight=1)

        self.fluktuasi_tree = ttk.Treeview(
            fluk_frame,
            columns=("kondisi", "b_val", "c_val", "q_opt", "modal_harian", "laba_max"),
            show="headings",
            height=4
        )
        for cid, cname, w, anc in [
            ("kondisi", "Kondisi Harga Pasar", 215, "w"),
            ("b_val", "Modal / Porsi (b)", 115, "e"),
            ("c_val", "Tetap / Hari (c)", 115, "e"),
            ("q_opt", "Target (q*)", 95, "center"),
            ("modal_harian", "Total Modal Harian", 140, "e"),
            ("laba_max", "Laba Bersih Maks/Hr", 145, "e"),
        ]:
            self.fluktuasi_tree.heading(cid, text=cname)
            self.fluktuasi_tree.column(cid, width=w, anchor=anc)
        fluk_xscroll = ttk.Scrollbar(fluk_frame, orient="horizontal", command=self.fluktuasi_tree.xview)
        self.fluktuasi_tree.configure(xscrollcommand=fluk_xscroll.set)
        self.fluktuasi_tree.grid(row=0, column=0, sticky="ew")
        fluk_xscroll.grid(row=1, column=0, sticky="ew")
        self.fluktuasi_tree.tag_configure("active_row", background="#064e3b", foreground="#a7f3d0")

        # Section 4: Katalog Harga Komoditas Tasikmalaya & Indonesia
        cat_title = ctk.CTkLabel(
            self.tasik_scroll,
            text="4. Katalog Acuan Harga Komoditas, Energi, Sewa & UMK Tasikmalaya / Indonesia (2025-2026)",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        cat_title.grid(row=7, column=0, sticky="w", padx=8, pady=(4, 4))

        cat_frame = ctk.CTkFrame(self.tasik_scroll, corner_radius=8)
        cat_frame.grid(row=8, column=0, sticky="nsew", padx=6, pady=(0, 10))
        cat_frame.grid_columnconfigure(0, weight=1)

        self.catalog_tree = ttk.Treeview(
            cat_frame,
            columns=("kategori", "komoditas", "harga", "kisaran", "sumber"),
            show="headings",
            height=13
        )
        for cid, cname, w, anc in [
            ("kategori", "Kategori", 130, "w"),
            ("komoditas", "Komoditas / Item", 205, "w"),
            ("harga", "Acuan Utama", 130, "e"),
            ("kisaran", "Kisaran Pasar Lapangan", 215, "w"),
            ("sumber", "Sumber Pemantauan", 200, "w"),
        ]:
            self.catalog_tree.heading(cid, text=cname)
            self.catalog_tree.column(cid, width=w, anchor=anc)

        cat_yscroll = ttk.Scrollbar(cat_frame, orient="vertical", command=self.catalog_tree.yview)
        cat_xscroll = ttk.Scrollbar(cat_frame, orient="horizontal", command=self.catalog_tree.xview)
        self.catalog_tree.configure(yscrollcommand=cat_yscroll.set, xscrollcommand=cat_xscroll.set)
        self.catalog_tree.grid(row=0, column=0, sticky="nsew")
        cat_yscroll.grid(row=0, column=1, sticky="ns")
        cat_xscroll.grid(row=1, column=0, sticky="ew")

        for item in KATALOG_KOMODITAS_TASIK:
            harga_txt = f"Rp {item['harga_tasik']:,.0f}/{item['satuan']}".replace(",", ".")
            self.catalog_tree.insert(
                "",
                tk.END,
                values=(
                    item["kategori"],
                    item["komoditas"],
                    harga_txt,
                    item["kisaran"],
                    item["sumber"],
                ),
            )

        self._apply_treeview_theme(ctk.get_appearance_mode().lower() == "dark")

    def _apply_treeview_theme(self, is_dark: bool):
        style = ttk.Style()
        style.theme_use("clam")
        if is_dark:
            bg = "#242424"
            fg = "#f3f4f6"
            head_bg = "#334155"
            head_fg = "#ffffff"
            total_bg = "#064e3b"
            total_fg = "#a7f3d0"
        else:
            bg = "#ffffff"
            fg = "#111827"
            head_bg = "#e2e8f0"
            head_fg = "#0f172a"
            total_bg = "#d1fae5"
            total_fg = "#065f46"

        style.configure(
            "Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=bg,
            font=("Segoe UI", 10),
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background=head_bg,
            foreground=head_fg,
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

        for tv_name in ("var_tree", "fixed_tree", "fluktuasi_tree"):
            tv = getattr(self, tv_name, None)
            if tv is not None:
                tv.tag_configure("total_row", background=total_bg, foreground=total_fg)
                tv.tag_configure("active_row", background=total_bg, foreground=total_fg)

    def _calculate_calculus_model(self):
        p = self.p
        c = self.c
        b = self.b
        a = self.a

        alpha = p - b

        if a > 0:
            q_opt = alpha / (2.0 * a)
            if 0.0 < q_opt < float(self.q_max):
                step_uji = 10.0 if q_opt >= 15.0 else max(0.5, round(q_opt / 2.0, 1))
                x_kiri = max(0.0, round(q_opt - step_uji, 1))
                x_kanan = min(float(self.q_max), round(q_opt + step_uji, 1))
                if x_kiri >= q_opt:
                    x_kiri = 0.0
                if x_kanan <= q_opt:
                    x_kanan = float(self.q_max)
            elif q_opt <= 0.0:
                x_kiri = 0.0
                x_kanan = min(float(self.q_max), 10.0)
            else:
                x_kiri = max(0.0, round(float(self.q_max) - 10.0, 1))
                x_kanan = float(self.q_max)

            p_prime_kiri = -2.0 * a * x_kiri + alpha
            p_prime_kanan = -2.0 * a * x_kanan + alpha
            is_max = (0.0 < q_opt < float(self.q_max)) and (p_prime_kiri > 0) and (p_prime_kanan < 0)
        else:
            q_opt = 0.0
            x_kiri = 0.0
            x_kanan = min(float(self.q_max), 10.0)
            p_prime_kiri = alpha
            p_prime_kanan = alpha
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
            "q_opt": q_opt, "is_max": is_max,
            "x_kiri": x_kiri, "x_kanan": x_kanan,
            "p_prime_kiri": p_prime_kiri, "p_prime_kanan": p_prime_kanan,
            "r_opt": r_opt, "c_opt": c_opt, "p_opt": p_opt,
            "ac_opt": ac_opt, "margin_pct": margin_pct,
            "D": D, "q_bep1": q_bep1, "q_bep2": q_bep2
        }

    @staticmethod
    def _parse_number_input(raw_text: str):
        """Parse angka standar maupun format pemisah ribuan Indonesia (mis. 20.000 atau Rp 20.000)."""
        import re
        cleaned = raw_text.strip().replace("Rp", "").replace("rp", "").replace(" ", "")
        if not cleaned or cleaned in ("-", "+", ".", "-.", "+."):
            return None
        if re.fullmatch(r"[+-]?\d{1,3}(\.\d{3})+", cleaned):
            cleaned = cleaned.replace(".", "")
        elif "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            if re.fullmatch(r"[+-]?\d{1,3}(,\d{3})+", cleaned):
                cleaned = cleaned.replace(",", "")
            else:
                cleaned = cleaned.replace(",", ".")
        try:
            val = float(cleaned)
        except ValueError:
            return None
        return val if math.isfinite(val) else None

    @staticmethod
    def _format_synced_number(value, max_decimals=2):
        """Format angka rapi tanpa .0 saat bilangan bulat dan bulatkan desimal seperlunya."""
        rounded = round(float(value), max_decimals)
        if rounded == 0 and value > 0:
            return f"{value:.4g}"
        if rounded.is_integer():
            return str(int(rounded))
        return f"{rounded:.{max_decimals}f}".rstrip("0").rstrip(".")

    def _sync_slider_and_views(self):
        """Hitung ulang model kalkulus, sesuaikan slider q dengan aman, dan perbarui tampilan."""
        self._calculate_calculus_model()

        self.q_slider.configure(to=self.q_max, number_of_steps=self.q_max)
        q_star = max(0, min(self.q_max, round(self.calc_results["q_opt"])))
        self.q_slider.set(q_star)
        self.slider_q = float(q_star)

        self._update_all_views()

    def _schedule_price_change(self, event=None):
        if self._syncing_from_p:
            return
        self._pending_price_autofill = True
        if self._price_debounce_id is not None:
            try:
                self.after_cancel(self._price_debounce_id)
            except Exception:
                pass
        self._price_debounce_id = self.after(300, lambda: self._on_price_change(immediate=False))

    def _on_wilayah_change(self, wilayah_name):
        self.wilayah = wilayah_name
        if self.auto_tasik_var.get():
            self._on_price_change(immediate=True, force=True)
        else:
            self._update_tasik_tab()

    def _on_kondisi_change(self, kondisi_name):
        self.kondisi_pasar = kondisi_name
        if self.auto_tasik_var.get():
            self._on_price_change(immediate=True, force=True)
        else:
            self.tasik_breakdown = hitung_estimasi_umkm(
                self.p, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
            )
            self._update_tasik_tab()

    def _on_toggle_auto_tasik(self):
        if self.auto_tasik_var.get():
            self._manual_override = False
            self._on_price_change(immediate=True, force=True)
        else:
            self._update_tasik_tab()

    def _on_manual_cost_edit(self, event=None):
        if not self._syncing_from_p:
            self._manual_override = True
            self._pending_price_autofill = False

    def _open_tasik_tab(self):
        self.tabview.set("Harga Tasik")

    def _reset_ketoprak_default(self):
        self.wilayah = "Kota Tasikmalaya (Pasar Cikurubuk)"
        self.wilayah_menu.set(self.wilayah)
        self.kondisi_pasar = "Harga Normal Pasar (Rata-rata)"
        self.kondisi_menu.set(self.kondisi_pasar)
        self.auto_tasik_var.set(True)
        self.preset_menu.set("UMKM Ketoprak (Harian Tasikmalaya)")
        self._apply_preset("UMKM Ketoprak (Harian Tasikmalaya)")

    def _on_price_change(self, event=None, immediate=False, force=False):
        """Mengisi otomatis c, b, a, q_max harian (non-borongan) dari harga pasar Tasikmalaya saat p berubah."""
        if self._syncing_from_p:
            return

        if immediate and self._price_debounce_id is not None:
            try:
                self.after_cancel(self._price_debounce_id)
            except Exception:
                pass
            self._price_debounce_id = None

        raw = self.entries["p"].get().strip()
        if not force and raw == self._last_p_text:
            return

        p_baru = self._parse_number_input(raw)
        if p_baru is None or p_baru <= 0:
            return

        # Tahan eksekusi saat pengguna baru mengetik digit awal (mis. '2' atau '20' menuju '20000')
        if not immediate and not force and p_baru < 1000:
            return

        self._last_p_text = raw
        self._pending_price_autofill = False

        if not self.auto_tasik_var.get():
            c_val = self._parse_number_input(self.entries["c"].get())
            b_val = self._parse_number_input(self.entries["b"].get())
            a_val = self._parse_number_input(self.entries["a"].get())
            q_val = self._parse_number_input(self.entries["q_max"].get())
            if None not in (c_val, b_val, a_val, q_val) and a_val > 0 and b_val >= 0 and c_val >= 0:
                self.c = c_val
                self.b = b_val
                self.a = a_val
                self.q_max = max(20, int(q_val))
            self.p = p_baru
            self.tasik_breakdown = hitung_estimasi_umkm(
                self.p, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
            )
            self._sync_slider_and_views()
            return

        estimasi = hitung_estimasi_umkm(
            p_baru, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
        )
        c_baru = estimasi["c"]
        b_baru = estimasi["b"]
        a_baru = estimasi["a"]
        q_max_baru = estimasi["q_max"]

        c_text = self._format_synced_number(c_baru, max_decimals=0)
        b_text = self._format_synced_number(b_baru, max_decimals=0)
        a_text = self._format_synced_number(a_baru, max_decimals=1)
        q_max_text = str(q_max_baru)

        self._syncing_from_p = True
        try:
            updates = {
                "c": c_text,
                "b": b_text,
                "a": a_text,
                "q_max": q_max_text,
            }
            for key, text_val in updates.items():
                entry = self.entries[key]
                entry.delete(0, tk.END)
                entry.insert(0, text_val)
        finally:
            self._syncing_from_p = False

        self.p = p_baru
        self.c = float(c_text)
        self.b = float(b_text)
        self.a = float(a_text)
        self.q_max = q_max_baru
        self._manual_override = False
        self.tasik_breakdown = estimasi
        self._sync_slider_and_views()

    def _apply_preset(self, preset_name):
        if preset_name in self.presets:
            data = self.presets[preset_name]
            self._syncing_from_p = True
            try:
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

                self._last_p_text = self.entries["p"].get().strip()
            finally:
                self._syncing_from_p = False

            if data.get("static_report"):
                self._manual_override = False
                self._on_click_calculate()
            elif self.auto_tasik_var.get():
                self._on_price_change(immediate=True, force=True)
            else:
                self._manual_override = False
                self._on_click_calculate()

    def _on_click_calculate(self):
        if self._pending_price_autofill and self.auto_tasik_var.get():
            self._on_price_change(immediate=True, force=True)
            return

        try:
            p_val = self._parse_number_input(self.entries["p"].get())
            c_val = self._parse_number_input(self.entries["c"].get())
            b_val = self._parse_number_input(self.entries["b"].get())
            a_val = self._parse_number_input(self.entries["a"].get())
            q_val = self._parse_number_input(self.entries["q_max"].get())

            if None in (p_val, c_val, b_val, a_val, q_val):
                raise ValueError("Invalid numeric format")

            self.p = p_val
            self.c = c_val
            self.b = b_val
            self.a = a_val
            self.q_max = max(20, int(q_val))

            if self.p <= 0 or self.a <= 0 or self.b < 0 or self.c < 0:
                messagebox.showerror("Kesalahan Input", "Parameter p dan a harus bernilai lebih besar dari 0, serta biaya tidak boleh negatif.")
                return

            est = hitung_estimasi_umkm(
                self.p, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
            )
            self.tasik_breakdown = est
            self._manual_override = (
                abs(self.c - est["c"]) > 1.0
                or abs(self.b - est["b"]) > 1.0
                or abs(self.a - est["a"]) > 0.15
            )
            self._last_p_text = self.entries["p"].get().strip()

            self._sync_slider_and_views()
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
        self._apply_treeview_theme(is_dark)
        self._redraw_graph()
        self._update_integral_tab()
        self._update_pdf_solver()

    def _update_all_views(self):
        self._update_summary_cards()
        self._update_live_card()
        self._update_tasik_tab()
        self._update_kalkulus_text()
        self._update_integral_tab()
        self._populate_table()
        self._redraw_graph()

    def _update_integral_tab(self):
        if not hasattr(self, "int_umkm_text_lbl"):
            return

        ig = hitung_integral_umkm(self.p, self.c, self.b, self.a, self.q_max)
        b3 = ig["b3"]
        b4 = ig["b4"]
        a3 = ig["a3"]
        b1 = ig["b1"]
        a4 = ig["a4_b2"]
        b5 = ig["b5"]

        sub_lines = []
        for idx, sub in enumerate(b4["sub_intervals"], 1):
            tanda_formula = "P(x)" if "Positif" in sub["tanda"] else "-(P(x))"
            sub_lines.append(
                f"   * Sub-interval {idx} [{sub['lo']:.2f} .. {sub['hi']:.2f}] ({sub['tanda']} -> {tanda_formula}): "
                f"Luas = Rp {sub['nilai_abs']:,.0f}"
            )
        sub_txt = "\n".join(sub_lines)

        bep1_s = f"{ig['q_bep1']:.2f}" if ig["q_bep1"] is not None else "-"
        bep2_s = f"{ig['q_bep2']:.2f}" if ig["q_bep2"] is not None else "-"
        samples_txt = " | ".join(f"x={qv:g} -> Rp {av:,.2f}" for qv, av in b5["samples"])

        txt = (
            f"==============================================================================================\n"
            f"     PENERAPAN RUMUS INTEGRAL (MENGIKUTI KODE RUMUS PDF A.1-A.5 & B.1-B.5) PADA MODEL UMKM\n"
            f"==============================================================================================\n"
            f"Parameter Aktif: p = Rp {ig['p']:,.0f} | c = Rp {ig['c']:,.0f} | b = Rp {ig['b']:,.0f} | a = {ig['a']} | Domain x ∈ [0, {ig['q_max']:.0f}]\n"
            f"Fungsi Laba: P(x) = -{ig['a']}x² + {ig['alpha']:,.0f}x - {ig['c']:,.0f}   |   Laba Marjinal: P'(x) = -{2*ig['a']:.0f}x + {ig['alpha']:,.0f}\n\n"
            f"1. INTEGRAL NILAI MUTLAK LINIER (MENGIKUTI RUMUS PDF B.3: ∫ |x - 4| dx)\n"
            f"   Rumus: ∫[0..{ig['q_max']:.0f}] |P'(x)| dx = ∫[0..{ig['q_max']:.0f}] |MR - MC| dx\n"
            f"   * Pembuat nol P'(x) = 0  ==>  x* = {ig['q_opt']:.2f} (split interval pada x = {b3['q_split']:.2f})\n"
            f"   * [0 <= x <= {b3['q_split']:.2f}]  : P'(x) >= 0  -> ∫ P'(x) dx  = Rp {b3['kenaikan_laba']:,.0f}  (Total Kenaikan Laba Menuju Puncak)\n"
            f"   * [{b3['q_split']:.2f} <= x <= {ig['q_max']:.0f}]: P'(x) < 0   -> ∫ -P'(x) dx = Rp {b3['pengikisan_laba']:,.0f}  (Pemborosan Over-Produksi)\n"
            f"   * Total Integral Mutlak |P'(x)| (Analitis) = Rp {b3['total_eksak']:,.0f}  (Cek Numerik: Rp {b3['total_numerik']:,.0f})\n\n"
            f"2. INTEGRAL NILAI MUTLAK KUADRAT (MENGIKUTI RUMUS PDF B.4: ∫ |x² - 3x - 4| dx)\n"
            f"   Rumus: ∫[0..{ig['q_max']:.0f}] |P(x)| dx   (Akar P(x) = 0 di BEP1 = {bep1_s}, BEP2 = {bep2_s})\n"
            f"{sub_txt}\n"
            f"   * Total Area Surplus Laba (+) = Rp {b4['area_laba']:,.0f}  |  Total Area Defisit (-) = Rp {b4['area_rugi']:,.0f}\n"
            f"   * Total Integral Mutlak ∫|P(x)| dx = Rp {b4['total_mutlak_eksak']:,.0f}  (Cek Numerik: Rp {b4['total_mutlak_numerik']:,.0f})\n"
            f"   * Integral Netto ∫ P(x) dx = Rp {b4['integral_netto']:,.0f}  |  Rata-Rata Laba di [0,{ig['q_max']:.0f}] = Rp {b4['rata_laba_domain']:,.0f}/hari\n\n"
            f"3. INTEGRAL PECAHAN POLINOM & ln|x| (MENGIKUTI RUMUS PDF A.3: ∫ (2x² - 5x + 6)/x dx)\n"
            f"   Biaya Rata-Rata AC(x) = C(x)/x = ({ig['a']}x² + {ig['b']:,.0f}x + {ig['c']:,.0f})/x = {ig['a']}x + {ig['b']:,.0f} + {ig['c']:,.0f}/x\n"
            f"   * ∫[{a3['q1']:.0f}..{a3['q2']:.0f}] AC(x) dx = [ ({ig['a']}/2)x² + {ig['b']:,.0f}x + {ig['c']:,.0f} ln|x| ]_{a3['q1']:.0f}^{a3['q2']:.0f} = Rp {a3['integral_ac']:,.0f}\n"
            f"   * Rata-Rata Biaya Per Porsi pada [{a3['q1']:.0f}, {a3['q2']:.0f}] = Rp {a3['rata_rata_ac']:,.0f}/porsi\n\n"
            f"4. INTEGRAL SUBSTITUSI u + UBAH BATAS (MENGIKUTI RUMUS PDF B.1 / A.1)\n"
            f"   Menghitung Total Biaya Variabel Optimal VC(x*) = ∫[0..{b1['q_hi']:.2f}] ({2*ig['a']:.0f}x + {ig['b']:,.0f}) dx\n"
            f"   * misal: u = {2*ig['a']:.0f}x + {ig['b']:,.0f}  ==>  du = {2*ig['a']:.0f} dx  ==>  dx = 1/{2*ig['a']:.0f} du\n"
            f"   * Ubah batas: x = 0 -> u = {b1['u_lo']:,.0f}  |  x = {b1['q_hi']:.2f} -> u = {b1['u_hi']:,.0f}\n"
            f"   * subs = (1/{2*ig['a']:.0f}) ∫[{b1['u_lo']:,.0f}..{b1['u_hi']:,.0f}] u du = [u² / {4*ig['a']:.0f}]_{b1['u_lo']:,.0f}^{b1['u_hi']:,.0f} = Rp {b1['vc_substitusi']:,.0f}\n"
            f"   * Verifikasi rumus langsung a(x*)² + b(x*) = Rp {b1['vc_langsung']:,.0f} (Identik 100%)\n\n"
            f"5. INTEGRAL TRIGONOMETRI SUBSTITUSI u = ωt (MENGIKUTI RUMUS PDF A.4 & B.2: Proyeksi Laba {a4['hari']} Hari)\n"
            f"   L(t) = P* + ΔP·(½ sin(ωt) + sin(2ωt)), dengan ω = 2π/7 (siklus mingguan), P* = Rp {ig['p_opt']:,.0f}, ΔP = Rp {a4['delta_p']:,.0f}\n"
            f"   * ∫[0..{a4['hari']}] L(t) dt = [ P*·t - (ΔP/(2ω))cos(ωt) - (ΔP/(2ω))cos(2ωt) ]_0^{a4['hari']}\n"
            f"   * Akumulasi Laba {a4['hari']} Hari (Gelombang Penjualan) = Rp {a4['laba_bulanan_musiman']:,.0f}  (vs Datar 30×P*: Rp {a4['laba_bulanan_datar']:,.0f})\n\n"
            f"6. TEOREMA DASAR KALKULUS I & L'HÔPITAL (MENGIKUTI RUMUS PDF B.5)\n"
            f"   lim[x->0] (1/x) ∫[0..x] MC(t) dt  =  lim[x->0] (d/dx ∫[0..x] (2at + b) dt) / (d/dx [x])  =  lim[x->0] (2ax + b)/1  =  Rp {b5['limit_eksak']:,.0f}\n"
            f"   * Konvergensi AVC(x) saat x -> 0+: {samples_txt}"
        ).replace(",", ".")
        self.int_umkm_text_lbl.configure(text=txt)

        # Gambar 4 panel grafik integral UMKM
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg = "#18181b" if is_dark else "#ffffff"
        fig_bg = "#18181b" if is_dark else "#f8f9fa"
        tc = "#f3f4f6" if is_dark else "#111827"
        gc = "#27272a" if is_dark else "#e5e7eb"

        self.int_umkm_fig.clear()
        self.int_umkm_fig.patch.set_facecolor(fig_bg)
        gs = self.int_umkm_fig.add_gridspec(2, 2, hspace=0.45, wspace=0.28)
        q_arr = np.linspace(0.0, ig["q_max"], 400)

        def _st(ax, title, xl, yl):
            ax.set_facecolor(bg)
            ax.set_title(title, fontsize=9.5, fontweight="bold", color=tc, pad=6)
            ax.set_xlabel(xl, fontsize=8, color=tc)
            ax.set_ylabel(yl, fontsize=8, color=tc)
            ax.tick_params(colors=tc, labelsize=7.5)
            ax.grid(True, linestyle="--", alpha=0.5, color=gc)

        # Panel 1: B.3 |P'(x)|
        ax1 = self.int_umkm_fig.add_subplot(gs[0, 0])
        _st(ax1, "B.3: Luas |P'(x)| = |MR - MC| (Naik vs Over-Produksi)", "Porsi (x)", "Rp/porsi")
        fp_arr = -2.0 * ig["a"] * q_arr + ig["alpha"]
        ax1.plot(q_arr, np.abs(fp_arr), color="#f59e0b", linewidth=2, label="|P'(x)|")
        ax1.fill_between(q_arr, np.abs(fp_arr), 0, where=(fp_arr >= 0), color="#10b981", alpha=0.28, label="Naik Laba")
        ax1.fill_between(q_arr, np.abs(fp_arr), 0, where=(fp_arr < 0), color="#ef4444", alpha=0.28, label="Pemborosan")
        ax1.legend(loc="upper right", fontsize=7, facecolor=bg, labelcolor=tc)

        # Panel 2: B.4 |P(x)|
        ax2 = self.int_umkm_fig.add_subplot(gs[0, 1])
        _st(ax2, "B.4: Luas |P(x)| (Surplus Laba & Defisit Dibalik)", "Porsi (x)", "Rupiah")
        f_arr = -ig["a"] * (q_arr ** 2) + ig["alpha"] * q_arr - ig["c"]
        ax2.plot(q_arr, np.abs(f_arr), color="#3b82f6", linewidth=2, label="|P(x)|")
        ax2.plot(q_arr, f_arr, color="#94a3b8", linestyle="--", linewidth=1, label="P(x) asli")
        ax2.fill_between(q_arr, np.abs(f_arr), 0, where=(f_arr >= 0), color="#10b981", alpha=0.28, label="Laba (+)")
        ax2.fill_between(q_arr, np.abs(f_arr), 0, where=(f_arr < 0), color="#ef4444", alpha=0.25, label="Defisit (-)")
        ax2.legend(loc="upper left", fontsize=7, facecolor=bg, labelcolor=tc)

        # Panel 3: A.3 AC(x) & B.1 VC(x*)
        ax3 = self.int_umkm_fig.add_subplot(gs[1, 0])
        _st(ax3, "A.3 & B.1: Luas ∫MC(x)dx = VC(x*) & Kurva AC(x)", "Porsi (x)", "Rp/porsi")
        q_pos = np.linspace(max(1.0, ig["q_max"] * 0.03), ig["q_max"], 350)
        mc_pos = 2.0 * ig["a"] * q_pos + ig["b"]
        ac_pos = ig["a"] * q_pos + ig["b"] + ig["c"] / q_pos
        ax3.plot(q_pos, mc_pos, color="#ef4444", linewidth=2, label="MC(x) = 2ax + b")
        ax3.plot(q_pos, ac_pos, color="#8b5cf6", linewidth=2, label="AC(x) = ax + b + c/x")
        ax3.fill_between(q_pos, mc_pos, 0, where=(q_pos <= ig["q_opt"]), color="#ef4444", alpha=0.2, label="VC(x*)")
        ax3.set_ylim(0, min(max(mc_pos) * 1.4, max(ac_pos)))
        ax3.legend(loc="upper right", fontsize=7, facecolor=bg, labelcolor=tc)

        # Panel 4: A.4/B.2 Proyeksi Laba 30 Hari
        ax4 = self.int_umkm_fig.add_subplot(gs[1, 1])
        _st(ax4, f"A.4/B.2: Proyeksi Laba Harian {a4['hari']} Hari (Gelombang)", "Hari ke-t", "Laba/Hari (Rp)")
        t_arr = np.linspace(0.0, float(a4["hari"]), 300)
        l_arr = ig["p_opt"] + a4["delta_p"] * (0.5 * np.sin(a4["omega"] * t_arr) + np.sin(2.0 * a4["omega"] * t_arr))
        ax4.plot(t_arr, l_arr, color="#10b981", linewidth=2, label="L(t) Harian")
        ax4.axhline(ig["p_opt"], color="#f59e0b", linestyle="--", linewidth=1.2, label="P* Rata-rata")
        ax4.fill_between(t_arr, l_arr, 0, where=(l_arr >= 0), color="#10b981", alpha=0.18)
        ax4.fill_between(t_arr, l_arr, 0, where=(l_arr < 0), color="#ef4444", alpha=0.18)
        ax4.legend(loc="lower right", fontsize=7, facecolor=bg, labelcolor=tc)

        self.int_umkm_fig.subplots_adjust(top=0.92, bottom=0.10, left=0.09, right=0.97, hspace=0.48, wspace=0.28)
        self.int_umkm_canvas.draw()

    def _update_pdf_solver(self):
        if not hasattr(self, "pdf_soal_menu"):
            return
        judul = self.pdf_soal_menu.get()
        kode = self._pdf_judul_to_kode.get(judul, "B.4")
        x_val = self._parse_number_input(self.pdf_x_entry.get())
        if x_val is None:
            x_val = 2.0

        hasil = evaluasi_soal_pdf(kode, x_uji=x_val)
        teks = (
            f"Soal [{hasil['kode']}]: {hasil['soal']}\n"
            f"Hasil Eksak: {hasil['hasil_eksak']}\n"
            f"-----------------------------------------------------------------------------------\n"
            f"{hasil['langkah']}\n"
            f"-----------------------------------------------------------------------------------\n"
            f"Verifikasi Komputasi: {hasil['verifikasi']}"
        )
        self.pdf_result_lbl.configure(text=teks)

        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg = "#18181b" if is_dark else "#ffffff"
        fig_bg = "#18181b" if is_dark else "#f8f9fa"
        tc = "#f3f4f6" if is_dark else "#111827"
        gc = "#27272a" if is_dark else "#e5e7eb"

        self.int_pdf_fig.clear()
        self.int_pdf_fig.patch.set_facecolor(fig_bg)
        ax = self.int_pdf_fig.add_subplot(111)
        ax.set_facecolor(bg)
        p_data = hasil["plot"]
        ax.set_title(p_data["title"], fontsize=10.5, fontweight="bold", color=tc, pad=8)
        ax.set_xlabel(p_data["xlabel"], fontsize=9, color=tc)
        ax.set_ylabel(p_data["ylabel"], fontsize=9, color=tc)
        ax.tick_params(colors=tc, labelsize=8)
        ax.grid(True, linestyle="--", alpha=0.55, color=gc)

        if hasil["jenis"] == "tak_tentu":
            ax.plot(p_data["x"], p_data["y"], color="#3b82f6", linewidth=2, label="Integran f(x)")
            ax.plot(p_data["x"], p_data["F"], color="#10b981", linewidth=2, linestyle="--", label="Antiturunan F(x) (C=0)")
            ax.axhline(0, color="#64748b", linewidth=0.9)
        elif hasil["jenis"] == "tentu":
            ax.plot(p_data["x"], p_data["y"], color="#10b981", linewidth=2.2, label=f"Luas Area = {hasil['hasil_eksak']}")
            ax.fill_between(p_data["x"], p_data["y"], 0, color="#10b981", alpha=0.25)
            for sp in p_data.get("split", []):
                ax.axvline(sp, color="#f59e0b", linestyle="--", linewidth=1.4, label=f"Titik Pecah x = {sp:g}")
        else:
            ax.plot(p_data["x"], p_data["y"], color="#8b5cf6", linewidth=2.2, label="Nilai fungsi saat x -> 0+")
            ax.axhline(p_data["limit_y"], color="#10b981", linestyle="--", linewidth=1.5, label="Limit Eksak = 1/18")

        ax.legend(loc="best", fontsize=8, facecolor=bg, labelcolor=tc)
        self.int_pdf_fig.tight_layout()
        self.int_pdf_canvas.draw()

    def _update_tasik_tab(self):
        est = getattr(self, "tasik_breakdown", None)
        if not est:
            return

        satuan = est["satuan_produk"]
        wil_cfg = WILAYAH_CONFIG.get(self.wilayah, WILAYAH_CONFIG["Kota Tasikmalaya (Pasar Cikurubuk)"])
        kondisi_cfg = KONDISI_PASAR_CONFIG.get(self.kondisi_pasar, KONDISI_PASAR_CONFIG["Harga Normal Pasar (Rata-rata)"])
        mode_txt = "Penyesuaian Manual / Studi Kasus" if self._manual_override else (
            f"Auto Harian Non-Borongan ({kondisi_cfg['label_ringkas']})" if self.auto_tasik_var.get() else "Mode Manual (Auto-Isi Nonaktif)"
        )

        res = self.calc_results
        q_opt = res.get("q_opt", 0.0)
        p_opt = res.get("p_opt", 0.0)
        q_harian = max(1, round(q_opt))
        modal_bahan_hari = self.b * q_harian
        total_modal_hari = modal_bahan_hari + self.c

        # Update kartu ringkas di sidebar
        self.tasik_segmen_lbl.configure(text=f"Segmen: {est['segmen']}")
        self.tasik_summary_lbl.configure(
            text=(
                f"Modal/Porsi (b): Rp {self.b:,.0f} (kisaran Rp {est['b_min']:,.0f} - Rp {est['b_max']:,.0f})\n"
                f"Tetap/Hari (c): Rp {self.c:,.0f}/hari (non-borongan)\n"
                f"Belanja Harian ({q_harian} {satuan}): Rp {total_modal_hari:,.0f}/hari"
            ).replace(",", ".")
        )
        if self._manual_override:
            note_txt = "Catatan: Parameter memakai nilai manual/laporan. Klik 'Lihat Rincian' untuk bandingkan dengan pasar Tasikmalaya."
        else:
            note_txt = (
                f"{wil_cfg['label_ringkas']} • {kondisi_cfg['label_ringkas']} | "
                f"Naik-turun modal/hr: Rp {est['modal_harian_min']:,.0f} - Rp {est['modal_harian_max']:,.0f}"
            ).replace(",", ".")
        self.tasik_note_lbl.configure(text=note_txt)

        if not hasattr(self, "tasik_detail_lbl"):
            return

        detail_txt = (
            f"Usaha: {est['nama_usaha']}   |   Wilayah: {est['wilayah']}   |   Kondisi Pasar: {est['kondisi_pasar']}\n"
            f"Status Model: {mode_txt}   |   Harga Jual (p): Rp {self.p:,.0f}/{satuan}   ->   {est['segmen']}\n"
            f"Modal Belanja Harian ({q_harian} {satuan}, Non-Borongan): Bahan Rp {modal_bahan_hari:,.0f} + Tetap Rp {self.c:,.0f} = Rp {total_modal_hari:,.0f}/hari\n"
            f"Rentang Naik-Turun Harga Pasar: b = Rp {est['b_min']:,.0f}-{est['b_max']:,.0f}/{satuan} | c = Rp {est['c_min']:,.0f}-{est['c_max']:,.0f}/hari | Laba Maks Aktif = Rp {p_opt:,.0f}/hari\n"
            f"Dasar Disekonomi (a={self.a}): {est['disekonomi_catatan']} | {est['kondisi_catatan']}"
        ).replace(",", ".")
        self.tasik_detail_lbl.configure(text=detail_txt)

        for tv in (self.var_tree, self.fixed_tree, self.fluktuasi_tree):
            for row_id in tv.get_children():
                tv.delete(row_id)

        q_ref_est = max(1, est["q_target_harian"])
        for it in est["var_items"]:
            rentang_str = f"Rp {it['min_subtotal']:,.0f} - Rp {it['max_subtotal']:,.0f}".replace(",", ".")
            belanja_item_harian = it["subtotal"] * q_ref_est
            self.var_tree.insert(
                "",
                tk.END,
                values=(
                    it["komponen"],
                    it["takaran"],
                    f"Rp {it['subtotal']:,.0f}".replace(",", "."),
                    rentang_str,
                    f"Rp {belanja_item_harian:,.0f}".replace(",", "."),
                ),
            )
        self.var_tree.insert(
            "",
            tk.END,
            values=(
                f"TOTAL MODAL VARIABEL (b) PER {satuan.upper()}",
                f"Belanja harian untuk {q_ref_est} {satuan} (non-borongan)",
                f"Rp {est['b']:,.0f}".replace(",", "."),
                f"Rp {est['b_min']:,.0f} - Rp {est['b_max']:,.0f}".replace(",", "."),
                f"Rp {est['modal_bahan_harian']:,.0f}".replace(",", "."),
            ),
            tags=("total_row",),
        )

        for it in est["fixed_items"]:
            rentang_fix = f"Rp {it['min_subtotal']:,.0f} - Rp {it['max_subtotal']:,.0f}".replace(",", ".")
            self.fixed_tree.insert(
                "",
                tk.END,
                values=(
                    it["komponen"],
                    it["basis"],
                    f"Rp {it['subtotal']:,.0f}".replace(",", "."),
                    rentang_fix,
                    it["sumber"],
                ),
            )
        self.fixed_tree.insert(
            "",
            tk.END,
            values=(
                "TOTAL BIAYA TETAP HARIAN (c / FC)",
                "Pemakaian riil per hari (non-borongan)",
                f"Rp {est['c']:,.0f}".replace(",", "."),
                f"Rp {est['c_min']:,.0f} - Rp {est['c_max']:,.0f}".replace(",", "."),
                f"Total modal keluar/hr: Rp {est['total_modal_harian']:,.0f}".replace(",", "."),
            ),
            tags=("total_row",),
        )

        for sk in est["skenario_harga"]:
            tag_sk = ("active_row",) if sk["aktif"] else ()
            nama_sk = f"{'>> ' if sk['aktif'] else ''}{sk['nama']}"
            self.fluktuasi_tree.insert(
                "",
                tk.END,
                values=(
                    nama_sk,
                    f"Rp {sk['b']:,.0f}".replace(",", "."),
                    f"Rp {sk['c']:,.0f}".replace(",", "."),
                    f"{sk['q_opt']:.1f} {satuan}",
                    f"Rp {sk['total_modal_harian']:,.0f}".replace(",", "."),
                    f"Rp {sk['p_opt']:,.0f}".replace(",", "."),
                ),
                tags=tag_sk,
            )

    def _update_summary_cards(self):
        res = self.calc_results
        q_opt = res["q_opt"]
        p_opt = res["p_opt"]
        c = res["c"]
        x_kiri = res["x_kiri"]
        x_kanan = res["x_kanan"]
        pp_kiri = res["p_prime_kiri"]
        pp_kanan = res["p_prime_kanan"]

        self.card_q_opt["val_lbl"].configure(text=f"x* = {q_opt:.1f} porsi")
        self.card_profit_max["val_lbl"].configure(text=f"Rp {p_opt:,.0f}".replace(",", "."))

        if res["q_bep1"] is not None and res["q_bep2"] is not None:
            self.card_bep["val_lbl"].configure(text=f"-Rp {c:,.0f}".replace(",", "."))
            self.card_bep["sub_lbl"].configure(text=f"BEP: {res['q_bep1']:.1f} & {res['q_bep2']:.1f} porsi")
        else:
            self.card_bep["val_lbl"].configure(text=f"-Rp {c:,.0f}".replace(",", "."))
            self.card_bep["sub_lbl"].configure(text="Tidak ada BEP real")

        if res["is_max"]:
            self.card_test1["val_lbl"].configure(text="P'(x): (+) -> 0 -> (-)")
            self.card_test1["sub_lbl"].configure(
                text=f"P'({x_kiri:g})>0, P'({x_kanan:g})<0 (Maks)"
            )
        elif pp_kiri <= 0 and pp_kanan < 0:
            self.card_test1["val_lbl"].configure(text="P'(x) <= 0 (Turun)")
            self.card_test1["sub_lbl"].configure(text="Maks ujung kiri x=0 (Rugi)")
        else:
            self.card_test1["val_lbl"].configure(text="P'(x) >= 0 (Naik)")
            self.card_test1["sub_lbl"].configure(text=f"Naik hingga x={self.q_max}")

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
        self.live_rev_lbl.configure(text=f"Pendapatan R(x): Rp {r:,.0f}".replace(",", "."))
        self.live_cost_lbl.configure(text=f"Biaya Total C(x): Rp {cost:,.0f}".replace(",", "."))

        p_str = f"Fungsi Laba P(x): Rp {profit:,.0f}".replace(",", ".")
        self.live_profit_lbl.configure(text=p_str)

        opt_q = self.calc_results["q_opt"]
        if abs(q - opt_q) < 0.5:
            self.live_status_lbl.configure(text="Status: TITIK KRITIS x* (NILAI MAKSIMUM)", text_color="#10b981")
            self.live_profit_lbl.configure(text_color="#10b981")
        elif q == 0:
            self.live_status_lbl.configure(text="Status: UJUNG DOMAIN x=0 (NILAI MINIMUM MUTLAK)", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")
        elif profit > 0:
            self.live_status_lbl.configure(text="Status: ZONA LABA POSITIF (P(x) > 0)", text_color="#3b82f6")
            self.live_profit_lbl.configure(text_color="#3b82f6")
        elif abs(profit) < 100:
            self.live_status_lbl.configure(text="Status: TITIK IMPAS BEP (P(x) = 0)", text_color="#f59e0b")
            self.live_profit_lbl.configure(text_color="#f59e0b")
        else:
            self.live_status_lbl.configure(text="Status: ZONA RUGI DEFISIT (P(x) < 0)", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")

        if p_prime > 50:
            laju_str = f"Laju Laba P'(x): +Rp {p_prime:,.0f} (P' > 0: kurva naik)"
        elif p_prime < -50:
            laju_str = f"Laju Laba P'(x): -Rp {abs(p_prime):,.0f} (P' < 0: kurva turun)"
        else:
            laju_str = f"Laju Laba P'(x): Rp 0 (Titik Kritis x*: P'(x*) = 0)"
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

        ig = hitung_integral_umkm(p, c, b, a, self.q_max)
        b3 = ig["b3"]
        b4 = ig["b4"]
        a3 = ig["a3"]
        b1 = ig["b1"]
        a4 = ig["a4_b2"]
        b5 = ig["b5"]

        sub_lines = []
        for idx, sub in enumerate(b4["sub_intervals"], 1):
            tanda_formula = "P(x)" if "Positif" in sub["tanda"] else "-(P(x))"
            sub_lines.append(
                f"      * Sub-interval {idx} [{sub['lo']:.2f} .. {sub['hi']:.2f}] ({sub['tanda']} -> {tanda_formula}): "
                f"Luas = Rp {sub['nilai_abs']:,.0f}"
            )
        sub_txt = "\n".join(sub_lines)

        bep_block = ""
        if res["q_bep1"] is not None:
            bep_block = (
                f"   * Titik Impas Bawah (BEP 1) : x1 = {res['q_bep1']:.2f} porsi/hari\n"
                f"   * Titik Impas Atas (BEP 2)  : x2 = {res['q_bep2']:.2f} porsi/hari\n"
                f"   * Rentang Produksi Untung (P(x) > 0): ({res['q_bep1']:.2f} ; {res['q_bep2']:.2f}) porsi/hari\n"
                f"   * Batas Aman Minimum: Minimal {int(np.ceil(res['q_bep1']))} porsi | Batas Atas: {int(np.floor(res['q_bep2']))} porsi"
            )
        else:
            bep_block = "   * Diskriminan negatif: Tidak ada titik impas real pada kombinasi parameter ini."

        penjelasan = f"""
========================================================================================
      PENERAPAN KALKULUS UMKM: INTEGRAL, SUBSTITUSI u, NILAI MUTLAK, & OPTIMASI P(x)
                    (MENGIKUTI KODE RUMUS PADA LEMBAR PDF A.1-A.5 & B.1-B.5)
========================================================================================

I. FORMULASI FUNGSI P(x), R(x), & C(x) DARI TEOREMA DASAR KALKULUS I (POLA PDF B.5)
----------------------------------------------------------------------------------------
Misalkan x = jumlah porsi produksi harian (domain tertutup: 0 <= x <= {self.q_max}).
Dari laju marjinal usaha di pasar:
   * Pendapatan Marjinal : MR(x) = R'(x) = p = Rp {p:,.0f} / porsi
   * Biaya Marjinal      : MC(x) = C'(x) = {2*a:.0f}x + {b:,.0f}
   * Laba Marjinal       : P'(x) = MR(x) - MC(x) = -{2*a:.0f}x + ({p:,.0f} - {b:,.0f}) = -{2*a:.0f}x + {alpha:,.0f}

Menggunakan Teorema Dasar Kalkulus I (antiturunan integral dengan nilai awal C(0) = c = Rp {c:,.0f}):
   1. R(x) = ∫[0..x] MR(t) dt = ∫[0..x] {p:,.0f} dt = {p:,.0f}x
   2. C(x) = c + ∫[0..x] MC(t) dt = {c:,.0f} + ∫[0..x] ({2*a:.0f}t + {b:,.0f}) dt = {a}x² + {b:,.0f}x + {c:,.0f}
   3. P(x) = -c + ∫[0..x] P'(t) dt = -{c:,.0f} + ∫[0..x] (-{2*a:.0f}t + {alpha:,.0f}) dt
      P(x) = -{a}x² + {alpha:,.0f}x - {c:,.0f}
   (Uji FTC I: d/dx [ P(x) ] = P'(x) = -{2*a:.0f}x + {alpha:,.0f})

----------------------------------------------------------------------------------------
II. TITIK KRITIS x*, UJI TURUNAN PERTAMA P'(x), & NILAI EKSTREM [0, {self.q_max}]
----------------------------------------------------------------------------------------
1. Syarat Stasioner P'(x) = 0  <==>  MR(x) = MC(x):
   -{2*a:.0f}x + {alpha:,.0f} = 0  ==>  {2*a:.0f}x = {alpha:,.0f}
   x* = {alpha:,.0f} / {2*a:.0f} = {q_opt:.2f} porsi/hari  (dibulatkan: {round(q_opt)} porsi/hari)

2. Uji Turunan Pertama (First Derivative Test) & Perubahan Tanda P'(x):
   * Interval Kiri  (0 <= x < {q_opt:.2f}), titik uji x = {res['x_kiri']:g}:
     P'({res['x_kiri']:g}) = -{2*a:.0f}({res['x_kiri']:g}) + {alpha:,.0f} = Rp {res['p_prime_kiri']:+,.0f}  ({'POSITIF (+) -> kurva NAIK' if res['p_prime_kiri'] > 0 else 'NEGATIF/NOL -> kurva TURUN'})
   * Titik Kritis (x* = {q_opt:.2f}):
     P'({q_opt:.2f}) = 0  (Stasioner / Puncak Perubahan Tanda)
   * Interval Kanan ({q_opt:.2f} < x <= {self.q_max}), titik uji x = {res['x_kanan']:g}:
     P'({res['x_kanan']:g}) = -{2*a:.0f}({res['x_kanan']:g}) + {alpha:,.0f} = Rp {res['p_prime_kanan']:+,.0f}  ({'NEGATIF (-) -> kurva TURUN' if res['p_prime_kanan'] < 0 else 'POSITIF/NOL -> kurva NAIK'})
   * Garis Tanda P'(x):  [0] {'+++ (naik) +++' if res['p_prime_kiri'] > 0 else '--- (turun) ---'} [x* = {q_opt:.2f}] {'--- (turun) ---' if res['p_prime_kanan'] < 0 else '+++ (naik) +++'} [{self.q_max}]
   * Kesimpulan Uji Turunan Pertama:
     {'Tanda P\'(x) berubah dari POSITIF (+) ke NEGATIF (-) saat melewati x*, terbukti P(x*) adalah MAKSIMUM MUTLAK.' if res['is_max'] else 'Tidak terjadi perubahan tanda (+) ke (-) di dalam interior (0, x_max); ekstrem berada di batas domain.'}

3. Evaluasi Nilai Maksimum, Minimum, & Titik Impas (BEP: P(x) = 0):
   * Nilai Maksimum Mutlak : P({q_opt:.2f}) = Rp {p_opt:,.0f}/hari  (Omzet R = Rp {r_opt:,.0f}, Biaya C = Rp {c_opt:,.0f})
   * Nilai Minimum Awal    : P(0) = -Rp {c:,.0f}/hari
   * Nilai Ujung Domain    : P({self.q_max}) = Rp {(-a*(self.q_max**2) + alpha*self.q_max - c):,.0f}/hari
   * Diskriminan BEP       : D = ({alpha:,.0f})² - 4({a})({c:,.0f}) = {res['D']:,.0f}
{bep_block}

----------------------------------------------------------------------------------------
III. BIAYA VARIABEL TOTAL VC(x*) VIA SUBSTITUSI u + UBAH BATAS (POLA PDF B.1 & A.1)
----------------------------------------------------------------------------------------
Menghitung VC(x*) = ∫[0..{b1['q_hi']:.2f}] ({2*a:.0f}x + {b:,.0f}) dx:
   misal : u = {2*a:.0f}x + {b:,.0f}  ==>  du = {2*a:.0f} dx  ==>  dx = (1/{2*a:.0f}) du
   Ubah batas integrasi:
   * Jika x = 0,       maka u = {b1['u_lo']:,.0f}
   * Jika x = {b1['q_hi']:.2f}, maka u = {2*a:.0f}({b1['q_hi']:.2f}) + {b:,.0f} = {b1['u_hi']:,.0f}
   subs  = (1/{2*a:.0f}) ∫[{b1['u_lo']:,.0f}..{b1['u_hi']:,.0f}] u du
         = [ u² / {4*a:.0f} ]_{b1['u_lo']:,.0f}^{b1['u_hi']:,.0f}
         = Rp {b1['vc_substitusi']:,.0f}   (sama persis dengan {a}({b1['q_hi']:.2f})² + {b:,.0f}({b1['q_hi']:.2f}) = Rp {b1['vc_langsung']:,.0f})

----------------------------------------------------------------------------------------
IV. INTEGRAL BIAYA RATA-RATA AC(x) VIA PECAH POLINOM & ln|x| (POLA PDF A.3)
----------------------------------------------------------------------------------------
   AC(x) = C(x) / x = ({a}x² + {b:,.0f}x + {c:,.0f}) / x = {a}x + {b:,.0f} + {c:,.0f}/x
   ∫[{a3['q1']:.0f}..{a3['q2']:.0f}] AC(x) dx = ∫[{a3['q1']:.0f}..{a3['q2']:.0f}] {a}x dx + ∫[{a3['q1']:.0f}..{a3['q2']:.0f}] {b:,.0f} dx + ∫[{a3['q1']:.0f}..{a3['q2']:.0f}] ({c:,.0f}/x) dx
   = [ ({a}/2)x² + {b:,.0f}x + {c:,.0f} ln|x| ]_{a3['q1']:.0f}^{a3['q2']:.0f}
   = Rp {a3['integral_ac']:,.0f}   ==>   Rata-rata AC(x) pada [{a3['q1']:.0f}, {a3['q2']:.0f}] = Rp {a3['rata_rata_ac']:,.0f}/porsi

----------------------------------------------------------------------------------------
V. INTEGRAL NILAI MUTLAK LINIER |P'(x)| (POLA PDF B.3: ∫ |x - 4| dx)
----------------------------------------------------------------------------------------
   ∫[0..{self.q_max}] |P'(x)| dx = ∫[0..{self.q_max}] |-{2*a:.0f}x + {alpha:,.0f}| dx
   Pembuat nol P'(x) = 0 di x = {q_opt:.2f} (split pada x = {b3['q_split']:.2f}):
   * 0 <= x <= {b3['q_split']:.2f}  : P'(x) >= 0  ==>  ∫ P'(x) dx  = Rp {b3['kenaikan_laba']:,.0f}  (Kenaikan laba menuju puncak)
   * {b3['q_split']:.2f} <= x <= {self.q_max}: P'(x) < 0   ==>  ∫ -P'(x) dx = Rp {b3['pengikisan_laba']:,.0f}  (Pemborosan over-produksi)
   * Total Integral Mutlak = Rp {b3['total_eksak']:,.0f}

----------------------------------------------------------------------------------------
VI. INTEGRAL NILAI MUTLAK KUADRAT |P(x)| (POLA PDF B.4: ∫ |x² - 3x - 4| dx)
----------------------------------------------------------------------------------------
   ∫[0..{self.q_max}] |P(x)| dx = ∫[0..{self.q_max}] |-{a}x² + {alpha:,.0f}x - {c:,.0f}| dx
{sub_txt}
   * Total Area Surplus Laba (+) = Rp {b4['area_laba']:,.0f}  |  Total Area Defisit (-) = Rp {b4['area_rugi']:,.0f}
   * Total Integral Mutlak ∫|P(x)| dx = Rp {b4['total_mutlak_eksak']:,.0f}
   * Integral Netto ∫ P(x) dx = Rp {b4['integral_netto']:,.0f}  |  Rata-Rata Laba Domain = Rp {b4['rata_laba_domain']:,.0f}/hari

----------------------------------------------------------------------------------------
VII. INTEGRAL TRIGONOMETRI 30 HARI (POLA PDF A.4/B.2) & LIMIT L'HÔPITAL (POLA PDF B.5)
----------------------------------------------------------------------------------------
   * Proyeksi Laba {a4['hari']} Hari L(t) = P* + ΔP(½ sin(ωt) + sin(2ωt)), u = 2ωt:
     ∫[0..{a4['hari']}] L(t) dt = Rp {a4['laba_bulanan_musiman']:,.0f} (vs datar 30×P* = Rp {a4['laba_bulanan_datar']:,.0f})
   * Limit Startup (FTC I + L'Hôpital):
     lim[x->0] (1/x) ∫[0..x] MC(t) dt = lim[x->0] (2ax + b)/1 = Rp {b5['limit_eksak']:,.0f}/porsi
"""
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

        if mode == "Kurva Keuntungan P(x)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, f"Fungsi Keuntungan P(x) = -{a}x² + {p-b:,.0f}x - {c:,.0f}",
                       "Jumlah Porsi Produksi per Hari (x)", "Nilai Fungsi Keuntungan P(x) (Rp)")

            ax.plot(q_arr, profit_arr, color="#10b981", linewidth=2.5, label="Fungsi Keuntungan P(x) = R(x) - C(x)")
            ax.axhline(0, color="#ef4444" if not is_dark else "#f87171", linestyle=":", linewidth=1.5, label="Garis Impas (P(x) = 0)")

            ax.fill_between(q_arr, profit_arr, 0, where=(profit_arr >= 0), color="#10b981", alpha=0.15, label="Zona Untung (P(x) >= 0)")
            ax.fill_between(q_arr, profit_arr, 0, where=(profit_arr < 0), color="#ef4444", alpha=0.15, label="Zona Rugi (P(x) < 0)")

            if 0 <= q_opt <= self.q_max:
                ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, alpha=0.8)
                ax.scatter([q_opt], [p_opt], color="#f59e0b", s=90, zorder=5, label=f"Titik Kritis x*: ({q_opt:.1f} porsi, P(x*)=Rp {p_opt:,.0f})")
                ax.annotate(
                    f"TITIK KRITIS (NILAI MAKSIMUM):\nx* = {q_opt:.1f} porsi | P'(x*) = 0\nP(x*) = Rp {p_opt:,.0f} (Maks Global)",
                    xy=(q_opt, p_opt),
                    xytext=(q_opt + 6, p_opt * 0.85),
                    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9, fontweight="bold", color=text_color,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#f59e0b", alpha=0.9)
                )

            ax.scatter([0], [-c], color="#ef4444", s=70, zorder=5, label=f"Nilai Min: (0, -Rp {c:,.0f})")
            ax.annotate(f"NILAI MINIMUM:\nP(0) = -Rp {c:,.0f}", xy=(0, -c), xytext=(3, -c * 0.80),
                        fontsize=8, color="#ef4444", fontweight="bold")

            if q_bep1 and 0 <= q_bep1 <= self.q_max:
                ax.scatter([q_bep1], [0], color="#60a5fa", s=60, zorder=5)
                ax.annotate(f"BEP 1: {q_bep1:.1f}\nP(x)=0", xy=(q_bep1, 0), xytext=(q_bep1 - 14, p_opt * 0.15),
                            fontsize=8, color="#60a5fa", fontweight="bold")
            if q_bep2 and 0 <= q_bep2 <= self.q_max:
                ax.scatter([q_bep2], [0], color="#60a5fa", s=60, zorder=5)
                ax.annotate(f"BEP 2: {q_bep2:.1f}\nP(x)=0", xy=(q_bep2, 0), xytext=(q_bep2 - 12, p_opt * 0.15),
                            fontsize=8, color="#60a5fa", fontweight="bold")

            ax.scatter([slider_q], [slider_p], color="#ec4899", s=70, zorder=6)
            ax.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1.2, alpha=0.7)

            ax.legend(loc="upper right", framealpha=0.85, facecolor=bg_color, labelcolor=text_color, fontsize=8)
            create_hover_elements(ax, "profit")

        elif mode == "Pendapatan R(x) vs Biaya C(x)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, "Perbandingan Pendapatan Total R(x) vs Total Biaya C(x)",
                       "Jumlah Porsi Produksi per Hari (x)", "Rupiah (Rp)")

            ax.plot(q_arr, r_arr, color="#3b82f6", linewidth=2.5, label=f"Pendapatan R(x) = {p:,.0f}x")
            ax.plot(q_arr, c_arr, color="#ef4444", linewidth=2.5, label=f"Biaya Total C(x) = {a}x² + {b:,.0f}x + {c:,.0f}")

            if 0 <= q_opt <= self.q_max:
                ax.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linestyle="-", linewidth=3,
                        label=f"Gap Keuntungan Max: Rp {p_opt:,.0f}")
                ax.scatter([q_opt, q_opt], [c_opt, r_opt], color="#10b981", s=60, zorder=5)
                ax.annotate(
                    f"JARAK MAKSIMAL (R - C):\nx* = {q_opt:.1f} porsi\nLaba = Rp {p_opt:,.0f}",
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
                       "Jumlah Porsi Produksi per Hari (x)", "Rupiah per Porsi (Rp/porsi)")

            ax.plot(q_arr, mr_arr, color="#3b82f6", linewidth=2.5, label=f"Marginal Revenue: MR(x) = R'(x) = Rp {p:,.0f}")
            ax.plot(q_arr, mc_arr, color="#ef4444", linewidth=2.5, label=f"Marginal Cost: MC(x) = C'(x) = {2*a:.0f}x + {b:,.0f}")

            if 0 <= q_opt <= self.q_max:
                ax.scatter([q_opt], [p], color="#f59e0b", s=90, zorder=5, label=f"Titik MR = MC di x = {q_opt:.1f}")
                ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, alpha=0.8)
                ax.annotate(
                    f"KONDISI OPTIMUM (MR = MC):\nx* = {q_opt:.1f} porsi\nTarif Marjinal = Rp {p:,.0f}",
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

            style_axis(ax1, "Kurva Keuntungan P(x)", "Porsi (x)", "Keuntungan (Rp)")
            ax1.plot(q_arr, profit_arr, color="#10b981", linewidth=2)
            ax1.axhline(0, color="#ef4444", linestyle=":", linewidth=1)
            if 0 <= q_opt <= self.q_max:
                ax1.scatter([q_opt], [p_opt], color="#f59e0b", s=60, zorder=5)
                ax1.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1)
            ax1.scatter([slider_q], [slider_p], color="#ec4899", s=50, zorder=6)
            create_hover_elements(ax1, "profit")

            style_axis(ax2, "Pendapatan R(x) vs Biaya C(x)", "Porsi (x)", "Rupiah (Rp)")
            ax2.plot(q_arr, r_arr, color="#3b82f6", linewidth=2, label="R(x)")
            ax2.plot(q_arr, c_arr, color="#ef4444", linewidth=2, label="C(x)")
            if 0 <= q_opt <= self.q_max:
                ax2.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linewidth=2)
            ax2.legend(loc="upper left", fontsize=7, facecolor=bg_color, labelcolor=text_color)
            create_hover_elements(ax2, "rev_cost")

            style_axis(ax3, "Marjinal MR vs MC", "Porsi (x)", "Rp/porsi")
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
        p_opt = res["p_opt"]
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
            label_tag = "TITIK UJUNG DOMAIN x=0 (NILAI MINIMUM MUTLAK)"
            accent_col = "#ef4444"
        elif is_near_bep1:
            q = q_bep1
            label_tag = "TITIK IMPAS BAWAH (BEP 1: P(x) = 0)"
            accent_col = "#60a5fa"
        elif is_near_bep2:
            q = q_bep2
            label_tag = "TITIK IMPAS ATAS (BEP 2: P(x) = 0)"
            accent_col = "#60a5fa"
        elif is_near_slider:
            q = slider_q
            label_tag = "TITIK PORSI SIMULASI AKTIF"
            accent_col = "#ec4899"
        else:
            label_tag = "TITIK PENELUSURAN KURVA P(x)"
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
                    f"Titik Kritis x*: {q:.1f} porsi/hari (P'(x*) = 0)\n"
                    f"Nilai Maksimum P(x*): Rp {profit:,.0f}\n"
                    f"Fungsi Pendapatan R(x*): Rp {r:,.0f}\n"
                    f"Fungsi Biaya C(x*): Rp {cost:,.0f}\n"
                    f"Biaya Rata-Rata AC: Rp {ac:,.0f}/porsi\n"
                    f"Turunan Pertama P'(x*): Rp 0/porsi (Kondisi Stasioner)\n"
                    f"Uji Turunan Pertama: (+) P'({res['x_kiri']:g})>0 -> 0 -> (-) P'({res['x_kanan']:g})<0 (Maks)\n"
                    f"Nilai Minimum Global: P(0) = -Rp {c:,.0f}\n"
                    f"Status: Puncak Tertinggi Nilai Maksimum Global"
                ).replace(",", ".")
            elif is_near_zero:
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (x): 0,0 porsi/hari\n"
                    f"Nilai Minimum P(0): -Rp {c:,.0f} (Defisit Biaya Tetap)\n"
                    f"Fungsi Pendapatan R(0): Rp 0\n"
                    f"Biaya Total C(0): Rp {c:,.0f} (Fixed Cost)\n"
                    f"Turunan Pertama P'(0): +Rp {p - b:,.0f}/porsi (P' > 0)\n"
                    f"Status: Nilai Minimum Mutlak pada Domain [0, {self.q_max}]"
                ).replace(",", ".")
            elif is_near_bep1 or is_near_bep2:
                bep_name = "BEP 1 (Bawah)" if is_near_bep1 else "BEP 2 (Atas)"
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Impas ({bep_name}): {q:.1f} porsi/hari\n"
                    f"Nilai Fungsi P(x): Rp 0 (Pulang Pokok)\n"
                    f"Pendapatan = Biaya: Rp {r:,.0f}\n"
                    f"Turunan Pertama P'(x): Rp {p_prime:,.0f}/porsi\n"
                    f"Status: Ambang Batas Wilayah Keuntungan (P(x) = 0)"
                ).replace(",", ".")
            elif is_near_slider:
                diff_s = q - q_opt
                s_note = f"+{diff_s:.1f} porsi dari opt" if diff_s > 0 else (f"{diff_s:.1f} porsi dari opt" if diff_s < 0 else "Tepat di optimum")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Terpilih: {q:.1f} porsi/hari ({s_note})\n"
                    f"Fungsi Keuntungan P(x): Rp {profit:,.0f}\n"
                    f"Pendapatan Total R(x): Rp {r:,.0f}\n"
                    f"Biaya Total C(x): Rp {cost:,.0f}\n"
                    f"Turunan Pertama P'(x): Rp {p_prime:,.0f}/porsi\n"
                    f"Status: Posisi Slider Simulasi Interaktif"
                ).replace(",", ".")
            else:
                st_txt = "Zona Laba Positif (P(x) > 0)" if profit > 0 else ("Titik Impas (P(x) = 0)" if abs(profit) < 1 else "Zona Rugi Defisit (P(x) < 0)")
                rec_txt = "Tambah porsi (P'(x) > 0)" if p_prime > 50 else ("Kurangi porsi (P'(x) < 0)" if p_prime < -50 else "Puncak laba (P'(x) = 0)")
                uji1_txt = "Monoton Naik (P'(x) > 0, kiri x*)" if p_prime > 1e-6 else ("Monoton Turun (P'(x) < 0, kanan x*)" if p_prime < -1e-6 else "Titik Balik Stasioner (P'(x) = 0)")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (x): {q:.1f} porsi/hari\n"
                    f"Fungsi Keuntungan P(x): Rp {profit:,.0f}\n"
                    f"Pendapatan Total R(x): Rp {r:,.0f}\n"
                    f"Biaya Total C(x): Rp {cost:,.0f}\n"
                    f"Biaya Rata-Rata AC(x): Rp {ac:,.0f}/porsi\n"
                    f"Turunan Pertama P'(x): Rp {p_prime:,.0f}/porsi\n"
                    f"Uji Turunan Pertama: {uji1_txt}\n"
                    f"Titik Kritis x*: {q_opt:.1f} | Nilai Maks: Rp {p_opt:,.0f}\n"
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
                    f"Porsi Optimum (x*): {q:.1f} porsi/hari\n"
                    f"Pendapatan Total R(x*): Rp {r:,.0f}\n"
                    f"Biaya Total C(x*): Rp {cost:,.0f}\n"
                    f"Gap Laba Maksimum (R - C): Rp {gap:,.0f}\n"
                    f"Kemiringan Kurva: R' = C' = Rp {p:,.0f}\n"
                    f"Biaya Tetap FC: Rp {c:,.0f}\n"
                    f"Biaya Variabel VC: Rp {a*(q**2) + b*q:,.0f}\n"
                    f"Status: Celah Vertikal R(x) - C(x) Terbesar"
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
                    f"Pendapatan Total R(x): Rp {r:,.0f}\n"
                    f"Biaya Total C(x): Rp {cost:,.0f}\n"
                    f"Celah Keuntungan: Rp {gap:,.0f}\n"
                    f"Status: Posisi Slider Pada R(x) dan C(x)"
                ).replace(",", ".")
            else:
                st_rc = "Laba (R > C)" if gap > 0 else ("Impas (R = C)" if abs(gap) < 1 else "Rugi (C > R)")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (x): {q:.1f} porsi/hari\n"
                    f"Pendapatan R(x): Rp {r:,.0f}\n"
                    f"Biaya Total C(x): Rp {cost:,.0f}\n"
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
                    f"Porsi Optimum (x*): {q:.1f} porsi/hari\n"
                    f"Marginal Revenue MR: Rp {mr:,.0f}/porsi\n"
                    f"Marginal Cost MC: Rp {mc:,.0f}/porsi\n"
                    f"Laba Marjinal P'(x*): Rp 0/porsi\n"
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
                    f"Porsi Produksi (x): {q:.1f} porsi/hari\n"
                    f"Marginal Revenue MR: Rp {mr:,.0f}/porsi\n"
                    f"Marginal Cost MC: Rp {mc:,.0f}/porsi\n"
                    f"Laju Laba P'(x): Rp {diff:,.0f}/porsi\n"
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
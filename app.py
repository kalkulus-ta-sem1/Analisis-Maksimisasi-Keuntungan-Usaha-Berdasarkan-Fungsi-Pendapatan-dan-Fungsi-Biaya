import io
import sys
import os
import math
from typing import Any, Literal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import customtkinter as ctk

AnchorType = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]

from src.tasik_market_data import (
    KATALOG_KOMODITAS_TASIK,
    KONDISI_PASAR_CONFIG,
    WILAYAH_CONFIG,
    hitung_estimasi_umkm,
)
from src.kalkulus_integral import (
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
                "c": 14500.0,
                "b": 6700.0,
                "a": 60.0,
                "q_max": 140
            },
            "UMKM Warung Nasi Goreng": {
                "p": 18000.0,
                "c": 17500.0,
                "b": 8200.0,
                "a": 50.0,
                "q_max": 200
            },
            "UMKM Kopi Susu Kekinian": {
                "p": 22000.0,
                "c": 21000.0,
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
                "c": 14500.0,
                "b": 6700.0,
                "a": 60.0,
                "q_max": 140
            }
        }

        self.p: float = 15000.0
        self.c: float = 14500.0
        self.b: float = 6700.0
        self.a: float = 60.0
        self.q_max: int = 140
        self.slider_q: float = 69.0
        self.sidebar_width = 380
        self._syncing_from_p = False
        self._last_p_text = "15000"
        self._price_debounce_id = None
        self._pending_price_autofill = False
        self._manual_override = False
        self._last_hover_q: float | None = None
        self._last_hover_ax: Any = None
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
        self._math_cache: dict[tuple, ctk.CTkImage] = {}
        self._paper_desks: list[ctk.CTkScrollableFrame] = []
        self._reporting_callback_err = False

        self._setup_layout()
        self._calculate_calculus_model()
        self._update_all_views()

    def report_callback_exception(self, exc, val, tb):
        import traceback
        traceback.print_exception(exc, val, tb, file=sys.stderr)
        if not self._reporting_callback_err:
            self._reporting_callback_err = True
            try:
                messagebox.showerror(
                    "Kesalahan Aplikasi",
                    f"Terjadi kesalahan saat memproses aksi:\n{val}",
                )
            except Exception:
                pass
            finally:
                self._reporting_callback_err = False

    def destroy(self):
        if getattr(self, "_price_debounce_id", None) is not None:
            try:
                self.after_cancel(self._price_debounce_id)
            except Exception:
                pass
            self._price_debounce_id = None
        super().destroy()

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
            ("c", "Biaya Tetap Harian (c / FC)", "Pecahan per hari: sewa/30hr, LPG/5-6hr, listrik/30hr, alat", "14500"),
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
            text="Fungsi Laba f(x): Rp 254.040",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            wraplength=calc_w,
            justify="left"
        )
        self.live_profit_lbl.pack(anchor="w", padx=10, pady=2)

        self.live_mp_lbl = ctk.CTkLabel(
            self.live_card,
            text="Laju Laba f'(x): Rp 0/porsi",
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

        self.card_q_opt = self._make_metric_card(self.summary_bar, 0, "Titik Kritis (x*)", "69,2 porsi", "Syarat Stasioner f'(x) = 0", "#3b82f6")
        self.card_profit_max = self._make_metric_card(self.summary_bar, 1, "Nilai Maksimum f(x*)", "Rp 254.042", "Laba harian puncak mutlak", "#10b981")
        self.card_bep = self._make_metric_card(self.summary_bar, 2, "Nilai Minimum & BEP", "-Rp 33.000", "Batas rentang laba f(x) >= 0", "#f59e0b")
        self.card_test1 = self._make_metric_card(self.summary_bar, 3, "Uji Turunan Pertama", "f'(x): (+) -> 0 -> (-)", "Kiri naik, kanan turun (Maks)", "#8b5cf6")

    def _make_metric_card(self, parent, col, title, value, subtitle, accent_color):
        card = ctk.CTkFrame(parent, fg_color=("gray90", "#1e1e24"), corner_radius=8, border_width=1, border_color=("gray75", "#334155"))
        card.grid(row=0, column=col, padx=5, pady=2, sticky="nsew")

        t_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray30", "gray70"))
        t_lbl.pack(anchor="w", padx=10, pady=(10, 0))

        v_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=15, weight="bold"), text_color=accent_color)
        v_lbl.pack(anchor="w", padx=10, pady=(1, 0))

        s_lbl = ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(size=9), text_color=("gray40", "gray60"))
        s_lbl.pack(anchor="w", padx=10, pady=(0, 8))

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
                "Kurva Keuntungan f(x)",
                "Pendapatan R(x) vs Biaya C(x)",
                "Pendekatan Marjinal (MR vs MC)",
                "Multi-Grafik (3-in-1 Dashboard)"
            ],
            command=self._on_graph_mode_change
        )
        self.graph_mode.set("Kurva Keuntungan f(x)")
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

    def _paper_desk_color(self) -> tuple[str, str]:
        return ("#e2e8f0", "#0f172a")

    def _create_paper_sheet_frame(self, parent_grid, row: int, max_w: int = 720, inner_w: int = 640) -> ctk.CTkFrame:
        parent_grid.grid_columnconfigure(0, weight=1)
        paper_card = ctk.CTkFrame(
            parent_grid,
            fg_color="#ffffff",
            corner_radius=10,
            border_width=1,
            border_color="#cbd5e1",
            width=max_w,
        )
        paper_card.grid(row=row, column=0, padx=18, pady=16, sticky="n")
        body = ctk.CTkFrame(paper_card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=26, pady=22)
        setattr(body, "_paper_inner_w", inner_w)
        ctk.CTkFrame(body, width=inner_w, height=1, fg_color="transparent").pack(fill="x")
        return body

    @staticmethod
    def _clear_paper_body(body: ctk.CTkFrame):
        for child in list(body.winfo_children()):
            child.destroy()
        inner_w = getattr(body, "_paper_inner_w", 640)
        ctk.CTkFrame(body, width=inner_w, height=1, fg_color="transparent").pack(fill="x")

    def _render_math_image(self, lines: list[str], bg: str = "#f8fafc", fg: str = "#0f172a", fontsize: float = 11.0, max_w: int = 595) -> ctk.CTkImage:
        key = (tuple(lines), bg, fg, fontsize, max_w)
        if key in self._math_cache:
            return self._math_cache[key]

        n = max(1, len(lines))
        buf = None
        try:
            fig = Figure(figsize=(6.8, max(0.55, 0.45 * n)), dpi=118)
            fig.patch.set_facecolor(bg)
            FigureCanvasAgg(fig)
            for idx, line in enumerate(lines):
                y = 1.0 - (idx + 0.5) / n
                fig.text(
                    0.01, y, line, fontsize=fontsize, va="center", ha="left",
                    color=fg, fontfamily="Times New Roman", math_fontfamily="stix"
                )

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=118, bbox_inches="tight", pad_inches=0.08, facecolor=bg)
            buf.seek(0)
            pil_img = Image.open(buf).copy()
        except Exception:
            fallback_txt = "\n".join(line.replace("$", "") for line in lines) or "-"
            pil_img = Image.new("RGB", (max_w, max(44, 24 * n + 14)), bg)
            draw = ImageDraw.Draw(pil_img)
            draw.multiline_text((8, 6), fallback_txt, fill=fg, font=ImageFont.load_default(), spacing=6)
        finally:
            if buf is not None:
                buf.close()

        w, h = pil_img.size
        if w > max_w:
            scale = max_w / float(w)
            disp_w, disp_h = max_w, max(1, int(round(h * scale)))
        else:
            disp_w, disp_h = w, h

        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(disp_w, disp_h))
        if len(self._math_cache) >= 160:
            self._math_cache.clear()
        self._math_cache[key] = ctk_img
        return ctk_img

    def _add_paper_header(self, body: ctk.CTkFrame, title: str, subtitle: str, chips: list[str] | None = None):
        ctk.CTkLabel(
            body, text=title, font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"),
            text_color="#0f172a", justify="left", anchor="w", wraplength=625
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            body, text=subtitle, font=ctk.CTkFont(family="Times New Roman", size=12),
            text_color="#475569", justify="left", anchor="w", wraplength=625
        ).pack(anchor="w", pady=(0, 10))

        if chips:
            chip_row = ctk.CTkFrame(body, fg_color="transparent")
            chip_row.pack(anchor="w", fill="x", pady=(0, 8))
            for ch in chips:
                pill = ctk.CTkFrame(chip_row, fg_color="#eff6ff", corner_radius=6, border_width=1, border_color="#bfdbfe")
                pill.pack(side="left", padx=(0, 5), pady=2)
                ctk.CTkLabel(
                    pill, text=ch, font=ctk.CTkFont(family="Times New Roman", size=10, weight="bold"),
                    text_color="#1e40af"
                ).pack(padx=7, pady=3)

        ctk.CTkFrame(body, width=10, height=2, fg_color="#1e3a8a").pack(fill="x", pady=(2, 12))

    def _add_math_box(self, body: ctk.CTkFrame, lines: list[str], bg: str = "#f8fafc", accent: str = "#2563eb", fontsize: float = 11.0):
        box = ctk.CTkFrame(body, fg_color=bg, corner_radius=6, border_width=1, border_color="#cbd5e1", height=10)
        box.pack(fill="x", pady=(4, 10))
        img = self._render_math_image(lines, bg=bg, fontsize=fontsize)
        lbl = ctk.CTkLabel(box, text="", image=img, anchor="w")
        lbl.pack(side="left", padx=14, pady=8)

    def _add_callout_box(self, body: ctk.CTkFrame, title: str, text: str, tone: str = "slate"):
        palette = {
            "emerald": ("#ecfdf5", "#6ee7b7", "#065f46", "#064e3b"),
            "amber": ("#fffbeb", "#fcd34d", "#92400e", "#78350f"),
            "blue": ("#eff6ff", "#93c5fd", "#1e40af", "#1e3a8a"),
            "slate": ("#f1f5f9", "#cbd5e1", "#0f172a", "#334155"),
        }
        bg, brd, t_col, b_col = palette.get(tone, palette["slate"])
        card = ctk.CTkFrame(body, fg_color=bg, corner_radius=6, border_width=1, border_color=brd, height=10)
        card.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(family="Times New Roman", size=12, weight="bold"),
            text_color=t_col, anchor="w", justify="left", wraplength=605
        ).pack(anchor="w", padx=12, pady=(8, 2))
        ctk.CTkLabel(
            card, text=text, font=ctk.CTkFont(family="Times New Roman", size=12),
            text_color=b_col, anchor="w", justify="left", wraplength=605
        ).pack(anchor="w", padx=12, pady=(0, 8))

    def _add_paper_section(
        self,
        body: ctk.CTkFrame,
        heading: str,
        prose: str | None = None,
        math_lines: list[str] | None = None,
        bullets: list[str] | None = None,
        callout: dict[str, str] | None = None,
        accent: str = "#1e3a8a",
    ):
        sec = ctk.CTkFrame(body, fg_color="transparent")
        sec.pack(fill="x", pady=(4, 12))
        ctk.CTkLabel(
            sec, text=heading, font=ctk.CTkFont(family="Times New Roman", size=14, weight="bold"),
            text_color=accent, anchor="w", justify="left", wraplength=625
        ).pack(anchor="w", pady=(0, 2))
        ctk.CTkFrame(sec, width=10, height=1, fg_color="#cbd5e1").pack(fill="x", pady=(3, 8))

        if prose:
            ctk.CTkLabel(
                sec, text=prose, font=ctk.CTkFont(family="Times New Roman", size=12),
                text_color="#1e293b", anchor="w", justify="left", wraplength=625
            ).pack(anchor="w", pady=(0, 6))

        if math_lines:
            self._add_math_box(sec, math_lines, accent=accent)

        if bullets:
            for item in bullets:
                ctk.CTkLabel(
                    sec, text=f"•  {item}", font=ctk.CTkFont(family="Times New Roman", size=12),
                    text_color="#334155", anchor="w", justify="left", wraplength=610
                ).pack(anchor="w", padx=(8, 0), pady=2)

        if callout:
            self._add_callout_box(sec, callout["title"], callout["text"], callout.get("tone", "slate"))

    def _setup_tab_kalkulus(self):
        self.tab_kalkulus.grid_rowconfigure(0, weight=1)
        self.tab_kalkulus.grid_columnconfigure(0, weight=1)

        self.calc_scroll = ctk.CTkScrollableFrame(self.tab_kalkulus, fg_color=self._paper_desk_color())
        self.calc_scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self._paper_desks.append(self.calc_scroll)
        self.calc_paper_body = self._create_paper_sheet_frame(self.calc_scroll, row=0)

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
        self.int_umkm_scroll = ctk.CTkScrollableFrame(self.int_container, fg_color=self._paper_desk_color())
        self.int_umkm_scroll.grid(row=0, column=0, sticky="nsew")
        self.int_umkm_scroll.grid_columnconfigure(0, weight=1)
        self._paper_desks.append(self.int_umkm_scroll)

        umkm_plot_box = ctk.CTkFrame(self.int_umkm_scroll, fg_color=("gray95", "#18181b"), corner_radius=8)
        umkm_plot_box.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 8))
        umkm_plot_box.grid_columnconfigure(0, weight=1)

        self.int_umkm_fig = Figure(figsize=(8.6, 5.2), dpi=96)
        self.int_umkm_canvas = FigureCanvasTkAgg(self.int_umkm_fig, master=umkm_plot_box)
        self.int_umkm_canvas.get_tk_widget().grid(row=0, column=0, sticky="ew")

        self.int_umkm_paper_body = self._create_paper_sheet_frame(self.int_umkm_scroll, row=1)

        # Panel 2: Kalkulator & Verifikator 10 Soal Rumus PDF (A.1-A.5 & B.1-B.5)
        self.int_pdf_frame = ctk.CTkScrollableFrame(self.int_container, fg_color=self._paper_desk_color())
        self.int_pdf_frame.grid(row=0, column=0, sticky="nsew")
        self.int_pdf_frame.grid_columnconfigure(0, weight=1)
        self._paper_desks.append(self.int_pdf_frame)

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

        self.int_pdf_paper_body = self._create_paper_sheet_frame(self.int_pdf_frame, row=1)

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

        col_configs: list[tuple[str, str, int, AnchorType]] = [
            ("q", "Porsi (x)", 75, "center"),
            ("R", "Pendapatan R(x)", 125, "e"),
            ("C", "Total Biaya C(x)", 125, "e"),
            ("P", "Keuntungan f(x)", 125, "e"),
            ("AC", "Biaya Rata2 AC(x)", 120, "e"),
            ("MR", "Marginal Rev (MR)", 115, "e"),
            ("MC", "Marginal Cost (MC)", 115, "e"),
            ("P_prime", "Laju Laba f'(x)", 115, "e"),
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

        self.lap_scroll = ctk.CTkScrollableFrame(self.tab_laporan, fg_color=self._paper_desk_color())
        self.lap_scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self._paper_desks.append(self.lap_scroll)
        paper = self._create_paper_sheet_frame(self.lap_scroll, row=0)

        cover = ctk.CTkFrame(paper, fg_color="transparent")
        cover.pack(fill="x", pady=(4, 10))
        ctk.CTkLabel(
            cover,
            text="LAPORAN AKHIR",
            font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"),
            text_color="#0f172a",
            justify="center",
        ).pack(anchor="center", pady=(0, 6))
        ctk.CTkLabel(
            cover,
            text="ANALISIS MAKSIMISASI KEUNTUNGAN USAHA BERDASARKAN\nFUNGSI PENDAPATAN DAN FUNGSI BIAYA",
            font=ctk.CTkFont(family="Times New Roman", size=14, weight="bold"),
            text_color="#1e3a8a",
            justify="center",
            wraplength=610,
        ).pack(anchor="center", pady=(0, 6))
        ctk.CTkLabel(
            cover,
            text="Disusun untuk Memenuhi Salah Satu Tugas Mata Kuliah Kalkulus Dasar",
            font=ctk.CTkFont(family="Times New Roman", size=11, slant="italic"),
            text_color="#475569",
            justify="center",
            wraplength=610,
        ).pack(anchor="center", pady=(0, 14))

        ctk.CTkLabel(
            cover,
            text="Dosen Pengampu:",
            font=ctk.CTkFont(family="Times New Roman", size=12),
            text_color="#334155",
            justify="center",
        ).pack(anchor="center")
        ctk.CTkLabel(
            cover,
            text="Neng Ika Kurniati, S.Si., M.Cs.",
            font=ctk.CTkFont(family="Times New Roman", size=12, weight="bold"),
            text_color="#0f172a",
            justify="center",
        ).pack(anchor="center", pady=(2, 14))

        ctk.CTkLabel(
            cover,
            text="Disusun Oleh:\nKelompok 3",
            font=ctk.CTkFont(family="Times New Roman", size=12, weight="bold"),
            text_color="#0f172a",
            justify="center",
        ).pack(anchor="center", pady=(0, 8))

        members_box = ctk.CTkFrame(
            cover,
            fg_color="#f8fafc",
            corner_radius=6,
            border_width=1,
            border_color="#cbd5e1",
            height=10,
        )
        members_box.pack(anchor="center", pady=(0, 16))
        members = [
            ("1.", "Muhammad Fikri Haikal", "267006111030"),
            ("2.", "Muhammad Amin Al Faruq", "267006111104"),
            ("3.", "Hirzan Khairurrizal Ahza", "267006111168"),
            ("4.", "Fahri Fauzira", "267006111171"),
            ("5.", "Mochammad Fauzan Rizaldy", "267006111173"),
            ("6.", "Anindi Nurmaleka", "267006111176"),
        ]
        for r_idx, (no_s, nama_s, npm_s) in enumerate(members):
            top_pad = 8 if r_idx == 0 else 2
            bot_pad = 8 if r_idx == len(members) - 1 else 2
            ctk.CTkLabel(
                members_box,
                text=no_s,
                font=ctk.CTkFont(family="Times New Roman", size=12),
                text_color="#0f172a",
                width=24,
                anchor="w",
            ).grid(row=r_idx, column=0, padx=(16, 4), pady=(top_pad, bot_pad), sticky="w")
            ctk.CTkLabel(
                members_box,
                text=nama_s,
                font=ctk.CTkFont(family="Times New Roman", size=12),
                text_color="#0f172a",
                width=230,
                anchor="w",
            ).grid(row=r_idx, column=1, padx=(0, 18), pady=(top_pad, bot_pad), sticky="w")
            ctk.CTkLabel(
                members_box,
                text=npm_s,
                font=ctk.CTkFont(family="Times New Roman", size=12),
                text_color="#1e3a8a",
                width=115,
                anchor="e",
            ).grid(row=r_idx, column=2, padx=(0, 16), pady=(top_pad, bot_pad), sticky="e")

        ctk.CTkLabel(
            cover,
            text="PROGRAM STUDI INFORMATIKA\nFAKULTAS TEKNIK\nUNIVERSITAS SILIWANGI\nTASIKMALAYA\n2026",
            font=ctk.CTkFont(family="Times New Roman", size=12, weight="bold"),
            text_color="#0f172a",
            justify="center",
        ).pack(anchor="center", pady=(0, 8))

        ctk.CTkFrame(paper, width=10, height=2, fg_color="#1e3a8a").pack(fill="x", pady=(6, 14))

        self._add_paper_section(
            paper,
            "1. Abstrak & Latar Belakang",
            prose=(
                "Usaha Mikro, Kecil, dan Menengah (UMKM) makanan menghadapi tantangan dalam menentukan jumlah porsi harian "
                "yang paling menguntungkan. Menambah produksi berpotensi menaikkan pendapatan, namun sekaligus memicu kenaikan "
                "biaya marjinal yang lebih cepat (disekonomi skala) akibat kelelahan kerja, lembur, serta pembelian bahan baku "
                "tambahan secara mendadak dengan harga eceran.\n\n"
                "Studi ini memodelkan hubungan antara porsi produksi (x), fungsi pendapatan R(x), fungsi biaya total C(x), "
                "dan fungsi keuntungan f(x) menggunakan turunan pertama, titik kritis, uji turunan pertama, serta penerapan integral "
                "(substitusi u, nilai mutlak, pecah polinom ln|x|, integral trigonometri, dan Teorema Dasar Kalkulus I)."
            ),
        )

        self._add_paper_section(
            paper,
            "2. Pemodelan Matematika Kalkulus (Studi Kasus Awal)",
            prose="Dengan variabel keputusan x >= 0 (jumlah porsi ketoprak/hari), harga jual p = Rp 15.000, biaya tetap c = Rp 60.000, biaya variabel b = Rp 8.000, dan disekonomi kuadrat a = 50:",
            math_lines=[
                r"$\mathrm{1.\ Pendapatan\ Total:}\quad R(x) = \int_0^x 15.000\,dt = 15.000x$",
                r"$\mathrm{2.\ Biaya\ Total:}\quad C(x) = 60.000 + \int_0^x (100t + 8.000)\,dt = 50x^2 + 8.000x + 60.000$",
                r"$\mathrm{3.\ Fungsi\ Keuntungan:}\quad f(x) = R(x) - C(x) = -50x^2 + 7.000x - 60.000$",
            ],
        )

        self._add_paper_section(
            paper,
            "3. Turunan Pertama, Titik Kritis, & Uji Turunan Pertama",
            prose="Turunan pertama f'(x) menyatakan Laba Marjinal (MR - MC). Titik kritis stasioner dicapai saat f'(x) = 0:",
            math_lines=[
                r"$f'(x) = \frac{d}{dx}\left(-50x^2 + 7.000x - 60.000\right) = -100x + 7.000$",
                r"$f'(x) = 0 \ \Rightarrow\ -100x + 7.000 = 0 \ \Rightarrow\ x^* = 70\ \mathrm{porsi/hari}$",
            ],
            bullets=[
                "Uji interval kiri (0 <= x < 70, uji x = 60): f'(60) = +1.000 > 0 (kurva naik).",
                "Titik kritis x* = 70: f'(70) = 0 (stasioner, MR = MC = Rp 15.000).",
                "Uji interval kanan (x > 70, uji x = 80): f'(80) = -1.000 < 0 (kurva turun).",
                "BEP (f(x) = 0): x_BEP1 = 9,17 porsi dan x_BEP2 = 130,83 porsi (rentang untung 10 s.d. 130 porsi/hari).",
            ],
            callout={
                "title": "Kesimpulan Teorema Nilai Ekstrem pada [0, 140]",
                "text": "Nilai Maksimum Mutlak: f(70) = Rp 185.000/hari (Omzet Rp 1.050.000, Biaya Rp 865.000)  |  Nilai Minimum Mutlak: f(0) = f(140) = -Rp 60.000/hari.",
                "tone": "emerald",
            },
        )

        self._add_paper_section(
            paper,
            "4. Integrasi Rumus PDF (A.1-A.5 & B.1-B.5) & Interpretasi Manajerial",
            bullets=[
                "Pola B.3 & B.4: Integral nilai mutlak linier int |f'(x)| dx dan kuadrat int |f(x)| dx untuk total pergerakan laba serta rasio surplus vs defisit.",
                "Pola A.3: Integral biaya rata-rata AC(x) = (ax^2 + bx + c)/x menggunakan pemecahan pecahan polinom & ln|x|.",
                "Pola B.1 & A.1: Integral substitusi u + ubah batas untuk menghitung VC(x*) = (p^2 - b^2)/(4a).",
                "Pola A.4 & B.2: Integral trigonometri proyeksi akumulasi laba bulanan 30 hari dengan gelombang penjualan.",
                "Selama x < x* (MR > MC), menambah porsi meningkatkan total laba; saat x > x* (MR < MC), over-produksi justru memangkas laba.",
            ],
        )

        self._add_paper_section(
            paper,
            "5. Rekomendasi Strategis & Daftar Referensi",
            bullets=[
                "Targetkan produksi di sekitar titik optimum x* agar margin bersih harian maksimal tanpa kelelahan/over-produksi.",
                "Catat biaya tetap per hari secara terpisah dari modal bahan baku per porsi (pendekatan full costing).",
                "Referensi: Stewart (2016) Calculus 8th ed.; Nurwahidah & Mariani (2021) Jurnal MSA 9(1); Riani dkk. (2025) Jurnal Lentera Pengabdian 3(3); Azizah & Cahyani (2024) Kompeten 2(5).",
            ],
        )

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
        var_cols: list[tuple[str, str, int, AnchorType]] = [
            ("komponen", "Komponen Bahan / Kemasan", 205, "w"),
            ("takaran", "Takaran / Porsi", 185, "w"),
            ("subtotal", "Modal / Porsi", 105, "e"),
            ("rentang", "Naik-Turun (/Porsi)", 150, "center"),
            ("harian", "Belanja Harian (q*)", 165, "e"),
        ]
        for cid, cname, w, anc in var_cols:
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
        fixed_cols: list[tuple[str, str, int, AnchorType]] = [
            ("komponen", "Komponen Operasional Tetap", 200, "w"),
            ("basis", "Pemakaian Riil / Hari", 190, "w"),
            ("subtotal", "Biaya / Hari", 105, "e"),
            ("rentang", "Naik-Turun (/Hari)", 145, "center"),
            ("sumber", "Referensi Tarif Lokal", 185, "w"),
        ]
        for cid, cname, w, anc in fixed_cols:
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
        fluk_cols: list[tuple[str, str, int, AnchorType]] = [
            ("kondisi", "Kondisi Harga Pasar", 215, "w"),
            ("b_val", "Modal / Porsi (b)", 115, "e"),
            ("c_val", "Tetap / Hari (c)", 115, "e"),
            ("q_opt", "Target (q*)", 95, "center"),
            ("modal_harian", "Total Modal Harian", 140, "e"),
            ("laba_max", "Laba Bersih Maks/Hr", 145, "e"),
        ]
        for cid, cname, w, anc in fluk_cols:
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
        cat_cols: list[tuple[str, str, int, AnchorType]] = [
            ("kategori", "Kategori", 130, "w"),
            ("komoditas", "Komoditas / Item", 205, "w"),
            ("harga", "Acuan Utama", 130, "e"),
            ("kisaran", "Kisaran Pasar Lapangan", 215, "w"),
            ("sumber", "Sumber Pemantauan", 200, "w"),
        ]
        for cid, cname, w, anc in cat_cols:
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

        f_zero = -c
        f_end = -a * (float(self.q_max) ** 2) + alpha * float(self.q_max) - c
        if a > 0 and 0.0 < q_opt < float(self.q_max) and is_max:
            x_max_dom = q_opt
            f_max_dom = p_opt
        elif f_end > f_zero:
            x_max_dom = float(self.q_max)
            f_max_dom = f_end
        else:
            x_max_dom = 0.0
            f_max_dom = f_zero

        if abs(f_zero - f_end) < 1e-6:
            x_min = 0.0
            f_min = f_zero
            min_both_ends = True
        elif f_end < f_zero:
            x_min = float(self.q_max)
            f_min = f_end
            min_both_ends = False
        else:
            x_min = 0.0
            f_min = f_zero
            min_both_ends = False

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
            "f_zero": f_zero, "f_end": f_end,
            "x_max_dom": x_max_dom, "f_max_dom": f_max_dom,
            "x_min": x_min, "f_min": f_min, "min_both_ends": min_both_ends,
            "ac_opt": ac_opt, "margin_pct": margin_pct,
            "D": D, "q_bep1": q_bep1, "q_bep2": q_bep2
        }

    @staticmethod
    def _fmt_rp(val: float) -> str:
        if val < 0:
            return f"-Rp {abs(val):,.0f}".replace(",", ".")
        return f"Rp {val:,.0f}".replace(",", ".")

    @staticmethod
    def _fmt_num(val: float, decimals: int = 0) -> str:
        if decimals == 0:
            return f"{val:,.0f}".replace(",", ".")
        return f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _rp_axis_formatter() -> FuncFormatter:
        return FuncFormatter(lambda v, _pos: f"{v:,.0f}".replace(",", "."))

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
            try:
                self.tasik_breakdown = hitung_estimasi_umkm(
                    self.p, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
                )
            except Exception as err:
                messagebox.showerror("Gagal Hitung Pasar", f"Tidak dapat menghitung estimasi pasar: {err}")
                return
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

    def _on_price_change(self, event=None, immediate=False, force=False) -> bool:
        """Mengisi otomatis c, b, a, q_max harian (non-borongan) dari harga pasar Tasikmalaya saat p berubah."""
        if self._syncing_from_p:
            return False

        if immediate and self._price_debounce_id is not None:
            try:
                self.after_cancel(self._price_debounce_id)
            except Exception:
                pass
            self._price_debounce_id = None

        raw = self.entries["p"].get().strip()
        if not force and raw == self._last_p_text:
            return False

        p_baru = self._parse_number_input(raw)
        if p_baru is None or p_baru <= 0 or p_baru > 1e9:
            return False

        # Tahan eksekusi saat pengguna baru mengetik digit awal (mis. '2' atau '20' menuju '20000')
        if not immediate and not force and p_baru < 1000:
            return False

        if not self.auto_tasik_var.get():
            c_val = self._parse_number_input(self.entries["c"].get())
            b_val = self._parse_number_input(self.entries["b"].get())
            a_val = self._parse_number_input(self.entries["a"].get())
            q_val = self._parse_number_input(self.entries["q_max"].get())
            if (
                c_val is not None
                and b_val is not None
                and a_val is not None
                and q_val is not None
                and 0 < a_val <= 1e7
                and 0 <= b_val <= 1e9
                and 0 <= c_val <= 1e10
            ):
                self.c = c_val
                self.b = b_val
                self.a = a_val
                self.q_max = min(10000, max(20, int(round(q_val))))
            self.p = p_baru
            try:
                self.tasik_breakdown = hitung_estimasi_umkm(
                    self.p, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
                )
            except Exception as err:
                messagebox.showerror("Gagal Hitung Estimasi", f"Gagal menghitung estimasi pasar: {err}")
                return False
            self._last_p_text = raw
            self._pending_price_autofill = False
            self._sync_slider_and_views()
            return True

        try:
            estimasi = hitung_estimasi_umkm(
                p_baru, self.preset_menu.get(), self.wilayah, self.kondisi_pasar
            )
        except Exception as err:
            messagebox.showerror("Gagal Hitung Estimasi", f"Gagal menghitung estimasi pasar: {err}")
            return False

        self._last_p_text = raw
        self._pending_price_autofill = False

        c_baru = estimasi["c"]
        b_baru = estimasi["b"]
        a_baru = estimasi["a"]
        q_max_baru = min(10000, max(20, int(estimasi["q_max"])))

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
        return True

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
                self._pending_price_autofill = False
                self._on_click_calculate()
            elif self.auto_tasik_var.get():
                self._on_price_change(immediate=True, force=True)
            else:
                self._manual_override = False
                self._on_click_calculate()

    def _on_click_calculate(self):
        if self._pending_price_autofill and self.auto_tasik_var.get():
            if self._on_price_change(immediate=True, force=True):
                return

        try:
            p_val = self._parse_number_input(self.entries["p"].get())
            c_val = self._parse_number_input(self.entries["c"].get())
            b_val = self._parse_number_input(self.entries["b"].get())
            a_val = self._parse_number_input(self.entries["a"].get())
            q_val = self._parse_number_input(self.entries["q_max"].get())

            if p_val is None or c_val is None or b_val is None or a_val is None or q_val is None:
                raise ValueError("Invalid numeric format")

            if p_val <= 0 or a_val <= 0 or b_val < 0 or c_val < 0:
                messagebox.showerror("Kesalahan Input", "Parameter p dan a harus bernilai lebih besar dari 0, serta biaya tidak boleh negatif.")
                return

            if p_val > 1e9 or c_val > 1e10 or b_val > 1e9 or a_val > 1e7:
                messagebox.showerror("Nilai Terlalu Besar", "Nilai parameter melebihi batas wajar kalkulasi. Mohon masukkan angka yang lebih realistis.")
                return

            if q_val < 20 or q_val > 10000:
                messagebox.showerror("Batas Rentang Porsi", "Batas rentang porsi harus berada antara 20 sampai 10.000 porsi.")
                return

            self.p = p_val
            self.c = c_val
            self.b = b_val
            self.a = a_val
            self.q_max = int(round(q_val))

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
            self._pending_price_autofill = False

            self._sync_slider_and_views()
        except ValueError:
            messagebox.showerror("Format Salah", "Mohon masukkan angka numerik yang valid pada seluruh kolom parameter.")
        except Exception as err:
            messagebox.showerror("Kesalahan Perhitungan", f"Gagal menghitung model kalkulus:\n{err}")

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

    def _fmt_rp_math(self, val: float) -> str:
        s = self._fmt_num(abs(val))
        return rf"-\mathrm{{Rp}}\,{s}" if val < 0 else rf"\mathrm{{Rp}}\,{s}"

    @staticmethod
    def _signed_poly_terms(quad_c: float, lin_c: float, const_c: float, var: str = "x") -> str:
        parts = []
        if quad_c != 0:
            q_s = f"{abs(quad_c):g}"
            parts.append((f"-{q_s}{var}^2" if quad_c < 0 else f"{q_s}{var}^2"))
        if lin_c != 0:
            l_s = f"{abs(lin_c):,.0f}".replace(",", ".")
            sign = " - " if lin_c < 0 else (" + " if parts else "")
            parts.append(f"{sign}{l_s}{var}")
        if const_c != 0:
            c_s = f"{abs(const_c):,.0f}".replace(",", ".")
            sign = " - " if const_c < 0 else (" + " if parts else "")
            parts.append(f"{sign}{c_s}")
        return "".join(parts) or "0"

    def _update_integral_tab(self):
        if not hasattr(self, "int_umkm_paper_body"):
            return

        try:
            ig = hitung_integral_umkm(self.p, self.c, self.b, self.a, self.q_max)
        except Exception as err:
            self._clear_paper_body(self.int_umkm_paper_body)
            self._add_callout_box(
                self.int_umkm_paper_body,
                "Gagal Menghitung Integral UMKM",
                f"Terjadi kesalahan perhitungan integral: {err}",
                tone="amber",
            )
            return
        b3 = ig["b3"]
        b4 = ig["b4"]
        a3 = ig["a3"]
        b1 = ig["b1"]
        a4 = ig["a4_b2"]
        b5 = ig["b5"]

        p_s = self._fmt_num(ig["p"])
        c_s = self._fmt_num(ig["c"])
        b_s = self._fmt_num(ig["b"])
        a_s = f"{ig['a']:g}"
        half_a_s = f"{ig['a'] / 2.0:g}"
        two_a_s = f"{2.0 * ig['a']:g}"
        four_a_s = f"{4.0 * ig['a']:g}"
        q_max_s = f"{ig['q_max']:.0f}"
        bep1_s = f"{ig['q_bep1']:.2f}" if ig["q_bep1"] is not None else "-"
        bep2_s = f"{ig['q_bep2']:.2f}" if ig["q_bep2"] is not None else "-"
        fx_tex = self._signed_poly_terms(-ig["a"], ig["alpha"], -ig["c"], "x")
        fp_tex = self._signed_poly_terms(0, -2.0 * ig["a"], ig["alpha"], "x")

        body = self.int_umkm_paper_body
        self._clear_paper_body(body)
        self._add_paper_header(
            body,
            title="Penerapan Rumus Integral pada Model UMKM (PDF A.1–A.5 & B.1–B.5)",
            subtitle="Evaluasi analitis & numerik integral nilai mutlak, pecahan polinom, substitusi u, trigonometri musiman, dan Teorema Dasar Kalkulus I.",
            chips=[
                f"Harga p = {self._fmt_rp(ig['p'])}",
                f"Tetap c = {self._fmt_rp(ig['c'])}",
                f"Modal b = {self._fmt_rp(ig['b'])}",
                f"Koef. a = {a_s}",
                f"Domain 0 ≤ x ≤ {q_max_s}",
            ],
        )
        self._add_math_box(
            body,
            [
                rf"$f(x) = {fx_tex},\qquad f'(x) = \mathrm{{MR}}(x) - \mathrm{{MC}}(x) = {fp_tex}$",
            ],
            accent="#0f172a",
            fontsize=11.5,
        )

        # 1. B.3
        self._add_paper_section(
            body,
            heading="1. Integral Nilai Mutlak Linier |f'(x)| — Pola PDF B.3",
            prose=f"Memecah integral pada titik stasioner x* = {b3['q_split']:.2f} di mana laju marjinal f'(x) = 0:",
            math_lines=[
                rf"$\int_{{0}}^{{{q_max_s}}} |f'(x)|\,dx = \int_{{0}}^{{{q_max_s}}} |{fp_tex}|\,dx$",
                rf"$\int_{{0}}^{{{b3['q_split']:.2f}}} f'(x)\,dx = {self._fmt_rp_math(b3['kenaikan_laba'])}\quad (\mathrm{{Kenaikan\ laba\ menuju\ puncak}})$",
                rf"$\int_{{{b3['q_split']:.2f}}}^{{{q_max_s}}} \left(-f'(x)\right)\,dx = {self._fmt_rp_math(b3['pengikisan_laba'])}\quad (\mathrm{{Pemborosan\ over-produksi}})$",
            ],
            callout={
                "title": "Total Variasi Laba (Analitis vs Numerik)",
                "text": (
                    f"Total Integral Mutlak ∫|f'(x)| dx (Analitis) = {self._fmt_rp(b3['total_eksak'])}  |  "
                    f"Verifikasi Numerik = {self._fmt_rp(b3['total_numerik'])}"
                ),
                "tone": "blue",
            },
            accent="#1e3a8a",
        )

        # 2. B.4
        b4_bullets = [
            f"Sub-interval {idx} [{sub['lo']:.2f} .. {sub['hi']:.2f}] ({sub['tanda']} → {'f(x)' if 'Positif' in sub['tanda'] else '-f(x)'}): Luas = {self._fmt_rp(sub['nilai_abs'])}"
            for idx, sub in enumerate(b4["sub_intervals"], 1)
        ]
        b4_bullets.extend([
            f"Area Surplus Laba (+) = {self._fmt_rp(b4['area_laba'])}  |  Area Defisit Rugi (-) = {self._fmt_rp(b4['area_rugi'])}",
            f"Verifikasi Numerik ∫|f(x)| dx = {self._fmt_rp(b4['total_mutlak_numerik'])}",
        ])
        self._add_paper_section(
            body,
            heading="2. Integral Nilai Mutlak Kuadrat |f(x)| — Pola PDF B.4",
            prose=f"Pembuat nol f(x) = 0 berada pada titik impas BEP₁ = {bep1_s} dan BEP₂ = {bep2_s}:",
            math_lines=[
                rf"$\int_{{0}}^{{{q_max_s}}} |f(x)|\,dx = \int_{{0}}^{{{q_max_s}}} |{fx_tex}|\,dx = {self._fmt_rp_math(b4['total_mutlak_eksak'])}$",
                rf"$\int_{{0}}^{{{q_max_s}}} f(x)\,dx\ (\mathrm{{Netto}}) = {self._fmt_rp_math(b4['integral_netto'])},\qquad \overline{{f}} = {self._fmt_rp_math(b4['rata_laba_domain'])}/\mathrm{{hari}}$",
            ],
            bullets=b4_bullets,
            accent="#0f766e",
        )

        # 3. A.3
        self._add_paper_section(
            body,
            heading="3. Integral Pecahan Polinom & ln|x| Biaya Rata-Rata AC(x) — Pola PDF A.3",
            math_lines=[
                rf"$\mathrm{{AC}}(x) = \frac{{C(x)}}{{x}} = \frac{{{a_s}x^2 + {b_s}x + {c_s}}}{{x}} = {a_s}x + {b_s} + \frac{{{c_s}}}{{x}}$",
                rf"$\int_{{{a3['q1']:.0f}}}^{{{a3['q2']:.0f}}} \mathrm{{AC}}(x)\,dx = \left[ {half_a_s}x^2 + {b_s}x + {c_s}\ln|x| \right]_{{{a3['q1']:.0f}}}^{{{a3['q2']:.0f}}} = {self._fmt_rp_math(a3['integral_ac'])}$",
            ],
            callout={
                "title": f"Rata-Rata Biaya Per Porsi pada [{a3['q1']:.0f}, {a3['q2']:.0f}]",
                "text": f"Nilai rata-rata AC(x) = {self._fmt_rp(a3['rata_rata_ac'])}/porsi",
                "tone": "slate",
            },
            accent="#7c3aed",
        )

        # 4. B.1 / A.1
        u_lo_s = self._fmt_num(b1["u_lo"])
        u_hi_s = self._fmt_num(b1["u_hi"])
        self._add_paper_section(
            body,
            heading="4. Integral Substitusi u + Ubah Batas VC(x*) — Pola PDF B.1 / A.1",
            math_lines=[
                rf"$\mathrm{{VC}}(x^*) = \int_{{0}}^{{{b1['q_hi']:.2f}}} ({two_a_s}x + {b_s})\,dx,\qquad u = {two_a_s}x + {b_s} \;\Rightarrow\; dx = \frac{{1}}{{{two_a_s}}}\,du$",
                rf"$\mathrm{{Batas:}}\ x = 0 \to u = {u_lo_s},\qquad x = {b1['q_hi']:.2f} \to u = {u_hi_s}$",
                rf"$\mathrm{{VC}}(x^*) = \frac{{1}}{{{two_a_s}}}\int_{{{u_lo_s}}}^{{{u_hi_s}}} u\,du = \left[ \frac{{u^2}}{{{four_a_s}}} \right]_{{{u_lo_s}}}^{{{u_hi_s}}} = {self._fmt_rp_math(b1['vc_substitusi'])}$",
            ],
            callout={
                "title": "Verifikasi Rumus Langsung",
                "text": f"VC langsung = a(x*)² + b(x*) = {self._fmt_rp(b1['vc_langsung'])} (Identik 100%)",
                "tone": "emerald",
            },
            accent="#b45309",
        )

        # 5. A.4 & B.2
        self._add_paper_section(
            body,
            heading=f"5. Integral Trigonometri Substitusi u = ωt — Proyeksi {a4['hari']} Hari (PDF A.4 & B.2)",
            math_lines=[
                rf"$L(t) = f^* + \Delta f\left(\frac{{1}}{{2}}\sin(\omega t) + \sin(2\omega t)\right),\quad \omega = \frac{{2\pi}}{{7}},\ f^* = {self._fmt_rp_math(ig['p_opt'])},\ \Delta f = {self._fmt_rp_math(a4['delta_p'])}$",
                rf"$\int_{{0}}^{{{a4['hari']}}} L(t)\,dt = \left[ f^*\,t - \frac{{\Delta f}}{{2\omega}}\cos(\omega t) - \frac{{\Delta f}}{{2\omega}}\cos(2\omega t) \right]_{{0}}^{{{a4['hari']}}} = {self._fmt_rp_math(a4['laba_bulanan_musiman'])}$",
            ],
            callout={
                "title": f"Akumulasi Laba {a4['hari']} Hari",
                "text": (
                    f"Gelombang Penjualan = {self._fmt_rp(a4['laba_bulanan_musiman'])}  |  "
                    f"Dibandingkan Laba Datar ({a4['hari']} × f*) = {self._fmt_rp(a4['laba_bulanan_datar'])}"
                ),
                "tone": "blue",
            },
            accent="#0369a1",
        )

        # 6. B.5
        samples_txt = "  |  ".join(f"x = {qv:g} → Rp {av:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for qv, av in b5["samples"])
        self._add_paper_section(
            body,
            heading="6. Teorema Dasar Kalkulus I & L'Hôpital — Pola PDF B.5",
            math_lines=[
                rf"$\lim_{{x \to 0}} \frac{{1}}{{x}}\int_{{0}}^{{x}} \mathrm{{MC}}(t)\,dt = \lim_{{x \to 0}} \frac{{\frac{{d}}{{dx}}\int_{{0}}^{{x}} ({two_a_s}t + {b_s})\,dt}}{{\frac{{d}}{{dx}}[x]}} = \lim_{{x \to 0}} ({two_a_s}x + {b_s}) = {self._fmt_rp_math(b5['limit_eksak'])}$",
            ],
            bullets=[f"Konvergensi AVC(x) saat x → 0⁺: {samples_txt}"],
            accent="#be123c",
        )

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
            ax.yaxis.set_major_formatter(self._rp_axis_formatter())
            ax.grid(True, linestyle="--", alpha=0.5, color=gc)

        # Panel 1: B.3 |f'(x)|
        ax1 = self.int_umkm_fig.add_subplot(gs[0, 0])
        _st(ax1, "B.3: Luas |f'(x)| = |MR - MC| (Naik vs Over-Produksi)", "Porsi (x)", "Rp/porsi")
        fp_arr = -2.0 * ig["a"] * q_arr + ig["alpha"]
        ax1.plot(q_arr, np.abs(fp_arr), color="#f59e0b", linewidth=2, label="|f'(x)|")
        ax1.fill_between(q_arr, np.abs(fp_arr), 0, where=(fp_arr >= 0), color="#10b981", alpha=0.28, label="Naik Laba")
        ax1.fill_between(q_arr, np.abs(fp_arr), 0, where=(fp_arr < 0), color="#ef4444", alpha=0.28, label="Pemborosan")
        ax1.legend(loc="upper center", fontsize=7, facecolor=bg, labelcolor=tc)

        # Panel 2: B.4 |f(x)|
        ax2 = self.int_umkm_fig.add_subplot(gs[0, 1])
        _st(ax2, "B.4: Luas |f(x)| (Surplus Laba & Defisit Dibalik)", "Porsi (x)", "Rupiah")
        f_arr = -ig["a"] * (q_arr ** 2) + ig["alpha"] * q_arr - ig["c"]
        ax2.plot(q_arr, np.abs(f_arr), color="#3b82f6", linewidth=2, label="|f(x)|")
        ax2.plot(q_arr, f_arr, color="#94a3b8", linestyle="--", linewidth=1, label="f(x) asli")
        ax2.fill_between(q_arr, np.abs(f_arr), 0, where=(f_arr >= 0), color="#10b981", alpha=0.28, label="Laba (+)")
        ax2.fill_between(q_arr, np.abs(f_arr), 0, where=(f_arr < 0), color="#ef4444", alpha=0.25, label="Defisit (-)")
        ax2.legend(loc="upper left", fontsize=7, facecolor=bg, labelcolor=tc)

        # Panel 3: A.3 AC(x) & B.1 VC(x*)
        ax3 = self.int_umkm_fig.add_subplot(gs[1, 0])
        _st(ax3, "A.3 & B.1: Luas ∫MC(x)dx = VC(x*) & Kurva AC(x)", "Porsi (x)", "Rp/porsi")
        q_pos = np.linspace(max(1.0, ig["q_max"] * 0.02), ig["q_max"], 350)
        mc_pos = 2.0 * ig["a"] * q_pos + ig["b"]
        ac_pos = ig["a"] * q_pos + ig["b"] + ig["c"] / q_pos
        ax3.plot(q_pos, mc_pos, color="#ef4444", linewidth=2, label="MC(x) = 2ax + b")
        ax3.plot(q_pos, ac_pos, color="#8b5cf6", linewidth=2, label="AC(x) = ax + b + c/x")
        ax3.fill_between(q_pos, mc_pos, 0, where=(q_pos <= ig["q_opt"]), color="#ef4444", alpha=0.2, label="VC(x*)")
        y_top_ac = max(1000.0, float(np.max(mc_pos)) * 1.12, float(np.percentile(ac_pos, 92)))
        ax3.set_ylim(0, y_top_ac)
        ax3.legend(loc="lower right", fontsize=7, facecolor=bg, labelcolor=tc)

        # Panel 4: A.4/B.2 Proyeksi Laba 30 Hari
        ax4 = self.int_umkm_fig.add_subplot(gs[1, 1])
        _st(ax4, f"A.4/B.2: Proyeksi Laba {a4['hari']} Hari (Gelombang)", "Hari ke-t", "Laba/Hari (Rp)")
        t_arr = np.linspace(0.0, float(a4["hari"]), 300)
        l_arr = ig["p_opt"] + a4["delta_p"] * (0.5 * np.sin(a4["omega"] * t_arr) + np.sin(2.0 * a4["omega"] * t_arr))
        ax4.plot(t_arr, l_arr, color="#10b981", linewidth=2, label="L(t) Harian")
        ax4.axhline(ig["p_opt"], color="#f59e0b", linestyle="--", linewidth=1.2, label="f* Rata-rata")
        ax4.fill_between(t_arr, l_arr, 0, where=(l_arr >= 0), color="#10b981", alpha=0.18)
        ax4.fill_between(t_arr, l_arr, 0, where=(l_arr < 0), color="#ef4444", alpha=0.18)
        ax4.legend(loc="lower right", fontsize=7, facecolor=bg, labelcolor=tc)

        self.int_umkm_fig.subplots_adjust(top=0.92, bottom=0.10, left=0.11, right=0.97, hspace=0.48, wspace=0.30)
        self.int_umkm_canvas.draw()

    def _update_pdf_solver(self):
        if not hasattr(self, "pdf_soal_menu") or not hasattr(self, "int_pdf_paper_body"):
            return
        try:
            judul = self.pdf_soal_menu.get()
            kode = self._pdf_judul_to_kode.get(judul, "B.4")
            raw_x = self.pdf_x_entry.get()
            x_val = self._parse_number_input(raw_x)
            note_invalid_x = None
            if x_val is None or abs(x_val) > 100.0:
                x_val = 2.0
                if raw_x.strip():
                    note_invalid_x = "Nilai x uji tidak valid atau di luar rentang [-100, 100], otomatis memakai x = 2."

            hasil = evaluasi_soal_pdf(kode, x_uji=x_val)
            x_shown = float(hasil.get("x_eval", x_val))
            body = self.int_pdf_paper_body
            self._clear_paper_body(body)
            self._add_paper_header(
                body,
                title=f"Pembahasan Soal Integral PDF [{hasil['kode']}]",
                subtitle=judul,
                chips=[
                    f"Kode: {hasil['kode']}",
                    f"Jenis: {str(hasil.get('jenis', '-')).replace('_', ' ').title()}",
                    f"Nilai Uji x = {x_shown:g}",
                ],
            )
            if note_invalid_x:
                self._add_callout_box(body, "Penyesuaian Nilai Uji", note_invalid_x, tone="amber")
            elif abs(x_shown - x_val) > 1e-6:
                self._add_callout_box(
                    body,
                    "Penyesuaian Domain Uji",
                    f"Titik x = {x_val:g} berada di luar domain aman atau dekat asimtot, sehingga verifikasi memakai x = {x_shown:g}.",
                    tone="amber",
                )
        except Exception as err:
            body = self.int_pdf_paper_body
            self._clear_paper_body(body)
            self._add_callout_box(body, "Gagal Memuat Soal Integral PDF", f"Terjadi kendala evaluasi: {err}", tone="amber")
            return
        self._add_paper_section(
            body,
            heading="Soal & Hasil Eksak",
            math_lines=[
                r"$\mathrm{Soal:}\quad$ " + hasil["latex_soal"],
                r"$\mathrm{Hasil\ Eksak:}\quad$ " + hasil["latex_hasil"],
            ],
            accent="#1e3a8a",
        )
        self._add_paper_section(
            body,
            heading="Langkah Penyelesaian Analitis",
            math_lines=list(hasil["latex_langkah"]),
            callout=(
                {
                    "title": "Catatan Penulisan Lembar PDF (A.3)",
                    "text": "Pada lembar PDF asli tertulis '6|x|', sedangkan antiturunan analitis baku dari ∫ (6/x) dx adalah 6 ln|x| sebagaimana ditampilkan pada langkah dan grafik.",
                    "tone": "amber",
                }
                if hasil["kode"] == "A.3"
                else None
            ),
            accent="#0f766e",
        )
        self._add_callout_box(
            body,
            title="Verifikasi Komputasi Numerik",
            text=hasil["verifikasi"],
            tone="emerald",
        )

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
        ac_opt = res.get("ac_opt", self.b)
        tetap_per_porsi = (self.c / q_opt) if q_opt > 0 else self.c
        self.tasik_segmen_lbl.configure(text=f"Segmen: {est['segmen']}")
        self.tasik_summary_lbl.configure(
            text=(
                f"Modal/Porsi (b): Rp {self.b:,.0f} (kisaran Rp {est['b_min']:,.0f} - Rp {est['b_max']:,.0f})\n"
                f"Tetap/Hari (c): Rp {self.c:,.0f}/hari (beban ~Rp {tetap_per_porsi:,.0f}/porsi)\n"
                f"Total Modal/Porsi di x*: Rp {ac_opt:,.0f} < Jual Rp {self.p:,.0f}\n"
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
        a = res["a"]
        q_opt = res["q_opt"]
        x_kiri = res["x_kiri"]
        x_kanan = res["x_kanan"]
        pp_kiri = res["p_prime_kiri"]
        pp_kanan = res["p_prime_kanan"]
        f_max_dom = res["f_max_dom"]
        x_max_dom = res["x_max_dom"]
        f_min = res["f_min"]
        x_min = res["x_min"]
        min_both = res["min_both_ends"]

        if a > 0:
            self.card_q_opt["val_lbl"].configure(text=f"x* = {q_opt:.1f} porsi")
            if 0.0 <= q_opt <= float(self.q_max):
                self.card_q_opt["sub_lbl"].configure(text="Syarat Stasioner f'(x) = 0")
            else:
                self.card_q_opt["sub_lbl"].configure(text=f"Di luar [0, {self.q_max}]; opt di x={x_max_dom:g}")
        else:
            self.card_q_opt["val_lbl"].configure(text=f"x_maks = {x_max_dom:g} porsi")
            self.card_q_opt["sub_lbl"].configure(text="Model linear (a = 0)")

        self.card_profit_max["val_lbl"].configure(text=self._fmt_rp(f_max_dom))
        if a > 0 and 0.0 <= q_opt <= float(self.q_max):
            self.card_profit_max["sub_lbl"].configure(text=f"Laba puncak pada x* = {q_opt:.1f} porsi")
        else:
            self.card_profit_max["sub_lbl"].configure(text=f"Maks ujung domain x = {x_max_dom:g} porsi")

        self.card_bep["val_lbl"].configure(text=self._fmt_rp(f_min))
        min_loc = f"x=0 & x={self.q_max}" if min_both else f"di x={x_min:g}"
        if res["q_bep1"] is not None and res["q_bep2"] is not None:
            self.card_bep["sub_lbl"].configure(
                text=f"Min {min_loc} | BEP: {res['q_bep1']:.1f} & {res['q_bep2']:.1f}"
            )
        else:
            self.card_bep["sub_lbl"].configure(text=f"Min {min_loc} | Tidak ada BEP real")

        if res["is_max"]:
            self.card_test1["val_lbl"].configure(text="f'(x): (+) -> 0 -> (-)")
            self.card_test1["sub_lbl"].configure(
                text=f"f'({x_kiri:g})>0, f'({x_kanan:g})<0 (Maks)"
            )
        elif pp_kiri <= 0 and pp_kanan <= 0:
            self.card_test1["val_lbl"].configure(text="f'(x) <= 0 (Turun)")
            self.card_test1["sub_lbl"].configure(text="Maks ujung kiri x=0")
        else:
            self.card_test1["val_lbl"].configure(text="f'(x) >= 0 (Naik)")
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

        p_str = f"Fungsi Laba f(x): Rp {profit:,.0f}".replace(",", ".")
        self.live_profit_lbl.configure(text=p_str)

        opt_q = self.calc_results["q_opt"]
        x_min_dom = self.calc_results["x_min"]
        min_both = self.calc_results["min_both_ends"]
        if abs(q - opt_q) < 0.5 and 0.0 <= opt_q <= float(self.q_max):
            self.live_status_lbl.configure(text="Status: TITIK KRITIS x* (NILAI MAKSIMUM)", text_color="#10b981")
            self.live_profit_lbl.configure(text_color="#10b981")
        elif q == 0:
            st_zero = "NILAI MINIMUM MUTLAK" if (x_min_dom == 0.0 or min_both) else "UJUNG KIRI / BIAYA TETAP"
            self.live_status_lbl.configure(text=f"Status: UJUNG DOMAIN x=0 ({st_zero})", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")
        elif abs(q - float(self.q_max)) < 0.5 and (x_min_dom == float(self.q_max) or min_both):
            self.live_status_lbl.configure(text=f"Status: UJUNG DOMAIN x={self.q_max} (NILAI MINIMUM MUTLAK)", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")
        elif profit > 0:
            self.live_status_lbl.configure(text="Status: ZONA LABA POSITIF (f(x) > 0)", text_color="#3b82f6")
            self.live_profit_lbl.configure(text_color="#3b82f6")
        elif abs(profit) < 100:
            self.live_status_lbl.configure(text="Status: TITIK IMPAS BEP (f(x) = 0)", text_color="#f59e0b")
            self.live_profit_lbl.configure(text_color="#f59e0b")
        else:
            self.live_status_lbl.configure(text="Status: ZONA RUGI DEFISIT (f(x) < 0)", text_color="#ef4444")
            self.live_profit_lbl.configure(text_color="#ef4444")

        if p_prime > 50:
            laju_str = f"Laju Laba f'(x): +Rp {p_prime:,.0f} (f' > 0: kurva naik)".replace(",", ".")
        elif p_prime < -50:
            laju_str = f"Laju Laba f'(x): -Rp {abs(p_prime):,.0f} (f' < 0: kurva turun)".replace(",", ".")
        else:
            laju_str = "Laju Laba f'(x): Rp 0 (Titik Kritis x*: f'(x*) = 0)"
        self.live_mp_lbl.configure(text=laju_str)

    def _update_kalkulus_text(self):
        if not hasattr(self, "calc_paper_body"):
            return

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

        p_s = self._fmt_num(p)
        c_s = self._fmt_num(c)
        b_s = self._fmt_num(b)
        alpha_s = self._fmt_num(alpha)
        a_s = f"{a:g}"
        half_a_s = f"{a / 2.0:g}"
        two_a_s = f"{2.0 * a:g}"
        four_a_s = f"{4.0 * a:g}"
        q_max_s = f"{self.q_max:g}"
        fx_tex = self._signed_poly_terms(-a, alpha, -c, "x")
        fp_tex = self._signed_poly_terms(0, -2.0 * a, alpha, "x")
        fp_t_tex = self._signed_poly_terms(0, -2.0 * a, alpha, "t")

        body = self.calc_paper_body
        self._clear_paper_body(body)
        self._add_paper_header(
            body,
            title="Penerapan Kalkulus UMKM: Integral, Substitusi u, Nilai Mutlak & Optimasi f(x)",
            subtitle="Formulasi fungsi f(x), R(x), C(x), uji turunan pertama, teorema nilai ekstrem, dan penerapan pola rumus PDF A.1–A.5 & B.1–B.5.",
            chips=[
                f"Harga p = {self._fmt_rp(p)}",
                f"Tetap c = {self._fmt_rp(c)}",
                f"Modal b = {self._fmt_rp(b)}",
                f"Koef. a = {a_s}",
                f"Domain 0 ≤ x ≤ {q_max_s}",
            ],
        )

        # I. Formulasi via FTC I
        self._add_paper_section(
            body,
            heading="I. Formulasi Fungsi f(x), R(x) & C(x) dari Teorema Dasar Kalkulus I (Pola PDF B.5)",
            prose=(
                f"Misalkan x adalah jumlah porsi produksi harian pada domain tertutup [0, {q_max_s}] "
                f"dengan nilai awal biaya tetap harian C(0) = c = {self._fmt_rp(c)}:"
            ),
            math_lines=[
                rf"$\mathrm{{MR}}(x) = R'(x) = p = {self._fmt_rp_math(p)} \;\Rightarrow\; R(x) = \int_{{0}}^{{x}} {p_s}\,dt = {p_s}x$",
                rf"$\mathrm{{MC}}(x) = C'(x) = {two_a_s}x + {b_s} \;\Rightarrow\; C(x) = {c_s} + \int_{{0}}^{{x}} ({two_a_s}t + {b_s})\,dt = {a_s}x^2 + {b_s}x + {c_s}$",
                rf"$f'(x) = \mathrm{{MR}}(x) - \mathrm{{MC}}(x) = -{two_a_s}x + ({p_s} - {b_s}) = {fp_tex}$",
                rf"$f(x) = -c + \int_{{0}}^{{x}} f'(t)\,dt = -{c_s} + \int_{{0}}^{{x}} ({fp_t_tex})\,dt = {fx_tex}$",
                rf"$\mathrm{{Uji\ FTC\ I:}}\quad \frac{{d}}{{dx}}\left[f(x)\right] = f'(x) = {fp_tex}$",
            ],
            accent="#1e3a8a",
        )

        # II. Titik Kritis, Uji Turunan Pertama, Nilai Ekstrem & BEP
        sign_kiri_tex = r"\mathrm{POSITIF}\ (+) \Rightarrow \mathrm{Kurva\ NAIK}" if res["p_prime_kiri"] > 0 else r"\mathrm{NEGATIF/NOL} \Rightarrow \mathrm{Kurva\ TURUN}"
        sign_kanan_tex = r"\mathrm{NEGATIF}\ (-) \Rightarrow \mathrm{Kurva\ TURUN}" if res["p_prime_kanan"] < 0 else r"\mathrm{POSITIF/NOL} \Rightarrow \mathrm{Kurva\ NAIK}"
        garis_tanda = (
            f"[0]  {'+++ (naik) +++' if res['p_prime_kiri'] > 0 else '--- (turun) ---'}  "
            f"[x* = {q_opt:.2f}]  {'--- (turun) ---' if res['p_prime_kanan'] < 0 else '+++ (naik) +++'}  [{q_max_s}]"
        )
        if alpha > 0 and abs(q_opt - alpha / (2.0 * a)) < 1e-6:
            stasioner_line = rf"$\mathrm{{Syarat\ Stasioner:}}\ f'(x) = 0 \Leftrightarrow \mathrm{{MR}} = \mathrm{{MC}} \;\Rightarrow\; {two_a_s}x = {alpha_s} \;\Rightarrow\; x^* = \frac{{{alpha_s}}}{{{two_a_s}}} = {q_opt:.2f}\ \mathrm{{porsi/hari}}$"
        else:
            stasioner_line = rf"$\mathrm{{Syarat\ Stasioner:}}\ {fp_tex} = 0,\quad \mathrm{{titik\ batas\ domain}}\ x^* = {q_opt:.2f}\ \mathrm{{porsi/hari}}$"

        min_at = f"0 & {q_max_s}" if res["min_both_ends"] else f"{res['x_min']:g}"
        ii_bullets = [
            f"Garis Tanda f'(x):  {garis_tanda}",
            f"Nilai Maksimum Mutlak: f({res['x_max_dom']:.2f}) = {self._fmt_rp(res['f_max_dom'])}/hari (Omzet R = {self._fmt_rp(r_opt)}, Biaya C = {self._fmt_rp(c_opt)})",
            f"Nilai Ujung Domain: f(0) = {self._fmt_rp(res['f_zero'])}/hari  |  f({q_max_s}) = {self._fmt_rp(res['f_end'])}/hari",
            f"Nilai Minimum Mutlak (Teorema Nilai Ekstrem): min(f(0), f({q_max_s})) = {self._fmt_rp(res['f_min'])}/hari (di x = {min_at})",
            f"Diskriminan BEP: D = ({alpha_s})² - 4({a_s})({c_s}) = {self._fmt_num(res['D'])}",
        ]
        if res["q_bep1"] is not None:
            ii_bullets.extend([
                f"Titik Impas: BEP₁ = {res['q_bep1']:.2f} porsi/hari  |  BEP₂ = {res['q_bep2']:.2f} porsi/hari",
                f"Rentang Untung (f(x) > 0): ({res['q_bep1']:.2f} ; {res['q_bep2']:.2f})  →  Batas aman: {int(np.ceil(res['q_bep1']))} s.d. {int(np.floor(res['q_bep2']))} porsi/hari",
            ])
        else:
            ii_bullets.append("Diskriminan negatif: Tidak ada titik impas real pada kombinasi parameter ini.")

        self._add_paper_section(
            body,
            heading=f"II. Titik Kritis x*, Uji Turunan Pertama f'(x) & Nilai Ekstrem [0, {q_max_s}]",
            prose=f"Dibulatkan secara operasional menjadi {round(q_opt)} porsi/hari. Evaluasi perubahan tanda f'(x) dan ujung interval:",
            math_lines=[
                stasioner_line,
                rf"$\mathrm{{Interval\ Kiri}}\ [0, {q_opt:.2f}):\ f'({res['x_kiri']:g}) = {self._fmt_rp_math(res['p_prime_kiri'])}\quad \left({sign_kiri_tex}\right)$",
                rf"$\mathrm{{Titik\ Kritis}}\ x^* = {q_opt:.2f}:\ f'({q_opt:.2f}) = 0\quad (\mathrm{{Stasioner\ /\ Puncak\ Perubahan\ Tanda}})$",
                rf"$\mathrm{{Interval\ Kanan}}\ ({q_opt:.2f}, {q_max_s}]:\ f'({res['x_kanan']:g}) = {self._fmt_rp_math(res['p_prime_kanan'])}\quad \left({sign_kanan_tex}\right)$",
            ],
            bullets=ii_bullets,
            callout={
                "title": "Kesimpulan Uji Turunan Pertama",
                "text": (
                    f"Tanda f'(x) berubah dari POSITIF (+) ke NEGATIF (-) saat melewati x* = {q_opt:.2f}, terbukti f(x*) adalah MAKSIMUM MUTLAK."
                    if res["is_max"]
                    else "Tidak terjadi perubahan tanda (+) ke (-) di dalam interior (0, x_max); nilai ekstrem berada di ujung batas domain."
                ),
                "tone": "emerald" if res["is_max"] else "amber",
            },
            accent="#0f766e",
        )

        # III. Biaya Variabel Total VC(x*) via Substitusi u
        u_lo_s = self._fmt_num(b1["u_lo"])
        u_hi_s = self._fmt_num(b1["u_hi"])
        self._add_paper_section(
            body,
            heading="III. Biaya Variabel Total VC(x*) via Substitusi u + Ubah Batas (Pola PDF B.1 & A.1)",
            math_lines=[
                rf"$\mathrm{{VC}}(x^*) = \int_{{0}}^{{{b1['q_hi']:.2f}}} ({two_a_s}x + {b_s})\,dx,\qquad u = {two_a_s}x + {b_s} \;\Rightarrow\; dx = \frac{{1}}{{{two_a_s}}}\,du$",
                rf"$\mathrm{{Ubah\ batas:}}\ x = 0 \to u = {u_lo_s},\qquad x = {b1['q_hi']:.2f} \to u = {two_a_s}({b1['q_hi']:.2f}) + {b_s} = {u_hi_s}$",
                rf"$\mathrm{{VC}}(x^*) = \frac{{1}}{{{two_a_s}}}\int_{{{u_lo_s}}}^{{{u_hi_s}}} u\,du = \left[ \frac{{u^2}}{{{four_a_s}}} \right]_{{{u_lo_s}}}^{{{u_hi_s}}} = {self._fmt_rp_math(b1['vc_substitusi'])}$",
            ],
            callout={
                "title": "Verifikasi Rumus Langsung",
                "text": f"Nilai VC(x*) dari {a_s}({b1['q_hi']:.2f})² + {b_s}({b1['q_hi']:.2f}) = {self._fmt_rp(b1['vc_langsung'])} (identik 100%).",
                "tone": "emerald",
            },
            accent="#b45309",
        )

        # IV. AC(x) Pecah Polinom & ln|x|
        self._add_paper_section(
            body,
            heading="IV. Integral Biaya Rata-Rata AC(x) via Pecah Polinom & ln|x| (Pola PDF A.3)",
            math_lines=[
                rf"$\mathrm{{AC}}(x) = \frac{{C(x)}}{{x}} = \frac{{{a_s}x^2 + {b_s}x + {c_s}}}{{x}} = {a_s}x + {b_s} + \frac{{{c_s}}}{{x}}$",
                rf"$\int_{{{a3['q1']:.0f}}}^{{{a3['q2']:.0f}}} \mathrm{{AC}}(x)\,dx = \left[ {half_a_s}x^2 + {b_s}x + {c_s}\ln|x| \right]_{{{a3['q1']:.0f}}}^{{{a3['q2']:.0f}}} = {self._fmt_rp_math(a3['integral_ac'])}$",
            ],
            callout={
                "title": f"Rata-Rata AC(x) pada [{a3['q1']:.0f}, {a3['q2']:.0f}]",
                "text": f"Biaya rata-rata per porsi pada interval produksi tersebut = {self._fmt_rp(a3['rata_rata_ac'])}/porsi.",
                "tone": "slate",
            },
            accent="#7c3aed",
        )

        # V. Nilai Mutlak Linier |f'(x)|
        self._add_paper_section(
            body,
            heading="V. Integral Nilai Mutlak Linier |f'(x)| (Pola PDF B.3)",
            prose=f"Pembuat nol f'(x) = 0 berada pada x* = {q_opt:.2f} (split integral di x = {b3['q_split']:.2f}):",
            math_lines=[
                rf"$\int_{{0}}^{{{q_max_s}}} |f'(x)|\,dx = \int_{{0}}^{{{q_max_s}}} |{fp_tex}|\,dx = {self._fmt_rp_math(b3['total_eksak'])}$",
            ],
            bullets=[
                f"0 ≤ x ≤ {b3['q_split']:.2f}: f'(x) ≥ 0  →  ∫ f'(x) dx = {self._fmt_rp(b3['kenaikan_laba'])} (Kenaikan laba menuju puncak)",
                f"{b3['q_split']:.2f} ≤ x ≤ {q_max_s}: f'(x) < 0  →  ∫ -f'(x) dx = {self._fmt_rp(b3['pengikisan_laba'])} (Pemborosan over-produksi)",
                f"Total Integral Mutlak |f'(x)| = {self._fmt_rp(b3['total_eksak'])}",
            ],
            accent="#1d4ed8",
        )

        # VI. Nilai Mutlak Kuadrat |f(x)|
        b4_bullets = [
            f"Sub-interval {idx} [{sub['lo']:.2f} .. {sub['hi']:.2f}] ({sub['tanda']} → {'f(x)' if 'Positif' in sub['tanda'] else '-f(x)'}): Luas = {self._fmt_rp(sub['nilai_abs'])}"
            for idx, sub in enumerate(b4["sub_intervals"], 1)
        ]
        b4_bullets.append(
            f"Total Area Surplus Laba (+) = {self._fmt_rp(b4['area_laba'])}  |  Total Area Defisit (-) = {self._fmt_rp(b4['area_rugi'])}"
        )
        self._add_paper_section(
            body,
            heading="VI. Integral Nilai Mutlak Kuadrat |f(x)| (Pola PDF B.4)",
            math_lines=[
                rf"$\int_{{0}}^{{{q_max_s}}} |f(x)|\,dx = \int_{{0}}^{{{q_max_s}}} |{fx_tex}|\,dx = {self._fmt_rp_math(b4['total_mutlak_eksak'])}$",
                rf"$\int_{{0}}^{{{q_max_s}}} f(x)\,dx\ (\mathrm{{Netto}}) = {self._fmt_rp_math(b4['integral_netto'])},\qquad \overline{{f}} = {self._fmt_rp_math(b4['rata_laba_domain'])}/\mathrm{{hari}}$",
            ],
            bullets=b4_bullets,
            accent="#0f766e",
        )

        # VII. Trigonometri 30 Hari & Limit L'Hopital
        self._add_paper_section(
            body,
            heading=f"VII. Proyeksi Trigonometri {a4['hari']} Hari (PDF A.4/B.2) & Limit L'Hôpital (PDF B.5)",
            math_lines=[
                rf"$L(t) = f^* + \Delta f\left(\frac{{1}}{{2}}\sin(\omega t) + \sin(2\omega t)\right) \;\Rightarrow\; \int_{{0}}^{{{a4['hari']}}} L(t)\,dt = {self._fmt_rp_math(a4['laba_bulanan_musiman'])}$",
                rf"$\lim_{{x \to 0}} \frac{{1}}{{x}}\int_{{0}}^{{x}} \mathrm{{MC}}(t)\,dt = \lim_{{x \to 0}} ({two_a_s}x + {b_s}) = {self._fmt_rp_math(b5['limit_eksak'])}/\mathrm{{porsi}}$",
            ],
            bullets=[
                f"Perbandingan proyeksi {a4['hari']} hari: Gelombang musiman = {self._fmt_rp(a4['laba_bulanan_musiman'])} vs datar ({a4['hari']} × f*) = {self._fmt_rp(a4['laba_bulanan_datar'])}.",
                f"Limit L'Hôpital startup: Biaya marjinal awal tepat pada 0 porsi konvergen ke biaya bahan baku b = {self._fmt_rp(b5['limit_eksak'])}/porsi.",
            ],
            accent="#be123c",
        )

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
        if q_bep1 is not None and 0.0 <= q_bep1 <= float(self.q_max):
            special_pts.append(round(q_bep1, 1))
        if q_bep2 is not None and 0.0 <= q_bep2 <= float(self.q_max):
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
            elif (q_bep1 is not None and abs(q - q_bep1) < 0.2) or (q_bep2 is not None and abs(q - q_bep2) < 0.2):
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
                "Porsi (x)": q,
                "Pendapatan R(x)": r,
                "Biaya Total C(x)": cost,
                "Keuntungan f(x)": profit,
                "Biaya Rata-Rata": ac,
                "MR": mr,
                "MC": mc,
                "Turunan Pertama f'(x)": p_prime,
                "Status": status
            })
            self.tree.insert("", tk.END, values=row_val, tags=(tag,))

    def _export_table_csv(self):
        try:
            if not getattr(self, "table_data_rows", None):
                messagebox.showwarning("Data Kosong", "Tidak ada data simulasi untuk diekspor.")
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV File", "*.csv"), ("Excel Spreadsheet", "*.xlsx"), ("All Files", "*.*")],
                title="Simpan Data Simulasi Kalkulus UMKM"
            )
            if file_path:
                df = pd.DataFrame(self.table_data_rows)
                if file_path.lower().endswith(".xlsx"):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False, encoding="utf-8-sig")
                messagebox.showinfo("Berhasil", f"Data berhasil diekspor ke:\n{file_path}")
        except ImportError:
            messagebox.showerror(
                "Modul Excel Tidak Tersedia",
                "Ekspor format Excel (.xlsx) memerlukan pustaka 'openpyxl'.\n"
                "Silakan pilih format CSV (.csv) yang dapat dibuka langsung di Microsoft Excel.",
            )
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
            ax.yaxis.set_major_formatter(self._rp_axis_formatter())
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

        if mode == "Kurva Keuntungan f(x)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, f"Fungsi Keuntungan f(x) = -{a:g}x² + {self._fmt_num(p-b)}x - {self._fmt_num(c)}",
                       "Jumlah Porsi Produksi per Hari (x)", "Nilai Fungsi Keuntungan f(x) (Rp)")

            ax.plot(q_arr, profit_arr, color="#10b981", linewidth=2.5, label="Fungsi Keuntungan f(x) = R(x) - C(x)")
            ax.axhline(0, color="#ef4444" if not is_dark else "#f87171", linestyle=":", linewidth=1.5, label="Garis Impas (f(x) = 0)")

            ax.fill_between(q_arr, profit_arr, 0, where=(profit_arr >= 0), color="#10b981", alpha=0.15, label="Zona Untung (f(x) >= 0)")
            ax.fill_between(q_arr, profit_arr, 0, where=(profit_arr < 0), color="#ef4444", alpha=0.15, label="Zona Rugi (f(x) < 0)")

            if 0 <= q_opt <= self.q_max:
                ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, alpha=0.8)
                ax.scatter([q_opt], [p_opt], color="#f59e0b", s=120, zorder=5,
                           label=f"Titik Kritis x*: ({q_opt:.1f} porsi, f(x*)={self._fmt_rp(p_opt)})")
                ax.annotate(
                    f"TITIK KRITIS (NILAI MAKSIMUM):\nx* = {q_opt:.1f} porsi | f'(x*) = 0\nf(x*) = {self._fmt_rp(p_opt)} (Maks Global)",
                    xy=(q_opt, p_opt),
                    xytext=(-15, -85),
                    textcoords="offset points",
                    ha="center",
                    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9, fontweight="bold", color=text_color,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#f59e0b", alpha=0.9)
                )

            x_min = res["x_min"]
            f_min = res["f_min"]
            min_both = res["min_both_ends"]
            if min_both:
                ax.scatter([0, float(self.q_max)], [res["f_zero"], res["f_end"]], color="#ef4444", s=70, zorder=5,
                           label=f"Nilai Min Mutlak: (0 & {self.q_max}, {self._fmt_rp(f_min)})")
                ax.annotate(f"NILAI MINIMUM:\nf(0)=f({self.q_max})={self._fmt_rp(f_min)}", xy=(0, f_min),
                            xytext=(14, 12), textcoords="offset points", fontsize=8, color="#ef4444", fontweight="bold")
            elif x_min == 0.0:
                ax.scatter([0], [f_min], color="#ef4444", s=70, zorder=5, label=f"Nilai Min Mutlak: (0, {self._fmt_rp(f_min)})")
                ax.annotate(f"NILAI MINIMUM:\nf(0) = {self._fmt_rp(f_min)}", xy=(0, f_min),
                            xytext=(14, 12), textcoords="offset points", fontsize=8, color="#ef4444", fontweight="bold")
            else:
                ax.scatter([x_min], [f_min], color="#ef4444", s=70, zorder=5, label=f"Nilai Min Mutlak: ({x_min:g}, {self._fmt_rp(f_min)})")
                ax.annotate(f"NILAI MINIMUM:\nf({x_min:g}) = {self._fmt_rp(f_min)}", xy=(x_min, f_min),
                            xytext=(-150, 6), textcoords="offset points", fontsize=8, color="#ef4444", fontweight="bold",
                            arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.2))

            bep1_y_offset = -30 if f_min < -1000 else 20
            if q_bep1 is not None and 0.0 <= q_bep1 <= float(self.q_max):
                ax.scatter([q_bep1], [0], color="#60a5fa", s=60, zorder=5)
                ax.annotate(f"BEP 1: {q_bep1:.1f}\nf(x)=0", xy=(q_bep1, 0),
                            xytext=(20, bep1_y_offset), textcoords="offset points",
                            arrowprops=dict(arrowstyle="->", color="#60a5fa", lw=1.2),
                            fontsize=8, color="#60a5fa", fontweight="bold")
            if q_bep2 is not None and 0.0 <= q_bep2 <= float(self.q_max):
                ax.scatter([q_bep2], [0], color="#60a5fa", s=60, zorder=5)
                ax.annotate(f"BEP 2: {q_bep2:.1f}\nf(x)=0", xy=(q_bep2, 0),
                            xytext=(-90, 28), textcoords="offset points",
                            arrowprops=dict(arrowstyle="->", color="#60a5fa", lw=1.2),
                            fontsize=8, color="#60a5fa", fontweight="bold")

            ax.scatter([slider_q], [slider_p], color="#ec4899", s=45, zorder=6)
            ax.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1.2, alpha=0.7)

            ax.legend(loc="upper right", framealpha=0.85, facecolor=bg_color, labelcolor=text_color, fontsize=8)
            create_hover_elements(ax, "profit")

        elif mode == "Pendapatan R(x) vs Biaya C(x)":
            ax = self.fig.add_subplot(111)
            style_axis(ax, "Perbandingan Pendapatan Total R(x) vs Total Biaya C(x)",
                       "Jumlah Porsi Produksi per Hari (x)", "Rupiah (Rp)")

            ax.plot(q_arr, r_arr, color="#3b82f6", linewidth=2.5, label=f"Pendapatan R(x) = {self._fmt_num(p)}x")
            ax.plot(q_arr, c_arr, color="#ef4444", linewidth=2.5,
                    label=f"Biaya Total C(x) = {a:g}x² + {self._fmt_num(b)}x + {self._fmt_num(c)}")

            bep_rc_pts = [bv for bv in (q_bep1, q_bep2) if bv is not None and 0.0 <= bv <= float(self.q_max)]
            if bep_rc_pts:
                bep_lbl = " & ".join(f"{bv:.1f}" for bv in bep_rc_pts)
                ax.scatter(bep_rc_pts, [p * bv for bv in bep_rc_pts], color="#60a5fa", s=55, zorder=5,
                           label=f"Titik Impas BEP (R = C): {bep_lbl}")

            if 0 <= q_opt <= self.q_max:
                ax.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linestyle="-", linewidth=3,
                        label=f"Gap Keuntungan Max: {self._fmt_rp(p_opt)}")
                ax.scatter([q_opt, q_opt], [c_opt, r_opt], color="#10b981", s=60, zorder=5)
                ax.annotate(
                    f"JARAK MAKSIMAL (R - C):\nx* = {q_opt:.1f} porsi\nLaba = {self._fmt_rp(p_opt)}",
                    xy=(q_opt, (r_opt + c_opt) / 2),
                    xytext=(30, -68),
                    textcoords="offset points",
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
            style_axis(ax, "Optimasi Marjinal: Pendapatan Marjinal (MR) vs Biaya Marjinal (MC)",
                       "Jumlah Porsi Produksi per Hari (x)", "Rupiah per Porsi (Rp/porsi)")

            ax.plot(q_arr, mr_arr, color="#3b82f6", linewidth=2.5, label=f"Marginal Revenue: MR(x) = R'(x) = {self._fmt_rp(p)}")
            ax.plot(q_arr, mc_arr, color="#ef4444", linewidth=2.5, label=f"Marginal Cost: MC(x) = C'(x) = {2*a:g}x + {self._fmt_num(b)}")

            y_top_mr = max(1000.0, float(np.max(mc_arr)), p) * 1.18
            ax.set_ylim(0, y_top_mr)

            ax.scatter([0], [b], color="#ef4444", s=50, zorder=5)
            ax.annotate(f"MC(0) = {self._fmt_rp(b)}", xy=(0, b), xytext=(10, -16), textcoords="offset points",
                        fontsize=8, fontweight="bold", color="#ef4444")

            if 0 <= q_opt <= self.q_max:
                ax.scatter([q_opt], [p], color="#f59e0b", s=110, zorder=5, label=f"Titik MR = MC di x* = {q_opt:.1f}")
                ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, alpha=0.8)
                ax.annotate(
                    f"KONDISI OPTIMUM (MR = MC):\nx* = {q_opt:.1f} porsi\nTarif Marjinal = {self._fmt_rp(p)}",
                    xy=(q_opt, p),
                    xytext=(125, -70),
                    textcoords="offset points",
                    ha="center",
                    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9, fontweight="bold", color=text_color,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#f59e0b", alpha=0.9)
                )

            ax.fill_between(q_arr, mr_arr, mc_arr, where=(q_arr <= q_opt), interpolate=True, color="#10b981", alpha=0.15, label="MR > MC (Keuntungan Bertambah)")
            ax.fill_between(q_arr, mr_arr, mc_arr, where=(q_arr >= q_opt), interpolate=True, color="#ef4444", alpha=0.15, label="MR < MC (Keuntungan Berkurang)")

            slider_mc = 2.0 * a * slider_q + b
            ax.scatter([slider_q], [p], color="#3b82f6", s=45, zorder=6)
            ax.scatter([slider_q], [slider_mc], color="#ec4899", s=45, zorder=6)
            ax.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1.2, alpha=0.7)

            ax.legend(loc="upper left", framealpha=0.85, facecolor=bg_color, labelcolor=text_color, fontsize=8)
            create_hover_elements(ax, "marginal")

        elif mode == "Multi-Grafik (3-in-1 Dashboard)":
            gs = self.fig.add_gridspec(2, 2, hspace=0.58, wspace=0.32)
            ax1 = self.fig.add_subplot(gs[0, :])
            ax2 = self.fig.add_subplot(gs[1, 0])
            ax3 = self.fig.add_subplot(gs[1, 1])

            style_axis(ax1, "Kurva Keuntungan f(x)", "Porsi (x)", "Keuntungan (Rp)")
            ax1.plot(q_arr, profit_arr, color="#10b981", linewidth=2, label="f(x)")
            ax1.axhline(0, color="#ef4444", linestyle=":", linewidth=1)
            ax1.fill_between(q_arr, profit_arr, 0, where=(profit_arr >= 0), interpolate=True, color="#10b981", alpha=0.14)
            ax1.fill_between(q_arr, profit_arr, 0, where=(profit_arr < 0), interpolate=True, color="#ef4444", alpha=0.14)
            if 0 <= q_opt <= self.q_max:
                ax1.scatter([q_opt], [p_opt], color="#f59e0b", s=85, zorder=5, label=f"x*={q_opt:.1f}")
                ax1.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1)
            if res["min_both_ends"]:
                ax1.scatter([0, float(self.q_max)], [res["f_zero"], res["f_end"]], color="#ef4444", s=45, zorder=5)
            else:
                ax1.scatter([res["x_min"]], [res["f_min"]], color="#ef4444", s=45, zorder=5)
            if q_bep1 is not None and 0.0 <= q_bep1 <= float(self.q_max):
                ax1.scatter([q_bep1], [0], color="#60a5fa", s=40, zorder=5)
            if q_bep2 is not None and 0.0 <= q_bep2 <= float(self.q_max):
                ax1.scatter([q_bep2], [0], color="#60a5fa", s=40, zorder=5)
            ax1.scatter([slider_q], [slider_p], color="#ec4899", s=38, zorder=6)
            ax1.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1, alpha=0.7)
            ax1.legend(loc="upper right", fontsize=7, facecolor=bg_color, labelcolor=text_color)
            create_hover_elements(ax1, "profit")

            style_axis(ax2, "Pendapatan R(x) vs Biaya C(x)", "Porsi (x)", "Rupiah (Rp)")
            ax2.plot(q_arr, r_arr, color="#3b82f6", linewidth=2, label="R(x)")
            ax2.plot(q_arr, c_arr, color="#ef4444", linewidth=2, label="C(x)")
            if 0 <= q_opt <= self.q_max:
                ax2.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linewidth=2, label="Gap Max")
            if q_bep1 is not None and 0.0 <= q_bep1 <= float(self.q_max):
                ax2.scatter([q_bep1], [p * q_bep1], color="#60a5fa", s=35, zorder=5)
            if q_bep2 is not None and 0.0 <= q_bep2 <= float(self.q_max):
                ax2.scatter([q_bep2], [p * q_bep2], color="#60a5fa", s=35, zorder=5)
            ax2.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1, alpha=0.7)
            ax2.legend(loc="upper left", fontsize=7, facecolor=bg_color, labelcolor=text_color)
            create_hover_elements(ax2, "rev_cost")

            style_axis(ax3, "Marjinal MR vs MC", "Porsi (x)", "Rp/porsi")
            ax3.plot(q_arr, mr_arr, color="#3b82f6", linewidth=2, label="MR")
            ax3.plot(q_arr, mc_arr, color="#ef4444", linewidth=2, label="MC")
            ax3.set_ylim(0, max(1000.0, float(np.max(mc_arr)), p) * 1.18)
            ax3.fill_between(q_arr, mr_arr, mc_arr, where=(q_arr <= q_opt), interpolate=True, color="#10b981", alpha=0.14)
            ax3.fill_between(q_arr, mr_arr, mc_arr, where=(q_arr >= q_opt), interpolate=True, color="#ef4444", alpha=0.14)
            if 0 <= q_opt <= self.q_max:
                ax3.scatter([q_opt], [p], color="#f59e0b", s=70, zorder=5, label=f"MR=MC ({q_opt:.1f})")
                ax3.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1)
            ax3.axvline(slider_q, color="#ec4899", linestyle=":", linewidth=1, alpha=0.7)
            ax3.legend(loc="upper left", fontsize=7, facecolor=bg_color, labelcolor=text_color)
            create_hover_elements(ax3, "marginal")

        if mode == "Multi-Grafik (3-in-1 Dashboard)":
            self.fig.subplots_adjust(top=0.92, bottom=0.10, left=0.11, right=0.96, hspace=0.58, wspace=0.32)
        else:
            try:
                self.fig.tight_layout()
            except Exception:
                pass
        try:
            self.canvas.draw()
        except Exception:
            pass

    def _on_plot_hover(self, event):
        if not event.inaxes or event.inaxes not in self.hover_items or event.xdata is None:
            self._hide_hover_elements()
            return

        active_ax = event.inaxes
        items = self.hover_items[active_ax]
        try:
            q_raw = float(event.xdata)
        except (TypeError, ValueError):
            self._hide_hover_elements()
            return
        if not math.isfinite(q_raw):
            self._hide_hover_elements()
            return
        q = max(0.0, min(float(self.q_max), q_raw))

        if self._last_hover_q is not None and abs(q - self._last_hover_q) < 0.2 and self._last_hover_ax == active_ax:
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
        is_near_end = abs(q - float(self.q_max)) <= snap_rad
        is_near_opt = (0.0 <= q_opt <= float(self.q_max)) and abs(q - q_opt) <= snap_rad
        is_near_bep1 = q_bep1 is not None and (0.0 <= q_bep1 <= float(self.q_max)) and abs(q - q_bep1) <= snap_rad
        is_near_bep2 = q_bep2 is not None and (0.0 <= q_bep2 <= float(self.q_max)) and abs(q - q_bep2) <= snap_rad
        is_near_slider = abs(q - slider_q) <= (snap_rad * 0.8)

        if is_near_opt:
            q = q_opt
            label_tag = "TITIK KRITIS (NILAI MAKSIMUM MUTLAK)"
            accent_col = "#f59e0b"
        elif is_near_zero:
            q = 0.0
            is_min_zero = res["x_min"] == 0.0 or res["min_both_ends"]
            label_tag = "TITIK UJUNG DOMAIN x=0 (NILAI MINIMUM MUTLAK)" if is_min_zero else "TITIK UJUNG DOMAIN x=0 (BIAYA TETAP)"
            accent_col = "#ef4444"
        elif is_near_bep1 and q_bep1 is not None:
            q = float(q_bep1)
            label_tag = "TITIK IMPAS BAWAH (BEP 1: f(x) = 0)"
            accent_col = "#60a5fa"
        elif is_near_bep2 and q_bep2 is not None:
            q = float(q_bep2)
            label_tag = "TITIK IMPAS ATAS (BEP 2: f(x) = 0)"
            accent_col = "#60a5fa"
        elif is_near_end and (res["x_min"] == float(self.q_max) or res["min_both_ends"]):
            q = float(self.q_max)
            label_tag = f"TITIK UJUNG DOMAIN x={self.q_max} (NILAI MINIMUM MUTLAK)"
            accent_col = "#ef4444"
        elif is_near_slider:
            q = slider_q
            label_tag = "TITIK PORSI SIMULASI AKTIF"
            accent_col = "#ec4899"
        else:
            label_tag = "TITIK PENELUSURAN KURVA f(x)"
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
                min_x_lbl = f"0 & {self.q_max}" if res["min_both_ends"] else f"{res['x_min']:g}"
                text_info = (
                    f"[{label_tag}]\n"
                    f"Titik Kritis x*: {q:.1f} porsi/hari (f'(x*) = 0)\n"
                    f"Nilai Maksimum f(x*): Rp {profit:,.0f}\n"
                    f"Fungsi Pendapatan R(x*): Rp {r:,.0f}\n"
                    f"Fungsi Biaya C(x*): Rp {cost:,.0f}\n"
                    f"Biaya Rata-Rata AC: Rp {ac:,.0f}/porsi\n"
                    f"Turunan Pertama f'(x*): Rp 0/porsi (Kondisi Stasioner)\n"
                    f"Uji Turunan Pertama: (+) f'({res['x_kiri']:g})>0 -> 0 -> (-) f'({res['x_kanan']:g})<0 (Maks)\n"
                    f"Nilai Minimum Global: f({min_x_lbl}) = {self._fmt_rp(res['f_min'])}\n"
                    f"Status: Puncak Tertinggi Nilai Maksimum Global"
                ).replace(",", ".")
            elif is_near_zero:
                min_status = f"Nilai Minimum Mutlak pada Domain [0, {self.q_max}]" if (res["x_min"] == 0.0 or res["min_both_ends"]) else f"Ujung Kiri (Min Mutlak di x={res['x_min']:g}: {self._fmt_rp(res['f_min'])})"
                f_prime_0_txt = f"+{self._fmt_rp(p - b)}" if (p - b) > 0 else self._fmt_rp(p - b)
                f_prime_0_dir = "f' > 0" if (p - b) > 0 else ("f' < 0" if (p - b) < 0 else "f' = 0")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (x): 0,0 porsi/hari\n"
                    f"Nilai Fungsi f(0): -Rp {c:,.0f} (Defisit Biaya Tetap)\n"
                    f"Fungsi Pendapatan R(0): Rp 0\n"
                    f"Biaya Total C(0): Rp {c:,.0f} (Fixed Cost)\n"
                    f"Turunan Pertama f'(0): {f_prime_0_txt}/porsi ({f_prime_0_dir})\n"
                    f"Status: {min_status}"
                ).replace(",", ".")
            elif is_near_bep1 or is_near_bep2:
                bep_name = "BEP 1 (Bawah)" if is_near_bep1 else "BEP 2 (Atas)"
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Impas ({bep_name}): {q:.1f} porsi/hari\n"
                    f"Nilai Fungsi f(x): Rp 0 (Pulang Pokok)\n"
                    f"Pendapatan = Biaya: Rp {r:,.0f}\n"
                    f"Turunan Pertama f'(x): Rp {p_prime:,.0f}/porsi\n"
                    f"Status: Ambang Batas Wilayah Keuntungan (f(x) = 0)"
                ).replace(",", ".")
            elif is_near_end and (res["x_min"] == float(self.q_max) or res["min_both_ends"]):
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (x): {q:.1f} porsi/hari\n"
                    f"Nilai Minimum f({self.q_max}): {self._fmt_rp(profit)}\n"
                    f"Fungsi Pendapatan R({self.q_max}): Rp {r:,.0f}\n"
                    f"Biaya Total C({self.q_max}): Rp {cost:,.0f}\n"
                    f"Turunan Pertama f'({self.q_max}): {self._fmt_rp(p_prime)}/porsi\n"
                    f"Status: Nilai Minimum Mutlak pada Domain [0, {self.q_max}]"
                ).replace(",", ".")
            elif is_near_slider:
                diff_s = q - q_opt
                s_note = f"+{diff_s:.1f} porsi dari opt" if diff_s > 0 else (f"{diff_s:.1f} porsi dari opt" if diff_s < 0 else "Tepat di optimum")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Terpilih: {q:.1f} porsi/hari ({s_note})\n"
                    f"Fungsi Keuntungan f(x): Rp {profit:,.0f}\n"
                    f"Pendapatan Total R(x): Rp {r:,.0f}\n"
                    f"Biaya Total C(x): Rp {cost:,.0f}\n"
                    f"Turunan Pertama f'(x): Rp {p_prime:,.0f}/porsi\n"
                    f"Status: Posisi Slider Simulasi Interaktif"
                ).replace(",", ".")
            else:
                st_txt = "Zona Laba Positif (f(x) > 0)" if profit > 0 else ("Titik Impas (f(x) = 0)" if abs(profit) < 1 else "Zona Rugi Defisit (f(x) < 0)")
                rec_txt = "Tambah porsi (f'(x) > 0)" if p_prime > 50 else ("Kurangi porsi (f'(x) < 0)" if p_prime < -50 else "Puncak laba (f'(x) = 0)")
                uji1_txt = "Monoton Naik (f'(x) > 0, kiri x*)" if p_prime > 1e-6 else ("Monoton Turun (f'(x) < 0, kanan x*)" if p_prime < -1e-6 else "Titik Balik Stasioner (f'(x) = 0)")
                text_info = (
                    f"[{label_tag}]\n"
                    f"Porsi Produksi (x): {q:.1f} porsi/hari\n"
                    f"Fungsi Keuntungan f(x): Rp {profit:,.0f}\n"
                    f"Pendapatan Total R(x): Rp {r:,.0f}\n"
                    f"Biaya Total C(x): Rp {cost:,.0f}\n"
                    f"Biaya Rata-Rata AC(x): Rp {ac:,.0f}/porsi\n"
                    f"Turunan Pertama f'(x): Rp {p_prime:,.0f}/porsi\n"
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
                    f"Laba Marjinal f'(x*): Rp 0/porsi\n"
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
                    f"Laju Laba f'(x): Rp {diff:,.0f}/porsi\n"
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

        patch = annot.get_bbox_patch()
        if patch is not None:
            patch.set_edgecolor(accent_col)
        annot.set_visible(True)

        for other_ax, other_items in self.hover_items.items():
            if other_ax != active_ax:
                other_items["dot"].set_visible(False)
                other_items["dot2"].set_visible(False)
                other_items["gap_line"].set_visible(False)
                other_items["vline"].set_visible(False)
                other_items["hline"].set_visible(False)
                other_items["annot"].set_visible(False)

        try:
            self.canvas.draw_idle()
        except Exception:
            pass

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
            try:
                self.canvas.draw_idle()
            except Exception:
                pass


if __name__ == "__main__":
    app = KalkulusUMKMApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        try:
            app.destroy()
        except tk.TclError:
            pass
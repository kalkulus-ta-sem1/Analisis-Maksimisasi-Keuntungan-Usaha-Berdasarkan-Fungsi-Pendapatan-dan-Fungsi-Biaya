<div align="center">

# Analisis Maksimisasi Keuntungan Usaha Berdasarkan Fungsi Pendapatan dan Fungsi Biaya

**Aplikasi Simulasi Kalkulus Diferensial & Integral untuk Optimasi Keuntungan UMKM**  
Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi — Tasikmalaya (2026)

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/CustomTkinter-6.0%2B-1E3A8A?style=for-the-badge&logo=python&logoColor=white" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=for-the-badge&logo=python&logoColor=white" alt="Matplotlib" />
  <img src="https://img.shields.io/badge/NumPy-1.26%2B-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/Pillow-10.0%2B-4B5563?style=for-the-badge&logo=python&logoColor=white" alt="Pillow" />
</p>

</div>

---

## Deskripsi Proyek

Proyek ini mengimplementasikan konsep **Kalkulus Diferensial** dan **Kalkulus Integral** ke dalam sebuah aplikasi desktop interaktif berbasis Python GUI untuk memecahkan permasalahan optimasi ekonomi mikro pada Usaha Mikro, Kecil, dan Menengah (UMKM) kuliner, khususnya menentukan jumlah porsi produksi harian (`x`) yang menghasilkan keuntungan bersih maksimum (`f(x*)`).

Dalam operasional UMKM harian, penambahan produksi memang menaikkan pendapatan total `R(x)`, tetapi juga memicu kenaikan biaya marjinal `MC(x)` akibat keterbatasan kapasitas alat/tenaga kerja dan pembelian bahan tambahan secara mendadak (disekonomi skala). Aplikasi ini memodelkan hubungan tersebut secara analitis dan numerik lengkap dengan basis data harga pasar tradisional Tasikmalaya (Pasar Induk Cikurubuk) menggunakan pendekatan belanja harian non-borongan.

---

## Identitas Akademik & Tim Penyusun

- **Mata Kuliah**: Kalkulus Dasar (*Team Project-Based Learning*)
- **Dosen Pengampu**: Neng Ika Kurniati, S.Si., M.Cs.
- **Instansi**: Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi, Tasikmalaya
- **Tahun**: 2026

### Kelompok 3

| No. | Nama Lengkap | NPM |
| :---: | :--- | :---: |
| 1 | Muhammad Fikri Haikal | `267006111030` |
| 2 | Muhammad Amin Al Faruq | `267006111104` |
| 3 | Hirzan Khairurrizal Ahza | `267006111168` |
| 4 | Fahri Fauzira | `267006111171` |
| 5 | Mochammad Fauzan Rizaldy | `267006111173` |
| 6 | Anindi Nurmaleka | `267006111176` |

---

## Teknologi & Pustaka yang Digunakan

Seluruh dependensi tercatat pada [`requirements.txt`](requirements.txt) dan berjalan pada **Python 3.10+** (lingkungan `.venv` proyek menggunakan Python 3.14):

| Teknologi / Pustaka | Versi Minimal | Peran dalam Aplikasi |
| :--- | :--- | :--- |
| **Python** | `3.10+` | Bahasa pemrograman inti & komputasi analitis/numerik |
| **CustomTkinter** | `>= 6.0.0` | Antarmuka desktop modern (tema Dark/Light, panel, slider, tab, UI kertas) |
| **Matplotlib** | `>= 3.8.0` | Plotting kurva interaktif (`TkAgg`), hover tooltip, toolbar, & rendering rumus STIX (`Agg`) |
| **NumPy** | `>= 1.26.0` | Komputasi array kurva, diskriminan BEP, dan integrasi numerik trapesium |
| **Pandas** | `>= 2.0.0` | Strukturisasi data tabel simulasi dan ekspor `.csv` / `.xlsx` |
| **Pillow (PIL)** | `>= 10.0.0` | Pengolahan gambar rumus STIX untuk tampilan kertas pada CustomTkinter |
| **Tkinter / ttk** | Bawaan Python | Dialog file, notifikasi error/info, splitter panel, dan `Treeview` tabel data |

---

## Landasan Matematis & Rumus yang Diterapkan

### 1. Fungsi Bisnis & Turunan Pertama
Untuk jumlah porsi harian `x` pada domain tertutup `[0, x_max]`:

- **Pendapatan Total**: `R(x) = p · x` dengan Pendapatan Marjinal `MR(x) = R'(x) = p`
- **Biaya Total**: `C(x) = a·x² + b·x + c` dengan Biaya Marjinal `MC(x) = C'(x) = 2ax + b`
- **Fungsi Keuntungan**: `f(x) = R(x) - C(x) = -a·x² + (p - b)·x - c`
- **Laba Marjinal (Turunan Pertama)**: `f'(x) = MR(x) - MC(x) = -2ax + (p - b)`

### 2. Optimasi, Uji Turunan Pertama, & Teorema Nilai Ekstrem
- **Titik Kritis Stasioner**: `f'(x) = 0  <==>  MR(x) = MC(x)  ==>  x* = (p - b) / (2a)`
- **Uji Turunan Pertama**: Memverifikasi perubahan tanda `f'(x)` dari positif (`+`) di kiri `x*` menuju negatif (`-`) di kanan `x*`, membuktikan `f(x*)` sebagai **Nilai Maksimum Mutlak**.
- **Teorema Nilai Ekstrem pada `[0, x_max]`**: Mengevaluasi titik kritis interior beserta kedua ujung interval untuk menentukan **Nilai Minimum Mutlak** `min(f(0), f(x_max))`.
- **Titik Impas (*Break-Even Point* / BEP)**: Akar persamaan `f(x) = 0` menggunakan diskriminan `D = (p - b)² - 4ac` untuk menemukan batas minimum (`BEP 1`) dan batas maksimum (`BEP 2`) zona untung.

### 3. Integrasi Rumus Integral PDF (Kode `A.1`–`A.5` & `B.1`–`B.5`)
Diimplementasikan secara terstruktur dalam [`src/kalkulus_integral.py`](src/kalkulus_integral.py):

- **Teorema Dasar Kalkulus I (`B.5`)**: Merekonstruksi `R(x)`, `C(x)`, dan `f(x)` dari fungsi laju marjinal serta memverifikasi limit startup `lim_{x -> 0} (1/x) ∫[0..x] MC(t) dt = b`.
- **Substitusi `u` + Ubah Batas (`B.1` / `A.1`)**: Menghitung Total Biaya Variabel Optimal `VC(x*) = ∫[0..x*] (2ax + b) dx`.
- **Pecah Pecahan Polinom & `ln|x|` (`A.3`)**: Mengintegralkan Biaya Rata-Rata `AC(x) = C(x)/x = ax + b + c/x`.
- **Integral Nilai Mutlak Linier (`B.3`)**: Memecah `∫[0..x_max] |f'(x)| dx` pada titik kritis `x*` untuk memisahkan total kenaikan laba vs pemborosan over-produksi.
- **Integral Nilai Mutlak Kuadrat (`B.4`)**: Memecah `∫[0..x_max] |f(x)| dx` pada akar-akar BEP untuk menghitung area surplus laba vs area defisit.
- **Integral Trigonometri Substitusi `u = ωt` (`A.4` & `B.2`)**: Proyeksi akumulasi laba 30 hari dengan gelombang penjualan mingguan `L(t) = f* + Δf·(0.5 sin(ωt) + sin(2ωt))`.

---

## Fitur Lengkap Aplikasi GUI

### Panel Kontrol Samping (Sidebar)
- **5 Pilihan Preset Usaha**:
  1. `UMKM Ketoprak (Harian Tasikmalaya)` *(Default)*
  2. `UMKM Warung Nasi Goreng`
  3. `UMKM Kopi Susu Kekinian`
  4. `UMKM Ketoprak (Studi Kasus Laporan UNSIL)`
  5. `Kustom Parameter Sendiri`
- **Otomasi Pasar Daerah Tasikmalaya & Indonesia**:
  - Pilihan wilayah (`Kota Tasikmalaya (Pasar Cikurubuk)`, `Kab. Tasikmalaya (Singaparna & Sekitar)`, `Rata-rata Nasional (Indonesia)`).
  - Simulasi 4 kondisi harga pasar (`Harga Normal Pasar`, `Harga Turun / Panen Raya`, `Harga Sedang Naik`, `Lonjakan Hari Besar / HBKN`).
  - Switch `Auto-Isi Modal Harian (Non-Borongan)` untuk menghitung `b`, `c`, `a`, dan `x_max` secara otomatis dari harga jual `p`, dengan pemecahan biaya tetap (sewa lapak, LPG 3 kg, listrik, penyusutan alat) menjadi biaya riil **per hari**.
- **Slider Simulasi Interaktif (`x`)** & kartu status langsung (`R(x)`, `C(x)`, `f(x)`, `f'(x)`).
- **Splitter Geser** untuk mengatur lebar sidebar (`280`–`650 px`) dan tombol pergantian tema **Dark / Light**.

### 6 Tab Utama
1. **`Visualisasi Grafik`**:
   - 4 mode grafik: `Kurva Keuntungan f(x)`, `Pendapatan R(x) vs Biaya C(x)`, `Pendekatan Marjinal (MR vs MC)`, dan `Multi-Grafik (3-in-1 Dashboard)`.
   - Hover tooltip interaktif yang menempel (*snapping*) ke titik kritis `x*`, titik ujung domain, `BEP 1`, `BEP 2`, dan posisi slider aktif.
   - Navigation toolbar (Zoom, Pan, Reset) dan ekspor gambar resolusi tinggi (`PNG`, `JPG`, `PDF`).
2. **`Rumus Kalkulus (PDF)`**:
   - Tampilan **Lembar Kertas Putih (Paper UI)** berfont **Times New Roman** dengan rendering notasi matematika asli (**STIX Mathtext**) dan baris chip parameter aktif yang rapi dalam satu baris.
   - Menyajikan Bab I–VII lengkap mulai dari formulasi FTC I hingga proyeksi 30 hari dan limit L'Hôpital.
3. **`Integral (PDF)`**:
   - Sub-mode 1 (**`Penerapan Integral di UMKM (Rumus PDF)`**): 4 panel grafik integral (`B.3`, `B.4`, `A.3 & B.1`, `A.4/B.2`) beserta penjelasan lembar kertas.
   - Sub-mode 2 (**`Kalkulator 10 Soal Rumus PDF (A.1 - B.5)`**): Penyelesai interaktif untuk seluruh 10 soal PDF lengkap dengan input `x uji`, penyesuaian domain otomatis, verifikasi komputasi numerik, dan plot fungsi/integral.
4. **`Tabel Simulasi`**:
   - Tabel data komputasi dengan langkah tiap 5 porsi serta baris titik kritis `x*` dan BEP yang ditandai warna khusus.
   - Ekspor data ke **CSV** (`UTF-8 BOM`) maupun **Excel** (`.xlsx` apabila `openpyxl` tersedia).
5. **`Harga Tasik`**:
   - Rincian takaran & komponen modal bahan baku harian per porsi (`b`) dan estimasi belanja harian non-borongan.
   - Rincian biaya tetap harian (`c`) terpecah per hari, simulasi perbandingan 4 skenario fluktuasi harga, serta katalog 30+ komoditas acuan Pasar Cikurubuk & Indonesia (`2025–2026`).
6. **`Laporan Proyek`**:
   - Dokumen laporan ilmiah lengkap dalam format lembaran kertas putih, diawali **Halaman Sampul / Identitas Resmi Kelompok 3** hingga daftar pustaka.

---

## Ringkasan Perbandingan Dua Studi Kasus Ketoprak

| Parameter / Hasil | Studi Kasus Harian Tasikmalaya *(Default App)* | Studi Kasus Awal Laporan UNSIL *(Static Preset)* |
| :--- | :--- | :--- |
| Harga Jual (`p`) | Rp 15.000 / porsi | Rp 15.000 / porsi |
| Biaya Tetap Harian (`c`) | Rp 14.500 / hari *(pecahan harian riil)* | Rp 60.000 / hari |
| Modal Bahan / Porsi (`b`) | Rp 6.700 / porsi *(belanja non-borongan)* | Rp 8.000 / porsi |
| Koefisien Disekonomi (`a`) | `60` | `50` |
| Fungsi Keuntungan `f(x)` | `-60x² + 8.300x - 14.500` | `-50x² + 7.000x - 60.000` |
| Titik Kritis (`x*`) | `69,17` porsi/hari (`~69` porsi) | `70` porsi/hari |
| Laba Maksimum `f(x*)` | **Rp 272.542 / hari** | **Rp 185.000 / hari** |
| Titik Impas (`BEP 1` & `BEP 2`) | `1,77` dan `136,56` porsi | `9,17` dan `130,83` porsi |

---

## Instalasi & Cara Menjalankan

### Opsi 1: Launcher Otomatis Windows
Klik ganda berkas [`run_app.bat`](run_app.bat) atau jalankan lewat Command Prompt/PowerShell:
```bat
run_app.bat
```
Skrip otomatis memakai `.venv\Scripts\python.exe` jika virtual environment lokal tersedia, atau memeriksa Python sistem dan `requirements.txt` sebelum membuka aplikasi.

### Opsi 2: Menggunakan Terminal / PowerShell
1. Siapkan virtual environment dan pasang dependensi:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Jalankan aplikasi GUI utama:
   ```powershell
   python app.py
   ```
3. *(Opsional)* Generate ulang 3 gambar grafik beresolusi tinggi (`300 dpi`) ke folder `assets/`:
   ```powershell
   python scripts/generate_graph.py
   ```

---

## Struktur Proyek

```text
Analisis-Maksimisasi-Keuntungan-Usaha-Berdasarkan-Fungsi-Pendapatan-dan-Fungsi-Biaya/
├── assets/
│   ├── grafik_keuntungan_maksimum.png          # Grafik HD Kurva Keuntungan f(q)
│   ├── grafik_marjinal_mr_mc.png               # Grafik HD Pendekatan Marjinal MR vs MC
│   └── grafik_pendapatan_vs_biaya.png          # Grafik HD Perbandingan R(q) vs C(q)
├── docs/
│   └── Laporan_Proyek_Akhir_Kalkulus_UMKM.md   # Naskah laporan ilmiah lengkap
├── scripts/
│   └── generate_graph.py                       # Generator 3 grafik HD ke folder assets/
├── src/
│   ├── __init__.py                             # Penanda package Python modul sumber
│   ├── kalkulus_integral.py                    # Perhitungan integral UMKM & 10 soal PDF (A.1-B.5)
│   └── tasik_market_data.py                    # Basis data harga Pasar Tasikmalaya & skenario harian
├── .gitignore                                  # Pengabaian cache, IDE, dan .venv
├── app.py                                      # Titik masuk utama aplikasi GUI CustomTkinter
├── README.md                                   # Dokumentasi teknis & panduan proyek
├── requirements.txt                            # Daftar pustaka Python yang dibutuhkan
└── run_app.bat                                 # Launcher Windows satu klik
```

---

## Aset Visualisasi Laporan (`assets/`)

Skrip [`scripts/generate_graph.py`](scripts/generate_graph.py) menghasilkan tiga grafik statis beresolusi tinggi (`300 dpi`) untuk kebutuhan dokumentasi dan laporan:

- [`assets/grafik_keuntungan_maksimum.png`](assets/grafik_keuntungan_maksimum.png) — Kurva Keuntungan Objektif `f(q)` lengkap dengan titik kritis, BEP, dan zona laba/rugi.
- [`assets/grafik_pendapatan_vs_biaya.png`](assets/grafik_pendapatan_vs_biaya.png) — Perbandingan Pendapatan Total `R(q)` vs Biaya Total `C(q)` beserta celah laba maksimum.
- [`assets/grafik_marjinal_mr_mc.png`](assets/grafik_marjinal_mr_mc.png) — Optimasi Marjinal pada perpotongan `MR = MC`.

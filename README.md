<div align="center">

# Analisis Maksimisasi Keuntungan Usaha Berdasarkan Fungsi Pendapatan dan Fungsi Biaya

**Aplikasi Simulasi Kalkulus Diferensial untuk Optimasi Keuntungan UMKM**  
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

Proyek ini mengimplementasikan konsep **Kalkulus Diferensial** ke dalam sebuah aplikasi desktop interaktif berbasis Python GUI untuk memecahkan permasalahan optimasi ekonomi mikro pada Usaha Mikro, Kecil, dan Menengah (UMKM) kuliner, khususnya menentukan jumlah porsi produksi harian (`x`) yang menghasilkan keuntungan bersih maksimum (`f(x*)`).

Dalam operasional UMKM harian, penambahan produksi menaikkan pendapatan total `R(x)`, tetapi juga memicu kenaikan biaya marjinal `MC(x)` akibat keterbatasan kapasitas alat/tenaga kerja serta pembelian bahan tambahan secara mendadak (disekonomi skala). Aplikasi ini berfokus pada **3 inti pembahasan kalkulus**—**Turunan Pertama**, **Titik Kritis**, dan **Nilai Maksimum & Minimum**—dilengkapi basis data harga pasar tradisional Tasikmalaya (Pasar Induk Cikurubuk) menggunakan pendekatan belanja harian non-borongan.

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
| **NumPy** | `>= 1.26.0` | Komputasi array kurva dan diskriminan titik impas (BEP) |
| **Pandas** | `>= 2.0.0` | Strukturisasi data tabel simulasi dan ekspor `.csv` / `.xlsx` |
| **Pillow (PIL)** | `>= 10.0.0` | Pengolahan gambar rumus STIX untuk tampilan kertas pada CustomTkinter |
| **Tkinter / ttk** | Bawaan Python | Dialog file, notifikasi error/info, splitter panel, dan `Treeview` tabel data |

---

## 3 Inti Pembahasan Kalkulus yang Diterapkan

Untuk jumlah porsi harian `x` pada domain tertutup `[0, x_max]`, dengan pendapatan total `R(x) = p · x`, biaya total `C(x) = a·x² + b·x + c`, dan fungsi keuntungan `f(x) = R(x) - C(x) = -a·x² + (p - b)·x - c`:

### 1. Turunan Pertama (`f'(x)`)
- **Pendapatan Marjinal**: `MR(x) = R'(x) = p`
- **Biaya Marjinal**: `MC(x) = C'(x) = 2ax + b`
- **Laba Marjinal**: `f'(x) = MR(x) - MC(x) = -2ax + (p - b)`
- **Uji Turunan Pertama**: Memeriksa perubahan tanda `f'(x)` dari positif (`+`, kurva naik) di interval kiri `x*` menuju negatif (`-`, kurva turun) di interval kanan `x*`.

### 2. Titik Kritis (`x*`)
- Syarat stasioner tercapai saat turunan pertama bernilai nol:
  `f'(x) = 0  <==>  MR(x) = MC(x)  ==>  x* = (p - b) / (2a)`
- Menandai puncak kurva tempat tambahan pendapatan per porsi tepat sama dengan tambahan biaya per porsi.

### 3. Nilai Maksimum & Nilai Minimum (Teorema Nilai Ekstrem)
- Pada domain tertutup `[0, x_max]`, kandidat nilai ekstrem mutlak terdiri atas titik kritis interior `x*` dan kedua ujung interval (`x = 0` dan `x = x_max`):
  - **Nilai Maksimum Mutlak**: `f(x*)` apabila `x*` berada di interior dan lolos Uji Turunan Pertama (`+ -> 0 -> -`), atau titik ujung tertinggi jika di luar interior.
  - **Nilai Minimum Mutlak**: `min(f(0), f(x_max))`.
  - **Titik Impas (*Break-Even Point* / BEP)**: Akar `f(x) = 0` melalui diskriminan `D = (p - b)² - 4ac` untuk mengetahui batas minimum (`BEP 1`) dan batas maksimum (`BEP 2`) zona untung.

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

### 5 Tab Utama
1. **`Visualisasi Grafik`**:
   - 4 mode grafik: `Kurva Keuntungan f(x)`, `Pendapatan R(x) vs Biaya C(x)`, `Pendekatan Marjinal (MR vs MC)`, dan `Multi-Grafik (3-in-1 Dashboard)`.
   - Hover tooltip interaktif yang menempel (*snapping*) ke titik kritis `x*`, titik ujung domain, `BEP 1`, `BEP 2`, dan posisi slider aktif.
   - Navigation toolbar (Zoom, Pan, Reset) dan ekspor gambar resolusi tinggi (`PNG`, `JPG`, `PDF`).
2. **`Rumus Kalkulus`**:
   - Tampilan **Lembar Kertas Putih (Paper UI)** berfont **Times New Roman** dengan rendering notasi matematika asli (**STIX Mathtext**) dan chip parameter aktif dalam satu baris.
   - Menyajikan 3 bagian inti secara fokus: **I. Turunan Pertama `f'(x)`**, **II. Titik Kritis `x*` & Uji Turunan Pertama**, dan **III. Nilai Maksimum, Nilai Minimum & Titik Impas (BEP)**.
3. **`Tabel Simulasi`**:
   - Tabel data komputasi dengan langkah tiap 5 porsi serta baris titik kritis `x*` dan BEP yang ditandai warna khusus.
   - Ekspor data ke **CSV** (`UTF-8 BOM`) maupun **Excel** (`.xlsx` apabila `openpyxl` tersedia).
4. **`Harga Tasik`**:
   - Rincian takaran & komponen modal bahan baku harian per porsi (`b`) dan estimasi belanja harian non-borongan.
   - Rincian biaya tetap harian (`c`) terpecah per hari, simulasi perbandingan 4 skenario fluktuasi harga, serta katalog 30+ komoditas acuan Pasar Cikurubuk & Indonesia (`2025–2026`).
5. **`Laporan Proyek`**:
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
| Turunan Pertama `f'(x)` | `-120x + 8.300` | `-100x + 7.000` |
| Titik Kritis (`x*`) | `69,17` porsi/hari (`~69` porsi) | `70` porsi/hari |
| Laba Maksimum `f(x*)` | **Rp 272.542 / hari** | **Rp 185.000 / hari** |
| Nilai Minimum Mutlak | **-Rp 28.500 / hari** *(di `x = 140`)* | **-Rp 60.000 / hari** *(di `x = 0` & `x = 140`)* |
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
│   └── tasik_market_data.py                    # Basis data harga Pasar Tasikmalaya & skenario harian
├── .gitignore                                  # Pengabaian cache, IDE, dan .venv
├── app.py                                      # Titik masuk utama aplikasi GUI CustomTkinter
├── README.md                                  # Dokumentasi teknis & panduan proyek
├── requirements.txt                            # Daftar pustaka Python yang dibutuhkan
└── run_app.bat                                 # Launcher Windows satu klik
```

---

## Aset Visualisasi Laporan (`assets/`)

Skrip [`scripts/generate_graph.py`](scripts/generate_graph.py) menghasilkan tiga grafik statis beresolusi tinggi (`300 dpi`) untuk kebutuhan dokumentasi dan laporan:

- [`assets/grafik_keuntungan_maksimum.png`](assets/grafik_keuntungan_maksimum.png) — Kurva Keuntungan Objektif `f(q)` lengkap dengan titik kritis, BEP, nilai minimum, dan zona laba/rugi.
- [`assets/grafik_pendapatan_vs_biaya.png`](assets/grafik_pendapatan_vs_biaya.png) — Perbandingan Pendapatan Total `R(q)` vs Biaya Total `C(q)` beserta celah laba maksimum.
- [`assets/grafik_marjinal_mr_mc.png`](assets/grafik_marjinal_mr_mc.png) — Optimasi Marjinal pada perpotongan `MR = MC`.

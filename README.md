# Analisis-Maksimisasi-Keuntungan-Usaha-Berdasarkan-Fungsi-Pendapatan-dan-Fungsi-Biaya

## Aplikasi Simulasi Kalkulus: Optimasi Keuntungan UMKM Ketoprak

Proyek Akhir Mata Kuliah Kalkulus Dasar
Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi (2026)

---

## Deskripsi Proyek
Aplikasi ini dikembangkan untuk mengimplementasikan kalkulus diferensial (khususnya fungsi, turunan pertama, titik kritis stasioner, dan uji turunan kedua) dalam menyelesaikan permasalahan nyata di bidang ekonomi manajerial mikro: menentukan jumlah porsi harian ketoprak yang menghasilkan keuntungan maksimum bagi pelaku UMKM.

Aplikasi dilengkapi dengan antarmuka grafis interaktif (GUI) modern berbasis CustomTkinter dan visualisasi komputasi Matplotlib, memungkinkan pengguna untuk bereksperimen mengubah parameter bisnis secara real-time.

---

## Fitur Utama Aplikasi GUI

1. Dashboard Metrik Finansial:
   - Menampilkan kuantitas porsi optimum (q*), keuntungan maksimum (P*), titik impas (Break-Even Point / BEP), dan hasil uji turunan kedua (P''(q) < 0).
2. Kontrol Parameter Fleksibel:
   - Harga jual (p), biaya tetap harian (c), biaya variabel linier (b), koefisien kuadrat disekonomi skala (a), dan batas rentang porsi.
   - Pilihan preset instan: UMKM Ketoprak (Studi Kasus Laporan), UMKM Nasi Goreng, UMKM Kopi Susu, dan Kustom Parameter.
3. Simulasi Slider Interaktif (q):
   - Geser slider untuk melihat posisi porsi harian tertentu secara langsung.
   - Kartu metrik real-time menampilkan pendapatan R(q), biaya C(q), keuntungan P(q), laju perubahan laba P'(q), serta status efisiensi (Zona Laba, Titik Optimum, Titik Impas, atau Defisit).
4. 4 Mode Visualisasi Grafik Matplotlib:
   - Mode 1: Kurva Keuntungan P(q) dengan titik puncak optimum, garis impas P=0, dan area warna laba/rugi.
   - Mode 2: Kurva Pendapatan R(q) vs Biaya Total C(q) yang memperlihatkan celah keuntungan terbesar.
   - Mode 3: Pendekatan Marjinal (MR vs MC) di mana titik optimum terjadi saat MR = MC.
   - Mode 4: Multi-Grafik 3-in-1 Dashboard yang merangkum ketiga grafik sekaligus.
   - Dilengkapi Navigation Toolbar untuk Zoom, Pan, dan Simpan Gambar.
5. Penurunan Rumus Kalkulus Lengkap (Step-by-Step):
   - Penjelasan matematis analitis dari fungsi, aturan pangkat turunan, solusi titik kritis, hingga uji konkavitas turunan kedua.
6. Tabel Data Numerik & Ekspor CSV:
   - Tabel simulasi per porsi dengan penandaan warna khusus baris optimum.
   - Fitur ekspor data tabel langsung ke file .csv atau .xlsx.
7. Pilihan Tema Visual:
   - Mendukung mode Dark Mode dan Light Mode.

---

## Instalasi & Menjalankan Program

### Cara 1: Menggunakan File Batch
Cukup klik ganda (double click) file:
```bash
run_app.bat
```
File ini akan memeriksa dependensi Python secara otomatis dan langsung membuka aplikasi.

---

### Cara 2: Menjalankan via Terminal / Command Prompt

1. Pastikan library Python terpasang:
   ```bash
   pip install -r requirements.txt
   ```

2. Jalankan aplikasi GUI:
   ```bash
   python app.py
   ```

3. Generate Gambar Grafik Resolusi Tinggi:
   ```bash
   python generate_graph.py
   ```

---

## Ringkasan Matematis Studi Kasus (UMKM Ketoprak)

| Notasi | Komponen | Rumus / Nilai |
| :---: | :--- | :--- |
| q | Variabel Bebas (Porsi/hari) | q >= 0 |
| p | Harga Jual per Porsi | Rp 15.000 |
| R(q) | Fungsi Pendapatan Total | R(q) = 15.000q |
| C(q) | Fungsi Biaya Total | C(q) = 50q² + 8.000q + 60.000 |
| P(q) | Fungsi Keuntungan | P(q) = -50q² + 7.000q - 60.000 |
| P'(q) | Turunan Pertama (Laba Marjinal) | P'(q) = -100q + 7.000 |
| q* | Titik Kritis (P'(q) = 0) | 70 porsi/hari |
| P''(q) | Uji Turunan Kedua | P''(70) = -100 < 0 (Terbukti Maksimum Mutlak) |
| P(70) | Keuntungan Maksimum | Rp 185.000 per hari |
| BEP | Titik Impas (P(q) = 0) | q1 = 9,17 dan q2 = 130,83 porsi |

---

## Struktur Berkas dalam Proyek
```text
menghitung umkm/
├── app.py                           # Kode utama aplikasi GUI interaktif
├── generate_graph.py                # Script pembuatan gambar grafik HD untuk laporan
├── requirements.txt                 # Daftar dependensi library Python
├── run_app.bat                      # Launcher satu-klik untuk Windows
├── Laporan_Proyek_Akhir_Kalkulus_UMKM.md # Dokumen laporan ilmiah lengkap
├── README.md                        # Dokumentasi teknis proyek
├── grafik_keuntungan_maksimum.png   # Grafik HD Kurva Keuntungan
├── grafik_pendapatan_vs_biaya.png   # Grafik HD Pendapatan vs Biaya
└── grafik_marjinal_mr_mc.png        # Grafik HD MR vs MC
```

---

## Tim Pengembang (Kelompok Mahasiswa)
- Program Studi: Informatika
- Fakultas: Teknik
- Universitas: Universitas Siliwangi
- Tahun: 2026

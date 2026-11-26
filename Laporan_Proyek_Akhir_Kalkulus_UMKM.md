# LAPORAN PROYEK AKHIR MATA KULIAH KALKULUS DASAR

## PENERAPAN KONSEP TURUNAN DALAM MENENTUKAN KEUNTUNGAN MAKSIMUM PADA UMKM KETOPRAK

---

**Program Studi Informatika**  
**Fakultas Teknik, Universitas Siliwangi**  
**Tahun Akademik 2026/2027**

### Disusun Oleh:
1. **[Nama Anggota 1]** – NPM: [267006xxx] *(Koordinator & Penyusun Metodologi)*
2. **[Nama Anggota 2]** – NPM: [267006xxx] *(Landasan Teori Kalkulus & Kajian Ekonomi)*
3. **[Nama Anggota 3]** – NPM: [267006xxx] *(Pemodelan Matematika & Fungsi Biaya)*
4. **[Nama Anggota 4]** – NPM: [267006xxx] *(Perhitungan Diferensial & Analisis Titik Kritis)*
5. **[Nama Anggota 5]** – NPM: [267006xxx] *(Pengembangan Perangkat Lunak GUI Python & Visualisasi)*
6. **[Nama Anggota 6]** – NPM: [267006xxx] *(Interpretasi Hasil, Kesimpulan, & Penyuntingan Laporan)*

---

## ABSTRAK
Usaha Mikro, Kecil, dan Menengah (UMKM) makanan menghadapi tantangan harian dalam menentukan kuantitas produksi yang optimal. Penambahan jumlah porsi yang diproduksi berpotensi meningkatkan omzet penjualan, namun dapat pula memicu lonjakan biaya produksi yang tidak linier (disekonomi skala) akibat kelelahan tenaga kerja, biaya lembur, dan pembelian bahan baku eceran darurat. Penelitian berbasis proyek *(Team Project-Based Learning)* ini bertujuan untuk menerapkan konsep kalkulus diferensial dalam memodelkan dan menentukan tingkat produksi harian porsi ketoprak yang menghasilkan keuntungan maksimum. 

Metode yang digunakan adalah pemodelan fungsi pendapatan $R(q)$, fungsi biaya $C(q)$, dan fungsi keuntungan $P(q)$, dilanjutkan dengan diferensiasi pertama untuk menentukan titik kritis stasioner serta uji turunan kedua untuk memverifikasi konkavitas kurva. Dengan asumsi harga jual $p = \text{Rp } 15.000$ per porsi dan fungsi biaya harian $C(q) = 50q^2 + 8.000q + 60.000$, diperoleh fungsi keuntungan $P(q) = -50q^2 + 7.000q - 60.000$. Turunan pertama $P'(q) = -100q + 7.000 = 0$ menghasilkan titik kritis pada $q^* = 70$ porsi/hari. Uji turunan kedua menghasilkan $P''(q) = -100 < 0$ untuk setiap nilai $q$, yang membuktikan bahwa titik tersebut adalah titik maksimum mutlak *(global maximum)*. Keuntungan maksimum yang diperoleh adalah sebesar $\text{Rp } 185.000$ per hari pada total omzet $\text{Rp } 1.050.000$ dan total biaya $\text{Rp } 865.000$. Analisis ini diintegrasikan ke dalam sebuah aplikasi simulasi interaktif berbasis Python GUI (*CustomTkinter & Matplotlib*) yang memudahkan pemangku kepentingan dalam melakukan analisis sensitivitas parameter bisnis secara visual.

**Kata Kunci**: *Kalkulus Dasar, Turunan Pertama, Uji Turunan Kedua, Optimasi, Keuntungan Maksimum, UMKM Ketoprak, Python GUI.*

---

## BAB I. PENDAHULUAN

### 1.1 Latar Belakang
Usaha Mikro, Kecil, dan Menengah (UMKM) merupakan tulang punggung perekonomian Indonesia, menyumbang lebih dari 60% Produk Domestik Bruto (PDB) nasional serta menyerap sebagian besar tenaga kerja. Di sektor informal perkotaan, usaha kuliner seperti pedagang ketoprak merupakan contoh nyata unit bisnis harian yang sangat dinamis. Setiap harinya, pelaku usaha dihadapkan pada keputusan strategis: **"Berapa banyak porsi ketoprak yang harus disiapkan hari ini agar keuntungan bersih mencapai tingkat tertinggi?"**

Dalam praktik nyata, menambah produksi tidak selalu berbanding lurus dengan kenaikan keuntungan. Jika produksi terlalu sedikit, penerimaan tidak mampu menutup biaya tetap harian (seperti sewa lahan gerobak, gas elpiji, dan kebersihan). Sebaliknya, jika memaksakan produksi dalam jumlah terlampau banyak dengan kapasitas gerobak tunggal, penjual akan mengalami disekonomi skala: kelelahan fisik, antrean panjang yang membuat pelanggan kabur, bahan pendukung yang mendadak habis sehingga harus dibeli eceran di warung terdekat dengan harga jauh lebih mahal, serta risiko makanan basi yang terbuang.

Konsep turunan *(derivatives)* dalam kalkulus diferensial memberikan kerangka analitis yang presisi untuk memecahkan dilema tersebut. Melalui pendekatan turunan pertama, laju perubahan sesaat dari fungsi keuntungan dapat dihitung untuk mencari titik kritis stasioner. Lebih lanjut, uji turunan kedua memastikan apakah titik kritis tersebut benar-benar menghasilkan keuntungan maksimum atau justru kerugian.

### 1.2 Identifikasi dan Rumusan Masalah
1. Bagaimana merumuskan model matematika fungsi pendapatan $R(q)$ dan fungsi biaya total $C(q)$ pada usaha ketoprak?
2. Bagaimana membentuk fungsi keuntungan total $P(q) = R(q) - C(q)$?
3. Bagaimana menerapkan turunan pertama $P'(q) = 0$ untuk menemukan titik kritis produksi?
4. Bagaimana memanfaatkan uji turunan kedua $P''(q)$ untuk membuktikan bahwa titik kritis tersebut adalah titik maksimum lokal sekaligus global?
5. Berapa jumlah porsi optimum, pendapatan total, biaya total, keuntungan maksimum, dan rentang titik impas *(Break-Even Point)* berdasarkan model?
6. Bagaimana mengimplementasikan model matematis ini ke dalam sebuah aplikasi perangkat lunak interaktif berbasis GUI Python?

### 1.3 Tujuan Proyek
1. Menerapkan konsep fungsi, turunan pertama, titik kritis, dan uji turunan kedua dalam pemodelan persoalan ekonomi mikro nyata.
2. Membangun model matematika yang menggambarkan hubungan kuantitas porsi, pendapatan, struktur biaya, dan laba pada UMKM ketoprak.
3. Menganalisis kondisi optimum melalui kesetaraan ekonomi marjinal, yaitu Pendapatan Marjinal sama dengan Biaya Marjinal ($MR = MC$).
4. Mengembangkan aplikasi komputer simulasi interaktif berbasis Python GUI (*CustomTkinter*, *Matplotlib*, dan *Pandas*) sebagai produk pendukung komputasi ilmiah.
5. Memberikan rekomendasi manajerial praktis bagi pelaku UMKM mengenai batas produksi yang menguntungkan.

### 1.4 Manfaat Proyek
- **Bagi Mahasiswa**: Memperdalam pemahaman aplikatif kalkulus dasar, melatih kemampuan abstraksi matematis, dan mengintegrasikan ilmu matematika dengan pemrograman komputer.
- **Bagi Akademisi & Dosen**: Menjadi contoh konkret implementasi pembelajaran berbasis proyek *(Team Project-Based Learning)* yang menghubungkan kalkulus dengan sains terapan dan rekayasa perangkat lunak.
- **Bagi Pelaku UMKM**: Memberikan wawasan edukatif mengenai pentingnya pencatatan biaya dan penentuan kuantitas produksi yang rasional agar terhindar dari pemborosan sumber daya.

---

## BAB II. LANDASAN TEORI

### 2.1 Konsep Fungsi dalam Ekonomi Manajerial
Fungsi menyatakan hubungan ketergantungan antara satu variabel bebas dengan variabel terikat. Dalam model ini, variabel bebas dinotasikan dengan $q$ ($q \ge 0$), yang menyatakan jumlah porsi ketoprak yang diproduksi dan terjual per hari.

1. **Fungsi Pendapatan Total (*Total Revenue* - $R(q)$)**:  
   Total penerimaan kas yang diperoleh dari penjualan $q$ unit produk pada tingkat harga satuan $p$:
   $$R(q) = p \cdot q$$

2. **Fungsi Biaya Total (*Total Cost* - $C(q)$)**:  
   Total pengeluaran yang dibutuhkan untuk memproduksi $q$ unit produk. Biaya terdiri dari biaya tetap (*Fixed Cost* - $FC$) dan biaya variabel (*Variable Cost* - $VC$):
   $$C(q) = a q^2 + b q + c$$
   - Konstanta $c$: Biaya tetap harian (tetap keluar meski $q = 0$).
   - Koefisien linier $b$: Biaya variabel dasar per unit porsi.
   - Koefisien kuadrat $a$: Parameter non-linier yang mencerminkan laju peningkatan biaya tambahan akibat keterbatasan kapasitas (*law of diminishing returns*).

3. **Fungsi Keuntungan Total Objektif ($f(q)$ atau $P(q)$)**:  
   Selisih bersih antara pendapatan total dan pengeluaran total yang diformulasikan sebagai fungsi tujuan $f(q)$:
   $$f(q) = R(q) - C(q) = -a q^2 + (p - b) q - c$$

### 2.2 Konsep Turunan Pertama $f'(q)$
Turunan pertama suatu fungsi $f(q)$ menyatakan limit dari laju perubahan rata-rata ketika perubahan nilai masukan mendekati nol:
$$f'(q) = \lim_{\Delta q \to 0} \frac{f(q + \Delta q) - f(q)}{\Delta q}$$

Berdasarkan aturan diferensiasi polinomial (Power Rule):
$$f'(q) = \frac{d}{dq} \left[-a q^2 + (p - b) q - c\right] = -2aq + (p - b)$$

Secara geometris, $f'(q)$ menyatakan gradien garis singgung kurva keuntungan pada absis $q$. Secara ekonomi manajerial, $f'(q)$ menyatakan **Keuntungan Marjinal (*Marginal Profit*)**, yaitu laju penambahan laba terhadap penambahan satu porsi produksi.

### 2.3 Konsep Titik Kritis (*Critical Point*)
Titik kritis suatu fungsi $f$ didefinisikan sebagai titik $q_c$ pada domain di mana:
1. $f'(q_c) = 0$ (Titik Stasioner), atau
2. $f'(q_c)$ tidak terdefinisi (Titik Singular).

Karena $f(q)$ adalah fungsi polinomial kuadrat kontinu dan terdiferensialkan di seluruh $\mathbb{R}$, titik kritis stasioner diperoleh dengan menyelesaikan persamaan:
$$f'(q) = 0 \iff -2aq + (p - b) = 0 \implies q_c = \frac{p - b}{2a}$$

### 2.4 Konsep Nilai Maksimum dan Nilai Minimum
Kalkulus diferensial menyediakan metode analitis yang ketat untuk menguji dan menentukan nilai ekstrem:

1. **Uji Turunan Pertama**:
   - Jika tanda $f'(q)$ bernilai positif ($f'(q) > 0$) untuk $q < q_c$ dan bernilai negatif ($f'(q) < 0$) untuk $q > q_c$, maka $f(q_c)$ merupakan **nilai maksimum lokal**.
   - Jika tanda $f'(q)$ berganti dari negatif ke positif, maka titik tersebut adalah **nilai minimum lokal**.

2. **Uji Turunan Kedua & Kecekungan (*Concavity*)**:
   Turunan kedua $f''(q) = \frac{d^2f}{dq^2} = -2a$ merepresentasikan kelengkungan kurva:
   - Jika $f''(q_c) < 0$, maka grafik berbentuk **cekung ke bawah (konkaf)**, sehingga $q_c$ merupakan titik **maksimum lokal**.
   - Jika $f''(q) < 0$ untuk seluruh $q$ dalam domain, maka $q_c$ adalah titik **maksimum mutlak (global maximum)**.

3. **Teorema Nilai Ekstrem (*Extreme Value Theorem*) pada Domain Tertutup $[0, q_{max}]$**:
   Jika fungsi $f$ kontinu pada interval tertutup $[a, b]$, maka $f$ pasti mencapai nilai maksimum mutlak dan nilai minimum mutlak pada interval tersebut, yang dapat terjadi pada titik kritis interior atau pada batas ujung interval (*endpoints*):
   - Nilai Maksimum Mutlak tercapai pada titik kritis: $\max f(q) = f(q_c)$.
   - Nilai Minimum Mutlak tercapai pada batas domain: $\min f(q) = \min \{ f(0), f(q_{max}) \}$.

### 2.5 Aplikasi Turunan dalam Optimasi UMKM
1. **Keseimbangan Ekonomi Marjinal ($MR = MC$)**:
   $$f'(q) = 0 \iff R'(q) - C'(q) = 0 \iff R'(q) = C'(q) \iff MR = MC$$
   Laba maksimal tercapai saat pendapatan marjinal dari penjualan satu porsi tepat sama dengan biaya marjinal untuk memproduksinya.

2. **Analisis Titik Impas (*Break-Even Point* - BEP)**:
   Titik impas terjadi ketika fungsi keuntungan bernilai nol ($f(q) = 0$):
   $$-a q^2 + (p - b) q - c = 0$$
   Akar-akar kuadrat ($q_{BEP1}$ dan $q_{BEP2}$) menentukan rentang interval kuantitas produksi yang menghasilkan laba bersih positif ($f(q) > 0$).

---

## BAB III. METODOLOGI DAN PEMODELAN MATEMATIKA

### 3.1 Identifikasi Objek Studi Kasus
Objek penelitian adalah pedagang ketoprak keliling/gerobak di kawasan Tasikmalaya/sekitarnya. Satu porsi ketoprak terdiri dari ketupat/lontong, tahu goreng, bihun, tauge, mentimun, sambal kacang ulek, kerupuk, dan kecap manis, disajikan dalam piring kertas/bungkus plastik.

### 3.2 Variabel dan Parameter Model
| Simbol | Deskripsi | Nilai Asumsi | Satuan |
| :---: | :--- | :---: | :---: |
| $q$ | Jumlah porsi yang diproduksi & terjual per hari | Variabel bebas ($q \ge 0$) | porsi/hari |
| $p$ | Harga jual ketoprak per porsi | $\text{Rp } 15.000$ | rupiah/porsi |
| $c$ | Biaya tetap harian (*sewa tempat, retribusi, gas, penyusutan alat*) | $\text{Rp } 60.000$ | rupiah/hari |
| $b$ | Biaya variabel bahan baku per porsi | $\text{Rp } 8.000$ | rupiah/porsi |
| $a$ | Koefisien kuadrat disekonomi skala | $50$ | rupiah/porsi² |

### 3.3 Pembentukan Model Matematika
1. **Fungsi Pendapatan Total**:
   $$R(q) = 15.000 q$$

2. **Fungsi Biaya Total**:
   $$C(q) = 50 q^2 + 8.000 q + 60.000$$

3. **Fungsi Keuntungan Total**:
   $$P(q) = R(q) - C(q)$$
   $$P(q) = 15.000 q - (50 q^2 + 8.000 q + 60.000)$$
   $$P(q) = -50 q^2 + 7.000 q - 60.000$$

---

## BAB IV. HASIL DAN PEMBAHASAN

### 4.1 Proses Perhitungan Diferensial Matematis

#### Langkah 1: Menentukan Turunan Pertama
Dengan aturan pangkat $\frac{d}{dq}[q^n] = n q^{n-1}$:
$$P'(q) = \frac{d}{dq} \left[ -50 q^2 + 7.000 q - 60.000 \right]$$
$$P'(q) = -50(2) q^{2-1} + 7.000(1) q^{1-1} - 0$$
$$P'(q) = -100 q + 7.000$$

#### Langkah 2: Menentukan Titik Kritis Stasioner
Syarat stasioner $P'(q) = 0$:
$$-100 q + 7.000 = 0$$
$$-100 q = -7.000$$
$$q^* = \frac{-7.000}{-100} = 70 \text{ porsi/hari}$$

#### Langkah 3: Uji Turunan Kedua
Diferensiasi kedua dari fungsi keuntungan:
$$P''(q) = \frac{d}{dq} \left[ -100 q + 7.000 \right] = -100$$
Evaluasi pada titik kritis $q^* = 70$:
$$P''(70) = -100 < 0$$
Karena turunan kedua bernilai negatif konstan untuk setiap $q \in [0, \infty)$, maka kurva $P(q)$ cekung ke bawah secara global. Dengan demikian, terbukti secara sah bahwa $q^* = 70$ adalah **titik maksimum mutlak *(global maximum)***.

#### Langkah 4: Evaluasi Finansial pada Titik Kritis
- **Pendapatan Total**:
  $$R(70) = 15.000 \times 70 = \text{Rp } 1.050.000$$
- **Biaya Total**:
  $$C(70) = 50(70^2) + 8.000(70) + 60.000$$
  $$C(70) = 50(4.900) + 560.000 + 60.000 = 245.000 + 560.000 + 60.000 = \text{Rp } 865.000$$
- **Keuntungan Maksimum**:
  $$P(70) = 1.050.000 - 865.000 = \text{Rp } 185.000 \text{ per hari}$$
- **Biaya Rata-Rata per Porsi (*Average Cost*)**:
  $$AC(70) = \frac{865.000}{70} \approx \text{Rp } 12.357,14 \text{/porsi}$$
- **Margin Keuntungan (*Profit Margin*)**:
  $$\frac{185.000}{1.050.000} \times 100\% \approx 17,62\%$$

#### Langkah 5: Perhitungan Titik Impas (*Break-Even Point*)
$$P(q) = 0 \iff -50 q^2 + 7.000 q - 60.000 = 0$$
Bagi kedua ruas dengan $-50$:
$$q^2 - 140 q + 1.200 = 0$$
Diskriminan $D = (-140)^2 - 4(1)(1.200) = 19.600 - 4.800 = 14.800$.
Akar persamaan kuadrat:
$$q_{1,2} = \frac{140 \pm \sqrt{14.800}}{2} = \frac{140 \pm 121,655}{2}$$
$$q_1 \approx \frac{140 - 121,655}{2} = 9,17 \text{ porsi} \implies \text{dibulatkan 10 porsi}$$
$$q_2 \approx \frac{140 + 121,655}{2} = 130,83 \text{ porsi} \implies \text{dibulatkan 130 porsi}$$
**Kesimpulan Rentang Operasional**: Usaha hanya akan menghasilkan laba positif jika menjual minimal **10 porsi** dan maksimal **130 porsi** per hari.

---

### 4.2 Tabel Simulasi Numerik Produksi Harian

| Porsi ($q$) | Pendapatan $R(q)$ | Biaya Total $C(q)$ | Keuntungan $f(q)$ | Biaya Rata-Rata | $MR$ | $MC$ | Turunan Pertama $f'(q)$ | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | Rp 0 | Rp 60.000 | -Rp 60.000 | - | Rp 15.000 | Rp 8.000 | +Rp 7.000 | **Nilai Minimum Mutlak (Biaya Tetap)** |
| 9,2 | Rp 137.586 | Rp 137.586 | Rp 0 | Rp 15.000 | Rp 15.000 | Rp 8.917 | +Rp 6.083 | **Titik Impas Bawah (BEP 1)** |
| 20 | Rp 300.000 | Rp 240.000 | Rp 60.000 | Rp 12.000 | Rp 15.000 | Rp 10.000 | +Rp 5.000 | Laba Bertumbuh (f' > 0) |
| 40 | Rp 600.000 | Rp 460.000 | Rp 140.000 | Rp 11.500 | Rp 15.000 | Rp 12.000 | +Rp 3.000 | Laba Bertumbuh (f' > 0) |
| 60 | Rp 900.000 | Rp 720.000 | Rp 180.000 | Rp 12.000 | Rp 15.000 | Rp 14.000 | +Rp 1.000 | Mendekati Puncak |
| **70** | **Rp 1.050.000** | **Rp 865.000** | **Rp 185.000** | **Rp 12.357** | **Rp 15.000** | **Rp 15.000** | **Rp 0** | **TITIK KRITIS (NILAI MAKSIMUM MUTLAK)** |
| 80 | Rp 1.200.000 | Rp 1.020.000 | Rp 180.000 | Rp 12.750 | Rp 15.000 | Rp 16.000 | -Rp 1.000 | Laba Menurun (f' < 0) |
| 100 | Rp 1.500.000 | Rp 1.360.000 | Rp 140.000 | Rp 13.600 | Rp 15.000 | Rp 18.000 | -Rp 3.000 | Laba Terkikis (f' < 0) |
| 130,8 | Rp 1.962.414 | Rp 1.962.414 | Rp 0 | Rp 15.000 | Rp 15.000 | Rp 21.083 | -Rp 6.083 | **Titik Impas Atas (BEP 2)** |
| 140 | Rp 2.100.000 | Rp 2.160.000 | -Rp 60.000 | Rp 15.429 | Rp 15.000 | Rp 22.000 | -Rp 7.000 | **Nilai Minimum Ujung Domain (Disekonomi)** |

---

### 4.3 Visualisasi Grafik Analisis

Berikut adalah visualisasi grafik yang dihasilkan oleh program:
1. **Kurva Keuntungan $P(q)$**: Memperlihatkan parabola konkaf ke bawah dengan puncak di $(70, 185.000)$ serta perpotongan sumbu horizontal pada $q = 9,17$ dan $q = 130,83$.
2. **Kurva Pendapatan $R(q)$ vs Biaya $C(q)$**: Memperlihatkan bahwa jarak vertikal terbesar antara garis linier $R(q)$ dan kurva kuadrat $C(q)$ terjadi persis saat $q = 70$.
3. **Kurva Marjinal ($MR$ vs $MC$)**: Memperlihatkan bahwa garis konstan $MR = 15.000$ berpotongan dengan garis linier $MC = 100q + 8.000$ tepat pada absis $q = 70$.

*(File visualisasi beresolusi tinggi tersedia dalam direktori: `grafik_keuntungan_maksimum.png`, `grafik_pendapatan_vs_biaya.png`, dan `grafik_marjinal_mr_mc.png`)*.

---

### 4.4 Analisis dan Pembahasan Ekonomi Manajerial
1. **Mengapa Menambah Porsi di Atas 70 Menurunkan Keuntungan?**  
   Pada kuantitas $q > 70$, nilai turunan pertama $P'(q)$ menjadi negatif. Dalam konsep ekonomi, ini menandakan bahwa Biaya Marjinal ($MC$) telah melampaui Pendapatan Marjinal ($MR$). Sebagai contoh pada porsi ke-80, biaya untuk memproduksi satu porsi tambahan adalah $\text{Rp } 16.000$, padahal harga jualnya tetap $\text{Rp } 15.000$. Akibatnya, setiap porsi tambahan di atas 70 porsi justru memotong keuntungan bersih sebesar $\text{Rp } 1.000$ per porsi.

2. **Dampak Perubahan Harga Bahan Baku (Sensitivitas Biaya)**:  
   Jika harga bahan baku (seperti kacang tanah dan cabai) naik, koefisien variabel $b$ akan meningkat. Berdasarkan rumus $q^* = \frac{p - b}{2a}$, kenaikan nilai $b$ akan menurunkan pembilang, yang menyebabkan titik produksi optimum $q^*$ bergeser ke kiri (kuantitas optimal menurun) dan keuntungan maksimal tertekan.

3. **Peran Aplikasi GUI Python dalam Pengambilan Keputusan**:  
   Perangkat lunak GUI yang dikembangkan memungkinkan penjual atau analis untuk mengubah parameter $p$, $c$, $b$, dan $a$ secara interaktif. Penggeseran slider produksi memberikan umpan balik seketika *(real-time feedback)* mengenai pendapatan, pengeluaran, keuntungan, serta status efisiensi operasional.

---

## BAB V. KESIMPULAN DAN SARAN

### 5.1 Kesimpulan
1. Konsep turunan kalkulus terbukti sangat efektif dan relevan dalam memodelkan serta menyelesaikan permasalahan optimasi ekonomi pada UMKM ketoprak.
2. Dari pemodelan fungsi biaya kuadrat $C(q) = 50q^2 + 8.000q + 60.000$ dan fungsi pendapatan linier $R(q) = 15.000q$, diperoleh fungsi keuntungan $P(q) = -50q^2 + 7.000q - 60.000$.
3. Titik kritis stasioner ditemukan melalui turunan pertama $P'(q) = -100q + 7.000 = 0$, menghasilkan kuantitas optimum $q^* = 70$ porsi/hari.
4. Uji turunan kedua $P''(70) = -100 < 0$ membuktikan secara matematis bahwa titik tersebut merupakan titik maksimum mutlak.
5. Keuntungan maksimum yang dapat diraih pelaku usaha adalah sebesar **$\text{Rp } 185.000$ per hari** (setara dengan $\pm \text{Rp } 5.550.000$ per bulan) dengan rentang aman produksi antara **10 hingga 130 porsi/hari**.
6. Aplikasi GUI Python yang dibangun berhasil mengintegrasikan pemodelan kalkulus, visualisasi grafik interaktif, navigasi parameter, dan ekspor data ke format CSV.

### 5.2 Saran
1. **Validasi Empiris Lapangan**: Mahasiswa disarankan melakukan wawancara langsung dengan paguyuban penjual ketoprak di wilayah Tasikmalaya untuk mencatat data akuntansi aktual agar koefisien fungsi biaya lebih akurat.
2. **Pengembangan Model Elastisitas Permintaan**: Untuk penelitian lanjutan, fungsi harga $p$ dapat dimodelkan sebagai fungsi permintaan non-linier $p(q) = p_0 - k q$ (pasar persaingan monopolistik).
3. **Penerapan Konsep Integral**: Di masa mendatang, konsep integral dapat diterapkan untuk menghitung akumulasi keuntungan bulanan atau surplus konsumen dan produsen.

---

## DAFTAR PUSTAKA
1. Azizah, S. U., & Cahyani, N. P. D. (2024). Analisis harga pokok produksi dengan metode full costing untuk menentukan harga jual pada UMKM Warung Makan Parkiran. *Kompeten: Jurnal Ilmiah Ekonomi dan Bisnis*, 2(5), 110–120. https://doi.org/10.57141/kompeten.v2i5.110
2. Nurwahidah, N., & Mariani, A. (2021). Turunan (Derivatif): Sebuah pendekatan matematis dalam analisis keuntungan maksimum. *Jurnal MSA (Matematika dan Statistika serta Aplikasinya)*, 9(1), 1–6. https://doi.org/10.24252/msa.v9i1.21406
3. Riani, A. C., Rukmana, A., Safira, N., & Purnamasari, P. (2025). Respon UMKM ketoprak terhadap kenaikan harga bahan baku: Implikasi terhadap minat beli konsumen. *Jurnal Lentera Pengabdian*, 3(3), 937–945. https://doi.org/10.59422/lp.v3i03.937
4. Satriani, A., Ade, & Wina. (2024). Perhitungan Harga Pokok Produksi untuk Penentuan Harga Jual Produk UMKM Makanan. *Jurnal Insan Unggul*, 12(2), 160–169. https://doi.org/10.47926/jiu.2024.12.2.160-169
5. Stewart, J. (2016). *Calculus: Early Transcendentals* (8th ed.). Cengage Learning.

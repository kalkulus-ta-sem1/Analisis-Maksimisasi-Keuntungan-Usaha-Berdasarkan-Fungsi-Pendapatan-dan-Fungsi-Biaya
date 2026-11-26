"""
Basis Data Harga Komoditas Pasar & Operasional Harian UMKM Indonesia (Fokus Tasikmalaya).

Dirancang dengan pendekatan BELANJA HARIAN (NON-BORONGAN) dan FLUKTUASI HARGA PASAR:
- Biaya bahan baku (b) dihitung dari takaran eceran/harian di pasar tradisional Tasikmalaya,
  bukan stok borongan/karungan, sehingga modal keluar dihitung sesuai kebutuhan per hari.
- Biaya tetap harian (c) memakai konsumsi riil per hari (mis. 1 tabung LPG 3 kg dibagi rata-rata
  2,5-3 hari pemakaian untuk gerobak ketoprak, sewa lapak PKL harian, listrik & penyusutan per hari).
- Setiap komponen memiliki rentang volatilitas (harga turun saat panen raya vs harga normal vs
  harga naik/lonjakan hari besar) berdasarkan pemantauan Pasar Induk Cikurubuk & Jawa Barat.
"""

from __future__ import annotations

import math
from typing import Dict, List, Any, Tuple


KATALOG_KOMODITAS_TASIK: List[Dict[str, Any]] = [
    {
        "kategori": "Bahan Pangan Pokok",
        "komoditas": "Beras Medium (IR 64 II)",
        "harga_tasik": 13250,
        "satuan": "kg",
        "kisaran": "Rp 12.500 - Rp 14.200/kg",
        "sumber": "Pasar Induk Cikurubuk, Kota Tasikmalaya",
    },
    {
        "kategori": "Bahan Pangan Pokok",
        "komoditas": "Beras Premium (IR 64 I)",
        "harga_tasik": 14600,
        "satuan": "kg",
        "kisaran": "Rp 13.800 - Rp 15.500/kg",
        "sumber": "Pasar Induk Cikurubuk, Kota Tasikmalaya",
    },
    {
        "kategori": "Bahan Pangan Pokok",
        "komoditas": "Kacang Tanah Kupas (Eceran Harian)",
        "harga_tasik": 32000,
        "satuan": "kg",
        "kisaran": "Rp 28.000 - Rp 38.000/kg",
        "sumber": "Pasar Cikurubuk & Pasar Pancasila Tasikmalaya",
    },
    {
        "kategori": "Bahan Pangan Pokok",
        "komoditas": "Minyak Goreng (Minyakita / Curah)",
        "harga_tasik": 17500,
        "satuan": "liter",
        "kisaran": "Rp 15.800 - Rp 19.500/L",
        "sumber": "Pemantauan Kemendag & Pasar Tasikmalaya",
    },
    {
        "kategori": "Protein & Lauk",
        "komoditas": "Telur Ayam Ras (Broiler)",
        "harga_tasik": 28000,
        "satuan": "kg (~15-16 btr)",
        "kisaran": "Rp 25.000 - Rp 31.000/kg (~Rp 1.650-2.050/btr)",
        "sumber": "Pasar Cikurubuk & Kemendag Tasikmalaya",
    },
    {
        "kategori": "Protein & Lauk",
        "komoditas": "Daging Ayam Ras (Broiler)",
        "harga_tasik": 38000,
        "satuan": "kg",
        "kisaran": "Rp 34.000 - Rp 43.000/kg",
        "sumber": "Pasar Cikurubuk & Singaparna Tasikmalaya",
    },
    {
        "kategori": "Protein & Lauk",
        "komoditas": "Daging Sapi Segar",
        "harga_tasik": 130000,
        "satuan": "kg",
        "kisaran": "Rp 122.000 - Rp 142.000/kg",
        "sumber": "Pasar Tradisional Priangan Timur / Tasikmalaya",
    },
    {
        "kategori": "Protein & Lauk",
        "komoditas": "Tahu Putih / Kuning Mentah",
        "harga_tasik": 500,
        "satuan": "potong (~Rp 11rb/kg)",
        "kisaran": "Rp 400 - Rp 600/biji",
        "sumber": "Pengrajin & Pasar Tradisional Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Cabai Rawit Merah (Domba)",
        "harga_tasik": 68000,
        "satuan": "kg",
        "kisaran": "Rp 48.000 (panen) - Rp 90.000/kg (HBKN)",
        "sumber": "Pemantauan Harga Pangan Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Cabai Merah Keriting / Besar",
        "harga_tasik": 55000,
        "satuan": "kg",
        "kisaran": "Rp 42.000 - Rp 72.000/kg",
        "sumber": "Pasar Induk Cikurubuk, Kota Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Bawang Merah",
        "harga_tasik": 35000,
        "satuan": "kg",
        "kisaran": "Rp 28.000 - Rp 45.000/kg",
        "sumber": "Pasar Induk Cikurubuk, Kota Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Bawang Putih (Impor Honan/Kating)",
        "harga_tasik": 35000,
        "satuan": "kg",
        "kisaran": "Rp 31.000 - Rp 41.000/kg",
        "sumber": "Pasar Induk Cikurubuk, Kota Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Gula Merah / Gula Kelapa Cetak",
        "harga_tasik": 24000,
        "satuan": "kg",
        "kisaran": "Rp 21.000 - Rp 26.000/kg",
        "sumber": "Pasar Tradisional Kab. & Kota Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Gula Aren Asli Tasikmalaya (Kawung/Cair)",
        "harga_tasik": 32000,
        "satuan": "kg / liter cair",
        "kisaran": "Rp 18.000 - Rp 36.000 (cetak/cair)",
        "sumber": "Sentra Gula Aren Tasikmalaya & Distributor FnB",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Tauge (Kecambah Segar)",
        "harga_tasik": 10000,
        "satuan": "kg",
        "kisaran": "Rp 8.000 - Rp 12.500/kg",
        "sumber": "Pasar Sayur Cikurubuk Tasikmalaya",
    },
    {
        "kategori": "Bumbu & Sayuran",
        "komoditas": "Mentimun Segar (Harian)",
        "harga_tasik": 8000,
        "satuan": "kg",
        "kisaran": "Rp 6.000 - Rp 11.000/kg",
        "sumber": "Pasar Sayur Priangan Timur / Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Bihun Jagung / Beras",
        "harga_tasik": 14000,
        "satuan": "kg",
        "kisaran": "Rp 12.000 - Rp 16.000/kg",
        "sumber": "Pasar & Warung Sembako Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Kerupuk Aci / Putih Mentah",
        "harga_tasik": 22000,
        "satuan": "kg",
        "kisaran": "Rp 18.000 - Rp 25.000/kg",
        "sumber": "Pasar Tradisional Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Kecap Manis (Refill 700ml/720g)",
        "harga_tasik": 27000,
        "satuan": "pouch (~Rp 38.5rb/L)",
        "kisaran": "Rp 25.000 - Rp 29.000/pouch",
        "sumber": "Agen Sembako & Pasar Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Biji Kopi Robusta Jabar (Roasted)",
        "harga_tasik": 150000,
        "satuan": "kg",
        "kisaran": "Rp 130.000 - Rp 185.000/kg",
        "sumber": "Roastery Lokal Tasikmalaya / Jawa Barat",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Biji Kopi Arabika Tasik (Taraju/Galunggung)",
        "harga_tasik": 220000,
        "satuan": "kg",
        "kisaran": "Rp 180.000 - Rp 265.000/kg",
        "sumber": "Petani & Roastery Priangan Timur / Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Susu UHT Full Cream (1 Liter)",
        "harga_tasik": 18000,
        "satuan": "liter",
        "kisaran": "Rp 17.000 - Rp 19.500/L",
        "sumber": "Distributor FnB & Grosir Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Susu Evaporasi (380g) & Creamer",
        "harga_tasik": 20000,
        "satuan": "kaleng 380g",
        "kisaran": "Rp 16.000 - Rp 25.000/kaleng",
        "sumber": "Toko Bahan Kue & Grosir Tasikmalaya",
    },
    {
        "kategori": "Pelengkap & Minuman",
        "komoditas": "Es Batu Kristal Pabrik",
        "harga_tasik": 700,
        "satuan": "kg (~Rp 12,5rb/bal 18kg)",
        "kisaran": "Rp 9.000 - Rp 15.000 per bal 18-20 kg",
        "sumber": "Agen Es Batu Kristal Tasikmalaya",
    },
    {
        "kategori": "Kemasan (Packaging)",
        "komoditas": "Kertas Nasi Laminasi / Styrofoam / Paper Bowl",
        "harga_tasik": 400,
        "satuan": "pcs (styrofoam)",
        "kisaran": "Kertas nasi Rp 105 | Styrofoam Rp 350-450 | Bowl Rp 950",
        "sumber": "Toko Plastik Tasikmalaya",
    },
    {
        "kategori": "Kemasan (Packaging)",
        "komoditas": "Cup Plastik 14-16oz + Tutup + Sedotan",
        "harga_tasik": 550,
        "satuan": "set gelas",
        "kisaran": "Rp 450 - Rp 900/set (tergantung ketebalan)",
        "sumber": "Grosir Kemasan Minuman Tasikmalaya",
    },
    {
        "kategori": "Energi, Sewa & Upah Lokal",
        "komoditas": "Gas LPG 3 kg (Pemakaian Riil Harian)",
        "harga_tasik": 21500,
        "satuan": "tabung (tahan 2,5-3 hr)",
        "kisaran": "HET Pangkalan Rp 16.000 | Eceran Rp 20.000 - Rp 25.000",
        "sumber": "Hiswana Migas Priangan Timur & Lapangan Tasik",
    },
    {
        "kategori": "Energi, Sewa & Upah Lokal",
        "komoditas": "Tarif Listrik PLN Non-Subsidi (R-1 / B-1)",
        "harga_tasik": 1445,
        "satuan": "kWh (1.300VA/B1)",
        "kisaran": "900VA Rp 1.352/kWh | 1.300VA & Bisnis Rp 1.444,70/kWh",
        "sumber": "Kementerian ESDM / PLN Nasional",
    },
    {
        "kategori": "Energi, Sewa & Upah Lokal",
        "komoditas": "Sewa Lapak Harian PKL / Kios Tasikmalaya",
        "harga_tasik": 15000,
        "satuan": "hari (PKL standar)",
        "kisaran": "PKL Rp 8rb-22rb/hr | Kios Kecil Rp 30rb-45rb/hr",
        "sumber": "Survei Lapangan PKL & Area UNSIL/Cihideung Tasik",
    },
    {
        "kategori": "Energi, Sewa & Upah Lokal",
        "komoditas": "Retribusi Pasar & Kebersihan Kota Tasik",
        "harga_tasik": 3500,
        "satuan": "hari (PKL / pelataran)",
        "kisaran": "Rp 2.500 - Rp 5.000/hari sesuai luas lapak",
        "sumber": "Perda Pajak & Retribusi Daerah Kota Tasikmalaya",
    },
    {
        "kategori": "Energi, Sewa & Upah Lokal",
        "komoditas": "UMK Kota & Kabupaten Tasikmalaya",
        "harga_tasik": 2980336,
        "satuan": "bulan (Kota Tasik)",
        "kisaran": "Kota Tasik Rp 2.980.336 | Kab. Tasik Rp 2.871.874/bln",
        "sumber": "Kepgub Jawa Barat (Acuan Upah Tenaga Bantu UMKM)",
    },
]


WILAYAH_CONFIG: Dict[str, Dict[str, Any]] = {
    "Kota Tasikmalaya (Pasar Cikurubuk)": {
        "kode": "kota_tasik",
        "label_ringkas": "Kota Tasikmalaya (Pasar Cikurubuk)",
        "var_factor": 1.00,
        "fixed_factor": 1.00,
        "a_factor": 1.00,
        "catatan": "Belanja harian Pasar Cikurubuk, pemakaian gas LPG 3kg per hari (~Rp 21.500/2,5-3 hr), sewa lapak harian PKL/kios Kota Tasik.",
    },
    "Kab. Tasikmalaya (Singaparna & Sekitar)": {
        "kode": "kab_tasik",
        "label_ringkas": "Kab. Tasikmalaya (Singaparna)",
        "var_factor": 0.95,
        "fixed_factor": 0.85,
        "a_factor": 0.95,
        "catatan": "Bahan sayur, beras & gula aren lokal ~5% lebih murah; sewa lapak harian di Singaparna/pinggiran ~15% lebih hemat.",
    },
    "Rata-rata Nasional (Indonesia)": {
        "kode": "nasional",
        "label_ringkas": "Rata-rata Indonesia",
        "var_factor": 1.06,
        "fixed_factor": 1.12,
        "a_factor": 1.05,
        "catatan": "Acuan rata-rata PIHPS/Kemendag & kota menengah Indonesia: bahan pokok ~+6%, sewa & operasional harian ~+12%.",
    },
}


KONDISI_PASAR_CONFIG: Dict[str, Dict[str, Any]] = {
    "Harga Normal Pasar (Rata-rata)": {
        "kode": "normal",
        "label_ringkas": "Normal",
        "vol_factor": 0.0,
        "catatan": "Harga rata-rata harian normal Pasar Cikurubuk & pasar tradisional Indonesia.",
    },
    "Harga Turun / Panen Raya": {
        "kode": "turun",
        "label_ringkas": "Harga Turun (Panen)",
        "vol_factor": -1.0,
        "catatan": "Pasokan cabai, sayur, telur & kacang melimpah (harga turun ke batas bawah musiman) + LPG pangkalan/HET.",
    },
    "Harga Sedang Naik (Musim Hujan)": {
        "kode": "naik_sedang",
        "label_ringkas": "Sedang Naik",
        "vol_factor": 0.5,
        "catatan": "Cuaca/distribusi membuat harga cabai, sayur, dan protein naik moderat (+50% dari rentang kenaikan).",
    },
    "Lonjakan Hari Besar / HBKN": {
        "kode": "melonjak",
        "label_ringkas": "Lonjakan HBKN",
        "vol_factor": 1.0,
        "catatan": "Menjelang Ramadan/Lebaran/Libur Nasional: cabai rawit, telur, ayam & bumbu melonjak ke batas atas pasar.",
    },
}


# Rentang volatilitas (persentase turun saat panen/HET, persentase naik saat lonjakan HBKN)
# Diterapkan per komponen agar simulasi naik-turunnya harga realistis (cabai/kacang lebih fluktuatif daripada kemasan/sewa).
VOLATILITAS_VAR: Dict[str, Tuple[float, float]] = {
    "ketupat": (-0.08, 0.12),
    "beras": (-0.08, 0.12),
    "bahan_utama": (-0.08, 0.12),
    "telur_topping": (-0.12, 0.20),
    "telur": (-0.12, 0.20),
    "protein": (-0.12, 0.22),
    "bumbu_kacang": (-0.18, 0.28),
    "bumbu": (-0.18, 0.28),
    "bumbu_sayur": (-0.16, 0.25),
    "tahu": (-0.08, 0.12),
    "minyak_kecap": (-0.08, 0.14),
    "minyak_saos": (-0.08, 0.14),
    "bihun_tauge": (-0.12, 0.18),
    "timun_kerupuk": (-0.10, 0.16),
    "pelengkap": (-0.10, 0.15),
    "kecap_kemasan": (-0.04, 0.08),
    "kemasan": (-0.04, 0.08),
    "kopi": (-0.10, 0.18),
    "susu_uht": (-0.05, 0.10),
    "evaporasi_creamer": (-0.06, 0.12),
    "gula_aren": (-0.10, 0.16),
    "es_cup": (-0.05, 0.08),
}

VOLATILITAS_FIXED: Dict[str, Tuple[float, float]] = {
    "sewa": (0.00, 0.05),
    "gas": (-0.25, 0.16),         # HET Rp 16rb vs eceran Rp 21,5rb vs langka Rp 25rb
    "listrik_air": (0.00, 0.08),
    "listrik_wifi": (0.00, 0.06),
    "retribusi": (0.00, 0.05),
    "retribusi_air": (0.00, 0.06),
    "penyusutan": (0.00, 0.03),
    "tenaga_bantu": (0.00, 0.05),
}


def _preset_to_kategori(preset_name: str) -> str:
    low = (preset_name or "").lower()
    if "ketoprak" in low:
        return "ketoprak"
    if "nasi goreng" in low:
        return "nasgor"
    if "kopi" in low:
        return "kopi"
    return "umum"


KATEGORI_MODELS: Dict[str, Dict[str, Any]] = {
    "ketoprak": {
        "nama": "UMKM Ketoprak",
        "satuan_produk": "porsi",
        "var_schema": [
            ("ketupat", "Ketupat / Lontong", "Beras IR 64 Pasar Cikurubuk (belanja harian)"),
            ("telur_topping", "Telur Ayam Ras / Topping Protein", "Telur eceran harian Rp 28.000/kg (~Rp 1.850/btr)"),
            ("bumbu_kacang", "Bumbu Kacang (Kacang, Gula Merah, Cabai, Bawang)", "Kacang Rp 32rb/kg, rawit Rp 68rb/kg (fluktuatif)"),
            ("tahu", "Tahu Goreng + Minyak Goreng", "Tahu pasar Rp 500/ptg + minyak Rp 17.500/L"),
            ("bihun_tauge", "Bihun & Tauge Segar", "Bihun Rp 14.000/kg & tauge Rp 10.000/kg"),
            ("timun_kerupuk", "Mentimun, Bawang Goreng & Kerupuk", "Timun Rp 8.000/kg & kerupuk Rp 22.000/kg"),
            ("kecap_kemasan", "Kecap Manis & Kemasan Harian", "Kecap pouch & kertas nasi/styrofoam harian"),
        ],
        "fixed_schema": [
            ("sewa", "Sewa Lapak Harian Tasikmalaya", "Tarif harian lapak PKL / teras / kios kecil"),
            ("gas", "Gas LPG 3 kg (Pemakaian Riil/Hari)", "1 tabung Rp 21.500 dipakai ~2,5-4 hari"),
            ("listrik_air", "Listrik & Air Bersih Harian", "Pemakaian harian lampu gerobak + air cuci"),
            ("retribusi", "Retribusi Kebersihan & Keamanan", "Iuran harian PKL / pasar Kota Tasikmalaya"),
            ("penyusutan", "Penyusutan Gerobak & Alat/Hari", "Gerobak, kompor & cobek dibagi umur pakai"),
            ("tenaga_bantu", "Tenaga Bantu Harian (Jika Ada)", "Bantuan paruh waktu saat volume kedai besar"),
        ],
        "tiers": [
            {
                "p": 10000.0,
                "segmen": "Ketoprak Hemat Harian (Non-Borongan)",
                "a": 50.0,
                "disekonomi_catatan": "Gerobak/lapak tunggal; jika penjualan melebihi titik puncak harian perlu beli bumbu tambahan mendadak.",
                "var_costs": {
                    "ketupat": 1150, "telur_topping": 0, "bumbu_kacang": 1450,
                    "tahu": 820, "bihun_tauge": 510, "timun_kerupuk": 500, "kecap_kemasan": 470,
                },
                "var_takaran": {
                    "ketupat": "75g beras medium + daun",
                    "telur_topping": "-",
                    "bumbu_kacang": "22g kacang, 12g gula merah, 4g rawit",
                    "tahu": "1,5 ptg tahu + 8ml minyak",
                    "bihun_tauge": "15g bihun + 30g tauge",
                    "timun_kerupuk": "20g timun + 15g kerupuk aci",
                    "kecap_kemasan": "8ml kecap + kertas nasi polos",
                },
                "fixed_costs": {
                    "sewa": 8000, "gas": 5500, "listrik_air": 2500,
                    "retribusi": 2500, "penyusutan": 3500, "tenaga_bantu": 0,
                },
                "fixed_basis": {
                    "sewa": "Lapak harian pinggiran (~Rp 240rb/bln)",
                    "gas": "0,25 tbg/hari (1 tabung tahan 4 hari)",
                    "listrik_air": "Lampu LED + air cuci harian",
                    "retribusi": "Kebersihan PKL harian",
                    "penyusutan": "Gerobak sederhana dibagi 3 tahun",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 15000.0,
                "segmen": "Ketoprak Reguler Harian (Tasikmalaya)",
                "a": 60.0,
                "disekonomi_catatan": "Kapasitas nyaman 1 gerobak harian ~69 porsi/hari; di atas itu kelelahan ulek & belanja eceran darurat menaikkan biaya.",
                "var_costs": {
                    "ketupat": 1400, "telur_topping": 0, "bumbu_kacang": 2050,
                    "tahu": 1210, "bihun_tauge": 680, "timun_kerupuk": 760, "kecap_kemasan": 600,
                },
                "var_takaran": {
                    "ketupat": "90g beras IR 64 + daun",
                    "telur_topping": "-",
                    "bumbu_kacang": "30g kacang, 16g gula merah, 6g rawit",
                    "tahu": "2 ptg tahu + 12ml minyak goreng",
                    "bihun_tauge": "20g bihun + 40g tauge segar",
                    "timun_kerupuk": "25g timun + 20g kerupuk + bwg grg",
                    "kecap_kemasan": "12ml kecap + kertas nasi laminasi",
                },
                "fixed_costs": {
                    "sewa": 15000, "gas": 7200, "listrik_air": 3500,
                    "retribusi": 3000, "penyusutan": 4300, "tenaga_bantu": 0,
                },
                "fixed_basis": {
                    "sewa": "Lapak harian PKL/teras (~Rp 450rb/bln)",
                    "gas": "0,33 tbg/hari (1 tabung tahan 3 hari)",
                    "listrik_air": "~1,5 kWh PLN + air bersih harian",
                    "retribusi": "Kebersihan & keamanan PKL Kota Tasik",
                    "penyusutan": "Gerobak, kompor & cobek dibagi 3 tahun",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 20000.0,
                "segmen": "Ketoprak Spesial Telur Harian (Tasikmalaya)",
                "a": 75.0,
                "disekonomi_catatan": "Goreng telur dadar/ceplok per porsi + ulek bumbu membatasi kapasitas nyaman di ~72 porsi/hari.",
                "var_costs": {
                    "ketupat": 1500, "telur_topping": 2000, "bumbu_kacang": 2200,
                    "tahu": 1200, "bihun_tauge": 700, "timun_kerupuk": 800, "kecap_kemasan": 800,
                },
                "var_takaran": {
                    "ketupat": "95g beras premium IR 64 + daun",
                    "telur_topping": "1 btr telur ayam ras + 10ml minyak",
                    "bumbu_kacang": "33g kacang, 18g gula merah, 7g rawit",
                    "tahu": "2 ptg tahu + 12ml minyak goreng",
                    "bihun_tauge": "22g bihun + 42g tauge segar",
                    "timun_kerupuk": "28g timun + 22g kerupuk ekstra",
                    "kecap_kemasan": "13ml kecap + styrofoam/kemasan harian",
                },
                "fixed_costs": {
                    "sewa": 20000, "gas": 8600, "listrik_air": 4500,
                    "retribusi": 3500, "penyusutan": 5400, "tenaga_bantu": 0,
                },
                "fixed_basis": {
                    "sewa": "Lapak strategis harian (~Rp 600rb/bln)",
                    "gas": "0,40 tbg/hari (1 tabung tahan 2,5 hari)",
                    "listrik_air": "Lampu + kulkas kecil telur + air cuci",
                    "retribusi": "Kebersihan & keamanan Kota Tasik",
                    "penyusutan": "Gerobak, wajan telur & cobek harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 28000.0,
                "segmen": "Ketoprak Komplet Jumbo (Kios Kecil Tasik)",
                "a": 85.0,
                "disekonomi_catatan": "Multi-topping (telur + ayam/bakso) memperlambat penyajian di jam makan siang.",
                "var_costs": {
                    "ketupat": 1750, "telur_topping": 3800, "bumbu_kacang": 2850,
                    "tahu": 1450, "bihun_tauge": 850, "timun_kerupuk": 1350, "kecap_kemasan": 1250,
                },
                "var_takaran": {
                    "ketupat": "115g beras premium + daun",
                    "telur_topping": "1 btr telur + 30g suwiran ayam",
                    "bumbu_kacang": "42g kacang, gula aren Tasik & rawit",
                    "tahu": "2,5 ptg tahu + minyak goreng",
                    "bihun_tauge": "26g bihun + 50g tauge segar",
                    "timun_kerupuk": "Timun + kerupuk udang + bwg goreng",
                    "kecap_kemasan": "Kecap + paper bowl / box + sendok",
                },
                "fixed_costs": {
                    "sewa": 35000, "gas": 11800, "listrik_air": 7500,
                    "retribusi": 4000, "penyusutan": 7700, "tenaga_bantu": 0,
                },
                "fixed_basis": {
                    "sewa": "Kios kecil harian (~Rp 1,05jt/bln)",
                    "gas": "0,55 tbg/hari (1 tabung tahan ~1,8 hari)",
                    "listrik_air": "Chiller kecil, lampu kios & air",
                    "retribusi": "Retribusi kios & sampah Kota Tasik",
                    "penyusutan": "Peralatan kedai harian",
                    "tenaga_bantu": "Dikelola mandiri / keluarga",
                },
            },
        ],
    },
    "nasgor": {
        "nama": "UMKM Warung Nasi Goreng",
        "satuan_produk": "porsi",
        "var_schema": [
            ("beras", "Nasi Putih (Beras IR 64)", "Beras Pasar Cikurubuk (belanja harian)"),
            ("telur", "Telur Ayam Ras", "Telur Rp 28.000/kg (~Rp 1.850/btr, fluktuatif)"),
            ("protein", "Topping Protein (Ayam / Bakso / Sapi)", "Ayam Rp 38rb/kg, sapi Rp 130rb/kg (harian)"),
            ("bumbu", "Bumbu Halus (Bawang & Cabai)", "Bawang Rp 35rb/kg, cabai Rp 55-68rb/kg"),
            ("minyak_kecap", "Minyak Goreng, Margarin & Kecap Manis", "Minyak Rp 17.500/L & kecap pouch harian"),
            ("pelengkap", "Timun, Kerupuk & Kemasan", "Timun Rp 8rb/kg, kerupuk Rp 22rb/kg, kemasan"),
        ],
        "fixed_schema": [
            ("sewa", "Sewa Lapak / Kios Harian Tasik", "Tarif sewa harian tenda PKL / kios"),
            ("gas", "Gas LPG 3 kg (Pemakaian Riil/Hari)", "1 tabung Rp 21.500 dibagi pemakaian harian"),
            ("listrik_air", "Listrik PLN & Air Bersih Harian", "Rice cooker, lampu tenda & air cuci"),
            ("retribusi", "Retribusi Kebersihan & Keamanan", "Iuran harian PKL / pasar Kota Tasikmalaya"),
            ("penyusutan", "Penyusutan Wajan, Kompor & Gerobak", "Amortisasi harian alat dapur"),
            ("tenaga_bantu", "Tenaga Bantu Harian (Jika Ada)", "Proporsi harian jika skala kedai besar"),
        ],
        "tiers": [
            {
                "p": 13000.0,
                "segmen": "Nasi Goreng Ekonomis Harian",
                "a": 45.0,
                "disekonomi_catatan": "1 wajan kompor standar; produksi tinggi berlebih memicu kelelahan & antrean.",
                "var_costs": {"beras": 1650, "telur": 1800, "protein": 650, "bumbu": 750, "minyak_kecap": 700, "pelengkap": 650},
                "var_takaran": {
                    "beras": "120g beras medium IR 64",
                    "telur": "1 btr telur ayam ras",
                    "protein": "15g irisan bakso/sosis",
                    "bumbu": "Bawang merah, putih, cabai & garam",
                    "minyak_kecap": "16ml minyak + 10ml kecap manis",
                    "pelengkap": "Timun, kerupuk & kertas nasi",
                },
                "fixed_costs": {"sewa": 15000, "gas": 10800, "listrik_air": 5000, "retribusi": 3000, "penyusutan": 4200, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Lapak tenda harian (~Rp 450rb/bln)",
                    "gas": "0,50 tbg/hari (1 tabung tahan 2 hari)",
                    "listrik_air": "Rice cooker + lampu tenda + air",
                    "retribusi": "Kebersihan & keamanan PKL",
                    "penyusutan": "Gerobak, kompor & wajan harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 18000.0,
                "segmen": "Nasi Goreng Ayam/Bakso Harian (Tasikmalaya)",
                "a": 50.0,
                "disekonomi_catatan": "1 wajan kompor api besar optimal di ~98 porsi/hari sebelum butuh asisten.",
                "var_costs": {"beras": 1900, "telur": 1850, "protein": 1750, "bumbu": 900, "minyak_kecap": 900, "pelengkap": 900},
                "var_takaran": {
                    "beras": "130g beras premium IR 64",
                    "telur": "1 btr telur ayam ras",
                    "protein": "38g ayam suwir & bakso iris",
                    "bumbu": "Bawang merah/putih, cabai & terasi",
                    "minyak_kecap": "20ml minyak + 15ml kecap & saus",
                    "pelengkap": "Timun, kerupuk & styrofoam/kertas nasi",
                },
                "fixed_costs": {"sewa": 20000, "gas": 13000, "listrik_air": 6500, "retribusi": 3500, "penyusutan": 5000, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Lapak strategis/tenda (~Rp 600rb/bln)",
                    "gas": "0,60 tbg/hari (1 tabung tahan ~1,7 hari)",
                    "listrik_air": "Rice cooker, kulkas kecil & lampu",
                    "retribusi": "Retribusi harian Kota Tasik",
                    "penyusutan": "Kompor high-pressure & wajan harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 20000.0,
                "segmen": "Nasi Goreng Spesial Harian (Tasikmalaya)",
                "a": 55.0,
                "disekonomi_catatan": "Porsi topping ekstra & penyajian box membuat kapasitas optimal ~99 porsi/hari.",
                "var_costs": {"beras": 2000, "telur": 1850, "protein": 2350, "bumbu": 1000, "minyak_kecap": 950, "pelengkap": 950},
                "var_takaran": {
                    "beras": "135g beras premium IR 64",
                    "telur": "1 btr telur ayam ras",
                    "protein": "50g ayam fillet & bakso",
                    "bumbu": "Bumbu ulek + cabai rawit domba",
                    "minyak_kecap": "Minyak, margarin & kecap manis",
                    "pelengkap": "Timun, acar, kerupuk & styrofoam",
                },
                "fixed_costs": {"sewa": 22000, "gas": 14000, "listrik_air": 7000, "retribusi": 3500, "penyusutan": 5500, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Lapak ramai / semi-kios (~Rp 660rb/bln)",
                    "gas": "0,65 tbg/hari (api besar harian)",
                    "listrik_air": "Kulkas, rice cooker, lampu & air",
                    "retribusi": "Kebersihan & keamanan Kota Tasik",
                    "penyusutan": "Peralatan masak harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 28000.0,
                "segmen": "Nasi Goreng Daging Sapi / Seafood (Kios Tasik)",
                "a": 65.0,
                "disekonomi_catatan": "Kontrol bahan segar & pesanan jam sibuk membatasi output harian tanpa tambahan kru.",
                "var_costs": {"beras": 2150, "telur": 1850, "protein": 4900, "bumbu": 1250, "minyak_kecap": 1200, "pelengkap": 1650},
                "var_takaran": {
                    "beras": "145g beras premium IR 64",
                    "telur": "1 btr telur ayam ras",
                    "protein": "38g daging sapi/udang segar",
                    "bumbu": "Bumbu halus, saus tiram & rawit",
                    "minyak_kecap": "Minyak, margarin & kecap manis",
                    "pelengkap": "Acar, emping/kerupuk & paper box",
                },
                "fixed_costs": {"sewa": 38000, "gas": 17200, "listrik_air": 10000, "retribusi": 4500, "penyusutan": 8300, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Kios kecil harian (~Rp 1,14jt/bln)",
                    "gas": "0,80 tbg/hari",
                    "listrik_air": "Freezer, rice cooker, lampu & air",
                    "retribusi": "Retribusi kios & sampah Kota Tasik",
                    "penyusutan": "Peralatan kios harian",
                    "tenaga_bantu": "Dikelola mandiri / keluarga",
                },
            },
        ],
    },
    "kopi": {
        "nama": "UMKM Kopi Susu Kekinian",
        "satuan_produk": "gelas",
        "var_schema": [
            ("kopi", "Biji Kopi (Robusta / Arabika Taraju-Galunggung)", "Robusta Rp 150rb/kg, Arabika Tasik Rp 220rb/kg"),
            ("susu_uht", "Susu UHT Full Cream", "Susu UHT Rp 17.000 - Rp 19.500/liter"),
            ("evaporasi_creamer", "Susu Evaporasi / Krimer Bubuk", "Evaporasi Rp 20rb/klg, Creamer Rp 32rb/kg"),
            ("gula_aren", "Gula Aren Cair Asli Tasikmalaya", "Sentra gula aren Tasik ~Rp 32.000/liter"),
            ("es_cup", "Es Batu Kristal & Cup Set (Lid + Sedotan)", "Es kristal Tasik Rp 700/kg + cup set harian"),
        ],
        "fixed_schema": [
            ("sewa", "Sewa Booth / Kios Harian Tasik", "Tarif sewa harian booth / teras / kios"),
            ("listrik_wifi", "Listrik PLN & WiFi Harian", "Tarif bisnis PLN Rp 1.444,70/kWh"),
            ("retribusi_air", "Retribusi & Air Galon Seduh Harian", "Iuran kebersihan + air galon/RO harian"),
            ("penyusutan", "Penyusutan Mesin, Grinder & Booth/Hari", "Amortisasi harian alat kedai"),
            ("tenaga_bantu", "Tenaga Bantu Harian (Jika Ada)", "Shift tambahan bila kelas ruko"),
        ],
        "tiers": [
            {
                "p": 14000.0,
                "segmen": "Es Kopi Susu Booth Harian (Tasikmalaya)",
                "a": 60.0,
                "disekonomi_catatan": "Kapasitas cup sealer & grinder booth harian efektif hingga ~78 cup/hari.",
                "var_costs": {"kopi": 1750, "susu_uht": 1350, "evaporasi_creamer": 350, "gula_aren": 550, "es_cup": 600},
                "var_takaran": {
                    "kopi": "12g Robusta lokal Jabar",
                    "susu_uht": "80ml susu UHT / SKM",
                    "evaporasi_creamer": "11g krimer bubuk",
                    "gula_aren": "18ml gula aren cair Tasik",
                    "es_cup": "140g es kristal + cup 14oz polos",
                },
                "fixed_costs": {"sewa": 18000, "listrik_wifi": 9000, "retribusi_air": 5000, "penyusutan": 10000, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Booth/teras harian (~Rp 540rb/bln)",
                    "listrik_wifi": "~6 kWh PLN B-1 (chiller & sealer)",
                    "retribusi_air": "Retribusi harian + air galon",
                    "penyusutan": "Booth, grinder & cup sealer harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 20000.0,
                "segmen": "Es Kopi Susu Gula Aren Harian (Kedai Tasik)",
                "a": 70.0,
                "disekonomi_catatan": "1 grup mesin seduh & 1 barista mandiri optimal di ~98 cup/hari.",
                "var_costs": {"kopi": 2400, "susu_uht": 1700, "evaporasi_creamer": 800, "gula_aren": 650, "es_cup": 650},
                "var_takaran": {
                    "kopi": "13g blend Arabika Tasik & Robusta",
                    "susu_uht": "95ml susu UHT Full Cream",
                    "evaporasi_creamer": "15ml susu evaporasi",
                    "gula_aren": "20ml gula aren cair Tasik",
                    "es_cup": "150g es kristal + cup 16oz + lid + sedotan",
                },
                "fixed_costs": {"sewa": 30000, "listrik_wifi": 14000, "retribusi_air": 5000, "penyusutan": 13000, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Kios kecil harian (~Rp 900rb/bln)",
                    "listrik_wifi": "Mesin seduh, chiller & WiFi harian",
                    "retribusi_air": "Retribusi & air galon RO harian",
                    "penyusutan": "Mesin kopi entry, grinder & chiller",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 22000.0,
                "segmen": "Es Kopi Susu Kekinian Standar (Kedai Tasik)",
                "a": 75.0,
                "disekonomi_catatan": "Antrean jam sibuk & batas kapasitas chiller menaikkan biaya marjinal di atas 101 cup/hari.",
                "var_costs": {"kopi": 2650, "susu_uht": 1850, "evaporasi_creamer": 900, "gula_aren": 700, "es_cup": 700},
                "var_takaran": {
                    "kopi": "14g blend Arabika Taraju & Robusta",
                    "susu_uht": "103ml susu UHT Full Cream",
                    "evaporasi_creamer": "17ml susu evaporasi",
                    "gula_aren": "22ml gula aren asli Tasik",
                    "es_cup": "160g es kristal + cup 16oz + lid + sedotan",
                },
                "fixed_costs": {"sewa": 33000, "listrik_wifi": 15500, "retribusi_air": 5000, "penyusutan": 14500, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Kios strategis harian (~Rp 990rb/bln)",
                    "listrik_wifi": "Espresso, chiller & WiFi harian",
                    "retribusi_air": "Retribusi Kota Tasik & air galon",
                    "penyusutan": "Mesin espresso, grinder & kulkas harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 30000.0,
                "segmen": "Specialty Coffee Shop Ruko Kecil Tasik",
                "a": 85.0,
                "disekonomi_catatan": "Standar penyajian specialty & dine-in membatasi volume tanpa kru tambahan.",
                "var_costs": {"kopi": 3900, "susu_uht": 2300, "evaporasi_creamer": 1050, "gula_aren": 950, "es_cup": 1000},
                "var_takaran": {
                    "kopi": "16g 100% Arabika Specialty Tasik",
                    "susu_uht": "128ml fresh milk / UHT",
                    "evaporasi_creamer": "20ml susu evaporasi/creamer",
                    "gula_aren": "26ml gula aren organik / sirup",
                    "es_cup": "Es kristal + cup tebal dome lid + sleeve",
                },
                "fixed_costs": {"sewa": 55000, "listrik_wifi": 22000, "retribusi_air": 8000, "penyusutan": 18000, "tenaga_bantu": 12000},
                "fixed_basis": {
                    "sewa": "Ruko kecil harian (~Rp 1,65jt/bln)",
                    "listrik_wifi": "AC, mesin espresso & WiFi harian",
                    "retribusi_air": "Retribusi, air PDAM/galon & kebersihan",
                    "penyusutan": "Mesin komersial & interior harian",
                    "tenaga_bantu": "Helper paruh waktu jam sibuk",
                },
            },
        ],
    },
    "umum": {
        "nama": "UMKM Kuliner Umum (Tasikmalaya)",
        "satuan_produk": "porsi",
        "var_schema": [
            ("bahan_utama", "Bahan Pokok / Karbohidrat Utama", "Beras/mie/tepung Pasar Cikurubuk (belanja harian)"),
            ("protein", "Lauk / Protein (Telur / Ayam / Daging)", "Telur Rp 28rb/kg, ayam Rp 38rb/kg (fluktuatif)"),
            ("bumbu_sayur", "Bumbu Dapur, Kacang & Sayuran Segar", "Cabai, bawang, kacang, sayur Pasar Cikurubuk"),
            ("minyak_saos", "Minyak Goreng, Kecap & Saus", "Minyak Rp 17.500/L & kecap/saus harian"),
            ("kemasan", "Kemasan & Pelengkap Saji", "Kertas nasi Rp 105, styrofoam Rp 400 harian"),
        ],
        "fixed_schema": [
            ("sewa", "Sewa Lapak / Kios Harian Tasik", "Tarif sewa harian PKL / teras / kios kecil"),
            ("gas", "Gas LPG 3 kg (Pemakaian Riil/Hari)", "1 tabung Rp 21.500 dibagi pemakaian harian"),
            ("listrik_air", "Listrik & Air Bersih Harian", "Pemakaian lampu, kulkas & air cuci"),
            ("retribusi", "Retribusi Kebersihan & Keamanan", "Iuran harian PKL / pasar Kota Tasikmalaya"),
            ("penyusutan", "Penyusutan Gerobak & Alat Harian", "Amortisasi harian alat usaha"),
            ("tenaga_bantu", "Tenaga Bantu Harian (Jika Ada)", "Disesuaikan untuk skala kedai besar"),
        ],
        "tiers": [
            {
                "p": 10000.0,
                "segmen": "Kuliner Hemat Harian PKL Tasik",
                "a": 50.0,
                "disekonomi_catatan": "Operasional harian gerobak tunggal; kelebihan volume memicu kelelahan & belanja eceran darurat.",
                "var_costs": {"bahan_utama": 1200, "protein": 1300, "bumbu_sayur": 1150, "minyak_saos": 700, "kemasan": 550},
                "var_takaran": {
                    "bahan_utama": "85g karbohidrat/basis porsi",
                    "protein": "1 porsi protein ekonomis",
                    "bumbu_sayur": "Bumbu & sayuran porsi harian",
                    "minyak_saos": "Minyak goreng & kecap harian",
                    "kemasan": "Kertas nasi laminasi / plastik",
                },
                "fixed_costs": {"sewa": 10000, "gas": 5500, "listrik_air": 2500, "retribusi": 2500, "penyusutan": 3500, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Lapak harian PKL (~Rp 300rb/bln)",
                    "gas": "0,25 tbg/hari (1 tabung tahan 4 hari)",
                    "listrik_air": "Lampu lapak + air cuci harian",
                    "retribusi": "Kebersihan PKL harian",
                    "penyusutan": "Gerobak & alat dasar harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 15000.0,
                "segmen": "Kuliner Standar Harian UMKM Tasik",
                "a": 60.0,
                "disekonomi_catatan": "Skala gerobak/warung harian; biaya marjinal naik jika melebihi kapasitas nyaman.",
                "var_costs": {"bahan_utama": 1500, "protein": 2000, "bumbu_sayur": 1600, "minyak_saos": 900, "kemasan": 700},
                "var_takaran": {
                    "bahan_utama": "100g beras/lontong/mie",
                    "protein": "Telur / tahu / suwiran ayam standar",
                    "bumbu_sayur": "Bumbu Pasar Cikurubuk & sayur segar",
                    "minyak_saos": "Minyak, kecap & saus takaran pas",
                    "kemasan": "Kertas nasi / kemasan + pelengkap",
                },
                "fixed_costs": {"sewa": 16000, "gas": 7200, "listrik_air": 3800, "retribusi": 3000, "penyusutan": 5000, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Teras/lapak strategis (~Rp 480rb/bln)",
                    "gas": "0,33 tbg/hari (1 tabung tahan 3 hari)",
                    "listrik_air": "Lampu, alat kecil & air bersih",
                    "retribusi": "Retribusi harian Kota Tasik",
                    "penyusutan": "Gerobak, kompor & peralatan harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 20000.0,
                "segmen": "Kuliner Spesial Harian (Tasikmalaya)",
                "a": 65.0,
                "disekonomi_catatan": "Tambahan lauk/telur menaikkan waktu saji dan biaya belanja mendadak bila terlalu ramai.",
                "var_costs": {"bahan_utama": 1850, "protein": 3200, "bumbu_sayur": 2100, "minyak_saos": 1100, "kemasan": 950},
                "var_takaran": {
                    "bahan_utama": "115g beras premium/basis utama",
                    "protein": "Telur + ayam/bakso porsi spesial",
                    "bumbu_sayur": "Bumbu ekstra & sayuran segar",
                    "minyak_kecap": "Minyak, margarin & kecap manis",
                    "minyak_saos": "Minyak, margarin, kecap & saus",
                    "kemasan": "Styrofoam/box + sendok + kerupuk",
                },
                "fixed_costs": {"sewa": 21000, "gas": 9000, "listrik_air": 4800, "retribusi": 3500, "penyusutan": 6700, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Lapak ramai / semi-kios (~Rp 630rb/bln)",
                    "gas": "0,42 tbg/hari (1 tabung tahan ~2,4 hari)",
                    "listrik_air": "Kulkas kecil, lampu & air bersih",
                    "retribusi": "Kebersihan & keamanan Kota Tasik",
                    "penyusutan": "Peralatan masak harian",
                    "tenaga_bantu": "Dikelola sendiri",
                },
            },
            {
                "p": 30000.0,
                "segmen": "Kuliner Komplet / Kios Tasikmalaya",
                "a": 75.0,
                "disekonomi_catatan": "Pengolahan porsi premium membatasi kapasitas tanpa tenaga bantu tambahan.",
                "var_costs": {"bahan_utama": 2150, "protein": 5600, "bumbu_sayur": 2800, "minyak_saos": 1550, "kemasan": 1700},
                "var_takaran": {
                    "bahan_utama": "135g beras premium / basis jumbo",
                    "protein": "Daging sapi/ayam penuh + telur",
                    "bumbu_sayur": "Bumbu spesial + lalap/sayur komplet",
                    "minyak_saos": "Minyak, margarin & saus",
                    "kemasan": "Paper bowl / box + alat makan",
                },
                "fixed_costs": {"sewa": 42000, "gas": 13000, "listrik_air": 8500, "retribusi": 4500, "penyusutan": 12000, "tenaga_bantu": 0},
                "fixed_basis": {
                    "sewa": "Kios kecil harian (~Rp 1,26jt/bln)",
                    "gas": "0,60 tbg/hari",
                    "listrik_air": "Chiller, lampu kios & air bersih",
                    "retribusi": "Retribusi kios & sampah Kota Tasik",
                    "penyusutan": "Peralatan kedai harian",
                    "tenaga_bantu": "Dikelola mandiri / keluarga",
                },
            },
        ],
    },
}


def _round_rupiah(val: float, step: int = 50) -> int:
    return int(round(val / step) * step)


def _apply_volatility(base_val: float, vol_bounds: Tuple[float, float], vol_factor: float) -> float:
    turun_pct, naik_pct = vol_bounds
    if vol_factor < 0:
        # turun_pct sudah bernilai negatif, mis. -0.18 -> skala berdasarkan abs(vol_factor)
        return base_val * (1.0 + abs(vol_factor) * turun_pct)
    if vol_factor > 0:
        return base_val * (1.0 + vol_factor * naik_pct)
    return base_val


def _compute_raw_tier_profile(p: float, kat_key: str, wil: Dict[str, Any]) -> Dict[str, Any]:
    model = KATEGORI_MODELS[kat_key]
    tiers = model["tiers"]
    v_fac = wil["var_factor"]
    f_fac = wil["fixed_factor"]
    a_fac = wil["a_factor"]

    if p <= tiers[0]["p"]:
        low = tiers[0]
        scale = max(0.70, p / low["p"])
        fixed_scale = max(0.65, 0.60 + 0.40 * (p / low["p"]))
        a_val = max(15.0, round(low["a"] * (0.85 + 0.15 * (p / low["p"])) * a_fac, 1))
        segmen = f"{low['segmen']} (Skala Harga Rp {p:,.0f})".replace(",", ".")
        disekonomi_note = low["disekonomi_catatan"]

        base_var = {k: low["var_costs"][k] * scale * v_fac for k in low["var_costs"]}
        base_fixed = {k: low["fixed_costs"][k] * fixed_scale * f_fac for k in low["fixed_costs"]}
        takaran_map = dict(low["var_takaran"])
        basis_map = dict(low["fixed_basis"])

    elif p >= tiers[-1]["p"]:
        high = tiers[-1]
        extra_p = p - high["p"]
        total_high_var = sum(high["var_costs"].values())
        extra_var_total = extra_p * 0.42
        var_scale = (total_high_var + extra_var_total) / max(1.0, total_high_var)

        total_high_fixed = sum(high["fixed_costs"].values())
        extra_fixed_total = min(85000.0, extra_p * 0.85)
        fixed_scale = (total_high_fixed + extra_fixed_total) / max(1.0, total_high_fixed)

        a_val = max(15.0, round((high["a"] + min(25.0, extra_p / 2000.0)) * a_fac, 1))
        segmen = f"{high['segmen']} - Premium (Rp {p:,.0f})".replace(",", ".")
        disekonomi_note = high["disekonomi_catatan"]

        base_var = {k: high["var_costs"][k] * var_scale * v_fac for k in high["var_costs"]}
        base_fixed = {k: high["fixed_costs"][k] * fixed_scale * f_fac for k in high["fixed_costs"]}
        takaran_map = dict(high["var_takaran"])
        basis_map = dict(high["fixed_basis"])

    else:
        low = tiers[0]
        high = tiers[-1]
        for idx in range(len(tiers) - 1):
            if tiers[idx]["p"] <= p <= tiers[idx + 1]["p"]:
                low = tiers[idx]
                high = tiers[idx + 1]
                break

        span = max(1.0, high["p"] - low["p"])
        t = (p - low["p"]) / span
        a_val = max(10.0, round((low["a"] + t * (high["a"] - low["a"])) * a_fac, 1))

        if t < 0.05:
            segmen = low["segmen"]
            disekonomi_note = low["disekonomi_catatan"]
        elif t > 0.95:
            segmen = high["segmen"]
            disekonomi_note = high["disekonomi_catatan"]
        else:
            segmen = f"Transisi {low['segmen'].split('(')[0].strip()} -> {high['segmen'].split('(')[0].strip()}"
            disekonomi_note = high["disekonomi_catatan"] if t >= 0.5 else low["disekonomi_catatan"]

        base_var = {
            k: (low["var_costs"][k] + t * (high["var_costs"][k] - low["var_costs"][k])) * v_fac
            for k in low["var_costs"]
        }
        base_fixed = {
            k: (low["fixed_costs"][k] + t * (high["fixed_costs"][k] - low["fixed_costs"][k])) * f_fac
            for k in low["fixed_costs"]
        }
        takaran_map = dict(high["var_takaran"] if t >= 0.5 else low["var_takaran"])
        basis_map = dict(high["fixed_basis"] if t >= 0.5 else low["fixed_basis"])

    return {
        "a": a_val,
        "segmen": segmen,
        "disekonomi_note": disekonomi_note,
        "base_var": base_var,
        "base_fixed": base_fixed,
        "takaran_map": takaran_map,
        "basis_map": basis_map,
    }


def _evaluate_scenario(
    p: float,
    model: Dict[str, Any],
    profile: Dict[str, Any],
    vol_factor: float,
    is_exact_normal_anchor: bool,
) -> Dict[str, Any]:
    a_val = profile["a"]
    var_items: List[Dict[str, Any]] = []
    for key, nama, sumber_ref in model["var_schema"]:
        base_val = profile["base_var"].get(key, 0.0)
        if base_val <= 0:
            continue
        bounds = VOLATILITAS_VAR.get(key, (-0.10, 0.15))
        adj_val = _apply_volatility(base_val, bounds, vol_factor)
        min_val = _apply_volatility(base_val, bounds, -1.0)
        max_val = _apply_volatility(base_val, bounds, 1.0)

        subtotal = int(round(adj_val)) if (is_exact_normal_anchor and vol_factor == 0.0) else _round_rupiah(adj_val, 10)
        min_sub = _round_rupiah(min_val, 10)
        max_sub = _round_rupiah(max_val, 10)
        var_items.append({
            "key": key,
            "komponen": nama,
            "takaran": profile["takaran_map"].get(key, "-"),
            "subtotal": subtotal,
            "min_subtotal": min_sub,
            "max_subtotal": max_sub,
            "sumber": sumber_ref,
        })

    fixed_items: List[Dict[str, Any]] = []
    for key, nama, sumber_ref in model["fixed_schema"]:
        base_val = profile["base_fixed"].get(key, 0.0)
        if base_val <= 0:
            continue
        bounds = VOLATILITAS_FIXED.get(key, (0.00, 0.05))
        adj_val = _apply_volatility(base_val, bounds, vol_factor)
        min_val = _apply_volatility(base_val, bounds, -1.0)
        max_val = _apply_volatility(base_val, bounds, 1.0)

        subtotal = int(round(adj_val)) if (is_exact_normal_anchor and vol_factor == 0.0) else _round_rupiah(adj_val, 100)
        min_sub = _round_rupiah(min_val, 100)
        max_sub = _round_rupiah(max_val, 100)
        fixed_items.append({
            "key": key,
            "komponen": nama,
            "basis": profile["basis_map"].get(key, "-"),
            "subtotal": subtotal,
            "min_subtotal": min_sub,
            "max_subtotal": max_sub,
            "sumber": sumber_ref,
        })

    b_total = float(sum(it["subtotal"] for it in var_items))
    c_total = float(sum(it["subtotal"] for it in fixed_items))

    alpha = p - b_total
    q_opt = (alpha / (2.0 * a_val)) if a_val > 0 else 0.0
    q_target_harian = max(1, round(q_opt))
    r_opt = p * q_opt
    c_opt = a_val * (q_opt ** 2) + b_total * q_opt + c_total
    p_opt = r_opt - c_opt

    modal_bahan_harian = b_total * q_target_harian
    total_modal_harian = modal_bahan_harian + c_total

    return {
        "b": b_total,
        "c": c_total,
        "a": a_val,
        "q_opt": q_opt,
        "q_target_harian": q_target_harian,
        "p_opt": p_opt,
        "modal_bahan_harian": modal_bahan_harian,
        "total_modal_harian": total_modal_harian,
        "var_items": var_items,
        "fixed_items": fixed_items,
    }


def hitung_estimasi_umkm(
    harga_jual: float,
    preset_name: str,
    wilayah: str = "Kota Tasikmalaya (Pasar Cikurubuk)",
    kondisi_pasar: str = "Harga Normal Pasar (Rata-rata)",
) -> Dict[str, Any]:
    """
    Hitung parameter model kalkulus (c, b, a, q_max), modal belanja harian (non-borongan),
    serta simulasi skenario naik-turunnya harga pasar Tasikmalaya & Indonesia.
    """
    p = float(harga_jual)
    kat_key = _preset_to_kategori(preset_name)
    model = KATEGORI_MODELS[kat_key]
    wil = WILAYAH_CONFIG.get(wilayah, WILAYAH_CONFIG["Kota Tasikmalaya (Pasar Cikurubuk)"])
    kondisi = KONDISI_PASAR_CONFIG.get(kondisi_pasar, KONDISI_PASAR_CONFIG["Harga Normal Pasar (Rata-rata)"])

    profile = _compute_raw_tier_profile(p, kat_key, wil)
    is_exact_normal_anchor = (
        wil["kode"] == "kota_tasik"
        and any(abs(p - tier["p"]) < 1e-6 for tier in model["tiers"])
    )

    aktif = _evaluate_scenario(
        p=p,
        model=model,
        profile=profile,
        vol_factor=kondisi["vol_factor"],
        is_exact_normal_anchor=is_exact_normal_anchor,
    )

    # Hitung seluruh skenario naik-turunnya harga agar penjual selalu melihat batas aman
    skenario_harga: List[Dict[str, Any]] = []
    for k_name, k_cfg in KONDISI_PASAR_CONFIG.items():
        ev = _evaluate_scenario(
            p=p,
            model=model,
            profile=profile,
            vol_factor=k_cfg["vol_factor"],
            is_exact_normal_anchor=is_exact_normal_anchor,
        )
        skenario_harga.append({
            "nama": k_name,
            "ringkas": k_cfg["label_ringkas"],
            "b": ev["b"],
            "c": ev["c"],
            "q_opt": ev["q_opt"],
            "q_target_harian": ev["q_target_harian"],
            "modal_bahan_harian": ev["modal_bahan_harian"],
            "total_modal_harian": ev["total_modal_harian"],
            "p_opt": ev["p_opt"],
            "aktif": (k_name == kondisi_pasar),
        })

    b_total = aktif["b"]
    c_total = aktif["c"]
    a_val = aktif["a"]

    alpha = p - b_total
    q_opt_est = max(1.0, alpha / (2.0 * a_val)) if a_val > 0 else 1.0
    disc = (alpha ** 2) - (4.0 * a_val * c_total)
    if disc >= 0 and a_val > 0 and alpha > 0:
        q_bep2_est = (alpha + math.sqrt(disc)) / (2.0 * a_val)
    else:
        q_bep2_est = q_opt_est * 2.0

    q_target = max(q_opt_est * 2.0, q_bep2_est * 1.07)
    q_max_baru = max(40, int(math.ceil(q_target / 5.0) * 5))

    return {
        "kategori": kat_key,
        "nama_usaha": model["nama"],
        "satuan_produk": model["satuan_produk"],
        "wilayah": wilayah,
        "wilayah_catatan": wil["catatan"],
        "kondisi_pasar": kondisi_pasar,
        "kondisi_catatan": kondisi["catatan"],
        "segmen": profile["segmen"],
        "disekonomi_catatan": profile["disekonomi_note"],
        "p": p,
        "c": c_total,
        "b": b_total,
        "a": a_val,
        "q_max": q_max_baru,
        "q_target_harian": aktif["q_target_harian"],
        "modal_bahan_harian": aktif["modal_bahan_harian"],
        "total_modal_harian": aktif["total_modal_harian"],
        "b_min": skenario_harga[1]["b"],
        "b_max": skenario_harga[3]["b"],
        "c_min": skenario_harga[1]["c"],
        "c_max": skenario_harga[3]["c"],
        "modal_harian_min": skenario_harga[1]["total_modal_harian"],
        "modal_harian_max": skenario_harga[3]["total_modal_harian"],
        "var_items": aktif["var_items"],
        "fixed_items": aktif["fixed_items"],
        "skenario_harga": skenario_harga,
    }

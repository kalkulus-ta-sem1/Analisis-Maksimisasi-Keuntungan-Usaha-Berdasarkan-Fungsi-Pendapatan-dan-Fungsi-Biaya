"""
Modul Implementasi Rumus Integral Kalkulus (Mengikuti Kode Rumus PDF A.1-A.5 & B.1-B.5)
serta Penerapannya Secara Langsung pada Model Optimasi Keuntungan UMKM.

Daftar Rumus PDF yang Diterapkan:
- A.1: Integral Tak Tentu Substitusi u: int x(x^2 + 2)^5 dx = (x^2 + 2)^6 / 12 + C
- A.2: Integral Tak Tentu Substitusi u Akar: int (x - 1)/sqrt(x^2 - 2x - 3) dx = sqrt(x^2 - 2x - 3) + C
- A.3: Pecah Pecahan Polinom + ln|x|: int (2x^2 - 5x + 6)/x dx = x^2 - 5x + 6 ln|x| + C
- A.4: Integral Trigonometri Substitusi u=2x: int (sin x + sin 2x - 1/2 sin x) dx = -1/2 cos x - 1/2 cos 2x + C
- A.5: Integral Trigonometri Baku (No. 6): int (3 sec x tan x + csc^2 x) dx = 3 sec x - cot x + C
- B.1: Integral Tentu Substitusi u + Ubah Batas: int_{-1}^2 3x^2 sqrt(x^3 + 1) dx = 18
- B.2: Integral Tentu Trigonometri Substitusi u + Ubah Batas: int_0^{pi/4} sin^2(2x) cos(2x) dx = 1/6
- B.3: Integral Tentu Nilai Mutlak Linier (Pecah Interval): int_0^6 |x - 4| dx = 10
- B.4: Integral Tentu Nilai Mutlak Kuadrat (Pecah Akar): int_0^8 |x^2 - 3x - 4| dx = 80
- B.5: Teorema Dasar Kalkulus I (FTC I) + L'Hopital: lim_{x->0} 1/(6x^3) int_0^x t^2/(t^4 + 1) dt = 1/18
"""

from __future__ import annotations

import math
from typing import Dict, List, Any
import numpy as np


def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def _antideriv_profit(x: float, p: float, c: float, b: float, a: float) -> float:
    """Antiturunan dari P(x) = -a*x^2 + (p - b)*x - c."""
    alpha = p - b
    return (-a / 3.0) * (x ** 3) + (alpha / 2.0) * (x ** 2) - c * x


def _antideriv_marginal_profit(x: float, p: float, b: float, a: float) -> float:
    """Antiturunan dari P'(x) = -2a*x + (p - b) adalah P(x) + c."""
    return -a * (x ** 2) + (p - b) * x


def hitung_integral_umkm(
    p: float,
    c: float,
    b: float,
    a: float,
    q_max: float,
    hari_siklus: int = 30,
    amplitudo_pct: float = 0.15,
) -> Dict[str, Any]:
    """
    Menerapkan rumus-rumus integral dari PDF (B.3, B.4, A.3, B.1, A.4/B.2, B.5)
    secara langsung menggunakan parameter UMKM aktif (p, c, b, a, q_max).
    """
    p = float(p)
    c = float(c)
    b = float(b)
    a = float(a)
    q_max = float(q_max)
    alpha = p - b
    q_opt = (alpha / (2.0 * a)) if a > 0 else 0.0
    p_opt = -a * (q_opt ** 2) + alpha * q_opt - c

    # 1. PENERAPAN B.3: Integral Nilai Mutlak Linier |P'(x)| = |MR - MC| pada [0, x_max]
    q_split_lin = max(0.0, min(q_max, q_opt))
    # Pada [0, q_split_lin], P'(x) >= 0 (jika alpha > 0); pada [q_split_lin, q_max], P'(x) <= 0
    if alpha >= 0:
        kenaikan_laba = _antideriv_marginal_profit(q_split_lin, p, b, a) - _antideriv_marginal_profit(0.0, p, b, a)
        pengikisan_laba = -(_antideriv_marginal_profit(q_max, p, b, a) - _antideriv_marginal_profit(q_split_lin, p, b, a))
    else:
        kenaikan_laba = 0.0
        pengikisan_laba = -(_antideriv_marginal_profit(q_max, p, b, a) - _antideriv_marginal_profit(0.0, p, b, a))
    total_mutlak_linier = kenaikan_laba + pengikisan_laba

    q_grid_lin = np.linspace(0.0, q_max, 1000)
    y_abs_lin = np.abs(-2.0 * a * q_grid_lin + alpha)
    num_mutlak_lin = _trapz(y_abs_lin, q_grid_lin)

    # 2. PENERAPAN B.4: Integral Nilai Mutlak Kuadrat |P(x)| pada [0, x_max]
    D = (alpha ** 2) - (4.0 * a * c)
    roots_in_domain: List[float] = []
    q_bep1 = None
    q_bep2 = None
    if D >= 0 and a > 0:
        sqrt_D = math.sqrt(D)
        q_bep1 = (alpha - sqrt_D) / (2.0 * a)
        q_bep2 = (alpha + sqrt_D) / (2.0 * a)
        for r in (q_bep1, q_bep2):
            if 0.0 < r < q_max:
                roots_in_domain.append(r)
    pts = sorted(list(set([0.0] + roots_in_domain + [q_max])))

    sub_intervals_b4 = []
    area_rugi_total = 0.0
    area_laba_total = 0.0
    for i in range(len(pts) - 1):
        u_lo, u_hi = pts[i], pts[i + 1]
        if u_hi - u_lo < 1e-9:
            continue
        mid = 0.5 * (u_lo + u_hi)
        f_mid = -a * (mid ** 2) + alpha * mid - c
        tanda = "Positif (+)" if f_mid >= 0 else "Negatif (-)"
        val_raw = _antideriv_profit(u_hi, p, c, b, a) - _antideriv_profit(u_lo, p, c, b, a)
        val_abs = val_raw if f_mid >= 0 else -val_raw
        if f_mid >= 0:
            area_laba_total += val_abs
        else:
            area_rugi_total += val_abs
        sub_intervals_b4.append({
            "lo": u_lo,
            "hi": u_hi,
            "tanda": tanda,
            "nilai_abs": val_abs,
        })

    integral_netto_f = _antideriv_profit(q_max, p, c, b, a) - _antideriv_profit(0.0, p, c, b, a)
    rata_laba_domain = integral_netto_f / q_max if q_max > 0 else 0.0
    total_mutlak_kuadrat = area_laba_total + area_rugi_total

    q_grid_quad = np.linspace(0.0, q_max, 1200)
    y_abs_quad = np.abs(-a * (q_grid_quad ** 2) + alpha * q_grid_quad - c)
    num_mutlak_quad = _trapz(y_abs_quad, q_grid_quad)

    # 3. PENERAPAN A.3: Integral Pecahan Polinom Biaya Rata-Rata AC(x) = (a*x^2 + b*x + c)/x = a*x + b + c/x
    q_ac_1 = 1.0
    q_ac_2 = max(2.0, float(round(q_opt)) if q_opt >= 2.0 else float(q_max))
    def _F_ac(q_val: float) -> float:
        return 0.5 * a * (q_val ** 2) + b * q_val + c * math.log(abs(q_val))
    integral_ac = _F_ac(q_ac_2) - _F_ac(q_ac_1)
    rata_rata_ac = integral_ac / (q_ac_2 - q_ac_1)

    # 4. PENERAPAN B.1: Substitusi u + Ubah Batas untuk Biaya Variabel Total VC(q*) = int_0^{q*} (2aq + b) dq
    # Misal u = 2aq + b -> du = 2a dq -> dq = 1/(2a) du; q=0 -> u=b; q=q* -> u = 2a*q* + b = p
    q_sub_hi = max(0.0, q_opt)
    u_lo_b1 = b
    u_hi_b1 = 2.0 * a * q_sub_hi + b
    vc_sub_u = ((u_hi_b1 ** 2) - (u_lo_b1 ** 2)) / (4.0 * a) if a > 0 else 0.0
    vc_langsung = a * (q_sub_hi ** 2) + b * q_sub_hi

    # 5. PENERAPAN A.4 & B.2: Proyeksi Akumulasi Laba 30 Hari dengan Gelombang Harian sin(wt) + sin(2wt)
    # L(t) = P* + dP * (0.5*sin(w*t) + sin(2*w*t)) dengan w = 2*pi/7 (siklus mingguan 7 hari)
    omega = 2.0 * math.pi / 7.0
    delta_p = abs(p_opt) * amplitudo_pct
    T = float(hari_siklus)
    def _F_musim(t_val: float) -> float:
        # int sin(w t) dt = -cos(w t)/w ; int sin(2 w t) dt = -cos(2 w t)/(2 w)
        return (
            p_opt * t_val
            - (delta_p / (2.0 * omega)) * math.cos(omega * t_val)
            - (delta_p / (2.0 * omega)) * math.cos(2.0 * omega * t_val)
        )
    laba_bulanan_musiman = _F_musim(T) - _F_musim(0.0)
    laba_bulanan_datar = p_opt * T

    # 6. PENERAPAN B.5: FTC I + L'Hopital lim_{q->0} (1/q) * int_0^q MC(t) dt = MC(0) = b
    limit_samples = []
    for q_eps in (1.0, 0.1, 0.01, 0.001):
        avc_eps = (a * (q_eps ** 2) + b * q_eps) / q_eps
        limit_samples.append((q_eps, avc_eps))

    return {
        "p": p,
        "c": c,
        "b": b,
        "a": a,
        "q_max": q_max,
        "alpha": alpha,
        "q_opt": q_opt,
        "p_opt": p_opt,
        "q_bep1": q_bep1,
        "q_bep2": q_bep2,
        "b3": {
            "q_split": q_split_lin,
            "kenaikan_laba": kenaikan_laba,
            "pengikisan_laba": pengikisan_laba,
            "total_eksak": total_mutlak_linier,
            "total_numerik": num_mutlak_lin,
        },
        "b4": {
            "sub_intervals": sub_intervals_b4,
            "area_laba": area_laba_total,
            "area_rugi": area_rugi_total,
            "total_mutlak_eksak": total_mutlak_kuadrat,
            "total_mutlak_numerik": num_mutlak_quad,
            "integral_netto": integral_netto_f,
            "rata_laba_domain": rata_laba_domain,
        },
        "a3": {
            "q1": q_ac_1,
            "q2": q_ac_2,
            "integral_ac": integral_ac,
            "rata_rata_ac": rata_rata_ac,
        },
        "b1": {
            "q_hi": q_sub_hi,
            "u_lo": u_lo_b1,
            "u_hi": u_hi_b1,
            "vc_substitusi": vc_sub_u,
            "vc_langsung": vc_langsung,
        },
        "a4_b2": {
            "hari": int(hari_siklus),
            "omega": omega,
            "delta_p": delta_p,
            "laba_bulanan_musiman": laba_bulanan_musiman,
            "laba_bulanan_datar": laba_bulanan_datar,
            "selisih_musiman": laba_bulanan_musiman - laba_bulanan_datar,
        },
        "b5": {
            "limit_eksak": b,
            "samples": limit_samples,
        },
    }


def daftar_soal_pdf() -> List[Dict[str, Any]]:
    return [
        {"kode": "A.1", "judul": "A.1 Substitusi u: ∫ x(x² + 2)⁵ dx"},
        {"kode": "A.2", "judul": "A.2 Substitusi u Akar: ∫ (x - 1) / √(x² - 2x - 3) dx"},
        {"kode": "A.3", "judul": "A.3 Pecah Polinom & ln|x|: ∫ (2x² - 5x + 6) / x dx"},
        {"kode": "A.4", "judul": "A.4 Trigonometri Substitusi: ∫ (sin x + sin 2x - ½ sin x) dx"},
        {"kode": "A.5", "judul": "A.5 (No. 6) Trigonometri Baku: ∫ (3 sec x tan x + csc² x) dx"},
        {"kode": "B.1", "judul": "B.1 Integral Tentu Substitusi u: ∫[-1..2] 3x² √(x³ + 1) dx"},
        {"kode": "B.2", "judul": "B.2 Integral Tentu Trigonometri: ∫[0..π/4] sin²(2x) cos(2x) dx"},
        {"kode": "B.3", "judul": "B.3 Nilai Mutlak Linier: ∫[0..6] |x - 4| dx"},
        {"kode": "B.4", "judul": "B.4 Nilai Mutlak Kuadrat: ∫[0..8] |x² - 3x - 4| dx"},
        {"kode": "B.5", "judul": "B.5 FTC I & L'Hôpital: lim[x->0] 1/(6x³) ∫[0..x] t²/(t⁴ + 1) dt"},
    ]


def evaluasi_soal_pdf(kode: str, x_uji: float = 2.0) -> Dict[str, Any]:
    """
    Mengimplementasikan ke-10 rumus pada PDF sesuai urutan langkah penyelesaiannya,
    lengkap dengan verifikasi numerik (turunan antiturunan / integrasi numerik / konvergensi limit)
    serta data kurva untuk visualisasi Matplotlib.
    """
    if kode == "A.1":
        # Cek numerik pada titik x_uji (hindari singularitas): d/dx F(x) == f(x)
        f_fn = lambda x: x * ((x ** 2 + 2.0) ** 5)
        F_fn = lambda x: ((x ** 2 + 2.0) ** 6) / 12.0
        h = 1e-6
        deriv_num = (F_fn(x_uji + h) - F_fn(x_uji - h)) / (2.0 * h)
        x_arr = np.linspace(-2.0, 2.0, 300)
        y_arr = x_arr * ((x_arr ** 2 + 2.0) ** 5)
        F_arr = ((x_arr ** 2 + 2.0) ** 6) / 12.0
        return {
            "kode": "A.1",
            "jenis": "tak_tentu",
            "soal": "∫ x (x² + 2)⁵ dx",
            "hasil_eksak": "(x² + 2)⁶ / 12 + C",
            "langkah": (
                "1. Identifikasi metode: Substitusi u\n"
                "   misal : u = x² + 2\n"
                "           du = 2x dx  ==>  x dx = (1/2) du\n"
                "2. Substitusi ke integral:\n"
                "   subs  = ∫ u⁵ · (1/2) du\n"
                "         = (1/2) ∫ u⁵ du\n"
                "         = (1/2) · (u⁶ / 6) + C\n"
                "         = u⁶ / 12 + C\n"
                "3. Kembalikan ke variabel x:\n"
                "         = (x² + 2)⁶ / 12 + C"
            ),
            "verifikasi": f"Uji pada x = {x_uji:g}: F({x_uji:g}) = {F_fn(x_uji):,.4f} | dF/dx = {deriv_num:,.4f} == f({x_uji:g}) = {f_fn(x_uji):,.4f}",
            "plot": {"x": x_arr, "y": y_arr, "F": F_arr, "xlabel": "x", "ylabel": "Nilai", "title": "A.1: f(x) = x(x²+2)⁵ dan F(x) = (x²+2)⁶/12"},
        }

    if kode == "A.2":
        # Domain real x^2 - 2x - 3 > 0 -> x < -1 atau x > 3
        x_eval = x_uji if (x_uji > 3.05 or x_uji < -1.05) else 4.0
        f_fn = lambda x: (x - 1.0) / math.sqrt(x ** 2 - 2.0 * x - 3.0)
        F_fn = lambda x: math.sqrt(x ** 2 - 2.0 * x - 3.0)
        h = 1e-6
        deriv_num = (F_fn(x_eval + h) - F_fn(x_eval - h)) / (2.0 * h)
        x_arr = np.linspace(3.15, 7.0, 300)
        y_arr = (x_arr - 1.0) / np.sqrt(x_arr ** 2 - 2.0 * x_arr - 3.0)
        F_arr = np.sqrt(x_arr ** 2 - 2.0 * x_arr - 3.0)
        return {
            "kode": "A.2",
            "jenis": "tak_tentu",
            "soal": "∫ (x - 1) / √(x² - 2x - 3) dx",
            "hasil_eksak": "√(x² - 2x - 3) + C",
            "langkah": (
                "1. Identifikasi metode: Substitusi u (bentuk akar di penyebut)\n"
                "   misal : u = x² - 2x - 3\n"
                "           du = (2x - 2) dx = 2(x - 1) dx\n"
                "           (x - 1) dx = (1/2) du\n"
                "2. Substitusi ke integral:\n"
                "   subs  = ∫ (1 / √u) · (1/2) du\n"
                "         = (1/2) ∫ u^(-1/2) du\n"
                "         = (1/2) · ( u^(1/2) / (1/2) ) + C\n"
                "         = u^(1/2) + C\n"
                "3. Kembalikan ke variabel x:\n"
                "         = √(x² - 2x - 3) + C   (domain real: x < -1 atau x > 3)"
            ),
            "verifikasi": f"Uji pada x = {x_eval:g}: F({x_eval:g}) = {F_fn(x_eval):.6f} | dF/dx = {deriv_num:.6f} == f({x_eval:g}) = {f_fn(x_eval):.6f}",
            "plot": {"x": x_arr, "y": y_arr, "F": F_arr, "xlabel": "x (domain x > 3)", "ylabel": "Nilai", "title": "A.2: f(x) = (x-1)/√(x²-2x-3) dan F(x) = √(x²-2x-3)"},
        }

    if kode == "A.3":
        x_eval = x_uji if abs(x_uji) > 0.1 else 2.0
        f_fn = lambda x: (2.0 * (x ** 2) - 5.0 * x + 6.0) / x
        F_fn = lambda x: (x ** 2) - 5.0 * x + 6.0 * math.log(abs(x))
        h = 1e-6
        deriv_num = (F_fn(x_eval + h) - F_fn(x_eval - h)) / (2.0 * h)
        x_arr = np.linspace(0.4, 6.0, 300)
        y_arr = (2.0 * (x_arr ** 2) - 5.0 * x_arr + 6.0) / x_arr
        F_arr = (x_arr ** 2) - 5.0 * x_arr + 6.0 * np.log(np.abs(x_arr))
        return {
            "kode": "A.3",
            "jenis": "tak_tentu",
            "soal": "∫ (2x² - 5x + 6) / x dx",
            "hasil_eksak": "x² - 5x + 6 ln|x| + C",
            "langkah": (
                "1. Pecah setiap suku pembilang terhadap penyebut x:\n"
                "   = ∫ ( 2x²/x - 5x/x + 6/x ) dx\n"
                "   = ∫ ( 2x - 5 + 6/x ) dx\n"
                "   = ∫ 2x dx - ∫ 5 dx + ∫ (6/x) dx\n"
                "2. Integralkan per suku (Aturan Pangkat & Logaritma Natural):\n"
                "   = 2(x²/2) - 5x + 6 ln|x| + C\n"
                "   = x² - 5x + 6 ln|x| + C\n"
                "   *Catatan verifikasi PDF: pada lembar tulis tangan baris akhir tertulis '6|x|'\n"
                "    tanpa simbol 'ln'; hasil integral baku dari ∫(6/x) dx adalah 6 ln|x|."
            ),
            "verifikasi": f"Uji pada x = {x_eval:g}: F({x_eval:g}) = {F_fn(x_eval):.6f} | dF/dx = {deriv_num:.6f} == f({x_eval:g}) = {f_fn(x_eval):.6f}",
            "plot": {"x": x_arr, "y": y_arr, "F": F_arr, "xlabel": "x (x > 0)", "ylabel": "Nilai", "title": "A.3: f(x) = 2x - 5 + 6/x dan F(x) = x² - 5x + 6 ln|x|"},
        }

    if kode == "A.4":
        f_fn = lambda x: math.sin(x) + math.sin(2.0 * x) - 0.5 * math.sin(x)
        F_fn = lambda x: -0.5 * math.cos(x) - 0.5 * math.cos(2.0 * x)
        h = 1e-6
        deriv_num = (F_fn(x_uji + h) - F_fn(x_uji - h)) / (2.0 * h)
        x_arr = np.linspace(0.0, 2.0 * math.pi, 350)
        y_arr = 0.5 * np.sin(x_arr) + np.sin(2.0 * x_arr)
        F_arr = -0.5 * np.cos(x_arr) - 0.5 * np.cos(2.0 * x_arr)
        return {
            "kode": "A.4",
            "jenis": "tak_tentu",
            "soal": "∫ (sin x + sin 2x - (1/2) sin x) dx",
            "hasil_eksak": "-(1/2) cos x - (1/2) cos 2x + C",
            "langkah": (
                "1. Gabungkan suku sejenis (sin x - 1/2 sin x = 1/2 sin x):\n"
                "   = ∫ ( (1/2) sin x + sin 2x ) dx\n"
                "   = (1/2) ∫ sin x dx + ∫ sin 2x dx\n"
                "2. Substitusi pada suku kedua:\n"
                "   u = 2x,  du = 2 dx  ==>  dx = (1/2) du\n"
                "   ∫ sin 2x dx = (1/2) ∫ sin u du = -(1/2) cos 2x\n"
                "3. Gabungkan seluruh hasil:\n"
                "   = -(1/2) cos x - (1/2) cos 2x + C"
            ),
            "verifikasi": f"Uji pada x = {x_uji:g}: F({x_uji:g}) = {F_fn(x_uji):.6f} | dF/dx = {deriv_num:.6f} == f({x_uji:g}) = {f_fn(x_uji):.6f}",
            "plot": {"x": x_arr, "y": y_arr, "F": F_arr, "xlabel": "x (radian)", "ylabel": "Nilai", "title": "A.4: f(x) = ½ sin x + sin 2x dan F(x) = -½ cos x - ½ cos 2x"},
        }

    if kode == "A.5":
        x_eval = x_uji if abs(math.cos(x_uji)) > 0.15 and abs(math.sin(x_uji)) > 0.15 else 0.8
        f_fn = lambda x: 3.0 * (1.0 / math.cos(x)) * math.tan(x) + (1.0 / (math.sin(x) ** 2))
        F_fn = lambda x: 3.0 * (1.0 / math.cos(x)) - (math.cos(x) / math.sin(x))
        h = 1e-6
        deriv_num = (F_fn(x_eval + h) - F_fn(x_eval - h)) / (2.0 * h)
        x_arr = np.linspace(0.25, 1.30, 300)
        y_arr = 3.0 / np.cos(x_arr) * np.tan(x_arr) + 1.0 / (np.sin(x_arr) ** 2)
        F_arr = 3.0 / np.cos(x_arr) - np.cos(x_arr) / np.sin(x_arr)
        return {
            "kode": "A.5",
            "jenis": "tak_tentu",
            "soal": "∫ (3 sec x tan x + csc² x) dx   (Nomor 6 di PDF)",
            "hasil_eksak": "3 sec x - cot x + C",
            "langkah": (
                "1. Pisahkan dengan sifat linearitas integral:\n"
                "   = 3 ∫ sec x tan x dx + ∫ csc² x dx\n"
                "2. Gunakan rumus integral trigonometri dasar:\n"
                "   * ∫ sec x tan x dx = sec x\n"
                "   * ∫ csc² x dx      = -cot x\n"
                "3. Hasil akhir:\n"
                "   = 3 sec x - cot x + C"
            ),
            "verifikasi": f"Uji pada x = {x_eval:g}: F({x_eval:g}) = {F_fn(x_eval):.6f} | dF/dx = {deriv_num:.6f} == f({x_eval:g}) = {f_fn(x_eval):.6f}",
            "plot": {"x": x_arr, "y": y_arr, "F": F_arr, "xlabel": "x (0.25 .. 1.30 rad)", "ylabel": "Nilai", "title": "A.5 (No. 6): 3 sec x tan x + csc² x dan F(x) = 3 sec x - cot x"},
        }

    if kode == "B.1":
        x_arr = np.linspace(-1.0, 2.0, 500)
        y_arr = 3.0 * (x_arr ** 2) * np.sqrt(np.maximum(0.0, x_arr ** 3 + 1.0))
        num_val = _trapz(y_arr, x_arr)
        eksak = (2.0 / 3.0) * (9.0 ** 1.5) - (2.0 / 3.0) * (0.0 ** 1.5)
        return {
            "kode": "B.1",
            "jenis": "tentu",
            "soal": "∫[-1..2] 3x² √(x³ + 1) dx",
            "hasil_eksak": "18",
            "langkah": (
                "1. Substitusi u dan ubah batas integrasi:\n"
                "   misal : u = x³ + 1  ==>  du = 3x² dx\n"
                "   * Jika x = -1, maka u = (-1)³ + 1 = 0\n"
                "   * Jika x = 2,  maka u = (2)³ + 1  = 9\n"
                "2. Evaluasi integral tentu dalam u:\n"
                "   subs  = ∫[0..9] √u du = ∫[0..9] u^(1/2) du\n"
                "         = [ u^(3/2) / (3/2) ]_0^9\n"
                "         = [ (2/3) u^(3/2) ]_0^9\n"
                "         = (2/3)(9)^(3/2) - (2/3)(0)^(3/2)\n"
                "         = (2/3)(27) - 0\n"
                "         = 18"
            ),
            "verifikasi": f"Hasil analitis = {eksak:.6f} | Verifikasi integrasi numerik (500 titik) = {num_val:.6f}",
            "plot": {"x": x_arr, "y": y_arr, "a": -1.0, "b": 2.0, "xlabel": "x", "ylabel": "3x² √(x³ + 1)", "title": "B.1: Luas Area ∫[-1..2] 3x² √(x³ + 1) dx = 18"},
        }

    if kode == "B.2":
        b_hi = math.pi / 4.0
        x_arr = np.linspace(0.0, b_hi, 500)
        y_arr = (np.sin(2.0 * x_arr) ** 2) * np.cos(2.0 * x_arr)
        num_val = _trapz(y_arr, x_arr)
        eksak = 1.0 / 6.0
        return {
            "kode": "B.2",
            "jenis": "tentu",
            "soal": "∫[0..π/4] sin²(2x) · cos(2x) dx",
            "hasil_eksak": "1/6 (≈ 0.166667)",
            "langkah": (
                "1. Substitusi u dan ubah batas integrasi:\n"
                "   misal : u = sin(2x)\n"
                "           du = 2 cos(2x) dx  ==>  cos(2x) dx = (1/2) du\n"
                "   * Jika x = 0,   maka u = sin 0 = 0\n"
                "   * Jika x = π/4, maka u = sin(2 · π/4) = sin(π/2) = 1\n"
                "2. Evaluasi integral tentu dalam u:\n"
                "   = (1/2) ∫[0..1] u² du\n"
                "   = (1/2) [ u³ / 3 ]_0^1\n"
                "   = (1/6) [ u³ ]_0^1\n"
                "   = (1/6)(1)³ - (1/6)(0)³\n"
                "   = 1/6"
            ),
            "verifikasi": f"Hasil analitis = {eksak:.6f} | Verifikasi integrasi numerik (500 titik) = {num_val:.6f}",
            "plot": {"x": x_arr, "y": y_arr, "a": 0.0, "b": b_hi, "xlabel": "x (0 .. π/4)", "ylabel": "sin²(2x) cos(2x)", "title": "B.2: Luas Area ∫[0..π/4] sin²(2x) cos(2x) dx = 1/6"},
        }

    if kode == "B.3":
        x_arr = np.linspace(0.0, 6.0, 600)
        y_arr = np.abs(x_arr - 4.0)
        num_val = _trapz(y_arr, x_arr)
        i1 = (4.0 * 4.0 - (4.0 ** 2) / 2.0) - 0.0
        i2 = ((6.0 ** 2) / 2.0 - 4.0 * 6.0) - ((4.0 ** 2) / 2.0 - 4.0 * 4.0)
        eksak = i1 + i2
        return {
            "kode": "B.3",
            "jenis": "tentu",
            "soal": "∫[0..6] |x - 4| dx",
            "hasil_eksak": "10",
            "langkah": (
                "1. Cari pembuat nol di dalam mutlak:\n"
                "   x - 4 = 0  ==>  x = 4\n"
                "   * Untuk 0 <= x <= 4, berlaku |x - 4| = 4 - x\n"
                "   * Untuk 4 <= x <= 6, berlaku |x - 4| = x - 4\n"
                "2. Pecah integral sesuai interval:\n"
                "   = ∫[0..4] (4 - x) dx + ∫[4..6] (x - 4) dx\n"
                "   Integral pertama: [ 4x - x²/2 ]_0^4 = (16 - 16/2) - 0 = 16 - 8 = 8\n"
                "   Integral kedua  : [ x²/2 - 4x ]_4^6 = (18 - 24) - (8 - 16) = -6 - (-8) = 2\n"
                "3. Jumlahkan hasil:\n"
                "   = 8 + 2 = 10"
            ),
            "verifikasi": f"Hasil analitis = {eksak:.6f} | Verifikasi integrasi numerik (600 titik) = {num_val:.6f}",
            "plot": {"x": x_arr, "y": y_arr, "a": 0.0, "b": 6.0, "split": [4.0], "xlabel": "x", "ylabel": "|x - 4|", "title": "B.3: Luas Area ∫[0..6] |x - 4| dx = 8 + 2 = 10"},
        }

    if kode == "B.4":
        x_arr = np.linspace(0.0, 8.0, 800)
        y_arr = np.abs((x_arr ** 2) - 3.0 * x_arr - 4.0)
        num_val = _trapz(y_arr, x_arr)
        i1 = (-(4.0 ** 3) / 3.0 + 1.5 * (4.0 ** 2) + 4.0 * 4.0) - 0.0
        i2 = ((8.0 ** 3) / 3.0 - 1.5 * (8.0 ** 2) - 4.0 * 8.0) - ((4.0 ** 3) / 3.0 - 1.5 * (4.0 ** 2) - 4.0 * 4.0)
        eksak = i1 + i2
        return {
            "kode": "B.4",
            "jenis": "tentu",
            "soal": "∫[0..8] |x² - 3x - 4| dx",
            "hasil_eksak": "80",
            "langkah": (
                "1. Cari akar pembuat nol x² - 3x - 4 = 0:\n"
                "   (x - 4)(x + 1) = 0  ==>  x = 4,  x = -1\n"
                "   Pada domain [0, 8]:\n"
                "   * 0 <= x <= 4  --> bertanda negatif: -(x² - 3x - 4) = -x² + 3x + 4\n"
                "   * 4 <= x <= 8  --> bertanda positif:  (x² - 3x - 4)\n"
                "2. Pecah integral menjadi dua bagian:\n"
                "   = ∫[0..4] (-x² + 3x + 4) dx + ∫[4..8] (x² - 3x - 4) dx\n"
                "   Integral pertama: [ -x³/3 + 3x²/2 + 4x ]_0^4 = -64/3 + 24 + 16 = -64/3 + 40 = 56/3\n"
                "   Integral kedua  : [  x³/3 - 3x²/2 - 4x ]_4^8 = (512/3 - 96 - 32) - (64/3 - 24 - 16)\n"
                "                                                 = 128/3 - (-56/3) = 184/3\n"
                "3. Jumlahkan hasil:\n"
                "   = 56/3 + 184/3 = 240/3 = 80"
            ),
            "verifikasi": f"Hasil analitis = {eksak:.6f} (56/3 + 184/3) | Verifikasi integrasi numerik (800 titik) = {num_val:.6f}",
            "plot": {"x": x_arr, "y": y_arr, "a": 0.0, "b": 8.0, "split": [4.0], "xlabel": "x", "ylabel": "|x² - 3x - 4|", "title": "B.4: Luas Area ∫[0..8] |x² - 3x - 4| dx = 56/3 + 184/3 = 80"},
        }

    # B.5: lim_{x->0} 1/(6x^3) * int_0^x t^2/(t^4 + 1) dt
    xs = np.array([0.5, 0.25, 0.1, 0.05, 0.01])
    vals = []
    for xv in xs:
        ts = np.linspace(0.0, xv, 400)
        integ = _trapz((ts ** 2) / (ts ** 4 + 1.0), ts)
        vals.append(integ / (6.0 * (xv ** 3)))
    x_plot = np.linspace(0.01, 0.8, 200)
    y_plot = []
    for xv in x_plot:
        ts = np.linspace(0.0, xv, 150)
        integ = _trapz((ts ** 2) / (ts ** 4 + 1.0), ts)
        y_plot.append(integ / (6.0 * (xv ** 3)))
    return {
        "kode": "B.5",
        "jenis": "limit",
        "soal": "lim[x->0]  1 / (6x³) · ∫[0..x] ( t² / (t⁴ + 1) ) dt",
        "hasil_eksak": "1/18 (≈ 0.055556)",
        "langkah": (
            "1. Identifikasi bentuk tak tentu 0/0 saat x -> 0, gunakan FTC I + Aturan L'Hôpital:\n"
            "   * Turunan pembilang (Teorema Dasar Kalkulus I):\n"
            "     d/dx [ ∫[0..x] t²/(t⁴ + 1) dt ] = x² / (x⁴ + 1)\n"
            "   * Turunan penyebut:\n"
            "     d/dx [ 6x³ ] = 18x²\n"
            "2. Substitusi ke limit L'Hôpital:\n"
            "   = lim[x->0] ( x² / (x⁴ + 1) ) / (18x²)\n"
            "   = lim[x->0] 1 / ( 18(x⁴ + 1) )\n"
            "   = 1 / ( 18(0⁴ + 1) )\n"
            "   = 1 / (18(1)) = 1/18"
        ),
        "verifikasi": "Konvergensi numerik: " + " | ".join(f"x={xv:g} -> {yv:.6f}" for xv, yv in zip(xs, vals)) + f" (eksak 1/18 = {1.0/18.0:.6f})",
        "plot": {"x": x_plot, "y": np.array(y_plot), "limit_y": 1.0 / 18.0, "xlabel": "x -> 0+", "ylabel": "Nilai Ekspresi", "title": "B.5: Konvergensi Limit Menuju 1/18 (≈ 0.055556)"},
    }

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = (
    os.path.dirname(CURRENT_DIR)
    if os.path.basename(CURRENT_DIR) in ("src", "scripts")
    else CURRENT_DIR
)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def _fmt_rp(val: float) -> str:
    if val < 0:
        return f"-Rp {abs(val):,.0f}".replace(",", ".")
    return f"Rp {val:,.0f}".replace(",", ".")


def _fmt_num(val: float) -> str:
    return f"{val:,.0f}".replace(",", ".")


def _signed_poly(quad_c: float, lin_c: float, const_c: float, var: str = "q") -> str:
    parts = []
    if quad_c != 0:
        q_s = f"{abs(quad_c):g}"
        parts.append(f"-{q_s}{var}²" if quad_c < 0 else f"{q_s}{var}²")
    if lin_c != 0:
        l_s = _fmt_num(abs(lin_c))
        sign = " - " if lin_c < 0 else (" + " if parts else "")
        parts.append(f"{sign}{l_s}{var}")
    if const_c != 0:
        c_s = _fmt_num(abs(const_c))
        sign = " - " if const_c < 0 else (" + " if parts else "")
        parts.append(f"{sign}{c_s}")
    return "".join(parts) or "0"


def _rp_axis_formatter() -> FuncFormatter:
    return FuncFormatter(lambda v, _pos: f"{v:,.0f}".replace(",", "."))


def generate_all_graphs(
    p: float = 15000.0,
    c: float = 60000.0,
    b: float = 8000.0,
    a: float = 50.0,
    q_max: int = 140,
) -> None:
    """Generate 3 grafik analisis kalkulus resolusi tinggi ke folder assets/."""
    if a <= 0 or p <= 0 or b < 0 or c < 0 or q_max <= 0:
        raise ValueError("Parameter p, a, dan q_max harus positif serta b dan c tidak boleh negatif.")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    rp_formatter = _rp_axis_formatter()

    alpha = p - b
    q_opt = alpha / (2.0 * a)
    r_opt = p * q_opt
    c_opt = a * (q_opt**2) + b * q_opt + c
    p_opt = r_opt - c_opt

    disc = (alpha**2) - 4.0 * a * c
    if disc >= 0:
        sqrt_d = float(np.sqrt(disc))
        q_bep1 = (alpha - sqrt_d) / (2.0 * a)
        q_bep2 = (alpha + sqrt_d) / (2.0 * a)
    else:
        q_bep1 = None
        q_bep2 = None

    q = np.linspace(0, q_max, 500)
    R = p * q
    C = a * (q**2) + b * q + c
    P = R - C
    MR = np.full_like(q, p)
    MC = 2.0 * a * q + b

    f_zero = -c
    f_end = -a * (float(q_max) ** 2) + alpha * float(q_max) - c
    if abs(f_zero - f_end) < 1e-6:
        min_lbl = f"f(0) = f({q_max}) = {_fmt_rp(f_zero)}"
        min_pts_q = [0.0, float(q_max)]
        min_pts_y = [f_zero, f_end]
        annot_min_q, annot_min_y = 0.0, f_zero
        annot_min_offset = (4.0, f_zero * 0.72 if f_zero < 0 else 12000.0)
    elif f_end < f_zero:
        min_lbl = f"f({q_max}) = {_fmt_rp(f_end)}"
        min_pts_q = [float(q_max)]
        min_pts_y = [f_end]
        annot_min_q, annot_min_y = float(q_max), f_end
        annot_min_offset = (max(2.0, float(q_max) * 0.72), f_end * 0.72 if f_end < 0 else 12000.0)
    else:
        min_lbl = f"f(0) = {_fmt_rp(f_zero)}"
        min_pts_q = [0.0]
        min_pts_y = [f_zero]
        annot_min_q, annot_min_y = 0.0, f_zero
        annot_min_offset = (4.0, f_zero * 0.72 if f_zero < 0 else 12000.0)

    fx_expr = _signed_poly(-a, alpha, -c, "q")
    cx_expr = _signed_poly(a, b, c, "q")
    mc_expr = _signed_poly(0.0, 2.0 * a, b, "q")

    # 1. Kurva Keuntungan f(q)
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_title(f"Fungsi Keuntungan Objektif: f(q) = {fx_expr}", fontsize=12, fontweight="bold", pad=12)
    ax.plot(q, P, color="#10b981", linewidth=2.5, label="Fungsi Keuntungan f(q) = R(q) - C(q)")
    ax.axhline(0, color="#ef4444", linestyle=":", linewidth=1.5, label="Garis Impas f(q) = 0")

    if 0.0 <= q_opt <= float(q_max):
        ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, label=f"Titik Kritis qc = {q_opt:.1f} porsi (f'(qc) = 0)")
        ax.scatter([q_opt], [p_opt], color="#f59e0b", s=90, zorder=5)
        ax.annotate(
            f"Titik Kritis (Nilai Maksimum):\nqc = {q_opt:.1f} porsi/hari | f'(qc) = 0\nf(qc) = {_fmt_rp(p_opt)} (Maks Global)",
            xy=(q_opt, p_opt),
            xytext=(q_opt, max(25000.0, p_opt * 0.48)),
            ha="center",
            arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
            fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#f59e0b", alpha=0.95)
        )

    ax.scatter(min_pts_q, min_pts_y, color="#ef4444", s=70, zorder=5)
    ax.annotate(
        f"Nilai Minimum Mutlak:\n{min_lbl}",
        xy=(annot_min_q, annot_min_y),
        xytext=annot_min_offset,
        arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.2),
        fontsize=8.5, fontweight="bold", color="#ef4444"
    )

    if q_bep1 is not None and q_bep2 is not None:
        bep_safe_y = max(20000.0, abs(p_opt) * 0.14)
        if 0.0 <= q_bep1 <= float(q_max):
            ax.scatter([q_bep1], [0], color="#2563eb", s=60, zorder=5)
            ax.annotate(
                f"BEP 1: {q_bep1:.1f}\nf(q)=0",
                xy=(q_bep1, 0),
                xytext=(max(2.0, float(q_bep1) + 4.0), bep_safe_y),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.2),
                fontsize=8.5, fontweight="bold", color="#2563eb",
            )
        if 0.0 <= q_bep2 <= float(q_max):
            ax.scatter([q_bep2], [0], color="#2563eb", s=60, zorder=5)
            ax.annotate(
                f"BEP 2: {q_bep2:.1f}\nf(q)=0",
                xy=(q_bep2, 0),
                xytext=(max(2.0, float(q_bep2) - 22.0), bep_safe_y),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.2),
                fontsize=8.5, fontweight="bold", color="#2563eb",
            )
        untung_label = f"Zona Laba Positif f(q) >= 0 ({int(np.ceil(q_bep1))} - {int(np.floor(q_bep2))} porsi)"
    else:
        untung_label = "Zona Laba Positif f(q) >= 0"

    ax.fill_between(q, P, 0, where=(P >= 0), interpolate=True, color="#10b981", alpha=0.15, label=untung_label)
    ax.fill_between(q, P, 0, where=(P < 0), interpolate=True, color="#ef4444", alpha=0.15, label="Zona Defisit / Rugi f(q) < 0")

    ax.set_xlabel("Jumlah Porsi Ketoprak per Hari (q)", fontsize=11)
    ax.set_ylabel("Nilai Fungsi Keuntungan f(q) (Rp)", fontsize=11)
    ax.yaxis.set_major_formatter(rp_formatter)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS_DIR, "grafik_keuntungan_maksimum.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 2. Perbandingan Pendapatan Total R(q) vs Total Biaya C(q)
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_title("Perbandingan Pendapatan Total R(q) vs Total Biaya C(q)", fontsize=12, fontweight="bold", pad=12)
    ax.plot(q, R, color="#2563eb", linewidth=2.5, label=f"Pendapatan R(q) = {_fmt_num(p)}q")
    ax.plot(q, C, color="#ef4444", linewidth=2.5, label=f"Biaya Total C(q) = {cx_expr}")

    if 0.0 <= q_opt <= float(q_max):
        ax.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linewidth=3, label=f"Gap Keuntungan Terlebar: {_fmt_rp(p_opt)}")
        ax.scatter([q_opt, q_opt], [c_opt, r_opt], color="#10b981", s=70, zorder=5)
        ax.annotate(
            f"Jarak Vertikal Terbesar (Laba Max):\nq* = {q_opt:.1f} porsi\nR = {_fmt_rp(r_opt)}\nC = {_fmt_rp(c_opt)}\nLaba = {_fmt_rp(p_opt)}",
            xy=(q_opt, (r_opt + c_opt) / 2.0),
            xytext=(min(float(q_max) * 0.62, q_opt + 10.0), max(0.0, (r_opt + c_opt) / 2.0 - r_opt * 0.42)),
            arrowprops=dict(facecolor="#10b981", shrink=0.08, width=1.5, headwidth=7),
            fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#10b981", alpha=0.95)
        )

    ax.set_xlabel("Jumlah Porsi Ketoprak per Hari (q)", fontsize=11)
    ax.set_ylabel("Rupiah (Rp)", fontsize=11)
    ax.yaxis.set_major_formatter(rp_formatter)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS_DIR, "grafik_pendapatan_vs_biaya.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 3. Optimasi Marjinal MR vs MC
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_title("Optimasi Marjinal: Marginal Revenue (MR) vs Marginal Cost (MC)", fontsize=12, fontweight="bold", pad=12)
    ax.plot(q, MR, color="#2563eb", linewidth=2.5, label=f"Pendapatan Marjinal MR(q) = {_fmt_rp(p)}")
    ax.plot(q, MC, color="#ef4444", linewidth=2.5, label=f"Biaya Marjinal MC(q) = {mc_expr}")

    if 0.0 <= q_opt <= float(q_max):
        ax.scatter([q_opt], [p], color="#f59e0b", s=90, zorder=5, label=f"Titik MR = MC di q = {q_opt:.1f} porsi")
        ax.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5)
        ax.annotate(
            f"Perpotongan Optimum MR = MC:\nq* = {q_opt:.1f} porsi\nTarif Marjinal = {_fmt_rp(p)}",
            xy=(q_opt, p),
            xytext=(min(float(q_max) * 0.72, q_opt + 8.0), p * 1.15),
            arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
            fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#f59e0b", alpha=0.95)
        )

    ax.fill_between(q, MR, MC, where=(q <= q_opt), interpolate=True, color="#10b981", alpha=0.15, label="MR > MC (Menambah Porsi Menaikkan Laba)")
    ax.fill_between(q, MR, MC, where=(q > q_opt), interpolate=True, color="#ef4444", alpha=0.15, label="MR < MC (Menambah Porsi Menurunkan Laba)")

    ax.set_xlabel("Jumlah Porsi Ketoprak per Hari (q)", fontsize=11)
    ax.set_ylabel("Rupiah per Porsi (Rp/porsi)", fontsize=11)
    ax.yaxis.set_major_formatter(rp_formatter)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS_DIR, "grafik_marjinal_mr_mc.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Semua gambar grafik resolusi tinggi berhasil dibuat.")


if __name__ == "__main__":
    try:
        generate_all_graphs()
    except Exception as exc:
        print(f"Gagal membuat gambar grafik: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        plt.close("all")

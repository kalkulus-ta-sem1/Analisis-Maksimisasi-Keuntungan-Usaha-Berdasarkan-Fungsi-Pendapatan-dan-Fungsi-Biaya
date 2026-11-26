import matplotlib.pyplot as plt
import numpy as np

p = 15000.0
c = 60000.0
b = 8000.0
a = 50.0
q_max = 140

q_opt = (p - b) / (2.0 * a)
r_opt = p * q_opt
c_opt = a * (q_opt**2) + b * q_opt + c
p_opt = r_opt - c_opt

D = (p - b)**2 - 4 * a * c
q_bep1 = ((p - b) - np.sqrt(D)) / (2.0 * a)
q_bep2 = ((p - b) + np.sqrt(D)) / (2.0 * a)

q = np.linspace(0, q_max, 500)
R = p * q
C = a * (q**2) + b * q + c
P = R - C
MR = np.full_like(q, p)
MC = 2.0 * a * q + b

plt.figure(figsize=(9, 5.5), dpi=300)
plt.title("Fungsi Keuntungan Objektif: f(q) = -50q² + 7.000q - 60.000", fontsize=12, fontweight="bold", pad=12)
plt.plot(q, P, color="#10b981", linewidth=2.5, label="Fungsi Keuntungan f(q) = R(q) - C(q)")
plt.axhline(0, color="#ef4444", linestyle=":", linewidth=1.5, label="Garis Impas f(q) = 0")
plt.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5, label=f"Titik Kritis qc = {q_opt:.0f} porsi (f'(qc) = 0)")
plt.scatter([q_opt], [p_opt], color="#f59e0b", s=90, zorder=5)

plt.annotate(
    f"Titik Kritis (Nilai Maksimum):\nqc = {q_opt:.0f} porsi/hari | f'(qc) = 0\nf(qc) = Rp {p_opt:,.0f} (Maks Global)".replace(",", "."),
    xy=(q_opt, p_opt),
    xytext=(q_opt + 8, p_opt * 0.82),
    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
    fontsize=9, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#f59e0b", alpha=0.95)
)

plt.scatter([0], [-c], color="#ef4444", s=70, zorder=5)
plt.annotate(
    f"Nilai Minimum Mutlak:\nf(0) = -Rp {c:,.0f}".replace(",", "."),
    xy=(0, -c),
    xytext=(3, -c * 0.75),
    fontsize=8.5, fontweight="bold", color="#ef4444"
)

plt.scatter([q_bep1, q_bep2], [0, 0], color="#2563eb", s=60, zorder=5)
plt.annotate(f"BEP 1: {q_bep1:.1f}\nf(q)=0", xy=(q_bep1, 0), xytext=(q_bep1 - 18, 20000), fontsize=8.5, fontweight="bold", color="#2563eb")
plt.annotate(f"BEP 2: {q_bep2:.1f}\nf(q)=0", xy=(q_bep2, 0), xytext=(q_bep2 - 14, 20000), fontsize=8.5, fontweight="bold", color="#2563eb")

plt.fill_between(q, P, 0, where=(P >= 0), color="#10b981", alpha=0.15, label="Zona Laba Positif f(q) >= 0 (10 - 130 porsi)")
plt.fill_between(q, P, 0, where=(P < 0), color="#ef4444", alpha=0.15, label="Zona Defisit / Rugi f(q) < 0")

plt.xlabel("Jumlah Porsi Ketoprak per Hari (q)", fontsize=11)
plt.ylabel("Nilai Fungsi Keuntungan f(q) (Rp)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper right", fontsize=8.5)
plt.tight_layout()
plt.savefig("grafik_keuntungan_maksimum.png", dpi=300)
plt.close()

plt.figure(figsize=(9, 5.5), dpi=300)
plt.title("Perbandingan Pendapatan Total R(q) vs Total Biaya C(q)", fontsize=12, fontweight="bold", pad=12)
plt.plot(q, R, color="#2563eb", linewidth=2.5, label="Pendapatan R(q) = 15.000q")
plt.plot(q, C, color="#ef4444", linewidth=2.5, label="Biaya Total C(q) = 50q² + 8.000q + 60.000")

plt.plot([q_opt, q_opt], [c_opt, r_opt], color="#10b981", linewidth=3, label=f"Gap Keuntungan Terlebar: Rp {p_opt:,.0f}".replace(",", "."))
plt.scatter([q_opt, q_opt], [c_opt, r_opt], color="#10b981", s=70, zorder=5)

plt.annotate(
    f"Jarak Vertikal Terbesar (Laba Max):\nq* = {q_opt:.0f} porsi\nR = Rp {r_opt:,.0f}\nC = Rp {c_opt:,.0f}\nLaba = Rp {p_opt:,.0f}".replace(",", "."),
    xy=(q_opt, (r_opt + c_opt) / 2),
    xytext=(q_opt + 10, (r_opt + c_opt) / 2 - 100000),
    arrowprops=dict(facecolor="#10b981", shrink=0.08, width=1.5, headwidth=7),
    fontsize=9, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#10b981", alpha=0.95)
)

plt.xlabel("Jumlah Porsi Ketoprak per Hari (q)", fontsize=11)
plt.ylabel("Rupiah (Rp)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper left", fontsize=8.5)
plt.tight_layout()
plt.savefig("grafik_pendapatan_vs_biaya.png", dpi=300)
plt.close()

plt.figure(figsize=(9, 5.5), dpi=300)
plt.title("Optimasi Marjinal: Marginal Revenue (MR) vs Marginal Cost (MC)", fontsize=12, fontweight="bold", pad=12)
plt.plot(q, MR, color="#2563eb", linewidth=2.5, label="Pendapatan Marjinal MR(q) = Rp 15.000")
plt.plot(q, MC, color="#ef4444", linewidth=2.5, label="Biaya Marjinal MC(q) = 100q + 8.000")
plt.scatter([q_opt], [p], color="#f59e0b", s=90, zorder=5, label=f"Titik MR = MC di q = {q_opt:.0f} porsi")
plt.axvline(q_opt, color="#f59e0b", linestyle="--", linewidth=1.5)

plt.annotate(
    f"Perpotongan Optimum MR = MC:\nq* = {q_opt:.0f} porsi\nTarif Marjinal = Rp {p:,.0f}".replace(",", "."),
    xy=(q_opt, p),
    xytext=(q_opt + 8, p * 1.15),
    arrowprops=dict(facecolor="#f59e0b", shrink=0.08, width=1.5, headwidth=7),
    fontsize=9, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#f59e0b", alpha=0.95)
)

plt.fill_between(q, MR, MC, where=(q <= q_opt), color="#10b981", alpha=0.15, label="MR > MC (Menambah Porsi Menaikkan Laba)")
plt.fill_between(q, MR, MC, where=(q > q_opt), color="#ef4444", alpha=0.15, label="MR < MC (Menambah Porsi Menurunkan Laba)")

plt.xlabel("Jumlah Porsi Ketoprak per Hari (q)", fontsize=11)
plt.ylabel("Rupiah per Porsi (Rp/porsi)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper right", fontsize=8.5)
plt.tight_layout()
plt.savefig("grafik_marjinal_mr_mc.png", dpi=300)
plt.close()

print("Semua gambar grafik resolusi tinggi berhasil dibuat.")

"""Step 5.3 — partial widths of the vector mediator and BR(V -> chi chi).

Inputs (read-only): data/relic/band_v2.csv, data/relic/band_v2_validity2.csv

Formulae (tree level, NLO QCD factor for quarks):
    Gamma(V -> chi1 chi2) = (g_chi/2)^2 M/(12 pi) * beta (3 - beta^2)/2
    Gamma(V -> q qbar)    = 3 g_Vq^2 M/(12 pi) * beta_q (3 - beta_q^2)/2 * (1+alpha_s/pi)

    beta^2 = 1 - (m1+m2)^2/M^2      (Delta m = 1 MeV, corrections O(1e-10))
    beta_q^2 = 1 - 4 m_q^2/M^2

Output: data/relic/widths_v2.csv
"""
import csv
import math

MQ = {"u": 0.0022, "d": 0.0047, "s": 0.093, "c": 1.27, "b": 4.18, "t": 172.0}
AS = 0.12
NLO = 1.0 + AS / math.pi
BAND = "/home/yy/lz-event/phenomenology/data/relic/band_v2.csv"
VAL = "/home/yy/lz-event/phenomenology/data/relic/band_v2_validity2.csv"
OUT = "/home/yy/lz-event/phenomenology/data/relic/widths_v2.csv"


def phase(beta2):
    """beta(3-beta^2)/2, zero below threshold."""
    if beta2 <= 0:
        return 0.0
    b = math.sqrt(beta2)
    return b * (3.0 - beta2) / 2.0


def widths(mv, gt, m1, gchi):
    m2 = m1 + 0.001
    w = {}
    w["chi"] = (gchi / 2.0) ** 2 * mv / (12 * math.pi) * phase(1 - ((m1 + m2) / mv) ** 2)
    for q, mq in MQ.items():
        gq = gt * mq / 172.0
        w[q] = 3.0 * gq * gq * mv / (12 * math.pi) * phase(1 - (2 * mq / mv) ** 2) * NLO
    tot = sum(w.values())
    return w, tot


def main():
    val = {(r["MV"], r["gt"]): r for r in csv.DictReader(open(VAL))}
    rows = list(csv.DictReader(open(BAND)))
    out = []
    worst = 0.0
    for r in sorted(rows, key=lambda z: (float(z["MV"]), float(z["gt"]))):
        mv, gt = float(r["MV"]), float(r["gt"])
        m1, gc = float(r["mchi"]), float(r["gchi"])
        w, tot = widths(mv, gt, m1, gc)
        v = val[(r["MV"], r["gt"])]
        g_prev = float(v["Gamma"])
        rel = abs(tot - g_prev) / g_prev if g_prev else 0.0
        worst = max(worst, rel)
        ssum = sum(w.values())
        out.append(dict(MV="%.0f" % mv, gt="%.1f" % gt, mchi="%.4f" % m1, gchi="%.5f" % gc,
                        G_chi="%.4e" % w["chi"], G_u="%.3e" % w["u"], G_d="%.3e" % w["d"],
                        G_s="%.3e" % w["s"], G_c="%.3e" % w["c"], G_b="%.3e" % w["b"],
                        G_t="%.3e" % w["t"], G_tot="%.5e" % tot, BRinv="%.6f" % (w["chi"] / tot),
                        sum_check="%.1e" % (abs(ssum - tot) / tot),
                        d_vs_validity="%.2e" % rel, verdict=v["verdict"]))
    with open(OUT, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0]))
        wr.writeheader()
        wr.writerows(out)
    print("wrote", OUT, len(out), "rows;  max |Gamma_new-Gamma_validity|/Gamma = %.2e" % worst)


if __name__ == "__main__":
    main()

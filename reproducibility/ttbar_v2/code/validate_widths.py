"""Step 5.4.1 -- compare our analytic mediator widths with micrOMEGAs/CalcHEP.

Analytic side is recomputed here at full precision (NOT read from the rounded
columns of widths_v2.csv, whose G_q would suffer from cancellation when
Gamma_q << Gamma_tot).

For every row of data/relic/widths_v2.csv:
  * build the param card (same numbers the relic/width chain used),
  * run PDmq/width_drv (pWidth("V") + printPartialWidth with 8 digits),
  * compare Gamma_tot, Gamma(V->chi1 chi2) and each quark channel with
    the tree-level analytic values; the QCD factor 1+alpha_s/pi is applied
    separately so that like is compared with like.

Output: cmsrepro/phase15/width_validation.csv
"""
import csv
import math
import os
import re
import subprocess

ROOT = "/home/yy/lz-event/phenomenology"
PD = os.path.join(ROOT, "tools/micromegas_7.1.10/PDmq")
SRC = os.path.join(ROOT, "data/relic/widths_v2.csv")
GRID = os.path.join(ROOT, "cmsrepro/phase15/grid_v2.csv")
OUT = os.path.join(ROOT, "cmsrepro/phase15/width_validation.csv")
MQ = [("u", 0.0022), ("d", 0.0047), ("s", 0.093), ("c", 1.27), ("b", 4.18), ("t", 172.0)]
NLO = 1.0 + 0.12 / math.pi
CH = {"u": "u,U", "d": "d,D", "s": "s,S", "c": "c,C", "b": "b,B", "t": "t,T"}


def analytic(mv, gt, m1, gchi):
    m2 = m1 + 0.001
    b2 = 1.0 - ((m1 + m2) / mv) ** 2
    g = (gchi / 2.0) ** 2 * mv / (12 * math.pi) * (math.sqrt(b2) * (3 - b2) / 2 if b2 > 0 else 0.0)
    q = {}
    for name, mq in MQ:
        bq2 = 1.0 - (2 * mq / mv) ** 2
        q[name] = (3 * (gt * mq / 172.0) ** 2 * mv / (12 * math.pi)
                   * (math.sqrt(bq2) * (3 - bq2) / 2 if bq2 > 0 else 0.0))
    return g, q


def run(mv, gt, mchi, gchi, tag):
    par = os.path.join(PD, "wd_%s.par" % tag)
    with open(par, "w") as f:
        f.write("Mchi %.6f\ndM 0.001\nMV %.6f\ngChi %.8e\n" % (mchi, mv, gchi))
        for q, mq in MQ:
            f.write("gV%s %.6e\n" % (q, gt * mq / 172.0))
        f.write("fExc 0.5\nrho0 0.3\nv0 238\nvE 254\nvesc 544\n")
    r = subprocess.run(["./width_drv", par], capture_output=True, text=True, cwd=PD, timeout=300)
    mt = re.search(r"WIDTH_V_TOTAL\s+([\d.eE+-]+)", r.stdout)
    if not mt:
        return None
    tot = float(mt.group(1))
    part = {}
    for line in r.stdout.splitlines():
        m = re.match(r"\s*([\d.eE+-]+)\s+([\d.eE+-]+) GeV\s+V -> (\S+)", line)
        if m:
            part[m.group(3)] = float(m.group(2))
    return tot, part


def main():
    rows = list(csv.DictReader(open(SRC)))
    valid = {(round(float(x["MV"])), round(float(x["gt"]), 4))
             for x in csv.DictReader(open(GRID)) if x["status"] == "ok"}
    out = []
    for i, r in enumerate(rows):
        mv, gt = float(r["MV"]), float(r["gt"])
        mchi, gchi = float(r["mchi"]), float(r["gchi"])
        res = run(mv, gt, mchi, gchi, "p%d" % i)
        if res is None:
            print("FAILED", mv, gt)
            continue
        tot_m, part = res
        gx_m = part.get("~x1,~x2", 0.0)
        g_an, q_an = analytic(mv, gt, mchi, gchi)
        gq_an = sum(q_an.values())
        rec = dict(
            MV="%.0f" % mv, gt="%.4f" % gt, mchi="%.4f" % mchi, gchi="%.5f" % gchi,
            valid=int((round(mv), round(gt, 4)) in valid),
            G_tot_micro="%.8e" % tot_m, G_chi_micro="%.8e" % gx_m, G_q_micro="%.8e" % (tot_m - gx_m),
            G_tot_an_tree="%.8e" % (g_an + gq_an), G_tot_an_qcd="%.8e" % (g_an + gq_an * NLO),
            G_chi_an="%.8e" % g_an, G_q_an="%.8e" % gq_an,
            d_chi="%.2e" % ((g_an - gx_m) / gx_m) if gx_m else "",
            d_tot_tree="%.2e" % ((g_an + gq_an - tot_m) / tot_m),
            d_tot_qcd="%.2e" % ((g_an + gq_an * NLO - tot_m) / tot_m),
            BR_micro="%.6f" % (gx_m / tot_m), BR_an="%.6f" % (g_an / (g_an + gq_an * NLO)),
            GM="%.4f" % (tot_m / mv),
        )
        for q, _ in MQ[:5]:
            rec["d_" + q] = ("%.2e" % ((q_an[q] - part.get(CH[q], 0.0)) / part.get(CH[q], 1.0))
                             if part.get(CH[q], 0) > 1e-12 else "")
        out.append(rec)
        print("%3d MV=%3.0f gt=%4.2f  d_tot_tree=%+.2e  d_tot_qcd=%+.2e  d_chi=%s"
              % (i, mv, gt, float(rec["d_tot_tree"]), float(rec["d_tot_qcd"]), rec["d_chi"]), flush=True)

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote", OUT, len(out), "rows")

if __name__ == "__main__":
    main()

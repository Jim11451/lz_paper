"""Step 5.2 — relic band with the corrected LZ normalisation (N0 = 1.12044).

For every (M_V, g_t) on the grid:

    g_chi(m) = kappa_v2(m) * M_V^2 / g_t        (kappa v2, 36 nodes, linear interp)
    solve  Omega h^2 = 0.1200  for m_chi        (implicit: kappa depends on m)

Rules implemented:
  * no extrapolation of kappa: m_chi is confined to [8.0, 47.778] (the v2 nodes);
  * 2 m_chi < M_V - 1 MeV is required (on-shell mediator);
  * every sign change of (Omega - 0.12) on a 10-point grid is bracketed and
    bisected; all roots are recorded with their branch index;
  * failures and out-of-range cases are written with an explicit status.

Output: data/relic/band_v2.csv
        data/relic/band_v2.log
"""
import csv
import math
import multiprocessing as mp
import os
import re
import subprocess
import time

BASE = "/home/yy/lz-event/phenomenology/tools/micromegas_7.1.10/PDmq"
KCSV = "/home/yy/lz-event/phenomenology/data/relic/kappa_lz_gN_v2.csv"
OUT = "/home/yy/lz-event/phenomenology/data/relic/band_v2.csv"
LOG = "/home/yy/lz-event/phenomenology/data/relic/band_v2.log"
M_Q = {"u": 0.0022, "d": 0.0047, "s": 0.093, "c": 1.27, "b": 4.18, "t": 172.0}
TARGET, TOL = 0.1200, 0.005
MVS = [20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]
GTS = [0.5, 1.0, 1.5, 2.0, 3.0]

KAP, KS = {}, []
for r in csv.DictReader(open(KCSV)):
    KAP[float(r["mchi"])] = float(r["kappa"])
    KS.append(float(r["mchi"]))
KS.sort()
KMIN, KMAX = KS[0], KS[-1]


def kappa(m):
    if m < KMIN or m > KMAX:
        return None
    lo, hi = KMIN, KMAX
    for a, b in zip(KS, KS[1:]):
        if a <= m <= b:
            return KAP[a] + (KAP[b] - KAP[a]) * (m - a) / (b - a)
    return KAP[KMAX]


def omega(m, mv, gt, tag):
    k = kappa(m)
    if k is None:
        return None, None
    g = k * mv ** 2 / gt
    par = os.path.join(BASE, "b2_%s.par" % tag)
    with open(par, "w") as f:
        f.write("Mchi %.8g\ndM 0.001\nMV %.8g\ngChi %.8e\n" % (m, mv, g))
        for q, mq in M_Q.items():
            f.write("gV%s %.6e\n" % (q, gt * mq / 172.0))
        f.write("fExc 0.5\nrho0 0.3\nv0 238\nvE 254\nvesc 544\n")
    r = subprocess.run(["./main", par], capture_output=True, text=True, cwd=BASE, timeout=600)
    mm = re.search(r"darkOmega=\s*([\d.eE+-]+)", r.stdout + r.stderr)
    return g, (float(mm.group(1)) if mm else None)


def solve(job):
    idx, mv, gt = job
    try:
        tag = "w%d" % mp.current_process()._identity[0]
    except IndexError:
        tag = "w0"
    mlo = KMIN + 1e-3
    mhi = min(KMAX - 1e-3, 0.5 * (mv - 1e-3))
    rows = []
    if mhi <= mlo:
        rows.append([mv, gt, "", "", "", "", "no_range(2m>MV or kappa range)"])
        return rows
    n = 10
    grid = [mlo * (mhi / mlo) ** (i / (n - 1)) for i in range(n)]
    vals = []
    for m in grid:
        g, o = omega(m, mv, gt, tag)
        vals.append((m, g, o))
    good = [(m, g, o) for m, g, o in vals if o is not None and o > 0]
    branches = 0
    for (m1, g1, o1), (m2, g2, o2) in zip(good, good[1:]):
        if (o1 - TARGET) * (o2 - TARGET) < 0:
            lo, hi, flo = m1, m2, o1
            best = None
            for _ in range(9):
                mid = 0.5 * (lo + hi)
                g, o = omega(mid, mv, gt, tag)
                if o is None:
                    break
                best = (mid, g, o)
                if abs(o / TARGET - 1) < TOL:
                    break
                if (flo - TARGET) * (o - TARGET) < 0:
                    hi = mid
                else:
                    lo, flo = mid, o
            if best:
                branches += 1
                m, g, o = best
                ok = 2 * m < mv
                rows.append([mv, gt, "%.4f" % m, "%.6e" % g, "%.6f" % o,
                             str(branches), "ok" if ok else "violates 2m<MV"])
    if branches == 0:
        mn = min(good, key=lambda t: abs(t[2] - TARGET)) if good else None
        note = "no_root in [%.2f,%.2f]" % (mlo, mhi)
        if mn:
            note += " closest m=%.2f Omega=%.4g" % (mn[0], mn[2])
        rows.append([mv, gt, "", "", "", "", note])
    return rows


if __name__ == "__main__":
    jobs = [(i, mv, gt) for i, (mv, gt) in enumerate((a, b) for a in MVS for b in GTS)]
    t0 = time.time()
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["MV", "gt", "mchi", "gchi", "omega", "branch", "status"])
        with mp.Pool(8) as pool:
            for rows in pool.imap_unordered(solve, jobs):
                w.writerows(rows)
                fh.flush()
                for r in rows:
                    print("%6s %5s  m=%-8s g=%-11s Om=%-9s br=%-2s %s" % tuple(r), flush=True)
    with open(LOG, "w") as lg:
        lg.write("Step 5.2 relic band, corrected kappa (N0=1.12044)\n")
        lg.write("kappa   %s\nMVs     %s\nGTs     %s\n" % (KCSV, MVS, GTS))
        lg.write("target  %.4f  tol %.3f\n" % (TARGET, TOL))
        lg.write("kappa range [%.3f, %.3f]  (no extrapolation)\n" % (KMIN, KMAX))
        lg.write("elapsed %.1f min\n" % ((time.time() - t0) / 60))
    print("DONE %.1f min" % ((time.time() - t0) / 60))

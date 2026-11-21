"""Step 5.4 -- extend the relic band below g_t = 0.5 (the grid uses g_t down to 0.1).

The map grid is logspace(0.1, sqrt(4pi), 44); the band was only solved at
g_t = 0.5 ... 3.0, so for g_t < 0.5 m_chi had to be clamped -- an extrapolation.
This script solves the missing low-g_t points with the same machinery
(solve_band_v2.solve) and writes data/relic/band_v2_ext.csv.

Nothing is overwritten: band_v2.csv stays as produced in Step 5.2.
"""
import csv
import multiprocessing as mp
import os
import sys

sys.path.insert(0, "/home/yy/.hermes/cache/scratch/relic")
import solve_band_v2 as S          # noqa: E402

OUT = "/home/yy/lz-event/phenomenology/data/relic/band_v2_ext.csv"
GTS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]


def job(a):
    mv, gt = a
    rows = S.solve((0, mv, gt))
    return [(mv, gt, r) for r in rows]


if __name__ == "__main__":
    jobs = [(float(mv), gt) for mv in S.MVS for gt in GTS]
    out = []
    with mp.Pool(8) as pool:
        for res in pool.imap_unordered(job, jobs):
            for mv, gt, r in res:
                out.append((mv, gt, r))
                print("MV=%5.0f gt=%.2f  m=%-9s g=%-11s Om=%-9s %s" % (mv, gt, r[2], r[3], r[4], r[6]), flush=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["MV", "gt", "mchi", "gchi", "omega", "branch", "status"])
        for mv, gt, r in sorted(out, key=lambda z: (z[0], z[1])):
            w.writerow([mv, gt, r[2], r[3], r[4], r[5], r[6]])
    print("wrote", OUT, len(out), "rows")

"""Step 5.4 -- exclusion grid with the corrected kappa (v2), relic band (v2) and widths (v2).

New with respect to cmsrepro/phase14/map_final.py:
  * kappa from data/relic/kappa_lz_gN_v2.csv (N0 = 1.12044, corrected prefactor);
  * m_chi from data/relic/band_v2.csv (per (M_V, g_t), linear in g_t, clamped
    outside the solved range and flagged);
  * Gamma_V and BR(V->chi chi) recomputed per grid point with the Step-5.3
    formulae (identical to final_plot2.widths, checked there);
  * the full validity set of the reference paper: 0.10 <= g_chi <= 1.50,
    0.1 <= g_t <= sqrt(4 pi), Gamma/M < 0.03, M_V - 2 m_chi >= 5 Gamma,
    m_chi >= 20 GeV;
  * every one of the 44 x 14 points is written with an explicit status.

Signal model (unchanged, verified in Step 5.4 stage 2):
    s_bin = shape(M_V) * eff(M_V) * sigma(M_V) * L * g_t^2 * BR_inv
with shape/eff from the existing Delphes samples (m_chi-independent), sigma at
g_t = 1 with the decay forced, so both g_t^2 and BR are applied exactly once.

Outputs (nothing overwritten):
    cmsrepro/phase15/grid_v2.npz
    cmsrepro/phase15/grid_v2.csv
    cmsrepro/phase15/shapes_v2.npz   (cache of the 14 shape/eff pairs)
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/yy/lz-event/phenomenology"
sys.path.insert(0, "/home/yy/.hermes/cache/scratch/ttDM")
sys.path.insert(0, os.path.join(ROOT, "cmsrepro/phase3"))
import final_plot as fp            # noqa: E402
import sys_likelihood as sl        # noqa: E402
import recompute2 as R             # noqa: E402

HS = "/home/yy/.hermes/cache/scratch/phase14/root"
KAPPA_CSV = os.path.join(ROOT, "data/relic/kappa_lz_gN_v2.csv")
BAND_CSV = os.path.join(ROOT, "data/relic/band_v2.csv")
SIGMA_CSV = os.path.join(ROOT, "data/lz/sigma_MV.csv")
SHAPES = os.path.join(HERE, "shapes_v2.npz")
LUMI = float(fp.LUMI)
SQ4PI = math.sqrt(4 * math.pi)
MVS = [20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]
GTS = np.logspace(math.log10(0.1), math.log10(SQ4PI), 44)
MQ = {"u": 0.0022, "d": 0.0047, "s": 0.093, "c": 1.27, "b": 4.18, "t": 172.0}
NLO = 1.0 + 0.12 / math.pi

# ---- inputs ---------------------------------------------------------------
KAP = {}
for r in csv.DictReader(open(KAPPA_CSV)):
    KAP[float(r["mchi"])] = float(r["kappa"])
_ks = sorted(KAP)
KMIN, KMAX = _ks[0], _ks[-1]

SIG = {float(r["MV"]): float(r["xsec_pb"]) for r in csv.DictReader(open(SIGMA_CSV))}

BAND = {}
for r in csv.DictReader(open(BAND_CSV)):
    BAND.setdefault(float(r["MV"]), []).append((float(r["gt"]), float(r["mchi"])))
# extension solved by cmsrepro/phase15/extend_band.py for g_t < 0.5
EXT = os.path.join(ROOT, "data/relic/band_v2_ext.csv")
if os.path.exists(EXT):
    for r in csv.DictReader(open(EXT)):
        if not r["mchi"].strip():
            continue
        BAND.setdefault(float(r["MV"]), []).append((float(r["gt"]), float(r["mchi"])))
for k in BAND:
    BAND[k] = sorted(set(BAND[k]))


def kappa(m):
    if m < KMIN or m > KMAX:
        return None
    return float(np.interp(m, _ks, [KAP[k] for k in _ks]))


def mchi_of(mv, gt):
    """linear in g_t; clamped outside the solved range (band is flat there)."""
    pts = BAND[mv]
    g = [p[0] for p in pts]
    m = [p[1] for p in pts]
    if gt < g[0] * (1 - 1e-6):
        return None, "no_band"
    if gt > g[-1] * (1 + 1e-6):
        return None, "no_band"
    return float(np.interp(gt, g, m)), "interp"


def widths(mv, gt, m1, gchi):
    m2 = m1 + 0.001
    b2 = 1.0 - ((m1 + m2) / mv) ** 2
    g = 0.0
    if b2 > 0:
        b = math.sqrt(b2)
        g = (gchi / 2.0) ** 2 * mv / (12 * math.pi) * b * (3 - b2) / 2
    q = 0.0
    for mq in MQ.values():
        bq2 = 1.0 - (2 * mq / mv) ** 2
        if bq2 > 0:
            bq = math.sqrt(bq2)
            q += 3 * (gt * mq / 172.0) ** 2 * mv / (12 * math.pi) * bq * (3 - bq2) / 2 * NLO
    return g, q


def load_shapes():
    if os.path.exists(SHAPES):
        d = np.load(SHAPES)
        return d["shape"], d["eff"]
    shape = np.zeros((len(MVS), 15))
    eff = np.zeros(len(MVS))
    for j, mv in enumerate(MVS):
        h = np.asarray(fp.shape(os.path.join(HS, "sig_MV%g.root" % mv)), float)
        n = 0
        import uproot
        n = uproot.open(os.path.join(HS, "sig_MV%g.root" % mv))["Delphes"].num_entries
        eff[j] = h.sum() / n
        shape[j] = h / h.sum()
        print("  shape MV=%3d eff=%.5f npass=%d/%d" % (mv, eff[j], h.sum(), n), flush=True)
    np.savez(SHAPES, shape=shape, eff=eff, MVS=np.array(MVS))
    return shape, eff


def main():
    shape, eff = load_shapes()
    edges, procs, b, sb, data = sl.load()
    w = float(sb.sum() / b.sum())
    print("background: %d bins, sum b=%.1f, coherent width w=%.4f" % (len(b), b.sum(), w))

    rows = []
    ZE = np.full((len(GTS), len(MVS)), np.nan)
    ZO = np.full((len(GTS), len(MVS)), np.nan)
    for j, mv in enumerate(MVS):
        sig = SIG[float(mv)]
        for i, gt in enumerate(GTS):
            m, bflag = mchi_of(mv, gt)
            if m is None:
                rec = dict(MV=mv, gt=gt, mchi=None, band=bflag, kappa=None, gchi=None,
                           Gamma=None, BR=None, S=None, SoB=None, mu95_exp=None,
                           mu95_obs=None, status="invalid:no_band")
                rows.append(rec)
                continue
            k = kappa(m)
            rec = dict(MV=mv, gt=gt, mchi=m, band=bflag, kappa=k, gchi=None,
                       Gamma=None, BR=None, S=None, SoB=None, mu95_exp=None,
                       mu95_obs=None, status="")
            if k is None:
                rec["status"] = "invalid:kappa_out_of_range"
                rows.append(rec)
                continue
            gchi = k * mv ** 2 / gt
            rec["gchi"] = gchi
            g, q = widths(mv, gt, m, gchi)
            rec["Gamma"] = g + q
            rec["BR"] = g / (g + q) if (g + q) > 0 else 0.0
            bad = []
            if not (0.10 <= gchi <= 1.50):
                bad.append("gchi")
            if m < 20.0:
                bad.append("mchi<20")
            if (g + q) / mv >= 0.03:
                bad.append("G/M")
            if mv - 2 * m - 1e-3 < 5 * (g + q):
                bad.append("5Gamma")
            if 2 * m >= mv:
                bad.append("2m>=MV")
            s = shape[j] * eff[j] * sig * LUMI * gt ** 2 * rec["BR"]
            rec["S"] = float(s.sum())
            rec["SoB"] = float(s.sum() / b.sum())
            if bad:
                rec["status"] = "invalid:" + ",".join(bad)
                rows.append(rec)
                continue
            if s.sum() <= 1e-12:
                rec["status"] = "invalid:zero_signal"
                rows.append(rec)
                continue
            e = R.mu95_coh(b, s, b, sb, w, nmax=1e4)[0]
            o = R.mu95_coh(data, s, b, sb, w, nmax=1e4)[0]
            rec["mu95_exp"] = e
            rec["mu95_obs"] = o
            ZE[i, j], ZO[i, j] = (e if e is not None else np.nan), (o if o is not None else np.nan)
            rec["status"] = "ok"
            rows.append(rec)

    np.savez(os.path.join(HERE, "grid_v2.npz"), MVS=np.array(MVS), gts=GTS, ZE=ZE, ZO=ZO)
    with open(os.path.join(HERE, "grid_v2.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        for r in rows:
            wr.writerow({k: ("" if v is None else v) for k, v in r.items()})

    n_ok = sum(1 for r in rows if r["status"] == "ok")
    print("wrote grid_v2.npz / grid_v2.csv : %d points, %d ok" % (len(rows), n_ok))
    for st in sorted({r["status"] for r in rows}):
        print("   %-28s %d" % (st, sum(1 for r in rows if r["status"] == st)))
    print("\nobserved mu95 < 1 windows:")
    for j, mv in enumerate(MVS):
        col = ZO[:, j]
        ok = np.isfinite(col)
        if not ok.any():
            continue
        segs, cur = [], None
        for i in range(len(GTS)):
            if not ok[i]:
                cur = None
                continue
            qq = col[i] < 1
            if cur is None or qq != cur[0]:
                cur = [qq, [i]]
                segs.append(cur)
            else:
                cur[1].append(i)
        print("  MV=%3d  %s" % (mv, " | ".join(
            ("EXCL" if qq else "allw") + " %.2f-%.2f" % (GTS[i[0]], GTS[i[-1]]) for qq, i in segs)))


if __name__ == "__main__":
    main()

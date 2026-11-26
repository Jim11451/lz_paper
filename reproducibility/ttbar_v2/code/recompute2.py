"""PHASE 3 -- (M_V, g_t) exclusion map with a COHERENT background nuisance.

Only the background model changes with respect to final_plot5.py:

  old : background fixed at its nominal value (fp.mu95, no profiled nuisance)
  new : one nuisance for the signal region, b_i -> b_i(1+theta), theta ~ N(0,w^2),
        w = sum(sigma_i)/sum(b_i) = 3.2%   (PHASE 2.5 "per-SR coherent" model)

Two signal inputs so the two effects can be separated:
  lz  : shapes/efficiency from the LZ+relic samples (sig_lz_MV*.root, per-column m_chi)
  old : shapes/efficiency from the m_chi = 35 samples (what fig_final_MVgt_v3 used)

CLs convention identical to the one validated against pyhf in PHASE 2:
  q_mu = max(0, nll(mu)-nll(mu_hat)) if mu > mu_hat else 0
  q_b  = max(0, nll(0) -nll(mu_hat));  CLs = (1-Phi(sqrt(q_mu)))/Phi(sqrt(q_b))
"""
import json
import math
import os
import sys

import numpy as np
import uproot

sys.path.insert(0, "/home/yy/.hermes/cache/scratch/ttDM")
import final_plot as fp            # noqa: E402
import final_plot5 as f5           # noqa: E402
import sys_likelihood as sl        # noqa: E402
from final_plot2 import widths, GCHI_MAX, GAMMA_MAX   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TTDM = "/home/yy/.hermes/cache/scratch/ttDM"
LUMI = fp.LUMI
SQ2 = math.sqrt(2.0)
MVS = [20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]


def phi(x):
    return 0.5 * math.erfc(-x / SQ2)


def nll_coh(n, s, b0, sbw, mu, th, w):
    t = np.maximum(b0 * (1.0 + th) + mu * s, 1e-9)
    return float(np.sum(-2.0 * (n * np.log(t) - t))) + (th / w) ** 2


def prof_theta(n, s, b0, sb, mu, w):
    grid = np.linspace(-3.0 * w, 3.0 * w, 21)
    vals = np.array([nll_coh(n, s, b0, sb, mu, t, w) for t in grid])
    i = int(np.argmin(vals))
    best, bth = float(vals[i]), float(grid[i])
    if 0 < i < len(grid) - 1:
        d0, d1 = vals[i - 1] - best, vals[i + 1] - best
        den = d0 + d1
        if den > 0:
            step = 0.5 * (d0 - d1) / den * (grid[i + 1] - grid[i - 1])
            cand = min(max(grid[i] + step, grid[i - 1]), grid[i + 1])
            v = nll_coh(n, s, b0, sb, mu, cand, w)
            if v < best:
                best, bth = v, float(cand)
    return best, bth


def mu95_coh(n, s, b0, sb, w, nmax=60.0):
    grid = np.linspace(0.0, 6.0, 25)
    vals = [prof_theta(n, s, b0, sb, m, w)[0] for m in grid]
    i = int(np.argmin(vals))
    muhat, nllhat = float(grid[i]), float(vals[i])
    if 0 < i < len(grid) - 1:
        g2 = np.linspace(grid[i - 1], grid[i + 1], 17)
        v2 = [prof_theta(n, s, b0, sb, m, w)[0] for m in g2]
        j = int(np.argmin(v2))
        muhat, nllhat = float(g2[j]), float(v2[j])
    qb = max(0.0, prof_theta(n, s, b0, sb, 0.0, w)[0] - nllhat)
    pb = phi(math.sqrt(qb))

    def cls(mu):
        f = prof_theta(n, s, b0, sb, mu, w)[0]
        q = max(0.0, f - nllhat) if mu > muhat else 0.0
        return (1.0 - phi(math.sqrt(q))) / max(pb, 1e-12)

    lo, hi = 1e-4, max(0.5, 2 * muhat + 0.5)
    while cls(hi) > 0.05:
        hi *= 2
        if hi > nmax:
            return None, muhat
    for _ in range(26):
        mid = 0.5 * (lo + hi)
        if cls(mid) > 0.05:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), muhat


def measure_lz(mv):
    path = "%s/sig_lz_MV%.1f.root" % (TTDM, float(mv))
    h = fp.shape(path).astype(float)
    ntot = uproot.open(path)["Delphes"].num_entries
    return h / h.sum(), h.sum() / ntot, ntot


def measure_old(mv):
    h = f5.shape_at(mv)
    return h / h.sum(), f5.eps(mv), None


def scan(mode, b, sb, data):
    w = float(sb.sum() / b.sum())
    rows = list(__import__("csv").DictReader(open(TTDM + "/lz_points.csv")))
    mchi_of = {float(r["mv"]): float(r["mchi"]) for r in rows}
    gts = np.logspace(math.log10(0.2), math.log10(4.0), 44)
    ZE = np.full((len(gts), len(MVS)), np.nan)
    ZO = np.full((len(gts), len(MVS)), np.nan)
    info = {}
    for j, mv in enumerate(MVS):
        mchi = mchi_of.get(float(mv))
        if mchi is None or 2 * mchi >= mv:
            print("  MV=%3d skipped (no relic solution / 2m_chi > M_V)" % mv)
            continue
        shape, eff, ntot = (measure_lz(mv) if mode == "lz" else measure_old(mv))
        sig = fp.sigma(mv)
        kk = fp.kappa(mchi) * mv ** 2
        info[mv] = {"mchi": mchi, "eff": float(eff), "sigma_pb": float(sig),
                    "kappa_mv2": float(kk)}
        for i, gt in enumerate(gts):
            gchi = kk / gt
            g, q = widths(mv, gchi, gt, mchi)
            br = g / (g + q) if (g + q) > 0 else 0.0
            if gchi > GCHI_MAX or (g + q) / mv > GAMMA_MAX or mv - 2 * mchi < 5 * (g + q):
                continue
            s = shape * eff * sig * LUMI * gt ** 2 * br
            if s.sum() <= 1e-9:
                continue
            ZE[i, j] = mu95_coh(b, s, b, sb, w)[0] or np.nan
            ZO[i, j] = mu95_coh(data, s, b, sb, w)[0] or np.nan
        print("  MV=%3d mchi=%5.2f eff=%.4f sigma=%.3f gchi(gt=1)=%.2f "
              "mu95exp=%.4f mu95obs=%.4f"
              % (mv, mchi, eff, sig, kk,
                 np.nanmin(ZE[:, j]) if np.isfinite(ZE[:, j]).any() else float("nan"),
                 np.nanmin(ZO[:, j]) if np.isfinite(ZO[:, j]).any() else float("nan")))
    np.savez(os.path.join(HERE, "grid_%s.npz" % mode), MVS=np.array(MVS), gts=gts, ZE=ZE, ZO=ZO)
    return {"w": w, "gts": gts.tolist(), "info": info}


def crossings(Z, gts):
    out = []
    for j, mv in enumerate(MVS):
        col = Z[:, j]
        ok = np.isfinite(col)
        if not ok.any():
            continue
        allowed = np.where(ok & (col > 1))[0]      # mu95 > 1 -> still alive
        excl = np.where(ok & (col < 1))[0]
        if len(allowed) and len(excl) and allowed.max() < excl.min():
            i1, i2 = allowed.max(), excl.min()     # crossing, low g_t side alive
            out.append((mv, 0.5 * (gts[i1] + gts[i2])))
        elif len(allowed) and not len(excl):
            out.append((mv, "alive"))
        elif len(excl) and not len(allowed):
            out.append((mv, "excluded"))
    return out


def main():
    edges, procs, b, sb, data = sl.load()
    print("AH0l2b: B=%.1f sum(sigma)=%.1f coherent width w=%.4f"
          % (b.sum(), sb.sum(), sb.sum() / b.sum()))
    res = {}
    for mode in ("lz", "old"):
        print("\n== signal input: %s" % ("LZ+relic samples" if mode == "lz" else "m_chi=35 samples"))
        res[mode] = scan(mode, b, sb, data)
        json.dump(res, open(os.path.join(HERE, "results_v2.json"), "w"), indent=1)
    print("\ng_t at mu95=1 (observed):")
    for mode in ("lz", "old"):
        Z = np.load(os.path.join(HERE, "grid_%s.npz" % mode))["ZO"]
        gts = np.array(res[mode]["gts"])
        print(" %-4s" % mode, ", ".join(
            "MV%d:%s" % (mv, "none" if g is None else "%.2f" % g) for mv, g in crossings(Z, gts)))


if __name__ == "__main__":
    main()

"""PHASE 9 -- corrected LZ normalisation (g_B = g_N(p) written into the par card).

Same machinery as cmsrepro/phase4/final_map.py, with ONE change: kappa_LZ(m_chi)
comes from relic/kappa_lz_gN.csv (per-column values computed with
g_B = 2 gVu + gVd = 5.291e-5) instead of the 3-point legacy table.

Outputs (kept separate from the phase-4 ones):
  cmsrepro/phase9/grid_gN.npz, templates_gN.json,
  cmsrepro/phase9/fig_exclusion_gN.png   (paper version is redrawn by plot_map_gN.py)
"""
import csv
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt       # noqa: E402
import numpy as np                    # noqa: E402
import uproot                         # noqa: E402

sys.path.insert(0, "/home/yy/.hermes/cache/scratch/ttDM")
sys.path.insert(0, "/home/yy/lz-event/phenomenology/cmsrepro/phase3")
import final_plot as fp               # noqa: E402
import sys_likelihood as sl           # noqa: E402
from final_plot2 import widths, GCHI_MAX, GAMMA_MAX   # noqa: E402
import recompute2 as R                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TTDM = "/home/yy/.hermes/cache/scratch/ttDM"
HS = os.path.join(TTDM, "hs")
KAPPA_CSV = "/home/yy/lz-event/phenomenology/data/relic/kappa_lz_gN.csv"
LUMI = fp.LUMI
SQ4PI = math.sqrt(4 * math.pi)
MVS = [20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]
OUTFIG = os.path.join(HERE, "fig_exclusion_gN.png")

# ---- replace the legacy 3-point table by the corrected per-mass values ----
rows = [r for r in csv.DictReader(open(KAPPA_CSV))]
KAPPA_NEW = {float(r["mchi"]): float(r["kappa"]) for r in rows}
fp.KAPPA = KAPPA_NEW
print("kappa table (%d 点):" % len(KAPPA_NEW))
for m in sorted(KAPPA_NEW):
    print("   m=%7.3f  kappa=%.4e" % (m, KAPPA_NEW[m]))


def measure(mv):
    hi = os.path.join(HS, "sig_hs_MV%d.root" % mv)
    path = hi if os.path.exists(hi) else "%s/sig_lz_MV%.1f.root" % (TTDM, float(mv))
    h = fp.shape(path).astype(float)
    ngen = uproot.open(path)["Delphes"].num_entries
    return h / h.sum(), h.sum() / ngen, ngen, int(h.sum()), os.path.basename(path)


def main():
    edges, procs, b, sb, data = sl.load()
    w = float(sb.sum() / b.sum())
    rows2 = list(csv.DictReader(open(TTDM + "/lz_points.csv")))
    mchi_of = {float(r["mv"]): float(r["mchi"]) for r in rows2}

    gts = np.logspace(math.log10(0.1), math.log10(SQ4PI), 44)
    ZE = np.full((len(gts), len(MVS)), np.nan)
    ZO = np.full((len(gts), len(MVS)), np.nan)
    tab = {}
    print("\nMV   file                ngen  npass   eff      kappa      minE    minO")
    for j, mv in enumerate(MVS):
        mchi = mchi_of.get(float(mv))
        if mchi is None or 2 * mchi >= mv:
            continue
        shape, eff, ngen, npass, base = measure(mv)
        sig = fp.sigma(mv)
        kap = fp.kappa(mchi)
        kk = kap * mv ** 2
        tab[mv] = {"mchi": mchi, "eff": eff, "npass": npass, "ngen": ngen,
                   "file": base, "kappa": kap}
        for i, gt in enumerate(gts):
            gchi = kk / gt
            g, q = widths(mv, gchi, gt, mchi)
            br = g / (g + q) if (g + q) > 0 else 0.0
            if gchi > GCHI_MAX or (g + q) / mv > GAMMA_MAX or mv - 2 * mchi < 5 * (g + q):
                continue
            s = shape * eff * sig * LUMI * gt ** 2 * br
            if s.sum() <= 1e-9:
                continue
            # nmax=1e4: the default bracket (60) returns None for points where the
            # signal is so weak that mu95 > 60; those are ALLOWED points and must not
            # be painted white (which the legend reserves for invalid parameters).
            e = R.mu95_coh(b, s, b, sb, w, nmax=1e4)[0]
            o = R.mu95_coh(data, s, b, sb, w, nmax=1e4)[0]
            ZE[i, j] = e if e is not None else 1e3
            ZO[i, j] = o if o is not None else 1e3
        print("%3d  %-18s %6d %6d  %.4f  %.3e  %7.4f %7.4f"
              % (mv, base, ngen, npass, eff, kap,
                 np.nanmin(ZE[:, j]) if np.isfinite(ZE[:, j]).any() else float("nan"),
                 np.nanmin(ZO[:, j]) if np.isfinite(ZO[:, j]).any() else float("nan")))

    np.savez(os.path.join(HERE, "grid_gN.npz"), MVS=np.array(MVS), gts=gts, ZE=ZE, ZO=ZO)
    json.dump({"w": w, "templates": tab}, open(os.path.join(HERE, "templates_gN.json"), "w"), indent=1)

    X, Y = np.meshgrid(MVS, gts)
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0), dpi=170, sharey=True)
    levels = np.logspace(math.log10(0.01), math.log10(40.0), 41)
    norm = matplotlib.colors.LogNorm(vmin=0.01, vmax=40.0)
    for ax, Z, tag in zip(axes, (ZE, ZO),
                          ("Expected (Asimov, $\\mu=0$)", "Observed (CMS data)")):
        Zm = np.ma.masked_invalid(Z)
        im = ax.contourf(X, Y, Zm, levels=levels, cmap="RdBu", norm=norm, extend="both")
        fin = Z[np.isfinite(Z)]
        if len(fin) and fin.min() < 1 < fin.max():
            cs = ax.contour(X, Y, Zm, levels=[1.0], colors="k", linewidths=2.4)
            ax.clabel(cs, fmt={1.0: r"$\mu_{95}=1$"}, fontsize=9, inline=True)
        ax.axhline(SQ4PI, color="0.1", ls="--", lw=1.4)
        ax.set_yscale("log")
        ax.set_xlabel(r"$M_V$  [GeV]", fontsize=10)
        ax.set_title(r"$t\bar t$ + DM, CMS EXO-22-014 AH 2$b$  —  " + tag, fontsize=9.5)
        ax.set_xlim(18, 205)
        ax.set_ylim(0.1, SQ4PI * 1.12)
        ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.35)
        ax.text(0.985, 0.03,
                "Red: excluded ($\\mu_{95}<1$)\nBlue: allowed ($\\mu_{95}>1$)\nWhite: invalid "
                "($g_\\chi>1.5$ or $\\Gamma_V/M_V>3\\%$)",
                transform=ax.transAxes, fontsize=7.4, ha="right", va="bottom",
                bbox=dict(fc="white", ec="0.7", lw=0.6, alpha=0.9))
    axes[0].set_ylabel(r"$g_t$", fontsize=10)
    cb = fig.colorbar(im, ax=axes, pad=0.015, ticks=[0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30])
    cb.ax.set_yticklabels(["0.01", "0.03", "0.1", "0.3", "1", "3", "10", "30"])
    cb.set_label(r"$\mu_{95}$", fontsize=9)
    fig.savefig(OUTFIG)
    print("\nwrote", OUTFIG)

    print("\nobserved mu95 = 1 windows:")
    for j, mv in enumerate(MVS):
        col = ZO[:, j]
        ok = np.isfinite(col)
        if not ok.any():
            continue
        segs, cur = [], None
        for i in range(len(gts)):
            if not ok[i]:
                cur = None
                continue
            s = col[i] < 1
            if cur is None or s != cur[0]:
                cur = [s, [i]]; segs.append(cur)
            else:
                cur[1].append(i)
        txt = " | ".join(("EXCL" if s else "allw") + " %.2f-%.2f" % (gts[i[0]], gts[i[-1]])
                         for s, i in segs)
        print("  MV=%3d  %s" % (mv, txt))


if __name__ == "__main__":
    main()

"""V10 figures 1, 3 and 4, built from the final grid.

Fig. 1  the solution set in two projections, panels labelled (a) and (b)
Fig. 3  mu95(g_t) for M_V = 20, 30, 40, 50, 100, 200 GeV
Fig. 4  sigma_vis and BR_inv for M_V = 20, 30, 40, 50 GeV
"""
import csv
import json
import os
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D

P = "/home/yy/lz-event/phenomenology"
OUT = P + "/V10_FINAL_MANUSCRIPT/figures"
os.makedirs(OUT, exist_ok=True)
TICK, LABEL, LEG = 9, 10, 8.5
plt.rcParams.update({"font.size": TICK, "axes.labelsize": LABEL, "legend.fontsize": LEG,
                     "xtick.labelsize": TICK, "ytick.labelsize": TICK,
                     "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in"})

rows = list(csv.DictReader(open(P + "/V10_FINAL_MANUSCRIPT/data/GRID_V10.csv")))
MV = np.array([float(r["MV"]) for r in rows])
MCHI = np.array([float(r["mchi"]) for r in rows])
GCHI = np.array([float(r["gchi"]) for r in rows])
GT = np.array([float(r["gt"]) for r in rows])
MU = np.array([float(r["mu95"]) for r in rows])

# ---------------------------------------------------------------- figure 1
fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.9))
fig.subplots_adjust(wspace=0.85)

sc = ax[0].scatter(MV, MCHI, c=GCHI, s=11, cmap="viridis",
                   norm=LogNorm(vmin=GCHI.min(), vmax=GCHI.max()), edgecolor="none")
ax[0].plot([30, 205], [15, 102.5], ":", color="0.35", lw=1.0, label=r"$m_\chi=M_V/2$")
ax[0].set_xlabel(r"$M_V$ [GeV]")
ax[0].set_ylabel(r"$m_\chi$ [GeV]")
ax[0].set_xlim(14, 210)
ax[0].set_ylim(4, 55)
ax[0].legend(loc="lower right", fontsize=7.5)
cb0 = fig.colorbar(sc, ax=ax[0], pad=0.035, fraction=0.045)
cb0.set_label(r"$g_\chi$", fontsize=8.5)
cb0.ax.tick_params(labelsize=7.5)

sc1 = ax[1].scatter(MCHI, GCHI, c=MV, s=11, cmap="viridis", edgecolor="none")
ax[1].set_yscale("log")
ax[1].set_xlabel(r"$m_\chi$ [GeV]")
ax[1].set_ylabel(r"$g_\chi$")
cb1 = fig.colorbar(sc1, ax=ax[1], pad=0.035, fraction=0.045)
cb1.set_label(r"$M_V$ [GeV]", fontsize=8.5)
cb1.ax.tick_params(labelsize=7.5)

ax[0].text(0.02, 0.97, "(a)", transform=ax[0].transAxes, fontsize=10, va="top")
ax[1].text(0.02, 0.97, "(b)", transform=ax[1].transAxes, fontsize=10, va="top")
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, "fig1_v10." + ext), bbox_inches="tight", dpi=300)
print("fig1 | points", len(MV))

# ---------------------------------------------------------------- figure 3
fig, ax = plt.subplots(figsize=(5.6, 3.7))
palette = {20: "#440154", 30: "#414487", 40: "#2a788e", 50: "#22a884", 100: "#e07b00", 200: "#8c2d04"}
marks = {20: "o", 30: "s", 40: "^", 50: "d", 100: "v", 200: "P"}
for mv in (20, 30, 40, 50, 100, 200):
    sel = np.isclose(MV, mv)
    o = np.argsort(GT[sel])
    ax.plot(GT[sel][o], MU[sel][o], marker=marks[mv], ms=3.4, lw=1.2,
            color=palette[mv], label=r"$M_V=%d$ GeV" % mv)


ax.axhline(1.0, color="k", ls="--", lw=1.0, zorder=1)
cap = np.isclose(MU, 64.0)
ax.plot(GT[cap], MU[cap], "o", ms=7, mfc="none", mec="k", mew=0.9, zorder=5)
ax.annotate("scan cap", xy=(GT[cap][0] if cap.any() else 3.0, 64.0), xytext=(1.15, 34),
            fontsize=8, arrowprops=dict(arrowstyle="-", lw=0.7, color="0.3"))
ax.text(0.105, 0.85, r"$\mu_{95}=1$", fontsize=8.5, ha="left", va="top")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$g_t$")
ax.set_ylabel(r"$\mu_{95}$ (expected)")
ax.set_xlim(0.09, 4.0)
ax.set_ylim(8e-4, 80)
ax.grid(axis="y", color="0.92", lw=0.6)
ax.legend(loc="lower left", ncol=2, framealpha=0.95, columnspacing=0.9, handlelength=1.6)
fig.tight_layout(pad=0.4)
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, "fig3_v10." + ext), bbox_inches="tight", dpi=300)
print("fig3 | curves 6 | mu range %.5f-%.3f" % (MU.min(), MU.max()))

# ---------------------------------------------------------------- figure 4
def sigma_of(pid):
    for sub in ("samples_v7", "samples_fill", "samples_regen", "samples"):
        p = "%s/V7_EXTENSION/%s/p_%s/result.json" % (P, sub, pid)
        if os.path.exists(p):
            d = json.load(open(p))
            if d.get("status") == "OK":
                return d["sigma_mg5"]
    p = "%s/V3_STEP61B/points/p_%s.json" % (P, pid)
    return json.load(open(p))["sigma_mg5"]


fig, axes = plt.subplots(2, 2, figsize=(7.6, 5.4), sharex=True)
fig.subplots_adjust(hspace=0.42, wspace=0.62, top=0.86)
meta = {}
for ax, mv in zip(axes.flat, (20, 30, 40, 50)):
    sel = [r for r in rows if float(r["MV"]) == mv]
    sel.sort(key=lambda r: float(r["gt"]))
    g = np.array([float(r["gt"]) for r in sel])
    br = np.array([float(r["BR_inv"]) for r in sel])
    mu = np.array([float(r["mu95"]) for r in sel])
    sg = np.array([sigma_of(r["point_id"]) for r in sel])
    ax.plot(g, sg, "o-", ms=2.6, lw=1.1, color="#08519c")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_ylabel(r"$\sigma_{\rm vis}$ [pb]", color="#08519c", fontsize=9)
    ax.tick_params(axis="y", colors="#08519c", labelsize=8)
    ax2 = ax.twinx()
    ax2.plot(g, br, "s--", ms=2.2, lw=1.0, color="#b2182b")
    ax2.set_yscale("log")
    ax2.set_ylim(1e-5, 2)
    ax2.set_ylabel(r"$\mathrm{BR}_{\rm inv}$", color="#b2182b", fontsize=9)
    ax2.tick_params(axis="y", colors="#b2182b", labelsize=8)
    s = mu - 1.0
    for i in range(len(s) - 1):
        if s[i] * s[i + 1] < 0:
            xc = np.exp(np.log(g[i]) + (s[i] / (s[i] - s[i + 1])) * (np.log(g[i + 1]) - np.log(g[i])))
            ax.axvline(xc, color="k", lw=0.9, ls=":")
    ax.set_title(r"$M_V=%d$ GeV" % mv, fontsize=9.5, pad=3)
    ax.tick_params(labelsize=8)
for ax in axes[1]:
    ax.set_xlabel(r"$g_t$")
handles = [Line2D([], [], color="#08519c", marker="o", ms=3.2, lw=1.1, label=r"$\sigma_{\rm vis}$ (MG5, BR included)"),
           Line2D([], [], color="#b2182b", ls="--", marker="s", ms=2.6, lw=1.0, label=r"$\mathrm{BR}_{\rm inv}$"),
           Line2D([], [], color="k", ls=":", lw=0.9, label=r"nominal $\mu_{95}=1$ crossing")]
fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.03), fontsize=8.5)
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, "fig4_v10." + ext), bbox_inches="tight", dpi=300)
print("fig4 | panels 4")

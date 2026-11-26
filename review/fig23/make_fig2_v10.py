"""Extended expected exclusion map: 244 old points + new points at M_V = 20-40 GeV.

Cell rendering as in the Stage-2 figure: each coloured rectangle is one computed
point, no interpolation between cells; the black curve is the mu95 = 1 level set
of an interpolation of log10(mu95) between neighbouring points.
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/home/yy/lz-event/phenomenology/V6_REVISION_STAGE2/code")
import style
style.apply()
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch

P = "/home/yy/lz-event/phenomenology"
OUT = os.path.join(P, "V10_FINAL_MANUSCRIPT/figures")
os.makedirs(OUT, exist_ok=True)

rows = list(csv.DictReader(open(os.path.join(P, "V10_FINAL_MANUSCRIPT/data/GRID_V10.csv"))))
pts = sorted((float(r["MV"]), float(r["gt"]), float(r["mu95"]), r["source"]) for r in rows)

cols = {}
for mv, gt, mu, src in pts:
    cols.setdefault(mv, []).append((gt, mu))
mvs = sorted(cols)
col_edges = [mvs[0] - 5] + [(mvs[i] + mvs[i + 1]) / 2 for i in range(len(mvs) - 1)] + [mvs[-1] + 10]

mu_all = np.array([p[2] for p in pts])
norm = TwoSlopeNorm(vmin=np.log10(mu_all.min()), vcenter=0.0, vmax=np.log10(mu_all.max()))
cmap = plt.get_cmap("RdBu")

fig, ax = plt.subplots(figsize=(7.6, 4.3))
ax.set_facecolor("#ebebeb")

for j, mv in enumerate(mvs):
    data = sorted(cols[mv])
    g = np.array([d[0] for d in data])
    m = np.array([d[1] for d in data])
    lg = np.log(g)
    be = np.concatenate([[lg[0]], 0.5 * (lg[1:] + lg[:-1]), [lg[-1]]]) if len(g) > 1 \
        else np.array([lg[0] * 0.98, lg[0] * 1.02])
    ye = np.exp(be)
    for i in range(len(g)):
        ax.pcolormesh([col_edges[j], col_edges[j + 1]], [ye[i], ye[i + 1]],
                      np.log10([[m[i]]]), cmap=cmap, norm=norm, shading="flat",
                      rasterized=True, edgecolor="none", linewidth=0, antialiased=False)

# Cells pinned at the numerical cap (mu95 = 64) are censored, not measured.
# They are marked with an open symbol here, as in Fig. 3, because they set the
# darkest part of the 20 GeV strip.
CAP = 64.0
for j, mv in enumerate(mvs):
    data = sorted(cols[mv])
    g = np.array([d[0] for d in data]); m = np.array([d[1] for d in data])
    if len(g) < 2:
        continue
    lg = np.log(g)
    be = np.concatenate([[lg[0]], 0.5 * (lg[1:] + lg[:-1]), [lg[-1]]])
    yc = np.exp(0.5 * (be[1:] + be[:-1]))
    sel = np.isclose(m, CAP)
    if sel.any():
        ax.plot(np.full(int(sel.sum()), 0.5 * (col_edges[j] + col_edges[j + 1])), yc[sel],
                marker="o", ms=3.4, mfc="none", mec="white", mew=0.9, ls="none", zorder=6)

# mu95 = 1 boundary: crossings computed per column, then joined across columns.
# The 20 GeV pair is nominal only (mu95 = 0.94-1.00 with sigma_MC = 0.10-0.16);
# it is not drawn so that the figure does not present it as a resolved island.
SUPPRESS = {20.0}
xc = np.array([0.5 * (col_edges[j] + col_edges[j + 1]) for j in range(len(mvs))])
lo_pts, hi_pts = [], []
for j, mv in enumerate(mvs):
    data = sorted(cols[mv])
    g = np.array([d[0] for d in data])
    m = np.array([d[1] for d in data])
    s = m - 1.0
    cross = []
    for i in range(len(s) - 1):
        if s[i] * s[i + 1] < 0:
            tt = s[i] / (s[i] - s[i + 1])
            cross.append(float(np.exp(np.log(g[i]) + tt * (np.log(g[i + 1]) - np.log(g[i])))))
    if mv in SUPPRESS:
        cross = []
    if cross:
        lo_pts.append((xc[j], min(cross)))
        hi_pts.append((xc[j], max(cross)) if len(cross) > 1 else (xc[j], np.nan))
    else:
        lo_pts.append((xc[j], np.nan))
        hi_pts.append((xc[j], np.nan))

def draw(pts):
    """Join crossings of adjacent columns only when they agree to within a
    factor 1.5; a larger jump means the boundary is not resolved between the
    two columns and the line is interrupted there."""
    seg = []
    for k, p in enumerate(pts):
        if not np.isfinite(p[1]):
            if len(seg) > 1:
                ax.plot([q[0] for q in seg], [q[1] for q in seg], "k-", lw=1.6, zorder=6)
            seg = []
            continue
        if seg and abs(np.log(p[1] / seg[-1][1])) > np.log(1.5):
            if len(seg) > 1:
                ax.plot([q[0] for q in seg], [q[1] for q in seg], "k-", lw=1.6, zorder=6)
            seg = []
        seg.append(p)
    if len(seg) > 1:
        ax.plot([q[0] for q in seg], [q[1] for q in seg], "k-", lw=1.6, zorder=6)

draw(lo_pts)
draw(hi_pts)

ax.set_yscale("log")
ax.set_xlim(14, 208)
ax.set_ylim(0.09, 3.9)
ax.set_yticks([0.1, 0.2, 0.4, 0.7, 1, 2, np.sqrt(4 * np.pi)])
ax.set_yticklabels(["0.1", "0.2", "0.4", "0.7", "1", "2", r"$\sqrt{4\pi}$"])
ax.set_xlabel(r"$M_V$ [GeV]", fontsize=11)
ax.set_ylabel(r"$g_t$", fontsize=11)
ax.tick_params(labelsize=9.5)

sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
ticks = [0.003, 0.01, 0.03, 0.1, 0.3, 1, 3]
ticks = [t for t in ticks if mu_all.min() <= t <= mu_all.max()]
cb = fig.colorbar(sm, ax=ax, pad=0.015, ticks=[np.log10(t) for t in ticks], extend="both")
cb.ax.set_yticklabels(["%g" % t for t in ticks])
cb.set_label(r"$\mu_{95}$", fontsize=10)

cb.ax.tick_params(labelsize=9)

handles = [Patch(fc=cmap(norm(np.log10(0.1))), ec="none", label=r"excluded ($\mu_{95}<1$)"),
           Patch(fc=cmap(norm(np.log10(3.0))), ec="none", label=r"not excluded ($\mu_{95}>1$)"),
           Patch(fc="#ebebeb", ec="0.75", label="no admissible solution"),
           plt.Line2D([], [], color="k", lw=1.5, label=r"$\mu_{95}=1$"),
           plt.Line2D([], [], marker="o", ms=3.6, mfc="none", mec="0.35", mew=0.9,
                      ls="none", label=r"pinned at cap ($\mu_{95}=64$)")]
ax.legend(handles=handles, loc="lower right", framealpha=0.96, fontsize=8.5, handlelength=1.4)

fig.tight_layout(pad=0.4)
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, "fig2_v10." + ext), bbox_inches="tight", dpi=300)
print("wrote fig2_v10.pdf | columns %d | points %d | mu range %.5f-%.4f"
      % (len(mvs), len(pts), mu_all.min(), mu_all.max()))

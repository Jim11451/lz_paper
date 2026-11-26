"""Step 5.4 -- figures and old/new comparison for the v2 grid."""
import csv
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/yy/lz-event/phenomenology"
sys.path.insert(0, os.path.join(ROOT, "cmsrepro/phase3"))
import recompute2 as R                   # noqa: E402
import sys_likelihood as sl              # noqa: E402

d = np.load(os.path.join(HERE, "grid_v2.npz"))
MVS, gts, ZE, ZO = d["MVS"], d["gts"], d["ZE"], d["ZO"]
old = np.load(os.path.join(ROOT, "cmsrepro/phase9/grid_gN.npz"))
OZE, OZO = old["ZE"], old["ZO"]

rows = list(csv.DictReader(open(os.path.join(HERE, "grid_v2.csv"))))


def windows(col, gt):
    segs, cur = [], None
    for i in range(len(gt)):
        if not np.isfinite(col[i]):
            cur = None
            continue
        q = col[i] < 1
        if cur is None or q != cur[0]:
            cur = [q, [i]]
            segs.append(cur)
        else:
            cur[1].append(i)
    return " | ".join(("EXCL" if q else "allw") + " %.2f-%.2f" % (gt[s[0]], gt[s[-1]]) for q, s in segs)


# ---- comparison table ------------------------------------------------------
lines = ["| $M_V$ | 旧（PHASE 14）观测窗口 | 新（v2 κ）观测窗口 | 变化 |", "|---|---|---|---|"]
for j, mv in enumerate(MVS):
    o = windows(OZO[:, j], gts)
    n = windows(ZO[:, j], gts)
    lines.append("| %d | %s | %s | %s |" % (mv, o or "—", n or "—", "改变" if o != n else "相同"))
open(os.path.join(HERE, "compare_old_new.md"), "w").write("\n".join(lines) + "\n")

# ---- statistics ------------------------------------------------------------
def counts(col):
    fin = np.isfinite(col)
    return int((fin & (col < 1)).sum()), int((fin & (col >= 1)).sum()), int((~fin).sum())


print("new (v2):  excluded/allowed/invalid = %d/%d/%d" % counts(ZO))
print("old (P14): excluded/allowed/invalid = %d/%d/%d" % counts(OZO))
st = {}
for r in rows:
    st[r["status"]] = st.get(r["status"], 0) + 1
for k, v in sorted(st.items()):
    print("   %-30s %d" % (k, v))

# ---- figure 1: nominal exclusion map --------------------------------------
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

lxe = np.sqrt(np.asarray(MVS[:-1], float) * np.asarray(MVS[1:], float))
xe = np.concatenate([[MVS[0] ** 2 / lxe[0]], lxe, [MVS[-1] ** 2 / lxe[-1]]])
lye = np.sqrt(gts[:-1] * gts[1:])
ye = np.concatenate([[gts[0] ** 2 / lye[0]], lye, [gts[-1] ** 2 / lye[-1]]])

M = np.zeros((len(gts), len(MVS)))
for i in range(len(gts)):
    for j, mv in enumerate(MVS):
        z = ZO[i, j]
        M[i, j] = 0 if not np.isfinite(z) else (2 if z < 1 else 1)

cmap = ListedColormap(["#ffffff", "#123f8c", "#8b0000"])
norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3)
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.pcolormesh(xe, ye, M, cmap=cmap, norm=norm, shading="flat", edgecolors="0.85", linewidth=0.15)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(xe[0], xe[-1])
ax.set_ylim(ye[0], ye[-1])
ax.set_xlabel(r"$M_V$ [GeV]")
ax.set_ylabel(r"$g_t$")
ax.set_title(r"$t\bar t$+MET exclusion (observed $\mu_{95}<1$), v2 $\kappa$")
ax.legend(handles=[Patch(color="#8b0000", label="excluded"),
                   Patch(color="#123f8c", label="allowed"),
                   Patch(facecolor="white", edgecolor="0.6", label="invalid / out of scan")],
          loc="upper left", fontsize=8, frameon=True)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig_exclusion_v2.png"), dpi=200)
plt.close(fig)

# ---- figure 2: +-2% efficiency, three classification maps -----------------
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), sharey=True)
for ax, R_, ttl in zip(axes, (0.98, 1.0, 1.02),
                       (r"$\varepsilon-2\%$", "nominal", r"$\varepsilon+2\%$")):
    M = np.zeros((len(gts), len(MVS)))
    for i in range(len(gts)):
        for j in range(len(MVS)):
            z = ZO[i, j] / R_
            M[i, j] = 0 if not np.isfinite(z) else (2 if z < 1 else 1)
    ax.pcolormesh(xe, ye, M, cmap=cmap, norm=norm, shading="flat", edgecolors="0.9", linewidth=0.1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(xe[0], xe[-1])
    ax.set_ylim(ye[0], ye[-1])
    ax.set_title(ttl)
    ax.set_xlabel(r"$M_V$ [GeV]")
axes[0].set_ylabel(r"$g_t$")
fig.suptitle(r"observed exclusion for $\pm2\%$ efficiency ($\mu_{95}\to\mu_{95}/R$)", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig_boundary_eff.png"), dpi=180)
plt.close(fig)

# ---- numerical check of the scaling relation ------------------------------
edges, procs, b, sb, data = sl.load()
w = float(sb.sum() / b.sum())
sh = np.load(os.path.join(HERE, "shapes_v2.npz"))
shape, eff, smvs = sh["shape"], sh["eff"], sh["MVS"]
sig = {float(r["MV"]): float(r["xsec_pb"]) for r in csv.DictReader(open(os.path.join(ROOT, "data/lz/sigma_MV.csv")))}
LUMI = 138.0
worst = 0.0
checked = 0
for mv in (60, 100, 160):
    j = smvs.tolist().index(mv)
    for r in rows:
        if r["status"] != "ok" or float(r["MV"]) != mv:
            continue
        gt = float(r["gt"])
        if not any(abs(gt-t)<0.02 for t in (0.5,1.0,3.0)):
            continue
        s = shape[j] * eff[j] * sig[float(mv)] * LUMI * gt ** 2 * float(r["BR"])
        a = R.mu95_coh(data, s, b, sb, w)[0]
        b98 = R.mu95_coh(data, 0.98 * s, b, sb, w)[0]
        if a is None or b98 is None:
            print("  MV=%3d gt=%.2f  skipped (no convergence)" % (mv, gt))
            continue
        rel = abs(b98 - a / 0.98) / a
        worst = max(worst, rel)
        checked += 1
        print("  MV=%3d gt=%.2f  mu95=%.5f  mu95(0.98s)=%.5f  mu95/0.98=%.5f  rel=%.1e"
              % (mv, gt, a, b98, a / 0.98, rel))
print("max relative deviation from mu95(R)=mu95(1)/R : %.1e (%d points)" % (worst, checked))
print("wrote fig_exclusion_v2.png, fig_boundary_eff.png, compare_old_new.md")


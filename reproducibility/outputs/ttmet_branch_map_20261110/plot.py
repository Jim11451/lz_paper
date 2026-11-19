"""Plot the inferred thermal solution branches in the AH 2b coordinates."""

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter
from PIL import Image


folder = Path(__file__).resolve().parent
with (folder / 'branches.csv').open(newline='', encoding='utf-8') as file:
    rows = list(csv.DictReader(file))
mvs = np.unique([float(row['mv_GeV']) for row in rows])
gts = np.unique([float(row['gt']) for row in rows])
assert len(mvs) == 41 and len(gts) == 27 and len(rows) == 1107
classes = np.full((len(gts), len(mvs)), 4)
for row in rows:
    i = np.searchsorted(mvs, float(row['mv_GeV']))
    j = np.searchsorted(gts, float(row['gt']))
    on = bool(int(row['on_count']))
    off = bool(int(row['off_count']))
    classes[j, i] = (2 * on + off) if on or off or not int(row['n_failed']) else 4

colors = ['#edf0f2', '#d87939', '#4688bc', '#8465a7', '#929799']
labels = ['No solution found', 'Off-shell only', 'On-shell only', 'Both solutions', 'Solver failure']
mv_edges = np.r_[mvs[0], (mvs[:-1] + mvs[1:]) / 2, mvs[-1]]
gt_edges = np.r_[gts[0], np.sqrt(gts[:-1] * gts[1:]), gts[-1]]
fig, ax = plt.subplots(figsize=(8.4, 5.7), layout='constrained')
ax.pcolormesh(mv_edges, gt_edges, classes, cmap=ListedColormap(colors),
              norm=BoundaryNorm(np.arange(6) - 0.5, len(colors)), shading='flat')
ax.set(xlim=(20, 100), ylim=(.2, 4), yscale='log',
       xlabel=r'$M_V$ [GeV]', ylabel=r'$g_t$',
       title=r'Mediator virtuality on the LZ + Planck solution set')
ax.set_xticks(np.arange(20, 101, 10))
ax.yaxis.set_major_locator(FixedLocator([.2, .5, 1, 2, 4]))
ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
ax.yaxis.set_minor_formatter(NullFormatter())
ax.axhline(math.sqrt(4 * math.pi), color='#303030', ls=':', lw=1)
ax.text(99, math.sqrt(4 * math.pi) / 1.02, r'$g_t=\sqrt{4\pi}$',
        ha='right', va='top', fontsize=9, bbox={'fc': 'white', 'ec': 'none', 'alpha': .88, 'pad': 1.7})
legend = [Patch(facecolor=color, label=label) for i, (color, label) in enumerate(zip(colors, labels))
          if np.any(classes == i)]
if len(sys.argv) == 2:
    image = np.asarray(Image.open(sys.argv[1]).convert('RGB'))
    assert image.shape == (784, 1888, 3)
    # Pixel coordinates of the observed panel's axes in the supplied JPEG.
    x0, x1, y0, y1 = 901, 1457, 94, 698
    for first_mv, last_mv, ylo, yhi in [(24, 52, 100, 540), (24, 94, 590, 660)]:
        x_values, gt_values = [], []
        for mass in range(first_mv, last_mv + 1, 2):
            x = round(x0 + (x1 - x0) * (mass - 20) / 80)
            black = np.flatnonzero(image[ylo:yhi, x].max(axis=1) < 55)
            groups = np.split(black, np.flatnonzero(np.diff(black) > 1) + 1)
            line = max(groups, key=len)
            if len(line) < 3:
                continue  # The contour label covers the line at some sampled columns.
            y = ylo + line.mean()
            x_values.append(mass)
            gt_values.append(4 * (.2 / 4) ** ((y - y0) / (y1 - y0)))
        contour, = ax.plot(x_values, gt_values, '--', color='#222222', linewidth=1.35,
                           label=r'AH 2b observed $\mu_{95}=1$ (from JPEG)')
    legend.append(contour)

for mass, coupling, marker in [(30, 0.4, 'o'), (48, 0.4, 's'), (60, 2, '^')]:
    ax.scatter(mass, gts[np.argmin(abs(gts - coupling))], marker=marker, facecolor='white',
               edgecolor='#222222', linewidth=1.1, s=32, zorder=4)

fig.legend(handles=legend, loc='outside lower center', ncol=3, frameon=False, fontsize=10)
fig.savefig(folder / 'ttmet_lz_planck_branches.png', dpi=215)

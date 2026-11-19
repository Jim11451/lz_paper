"""Compare cumulative truth-level MET rates at matching parameter points."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


folder = Path(__file__).resolve().parent


def read(path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file))


single_top = read(folder / 'single_top_pilot.csv')
previous_tt = read(folder.parent / 'pseudoDirac_yukawaLZ_xsec_20261020/results/ttmet_cross_sections.csv')
off_shell = read(folder.parent / 'ttmet_branch_map_20261110/off_shell_xsec/cross_sections.csv')
new_tt = read(folder / 'ttbar_M48.csv')
tt = {row['benchmark']: row for row in off_shell + new_tt}
tt['ON_M87'] = next(row for row in previous_tt if row['benchmark'] == 'LZ_M87_gc0p3'
                    and float(row['sqrt_s_TeV']) == 13.)

thresholds = [100, 150, 200, 250, 300, 400, 500]
styles = {'tj': (r'$tj$ (light spectator)', '#2b6cb0', 'o'),
          'tW': (r'$tW$', '#ce6e21', 's'), 'tt': (r'$t\bar t$', '#343a40', '^')}
fig = plt.figure(figsize=(8.6, 6.5), layout='constrained')
grid = fig.add_gridspec(3, 2, height_ratios=[1, 1, .12])
axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(2)]
for ax, benchmark in zip(axes, ['ON_M87', 'ON_M48', 'OFF_M60', 'OFF_M30']):
    rows = {r['channel']: r for r in single_top if r['benchmark'] == benchmark}
    rows['tt'] = tt[benchmark]
    for channel, (name, color, marker) in styles.items():
        values = [float(rows[channel][f'sigma_MET{cut}_fb']) for cut in thresholds]
        ax.plot(thresholds, [v if v > 0 else float('nan') for v in values], label=name,
                color=color, marker=marker, markersize=3.5)
    side, mass = benchmark.split('_M')
    ax.set_title(rf'$M_V\simeq {mass}$ GeV, {side.lower()}-shell', fontsize=11)
    ax.axvline(250, color='#858b90', ls=':', lw=1)
    ax.set_yscale('log')
    ax.grid(axis='y', which='major', alpha=.22)
for ax in axes[2:]:
    ax.set_xlabel(r'Threshold on truth $p_T^{\chi\chi}$ [GeV]')

fig.suptitle('Top-associated dark-pair production at 13 TeV', fontsize=15)
fig.supylabel('Cross section above threshold [fb]')
handles, labels = axes[0].get_legend_handles_labels()
legend_axis = fig.add_subplot(grid[2, :])
legend_axis.set_axis_off()
legend_axis.legend(handles, labels, loc='center', ncol=3, frameon=False)
fig.savefig(folder / 'single_top_truth_met.png', dpi=205)

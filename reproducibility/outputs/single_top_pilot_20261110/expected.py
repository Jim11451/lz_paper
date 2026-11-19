"""Approximate expected CLs for the CMS AH 1b 1FJ channel and the LZ+Planck grid."""

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter


FOLDER = Path(__file__).resolve().parent
LUMI = 138.
HADRONIC_W = .674
BTAG = .70
GT_MAX = math.sqrt(4*math.pi)
MODES = ['full', '1500', '1000', '750']
source = json.loads((FOLDER/'hepdata_AH1b1FJ.json').read_text())
background_group = next(q['group'] for q in source['qualifiers']['Process'] if q['value'] == '$Background$')
background = [next(y for y in row['y'] if y['group'] == background_group) for row in source['values']]
b = np.array([float(row['value']) for row in background])
db = np.array([float(row['errors'][0]['symerror']) for row in background])
assert [int(row['x'][0]['low']) for row in source['values']] == list(range(250, 531, 20))


def mu95(signal, sigma=db):
    if not np.any(signal):
        return math.inf
    variance = sigma**2

    def qmu(mu):
        signal_mu = mu*signal
        linear = signal_mu+b-variance
        total = np.maximum(signal_mu, (linear + np.hypot(linear, 2*np.sqrt(b*variance)))/2)
        shift = total-b
        stat = 2*np.sum(shift-b*np.log1p(shift/b))
        nonzero = variance > 0
        syst = np.sum((total[nonzero]-signal_mu[nonzero]-b[nonzero])**2/variance[nonzero])
        return stat+syst

    lo, hi = 0., 1.
    while qmu(hi) < 1.95996398454**2:
        hi *= 2
    for _ in range(42):
        mid = (lo+hi)/2
        if qmu(mid) < 1.95996398454**2:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def nwa_factor(mv, mchi, gt, gc):
    q_width = 0.
    for m in (.0022, .0047, .096, 1.27, 4.18, 172.):
        if mv > 2*m:
            r = (m/mv)**2
            q_width += (gt*m/172)**2*mv/(4*math.pi)*(1+2*r)*math.sqrt(1-4*r)
    m2 = mchi+.001
    r1, r2 = (mchi/mv)**2, (m2/mv)**2
    gap = mv-mchi-m2
    phase = math.sqrt(max(0., (1-((mchi+m2)/mv)**2)*(1-(.001/mv)**2)))
    spin = 1-(r1+r2)/2-(r1-r2)**2/2+3*math.sqrt(r1*r2)
    inv_width = (gc/2)**2*mv/(12*math.pi)*phase*spin
    width = inv_width+q_width
    return gt**2*inv_width/width, width, gap


def yield_for(template, mode):
    return LUMI*HADRONIC_W*BTAG*np.array(template['fiducial_'+mode])


def write_csv(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


templates = [json.loads(line) for line in (FOLDER/'tj_expected_templates.jsonl').read_text().splitlines()]
benchmarks = []
for template in sorted(templates, key=lambda r: float(r['mv_GeV'])):
    row = {key: template[key] for key in ('benchmark','mv_GeV','mchi_GeV','gt','gchi')}
    for mode in MODES:
        signal = yield_for(template, mode)
        row['yield_'+mode] = signal.sum()
        row['mu95_'+mode] = mu95(signal)
        row['mu95_stat_'+mode] = mu95(signal, np.zeros_like(db))
    row['mu95_forward_only'] = mu95(LUMI*np.array(template['forward_full']))
    benchmarks.append(row)
write_csv(FOLDER/'expected_benchmarks.csv', benchmarks)

anchors = sorted((r for r in templates if r['benchmark'].startswith('ON')), key=lambda r: float(r['mv_GeV']))
assert len(anchors) == 5
masses = np.array([float(t['mv_GeV']) for t in anchors])
unit_yields = {}
for mode in MODES:
    unit_yields[mode] = np.array([yield_for(t, mode)/nwa_factor(*[float(t[k]) for k in
                               ('mv_GeV','mchi_GeV','gt','gchi')])[0] for t in anchors])

with (FOLDER.parent/'ttmet_branch_map_20261110/branches.csv').open(newline='') as file:
    grid = list(csv.DictReader(file))
mv_values = np.unique([float(r['mv_GeV']) for r in grid])
gt_values = np.unique([float(r['gt']) for r in grid if float(r['gt']) <= GT_MAX])
unit_limits = {}
for mode in MODES:
    for mv in mv_values[mv_values >= masses[0]]:
        signal = np.array([np.interp(mv, masses, ys) for ys in unit_yields[mode].T])
        unit_limits[mv, mode] = mu95(signal)
results = []
for point in grid:
    mv, gt = float(point['mv_GeV']), float(point['gt'])
    if gt > GT_MAX or int(point['on_count']) == 0:
        continue
    mchi, gchi = float(point['on_mchi_GeV']), float(point['on_gchi'])
    factor, width, gap = nwa_factor(mv, mchi, gt, gchi)
    if gap <= 5*width or width/mv >= .03:
        continue
    row = dict(mv_GeV=mv, gt=gt, mchi_GeV=mchi, gchi=gchi, off_also_exists=int(point['off_count'])>0)
    for mode in MODES:
        row['mu95_'+mode] = unit_limits[mv, mode]/factor
    results.append(row)
write_csv(FOLDER/'expected_on_shell_grid.csv', results)

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.9), layout='constrained', sharey=True)
fig.suptitle(r'$tj+\mathrm{MET}$, CMS AH 1b 1FJ expected sensitivity pilot', fontsize=14)
norm = LogNorm(.003, 300)
cmap = plt.get_cmap('RdYlBu').with_extremes(bad='#eceff2')
mv_edges = np.r_[mv_values[0], (mv_values[1:]+mv_values[:-1])/2, mv_values[-1]]
gt_edges = np.r_[gt_values[0], np.sqrt(gt_values[1:]*gt_values[:-1]), GT_MAX]
for ax, mode, title in zip(axes, ['full','1000'], ['Full partonic energy', r'$\sqrt{\hat s}<1$ TeV diagnostic']):
    values = np.full((len(gt_values), len(mv_values)), np.nan)
    for r in results:
        values[np.searchsorted(gt_values, r['gt']), np.searchsorted(mv_values, r['mv_GeV'])] = r['mu95_'+mode]
    plot = ax.pcolormesh(mv_edges, gt_edges, np.ma.masked_invalid(values), cmap=cmap, norm=norm, shading='flat')
    if np.nanmin(values) < 1 < np.nanmax(values):
        ax.contour(mv_values, gt_values, values, levels=[1], colors='#222222', linewidths=1.25)
    if np.nanmin(values) < .5 < np.nanmax(values):
        ax.contour(mv_values, gt_values, values, levels=[.5], colors='#222222', linewidths=1.05,
                   linestyles='--')
    on = [row for row in benchmarks if row['benchmark'].startswith('ON')]
    off = [row for row in benchmarks if row['benchmark'].startswith('OFF')]
    ax.scatter([float(r['mv_GeV']) for r in on], [float(r['gt']) for r in on], s=27,
               facecolor='white', edgecolor='#202020', marker='o', zorder=4, clip_on=False, label='On-shell MC')
    ax.scatter([float(r['mv_GeV']) for r in off], [float(r['gt']) for r in off], s=29,
               c=[r['mu95_'+mode] for r in off], cmap=cmap, norm=norm, edgecolor='#202020', marker='D',
               zorder=4, label='Off-shell MC')
    ax.set(xlim=(20,100), ylim=(.2,GT_MAX), yscale='log', xlabel=r'$M_V$ [GeV]', title=title)
    ax.yaxis.set_major_locator(FixedLocator([.2,.3,.5,1,2,3]))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.yaxis.set_minor_formatter(NullFormatter())
axes[0].set_ylabel(r'$g_t$')
axes[0].legend(loc='upper left', framealpha=.96, fontsize=8)
axes[1].legend(handles=[Line2D([], [], color='#222222', lw=1.25, label=r'$\mu_{95}=1$'),
                        Line2D([], [], color='#222222', lw=1.05, ls='--', label=r'$\mu_{95}=1$ at half signal efficiency')],
               loc='upper left', framealpha=.96, fontsize=8)
fig.colorbar(plot, ax=axes, label=r'Median expected $\mu_{95}$', extend='both', pad=.025,
             ticks=[.003, .01, .1, 1, 10, 100, 300])
fig.savefig(FOLDER/'single_top_expected_pilot.png', dpi=205)

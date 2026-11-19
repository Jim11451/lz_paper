"""Transfer the archived ttbar expected likelihood to the new on-shell roots."""

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'work/lz_analysis_deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def invisible_width(mv, mass, coupling):
    a, b = (mass/mv)**2, ((mass+.001)/mv)**2
    phase = math.sqrt(max(0., (1-((2*mass+.001)/mv)**2)*(1-(.001/mv)**2)))
    spin = 1-(a+b)/2-(a-b)**2/2+3*math.sqrt(a*b)
    return (coupling/2)**2*mv*phase*spin/(12*math.pi)


def visible_width(mv, coupling):
    return coupling**2*mv/(12*math.pi)*sum(
        3*(mass/172)**2*(1+2*(mass/mv)**2)*math.sqrt(1-4*(mass/mv)**2)
        for mass in (.0022, .0047, .096, 1.27, 4.18))


grid = np.load(ROOT / 'lz-phenomenology-paper/ttbar/data/grid_gN.npz')
templates = json.loads((HERE/'ttbar_inputs/templates_gN.json').read_text())['templates']
normalization = {}
checks = []
for mv in (60., 100.):
    template = templates[str(int(mv))]
    mass = template['mchi']
    gc_at_gt1 = template['kappa']*mv**2
    reference = []
    for gt, mu in zip(grid['gts'], grid['ZE'][:, list(grid['MVS']).index(mv)]):
        if not math.isfinite(mu):
            continue
        inv = invisible_width(mv, mass, gc_at_gt1/gt)
        br = inv/(inv+visible_width(mv, gt))
        reference.append(float(mu*gt**2*br))
    normalization[mv] = float(np.median(reference))
    variation = max(reference)/min(reference)-1
    assert variation < 1e-4
    checks.append(dict(mv_GeV=mv, expected_unit_signal_limit=normalization[mv],
                       relative_scaling_spread=variation, checked_grid_points=len(reference)))

raw = [json.loads(line) for line in (HERE/'roots.jsonl').read_text().splitlines()]
rows = []
for point in raw:
    if point['point']=='M60_g1':
        continue
    mv, gt, d = point['mv_GeV'], point['gt'], point['d']
    roots = point['roots']['0']
    on = [r for r in roots if r[0]=='on']
    status = 'no_on_shell_root_in_scan'
    result = dict(point=point['point'], mv_GeV=mv, gt=gt, d_gamma0=d,
                  epsilon_gamma0=d*gt/math.sqrt(4*math.pi/137.035999),
                  on_roots=len(on), off_roots=sum(r[0]=='off' for r in roots),
                  status=status, mchi_GeV='', gchi='', width_GeV='', gap_GeV='',
                  BR_invisible='', expected_mu95='', omega_h2='')
    if on:
        assert len(on)==1
        _, mass, omega, xf, width, gc = on[0]
        gap = mv-2*mass-.001
        status = 'valid' if gap>5*width and width/mv<.03 else 'fails_narrow_width'
        br = invisible_width(mv, mass, gc)/width
        assert 0 < br <= 1
        mu = normalization[mv]/(gt**2*(1+2*d/3)**2*br)
        result.update(status=status, mchi_GeV=mass, gchi=gc, width_GeV=width,
                      gap_GeV=gap, BR_invisible=br,
                      expected_mu95=mu if status=='valid' else '', omega_h2=omega)
    rows.append(result)
with (HERE/'expected_limits.csv').open('w', newline='') as stream:
    writer=csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(HERE/'scaling_checks.json').write_text(json.dumps(checks, indent=2))

fig, axes=plt.subplots(1,2,figsize=(11,4.6),constrained_layout=True)
for point in sorted({r['point'] for r in rows}):
    selected=sorted([r for r in rows if r['point']==point], key=lambda r:r['d_gamma0'])
    first=selected[0]
    label=rf'$M_V={first["mv_GeV"]:g}$ GeV, $g_t={first["gt"]:.3g}$'
    x=[r['d_gamma0']/1e-4 for r in selected]
    axes[0].plot(x,[r['expected_mu95'] if r['expected_mu95']!='' else np.nan for r in selected],
                 'o-',label=label,markersize=4)
    axes[1].plot(x,[r['mchi_GeV'] if r['mchi_GeV']!='' else np.nan for r in selected],
                 'o-',label=label,markersize=4)
for ax in axes:
    ax.axvline(-1.49,color='.4',ls=':',label='Xe cancellation' if ax==axes[0] else None)
    ax.set_xlabel(r'$d_\gamma(0)\ [10^{-4}]$')
    ax.grid(alpha=.2)
axes[0].set_yscale('log')
axes[0].axhline(1,color='black',ls='--',lw=1)
axes[0].set_ylabel(r'Expected $\mu_{95}$ (fixed signal templates)')
axes[0].legend(fontsize=8)
axes[1].set_ylabel(r'$m_\chi$ [GeV], central Planck root')
axes[1].axhline(20,color='.6',ls='--',lw=1)
fig.suptitle(r'$t\bar t+\mathrm{MET}$, LZ rate matched; $20\leq m_\chi\leq100$ GeV, $0.1\leq g_\chi\leq1.5$')
fig.savefig(HERE/'expected_limits.png',dpi=180)
fig.savefig(HERE/'expected_limits.pdf')
for r in rows:
    print(r['point'],f"{r['d_gamma0']:.3g}",r['status'],
          f"m={r['mchi_GeV']} BR={r['BR_invisible']} mu95={r['expected_mu95']}")

"""Inspect the merged ttbar grid without rerunning or modifying its fit."""
import csv
import io
import json
import math
from pathlib import Path
import subprocess

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = HERE / 'review_20261120'


def main():
    OUT.mkdir(exist_ok=True)
    current = np.load(HERE / 'data/grid_gN.npz')
    previous = np.load(io.BytesIO(subprocess.check_output(
        ['git', 'show', '619020c:ttbar/data/grid_gN.npz'], cwd=REPO)))
    assert np.array_equal(current['MVS'], previous['MVS'])
    assert np.array_equal(current['gts'], previous['gts'])
    stats = []
    for j, mv in enumerate(current['MVS']):
        exp, obs = current['ZE'][:, j], current['ZO'][:, j]
        finite = np.isfinite(exp)
        assert np.array_equal(finite, np.isfinite(obs))
        assert np.all(exp[finite] > 0) and np.all(obs[finite] > 0)
        stats.append(dict(
            MV_GeV=int(mv), valid_grid_points=int(finite.sum()),
            min_expected_mu95=float(np.nanmin(exp)),
            min_observed_mu95=float(np.nanmin(obs)),
            expected_excluded_grid_points=int(np.sum(exp < 1)),
            observed_excluded_grid_points=int(np.sum(obs < 1)),
            previous_min_expected_mu95=float(np.nanmin(previous['ZE'][:, j])),
            previous_min_observed_mu95=float(np.nanmin(previous['ZO'][:, j]))))
    write_csv(OUT / 'grid_summary.csv', stats)

    with (REPO / 'data/lz_mass_normalization.csv').open() as f:
        reference = list(csv.DictReader(f))
    with (HERE / 'data/kappa_lz_gN.csv').open() as f:
        collaborator = list(csv.DictReader(f))
    masses = np.array([float(r['mchi_GeV']) for r in reference])
    logs = np.log([float(r['kappa_equal_rate']) for r in reference])
    other_masses = np.array([float(r['mchi']) for r in collaborator])
    other_kappa = np.array([float(r['kappa']) for r in collaborator])
    comparisons = []
    for mass in (24., 32., 36., 44., 48.):
        # Both columns here refer to one truth ROI event, at tree level.
        ours = float(np.exp(np.interp(mass, masses, logs))) / math.sqrt(1.120444105)
        theirs = float(np.interp(mass, other_masses, other_kappa))
        comparisons.append(dict(mchi_GeV=mass,
            paper_tree_kappa_one_event=ours, ttbar_kappa_one_event=theirs,
            amplitude_ratio=theirs / ours))
    write_csv(OUT / 'lz_normalization_comparison.csv', comparisons)
    metadata = dict(
        inspected_commit=subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        previous_commit='619020c',
        scope='Archived-grid and normalization-table checks only; no new MC or CLs fits.',
        interpolation='Paper: log-linear; collaborator: linear; five comparison masses.',
        reference_truth_ROI_yield=1.120444105,
        grid_shape=list(current['ZE'].shape))
    (OUT / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))
    print('Wrote grid_summary.csv and lz_normalization_comparison.csv')


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()

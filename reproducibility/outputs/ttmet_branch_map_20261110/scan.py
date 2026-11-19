"""Invert the equal-rate LZ relation and look for Planck solutions on each side of threshold."""

import bisect
import csv
import math
import subprocess
import sys
from pathlib import Path


PLANCK_LOW, PLANCK_HIGH = 0.1176, 0.1224
PLANCK_CENTRAL = 0.1200
SPLITTING = 0.001


def read_normalization(project):
    with (project / 'equal/lz_mass_normalization.csv').open() as file:
        return [(float(row['mchi_GeV']), math.log(float(row['kappa_equal_rate'])))
                for row in csv.DictReader(file)]


def allowed_mass_ranges(normalization, mv, gt):
    lower = math.log(0.10 * gt / mv**2)
    upper = math.log(1.50 * gt / mv**2)
    intervals = []
    for (a, fa), (b, fb) in zip(normalization, normalization[1:]):
        if max(fa, fb) < lower or min(fa, fb) > upper:
            continue
        if fa == fb:
            left, right = a, b
        else:
            lo, hi = sorted(((lower - fa) / (fb - fa), (upper - fa) / (fb - fa)))
            left = a + (b - a) * max(0.0, lo)
            right = a + (b - a) * min(1.0, hi)
        if intervals and left <= intervals[-1][1] + 1e-10:
            intervals[-1] = (intervals[-1][0], right)
        else:
            intervals.append((left, right))
    return intervals


def scan_cell(project, normalization, mv, gt, step):
    masses, log_kappas = zip(*normalization)
    threshold = (mv - SPLITTING) / 2
    cache = {}

    def evaluate(mass):
        if mass in cache:
            return cache[mass]
        index = min(len(masses) - 2, max(0, bisect.bisect_right(masses, mass) - 1))
        weight = (mass - masses[index]) / (masses[index + 1] - masses[index])
        gchi = math.exp((1 - weight) * log_kappas[index] + weight * log_kappas[index + 1]) * mv**2 / gt
        try:
            run = subprocess.run(['./mass_relic', str(mass), str(mv), str(gt), str(gchi)], cwd=project,
                                 capture_output=True, text=True, timeout=25)
        except subprocess.TimeoutExpired:
            cache[mass] = None
            return None
        result = next((line.split() for line in run.stdout.splitlines() if line.startswith('RESULT ')), None)
        value = None
        if run.returncode == 0 and result and int(result[4]) == 0:
            omega, width = float(result[1]), float(result[3])
            if math.isfinite(omega) and omega > 0:
                value = (mass, gchi, omega, width, mv - 2 * mass - SPLITTING)
        cache[mass] = value
        return value

    def in_band(point):
        return point is not None and PLANCK_LOW <= point[2] <= PLANCK_HIGH

    def root_between(left, right):
        if left is None or right is None:
            return None
        fa, fb = left[2] - PLANCK_CENTRAL, right[2] - PLANCK_CENTRAL
        if fa * fb >= 0:
            return None
        for _ in range(18):
            mid = evaluate((left[0] + right[0]) / 2)
            if mid is None:
                break
            fm = mid[2] - PLANCK_CENTRAL
            if abs(fm) < 2e-5:
                return mid
            if fa * fm < 0:
                right = mid
            else:
                left, fa = mid, fm
        best = min((left, right), key=lambda point: abs(point[2] - PLANCK_CENTRAL))
        return best if in_band(best) else None

    found = {'on': [], 'off': []}
    for low, high in allowed_mass_ranges(normalization, mv, gt):
        for branch, a, b in [('on', low, min(high, threshold - 0.0005)),
                             ('off', max(low, threshold + 0.0005), high)]:
            if b < a:
                continue
            count = max(1, math.ceil((b - a) / step))
            knots = {a + (b - a) * i / count for i in range(count + 1)}
            for center in (threshold, mv, 22.0):
                knots.update(x for x in (center - 0.2, center - 0.01, center + 0.01, center + 0.2)
                             if a < x < b)
            points = [evaluate(mass) for mass in sorted(knots)]
            found[branch].extend(point for point in points if in_band(point))
            for left, right in zip(points, points[1:]):
                root = root_between(left, right)
                if root is not None:
                    found[branch].append(root)
    return found, len(cache), sum(point is None for point in cache.values())


def main():
    project = Path(sys.argv[1])
    normalization = read_normalization(project)
    assert normalization[0][0] == 20 and normalization[-1][0] == 100
    writer = csv.writer(sys.stdout, lineterminator='\n')
    fields = ('mchi_GeV', 'gchi', 'omega_h2', 'width_GeV', 'gap_GeV')
    writer.writerow(['mv_GeV', 'gt', 'on_count', 'off_count', 'n_calls', 'n_failed',
                     *(f'{branch}_{field}' for branch in ('on', 'off') for field in fields)])
    if sys.argv[2:] == ['benchmark']:
        grid = [(30, 0.2), (36, 0.3), (62.2627568245, 0.54569366783),
                (87.1833, 1.06994), (70, 1), (90, 0.3)]
    else:
        masses = range(20, 101, 2)
        couplings = [0.2 * 20**(i / 26) for i in range(27)]
        grid = [(mv, gt) for mv in masses for gt in couplings]
        grid = grid[int(sys.argv[2]):] if len(sys.argv) > 2 else grid
    for mv, gt in grid:
        found, calls, failures = scan_cell(project, normalization, mv, gt, 1.0)
        representatives = [min(found[branch], key=lambda point: abs(point[2] - PLANCK_CENTRAL))
                           if found[branch] else ('',) * len(fields) for branch in ('on', 'off')]
        writer.writerow([mv, gt, len(found['on']), len(found['off']), calls, failures,
                         *representatives[0], *representatives[1]])
        sys.stdout.flush()


if __name__ == '__main__':
    main()

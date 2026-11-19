"""Find the on-shell Planck crossings as a function of both masses and gchi."""
import argparse
import csv
import itertools
import math
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue

import numpy as np
from scipy.integrate import trapezoid
from scipy.optimize import brentq
from scipy.special import ndtr


TARGET = 1.120444105
OMEGA = (.1176, .12, .1224)
GT_MAX = math.sqrt(4*math.pi)
COUPLINGS = sorted({round(float(x), 9) for x in np.geomspace(.1, 1.5, 49)}
                   | {.18, .2, .25, .3, .4, .5, .6, .8, 1.})
MASSES = sorted(set(range(20, 101, 2)) | set(range(31, 54))
                | {34.5+.5*i for i in range(16)})


def write(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def recoil(project, mchi, folder):
    card, output = (folder/f"mchi_{mchi:g}.{ext}" for ext in ("par", "csv"))
    card.write_text(f"Mchi {mchi}\ndM .001\nMV 100\ngYt 1\ngChi .3\nfExc .5\nrho0 .3\n"
                    "v0 238\nvE 254\nvesc 544\n")
    args = [str(project/"lz_recoil"), str(card), str(output)]
    run = subprocess.run(args, cwd=project, check=True, capture_output=True, text=True, timeout=100)
    nroi = float(re.search(r"ROI_5\.4_269\.9=(\S+)",run.stdout)[1])
    nsb = float(re.search(r"SB_350_675=(\S+)",run.stdout)[1])
    energy, rate = np.loadtxt(output, skiprows=4, delimiter=",", unpack=True)
    y = rate*(2.84e3*365.25)
    at_event = np.interp(248.,energy,y)
    sigma = math.hypot(23,23)
    p_roi = ndtr((269.9-energy)/sigma)-ndtr((5.4-energy)/sigma)
    p_sb = ndtr((675-energy)/sigma)-ndtr((350-energy)/sigma)
    gn_roi, gn_sb = (float(trapezoid(p*y,x=energy)) for p in (p_roi, p_sb))
    g_density = float(trapezoid(y*np.exp(-.5*((248-energy)/sigma)**2),x=energy)/(sigma*math.sqrt(2*math.pi)))
    return dict(mchi_GeV=mchi, truth_roi_ref=nroi, truth_sb_ref=nsb,
                kappa_equal_rate=.3/100**2*math.sqrt(TARGET/nroi) if nroi > 0 else math.inf,
                kappa_gaussian_profile=.3/100**2/math.sqrt(gn_roi+gn_sb) if gn_roi+gn_sb > 0 else math.inf,
                truth_shape_density_per_keV=at_event/(nroi+nsb) if nroi+nsb > 0 else 0.,
                gauss_shape_density_per_keV=g_density/(gn_roi+gn_sb) if gn_roi+gn_sb > 0 else 0.,
                sb_over_roi=nsb/nroi if nroi > 0 else math.inf,
                gauss_sb_over_roi=gn_sb/gn_roi if gn_roi > 0 else math.inf,
                zero_recoil_Xe131_keV=1000*mchi/(.93149410242*131+mchi))


def evaluate(project, mchi, mv, gchi, kappa):
    gt = kappa*mv**2/gchi
    run = subprocess.run([str(project/"mass_relic"),str(mchi),str(mv),str(gt),str(gchi)],
                         cwd=project, check=True, capture_output=True, text=True, timeout=80)
    result, = (line for line in run.stdout.splitlines() if line.startswith("RESULT "))
    omega, xf, width, err = map(float,result.split()[1:])
    if err or not all(math.isfinite(v) and v > 0 for v in (omega,xf,width)):
        raise ValueError(run.stdout + run.stderr)
    return dict(mchi_GeV=mchi, mass_GeV=mv, gchi=gchi, gt_LZ=gt, omega_h2=omega,
                Xf=xf, width_GeV=width, width_over_mass=width/mv,
                threshold_distance_over_width=(mv-2*mchi-.001)/width)


def scan_slice(project, recoil_row, gc, norm):
    mchi = recoil_row["mchi_GeV"]
    kappa = recoil_row[f"kappa_{norm}"]
    low = 2*mchi+.001+.05
    top = min(240.,math.sqrt(GT_MAX*gc/kappa)) if math.isfinite(kappa) else 0.
    if top <= low:
        return [], [], dict(mchi_GeV=mchi,gchi=gc,top_GeV=top,n_evals=0,n_crossings=0)
    cache = {}

    def point(m):
        if m not in cache:
            cache[m] = evaluate(project,mchi,m,gc,kappa)
        return cache[m]

    grid = sorted({low,top} | {x for x in np.arange(45.,241.,8.) if low < x < top}
                  | {low+d for d in (1,3,8,16,24,40) if low+d < top})
    rows = [point(m) for m in grid]
    roots = []
    for a,b in zip(rows,rows[1:]):
        below, above = sorted((a["omega_h2"],b["omega_h2"]))
        for level in OMEGA:
            if below <= level <= above:
                root = brentq(lambda m: point(m)["omega_h2"]-level,
                              a["mass_GeV"],b["mass_GeV"],xtol=2e-5)
                roots.append(dict(point(root),target_omega_h2=level,
                                  crossing_direction=1 if b["omega_h2"]>=a["omega_h2"] else -1))
    return rows, roots, dict(mchi_GeV=mchi,gchi=gc,top_GeV=top,n_evals=len(cache),n_crossings=len(roots))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mass", type=float, nargs="+", default=MASSES)
    parser.add_argument("--gchi", type=float, nargs="+", default=COUPLINGS)
    parser.add_argument("--normalization", choices=("equal_rate","gaussian_profile"), default="equal_rate")
    parser.add_argument("projects",type=Path,nargs="+")
    args = parser.parse_args()
    out = args.output.resolve()
    recoil_folder = out/"spectra"
    recoil_folder.mkdir(exist_ok=True,parents=True)
    recoil_rows = [recoil(Path.cwd(),m,recoil_folder) for m in sorted(set(args.mass))]
    for row in recoil_rows:
        if row["mchi_GeV"] == 35:
            assert math.isclose(row["kappa_equal_rate"],.0380063/30**2,rel_tol=1e-4), row
    write(out/"lz_mass_normalization.csv",recoil_rows)

    workers = Queue()
    for project in args.projects:
        workers.put(project.resolve())

    def run(item):
        project = workers.get()
        try:
            return scan_slice(project,*item,args.normalization)
        finally:
            workers.put(project)

    grid, roots, logs = [], [], []
    with ThreadPoolExecutor(max_workers=len(args.projects)) as pool:
        for i,(rows,crossings,log) in enumerate(pool.map(run,itertools.product(recoil_rows,sorted(set(args.gchi)))),1):
            grid.extend(rows)
            roots.extend(crossings)
            logs.append(log)
            if i%250 == 0:
                print(i, "slices", len(roots), "crossings", flush=True)
    for name, rows in (("relic_grid",grid),("relic_crossings",roots),("relic_scan_log",logs)):
        if rows:
            write(out/f"{name}.csv",rows)
    print(len(logs),"slices",sum(row["n_evals"] for row in logs),"evaluations",len(roots),"crossings",flush=True)


if __name__ == "__main__":
    main()

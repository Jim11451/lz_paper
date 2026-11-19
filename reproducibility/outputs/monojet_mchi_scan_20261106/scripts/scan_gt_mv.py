"""Invert the LZ and thermal constraints at fixed mediator mass and top coupling."""
import argparse
import itertools
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from scan import evaluate, write


OMEGA_LO, OMEGA_HI = .1176, .1224
MCHI_MIN = 28.
GT_MAX = math.sqrt(4*math.pi)


def dark_width(row):
    mv,m,g = (row[k] for k in ("mass_GeV","mchi_GeV","gchi"))
    r1,r2 = (m/mv)**2,((m+.001)/mv)**2
    phase = math.sqrt((1-((2*m+.001)/mv)**2)*(1-(.001/mv)**2))
    spin = 1-(r1+r2)/2-(r1-r2)**2/2+3*math.sqrt(r1*r2)
    return (g/2)**2*mv/(12*math.pi)*phase*spin


def project_point(project, mv, gt, kappa):
    """The largest invisible branching fraction gives the best CMS limit."""
    out = dict(mass_GeV=mv,gt_LZ=gt,mchi_low_GeV=math.nan,mchi_high_GeV=math.nan,
               mchi_best_GeV=math.nan,gchi_best=math.nan,omega_h2_best=math.nan,
               width_GeV=math.nan,BR_invisible=math.nan,n_intervals=0,n_calls=0)
    lo,hi = MCHI_MIN,min(100.,(mv-.051)/2)
    gc = lambda m: kappa(m)*mv**2/gt
    if gc(hi)<.1 or gc(lo)>1.5:
        return out
    if gc(lo)<.1:
        lo = brentq(lambda m: gc(m)-.1,lo,hi,xtol=1e-8)
    if gc(hi)>1.5:
        hi = brentq(lambda m: gc(m)-1.5,lo,hi,xtol=1e-8)
    if hi-lo<1e-6:
        return out

    cache = {}

    def point(m):
        if m not in cache:
            cache[m] = evaluate(project,m,mv,gc(m),kappa(m))
        return cache[m]

    def abundance(m):
        return point(m)["omega_h2"]

    anchors = [lo,(lo+hi)/2,hi]
    for x in anchors:
        abundance(x)
    roots = []
    for level in (OMEGA_LO,OMEGA_HI):
        known = sorted(cache)
        for a,b in zip(known,known[1:]):
            if (abundance(a)-level)*(abundance(b)-level)<0:
                root = brentq(lambda m: abundance(m)-level,a,b,xtol=1e-5)
                roots.append(root)
                abundance(root)
    boundaries = sorted(set([lo,hi,*roots]))
    intervals, viable = [], []
    for a,b in zip(boundaries,boundaries[1:]):
        if any(not OMEGA_LO-2e-6 <= abundance(m) <= OMEGA_HI+2e-6 for m in (a,b)):
            continue
        options = [point(m) for m in (a,(a+b)/2,b)]
        options = [p for p in options if OMEGA_LO-2e-6 <= p["omega_h2"] <= OMEGA_HI+2e-6
                   and p["width_over_mass"]<.03 and p["threshold_distance_over_width"]>=5]
        if options:
            intervals.append((options[0]["mchi_GeV"],options[-1]["mchi_GeV"]))
            viable.extend(options)
    out["n_calls"] = len(cache)
    if viable:
        best = max(viable,key=lambda p: dark_width(p)/p["width_GeV"])
        out.update(mchi_low_GeV=min(a for a,_ in intervals),mchi_high_GeV=max(b for _,b in intervals),
                   mchi_best_GeV=best["mchi_GeV"],gchi_best=best["gchi"],omega_h2_best=best["omega_h2"],
                   width_GeV=best["width_GeV"],BR_invisible=dark_width(best)/best["width_GeV"],
                   n_intervals=len(intervals))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lz",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--resolution",type=int,default=81)
    parser.add_argument("projects",type=Path,nargs="+")
    args = parser.parse_args()
    rows = np.genfromtxt(args.lz,names=True,delimiter=",")
    rows = rows[rows["mchi_GeV"]>=MCHI_MIN]
    log_kappa = np.log(rows["kappa_equal_rate"])
    assert np.all(np.diff(log_kappa)>0)
    interpolator = PchipInterpolator(rows["mchi_GeV"],log_kappa)
    kappa = lambda m: math.exp(interpolator(m))
    mvs = np.linspace(72.,200.,args.resolution)
    gts = np.geomspace(.1,GT_MAX,101)

    workers = Queue()
    for project in args.projects:
        workers.put(project.resolve())

    def run(inputs):
        project = workers.get()
        try:
            return project_point(project,*inputs,kappa)
        finally:
            workers.put(project)

    output = []
    with ThreadPoolExecutor(max_workers=len(args.projects)) as pool:
        for i,row in enumerate(pool.map(run,itertools.product(mvs,gts)),1):
            output.append(row)
            if i%1000==0:
                print(i,len(mvs)*len(gts),sum(r["n_intervals"]>0 for r in output),flush=True)
    write(args.output,output)
    print(len(output),"pixels",sum(r["n_intervals"]>0 for r in output),"valid",
          sum(r["n_calls"] for r in output),"evaluations",flush=True)


if __name__ == "__main__":
    main()

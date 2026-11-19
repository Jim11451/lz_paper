import gzip
import sys
from pathlib import Path

import numpy as np
from build_templates import BIN_LOW, HERE, PREVIOUS, STITCH, detector_bins, uncompress_and_read

mass = 87.1833386421
for original, channel in (("B13_loop_loose", "loop"), ("B13_loop_tail", "loop_hard")):
    reference = PREVIOUS / "production" / original / "Events" / original / "unweighted_events.lhe.gz"
    target = HERE / f"validation_{original}.lhe"
    p = uncompress_and_read(reference, target, mass)
    source = PREVIOUS / "detector" / original / "events.root"
    counts, alignment = detector_bins(source, p, mass, channel)
    with gzip.open(PREVIOUS / "results/events" / f"{original}.csv.gz", "rt") as stream:
        e = np.genfromtxt(stream, names=True, delimiter=",")
    met, phi = e["met"], e["met_phi"]
    lo, hi = STITCH[channel]
    sel = ((e["gen_met"] >= lo) & (e["gen_met"] < hi) & (e["j1_pt"] > 100)
           & (abs(e["j1_eta"]) < 2.4) & (met > 250) & (e["min_dphi"] > .5))
    for key in ("electron_veto", "muon_veto", "photon_veto", "tau_veto_run2", "b_veto"):
        sel &= e[key] > 0
    hem = ((met >= 470) | (phi < -1.62) | (phi > -.62)) & (e["hem_jet_veto"] > 0)
    legacy = np.zeros(len(e), dtype=int)
    legacy[sel] = 1 + 2*(np.searchsorted(BIN_LOW, met[sel], side="right")-1) + hem[sel]
    assert np.array_equal(counts, np.bincount(legacy, minlength=45)), original
    target.unlink()
    print(original, "45 paired year/bin categories reproduced", int(sel.sum()), alignment, flush=True)

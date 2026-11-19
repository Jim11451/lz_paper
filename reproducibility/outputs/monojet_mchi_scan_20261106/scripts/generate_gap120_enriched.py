"""Independently enrich the reconstructed MET tail at the 120 GeV node."""
from pathlib import Path
import shutil
import sys

import numpy as np

here = Path.cwd()
previous = here.parent/"monojet_expected_lz_scan_20261106"
sys.path.insert(0,str(previous/"scripts"))
import generate_templates as production
import build_templates as detector

for name in ("logs","production","results","detector","templates"):
    (here/name).mkdir(exist_ok=True)
mg = production.mg
mg.HERE = here
mg.SPECS = dict(production.SPECS,loop=(230,4.5,1800))
detector.HERE = here
key = "loop_m18"
proc = here/"production"/key
if not proc.exists():
    shutil.copytree(previous/"production/loop_m06",proc,symlinks=True,
                    ignore=shutil.ignore_patterns("Events","HTML"))

# Re-bin the old independent sample only below the new generation threshold.
with np.load(previous/"templates/loop_m06.npz") as old:
    hard_pt = detector.uncompress_and_read(
        previous/"production/loop_m06/Events/loop_m06/unweighted_events.lhe.gz",
        here/"detector/original.lhe",120.)
    detector.STITCH["loop"] = (100,230)
    counts,alignment = detector.detector_bins(previous/"detector/loop_m06/events.root",hard_pt,120.,"loop")
    np.savez_compressed(here/"templates/loop_below230.npz",counts=counts,alignment=alignment,
                        cross=old["cross"],cross_error=old["cross_error"],channel="loop",mass=120.)
    print("BELOW 230",counts.sum(),counts[1:].sum(),flush=True)

detector.STITCH["loop"] = (230,480)
row = mg.execute(18,120.,"loop",production.REFERENCE/"tree_template")
print("GENERATED",row,flush=True)
print("SELECTED",detector.process(here/"results"/f"{key}.csv"),flush=True)

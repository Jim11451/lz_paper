"""Generate two independent high-statistics samples for the 120 GeV loop bulk."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import sys

here = Path.cwd()
previous = here.parent/"monojet_expected_lz_scan_20261106"
sys.path.insert(0,str(previous/"scripts"))
import generate_templates as production
import build_templates as detector

for name in ("logs","production","results","detector","templates"):
    (here/name).mkdir(exist_ok=True)
mg = production.mg
mg.HERE = here
mg.SPECS = dict(production.SPECS,loop=(100,4.5,10800))
detector.HERE = here


def run(index):
    proc = here/"production"/f"loop_m{index:02d}"
    if not proc.exists():
        source = previous/"production/loop_m06"
        shutil.copytree(source,proc,symlinks=True,ignore=shutil.ignore_patterns("Events","HTML"))
    row = mg.execute(index,120.,"loop",production.REFERENCE/"tree_template")
    print("GENERATED",row,flush=True)
    result = detector.process(here/"results"/f"{row['run']}.csv")
    print("SELECTED",result,flush=True)


with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(run,(16,17)))

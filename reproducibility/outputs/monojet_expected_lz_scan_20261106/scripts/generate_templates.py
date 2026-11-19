import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REFERENCE = HERE.parent / "truth_xsec_scan_20261106"
sys.path.insert(0, str(REFERENCE / "scripts"))
import run_scan as mg

SPECS = {"loop": (100, 4.5, 3600), "loop_hard": (480, 4.5, 2100),
         "jet_tree": (100, 4.5, 12000), "jet_tree_hard": (350, 4.5, 3000)}
INDICES = (3, 0, 10, 5, 8, 2, 6, 9, 1, 4, 7)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--channels", nargs="+", choices=SPECS, default=list(SPECS))
    args = parser.parse_args()
    mg.HERE = HERE
    mg.SPECS = SPECS
    tree = REFERENCE / "tree_template"
    jobs = [(index, mg.MASSES[index], channel) for index in INDICES for channel in args.channels]
    failed = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(mg.execute, *job, tree): job for job in jobs}
        for future in as_completed(futures):
            try:
                print("DONE", future.result(), flush=True)
            except Exception as exc:
                print("ERROR", futures[future], repr(exc), flush=True)
                failed = True
    if failed:
        raise SystemExit(1)
    print("COMPLETE", flush=True)


if __name__ == "__main__":
    main()

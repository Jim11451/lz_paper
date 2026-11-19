import argparse
import re
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
LOOP = HERE.parent / "monojet_loop_20261103"
TREE = HERE.parent / "PseudoDiracYukawaLZ_xsec_20261020"
B_TREE = "LZ_M87_gc0p3_monojet_13p6TeV"
JOBS = {
    "B13_tree_loose": (TREE, "proc_monojet", B_TREE, 13000, 100, 15000, 619602),
    "B13_loop_loose": (LOOP, "ggVg", "B_13TeV", 13000, 100, 6000, 619601),
    "B13_loop_tail": (LOOP, "ggVg", "B_13TeV", 13000, 480, 3000, 619603),
}


def set_values(card, values):
    for key, value in values.items():
        pattern = rf"(?m)^\s*[^\r\n=!#]+?\s*=\s*{re.escape(key)}\b[^\r\n]*"
        card, count = re.subn(pattern, f" {value} = {key}", card)
        if count != 1:
            raise ValueError((key, count))
    return card


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample", choices=JOBS)
    args = parser.parse_args()
    base, source, point, energy, ptmin, nevents, seed = JOBS[args.sample]
    evidence = base / ("results" if base == LOOP else "evidence") / point
    proc = HERE / "production" / args.sample
    if not proc.exists():
        shutil.copytree(base / source, proc, symlinks=True, ignore=shutil.ignore_patterns("Events", "HTML"))
    for directory in ("Events", "HTML"):
        (proc / directory).mkdir(exist_ok=True)
    for path in (proc / "Cards").glob("shower_card.dat"):
        path.unlink()
    shutil.copyfile(evidence / "param_card.dat", proc / "Cards/param_card.dat")
    card = (evidence / "run_card.dat").read_text()
    (proc / "Cards/run_card.dat").write_text(set_values(card, {
        "nevents": nevents, "iseed": seed, "ebeam1": energy / 2, "ebeam2": energy / 2,
        "ptj": ptmin, "use_syst": "False",
    }))
    configuration = proc / "Cards/me5_configuration.txt"
    old_configuration = re.sub(r"(?m)^\s*(run_mode|nb_core|automatic_html_opening)\s*=.*$", "",
                               configuration.read_text())
    configuration.write_text(old_configuration + "\nrun_mode = 2\nnb_core = 4\n"
                             "automatic_html_opening = False\n")
    with (HERE / "logs" / f"generate_{args.sample}.log").open("w") as log:
        subprocess.run([str(proc / "bin/generate_events"), args.sample, "-f"],
                       cwd=proc, check=True, stdout=log, stderr=subprocess.STDOUT)
    events = proc / "Events" / args.sample
    assert (events / "unweighted_events.lhe.gz").stat().st_size > 1000
    print(events, flush=True)


if __name__ == "__main__":
    main()

import argparse
import csv
import gzip
import math
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
BASE = HERE.parent
MG = Path.home() / "MG5_aMC_v3_6_6/bin/mg5_aMC"
LOOP = BASE / "monojet_loop_20261103"
YUKAWA = BASE / "PseudoDiracYukawaLZ_xsec_20261020"
TREE_UFO = BASE / "PseudoDiracFlavorEFT_20261020/PseudoDiracFlavorEFT_UFO"
QUARKS = (0.0022, 0.0047, 0.096, 1.27, 4.18, 172.0)
MASSES = (72.0, 76.0, 82.0, 87.1833386421, 95.0, 105.0, 120.0, 135.0, 150.0, 175.0, 200.0)
SPECS = {"loop": (20, 6, 600), "jet_tree": (20, 6, 1000),
         "jet_tree_hard": (200, 4.5, 1000), "tops": (None, None, 4000),
         "loop_hard": (200, 4.5, 180)}


def change_run(card, edits):
    for key, value in edits.items():
        card, n = re.subn(rf"(?m)^[^\r\n=!#]+?\s*=\s*{key}\b[^\r\n]*",
                          f" {value} = {key}", card)
        if n != 1:
            raise ValueError((key, n))
    return card


def change_param(card, block, code, value):
    section = re.search(rf"(?ims)^Block\s+{block}\b[^\n]*\n(.*?)(?=^Block\s|^DECAY\s|\Z)", card)
    if section is None:
        raise ValueError(block)
    updated, n = re.subn(rf"(?m)^(\s*{code}\s+)\S+", rf"\g<1>{value:.12e}", section[1])
    if n != 1:
        raise ValueError((block, code, n))
    return card[:section.start(1)] + updated + card[section.end(1):]


def make_tree():
    proc = HERE / "tree_template"
    if not (proc / "Cards/run_card.dat").is_file():
        commands = HERE / "tree_template.mg5"
        commands.write_text(f"import model {TREE_UFO}-full\n"
                            "define p5 = g u c d s b u~ c~ d~ s~ b~\n"
                            "define j5 = p5\n"
                            "generate p5 p5 > Vb j5 PDB=1 QCD=1 QED=0\n"
                            f"output {proc} -f\nquit\n")
        with (HERE / "logs/tree_template.log").open("w") as stream:
            subprocess.run([str(MG), str(commands)], cwd=HERE, stdout=stream,
                           stderr=subprocess.STDOUT, check=True)
    return proc


def recoil_counts(lhe):
    count = 0
    cuts = [0, 0, 0]
    with gzip.open(lhe, "rt") as stream:
        for line in stream:
            if line.strip() != "<event>":
                continue
            n = int(next(stream).split()[0])
            particles = [next(stream).split() for _ in range(n)]
            mediator, = [p for p in particles if int(p[0]) == 9900032 and int(p[1]) == 1]
            pt = math.hypot(float(mediator[6]), float(mediator[7]))
            count += 1
            cuts[0] += pt > 20
            cuts[1] += pt > 100
            jets = [p for p in particles if int(p[1]) == 1 and
                    (abs(int(p[0])) <= 5 or int(p[0]) == 21)]
            eta_ok = all(abs(math.asinh(float(j[8]) / math.hypot(float(j[6]), float(j[7])))) < 4.5
                         for j in jets)
            cuts[2] += pt > 200 and eta_ok
    return count, cuts


def execute(index, mass, channel, tree_template):
    key = f"{channel}_m{index:02d}"
    report = HERE / "results" / f"{key}.csv"
    if report.is_file():
        with report.open() as stream:
            return next(csv.DictReader(stream))
    template, evidence = {
        "loop": (LOOP / "ggVg", LOOP / "results/B_13TeV"),
        "loop_hard": (LOOP / "ggVg", LOOP / "results/B_13TeV"),
        "tops": (YUKAWA / "proc_ttv_nwa", YUKAWA / "evidence/LZ_M87_gc0p3_ttv_nwa_13TeV"),
        "jet_tree": (tree_template, tree_template / "Cards"),
        "jet_tree_hard": (tree_template, tree_template / "Cards"),
    }[channel]
    proc = HERE / "production" / key
    if not proc.exists():
        shutil.copytree(template, proc, symlinks=True, ignore=shutil.ignore_patterns("Events", "HTML"))
    for sub in ("Events", "HTML"):
        (proc / sub).mkdir(exist_ok=True)
    param = (evidence / "param_card.dat").read_text()
    for pdg, mq in enumerate(QUARKS, 1):
        param = change_param(param, "flavcoup", pdg, mq / 172)
    for block, code, value in (("mass", 9900032, mass), ("mass", 100051, 35),
                               ("pdbinputs", 2, 0.3), ("pdbinputs", 3, 0.001)):
        param = change_param(param, block, code, value)
    (proc / "Cards/param_card.dat").write_text(param)
    pt, eta, target = SPECS[channel]
    card = (evidence / "run_card.dat").read_text()
    edits = dict(nevents=target, iseed=620000 + 10*index + list(SPECS).index(channel),
                 ebeam1=6500, ebeam2=6500, use_syst="False",
                 dynamical_scale_choice=-1)
    pdf_keys = ("pdlabel1", "pdlabel2") if re.search(r"=\s*pdlabel1\b", card) else ("pdlabel",)
    edits.update(dict.fromkeys(pdf_keys, "nn23lo1"))
    if pt is not None:
        edits.update(ptj=pt, etaj=eta)
    (proc / "Cards/run_card.dat").write_text(change_run(card, edits))
    conf = proc / "Cards/me5_configuration.txt"
    config = re.sub(r"(?m)^\s*(run_mode|nb_core|automatic_html_opening)\s*=.*$", "", conf.read_text())
    conf.write_text(config + "\nrun_mode = 2\nnb_core = 3\nautomatic_html_opening = False\n")
    logfile = HERE / "logs" / f"{key}.log"
    with logfile.open("w") as stream:
        subprocess.run([str(proc / "bin/generate_events"), key, "-f"], cwd=proc, stdout=stream,
                       stderr=subprocess.STDOUT, check=True, timeout=1800)
    event = proc / "Events" / key
    banner = next(event.glob("*_banner.txt"))
    xs = float(re.search(r"Integrated weight \(pb\)\s*:\s*([.\dEe+\-]+)", banner.read_text())[1])
    error = float(re.findall(r"Cross-section\s*:\s*[.\dEe+\-]+\s*\+\-\s*([.\dEe+\-]+)",
                             logfile.read_text(errors="replace"))[-1])
    n, (n20, n100, n200) = recoil_counts(event / "unweighted_events.lhe.gz")
    if n < 0.95 * target or xs <= 0:
        raise ValueError((key, n, target, xs))
    shutil.copyfile(banner, HERE / "results" / banner.name)
    row = dict(mass_GeV=mass, channel=channel, cross_pb=xs, error_pb=error, events=n,
               pass20=n20, pass100=n100, pass200=n200, run=key)
    with report.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, row.keys())
        writer.writeheader()
        writer.writerow(row)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--channels", nargs="+", choices=SPECS, default=list(SPECS))
    args = parser.parse_args()
    for name in ("logs", "production", "results"):
        (HERE / name).mkdir(exist_ok=True)
    tree = make_tree()
    indices = (3, 0, 6, 10, 1, 2, 4, 5, 7, 8, 9)
    jobs = [(i, MASSES[i], c) for c in args.channels for i in indices]
    failed = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(execute, *job, tree): job for job in jobs}
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

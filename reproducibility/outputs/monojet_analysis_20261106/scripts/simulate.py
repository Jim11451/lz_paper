import argparse
import gzip
import os
import re
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
DELPHES = HERE / "tools/delphes-3.5.0"
LOOP = HERE.parent / "monojet_loop_20261103/ggVg/Events"
TREE = HERE.parent / "PseudoDiracYukawaLZ_xsec_20261020/proc_monojet/Events"
SAMPLES = {
    "A_loop": (LOOP / "A", 240.0154004125486, 1.5077700519172976, 13.6, 200),
    "B_loop": (LOOP / "B", 152.53864875243084, 1.1315752047565861, 13.6, 200),
    "C_loop": (LOOP / "C", 14.560355205727191, 0.09047148926424427, 13.6, 200),
    "B13_loop": (LOOP / "B_13TeV", 135.1472356486896, 0.7336127387946665, 13.0, 200),
    "B_tree": (TREE / "LZ_M87_gc0p3_monojet_13p6TeV", 33.4684014, 0.12, 13.6, 200),
    "C_tree": (TREE / "LZ_M86_gc1_monojet_13p6TeV", 3.25219801, 0.01453, 13.6, 200),
}
for name, ptmin in (("B13_loop_loose", 100), ("B13_tree_loose", 100), ("B13_loop_tail", 480)):
    SAMPLES[name] = (HERE / "production" / name / "Events" / name, None, None, 13.0, ptmin)


def detector_card(seed):
    original = (DELPHES / "cards/delphes_card_CMS.tcl").read_text()
    card = f"set RandomSeed {seed}\n" + original.replace("set ParameterR 0.5", "set ParameterR 0.4")
    invisible = "\n".join(f"  add EnergyFraction {{{pid}}} {{0.0}}" for pid in (9900032, 100051, 100052))
    card = card.replace("add EnergyFraction {1000022} {0.0}",
                        "add EnergyFraction {1000022} {0.0}\n" + invisible)
    header = "module PdgCodeFilter NeutrinoFilter {"
    card = card.replace(header, header + "\n  add PdgCode {9900032}\n  add PdgCode {100051}\n  add PdgCode {100052}")
    card = card.replace("add Branch Delphes/allParticles Particle GenParticle",
                        "add Branch Delphes/allParticles Particle GenParticle\n"
                        "  add Branch Delphes/allParticlesLHEF ParticleLHEF GenParticle")
    return card


def source_events(name):
    path, cross, error, energy, ptmin = SAMPLES[name]
    source = path / "unweighted_events.lhe.gz"
    banner = next(path.glob("*_banner.txt")).read_text()
    factor = 0.8889043242392664 if "loop" in name else 1.0
    if cross is None:
        cross = float(re.search(r"Integrated weight \(pb\)\s*:\s*([.\dEe+\-]+)", banner)[1]) * 1000 * factor
    if error is None:
        new_log = HERE / "logs" / f"generate_{name}.log"
        if new_log.exists():
            matches = re.findall(r"Cross-section\s*:\s*([.\dEe+\-]+)\s*\+\-\s*([.\dEe+\-]+)",
                                 new_log.read_text(errors="replace"))
            if matches:
                error = float(matches[-1][1]) * 1000 * factor
    return source, cross, error, energy, ptmin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample", choices=SAMPLES)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    source, _, _, _, _ = source_events(args.sample)
    name = args.sample + ("_test" if args.test else "")
    run = HERE / "detector" / name
    run.mkdir(parents=True, exist_ok=True)
    lhe = run / "hard.lhe"
    with gzip.open(source, "rb") as incoming, lhe.open("wb") as outgoing:
        shutil.copyfileobj(incoming, outgoing)
    with lhe.open() as stream:
        n_events = sum(line.strip().startswith("<event") and line.strip() != "<eventgroup>" for line in stream)
    seed = 960100 + list(SAMPLES).index(args.sample)
    card = run / "cms_ak4.tcl"
    card.write_text(detector_card(seed))
    pythia = run / "shower.cmnd"
    pythia.write_text(f"""Main:numberOfEvents = {min(40, n_events) if args.test else n_events}
Main:timesAllowErrors = 20
Beams:frameType = 4
Beams:LHEF = {lhe}
SLHA:readFrom = 0
Tune:pp = 14
Random:setSeed = on
Random:seed = {seed}
9900032:new = Vb Vb 3 0 0 87.0 0.0 0.0 0.0 0.0
9900032:mayDecay = off
9900032:isVisible = off
100051:new = X1 X1 2 0 0 35.0 0.0 0.0 0.0 0.0
100051:mayDecay = off
100051:isVisible = off
100052:new = X2 X2 2 0 0 35.001 0.0 0.0 0.0 0.0
100052:mayDecay = off
100052:isVisible = off
Next:numberShowInfo = 0
Next:numberShowProcess = 0
Next:numberShowEvent = 0
""")
    home = Path.home()
    pkg = home / "miniconda3/pkgs/pythia8-8.312-py310hd4c7fa3_305"
    env = {**os.environ, "PYTHIA8DATA": str(pkg / "share/Pythia8/xmldoc"),
           "LD_LIBRARY_PATH": f"/usr/local/root/lib:{home}/miniconda3/envs/public/lib:{pkg}/lib"}
    with (HERE / "logs" / f"detector_{name}.log").open("w") as log:
        subprocess.run([str(DELPHES / "DelphesPythia8"), str(card), str(pythia), str(run / "events.root")],
                       cwd=DELPHES, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
    print(run, flush=True)


if __name__ == "__main__":
    main()

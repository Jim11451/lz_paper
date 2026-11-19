"""Independent LO DMsimp signal with the project's monojet fast simulation."""

import csv
import gzip
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

HERE = Path(__file__).resolve().parent.parent
BASE = HERE.parent
sys.path.insert(0, str(BASE / "truth_xsec_scan_20261106/scripts"))
sys.path.insert(0, str(BASE / "monojet_analysis_20261106/scripts"))
sys.path.insert(0, str(BASE / "monojet_expected_lz_scan_20261106/scripts"))
from build_templates import BIN_LOW, veto
from run_scan import MG, change_param, change_run
from simulate import DELPHES, detector_card

PDG = 5000521
NEVENTS = 45000


def run_command(command, path, log, env=None):
    with log.open("w") as stream:
        subprocess.run([str(arg) for arg in command], cwd=path, env=env, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)


def width(mass):
    def term(m, coupling, color):
        r = (m / mass) ** 2
        return color * coupling**2 * (1 + 2*r) * math.sqrt(1 - 4*r) if r < .25 else 0.
    return mass / (12 * math.pi) * (term(1., 1., 1) + 5*term(0., .25, 3) + term(172., .25, 3))


def generation_results(mass, proc):
    run = proc / "Events" / "vector"
    log = HERE / "logs" / f"generate_{mass}.log"
    banner = next(run.glob("*_banner.txt"), None)
    if banner is None:
        raise RuntimeError(f"MadGraph did not produce a banner. See {log}")
    shutil.copyfile(banner, HERE / "results" / f"vector_{mass}_banner.txt")
    cross = float(re.search(r"Integrated weight \(pb\)\s*:\s*([.\dEe+\-]+)", banner.read_text())[1])
    error = float(re.findall(r"Cross-section\s*:\s*[.\dEe+\-]+\s*\+\-\s*([.\dEe+\-]+)", log.read_text())[-1])
    return run / "unweighted_events.lhe.gz", cross, error


def generate(mass, proc, seed):
    if (proc / "Events/vector/unweighted_events.lhe.gz").is_file():
        return generation_results(mass, proc)
    commands = proc.with_suffix(".mg5")
    commands.write_text(f"import model {HERE / 'DMsimp_s_spin1'}\n"
                        "define p5 = g u c d s b u~ c~ d~ s~ b~\n"
                        "generate p5 p5 > xd xd~ p5 DMV=2 QCD=1 QED=0\n"
                        f"output {proc} -f\nquit\n")
    run_command([MG, commands], HERE, HERE / "logs" / f"setup_{mass}.log")
    # MG5 also invokes the converted UFO's card writer as a standalone script.
    writer = proc / "bin/internal/ufomodel/write_param_card.py"
    writer.write_text("import sys\nfrom pathlib import Path\n"
                      "if not __package__:\n"
                      "    path = Path(__file__).resolve().parent\n"
                      "    sys.path.insert(0, str(path.parent))\n"
                      "    __package__ = path.name\n\n" + writer.read_text())
    card = proc / "Cards/param_card.dat"
    param = change_param(change_param(card.read_text(), "mass", 5000001, mass), "mass", PDG, 1.)
    param, n = re.subn(r"(?mi)^(DECAY\s+5000001\s+)\S+", rf"\g<1>{width(mass):.12e}", param)
    assert n == 1
    card.write_text(param)
    card = proc / "Cards/run_card.dat"
    settings = card.read_text()
    edits = dict(nevents=NEVENTS, iseed=seed, ebeam1=6500, ebeam2=6500,
                 use_syst="False", ptj=100, etaj=4.5, dynamical_scale_choice=-1)
    keys = ("pdlabel1", "pdlabel2") if re.search(r"=\s*pdlabel1\b", settings) else ("pdlabel",)
    edits.update(dict.fromkeys(keys, "nn23lo1"))
    card.write_text(change_run(settings, edits))
    conf = proc / "Cards/me5_configuration.txt"
    config = re.sub(r"(?m)^\s*(run_mode|nb_core|automatic_html_opening)\s*=.*$", "", conf.read_text())
    conf.write_text(config + "\nrun_mode = 2\nnb_core = 4\nautomatic_html_opening = False\n")
    log = HERE / "logs" / f"generate_{mass}.log"
    run_command([proc / "bin/generate_events", "vector", "-f"], proc, log)
    return generation_results(mass, proc)


def simulate(source, run, mass, seed):
    run.mkdir(exist_ok=True)
    lhe = run / "hard.lhe"
    with gzip.open(source, "rb") as incoming, lhe.open("wb") as outgoing:
        shutil.copyfileobj(incoming, outgoing)
    with lhe.open() as stream:
        total = sum(line.strip() == "<event>" for line in stream)
    card = run / "cms_ak4.tcl"
    text = detector_card(seed).replace("add EnergyFraction {1000022} {0.0}",
                                       f"add EnergyFraction {{1000022}} {{0.0}}\n  add EnergyFraction {{{PDG}}} {{0.0}}")
    text = text.replace("module PdgCodeFilter NeutrinoFilter {",
                        f"module PdgCodeFilter NeutrinoFilter {{\n  add PdgCode {{{PDG}}}\n  add PdgCode {{-{PDG}}}")
    branches = {"Jet", "MissingET", "Electron", "Muon", "Photon", "ParticleLHEF"}
    text = re.sub(r"(?m)^(\s*add Branch \S+ )(\S+)( [^\r\n]*)$",
                  lambda match: match[0] if match[2] in branches else "", text)
    card.write_text(text)
    settings = run / "shower.cmnd"
    settings.write_text(f"""Main:numberOfEvents = {total}
Main:timesAllowErrors = 20
Beams:frameType = 4
Beams:LHEF = {lhe}
SLHA:readFrom = 0
Tune:pp = 14
Random:setSeed = on
Random:seed = {seed}
5000001:new = y1 y1 3 0 0 {mass} {width(mass)} 0.0 0.0 0.0
5000001:mayDecay = off
{PDG}:new = xd xdbar 2 0 0 1.0 0.0 0.0 0.0 0.0
{PDG}:mayDecay = off
{PDG}:isVisible = off
Next:numberShowInfo = 0
Next:numberShowProcess = 0
Next:numberShowEvent = 0
""")
    home = Path.home()
    pkg = home / "miniconda3/pkgs/pythia8-8.312-py310hd4c7fa3_305"
    env = {**os.environ, "PYTHIA8DATA": str(pkg / "share/Pythia8/xmldoc"),
           "LD_LIBRARY_PATH": f"/usr/local/root/lib:{home}/miniconda3/envs/public/lib:{pkg}/lib"}
    output = run / "events.root"
    if output.exists():
        output.rename(run / "events_previous.root")
    run_command([DELPHES / "DelphesPythia8", card, settings, output], DELPHES,
                HERE / "logs" / f"detector_{mass}.log", env)
    return output, total


def cutflow(output, total):
    fields = {"Jet": "PT Eta Phi BTag TauTag", "MissingET": "MET Phi", "Electron": "PT Eta",
              "Muon": "PT Eta", "Photon": "PT Eta", "ParticleLHEF": "PID Status"}
    columns = [f"{name}.{prop}" for name, values in fields.items() for prop in values.split()]
    labels = ("full", "met", "electron", "muon", "tau", "b", "photon", "dphi",
              "jet_pt", "jet_eta", "hem_jet", "hem_phi")
    counts = dict.fromkeys(labels, 0)
    hist = np.zeros((2, len(BIN_LOW)), dtype=int)
    with uproot.open(output) as f:
        tree = f["Delphes"]
        assert tree.num_entries == total
        for a in tree.iterate(columns, step_size=1500, library="ak", how=dict):
            ids = a["ParticleLHEF.PID"][a["ParticleLHEF.Status"] == 1]
            assert ak.all(ak.sum(ids == PDG, axis=1) == 1)
            assert ak.all(ak.sum(ids == -PDG, axis=1) == 1)
            met, phi = (ak.to_numpy(ak.firsts(a[f"MissingET.{k}"])) for k in ("MET", "Phi"))
            pt, eta, jphi = (a[f"Jet.{field}"] for field in ("PT", "Eta", "Phi"))
            order = ak.argsort(pt, ascending=False)
            lead_pt = ak.fill_none(ak.firsts(pt[order]), 0)
            lead_eta = ak.fill_none(ak.firsts(eta[order]), 99)
            dphi = abs((jphi[order][:, :4] - phi + np.pi) % (2*np.pi) - np.pi)
            hem_jet = (pt > 30) & (eta > -3) & (eta < -1.3) & (jphi > -1.57) & (jphi < -.87)
            passes = (np.ones(len(met), dtype=bool), met > 250, veto(a, "Electron", 10, 2.5),
                      veto(a, "Muon", 10, 2.4), ~ak.any((pt > 18) & (abs(eta) < 2.3) & (a["Jet.TauTag"] != 0), axis=1),
                      ~ak.any((pt > 20) & (abs(eta) < 2.4) & (a["Jet.BTag"] != 0), axis=1), veto(a, "Photon", 15, 2.5),
                      ~ak.any((pt[order][:, :4] > 30) & (dphi <= .5), axis=1), lead_pt > 100, abs(lead_eta) < 2.4,
                      ~ak.any(hem_jet, axis=1), (met >= 470) | (phi < -1.62) | (phi > -.62))
            passing = passes[0].copy()
            for name, mask in zip(labels, passes):
                passing &= ak.to_numpy(mask)
                counts[name] += int(passing.sum())
                if name in ("jet_eta", "hem_phi"):
                    indices = np.searchsorted(BIN_LOW, met[passing], side="right") - 1
                    hist[int(name == "hem_phi")] += np.bincount(indices, minlength=len(BIN_LOW))
    assert counts["full"] == total and hist[0].sum() == counts["jet_eta"] and hist[1].sum() == counts["hem_phi"]
    return counts, hist


def main():
    mass = int(sys.argv[1])
    for name in ("results", "logs"):
        (HERE / name).mkdir(exist_ok=True)
    seed = 947000 + mass
    source, cross, error = generate(mass, HERE / f"mg_{mass}", seed)
    root, total = simulate(source, HERE / f"detector_{mass}", mass, seed)
    counts, hist = cutflow(root, total)
    with (HERE / "results" / f"vector_{mass}_flow.csv").open("w", newline="") as f:
        out = csv.writer(f)
        out.writerow(["stage", "count", "generated", "cross_pb", "integration_error_pb"])
        out.writerows((stage, count, total, cross, error) for stage, count in counts.items())
    with (HERE / "results" / f"vector_{mass}_hist.csv").open("w", newline="") as f:
        out = csv.writer(f)
        out.writerow(["bin", "met_low", "count_2017", "count_2018"])
        out.writerows((i, low, hist[0, i], hist[1, i]) for i, low in enumerate(BIN_LOW))
    print(f"DONE {mass} GeV, {total} events, {cross:.6g} pb, {hist.sum(axis=1).tolist()}", flush=True)


if __name__ == "__main__":
    main()

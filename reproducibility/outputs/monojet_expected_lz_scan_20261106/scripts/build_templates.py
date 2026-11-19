import argparse
import csv
import gzip
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

import awkward as ak
import numpy as np
import uproot


HERE = Path(__file__).resolve().parent.parent
PREVIOUS = HERE.parent / "monojet_analysis_20261106"
sys.path.insert(0, str(PREVIOUS / "scripts"))
from simulate import detector_card, DELPHES


BIN_LOW = np.array([250, 280, 310, 340, 370, 400, 430, 470, 510, 550, 590, 640,
                    690, 740, 790, 840, 900, 960, 1020, 1090, 1160, 1250])
STITCH = {"loop": (100, 480), "loop_hard": (480, np.inf),
          "jet_tree": (100, 350), "jet_tree_hard": (350, np.inf)}
OBJECTS = {"Jet": "PT Eta Phi BTag TauTag", "MissingET": "MET Phi",
           "Electron": "PT Eta", "Muon": "PT Eta", "Photon": "PT Eta",
           "ParticleLHEF": "PID Status PT Mass", "Particle": "PID Status Mass"}


def record(path):
    with path.open() as stream:
        return next(csv.DictReader(stream))


def uncompress_and_read(source, lhe, mass):
    with gzip.open(source, "rb") as incoming, lhe.open("wb") as outgoing:
        shutil.copyfileobj(incoming, outgoing)
    pt, weights = [], []
    with lhe.open() as stream:
        for line in stream:
            if line.strip() != "<event>":
                continue
            header = next(stream).split()
            rows = [next(stream).split() for _ in range(int(header[0]))]
            mediator, = [p for p in rows if int(p[0]) == 9900032 and int(p[1]) == 1]
            assert abs(float(mediator[10]) - mass) < 0.001
            pt.append(np.hypot(float(mediator[6]), float(mediator[7])))
            weights.append(float(header[2]))
    assert np.allclose(weights, weights[0], rtol=1e-7) and weights[0] > 0
    return np.array(pt)


def run_detector(run, key, lhe, mass, n, seed):
    card = run / "cms_ak4.tcl"
    text = detector_card(seed)
    text = re.sub(r"(?m)^(\s*add Branch \S+ )(\S+)( [^\r\n]*)$",
                  lambda match: match[0] if match[2] in OBJECTS else "", text)
    card.write_text(text)
    settings = run / "shower.cmnd"
    settings.write_text(f"""Main:numberOfEvents = {n}
Main:timesAllowErrors = 20
Beams:frameType = 4
Beams:LHEF = {lhe}
SLHA:readFrom = 0
Tune:pp = 14
Random:setSeed = on
Random:seed = {seed}
9900032:new = Vb Vb 3 0 0 {mass} 0.0 0.0 0.0 0.0
9900032:mayDecay = off
9900032:isVisible = off
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
        attempt = 1
        while (run / f"events_attempt{attempt}.root").exists():
            attempt += 1
        output.rename(run / f"events_attempt{attempt}.root")
    with (HERE / "logs" / f"detector_{key}.log").open("w") as log:
        subprocess.run([str(DELPHES / "DelphesPythia8"), str(card), str(settings), str(output)],
                       cwd=DELPHES, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
    return output


def veto(arrays, name, pt_min, eta_max):
    return ~ak.any((arrays[f"{name}.PT"] > pt_min) & (abs(arrays[f"{name}.Eta"]) < eta_max), axis=1)


def detector_bins(output, gen_pt, mass, channel):
    columns = [f"{key}.{field}" for key, fields in OBJECTS.items() for field in fields.split()]
    all_counts = np.zeros(1 + 2*len(BIN_LOW), dtype=np.int64)
    offset = 0
    alignment = 0.0
    with uproot.open(output) as f:
        tree = f["Delphes"]
        assert tree.num_entries == len(gen_pt), (output, tree.num_entries, len(gen_pt))
        for batch in tree.iterate(columns, step_size=500, library="ak", how=dict):
            for name in ("Particle", "ParticleLHEF"):
                dark = (batch[f"{name}.PID"] == 9900032) & (batch[f"{name}.Status"] == 1)
                assert ak.all(ak.sum(dark, axis=1) == 1), (name, output)
                assert ak.all(abs(ak.firsts(batch[f"{name}.Mass"][dark]) - mass) < 0.001)
                if name == "ParticleLHEF":
                    lhe_pt = ak.to_numpy(ak.firsts(batch[f"{name}.PT"][dark]))
            met = ak.to_numpy(ak.firsts(batch["MissingET.MET"]))
            phi = ak.to_numpy(ak.firsts(batch["MissingET.Phi"]))
            jpt, jeta, jphi = (batch[f"Jet.{field}"] for field in ("PT", "Eta", "Phi"))
            order = ak.argsort(jpt, ascending=False)
            lead_pt = ak.fill_none(ak.firsts(jpt[order]), 0)
            lead_eta = ak.fill_none(ak.firsts(jeta[order]), 99)
            dphi = abs((jphi[order][:, :4] - phi + np.pi) % (2*np.pi) - np.pi)
            angular = ~ak.any((jpt[order][:, :4] > 30) & (dphi <= .5), axis=1)
            b = (jpt > 20) & (abs(jeta) < 2.4) & (batch["Jet.BTag"] != 0)
            tau = (jpt > 18) & (abs(jeta) < 2.3) & (batch["Jet.TauTag"] != 0)
            hem_jet = ((jpt > 30) & (jeta > -3) & (jeta < -1.3) & (jphi > -1.57) & (jphi < -.87))
            hem = (~ak.to_numpy(ak.any(hem_jet, axis=1))) & ((met >= 470) | (phi < -1.62) | (phi > -.62))
            selected = (met > 250) & ak.to_numpy((lead_pt > 100) & (abs(lead_eta) < 2.4) & angular
                       & ~ak.any(b | tau, axis=1) & veto(batch, "Electron", 10, 2.5)
                       & veto(batch, "Muon", 10, 2.4) & veto(batch, "Photon", 15, 2.5))
            hard_pt = gen_pt[offset:offset+len(met)]
            alignment = max(alignment, float(np.max(abs(lhe_pt-hard_pt))))
            lo, hi = STITCH[channel]
            selected &= (hard_pt >= lo) & (hard_pt < hi)
            category = np.zeros(len(met), dtype=np.int64)
            bin_idx = np.searchsorted(BIN_LOW, met[selected], side="right") - 1
            category[selected] = 1 + 2*bin_idx + hem[selected]
            all_counts += np.bincount(category, minlength=len(all_counts))
            offset += len(met)
    assert alignment < 0.005 and offset == len(gen_pt) and all_counts.sum() == offset
    return all_counts, alignment


def process(path):
    row = record(path)
    key, channel, mass = row["run"], row["channel"], float(row["mass_GeV"])
    run = HERE / "detector" / key
    run.mkdir(exist_ok=True)
    source = HERE / "production" / key / "Events" / key / "unweighted_events.lhe.gz"
    lhe = run / "hard.lhe"
    gen_pt = uncompress_and_read(source, lhe, mass)
    seed = 970000 + 10*int(key.rsplit("_m", 1)[1]) + list(STITCH).index(channel)
    output = run_detector(run, key, lhe, mass, len(gen_pt), seed)
    counts, alignment = detector_bins(output, gen_pt, mass, channel)
    destination = HERE / "templates" / f"{key}.npz"
    np.savez_compressed(destination, counts=counts, mass=mass, cross=float(row["cross_pb"]),
                        cross_error=float(row["error_pb"]), channel=channel, alignment=alignment)
    return key, len(gen_pt), int(counts[1:].sum()), alignment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    (HERE / "templates").mkdir(exist_ok=True)
    jobs = {}
    processed = {p.stem for p in (HERE / "templates").glob("*.npz")}
    failed = set()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        while len(processed | failed) < 44:
            free = args.workers - len(jobs)
            pending = [p for p in sorted((HERE / "results").glob("*_m*.csv"))
                       if p.stem not in processed | failed | set(jobs.values())]
            for path in pending[:free]:
                jobs[pool.submit(process, path)] = path.stem
            if jobs:
                done, _ = wait(jobs, timeout=8, return_when=FIRST_COMPLETED)
                for job in done:
                    key = jobs.pop(job)
                    try:
                        print("DONE", job.result(), flush=True)
                        processed.add(key)
                    except Exception as exc:
                        print("ERROR", key, repr(exc), flush=True)
                        failed.add(key)
            else:
                time.sleep(5)
    print("COMPLETE", len(processed), "FAILED", sorted(failed), flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

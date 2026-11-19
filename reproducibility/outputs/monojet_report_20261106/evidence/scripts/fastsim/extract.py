import argparse
import csv
import gzip
import json
import math
import random
from pathlib import Path

import awkward as ak
import uproot

from simulate import HERE, SAMPLES, source_events


DARK = {9900032, 100051, 100052}


def objects(arrays, entry, prefix, columns):
    return list(zip(*(ak.to_list(arrays[f"{prefix}.{key}"][entry]) for key in columns), strict=True))


def delta_phi(left, right):
    return abs(math.remainder(left - right, 2 * math.pi))


def vector(objects):
    px = sum(pt * math.cos(phi) for pt, phi in objects)
    py = sum(pt * math.sin(phi) for pt, phi in objects)
    return math.hypot(px, py), math.atan2(py, px)


def hadron_level(arrays, i, prefix, met_prefix):
    jets = sorted(objects(arrays, i, prefix, ("PT", "Eta", "Phi")), reverse=True)
    met, phi = objects(arrays, i, met_prefix, ("MET", "Phi"))[0]
    lead = jets[0] if jets else (0, 0, 0)
    accepted = [(pt, eta, jphi) for pt, eta, jphi in jets if pt > 30 and abs(eta) < 4.7]
    return dict(met=met, met_phi=phi, j1_pt=lead[0], j1_eta=lead[1], j1_phi=lead[2],
                j2_pt=accepted[1][0] if len(accepted) > 1 else 0,
                njets=len(accepted), dphi_j1=delta_phi(phi, lead[2]),
                min_dphi=min((delta_phi(phi, jphi) for pt, _, jphi in jets[:4] if pt > 30), default=math.pi),
                balance=lead[0] / met if met else 0)


def truth_rows(path):
    with gzip.open(path, "rt") as stream:
        for line in stream:
            if line.strip() != "<event>":
                continue
            fields = next(stream).split()
            particles = [next(stream).split() for _ in range(int(fields[0]))]
            final = [(int(p[0]), *(float(x) for x in p[6:10])) for p in particles if int(p[1]) == 1]
            dark = [p for p in final if abs(p[0]) in DARK]
            partons = [p for p in final if abs(p[0]) <= 5 or p[0] == 21]
            assert len(partons) == 1 and {abs(p[0]) for p in dark} in ({9900032}, {100051, 100052})
            px = sum(p[1] for p in dark)
            py = sum(p[2] for p in dark)
            pid, jx, jy, jz, _ = partons[0]
            pt = math.hypot(jx, jy)
            assert math.hypot(px + jx, py + jy) < 1e-5
            yield dict(weight=float(fields[2]), gen_met=math.hypot(px, py), gen_j1_pt=pt,
                       gen_j1_eta=math.asinh(jz / pt), gen_jet_pid=pid), dark


def extract(sample, test):
    name = sample + ("_test" if test else "")
    source, cross, error, energy, ptmin = source_events(sample)
    root = HERE / "detector" / name / "events.root"
    destination = HERE / "results" / "events"
    destination.mkdir(parents=True, exist_ok=True)
    branches = {
        "Jet": "PT Eta Phi BTag TauTag ChargedEnergyFraction NeutralEnergyFraction Flavor",
        "GenJet": "PT Eta Phi", "MissingET": "MET Phi", "GenMissingET": "MET Phi",
        "Electron": "PT Eta", "Muon": "PT Eta", "Photon": "PT Eta", "FatJet": "PT Eta",
        "Particle": "PID Status PT Phi", "ParticleLHEF": "PID Status PT Phi",
    }
    truth = list(truth_rows(source))
    assert all(item[0]["weight"] > 0 for item in truth)
    results = []
    max_lhe_difference = 0.0
    tags = random.Random(962000 + list(SAMPLES).index(sample))
    with uproot.open(root) as f:
        tree = f["Delphes"]
        if tree.num_entries != (min(40, len(truth)) if test else len(truth)):
            raise ValueError(f"{name}: {tree.num_entries} reconstructed entries, {len(truth)} LHE entries")
        columns = [f"{key}.{field}" for key, fields in branches.items() for field in fields.split()]
        for batch in tree.iterate(columns, step_size=500, library="ak", how=dict):
            for i in range(len(batch["MissingET.MET"])):
                row, dark = truth[len(results)]
                expected_ids = {abs(p[0]) for p in dark}
                for prefix in ("Particle", "ParticleLHEF"):
                    invisible = [(abs(pid), pt, phi) for pid, status, pt, phi in
                                 objects(batch, i, prefix, ("PID", "Status", "PT", "Phi"))
                                 if status == 1 and abs(pid) in DARK]
                    if len(invisible) != len(dark) or {p[0] for p in invisible} != expected_ids:
                        raise ValueError(f"{name} event {len(results)} lost invisible particles in {prefix}")
                    invisible_pt, _ = vector([(pt, phi) for _, pt, phi in invisible])
                    if prefix == "ParticleLHEF":
                        max_lhe_difference = max(max_lhe_difference, abs(invisible_pt - row["gen_met"]))
                    else:
                        row["shower_invisible_pt"] = invisible_pt
                row.update({f"shower_{key}": value for key, value in
                            hadron_level(batch, i, "GenJet", "GenMissingET").items()})
                row.update(hadron_level(batch, i, "Jet", "MissingET"))
                jets = sorted(objects(batch, i, "Jet", tuple(branches["Jet"].split())), reverse=True)
                row["b_veto"] = int(not any(pt > 20 and abs(eta) < 2.4 and b for pt, eta, _, b, *_ in jets))
                b_probability = [0.85 if abs(flavor) == 5 else 0.10 for pt, eta, *_, flavor in jets
                                 if pt > 20 and abs(eta) < 2.4]
                row["b_veto_run3"] = int(tags.random() < math.prod(1 - p for p in b_probability))
                for run, pt_min, eta_max in (("run2", 18, 2.3), ("run3", 20, 2.5)):
                    row[f"tau_veto_{run}"] = int(not any(pt > pt_min and abs(eta) < eta_max and tau
                                                         for pt, eta, _, _, tau, *_ in jets))
                row["jet_quality"] = int(bool(jets) and jets[0][-3] > 0.1 and jets[0][-2] < 0.8)
                for prefix, ptmin_obj, etamax in (("Electron", 10, 2.5), ("Muon", 10, 2.4), ("Photon", 15, 2.5)):
                    row[f"{prefix.lower()}_veto"] = int(not any(pt > ptmin_obj and abs(eta) < etamax
                                                              for pt, eta in objects(batch, i, prefix, ("PT", "Eta"))))
                row["photon_veto_run3"] = int(not any(pt > 20 and abs(eta) < 2.5
                                                     for pt, eta in objects(batch, i, "Photon", ("PT", "Eta"))))
                row["ak8_candidate"] = int(any(pt > 250 and abs(eta) < 2.4
                                              for pt, eta in objects(batch, i, "FatJet", ("PT", "Eta"))))
                row["hem_jet_veto"] = int(not any(pt > 30 and -3 < eta < -1.3 and -1.57 < phi < -0.87
                                                 for pt, eta, phi, *_ in jets))
                results.append(row)
    if max_lhe_difference > 0.005:
        raise ValueError(f"{name}: LHE alignment failed by {max_lhe_difference} GeV")
    with gzip.open(destination / f"{name}.csv.gz", "wt", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    (destination / f"{name}.json").write_text(json.dumps({
        "sample": sample, "energy_TeV": energy, "pt_gen_GeV": ptmin, "sigma_fb": cross,
        "integration_error_fb": error, "events": len(results), "max_lhe_alignment_error_GeV": max_lhe_difference,
        "source": str(source), "root": str(root),
    }, indent=2) + "\n")
    print(name, len(results), cross, max_lhe_difference, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sample", choices=SAMPLES)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    extract(args.sample, args.test)

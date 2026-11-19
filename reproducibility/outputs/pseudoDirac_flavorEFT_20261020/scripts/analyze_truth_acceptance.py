#!/usr/bin/env python3
"""Truth-level acceptance and a monojet model-independent-limit proxy."""

from __future__ import annotations

import csv
import gzip
import math
from pathlib import Path


ROOT = Path("/home/cms/phenomenology/PseudoDiracFlavorEFT_20261020")
RESULTS = ROOT / "results"
PROCS = {
    "monojet": ROOT / "proc_monojet",
    "monophoton": ROOT / "proc_monophoton",
    "monozll": ROOT / "proc_monozll",
}
ATLAS_MONOJET_LIMIT_FB = {
    200: 736.0, 250: 296.0, 300: 150.0, 350: 86.0,
    400: 52.0, 500: 21.0, 600: 10.0, 700: 4.1,
    800: 2.1, 900: 1.2, 1000: 1.3, 1100: 0.5, 1200: 0.3,
}


def events_from_lhe(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", errors="replace") as handle:
        inside = False
        particles = []
        header_seen = False
        for raw in handle:
            line = raw.strip()
            if line == "<event>":
                inside = True
                particles = []
                header_seen = False
                continue
            if line == "</event>":
                if particles:
                    yield particles
                inside = False
                continue
            if not inside or not line or line.startswith("#"):
                continue
            if not header_seen:
                header_seen = True
                continue
            fields = line.split()
            if len(fields) < 10:
                continue
            pid, status = int(fields[0]), int(fields[1])
            if status != 1:
                continue
            px, py, pz, energy = map(float, fields[6:10])
            particles.append((pid, px, py, pz, energy))


def pt(p):
    return math.hypot(p[1], p[2])


def eta(p):
    momentum = math.sqrt(p[1]**2 + p[2]**2 + p[3]**2)
    if momentum == abs(p[3]):
        return math.copysign(99.0, p[3])
    return 0.5 * math.log((momentum + p[3]) / (momentum - p[3]))


def phi_xy(x, y):
    return math.atan2(y, x)


def dphi(a, b):
    return abs((a - b + math.pi) % (2.0 * math.pi) - math.pi)


def dr(p1, p2):
    return math.hypot(eta(p1) - eta(p2),
                      dphi(phi_xy(p1[1], p1[2]), phi_xy(p2[1], p2[2])))


def inv_mass(p1, p2):
    e = p1[4] + p2[4]
    px, py, pz = p1[1] + p2[1], p1[2] + p2[2], p1[3] + p2[3]
    return math.sqrt(max(0.0, e*e - px*px - py*py - pz*pz))


def missing_xy(parts):
    invisible = [p for p in parts if abs(p[0]) in (100051, 100052)]
    return sum(p[1] for p in invisible), sum(p[2] for p in invisible)


def mono_z_pass(parts):
    leptons = [p for p in parts if abs(p[0]) in (11, 13)]
    if len(leptons) != 2 or leptons[0][0] != -leptons[1][0]:
        return False
    leptons.sort(key=pt, reverse=True)
    if pt(leptons[0]) <= 25.0 or pt(leptons[1]) <= 20.0:
        return False
    if any(abs(eta(p)) >= (2.5 if abs(p[0]) == 11 else 2.4) for p in leptons):
        return False
    if abs(inv_mass(*leptons) - 91.1876) >= 15.0:
        return False
    zpx = leptons[0][1] + leptons[1][1]
    zpy = leptons[0][2] + leptons[1][2]
    zpt = math.hypot(zpx, zpy)
    if zpt <= 60.0:
        return False
    mx, my = missing_xy(parts)
    met = math.hypot(mx, my)
    if met <= 100.0:
        return False
    if dphi(phi_xy(zpx, zpy), phi_xy(mx, my)) <= 2.6:
        return False
    if abs(met - zpt) / zpt >= 0.4:
        return False
    return dr(*leptons) < 1.8


def find_lhe(proc, run_name):
    directory = proc / "Events" / run_name
    candidates = list(directory.glob("*.lhe.gz")) + list(directory.glob("*.lhe"))
    if not candidates:
        raise FileNotFoundError(f"no LHE for {run_name}")
    return candidates[0]


cross_rows = list(csv.DictReader((RESULTS / "pilot_channel_cross_sections.csv").open()))
output = []
for row in cross_rows:
    channel = row["channel"]
    if channel not in PROCS:
        continue
    sigma_fb = float(row["cross_section_pb"]) * 1000.0
    parts = list(events_from_lhe(find_lhe(PROCS[channel], row["run_name"])))
    n_total = len(parts)
    if channel == "monojet":
        for threshold, limit in ATLAS_MONOJET_LIMIT_FB.items():
            passed = 0
            for event in parts:
                mx, my = missing_xy(event)
                if math.hypot(mx, my) > threshold:
                    passed += 1
            acc = passed / n_total
            visible = sigma_fb * acc
            output.append(dict(
                benchmark=row["benchmark"], channel=channel,
                selection=f"truth_MET_gt_{threshold}_GeV", passed=passed,
                total=n_total, acceptance=acc, visible_xsec_fb=visible,
                events_at_137fb=visible*137.0, reference_limit_fb=limit,
                signal_to_limit=visible/limit,
            ))
    elif channel == "monophoton":
        for threshold in (150, 200, 250, 300, 400, 500):
            passed = sum(any(abs(p[0]) == 22 and pt(p) > threshold for p in event)
                         for event in parts)
            acc = passed / n_total
            visible = sigma_fb * acc
            output.append(dict(
                benchmark=row["benchmark"], channel=channel,
                selection=f"truth_photon_pt_gt_{threshold}_GeV", passed=passed,
                total=n_total, acceptance=acc, visible_xsec_fb=visible,
                events_at_137fb=visible*137.0, reference_limit_fb="",
                signal_to_limit="",
            ))
    else:
        passed = sum(mono_z_pass(event) for event in parts)
        acc = passed / n_total
        visible = sigma_fb * acc
        output.append(dict(
            benchmark=row["benchmark"], channel=channel,
            selection="CMS_EXO_19_003_truth_kinematics", passed=passed,
            total=n_total, acceptance=acc, visible_xsec_fb=visible,
            events_at_137fb=visible*137.0, reference_limit_fb="",
            signal_to_limit="",
        ))

fields = list(output[0])
with (RESULTS / "truth_acceptance_and_sensitivity.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(output)

# One concise row per benchmark for the monojet screening metric.
best = {}
for row in output:
    if row["channel"] != "monojet" or row["passed"] < 20:
        continue
    name = row["benchmark"]
    if name not in best or row["signal_to_limit"] > best[name]["signal_to_limit"]:
        best[name] = row
with (RESULTS / "monojet_best_bin_proxy.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(best.values())

for name, row in best.items():
    print(name, row["selection"], f"R={row['signal_to_limit']:.4g}",
          f"N={row['passed']}/{row['total']}")

#!/usr/bin/env python3
"""Reproduction driver for the v2 (corrected-kappa) ttbar+MET analysis package.

    python3 run.py --check      # verify every shipped file against manifest.json (sha256)
    python3 run.py --widths     # re-derive widths_v2.csv from band_v2.csv and compare
    python3 run.py --manifest   # regenerate manifest.json (maintainer use)

Only the standard library is required for --check and --widths.
The steps that need external software are listed in README.md.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MQ = {"u": 0.0022, "d": 0.0047, "s": 0.093, "c": 1.27, "b": 4.18, "t": 172.0}
AS = 0.12
NLO = 1.0 + AS / math.pi


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cmd_check():
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = 0
    for e in man:
        p = os.path.join(HERE, e["path"])
        if not os.path.exists(p):
            print("MISSING", e["path"]); bad += 1; continue
        got = sha256(p)
        if got != e["sha256"]:
            print("DIFF   ", e["path"], got[:12], "!=", e["sha256"][:12]); bad += 1
    print("%d files checked, %d mismatch" % (len(man), bad))
    return 1 if bad else 0


def cmd_manifest():
    rows = []
    for root, _, files in os.walk(HERE):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, HERE)
            if rel == "manifest.json" or rel.startswith(".") or "__pycache__" in rel or rel.endswith(".pyc"):
                continue
            rows.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha256(p)})
    rows.sort(key=lambda r: r["path"])
    json.dump(rows, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
    print("wrote manifest.json with", len(rows), "entries")


def phase(beta2):
    if beta2 <= 0:
        return 0.0
    b = math.sqrt(beta2)
    return b * (3.0 - beta2) / 2.0


def widths(mv, gt, m1, gchi):
    m2 = m1 + 0.001
    w = {"chi": (gchi / 2.0) ** 2 * mv / (12 * math.pi) * phase(1 - ((m1 + m2) / mv) ** 2)}
    for q, mq in MQ.items():
        gq = gt * mq / 172.0
        w[q] = 3.0 * gq * gq * mv / (12 * math.pi) * phase(1 - (2 * mq / mv) ** 2) * NLO
    return w, sum(w.values())


def cmd_widths():
    band = list(csv.DictReader(open(os.path.join(HERE, "inputs", "band_v2.csv"))))
    ref = {(round(float(r["MV"]), 1), round(float(r["gt"]), 3)): r
           for r in csv.DictReader(open(os.path.join(HERE, "inputs", "widths_v2.csv")))}
    worst_tot = worst_br_rel = worst_br_abs = 0.0
    n = 0
    for r in band:
        mv, gt = float(r["MV"]), float(r["gt"])
        m1, gc = float(r["mchi"]), float(r["gchi"])
        w, tot = widths(mv, gt, m1, gc)
        br = w["chi"] / tot
        e = ref.get((round(mv, 1), round(gt, 3)))
        if e is None:
            continue
        et, eb = float(e["G_tot"]), float(e["BRinv"])
        worst_tot = max(worst_tot, abs(tot - et) / et)
        worst_br_rel = max(worst_br_rel, abs(br - eb) / eb)
        worst_br_abs = max(worst_br_abs, abs(br - eb))
        n += 1
    print("%d points compared" % n)
    print("max |dGamma/Gamma| = %.2e" % worst_tot)
    print("max |dBR|          = %.2e  (relative %.2e)" % (worst_br_abs, worst_br_rel))
    # BR is stored with 6 decimals; compare absolutely at that precision
    ok = worst_tot < 1e-3 and worst_br_abs < 1e-6
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--widths", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(cmd_check())
    if a.widths:
        sys.exit(cmd_widths())
    if a.manifest:
        cmd_manifest()
    if not (a.check or a.widths or a.manifest):
        ap.print_help()

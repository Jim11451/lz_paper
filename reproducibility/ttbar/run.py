#!/usr/bin/env python3
"""Reproducible package for the ttbar+MET paper (CMS EXO-22-014 recast).

Stages
------
verify  : check every archived input against manifest.json (sha256)
limits  : rebuild the pyhf workspace from the HEPData tables and refit the
          19-channel (11 SR + 8 CR) model, then compare mu95 with expected.json
stamp   : rewrite manifest.json from the current files (maintenance only)

Usage
-----
    python run.py verify
    python run.py limits
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
MANIFEST = os.path.join(HERE, "manifest.json")
EXPECTED = os.path.join(HERE, "expected", "expected.json")
CODE = os.path.join(HERE, "code")


def _hash(path, normalization="lf"):
    payload = open(path, "rb").read()
    if normalization == "lf":
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def verify():
    entries = json.load(open(MANIFEST))
    bad = []
    for item in entries:
        path = os.path.join(HERE, item["path"])
        if not os.path.isfile(path):
            bad.append((item["path"], "missing"))
            continue
        if _hash(path, item.get("normalization", "lf")) != item["sha256"]:
            bad.append((item["path"], "changed"))
    if bad:
        for p, why in bad:
            print("  %-8s %s" % (why, p))
        raise SystemExit("verify failed: %d/%d files" % (len(bad), len(entries)))
    print("Verified %d archived source and input files." % len(entries))


def stamp():
    entries = []
    for root, _, files in os.walk(HERE):
        if os.path.relpath(root, HERE).split(os.sep)[0] in ("build", "expected", ".git"):
            continue
        for f in sorted(files):
            if f in ("manifest.json", "run.py") or f.endswith(".pyc"):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, HERE)
            entries.append({"path": rel,
                            "bytes": os.path.getsize(full),
                            "normalization": "lf",
                            "sha256": _hash(full)})
    json.dump(entries, open(MANIFEST, "w"), indent=1)
    print("stamped %d entries" % len(entries))


def limits():
    os.makedirs(BUILD, exist_ok=True)
    for script in ("build_workspace.py", "fit_cr.py"):
        subprocess.run([sys.executable, os.path.join(CODE, script)], check=True)
    got = json.load(open(os.path.join(BUILD, "phase12_results.json")))
    exp = json.load(open(EXPECTED))
    fields = ("muhat", "m95_obs", "m95_exp")
    ok = True
    print("%-6s %-14s %10s %10s" % ("case", "quantity", "reproduced", "archived"))
    for case in ("withCR", "noCR"):
        for f in fields:
            a, b = got[case][f], exp[case][f]
            good = abs(a - b) <= 2e-3
            ok &= good
            print("%-6s %-14s %10.5f %10.5f %s" % (case, f, a, b, "" if good else "  <-- MISMATCH"))
    if not ok:
        raise SystemExit("limits do not match the archived values")
    print("OK: 19-channel (11 SR + 8 CR) and 11-SR-only limits reproduced.")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    {"verify": verify, "limits": limits, "stamp": stamp}.get(
        stage, lambda: (_ for _ in ()).throw(SystemExit(__doc__)))()

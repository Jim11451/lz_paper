"""PHASE 12 -- simultaneous fit with the control regions (pyhf).

Model
-----
Channels : 11 signal regions + 10 control regions (all from HEPData ins2919645).
Samples  : the ten background processes, each with ONE unconstrained
           normalisation factor shared across all channels (this is what the
           CRs constrain), plus the benchmark signal with normalisation mu.
Data     : the observed counts of each table.

Outputs
-------
workspace.json           the pyhf workspace used here
phase12_results.json     muhat, kappa hats, CLs crossings (obs / exp)
"""
import glob
import json
import os
import re

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
HEP = os.path.join(BASE, "inputs", "hepdata")
BUILD = os.path.join(BASE, "build")
os.makedirs(BUILD, exist_ok=True)

PROC_KEYS = ["tt1l", "tt2l", "Znn", "Zll", "Wjets", "singlet", "VV", "QCD", "ttV", "other"]
# only the backgrounds that a control region actually constrains are floated;
# the rest (VV, ttV, other, single top) stay at their nominal yield
NORM_FREE = ["tt1l", "tt2l", "Wjets", "QCD", "Zll", "Znn"]


def classify(raw):
    s = raw.lower()
    if "gamma" in s:
        return "Zll"
    if "vv" in s:
        return "VV"
    if "qcd" in s:
        return "QCD"
    if "(1l)" in s:
        return "tt1l"
    if "(2l)" in s:
        return "tt2l"
    if "t}v" in s:
        return "ttV"
    if "nu" in s:
        return "Znn"
    if "jets" in s:
        return "Wjets"
    if "single" in s:
        return "singlet"
    return "other"


def read(fn):
    d = yaml.safe_load(open(fn))
    iv = d["independent_variables"][0]["values"]
    nb = len(iv)
    out = {k: np.zeros(nb) for k in PROC_KEYS}
    sig = np.zeros(nb)
    dat = np.zeros(nb)
    for dv in d["dependent_variables"]:
        q = {x["name"]: x["value"] for x in dv.get("qualifiers", [])}
        raw = str(q.get("Process", ""))

        def f(x):
            try:
                return float(x)
            except (TypeError, ValueError):
                return 0.0
        v = np.array([f(x["value"]) for x in dv["values"]])
        if "Data" in raw:
            dat = v
        elif raw.startswith("Signal"):
            sig = v
        elif "Background" in raw:
            continue
        else:
            out[classify(raw)] += v
    return out, sig, dat


def main():
    srs, crs = {}, {}
    for f in sorted(glob.glob(os.path.join(HEP, "postfit_*.yaml"))):
        nm = os.path.basename(f)[len("postfit_"):-len(".yaml")]
        comps, sig, dat = read(f)
        is_cr = nm.endswith("CR") or re.search(r"(QR|TR|WR|ZR)$", nm)
        is_sr = nm.endswith("SR") or nm.startswith("NN_distribution_DL_ttDM")
        if is_sr and not is_cr:
            srs[nm] = (comps, sig, dat)
        elif is_cr:
            crs[nm] = (comps, sig, dat)
        else:
            print("  skip (different signal model):", nm)
    print("SR: %d  CR: %d" % (len(srs), len(crs)))

    channels, samples, observations = [], [], []
    for nm, (comps, sig, dat) in list(srs.items()) + list(crs.items()):
        nb = len(dat)
        ch = {"name": nm, "samples": []}
        for k in PROC_KEYS:
            mods = ([{"name": "k_" + k, "type": "normfactor", "data": None}]
                    if k in NORM_FREE else [])
            ch["samples"].append({"name": k, "data": comps[k].tolist(), "modifiers": mods})
        ch["samples"].append({"name": "signal", "data": sig.tolist(),
                              "modifiers": [{"name": "mu", "type": "normfactor",
                                             "data": None}]})
        channels.append(ch)
        observations.append({"name": nm, "data": dat.tolist()})

    ws = {
        "channels": channels,
        "observations": observations,
        "measurements": [{
            "name": "Measurement",
            "config": {
                "poi": "mu",
                "parameters": [{"name": "mu", "bounds": [[0.0, 10.0]],
                                "inits": [1.0]}] +
                              [{"name": "k_" + k, "bounds": [[0.2, 5.0]],
                                "inits": [1.0]} for k in NORM_FREE],
            },
        }],
        "version": "1.0.0",
    }
    p = os.path.join(BUILD, "workspace.json")
    json.dump(ws, open(p, "w"))
    print("wrote", p)

    # same model without the control regions (for the comparison)
    keep = set(srs)
    ws2 = dict(ws)
    ws2["channels"] = [c for c in ws["channels"] if c["name"] in keep]
    ws2["observations"] = [o for o in ws["observations"] if o["name"] in keep]
    p2 = os.path.join(BUILD, "workspace_nocr.json")
    json.dump(ws2, open(p2, "w"))
    print("wrote", p2)


if __name__ == "__main__":
    main()

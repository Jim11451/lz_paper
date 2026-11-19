"""PHASE 2 / Step 2 -- run the existing asymptotic CLs code on the official
CMS template and store the 95% CL signal-strength limits.

  expected : Asimov dataset n_i = b_i
  observed : n_i = data_i

Our implementation is ttDM/sys_likelihood.py (per-bin Gaussian background
nuisance, profiled by bisection, Cowan- asymptotic CLs).  Two variants are
evaluated so that the convention in the p_b term is visible:

  as_is   : p_b = Phi(+sqrt(q_b))          <- what sys_likelihood.py does today
  fixed   : p_b = Phi(-sqrt(q_b))          <- CLs as defined in CMS/ATLAS (pb = 1-Phi)

Both are reported; the pyhf comparison (run_pyhf.py) decides which one is right.
"""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/home/yy/.hermes/cache/scratch/ttDM")
import sys_likelihood as sl   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SQ2 = np.sqrt(2.0)


def load():
    rows = list(csv.DictReader(open(os.path.join(HERE, "inputs_AH0l2bSR.csv"))))
    s = np.array([float(r["s"]) for r in rows])
    b = np.array([float(r["b"]) for r in rows])
    sb = np.array([float(r["sb"]) for r in rows])
    n = np.array([float(r["n"]) for r in rows])
    return s, b, sb, n


def cls_fixed(mu, n, s, b0, sb, muhat=None, nllhat=None):
    """Same likelihood as sys_likelihood.cls but with p_b = Phi(-sqrt(q_b))."""
    from math import erf, sqrt
    if muhat is None:
        muhat = sl.fit_mu(n, s, b0, sb)
        nllhat = sl.nll(n, s, b0, sb, muhat)
    qmu = max(0.0, sl.nll(n, s, b0, sb, mu) - nllhat) if mu > muhat else 0.0
    qb = max(0.0, sl.nll(n, s, b0, sb, 0.0) - nllhat)
    p_mu = 1.0 - 0.5 * (1.0 + erf(sqrt(qmu) / SQ2))     # 1 - Phi(+sqrt(qmu))
    p_b = 0.5 * (1.0 + erf(-sqrt(qb) / SQ2))            # Phi(-sqrt(qb))
    return p_mu / max(p_b, 1e-12)


def mu95_fixed(n, s, b0, sb):
    muhat = sl.fit_mu(n, s, b0, sb)
    nllhat = sl.nll(n, s, b0, sb, muhat)
    lo, hi = 1e-5, max(1.0, 2 * muhat + 1)
    while cls_fixed(hi, n, s, b0, sb, muhat, nllhat) > 0.05:
        hi *= 2
        if hi > 1e5:
            return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if cls_fixed(mid, n, s, b0, sb, muhat, nllhat) > 0.05:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    s, b, sb, n = load()
    res = {"bins": len(s), "S_total": float(s.sum()), "B_total": float(b.sum()),
           "data_total": float(n.sum())}
    for tag, nd in (("exp", b), ("obs", n)):
        a = sl.mu95(nd, s, b, sb, True)
        f = mu95_fixed(nd, s, b, sb)
        a0 = sl.mu95(nd, s, b, sb, False)
        f0 = None
        # stat-only variant of the fixed convention
        muhat = sl.fit_mu(nd, s, b, np.zeros_like(sb))
        nllhat = sl.nll(nd, s, b, np.zeros_like(sb), muhat)
        lo, hi = 1e-5, max(1.0, 2 * muhat + 1)
        sbb = np.zeros_like(sb)
        while cls_fixed(hi, nd, s, b, sbb, muhat, nllhat) > 0.05:
            hi *= 2
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if cls_fixed(mid, nd, s, b, sbb, muhat, nllhat) > 0.05:
                lo = mid
            else:
                hi = mid
        f0 = 0.5 * (lo + hi)
        muh = sl.fit_mu(nd, s, b, sb)
        res[tag] = {
            "muhat": float(muh),
            "mu95_as_is_syst": a, "mu95_as_is_stat": a0,
            "mu95_fixed_syst": f, "mu95_fixed_stat": f0,
        }
        print("%s  muhat=%.4f  as-is: %.4f (stat %.4f)   fixed: %.4f (stat %.4f)"
              % (tag, muh, a or -1, a0 or -1, f or -1, f0 or -1))

    json.dump(res, open(os.path.join(HERE, "our_results.json"), "w"), indent=1)
    meta = json.load(open(os.path.join(HERE, "template_meta.json")))
    for tag in ("exp", "obs"):
        # as_is is the convention validated against pyhf (see PHASE_2_REPORT.md 4.4)
        print("%s  -> sigma_UL(as_is) = %.5f pb" % (tag, res[tag]["mu95_as_is_syst"] * meta["sigma_ref_pb"]))


if __name__ == "__main__":
    main()

"""PHASE 12 -- CR-constrained simultaneous fit (pyhf model + iminuit profiler).

The likelihood is pyhf's (Poisson over all SR and CR bins, one normfactor per
floated background); the profiling and the CLs definition are the same as in
cmsrepro/phase3/sys_likelihood.py:

    q_mu = -2lnL(mu fixed) + 2lnL(hat)      (q_mu = 0 if mu < muhat)
    q_b  = -2lnL(mu = 0)   + 2lnL(hat)
    CLs  = (1 - Phi(sqrt(q_mu))) / Phi(sqrt(q_b))

Run with:
    /home/yy/lz-event/phenomenology/tools/pyhfenv/bin/python cmsrepro/phase12/fit_cr.py
"""
import json
import math
import os

import numpy as np
import pyhf
from iminuit import Minuit

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, "..", "build"))
SQ2 = math.sqrt(2.0)
PHI = lambda x: 0.5 * math.erfc(-x / SQ2)   # noqa: E731


def load(fn):
    ws = json.load(open(os.path.join(BUILD, fn)))
    model = pyhf.Model({"channels": ws["channels"]}, poi_name="mu")
    # pyhf re-orders the channels internally -> align the observations to it
    obs = {o["name"]: np.asarray(o["data"], float) for o in ws["observations"]}
    data = np.concatenate([obs[c] for c in model.config.channels])
    return model, data, ws


KAPPA_SIGMA = 0.10          # Gaussian prior on every floated background normalisation


def profile(model, data, mu=None):
    order = model.config.par_order
    knorm = [i for i, p in enumerate(order) if p.startswith("k_")]
    init = np.ones(len(order))
    lim = [(0.0, 10.0) if p == "mu" else (0.3, 3.0) for p in order]

    def f(*pars):
        v = pyhf.infer.mle.twice_nll(np.asarray(pars, float),
                                     pyhf.tensorlib.astensor(data), model)
        v = float(np.ravel(np.asarray(v, float))[0])
        pen = sum(((pars[i] - 1.0) / KAPPA_SIGMA) ** 2 for i in knorm)
        return v + pen
    m = Minuit(f, *init)
    m.errordef = Minuit.LIKELIHOOD
    for i, b in enumerate(lim):
        m.limits[i] = b
    if mu is not None:
        i = order.index("mu")
        m.values[i] = mu
        m.fixed[i] = True
    m.migrad()
    return m


def cls(mu, model, data, m0):
    order = model.config.par_order
    muhat = m0.values[order.index("mu")]
    nll0 = m0.fval
    qmu = 0.0 if mu <= muhat else max(0.0, profile(model, data, mu=mu).fval - nll0)
    qb = max(0.0, profile(model, data, mu=0.0).fval - nll0)
    return (1.0 - PHI(math.sqrt(qmu))) / max(PHI(math.sqrt(qb)), 1e-12)


def crossing(model, data, m0, hi=2.0, tol=0.01):
    if cls(0.0, model, data, m0) < 0.05:
        return 0.0
    while cls(hi, model, data, m0) > 0.05 and hi < 40:
        hi *= 1.5
    a, b = 0.0, hi
    while b - a > tol:
        mid = 0.5 * (a + b)
        if cls(mid, model, data, m0) > 0.05:
            a = mid
        else:
            b = mid
    return 0.5 * (a + b)


def main():
    pyhf.set_backend("numpy")
    out = {}
    for tag, fn in (("withCR", "workspace.json"), ("noCR", "workspace_nocr.json")):
        model, data, ws = load(fn)
        order = model.config.par_order
        m0 = profile(model, data)
        muhat = float(m0.values[order.index("mu")])
        kap = {p.replace("k_", ""): float(m0.values[i])
               for i, p in enumerate(order) if p.startswith("k_")}
        q0 = max(0.0, profile(model, data, mu=0.0).fval - m0.fval)
        m95o = crossing(model, data, m0)
        b_pars = np.array([0.0 if p == "mu" else 1.0 for p in order])
        asimov = np.asarray(model.expected_data(b_pars, include_auxdata=True), float)
        ma = profile(model, asimov)
        m95e = crossing(model, asimov, ma)
        print("\n=== %s  (%d channels, %d bins)" % (tag, len(ws["channels"]), len(data)))
        print("  muhat = %.4f    q0(mu=0) = %.2f  ->  Z = %.2f sigma"
              % (muhat, q0, math.sqrt(q0)))
        print("  mu95 obs = %.4f    exp = %.4f" % (m95o, m95e))
        print("  kappa: " + ", ".join("%s=%.3f" % (k, v) for k, v in sorted(kap.items())))
        out[tag] = dict(muhat=muhat, q0=q0, z=math.sqrt(q0), m95_obs=m95o, m95_exp=m95e,
                        kappas=kap, n_channels=len(ws["channels"]))
    out["cms"] = dict(m95_obs_pb=0.53209, m95_exp_pb=0.29472, sigma_ref_pb=1.06241,
                      m95_obs=0.53209 / 1.06241, m95_exp=0.29472 / 1.06241)
    json.dump(out, open(os.path.join(BUILD, "phase12_results.json"), "w"), indent=1)
    print("\nCMS official: obs 0.53209 pb (mu=%.3f)   exp 0.29472 pb (mu=%.3f)"
          % (0.53209 / 1.06241, 0.29472 / 1.06241))


if __name__ == "__main__":
    main()

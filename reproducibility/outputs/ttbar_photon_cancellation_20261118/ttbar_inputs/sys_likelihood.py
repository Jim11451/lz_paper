"""Step 2: asymptotic CLs with the CMS per-bin background nuisances.

Per bin the background carries a Gaussian constraint from the HEPData
"Stat + syst (1 s.d.)" error of the total $Background$ yield:

    -2 lnL_i(mu) = min_b [ -2(n_i ln(b + mu s_i) - (b + mu s_i))
                           + ((b - b_i^0)/sigma_i)^2 ]

The mode solves  n/(b+m) - 1 - (b-b0)/sigma^2 = 0, monotone in b, so each bin
is solved by bisection.  CLs uses the asymptotic formulae with q_mu and q_b
relative to the best-fit mu_hat.
"""
import math

import numpy as np
import yaml

YAML = "/home/yy/lz-event/phenomenology/data/cms/hepdata/postfit_MET_distribution_AH0l2bSR.yaml"
SQ2 = math.sqrt(2.0)


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _phi(x):
    return 0.5 * math.erfc(-x / SQ2)


def load():
    d = yaml.safe_load(open(YAML))
    iv = d["independent_variables"][0]["values"]
    edges = np.array([float(x["low"]) for x in iv] + [float(iv[-1]["high"])])
    procs, data = {}, None
    for dv in d["dependent_variables"]:
        q = {x["name"]: x["value"] for x in dv.get("qualifiers", [])}
        nm = str(q.get("Process", ""))
        val = np.array([_f(v["value"]) for v in dv["values"]])
        err = np.array([_f(v["errors"][0].get("symerror", 0.0)) if v.get("errors") else 0.0
                        for v in dv["values"]])
        if "Data" in nm:
            data = val
        elif "Signal" in nm:
            procs["__cms_signal__"] = (val, err)
        else:
            procs[nm] = (val, err)
    b, sb = procs["$Background$"]
    # bin 3 of the HEPData table carries a corrupted total error (5509 on a
    # background of 888); rebuild every bin from the component errors instead.
    comp = [v for k, v in procs.items() if not k.startswith("__") and k != "$Background$"]
    sb = np.sqrt(np.sum([e ** 2 for _, e in comp], axis=0))
    return edges, procs, b, sb, data


def bin_nll(n, m, b0, sb):
    """vectorised over bins: profiled -2lnL per bin."""
    n = np.asarray(n, float)
    m = np.asarray(m, float)
    b0 = np.asarray(b0, float)
    sb = np.asarray(sb, float)
    lo = np.full_like(b0, 1e-8)
    hi = np.maximum(b0 + 12 * sb, 1.0) + 10.0
    for _ in range(80):                      # bisection on d/db, all bins at once
        mid = 0.5 * (lo + hi)
        d = n / np.maximum(mid + m, 1e-9) - 1.0 - (mid - b0) / np.maximum(sb, 1e-12) ** 2
        pos = d > 0
        lo = np.where(pos, mid, lo)
        hi = np.where(pos, hi, mid)
    x = 0.5 * (lo + hi)
    t = np.maximum(x + m, 1e-9)
    with np.errstate(divide="ignore", invalid="ignore"):
        ll = np.where(sb > 1e-12,
                      -2 * (n * np.log(t) - t) + ((x - b0) / np.maximum(sb, 1e-12)) ** 2,
                      -2 * (n * np.log(t) - t))
    return float(np.sum(ll))


def nll(n, s, b0, sb, mu):
    return bin_nll(n, mu * np.asarray(s, float), b0, sb)


def fit_mu(n, s, b0, sb, hi=10.0):
    """best-fit signal strength (>= 0) by golden section"""
    gr = (math.sqrt(5) - 1) / 2
    a, c = 0.0, hi
    bb = c - gr * (c - a)
    dd = a + gr * (c - a)
    fb, fd = nll(n, s, b0, sb, bb), nll(n, s, b0, sb, dd)
    for _ in range(60):
        if fb < fd:
            c, dd, fd = dd, bb, fb
            bb = c - gr * (c - a)
            fb = nll(n, s, b0, sb, bb)
        else:
            a, bb, fb = bb, dd, fd
            dd = a + gr * (c - a)
            fd = nll(n, s, b0, sb, dd)
    return 0.5 * (a + c)


def cls(mu, n, s, b0, sb, muhat=None, nllhat=None):
    if muhat is None:
        muhat = fit_mu(n, s, b0, sb)
        nllhat = nll(n, s, b0, sb, muhat)
    # constrained mu_hat (<= mu): q_mu = 0 for mu below the best fit
    qmu = max(0.0, nll(n, s, b0, sb, mu) - nllhat) if mu > muhat else 0.0
    qb = max(0.0, nll(n, s, b0, sb, 0.0) - nllhat)
    p_mu = 1.0 - _phi(math.sqrt(qmu))
    pb = _phi(math.sqrt(qb))
    return p_mu / max(pb, 1e-12)


def mu95(n, s, b0, sb, with_syst=True):
    sbb = np.asarray(sb, float) if with_syst else np.zeros(len(b0))
    muhat = fit_mu(n, s, b0, sbb)
    nllhat = nll(n, s, b0, sbb, muhat)
    lo, hi = 1e-5, max(1.0, 2 * muhat + 1)
    while cls(hi, n, s, b0, sbb, muhat, nllhat) > 0.05:
        hi *= 2
        if hi > 1e5:
            return None
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if cls(mid, n, s, b0, sbb, muhat, nllhat) > 0.05:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    edges, procs, b, sb, data = load()
    print("bins=%d  B=%.1f  data=%.1f" % (len(b), b.sum(), data.sum()))
    print("bkg rel. unc.:", " ".join("%.0f%%" % (100 * x / max(y, 1e-9)) for y, x in zip(b, sb)))
    import final_plot as fp
    h = fp.shape("/home/yy/.hermes/cache/scratch/ttDM/sig_MV110.root")
    print("our shape:", np.round(h / h.sum(), 3))
    print("CMS shape:", np.round(procs["__cms_signal__"][0] / procs["__cms_signal__"][0].sum(), 3))
    for nev in (300, 500, 1000, 1500, 3000, 7000):
        s = h / h.sum() * nev
        a = mu95(data, s, b, sb, False)
        c = mu95(data, s, b, sb, True)
        print("S=%5d  stat-only %s   with syst %s"
              % (nev, ("%.3f" % a) if a else "None", ("%.3f" % c) if c else "None"))

"""Final (M_V, g_t) figure for the tt~+DM channel.

Ingredients
  * CMS-EXO-22-014 AH 0l 2b: 15 MET bins, post-fit background, observed counts.
  * signal shape per M_V from the full chain (Pythia8 + Delphes + selection).
  * sigma(M_V) interpolated from the tt~Vb scan (same physics, g_t = 0.994).
  * Planck band from the micrOMEGAs scan: for each M_V the m_chi with
    Omega h^2 = 0.12.
Statistics: 15-bin Poisson CLs, expected (n = b) and observed (n = data).
"""
import csv
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import awkward as ak  # noqa: E402
import numpy as np  # noqa: E402
import uproot  # noqa: E402
import yaml  # noqa: E402

YAML = "/home/yy/.hermes/cache/scratch/exo22014_data/postfit_MET_distribution_AH0l2bSR.yaml"
MM = "/home/yy/.hermes/cache/scratch/relic/mm_grid.csv"
MVS = [72, 90, 110, 140, 180]
LUMI = 138000.0
NSEV = 5000
METMIN, METMAX, NB = 250.0, 550.0, 15
# sigma(tt~Vb) [pb] at g_t = 0.994, from the earlier scan
REF_SIG = [(80, 2.561), (100, 2.031), (150, 1.135), (200, 0.6886), (300, 0.2786)]
KAPPA = {35: 4.223e-5, 40: 5.665e-5, 44: 7.202e-5}
M_Q = [0.0022, 0.0047, 0.093, 1.27, 4.18, 172.0]


def cms():
    d = yaml.safe_load(open(YAML))
    iv = d["independent_variables"][0]["values"]
    edges = [float(b["low"]) for b in iv] + [float(iv[-1]["high"])]
    bkg = obs = None
    for dv in d["dependent_variables"]:
        q = {x["name"]: x["value"] for x in dv.get("qualifiers", [])}
        nm = str(q.get("Process", ""))

        def num(v):
            try:
                return float(v["value"])
            except (TypeError, ValueError):
                return 0.0
        vals = np.array([num(v) for v in dv["values"]])
        if nm == "$Background$":
            bkg = vals
        elif "Data" in nm:
            obs = vals
    return edges, bkg, obs


def shape(root):
    t = uproot.open(root)["Delphes"]
    jet = t.arrays(["Jet.PT", "Jet.Eta", "Jet.Phi", "Jet.BTag"], library="ak")
    met = t.arrays(["MissingET.MET", "MissingET.Phi"], library="ak")
    el = t.arrays(["Electron.PT", "Electron.Eta"], library="ak")
    mu = t.arrays(["Muon.PT", "Muon.Eta"], library="ak")
    m_et = ak.to_numpy(met["MissingET.MET"])
    if m_et.ndim > 1:
        m_et = m_et[:, 0]
    m_ph = ak.to_numpy(met["MissingET.Phi"])
    if m_ph.ndim > 1:
        m_ph = m_ph[:, 0]
    good = (jet["Jet.PT"] > 30) & (np.abs(jet["Jet.Eta"]) < 2.4)
    nj = ak.sum(good, axis=1)
    nb = ak.sum(good & (jet["Jet.BTag"] > 0), axis=1)
    lep = (ak.sum((el["Electron.PT"] > 10) & (np.abs(el["Electron.Eta"]) < 2.4), axis=1)
           + ak.sum((mu["Muon.PT"] > 10) & (np.abs(mu["Muon.Eta"]) < 2.4), axis=1))
    base = (lep == 0) & (nj >= 3) & (nb >= 2) & (m_et > 250)
    h = np.zeros(NB)
    for i in np.where(base)[0]:
        pt = ak.to_numpy(jet["Jet.PT"][i][good[i]])
        ph = ak.to_numpy(jet["Jet.Phi"][i][good[i]])
        bt = ak.to_numpy(jet["Jet.BTag"][i][good[i]])
        o = np.argsort(-pt)
        pt, ph, bt = pt[o], ph[o], bt[o]
        if pt[0] / pt.sum() >= 0.5:
            continue
        d = np.abs(ph - m_ph[i])
        d = np.minimum(d, 2 * math.pi - d)
        if min(d[0], d[1]) <= 0.8:
            continue
        bs = np.where(bt > 0)[0]
        k = bs[np.argmin(d[bs])]
        mtb = math.sqrt(max(0.0, 2 * pt[k] * m_et[i] * (1 - math.cos(d[bs[np.argmin(d[bs])]]))))
        if mtb <= 140:
            continue
        h[min(int((m_et[i] - METMIN) / (METMAX - METMIN) * NB), NB - 1)] += 1
    return h


def sigma(mv):
    xs = [math.log(a) for a, _ in REF_SIG]
    ys = [math.log(b) for _, b in REF_SIG]
    s = math.exp(np.interp(math.log(mv), xs, ys))
    return s / 0.994 ** 2          # to g_t = 1


def br_chi(mv, gchi, mchi):
    if mv <= 2 * mchi:
        return 0.0
    b = math.sqrt(1 - (2 * mchi / mv) ** 2)
    g = gchi ** 2 * mv * b * (3 - b * b) / (96 * math.pi)
    return g


def br_total(mv, gchi, mchi, gt=1.0):
    g = br_chi(mv, gchi, mchi)
    q = 0.0
    for mq in M_Q:
        if mv > 2 * mq:
            bb = math.sqrt(1 - 4 * mq ** 2 / mv ** 2)
            q += 3 * (gt * mq / 172.0) ** 2 * mv * bb * (3 - bb * bb) / (24 * math.pi)
    return g, g / (g + q) if g + q > 0 else 0.0


def kappa(m):
    ks = sorted(KAPPA)
    if m <= ks[0]:
        return KAPPA[ks[0]]
    if m >= ks[-1]:
        return KAPPA[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= m <= b:
            return KAPPA[a] + (KAPPA[b] - KAPPA[a]) * (m - a) / (b - a)
    return KAPPA[ks[-1]]


def band_mchi():
    """m_chi(M_V) with Omega h^2 = 0.12 from the micrOMEGAs grid."""
    rows = []
    for r in csv.DictReader(open(MM)):
        try:
            rows.append((float(r["mchi"]), float(r["mv"]), float(r["omega"])))
        except (TypeError, ValueError):
            continue
    out = {}
    for mv in MVS:
        pts = sorted((m, o) for m, v, o in rows if abs(v - mv) < 1e-6)
        best = None
        for (m1, o1), (m2, o2) in zip(pts, pts[1:]):
            if (o1 - 0.12) * (o2 - 0.12) < 0:
                f = (0.12 - o1) / (o2 - o1)
                best = m1 + f * (m2 - m1)
                break
        out[mv] = best
    return out


def mu95(s, b, n):
    def ll(nn, m):
        return float(np.sum(nn * np.log(np.maximum(m, 1e-300)) - m))

    def p(mu):
        q = max(0.0, 2 * (ll(n, b) - ll(n, mu * s + b)))
        return 0.5 * math.erfc(math.sqrt(q / 2))

    lo, hi = 1e-3, 1.0
    while p(hi) > 0.05:
        hi *= 2
        if hi > 1e4:
            return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if p(mid) > 0.05:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    edges, bkg, obs = cms()
    band = band_mchi()
    print("band m_chi(MV):", {k: (round(v, 2) if v else None) for k, v in band.items()})

    shapes = {}
    for mv in MVS:
        try:
            shapes[mv] = shape("/home/yy/.hermes/cache/scratch/ttDM/sig_MV%d.root" % mv)
        except FileNotFoundError:
            print("missing root for MV", mv)
    for mv, h in shapes.items():
        print("MV=%d  selected=%d" % (mv, int(h.sum())))

    mvs = sorted(shapes)
    gts = np.logspace(math.log10(0.1), math.log10(3.5), 40)
    ZE = np.full((len(gts), len(mvs)), np.nan)
    ZO = np.full((len(gts), len(mvs)), np.nan)
    for j, mv in enumerate(mvs):
        mchi = band.get(mv)
        h = shapes[mv]
        sig = sigma(mv)
        gchi = kappa(mchi) * mv ** 2 if mchi else 0.0
        _, br = br_total(mv, gchi, mchi) if mchi else (0, 0)
        g0 = 0.32 * 0 + kappa(35.0) * mv ** 2
        _, br0 = br_total(mv, g0, 35.0)
        if mchi is None or 2 * mchi >= mv:      # V cannot decay to chi chi -> no signal
            print("MV=%d: no chi chi channel (m_chi=%.1f)" % (mv, mchi or -1))
            continue
        base = h / NSEV * sig * LUMI * (br / br0 if br0 else 0)
        for i, gt in enumerate(gts):
            s = base * gt ** 2
            ZE[i, j] = mu95(s, bkg, bkg) or np.nan
            ZO[i, j] = mu95(s, bkg, obs) or np.nan

    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.8), dpi=160, sharey=True)
    for ax, Z, tag in zip(axes, (ZE, ZO), ("expected (Asimov)", "observed (CMS data)")):
        Zm = np.ma.masked_invalid(Z)
        im = ax.pcolormesh(mvs, gts, Zm, shading="auto", cmap="RdBu_r",
                           norm=matplotlib.colors.LogNorm(vmin=0.02, vmax=5))
        cs = ax.contour(mvs, gts, Zm, levels=[1.0], colors="k", linewidths=1.6)
        for j, mv in enumerate(mvs):
            mm = band.get(mv)
            if mm is None or 2 * mm >= mv:
                ax.axvspan(mv - 9, mv + 9, color="0.85", zorder=0)
                ax.text(mv, 0.13, "no $\chi\chi$", rotation=90, fontsize=7,
                        color="0.4", ha="center")
        ax.clabel(cs, fmt={1.0: r"$\mu_{95}=1$"}, fontsize=8)
        ax.set_yscale("log")
        ax.set_xlabel(r"$M_V$  [GeV]")
        ax.set_title(r"$t\bar t$+DM, CMS-EXO-22-014 AH 2$b$, " + tag, fontsize=9)
        ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.5)
    axes[0].set_ylabel(r"$g_t$")
    cb = fig.colorbar(im, ax=axes, pad=0.015)
    cb.set_label(r"$\mu_{95}$", fontsize=9)
    out = "/home/yy/.hermes/cache/scratch/ttDM/fig_final_MVgt.png"
    fig.savefig(out)
    print("wrote", out)

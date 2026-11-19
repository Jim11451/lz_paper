"""Recalculate CMS EXO-20-004 limits using the published benchmark yields."""

import csv
import math
import sys
import tarfile
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parents[1]
OUTPUTS = HERE.parent
ARCHIVE = OUTPUTS.parent / "tmp/cms_monojet_hepdata_v2.tar.gz"
sys.path.insert(0, str(OUTPUTS / "monojet_expected_lz_scan_20261106/scripts"))
sys.path.insert(0, str(OUTPUTS / "monojet_mchi_scan_20261106/scripts"))
from expected_scan import AsimovFit, cms_inputs, write
from observed_fit import ObservedFit, cls
from scan_observed import PhysicalAsimov


def tables(archive, name):
    file = f"HEPData-ins1894408-v2-csv/{name}.csv"
    text = archive.extractfile(file).read().decode("utf-8-sig")
    for group in text.strip().split("\n\n"):
        rows = list(csv.reader(group.splitlines()))
        meta = {r[0][3:]: r[-1] for r in rows if r and r[0].startswith("#: ") and len(r) > 1}
        data = [r for r in rows if r and not r[0].startswith("#")]
        if data:
            yield meta, [dict(zip(data[0], r)) for r in data[1:]]


def background(archive):
    table = "Simplifiedlikelihood:Yields(Monojet+mono-V)"
    tables_yield = list(tables(archive, table))
    bdict = {r["Bin"]: float(r["Background yield"]) for r in tables_yield[0][1]}
    ndict = {r["Bin"]: int(r["Data yield"]) for r in tables_yield[1][1]}
    _, elements = next(tables(archive, "Simplifiedlikelihood:covariancematrix(Monojet+mono-V)"))
    cdict = {(r["First Bin"], r["Second Bin"]): float(r["Covariance"]) for r in elements}
    source_bins, original_fit, _ = cms_inputs()
    labels = [r["region"].replace("monojet_SR_", "monojet_") for r in source_bins]
    labels += [f"monovtau21_2016_bin{i}" for i in range(7)]
    b = np.array([bdict[key] for key in labels])
    n = np.array([ndict[key] for key in labels])
    cov = np.array([[cdict[(a, c)] for c in labels] for a in labels])
    assert np.allclose(original_fit.b, b[:66]) and np.allclose(original_fit.covariance, cov[:66, :66])
    assert np.array_equal(n[:66], [int(r["observed"]) for r in source_bins])
    return labels, b, n, cov


def official_signals(archive):
    by_mode = defaultdict(dict)
    for spin in (0, 1):
        for category in ("Monojet", "Mono-V(tau_{21})"):
            for meta, rows in tables(archive, f"Signaltemplates,DMsimp,spin-{spin},{category}"):
                if float(meta["$m_{DM}$"]) != 1.:
                    continue
                key = (meta["Coupling type"], float(meta["$m_{med}$"]))
                year = int(meta["Data-taking period"])
                mode = meta["Production mode"]
                prefix = "monojet" if category == "Monojet" else "monovtau21"
                assert len(rows) == (22 if prefix == "monojet" else 7)
                for i, r in enumerate(rows):
                    label = f"{prefix}_{year}_bin{i}"
                    mode_data = by_mode[key].setdefault(mode, {})
                    assert label not in mode_data
                    mode_data[label] = (float(r["Signal yield"]), float(r["Sample size +"]),
                                        float(r["Recoil (GeV) LOW"]))
    return by_mode


class GeneralAsimov(AsimovFit):
    """Use the existing expected-limit inversion with the same Poisson profiler at any bin count."""

    def __init__(self, background, covariance):
        self.fisher = np.linalg.cholesky(covariance + np.diag(background))
        self.profile = ObservedFit(background, background, covariance).profile

    def q(self, amplitude, signal, signal_cov=None):
        return self.profile(amplitude, signal, signal_cov).deviance


class Fit:
    def __init__(self, b, n, cov):
        asimov_type = PhysicalAsimov if len(b) == 66 else GeneralAsimov
        self.expected = asimov_type(b, cov)
        self.observed = ObservedFit(n, b, cov)
        conditional = self.observed.profile(0., np.zeros(len(b))).mean
        self.conditional = asimov_type(conditional, cov)

    def upper(self, signal, signal_cov):
        exp = self.expected.upper(signal, signal_cov)
        obs, best, qobs, qa = self.observed.upper(signal, signal_cov, exp, self.conditional)
        assert abs(cls(qobs, qa) - .05) < 5e-8
        return exp, obs, best


def official_limits(archive):
    values = {}
    for family in ("scalar", "pseudoscalar"):
        for meta, rows in tables(archive, f"Signalstrengthlimits,{family}mediator"):
            q = meta["Quantile"].lower()
            if q not in {"median expected", "observed"}:
                continue
            for r in rows:
                values[family.capitalize(), float(r["$m_{med}$ [GeV]"]), q] = float(r["Signal strength limit"])
    return values


def vector_crossings(archive, rows):
    crossings = []
    for quantile, file_quantile in (("expected", "MedianExpected"), ("observed", "Observed")):
        _, table = next(tables(archive, f"2Dexclusioncontour,vector,{file_quantile}"))
        nodes = [(float(row["$m_{med}$ [GeV]"]), float(row["$m_{\\chi}$ [GeV]"])) for row in table]
        official = []
        for (m1, d1), (m2, d2) in zip(nodes, nodes[1:] + nodes[:1]):
            if (d1 < 1. <= d2) or (d2 < 1. <= d1):
                official.append(m1 + (m2-m1)*(1.-d1)/(d2-d1))
        assert official
        cms = max(official)
        for channels in ("monojet_66", "monojet_plus_2016_monov_73"):
            subset = sorted((r["mediator_GeV"], r[f"mu95_{quantile}"]) for r in rows if r["coupling"] == "Vector"
                            and r["fit"] == channels and r["signal_uncertainty"] == "HEPData_binwise_MC")
            m, mu = np.asarray(subset).T
            i, = np.flatnonzero((mu[:-1] < 1.) & (mu[1:] >= 1.))
            reach = np.interp(0., np.log(mu[i:i+2]), m[i:i+2])
            crossings.append(dict(quantile=quantile, fit=channels, mass_crossing_GeV=reach,
                                  bracket_low_GeV=m[i], bracket_high_GeV=m[i+1],
                                  CMS_combined_mass_crossing_GeV=cms, ratio=reach/cms))
    return crossings


def plot_limits(rows, crossings):
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.25), layout="constrained")
    for ax, family in zip(axes, ("Scalar", "Pseudoscalar", "Vector")):
        selection = [r for r in rows if r["coupling"] == family and r["signal_uncertainty"] == "HEPData_binwise_MC"]
        for quantile, color in (("expected", "#206f9a"), ("observed", "#b14232")):
            for channels, style in (("monojet_66", "-"), ("monojet_plus_2016_monov_73", "--")):
                curve = sorted((r["mediator_GeV"], r[f"mu95_{quantile}"]) for r in selection if r["fit"] == channels)
                x, y = np.asarray(curve).T
                ax.plot(x, y, style, marker="." if channels == "monojet_66" else None, color=color,
                        label=f"{quantile.capitalize()}, {'66 bins' if channels == 'monojet_66' else '73 bins'}")
            if family != "Vector":
                points = [(r["mediator_GeV"], r[f"CMS_combined_mu95_{quantile}"]) for r in selection
                          if r["fit"] == "monojet_66" and np.isfinite(r[f"CMS_combined_mu95_{quantile}"])]
                x, y = np.asarray(sorted(points)).T
                ax.plot(x, y, marker="o", mfc="none", ls="none", color=color,
                        label=f"CMS combined {quantile}")
            else:
                c = next(r for r in crossings if r["quantile"] == quantile)
                ax.scatter(c["CMS_combined_mass_crossing_GeV"], 1., marker="o", facecolors="none", edgecolors=color)
        ax.axhline(1., color="0.5", lw=1, ls=":")
        ax.set(title=family, yscale="log", xlabel=r"Mediator mass [GeV]", ylabel=r"95% $CL_s$ upper limit on $\mu$")
        ax.grid(alpha=.18)
    axes[0].legend(fontsize=8)
    axes[2].text(.04, .96, "Open circles: CMS combined mass reach", transform=axes[2].transAxes,
                 va="top", fontsize=8)
    fig.suptitle(r"CMS EXO-20-004 benchmarks with official signal templates ($m_{\rm DM}=1$ GeV)")
    fig.savefig(HERE / "figures/benchmark_limits.png", dpi=200)


def main():
    for folder in ("results", "figures"):
        (HERE / folder).mkdir(exist_ok=True)
    with tarfile.open(ARCHIVE) as archive:
        labels, b, n, cov = background(archive)
        templates = official_signals(archive)
        official = official_limits(archive)
        configurations = (("monojet_66", 66), ("monojet_plus_2016_monov_73", 73))
        fits = {name: Fit(b[:i], n[:i], cov[:i, :i]) for name, i in configurations}
        rows, spectra = [], []
        for (family, mass), contributions in sorted(templates.items()):
            assert len(contributions) == (3 if family in ("Vector", "Axial") else 2)
            s = np.zeros(73)
            var = np.zeros(73)
            for mode, bins in contributions.items():
                assert set(labels) <= set(bins)
                for i, label in enumerate(labels):
                    y, dy, low = bins[label]
                    s[i] += y
                    var[i] += dy**2
                    if family == "Vector" and mass in (100, 750, 2000) and i < 66:
                        spectra.append(dict(coupling=family, mass_GeV=mass, mode=mode, label=label,
                                            met_low=low, cms_yield=y, cms_mc_error=dy))
            for name, i in configurations:
                # A handful of official NLO bins have a negative MC estimator.
                # Keep the published uncertainty and enforce a physical central yield.
                physical_signal = np.maximum(s[:i], 0.)
                for uncertainty, signal_cov in (("fixed", None), ("HEPData_binwise_MC", np.diag(var[:i]))):
                    exp, obs, best = fits[name].upper(physical_signal, signal_cov)
                    cms_exp = official.get((family, mass, "median expected"), math.nan)
                    cms_obs = official.get((family, mass, "observed"), math.nan)
                    rows.append(dict(coupling=family, mediator_GeV=mass, fit=name, signal_uncertainty=uncertainty,
                                     mu95_expected=exp, mu95_observed=obs, mu_best=best, signal_events=physical_signal.sum(),
                                     negative_signal_bins=int((s[:i] < 0.).sum()),
                                     CMS_combined_mu95_expected=cms_exp, CMS_combined_mu95_observed=cms_obs,
                                     expected_ratio=exp/cms_exp, observed_ratio=obs/cms_obs))
        crossings = vector_crossings(archive, rows)
    write(HERE / "results/official_template_limits.csv", rows)
    write(HERE / "results/vector_reach.csv", crossings)
    write(HERE / "results/official_vector_spectra.csv", spectra)
    plot_limits(rows, crossings)
    print(f"{len(rows)} fits with official templates and {len(spectra)} benchmark spectrum bins", flush=True)
    for row in crossings:
        print(row, flush=True)


if __name__ == "__main__":
    main()

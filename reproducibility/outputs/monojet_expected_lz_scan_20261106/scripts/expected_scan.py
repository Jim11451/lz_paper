import csv
import json
import math
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter, ScalarFormatter


HERE = Path(__file__).resolve().parent.parent
INPUTS = HERE.parent / "monojet_report_20261106/data"
sys.path.insert(0, str(HERE.parent / "truth_xsec_scan_20261106/scripts"))
from plot_scan import POINTS, GT_MAX, br, lz_product


N_BINS = 22
N_YEARS = 3
LUMINOSITY = (36, 41, 60)
TARGET_Q = NormalDist().inv_cdf(.975)**2
CHANNELS = {"loop", "loop_hard", "jet_tree", "jet_tree_hard"}
BOOTSTRAPS = 120


class AsimovFit:
    def __init__(self, background, covariance):
        assert len(background) == 66 and np.all(background > 0)
        assert np.allclose(covariance, covariance.T)
        self.b = background
        self.covariance = covariance
        self.chol = np.linalg.cholesky(covariance)
        self.fisher = np.linalg.cholesky(covariance + np.diag(background))
        self.identity = np.eye(len(background))

    def q(self, amplitude, signal, signal_cov=None):
        b = self.b
        chol = self.chol if signal_cov is None else np.linalg.cholesky(
            self.covariance + amplitude**2*signal_cov)
        shift = amplitude * signal
        latent = np.zeros_like(b)

        def deviance(offset):
            relative = (shift + chol @ offset) / b
            return float(2*np.sum(b*(relative - np.log1p(relative))) + offset @ offset)

        for _ in range(30):
            lam = b + shift + chol @ latent
            grad = latent + chol.T @ (1 - b/lam)
            if np.max(np.abs(grad)) < 1e-7:
                return deviance(latent)
            hessian = self.identity + chol.T @ ((b/lam**2)[:, None]*chol)
            direction = np.linalg.solve(hessian, -grad)
            step = 1.0
            current = deviance(latent)
            while np.min(lam + chol @ (step*direction)) <= 0 or deviance(latent+step*direction) > current+1e-10:
                step *= .5
                if step < 1e-8:
                    raise RuntimeError("Profile line search did not converge")
            latent += step*direction
        raise RuntimeError("Profile fit did not converge")

    def upper(self, signal, signal_cov=None):
        fisher_signal = np.linalg.solve(self.fisher, signal)
        guess = math.sqrt(TARGET_Q / (fisher_signal @ fisher_signal))
        lo, hi = 0.0, 1.5*guess
        while self.q(hi, signal, signal_cov) < TARGET_Q:
            hi *= 2
            if hi > 1000*guess:
                raise RuntimeError("Expected limit is not bracketed")
        for _ in range(24):
            mid = (lo+hi)/2
            if self.q(mid, signal, signal_cov) < TARGET_Q:
                lo = mid
            else:
                hi = mid
        limit = (lo+hi)/2
        assert abs(self.q(limit, signal, signal_cov) - TARGET_Q) < 1e-5
        return limit


def write(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def cms_inputs():
    with (INPUTS/"cms_run2_bin_yields.csv").open() as stream:
        records = list(csv.DictReader(stream))
    xml = {r.attrib["id"]: r for r in ET.parse(INPUTS/"cms_exo_20_004.info").getroot().findall("region")}
    ids = [r["region"] for r in records]
    for i, row in enumerate(records):
        assert row["year"] == str(2016+i//22) and int(ids[i].split("bin")[-1]) == i % 22
        assert float(row["background"]) == float(xml[ids[i]].findtext("nb"))
    covariance = np.array([[float(xml[i].find(f"covariance[@region='{j}']").text) for j in ids] for i in ids])
    background = np.array([float(row["background"]) for row in records])
    old_b = np.array([float(row["signal_total"]) for row in records])
    return records, AsimovFit(background, covariance), old_b


def to_yields(counts, cross):
    # A category retains both the common selection bin and the 2018 HEM status.
    normal, hem = counts[1:].reshape(N_BINS, 2).T
    cross_per_event_fb = cross*1000/counts.sum()
    return cross_per_event_fb*np.concatenate((LUMINOSITY[0]*(normal+hem),
                                              LUMINOSITY[1]*(normal+hem), LUMINOSITY[2]*hem))


def template_covariance(counts, cross, error):
    n = counts.sum()
    one_event = np.eye(len(counts), dtype=int)
    response = np.array([to_yields(event, cross/n) for event in one_event])
    probabilities = counts/n
    average = probabilities @ response
    centered = response-average
    covariance = n*centered.T @ (probabilities[:,None]*centered)
    rate_error = n*average*(error/cross)
    return covariance + np.outer(rate_error, rate_error)


def load_templates(directory):
    samples = defaultdict(dict)
    for path in sorted(directory.glob("*.npz")):
        with np.load(path) as data:
            mass, channel = float(data["mass"]), str(data["channel"])
            counts = data["counts"]
            assert counts.shape == (45,) and counts[1:].sum() > 0 and float(data["alignment"]) < .005
            assert channel not in samples[mass]
            samples[mass][channel] = (counts, float(data["cross"]), float(data["cross_error"]))
    assert len(samples) == 11 and all(set(group) == CHANNELS for group in samples.values())
    return dict(sorted(samples.items()))


def evaluate_nodes(samples, records, fit, result_dir):
    rng = np.random.default_rng(20261106)
    rows, node_rows, vectors, matrices, bootstrap_vectors = [], [], [], [], []
    for mass, group in samples.items():
        signals = {channel: to_yields(counts, cross) for channel, (counts, cross, _) in group.items()}
        loop = signals["loop"] + signals["loop_hard"]
        tree = signals["jet_tree"] + signals["jet_tree_hard"]
        nominal = loop+tree
        vectors.append(nominal)
        signal_cov = sum(template_covariance(*sample) for sample in group.values())
        matrices.append(signal_cov)
        amplitude95 = fit.upper(nominal)
        amplitude95_mc = fit.upper(nominal, signal_cov)
        variations, varied_templates = [], []
        for _ in range(BOOTSTRAPS):
            alternative = np.zeros(66)
            for counts, cross, error in group.values():
                draw = rng.multinomial(int(counts.sum()), counts/counts.sum())
                alternative += to_yields(draw, rng.normal(cross, error))
            varied_templates.append(alternative)
            variations.append(fit.upper(alternative))
        bootstrap_vectors.append(varied_templates)
        lo, hi = np.quantile(variations, [.16, .84])
        node_rows.append(dict(mass_GeV=mass, amplitude95=amplitude95, amplitude95_mc_profiled=amplitude95_mc,
                              mc_amplitude95_lo68=lo,
                              mc_amplitude95_hi68=hi, signal_ref=nominal.sum(),
                              loop_fraction=loop.sum()/nominal.sum(), signal_ref_overflow=nominal[21::22].sum(),
                              generated_events=sum(int(group[c][0].sum()) for c in group)))
        for i, row in enumerate(records):
            rows.append(dict(mass_GeV=mass, region=row["region"], year=row["year"],
                             met_low_GeV=row["met_low_GeV"], met_high_GeV=row["met_high_GeV"],
                             signal_tree_ref=tree[i], signal_loop_ref=loop[i], signal_total_ref=nominal[i],
                             background=row["background"]))
    write(result_dir/"cms66_signal_templates.csv", rows)
    write(result_dir/"mass_node_limits.csv", node_rows)
    return node_rows, np.array(vectors), np.array(matrices), np.array(bootstrap_vectors)


def interpolate(masses, node_masses, vectors):
    return np.column_stack([np.interp(masses, node_masses, vec) for vec in vectors.T])


def interpolate_covariance(masses, nodes, matrices):
    hi = np.clip(np.searchsorted(nodes, masses, side="right"), 1, len(nodes)-1)
    lo = hi-1
    fraction = ((masses-nodes[lo])/(nodes[hi]-nodes[lo]))[:, None, None]
    return (1-fraction)**2*matrices[lo] + fraction**2*matrices[hi]


def coupling_plane(masses, amplitudes, reference_yields):
    gc_axis = np.unique(np.r_[np.geomspace(.1, 1.5, 241), [gc for _, gc in POINTS.values()]])
    mass, gc = np.meshgrid(masses, gc_axis)
    gt = lz_product(mass)/gc
    branch, width = br(mass, gt, gc)
    allowed = (gt <= GT_MAX) & (width < .03)
    scaling = gt**2 * branch
    limits = np.where(allowed, amplitudes[None,:]/scaling, np.nan)
    events = np.where(allowed, reference_yields[None,:]*scaling, np.nan)
    return mass, gc, gt, branch, width, allowed, limits, events


def plot(plane, mc_limits, node_rows, figures):
    mass, gc, _, _, _, _, limit, _ = plane
    fig, (ax, profile) = plt.subplots(1, 2, figsize=(12.6, 5.2),
                                    gridspec_kw={"width_ratios": [1.25, 1]}, layout="constrained")
    norm = TwoSlopeNorm(vmin=-0.9, vcenter=0, vmax=1.6)
    image = ax.pcolormesh(mass, gc, np.log10(limit), cmap="RdBu", norm=norm, shading="auto", rasterized=True)
    ticks = np.array([.15, .25, .5, 1, 2, 5, 10, 20])
    cbar = fig.colorbar(image, ax=ax, ticks=np.log10(ticks), extend="both", pad=.02)
    cbar.ax.set_yticklabels([f"{t:g}" for t in ticks])
    cbar.set_label(r"Median expected $\mu_{95}$")
    if np.nanmin(limit) < 1 < np.nanmax(limit):
        ax.contour(mass, gc, limit, levels=[1], colors="#191923", linewidths=1.5)
    if np.nanmin(mc_limits) < 1 < np.nanmax(mc_limits):
        ax.contour(mass, gc, mc_limits, levels=[1], colors="#191923", linewidths=1.4, linestyles="--")
    ax.plot(mass[0], lz_product(mass[0])/GT_MAX, color="#626574", linewidth=1.0)
    for name, (m, g) in POINTS.items():
        ax.scatter(m, g, s=33, color="white", edgecolor="#151515", linewidth=.9, zorder=4)
        ax.annotate(name, (m,g), xytext=(6,2), textcoords="offset points", fontsize=10, weight="bold")
    ax.set(xlabel=r"$M_V$ [GeV]", ylabel=r"$g_\chi$", yscale="log", xlim=(72,200), ylim=(.1,1.5),
           title=r"LZ rate matched  |  contours $\mu_{95}=1$")
    ax.set_yticks([.1,.2,.3,.5,1,1.5])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_facecolor("#eaeaea")
    ax.legend(handles=[Line2D([], [], color="#191923", label="Nominal contour"),
                       Line2D([], [], color="#191923", ls="--", label="MC statistics profiled")],
              loc="lower right", fontsize=8, framealpha=.95)
    minima = np.nanmin(limit, axis=0)
    profile.plot(mass[0], minima, color="#274867", label="Nominal template")
    profile.plot(mass[0], np.nanmin(mc_limits, axis=0), "--", color="#9b4a32", label="MC statistics profiled")
    x = np.array([row["mass_GeV"] for row in node_rows])
    profile.scatter(x, minima[np.searchsorted(mass[0], x)], color="#274867", s=18, zorder=3)
    profile.axhline(1, color="#29292f", linestyle="--", linewidth=1)
    profile.set(xlabel=r"$M_V$ [GeV]", ylabel=r"Minimum expected $\mu_{95}$",
                xlim=(72,200), title=r"Best coupling at each $M_V$")
    profile.grid(alpha=.2)
    profile.legend()
    fig.suptitle(r"CMS monojet Run 2, 13 TeV, 137 fb$^{-1}$  |  66-bin expected $CL_s$", fontsize=14)
    for suffix in ("png","pdf"):
        fig.savefig(figures/f"expected_mu95_lz_plane.{suffix}", dpi=210)
    plt.close(fig)


def main():
    result_dir, figures = HERE/"results", HERE/"figures"
    result_dir.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    records, fit, old_b = cms_inputs()
    closure = fit.upper(old_b)
    assert abs(closure-1.73685) < .0001
    samples = load_templates(HERE/"templates")
    nodes, vectors, matrices, bootstrap_vectors = evaluate_nodes(samples, records, fit, result_dir)
    node_masses = np.array(list(samples))
    masses = np.unique(np.r_[np.linspace(72,200,257), node_masses, [m for m, _ in POINTS.values()]])
    signals = interpolate(masses, node_masses, vectors)
    signal_covs = interpolate_covariance(masses, node_masses, matrices)
    amplitudes = np.array([fit.upper(vec) for vec in signals])
    amplitudes_mc = np.array([fit.upper(vec, cov) for vec, cov in zip(signals, signal_covs, strict=True)])
    plane = coupling_plane(masses, amplitudes, signals.sum(axis=1))
    mass, gc, gt, branch, width, allowed, limits, events = plane
    limits_mc = limits*(amplitudes_mc/amplitudes)[None,:]
    assert np.all(limits_mc[allowed] >= limits[allowed]*(1-1e-6))
    columns = (mass, gc, gt, branch, width, allowed, limits, limits_mc, events)
    with (result_dir/"expected_mu95_grid.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("mass_GeV","gchi","gt_LZ","BR_invisible","width_over_mass","valid",
                         "expected_mu95","expected_mu95_mc_profiled","signal_events"))
        writer.writerows(([f"{v:.9g}" if np.isfinite(v) else "" for v in values]
                          for values in zip(*(c.ravel() for c in columns), strict=True)))
    benchmark_rows = []
    for name, (m,g) in POINTS.items():
        i, j = np.searchsorted(gc[:,0], g), np.searchsorted(masses, m)
        scale = gt[i,j]**2*branch[i,j]
        direct = fit.upper(signals[j]*scale)
        assert math.isclose(direct, limits[i,j], rel_tol=1e-6)
        direct_mc = fit.upper(signals[j]*scale, signal_covs[j]*scale**2)
        assert math.isclose(direct_mc, limits_mc[i,j], rel_tol=1e-6)
        variations = [fit.upper(interpolate([m], node_masses, ensemble)[0]*scale)
                      for ensemble in bootstrap_vectors.transpose(1,0,2)]
        lo, hi = np.quantile(variations, [.16, .84])
        benchmark_rows.append(dict(point=name, mass_GeV=m, gchi=g, gt_LZ=gt[i,j],
                                   expected_mu95=limits[i,j], expected_mu95_mc_profiled=limits_mc[i,j],
                                   mc_resampled_lo68=lo, mc_resampled_hi68=hi,
                                   signal_events=events[i,j]))
    write(result_dir/"benchmark_expected_limits.csv", benchmark_rows)
    idx = np.unravel_index(np.nanargmin(limits), limits.shape)
    idx_mc = np.unravel_index(np.nanargmin(limits_mc), limits_mc.shape)
    reach = masses[np.nanmin(limits, axis=0) < 1]
    reach_mc = masses[np.nanmin(limits_mc, axis=0) < 1]
    summary = dict(previous_B_template_mu95=closure, benchmarks=benchmark_rows,
                   best=dict(mass_GeV=mass[idx], gchi=gc[idx], gt=gt[idx], mu95=limits[idx]),
                   best_mc=dict(mass_GeV=mass[idx_mc], gchi=gc[idx_mc], gt=gt[idx_mc],
                                mu95=limits_mc[idx_mc]),
                   first_mass_with_mu95_below_one=float(reach[0]) if reach.size else None,
                   first_mass_with_mc_mu95_below_one=float(reach_mc[0]) if reach_mc.size else None,
                   n_mass_nodes=len(node_masses), grid_points=mass.size, valid_grid_points=int(allowed.sum()),
                   generated_events=sum(r["generated_events"] for r in nodes))
    (result_dir/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    np.savez_compressed(result_dir/"node_signal_covariances.npz", mass_GeV=node_masses,
                        covariance=matrices)
    plot(plane, limits_mc, nodes, figures)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

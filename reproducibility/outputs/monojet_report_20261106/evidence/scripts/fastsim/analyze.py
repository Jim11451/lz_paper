import csv
import gzip
import json
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent.parent
MET_CUTS = (250, 300, 350, 400, 500, 600, 700, 800, 900, 1000, 1200)
CMS_BINS = (250, 280, 310, 340, 370, 400, 430, 470, 510, 550, 590, 640,
            690, 740, 790, 840, 900, 960, 1020, 1090, 1160, 1250, 1400)
STAGES = ("generated", "leading AK4", "MET > 250", "jet quality", "min dphi", "e/mu/gamma veto",
          "tau veto", "b veto")
RUN2_STAGES = tuple(stage for stage in STAGES if stage != "jet quality")
RUN2_BINS = CMS_BINS[:-1]
RUN3_BINS = CMS_BINS
RUN2_MIX = (("B13_loop_loose", 0, 480), ("B13_loop_tail", 480, np.inf),
            ("B13_tree_loose", 0, np.inf))


@dataclass
class Sample:
    name: str
    meta: dict
    events: dict

    @classmethod
    def load(cls, source):
        with gzip.open(source, "rt") as f:
            table = np.genfromtxt(f, names=True, delimiter=",")
        meta = json.loads(source.with_suffix("").with_suffix(".json").read_text())
        assert meta["events"] == len(table)
        return cls(meta["sample"], meta, table)

    @property
    def weight(self):
        return self.events["weight"]

    @property
    def sigma(self):
        return self.meta["sigma_fb"]

    def fraction(self, mask):
        return self.weight[mask].sum() / self.weight.sum()

    def result(self, mask):
        w = self.weight
        p = self.fraction(mask)
        neff = w.sum()**2 / (w @ w)
        denominator = 1 + 1 / neff
        center = (p + 0.5 / neff) / denominator
        half = math.sqrt(p * (1 - p) / neff + 0.25 / neff**2) / denominator
        return dict(n_pass=np.count_nonzero(mask), n_generated=len(w), efficiency=p,
                    efficiency_lo68=max(0.0, center - half), efficiency_hi68=min(1.0, center + half),
                    selected_fb=self.sigma * p, selected_mc_lo68_fb=self.sigma * max(0.0, center - half),
                    selected_mc_hi68_fb=self.sigma * min(1.0, center + half),
                    selected_integral_error_fb=(self.meta["integration_error_fb"] or 0) * p
                    if self.meta["integration_error_fb"] is not None else "")


def masks(sample, alternate_b_tag=False):
    e = sample.events
    run3 = sample.meta["energy_TeV"] == 13.6
    all_events = np.ones(len(e), dtype=bool)
    cuts = (all_events, (e["j1_pt"] > 100) & (abs(e["j1_eta"]) < (2.5 if run3 else 2.4)), e["met"] > 250)
    if run3:
        cuts += (e["jet_quality"] > 0,)
    photon = e["photon_veto_run3"] if run3 else e["photon_veto"]
    b_tag = e["b_veto_run3" if run3 and not alternate_b_tag else "b_veto"]
    cuts += (e["min_dphi"] > 0.5, (e["electron_veto"] * e["muon_veto"] * photon) > 0,
             e["tau_veto_run3" if run3 else "tau_veto_run2"] > 0, b_tag > 0)
    return list(np.logical_and.accumulate(cuts, axis=0))


def write_csv(name, rows):
    with (HERE / "results" / f"{name}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def selected_parts(sample, met_min):
    e = sample.events
    eta_max = 2.5 if sample.meta["energy_TeV"] == 13.6 else 2.4
    return {
        "parton": (e["gen_met"] > met_min) & (abs(e["gen_j1_eta"]) < eta_max),
        "shower": (e["shower_met"] > met_min) & (e["shower_j1_pt"] > 100)
        & (abs(e["shower_j1_eta"]) < eta_max) & (e["shower_min_dphi"] > 0.5),
        "reco": masks(sample)[-1] & (e["met"] > met_min),
    }


def region_rows(samples):
    cutflow, thresholds, bins = [], [], []
    for s in samples.values():
        previous = 1.0
        run3 = s.meta["energy_TeV"] == 13.6
        for name, mask in zip(STAGES if run3 else RUN2_STAGES, masks(s), strict=True):
            result = s.result(mask)
            efficiency = result["efficiency"]
            cutflow.append(dict(sample=s.name, energy_TeV=s.meta["energy_TeV"], stage=name,
                                step_efficiency=efficiency / previous if previous else "", **result))
            previous = efficiency
        for met in MET_CUTS:
            for level, mask in selected_parts(s, met).items():
                thresholds.append(dict(sample=s.name, energy_TeV=s.meta["energy_TeV"],
                                       min_met_GeV=met, level=level, **s.result(mask)))
        edges = RUN3_BINS if run3 else RUN2_BINS
        for low, high in zip(edges, (*edges[1:], np.inf), strict=True):
            selected = masks(s)[-1] & (s.events["met"] >= low) & (s.events["met"] < high)
            bins.append(dict(sample=s.name, energy_TeV=s.meta["energy_TeV"], met_low_GeV=low,
                             met_high_GeV=high, **s.result(selected)))
    return cutflow, thresholds, bins


def mixed_thresholds(samples):
    mixes = {
        "B_13p6": (("B_loop", 0, np.inf), ("B_tree", 0, np.inf)),
        "C_13p6": (("C_loop", 0, np.inf), ("C_tree", 0, np.inf)),
        "B_13": RUN2_MIX,
    }
    rows = []
    for label, parts in mixes.items():
        if any(name not in samples for name, _, _ in parts):
            continue
        for met in MET_CUTS:
            for level in ("parton", "shower", "reco"):
                result = {}
                for name, low, high in parts:
                    s = samples[name]
                    stitched = (s.events["gen_met"] >= low) & (s.events["gen_met"] < high)
                    result[name] = s.result(stitched & selected_parts(s, met)[level])
                loop = sum(r["selected_fb"] for name, r in result.items() if "loop" in name)
                tree = sum(r["selected_fb"] for name, r in result.items() if "tree" in name)
                total = loop + tree
                mc_low = math.sqrt(sum((r["selected_fb"] - r["selected_mc_lo68_fb"])**2
                                       for r in result.values()))
                mc_high = math.sqrt(sum((r["selected_mc_hi68_fb"] - r["selected_fb"])**2
                                        for r in result.values()))
                error = [r["selected_integral_error_fb"] for r in result.values()]
                rows.append(dict(benchmark=label, level=level, min_met_GeV=met,
                                 loop_fb=loop, tree_fb=tree, total_fb=total, loop_fraction=loop / total if total else "",
                                 mc_lo68_fb=max(0, total - mc_low), mc_hi68_fb=total + mc_high,
                                 integral_error_fb=math.sqrt(sum(e**2 for e in error)) if "" not in error else "",
                                 sum_n_pass=sum(r["n_pass"] for r in result.values())))
    return rows


def migration_rows(samples):
    rows = []
    for label in ("B13_loop_loose", "B13_tree_loose"):
        if label not in samples:
            continue
        s = samples[label]
        for met in (250, 300, 400, 500):
            selection = selected_parts(s, met)["reco"]
            for gen_min in (150, 200, 250, 300, 480):
                below = s.events["gen_met"] < gen_min
                low_part = s.sigma * s.fraction(below & selection)
                total = s.sigma * s.fraction(selection)
                rows.append(dict(sample=label, reco_met_min_GeV=met, gen_met_below_GeV=gen_min,
                                 n_pass_below=np.count_nonzero(below & selection), contribution_fb=low_part,
                                 total_fb=total, fraction_of_selected=low_part / total if total else ""))
    return rows


def kinematic_rows(samples):
    rows = []
    for s in samples.values():
        e = s.events
        for prefix, level in (("gen_", "parton"), ("shower_", "particle"), ("", "reco")):
            met = e[prefix + "met"]
            valid_jets = e[prefix + "j1_pt"] > 0
            high_mult = e[prefix + "njets"] >= 2 if level != "parton" else np.zeros(len(e), dtype=bool)
            dphi = e[prefix + "min_dphi"] if level != "parton" else np.full(len(e), math.pi)
            selected = selected_parts(s, 250)["shower" if level == "particle" else level]
            rows.append(dict(sample=s.name, level=level, median_met_GeV=np.median(met),
                             p90_met_GeV=np.quantile(met, 0.9), median_j1_pt_GeV=np.median(e[prefix + "j1_pt"]),
                             median_abs_j1_eta=np.median(abs(e[prefix + "j1_eta"][valid_jets])),
                             multijet_fraction=s.fraction(high_mult), min_dphi_fail_fraction=s.fraction(dphi <= 0.5),
                             fraction_b_parton=s.fraction(abs(e["gen_jet_pid"]) == 5),
                             selected_fb=s.sigma * s.fraction(selected)))
    return rows


def tag_variation(samples):
    rows = []
    for s in samples.values():
        if s.meta["energy_TeV"] != 13.6:
            continue
        for cut in (250, 400, 500):
            nominal = masks(s)[-1] & (s.events["met"] > cut)
            alt = masks(s, alternate_b_tag=True)[-1] & (s.events["met"] > cut)
            rows.append(dict(sample=s.name, min_met_GeV=cut, run3_working_point_fb=s.sigma*s.fraction(nominal),
                             stock_delphes_working_point_fb=s.sigma*s.fraction(alt)))
    return rows


def run2_yields(samples):
    if not all(name in samples for name, _, _ in RUN2_MIX):
        return [], []
    source = HERE / "references" / "cms_exo_20_004.info"
    regions = ET.parse(source).getroot().findall("region")
    indices = {region.attrib["id"]: i for i, region in enumerate(regions)}
    assert len(indices) == 3 * len(RUN2_BINS)
    cov = np.zeros((len(regions), len(regions)))
    rows = []
    for region in regions:
        label = region.attrib["id"]
        index = indices[label]
        year, bin_number = label.split("_")[-2:]
        year, b = int(year), int(bin_number[3:])
        lumi = {2016: 36, 2017: 41, 2018: 60}[year]
        low, high = RUN2_BINS[b], (*RUN2_BINS[1:], np.inf)[b]
        loop, tree = 0.0, 0.0
        for name, lo, hi in RUN2_MIX:
            s = samples[name]
            e = s.events
            selected = masks(s)[-1] & (e["met"] >= low) & (e["met"] < high)
            selected &= (e["gen_met"] >= lo) & (e["gen_met"] < hi)
            if year == 2018:
                hem_met = (e["met"] >= 470) | (e["met_phi"] < -1.62) | (e["met_phi"] > -0.62)
                selected &= hem_met & (e["hem_jet_veto"] > 0)
            expected = lumi * s.sigma * s.fraction(selected)
            if "loop" in name:
                loop += expected
            else:
                tree += expected
        for entry in region.findall("covariance"):
            cov[index, indices[entry.attrib["region"]]] = float(entry.text)
        rows.append(dict(region=label, year=year, lumi_fb_inverse=lumi, met_low_GeV=low, met_high_GeV=high,
                         signal_loop=loop, signal_tree=tree, signal_total=loop + tree,
                         background=float(region.findtext("nb")), observed=int(float(region.findtext("nobs")))))
    assert np.allclose(cov, cov.T)
    scans = []
    for cut in RUN2_BINS:
        active = [i for i, r in enumerate(rows) if r["met_low_GeV"] >= cut]
        signal = sum(rows[i]["signal_total"] for i in active)
        bkg = sum(rows[i]["background"] for i in active)
        delta = math.sqrt(cov[np.ix_(active, active)].sum())
        scans.append(dict(min_met_GeV=cut, signal=signal, background=bkg, background_uncertainty=delta,
                          observed=sum(rows[i]["observed"] for i in active), signal_over_background=signal / bkg,
                          expected_ranking_proxy=signal / math.sqrt(bkg + delta**2)))
    return rows, scans


def stairs(ax, values, weights, bins, label, **kwargs):
    histogram, _ = np.histogram(values, bins=bins, weights=weights)
    density = histogram / weights.sum() / np.diff(bins)
    ax.stairs(density, bins, label=label, **kwargs)


def plot_kinematics(samples, directory):
    observables = (
        ("met", r"$p_T^{\rm miss}$ [GeV]", np.linspace(100, 800, 29)),
        ("j1_pt", r"$p_T(j_1)$ [GeV]", np.linspace(100, 800, 29)),
        ("j2_pt", r"$p_T(j_2)$ [GeV] (0 if absent)", np.linspace(0, 400, 21)),
        ("j1_eta", r"$|\eta(j_1)|$", np.linspace(0, 4.8, 25)),
        ("njets", r"$N_{\rm jets}$ ($p_T>30$ GeV, $|\eta|<4.7$)", np.arange(-0.5, 10.6)),
        ("min_dphi", r"$\min\Delta\phi(j,p_T^{\rm miss})$", np.linspace(0, math.pi, 25)),
        ("balance", r"$p_T(j_1)/p_T^{\rm miss}$", np.linspace(0, 2, 31)),
        ("response", r"$p_T^{\rm miss}/p_{T,\rm hard}^{\rm miss}$", np.linspace(0, 2, 31)),
    )
    sample_names = ("B_loop", "B_tree")
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.7), layout="constrained")
    for ax, (key, xlabel, bins) in zip(axes.flat, observables, strict=True):
        for label, color in zip(sample_names, ("#27678b", "#be552c"), strict=True):
            if label not in samples:
                continue
            s = samples[label]
            e = s.events
            for prefix, level, ls in (("shower_", "particle", "--"), ("", "reco", "-")):
                if key == "response":
                    value = e[prefix + "met"] / e["gen_met"]
                else:
                    value = abs(e[prefix + key]) if key == "j1_eta" else e[prefix + key]
                stairs(ax, value, s.weight, bins, f"{label[2:]} {level}", color=color, linestyle=ls)
            if key in ("met", "j1_pt"):
                column = "gen_met" if key == "met" else "gen_j1_pt"
                stairs(ax, e[column], s.weight, bins, f"{label[2:]} parton", color=color,
                       linestyle=":", alpha=0.7)
        if key in ("met", "j1_pt", "j2_pt", "njets"):
            ax.set_yscale("log")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Normalized density")
        ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8, ncols=2)
    fig.suptitle("Benchmark B, 13.6 TeV  |  hard jet generation threshold 200 GeV")
    fig.savefig(directory / "kinematics_B_13p6TeV.png", dpi=180)
    plt.close(fig)


def plot_cutflow(rows, directory):
    fig, ax = plt.subplots(figsize=(9, 4.4), layout="constrained")
    for label in ("A_loop", "B_loop", "C_loop", "B_tree", "C_tree"):
        group = [r for r in rows if r["sample"] == label]
        if group:
            ax.plot(np.arange(len(group)), [100 * r["efficiency"] for r in group], marker="o", label=label)
    ax.set_xticks(np.arange(len(STAGES)), STAGES, rotation=25, ha="right")
    ax.set(ylabel="Cumulative efficiency [%]", ylim=(0, 105), title="CMS Run 3 cutflow proxy, 13.6 TeV")
    ax.grid(alpha=0.25)
    ax.legend(ncols=2)
    fig.savefig(directory / "cutflow_13p6TeV.png", dpi=180)
    plt.close(fig)


def plot_threshold(rows, directory):
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5), layout="constrained")
    for ax, label in zip(axes, ("B_13p6", "B_13"), strict=True):
        group = [r for r in rows if r["benchmark"] == label and r["level"] == "reco"]
        if not group:
            continue
        for key, color in (("loop", "#27678b"), ("tree", "#be552c"), ("total", "#222222")):
            met = [r["min_met_GeV"] for r in group]
            rate = np.array([r[f"{key}_fb"] for r in group])
            ax.plot(met, np.where(rate > 0, rate, np.nan), "o-", label=key, color=color)
        bounds = [(r["mc_lo68_fb"], r["mc_hi68_fb"]) for r in group]
        lo, hi = np.asarray(bounds).T
        ax.fill_between(met, lo, hi, where=lo > 0, alpha=0.18, color="#222222", label="MC counting")
        ax.set(title=label.replace("_13p6", " at 13.6 TeV").replace("_13", " at 13 TeV"),
               xlabel=r"Minimum $p_T^{\rm miss}$ [GeV]", ylabel="Selected cross section [fb]", yscale="log")
        ax.grid(alpha=0.2)
        ax.legend()
    fig.savefig(directory / "selected_cross_section_vs_met.png", dpi=180)
    plt.close(fig)


def plot_run2_ranking(rows, directory):
    if not rows:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), layout="constrained")
    met = [r["min_met_GeV"] for r in rows]
    for key, ylabel, ax in (("expected_ranking_proxy", r"$S/\sqrt{B+\sigma_B^2}$", axes[0]),
                            ("signal_over_background", r"$S/B$", axes[1])):
        values = [r[key] for r in rows]
        ax.plot(met, values, "o-", color="#27678b")
        ax.set(xlabel=r"Minimum $p_T^{\rm miss}$ [GeV]", ylabel=ylabel)
        ax.grid(alpha=0.25)
    fig.suptitle("Benchmark B, CMS Run 2  |  inclusive threshold comparison")
    fig.savefig(directory / "cms_run2_cut_ranking.png", dpi=180)
    plt.close(fig)


def main():
    samples = {s.name: s for s in (Sample.load(path) for path in sorted((HERE / "results/events").glob("*.csv.gz"))
                                   if not path.name.endswith("_test.csv.gz"))}
    cutflow, thresholds, bins = region_rows(samples)
    mixed = mixed_thresholds(samples)
    run2_bins, run2_scan = run2_yields(samples)
    for name, rows in (("cutflow", cutflow), ("met_thresholds", thresholds), ("met_bins", bins),
                       ("combined_thresholds", mixed), ("migration", migration_rows(samples)),
                       ("kinematics", kinematic_rows(samples)), ("b_tag_variation_run3", tag_variation(samples)),
                       ("cms_run2_bin_yields", run2_bins), ("cms_run2_cut_ranking", run2_scan)):
        if rows:
            write_csv(name, rows)
    directory = HERE / "figures"
    directory.mkdir(exist_ok=True)
    plot_kinematics(samples, directory)
    plot_cutflow(cutflow, directory)
    plot_threshold(mixed, directory)
    plot_run2_ranking(run2_scan, directory)


if __name__ == "__main__":
    main()

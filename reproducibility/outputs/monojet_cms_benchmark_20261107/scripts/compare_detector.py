"""Compare the independent detector run against the CMS spin-1 cutflow and spectrum."""

import csv
import tarfile

import matplotlib.pyplot as plt
import numpy as np

from benchmark_fit import ARCHIVE, HERE, Fit, background, tables, write


LUMI = {2016: 35.9, 2017: 41.5, 2018: 59.7}
STAGES = {
    "Full sample": "full",
    "$p_{T}^{miss} > 250$ GeV": "met",
    "Electron veto": "electron",
    "Muon veto": "muon",
    "Tau veto": "tau",
    "B jet veto": "b",
    "Photon veto": "photon",
    "$\\Delta\\phi(jet,p_{T}^{miss}) > 0.5$ rad": "dphi",
    "Leading AK4 jet $p_{T} > 100$ GeV": "jet_pt",
    "Leading AK4 jet $\\eta < 2.4$": "jet_eta",
    "HCAL mitigation (jets)": "hem_jet",
    "HCAL mitigation ($\\phi^{miss}$)": "hem_phi",
}


def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def official_cutflow(archive, mass, year):
    rows, = [rows for meta, rows in tables(archive, "CutflowforMonojet,DM,spin-1mediator")
             if meta.get("Coupling") == "Vector" and meta.get("Mode") == "$\\chi\\chi+j$"
             and float(meta["$m_{med}$"]) == mass and float(meta["$m_{DM}$"]) == 1.
             and int(meta["Data-taking period"]) == year]
    return {r["Cut stage"]: float(r["Fraction of passing events"]) for r in rows}


def plot(flow, spectrum, mass=750):
    fig, (ax_flow, ax_spec) = plt.subplots(1, 2, figsize=(11.8, 4.7), layout="constrained")
    d = [r for r in flow if r["mass_GeV"] == mass and r["year"] == 2017 and r["stage"] in STAGES
         and r["stage"] != "Full sample" and not r["stage"].startswith("HCAL")]
    x = np.arange(len(d))
    ax_flow.plot(x, [r["CMS_conditional_on_met"] for r in d], "o-", color="#202020", label="CMS full simulation")
    ax_flow.plot(x, [r["ours_conditional_on_met"] for r in d], "s-", color="#256d9b", label="Independent LO + fast simulation")
    ax_flow.set(xticks=x, xticklabels=[STAGES[r["stage"]].replace("_", " ") for r in d],
                ylabel=r"Fraction of events surviving $p_T^{\rm miss}>250$ GeV", title="2017 cutflow after MET cut")
    ax_flow.tick_params(axis="x", labelrotation=38)
    ax_flow.legend(fontsize=8)
    ax_flow.grid(alpha=.2)

    s = [r for r in spectrum if r["mass_GeV"] == mass and r["year"] == 2017]
    edges = [r["met_low_GeV"] for r in s] + [1340.]
    observed = np.array([r["CMS_fraction"] for r in s])
    ours = np.array([r["ours_fraction"] for r in s])
    counts = np.array([r["ours_selected"] for r in s])
    err = np.sqrt(ours * (1 - ours) / counts.sum())
    ax_spec.stairs(np.where(observed > 0., observed, np.nan), edges, color="#202020", label="CMS full simulation")
    ax_spec.errorbar((np.array(edges[:-1])+edges[1:])/2, ours, yerr=err, fmt="s", ms=3,
                     color="#256d9b", label="Independent LO + fast simulation")
    ax_spec.set(yscale="log", xlabel=r"$p_T^{\rm miss}$ [GeV]", ylabel="Fraction of selected events per bin",
                title="2017 signal spectrum, unit-area comparison")
    ax_spec.grid(alpha=.2)
    ax_spec.legend(fontsize=8)
    fig.suptitle(f"CMS vector benchmark, $m_{{med}}={mass}$ GeV, $m_{{DM}}=1$ GeV, DM + QCD jets")
    fig.savefig(HERE / f"figures/vector_{mass}_detector_validation.png", dpi=210)


def main():
    results = HERE / "results"
    official = read(results / "official_vector_spectra.csv")
    detector_masses = sorted(int(f.name.split("_")[1]) for f in results.glob("vector_*_hist.csv"))
    assert detector_masses
    flow, spectrum, summary = [], [], []
    with tarfile.open(ARCHIVE) as archive:
        labels, b, n, cov = background(archive)
        fit = Fit(b[:66], n[:66], cov[:66, :66])
        for mass in detector_masses:
            raw = {r["stage"]: r for r in read(results / f"vector_{mass}_flow.csv")}
            reco = read(results / f"vector_{mass}_hist.csv")
            n_gen = int(raw["full"]["generated"])
            cross = float(raw["full"]["cross_pb"])
            cross_err = float(raw["full"]["integration_error_pb"])
            if n_gen <= 0 or cross <= 0:
                raise ValueError((mass, n_gen, cross))
            counts_by_year, cms_templates, sim_templates = {}, {}, {}
            for year in LUMI:
                shape = [r for r in official if float(r["mass_GeV"]) == mass and r["mode"] == "DM + QCD jets"
                         and r["label"].startswith(f"monojet_{year}_")]
                cms_qcd = np.array([float(r["cms_yield"]) for r in shape])
                assert np.array_equal([float(r["met_low"]) for r in shape], [float(r["met_low"]) for r in reco])
                counts = np.array([int(r[f"count_{max(2017, year)}"]) for r in reco])
                y = counts * cross * 1000 * LUMI[year] / n_gen
                counts_by_year[year] = counts
                cms_templates[year], sim_templates[year] = cms_qcd, y
                for i, (ref, pred, low) in enumerate(zip(cms_qcd, y, reco)):
                    spectrum.append(dict(mass_GeV=mass, year=year, bin=i, met_low_GeV=float(low["met_low"]),
                                         CMS_yield=ref, ours_yield=pred, ours_selected=counts[i],
                                         CMS_fraction=ref/cms_qcd.sum(), ours_fraction=pred/y.sum(),
                                         absolute_ratio=pred/ref if ref > 0. else float("nan"),
                                         shape_ratio=(pred/y.sum())/(ref/cms_qcd.sum()) if ref > 0. else float("nan")))
                if year != 2016:
                    cf = official_cutflow(archive, mass, year)
                    c_met = cf["$p_{T}^{miss} > 250$ GeV"]
                    s_met = int(raw["met"]["count"])
                    last = "jet_eta" if year == 2017 else "hem_phi"
                    for stage, value in cf.items():
                        key = STAGES.get(stage)
                        if year == 2017 and key in ("hem_jet", "hem_phi"):
                            key = None
                        count = int(raw[key]["count"]) if key is not None else float("nan")
                        flow.append(dict(mass_GeV=mass, year=year, stage=stage, CMS_fraction=value,
                                         ours_fraction=count/n_gen, ours_count=count, generated=n_gen,
                                         CMS_conditional_on_met=value/c_met if stage not in ("Full sample", "Trigger emulation") else float("nan"),
                                         ours_conditional_on_met=count/s_met if stage != "Full sample" else float("nan")))
                    acc = int(raw[last]["count"])/n_gen
                    summary.append(dict(mass_GeV=mass, year=year, generated=n_gen, cross_pb=cross,
                                        CMS_full_acceptance=list(cf.values())[-1], ours_acceptance=acc,
                                        CMS_postMET_efficiency=list(cf.values())[-1]/c_met,
                                        ours_postMET_efficiency=int(raw[last]["count"])/s_met,
                                        yield_ratio=y.sum()/cms_qcd.sum(),
                                        tail_fraction_CMS=cms_qcd[9:].sum()/cms_qcd.sum(),
                                        tail_fraction_ours=y[9:].sum()/y.sum()))

            official_sum = np.concatenate([cms_templates[year] for year in LUMI])
            sim_sum = np.concatenate([sim_templates[year] for year in LUMI])
            other = {key: 0. for key in labels[:66]}
            for row in official:
                if float(row["mass_GeV"]) == mass and row["mode"] != "DM + QCD jets":
                    other[row["label"]] += float(row["cms_yield"])
            extra = np.array(list(other.values()))
            # Both samples use the same QCD hard events in 2016 and 2017.
            # The 2018 events form a subset of those bins after the HEM veto.
            a, h = counts_by_year[2017], counts_by_year[2018]
            assert np.all(h <= a)
            probabilities = np.r_[n_gen-a.sum(), a-h, h] / n_gen
            response = np.zeros((66, 45))
            for i, year in enumerate(LUMI):
                sl = slice(i*22, (i+1)*22)
                response[sl, 23:] = np.eye(22)*LUMI[year]
                if year != 2018:
                    response[sl, 1:23] = np.eye(22)*LUMI[year]
            signal_cov = (1000*cross)**2/n_gen * response @ (
                np.diag(probabilities) - np.outer(probabilities, probabilities)) @ response.T
            signal_cov += np.outer(sim_sum, sim_sum) * (cross_err/cross)**2
            normalized = np.concatenate([sim_templates[year]*cms_templates[year].sum()/sim_templates[year].sum()
                                         for year in LUMI])
            variants = (("CMS_QCD", official_sum, None), ("independent_QCD", sim_sum, signal_cov),
                        ("independent_QCD_fixed", sim_sum, None),
                        ("shape_only_QCD", normalized, None))
            for tag, qcd, uncertainty in variants:
                exp, obs, _ = fit.upper(np.maximum(qcd + extra, 0.), uncertainty)
                for entry in summary:
                    if entry["mass_GeV"] == mass:
                        entry[f"{tag}_mu95_expected"] = exp
                        entry[f"{tag}_mu95_observed"] = obs
    write(results / "detector_cutflow_comparison.csv", flow)
    write(results / "detector_spectrum_comparison.csv", spectrum)
    write(results / "detector_summary.csv", summary)
    for mass in detector_masses:
        plot(flow, spectrum, mass)
    for row in summary:
        print(row)


if __name__ == "__main__":
    main()

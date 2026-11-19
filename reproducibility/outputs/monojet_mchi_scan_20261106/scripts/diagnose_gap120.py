"""Diagnose the observed monojet contour at the 120 GeV signal-template node."""
import json

import numpy as np

from assess import CMS, RESULTS, read, write
from expected_scan import cms_inputs, load_templates, template_covariance, to_yields
from observed_fit import ObservedFit
from scan_observed import PhysicalAsimov


OUT = RESULTS/"gap120"


def channel_inputs(group):
    signal = {name:to_yields(counts,xsec) for name,(counts,xsec,error) in group.items()}
    shape = {name:template_covariance(counts,xsec,0.) for name,(counts,xsec,error) in group.items()}
    rate = {name:np.outer(signal[name],signal[name])*(error/xsec)**2
            for name,(counts,xsec,error) in group.items()}
    return signal,shape,rate


def summarize_fit(label,data,background,bkg_cov,signal,signal_cov,scale):
    fitter = ObservedFit(data,background,bkg_cov)
    expected = PhysicalAsimov(background,bkg_cov)
    conditional = PhysicalAsimov(fitter.profile(0.,np.zeros_like(data)).mean,bkg_cov)
    e = expected.upper(signal,signal_cov)
    o,hat,q,qa = fitter.upper(signal,signal_cov,e,conditional)
    return dict(case=label,expected_nu95=e,observed_nu95=o,observed_nu_hat=hat,
                qtilde_at_95=q,qA_at_95=qa,expected_mu95=e/scale,observed_mu95=o/scale)


def main():
    OUT.mkdir(exist_ok=True)
    records,asy,_ = cms_inputs()
    b,C = asy.b,asy.covariance
    data = np.array([int(r["observed"]) for r in records],float)
    fitter = ObservedFit(data,b,C)
    postfit = fitter.profile(0.,np.zeros_like(b)).mean
    templates = load_templates(CMS/"templates")
    components,shape,rate = channel_inputs(templates[120.])
    signal = sum(components.values())
    shape_cov = sum(shape.values())
    rate_cov = sum(rate.values())
    total = shape_cov+rate_cov
    with np.load(CMS/"results/node_signal_covariances.npz") as stored:
        nodes,covs = stored["mass_GeV"],stored["covariance"]
    assert np.allclose(total,covs[nodes==120][0],rtol=1e-11,atol=1e-12)
    neighbors = [channel_inputs(templates[m]) for m in (105.,135.)]
    neighbor_signal = .5*sum(sum(item[0].values()) for item in neighbors)
    neighbor_cov = .25*sum(covs[nodes==m][0] for m in (105.,135.))
    plane = read(RESULTS/"gt_mv_observed_heatmap.csv")
    band = plane[(plane["mass_GeV"]==120)&np.isfinite(plane["observed_mu95_mc_profiled"])]
    best = band[np.argmin(band["observed_mu95_mc_profiled"])]
    scale = best["gt_LZ"]**2*best["BR_invisible"]

    variants = [
        ("fixed_template",signal,None),("all_mc",signal,total),
        ("shape_only",signal,shape_cov),("integration_rate_only",signal,rate_cov),
        ("loop_bulk_only",signal,shape["loop"]+rate["loop"]),
        ("all_except_loop_bulk",signal,total-shape["loop"]-rate["loop"]),
        ("loop_tail_only",signal,shape["loop_hard"]+rate["loop_hard"]),
        ("tree_both_only",signal,sum(shape[k]+rate[k] for k in ("jet_tree","jet_tree_hard"))),
        ("shape_half_keep_rate",signal,shape_cov/2+rate_cov),
        ("shape_quarter_keep_rate",signal,shape_cov/4+rate_cov),
        ("shape_tenth_keep_rate",signal,shape_cov/10+rate_cov),
        ("neighbor_interpolated_cov_only",signal,neighbor_cov),
        ("neighbor_interpolated_signal_only",neighbor_signal,total),
        ("skip_120_interpolate_105_135",neighbor_signal,neighbor_cov),
    ]
    rows = [summarize_fit(name,data,b,C,s,c,scale) for name,s,c in variants]
    nu = rows[1]["observed_nu95"]
    fit = fitter.profile(nu,signal,total)
    assert fit.active_bins==0
    score = 1-data/fit.mean
    dark_shifts = {key:-nu*(shape[key]+rate[key])@score for key in components}
    pulls = (data-postfit)/np.sqrt(postfit)
    bins = []
    for i,row in enumerate(records):
        bins.append(dict(region=row["region"],year=row["year"],met_low_GeV=row["met_low_GeV"],
                         met_high_GeV=row["met_high_GeV"],observed=int(data[i]),control_background=b[i],
                         fitted_background_mu0=postfit[i],residual_over_poisson_sd=pulls[i],
                         signal_ref=signal[i],signal_mc_sd=np.sqrt(total[i,i]),
                         observed_fit_signal_shift=sum(x[i] for x in dark_shifts.values()),
                         loop_bulk_signal_ref=components["loop"][i],
                         loop_bulk_signal_shift=dark_shifts["loop"][i],
                         signal_shift_alignment=-sum(x[i] for x in dark_shifts.values())*score[i]))
    write(OUT/"bin_diagnostics.csv",bins)
    write(OUT/"fit_variants.csv",rows)

    # Neutralize selected observed fluctuations while keeping the full fit and covariance.
    groups = {}
    for year in (2016,2017,2018):
        groups[f"year_{year}"] = np.array([int(r["year"])==year for r in records])
    energy = np.array([float(r["met_low_GeV"]) for r in records])
    for lo,hi in ((250,340),(340,470),(470,690),(690,1020),(1020,np.inf)):
        groups[f"MET_{lo}_{hi}"] = (energy>=lo)&(energy<hi)
    for i in np.argsort([r["signal_shift_alignment"] for r in bins])[-5:]:
        groups[records[i]["region"]] = np.arange(len(data))==i
    groups["all_bins"] = np.ones(len(data),bool)
    muted = [summarize_fit(label,np.where(mask,postfit,data),b,C,signal,total,scale)
             for label,mask in groups.items()]
    write(OUT/"neutralized_data.csv",muted)

    channel_rows = []
    for m in (105.,120.,135.):
        for name,(counts,xsec,error) in templates[m].items():
            events = counts[1:].reshape(22,2).sum(axis=1)
            channel_rows.append(dict(mass_GeV=m,channel=name,generated=int(counts.sum()),
                                     selected=int(events.sum()),selected_first_three=int(events[:3].sum()),
                                     selected_above_470=int(events[7:].sum()),relative_integration_error=error/xsec,
                                     sum_signal=float(to_yields(counts,xsec).sum())))
    write(OUT/"channel_counts.csv",channel_rows)
    contributions = {key:float(score@(shape[key]+rate[key])@score) for key in components}
    info = dict(selected_scale=float(scale),gt=float(best["gt_LZ"]),mchi=float(best["mchi_best_GeV"]),
                finite_mc_score_variance_by_component=contributions,
                shape_score_variance=float(score@shape_cov@score),
                integration_rate_score_variance=float(score@rate_cov@score))
    (OUT/"summary.json").write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps(info,indent=2))
    for row in [*rows,*muted]:
        print(row["case"],round(row["expected_mu95"],5),round(row["observed_mu95"],5))
    for row in channel_rows:
        if row["mass_GeV"]==120:
            print(row)


if __name__ == "__main__":
    main()

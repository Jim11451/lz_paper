"""Refit the 120 GeV neighborhood after adding independent loop-bulk events."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from assess import CMS, FIGURES, RESULTS, read, write
from diagnose_gap120 import OUT, channel_inputs, summarize_fit
from expected_scan import cms_inputs, interpolate, interpolate_covariance, load_templates
from observed_fit import ObservedFit
from scan_observed import PhysicalAsimov, plot as plot_plane


def load_replica(path):
    with np.load(path) as data:
        assert str(data["channel"])=="loop" and float(data["mass"])==120.
        assert float(data["alignment"])<.005
        return data["counts"],float(data["cross"]),float(data["cross_error"])


def merge(samples):
    counts = sum(row[0] for row in samples)
    xs = np.array([row[1] for row in samples])
    weights = np.array([row[2]**-2 for row in samples])
    cross = float(xs@weights/weights.sum())
    error = float(weights.sum()**-.5)
    return counts,cross,error


def combined_inputs(group):
    signal,shape,rate = channel_inputs(group)
    return sum(signal.values()),sum(shape.values())+sum(rate.values())


def fit_local(plane,refs,old,new,background,data):
    fitter = ObservedFit(data,background.b,background.covariance)
    expected = PhysicalAsimov(background.b,background.covariance)
    conditional = PhysicalAsimov(fitter.profile(0.,np.zeros_like(data)).mean,background.covariance)
    masses = np.unique(plane["mass_GeV"])
    local = masses[(masses>105.)&(masses<135.)]
    s = interpolate(local,np.array([105.,120.,135.]),np.array([old[0][0],new[0],old[2][0]]))
    cov = interpolate_covariance(local,np.array([105.,120.,135.]),np.array([old[0][1],new[1],old[2][1]]))
    by_mass = {}
    limits = []
    for m,s0,c0 in zip(local,s,cov,strict=True):
        en = expected.upper(s0)
        ec = expected.upper(s0,c0)
        on,_,_,_ = fitter.upper(s0,None,en,conditional)
        oc,hat,_,_ = fitter.upper(s0,c0,ec,conditional)
        by_mass[m] = (en,ec,on,oc,hat)
        available = plane[(plane["mass_GeV"]==m)&np.isfinite(plane["observed_mu95_mc_profiled"])]
        scale = max(available["gt_LZ"]**2*available["BR_invisible"])
        ref = refs[refs["mass_GeV"]==m][0]
        limits.append(dict(mass_GeV=float(m),old_expected=float(ref["expected95_mc"]/scale),
                           old_observed=float(ref["observed95_mc"]/scale),
                           new_expected=ec/scale,new_observed=oc/scale,new_observed_fixed=on/scale))
    rows = []
    for row in plane:
        fields = dict(zip(row.dtype.names,map(float,row),strict=True))
        m = row["mass_GeV"]
        if m in by_mass and np.isfinite(row["observed_mu95_mc_profiled"]):
            scale = row["gt_LZ"]**2*row["BR_invisible"]
            for key,value in zip(("expected_mu95","expected_mu95_mc_profiled","observed_mu95",
                                  "observed_mu95_mc_profiled","observed_muhat_mc_profiled"),
                                 by_mass[m],strict=True):
                fields[key] = value/scale
        rows.append(fields)
    write(OUT/"local_mass_limits.csv",limits)
    write(OUT/"gt_mv_observed_highstat.csv",rows)
    gts = np.unique(plane["gt_LZ"])
    shape = len(masses),len(gts)
    e,o = [np.array([r[key] for r in rows]).reshape(shape).T for key in
           ("expected_mu95_mc_profiled","observed_mu95_mc_profiled")]
    plot_plane(masses,gts,e,o,"gt_mv_observed_cms_highstat120")
    return limits,int(np.sum(o<1))


def plot(limits, original, updated_counts, updated_label):
    fig,(ax,counts) = plt.subplots(1,2,figsize=(11.1,4.3),layout="constrained")
    m = [r["mass_GeV"] for r in limits]
    ax.plot(m,[r["old_observed"] for r in limits],marker="o",ms=3,color="#aa4936",label="Original observed")
    ax.plot(m,[r["new_observed"] for r in limits],marker="o",ms=3,color="#176494",label="With independent extra MC")
    ax.plot(m,[r["new_expected"] for r in limits],ls="--",color="#718ca3",label="Updated median expected")
    ax.axhline(1,ls=":",lw=1.1,color=".22")
    ax.axvline(120,ls=":",lw=.85,color=".55")
    ax.set(xlabel=r"$M_V$ [GeV]",ylabel=r"Minimum $\mu_{95}$ on the Planck band",
           title="Local CMS limit")
    ax.legend(fontsize=8.1)
    low = np.array([250,280,310,340,370,400,430,470,510,550,590,640,690,740,790,840,900,960,1020,1090,1160,1250])
    for label,c,color in (("Original",original[0],"#aa4936"),(updated_label,updated_counts,"#176494")):
        values = c[1:].reshape(22,2).sum(axis=1)
        bins = values>0
        counts.plot(low[bins],values[bins],marker="o",ms=3,ls="-",color=color,label=label)
    counts.axvline(470,ls=":",lw=.9,color=".48")
    counts.set(xlim=(240,820),yscale="log",xlabel="Reconstructed MET bin lower edge [GeV]",
               ylabel="Selected MC events per bin",title="120 GeV loop bulk")
    counts.legend(fontsize=8.1)
    for ax in (ax,counts):
        ax.grid(alpha=.19)
    fig.suptitle("Checking the 120 GeV gap with independent signal simulation",fontsize=13)
    for extension in ("png","pdf"):
        fig.savefig(FIGURES/f"observed_gap120_diagnosis.{extension}",dpi=225)
    plt.close(fig)


def main():
    records,background,_ = cms_inputs()
    data = np.array([int(r["observed"]) for r in records])
    source = load_templates(CMS/"templates")
    old = source[120.]["loop"]
    paths = [OUT/"replicas"/f"loop_m{index}.npz" for index in (16,17)]
    replicas = {path.stem:load_replica(path) for path in paths if path.is_file()}
    high_path,low_path = (OUT/"replicas"/name for name in ("loop_m18.npz","loop_below230.npz"))
    shapes = dict(original=old,**replicas)
    if replicas:
        shapes["pooled"] = merge([old,*replicas.values()])
    if len(replicas)==2:
        shapes["new_only"] = merge(list(replicas.values()))
    scale = json.loads((OUT/"summary.json").read_text())["selected_scale"]
    rows = []
    for label,sample in shapes.items():
        signal,cov = combined_inputs(dict(source[120.],loop=sample))
        row = summarize_fit(label,data,background.b,background.covariance,signal,cov,scale)
        counts,cross,error = sample
        row.update(generated=int(counts.sum()),selected=int(counts[1:].sum()),
                   selected_above_470=int(counts[1:].reshape(22,2)[7:].sum()),cross_pb=cross,error_pb=error)
        rows.append(row)
    plane = read(RESULTS/"gt_mv_observed_heatmap.csv")
    refs = read(RESULTS/"cms_observed_reference_limits.csv")
    neighbors = [combined_inputs(source[m]) for m in (105.,120.,135.)]
    if high_path.is_file() and low_path.is_file():
        low,high = load_replica(low_path),load_replica(high_path)
        new = combined_inputs(dict(source[120.],loop=low,loop_enriched=high))
        counts, updated_label = low[0]+high[0],"Stratified"
        enriched = summarize_fit("stratified",data,background.b,background.covariance,*new,scale)
        enriched.update(generated=int(counts.sum()),selected=int(counts[1:].sum()),
                        selected_above_470=int(counts[1:].reshape(22,2)[7:].sum()),
                        cross_pb=float("nan"),error_pb=float("nan"))
        rows.append(enriched)
    else:
        assert replicas
        pooled = shapes["pooled"]
        new = combined_inputs(dict(source[120.],loop=pooled))
        counts,updated_label = pooled[0],"Pooled"
    write(OUT/"replica_comparison.csv",rows)
    crossover = []
    for label,signal,cov in (("old_signal_new_cov",neighbors[1][0],new[1]),
                             ("new_signal_old_cov",new[0],neighbors[1][1])):
        crossover.append(summarize_fit(label,data,background.b,background.covariance,signal,cov,scale))
    write(OUT/"covariance_crossover.csv",crossover)
    limits,n = fit_local(plane,refs,neighbors,new,background,data)
    plot(limits,old,counts,updated_label)
    print(json.dumps(dict(replicas=rows,crossover=crossover,grid_cells_observed_sensitive=n),indent=2),flush=True)


if __name__ == "__main__":
    main()

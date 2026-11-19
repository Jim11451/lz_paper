"""Render the mediator-mass versus top-coupling plane after LZ and Planck."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, NullFormatter

from assess import FIGURES, RESULTS, ReferenceLimits, read, write


def evaluate():
    source = read(RESULTS/"gt_mv/thermal_plane.csv")
    mv = np.unique(source["mass_GeV"])
    gt = np.unique(source["gt_LZ"])
    shape = len(mv),len(gt)
    assert np.array_equal(source["mass_GeV"].reshape(shape)[:,0],mv)
    assert np.array_equal(source["gt_LZ"].reshape(shape)[0],gt)
    ok = source["n_intervals"]>0
    assert np.all((source["BR_invisible"][ok]>0)&(source["BR_invisible"][ok]<1.0001))
    assert np.all((source["gchi_best"][ok]>=.1-1e-8)&(source["gchi_best"][ok]<=1.5+1e-8))
    assert np.all((source["omega_h2_best"][ok]>=.1176-2e-6)&(source["omega_h2_best"][ok]<=.1224+2e-6))
    assert np.all(source["width_GeV"][ok]/source["mass_GeV"][ok]<.03)
    limits = ReferenceLimits(grid=mv)
    nu,nu_mc = limits.lookup(mv)
    k = source["gt_LZ"]**2*np.minimum(1.,source["BR_invisible"])
    nom = np.repeat(nu,len(gt))/k
    prof = np.repeat(nu_mc,len(gt))/k

    keys = ("mass_GeV","gt_LZ","mchi_low_GeV","mchi_high_GeV","mchi_best_GeV","gchi_best",
            "omega_h2_best","width_GeV","BR_invisible","n_intervals")
    out = [dict({key:float(r[key]) for key in keys},expected_mu95=float(a),
                expected_mu95_mc_profiled=float(b)) for r,a,b in zip(source,nom,prof,strict=True)]
    write(RESULTS/"gt_mv_heatmap.csv",out)
    best = out[int(np.nanargmin(prof))]
    tested = ok & (prof<1)
    summary = dict(grid_pixels=len(source),valid_pixels=int(ok.sum()),expected_sensitive_pixels=int(tested.sum()),
                   strongest=best,minimum_scanned_MV_with_mu95_below_one=float(min(source["mass_GeV"][tested])),
                   n_micromegas_evaluations=int(source["n_calls"].sum()))
    (RESULTS/"gt_mv_heatmap_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    return mv,gt,prof.reshape(shape).T,source["mchi_best_GeV"].reshape(shape).T


def plot(mv,gt,mu,mchi):
    fig,ax = plt.subplots(figsize=(9.5,5.45),layout="constrained")
    ax.set_facecolor("#e9ebed")
    norm = TwoSlopeNorm(vmin=np.log10(.16),vcenter=0,vmax=np.log10(40))
    img = ax.pcolormesh(mv,gt,np.log10(mu),cmap="RdBu",norm=norm,shading="nearest",rasterized=True)
    ax.contour(mv,gt,mu,levels=[1],colors="#222127",linewidths=1.45)
    contours = ax.contour(mv,gt,mchi,levels=[35,40,44],colors="#484f62",linewidths=.7,linestyles=":")
    labels = ax.clabel(contours,fmt=lambda v:fr"$m_\chi={v:g}$ GeV",fontsize=8.6,inline=False,
                       manual=[(88,.52),(112,.85),(152,1.95)])
    for label in labels:
        label.set_rotation(0)
        label.set_bbox(dict(facecolor="white",edgecolor="none",alpha=.82,pad=1.5))
    ax.axhline(gt[-1],color="#747b84",lw=.9,ls="--")
    ax.set(xlim=(72,200),ylim=(.1,3.78),yscale="log",
           xlabel=r"$M_V$ [GeV]",ylabel=r"Top coupling $g_t$",
           xticks=[75,90,110,130,150,175,200])
    ax.set_yticks([.1,.2,.4,.7,1,2,np.sqrt(4*np.pi)],
                  labels=["0.1","0.2","0.4","0.7","1","2",r"$\sqrt{4\pi}$"])
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(direction="out")
    ax.grid(alpha=.17,lw=.7)
    ax.set_axisbelow(True)
    ticks = [.2,.35,.6,1,2,5,10,20,40]
    bar = fig.colorbar(img,ax=ax,ticks=np.log10(ticks),extend="max",pad=.025)
    bar.ax.set_yticklabels([f"{x:g}" for x in ticks])
    bar.set_label(r"Minimum median expected $\mu_{95}$")
    ax.legend(handles=[Line2D([],[],color="#222127",lw=1.45,label=r"CMS expected $\mu_{95}=1$"),
                       Patch(facecolor="#e9ebed",edgecolor="#bbc0c4",label="No joint solution within the scan")],
              loc="lower right",fontsize=8.8,framealpha=.95)
    ax.set_title(r"CMS monojet on the LZ and Planck solution plane",fontsize=14,weight="bold",pad=11)
    fig.supxlabel(r"On-shell vector  |  $\Delta m=1$ MeV, $f_2=0.5$  |  66-bin Asimov fit with finite MC profiled",
                  fontsize=9.5,color="#4c5563")
    FIGURES.mkdir(exist_ok=True)
    for ext in ("png","pdf"):
        fig.savefig(FIGURES/f"gt_mv_relic_cms_heatmap.{ext}",dpi=230)
    plt.close(fig)


if __name__ == "__main__":
    plot(*evaluate())

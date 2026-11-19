"""Draw the LZ, Planck, and CMS result directly in the two mass coordinates."""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE/"results"
FIGURES = HERE/"figures"
BLUE = "#6e9cc5"
BLUE_EDGE = "#315e87"
ORANGE = "#eea46e"
ORANGE_EDGE = "#9e421f"
INK = "#263747"


def read(path):
    return np.atleast_1d(np.genfromtxt(path,names=True,delimiter=","))


def envelopes(rows):
    masses = defaultdict(list)
    for row in rows:
        masses[float(row["mchi_GeV"])].append(float(row["mass_GeV"]))
    return {key:(min(values),max(values)) for key,values in sorted(masses.items())}


def load():
    points = read(RESULTS/"equal_rate_band_cms.csv")
    selected = points[(points["cms_covered"]==1)&(points["expected_mu95_mc_profiled"]<1)]
    overlap = envelopes(selected)
    assert min(overlap)==36 and max(overlap)==46.25
    assert all(72 <= lo <= hi <= 200 for lo,hi in overlap.values())

    # Use the broad coupling scan for the full envelope, so that a targeted
    # refinement of the CMS crossing cannot artificially shrink the blue band.
    source = RESULTS/"equal"
    base = read(source/"relic_crossings.csv")
    grid = read(source/"relic_grid.csv")
    grid = grid[(grid["omega_h2"]>=.1176)&(grid["omega_h2"]<=.1224)]
    full = envelopes(np.concatenate([base[list(grid.dtype.names)],grid]))
    # At high mchi, the perturbativity bound already eliminates low-gchi solutions.
    for key,(lo,hi) in envelopes(points[points["mchi_GeV"]>=45.75]).items():
        if key in full:
            lo,hi = min(lo,full[key][0]),max(hi,full[key][1])
        full[key] = lo,hi
    full = dict(sorted(full.items()))
    mass = sorted(full)
    bounds = np.array(list(full.values()))
    data = []
    for mchi in sorted(set(mass)|set(overlap)):
        lo,hi = (np.interp(mchi,mass,arr) for arr in bounds.T)
        match = overlap.get(mchi)
        if match:
            lo,hi = min(lo,match[0]),max(hi,match[1])
        data.append(dict(mchi_GeV=mchi, planck_MV_low_GeV=lo, planck_MV_high_GeV=hi,
                         cms_overlap_MV_low_GeV=match[0] if match else "",
                         cms_overlap_MV_high_GeV=match[1] if match else "",
                         planck_envelope_interpolated=int(mchi not in full)))
    with (RESULTS/"mass_plane_projection.csv").open("w",newline="") as stream:
        writer = csv.DictWriter(stream,data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    benchmark = read(RESULTS/"equal_rate_mass_summary.csv")
    return data,{m:benchmark[benchmark["mchi_GeV"]==m][0] for m in (35,36,40,44)}


def plot(data, benchmarks):
    fig,(ax,zoom) = plt.subplots(1,2,figsize=(11.9,5.1),
                                gridspec_kw={"width_ratios":[1.2,1]},layout="constrained")
    mchi = [r["mchi_GeV"] for r in data]
    mlo,mhi = ([r[k] for r in data] for k in ("planck_MV_low_GeV","planck_MV_high_GeV"))
    overlap = [r for r in data if r["cms_overlap_MV_low_GeV"]!=""]
    x,lo,hi = ([r[k] for r in overlap] for k in ("mchi_GeV","cms_overlap_MV_low_GeV",
                                                "cms_overlap_MV_high_GeV"))
    for a in (ax,zoom):
        a.axhspan(0,72,color="#f1f2f4",zorder=0)
        a.axhspan(200,245,color="#f1f2f4",zorder=0)
        a.axhline(72,ls=":",color="#8f969e",lw=.85)
        a.axhline(200,ls=":",color="#8f969e",lw=.85)
        a.fill_between(mchi,mlo,mhi,facecolor=BLUE,edgecolor=BLUE_EDGE,
                       alpha=.74,linewidth=.8,zorder=3)
        a.fill_between(x,lo,hi,facecolor=ORANGE,edgecolor=ORANGE_EDGE,
                       linewidth=.75,zorder=4)
        a.set_xlabel(r"$m_{\chi_1}$ [GeV]")
        a.grid(alpha=.18,linewidth=.75)
        a.tick_params(direction="out")
        for side in ("top","right"):
            a.spines[side].set_visible(False)
    ax.plot([20,48],[40.001,96.001],color="#7b8791",ls="--",lw=.9)
    ax.set(xlim=(28,47.15),ylim=(66,238),ylabel=r"$M_V$ [GeV]",
           xticks=[28,32,36,40,44,47],yticks=[75,100,125,150,175,200,225],
           title="On-shell mass plane")
    ax.text(29.0,207.8,r"Above CMS template range ($M_V>200$ GeV)",
            fontsize=8.5,color="#626d77")
    ax.legend(handles=[
        Patch(facecolor=BLUE,edgecolor=BLUE_EDGE,alpha=.74,label=r"Planck relic band after LZ rate matching"),
        Patch(facecolor=ORANGE,edgecolor=ORANGE_EDGE,label=r"Overlap with CMS expected $\mu_{95}<1$"),
        Line2D([],[],color="#7b8791",ls="--",label=r"$V\to\chi_1\chi_2$ threshold"),
    ],loc="upper left",bbox_to_anchor=(.01,.8),fontsize=8.5,framealpha=.97)
    zoom.set(xlim=(34.45,38.5),ylim=(82.5,103.5),ylabel=r"$M_V$ [GeV]",
             xticks=[34.5,35,36,37,38],yticks=[85,90,95,100],title="Zoom near the first overlap")
    zoom.axvline(36,ls=":",color=ORANGE_EDGE,alpha=.8,lw=.85,zorder=1)
    for a,mchi,offset,align in [(zoom,35,(8,-29),"left"),(zoom,36,(8,-21),"left"),
                                (ax,40,(9,-9),"left"),(ax,44,(-10,10),"right")]:
        row = benchmarks[mchi]
        mv,mu = row["best_mv_GeV"],row["minimum_mu95_profiled"]
        edge = ORANGE_EDGE if mu<1 else BLUE_EDGE
        a.scatter(mchi,mv,s=30,facecolor="white",edgecolor=edge,linewidth=1.1,zorder=6)
        if mchi==36:
            label = f"First sampled overlap at {mchi:g} GeV"
        else:
            label = fr"{mchi:g} GeV, $\mu_{{95}}={mu:.2f}$"
        a.annotate(label,(mchi,mv),xytext=offset,textcoords="offset points",
                   ha=align,va="center",color=INK,fontsize=8.5,zorder=7)
    fig.suptitle(r"LZ, thermal relic density and CMS monojet in the mass plane",
                 fontsize=14,weight="bold",color=INK)
    fig.supxlabel(r"Projection over $g_\chi$  |  $\Delta m=1$ MeV, $f_2=0.5$  |  CMS median expected, finite MC profiled",
                  fontsize=9.5,color="#536372")
    FIGURES.mkdir(exist_ok=True)
    for ext in ("png","pdf"):
        fig.savefig(FIGURES/f"mchi_mv_projection.{ext}",dpi=235)
    plt.close(fig)


if __name__ == "__main__":
    plot(*load())

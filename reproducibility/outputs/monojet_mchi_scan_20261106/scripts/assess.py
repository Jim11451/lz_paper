"""Re-evaluate the CMS Run 2 monojet likelihood on the thermal band."""
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, NullFormatter


HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE/"results"
FIGURES = HERE/"figures"
CMS = HERE.parent/"monojet_expected_lz_scan_20261106"
sys.path.insert(0, str(CMS/"scripts"))
from expected_scan import cms_inputs, interpolate, interpolate_covariance, write


def read(path):
    return np.atleast_1d(np.genfromtxt(path, names=True, delimiter=","))


def width_dark(mv, mchi, gc):
    m2 = mchi + .001
    r1, r2 = (mchi/mv)**2, (m2/mv)**2
    threshold = np.maximum(0, (1-((mchi+m2)/mv)**2)*(1-((mchi-m2)/mv)**2))
    spin = 1-(r1+r2)/2-(r1-r2)**2/2+3*np.sqrt(r1*r2)
    return (gc/2)**2*mv/(12*np.pi)*np.sqrt(threshold)*spin


class ReferenceLimits:
    def __init__(self, grid=None):
        _, self.fit, old_b = cms_inputs()
        assert abs(self.fit.upper(old_b)-1.73685) < .0001
        with np.load(CMS/"results/node_signal_covariances.npz") as data:
            self.nodes = data["mass_GeV"]
            self.cov = data["covariance"]
        with (CMS/"results/cms66_signal_templates.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        assert np.array_equal(np.array([float(row["mass_GeV"]) for row in rows[::66]]), self.nodes)
        self.vectors = np.array([float(row["signal_total_ref"]) for row in rows]).reshape(-1,66)
        self.grid = np.unique(np.r_[np.linspace(72.,200.,1025) if grid is None else grid,self.nodes])
        signals = interpolate(self.grid,self.nodes,self.vectors)
        covs = interpolate_covariance(self.grid,self.nodes,self.cov)
        self.amplitudes = np.array([self.fit.upper(s) for s in signals])
        self.amplitudes_mc = np.array([self.fit.upper(s,c) for s,c in zip(signals,covs,strict=True)])

    def exact(self,mv):
        signal = interpolate([mv],self.nodes,self.vectors)[0]
        cov = interpolate_covariance(np.array([mv]),self.nodes,self.cov)[0]
        return self.fit.upper(signal),self.fit.upper(signal,cov)

    def lookup(self,mv):
        return (np.interp(mv,self.grid,table) for table in (self.amplitudes,self.amplitudes_mc))


def evaluate(rows, limits):
    mchi, mv, g, gt = (rows[k] for k in ("mchi_GeV","mass_GeV","gchi","gt_LZ"))
    width = rows["width_GeV"]
    branch = width_dark(mv,mchi,g)/width
    assert np.all((0 < branch) & (branch < 1.0001)), max(branch)
    branch = np.minimum(1.,branch)
    scale = gt**2*branch
    nu,nu_mc = limits.lookup(mv)
    valid = ((mv>=72.) & (mv<=200.) & (rows["width_over_mass"]<.03)
             & (rows["threshold_distance_over_width"]>=5) & (gt<=np.sqrt(4*np.pi)*(1+1e-12)))
    nom = np.where(valid,nu/scale,np.nan)
    mc = np.where(valid,nu_mc/scale,np.nan)
    return branch,scale,nom,mc,valid


def load_case(paths, limits, label):
    spectrum = {}
    data = {}
    for path in paths:
        recoils = read(path/"lz_mass_normalization.csv")
        for row in recoils:
            spectrum[row["mchi_GeV"]] = row
        for filename in ("relic_crossings","relic_grid"):
            values = read(path/f"{filename}.csv")
            values = values[(values["gchi"]>=.1)&(values["gchi"]<=1.5)]
            if filename == "relic_grid":
                values = values[(values["omega_h2"]>=.1176)&(values["omega_h2"]<=.1224)]
            for row in values:
                key = (row["mchi_GeV"],row["gchi"],row["mass_GeV"])
                data[key] = row
    keys = tuple(next(iter(data.values())).dtype.names[:9])
    rows = np.array([tuple(row[k] for k in keys) for row in data.values()],dtype=[(k,"f8") for k in keys])
    branch,scale,nom,mc,valid = evaluate(rows,limits)
    all_rows = []
    for i,row in enumerate(rows):
        x = {k:float(row[k]) for k in keys}
        x.update(BR_invisible=float(branch[i]), rate_scale=float(scale[i]), cms_covered=int(valid[i]),
                 expected_mu95=float(nom[i]),expected_mu95_mc_profiled=float(mc[i]))
        all_rows.append(x)
    summary = []
    for mchi in sorted(spectrum):
        rr = spectrum[mchi]
        selected = [row for row in all_rows if row["mchi_GeV"] == mchi]
        active = [row for row in selected if row["cms_covered"]]
        best = min(active,key=lambda r:r["expected_mu95_mc_profiled"]) if active else None
        n_below = 0
        for row in active:
            if row is best or min(abs(row[k]-1) for k in ("expected_mu95","expected_mu95_mc_profiled")) < .025:
                nu,nu_mc = limits.exact(row["mass_GeV"])
                for key, amplitude in (("expected_mu95",nu),("expected_mu95_mc_profiled",nu_mc)):
                    direct = amplitude/row["rate_scale"]
                    assert abs(row[key]/direct-1)<.002
                    row[key] = direct
            n_below += int(row["expected_mu95_mc_profiled"] < 1)
        if active:
            best = min(active,key=lambda r:r["expected_mu95_mc_profiled"])
        summary.append(dict(mchi_GeV=float(mchi),relic_points=len(selected),cms_points=len(active),
                            cms_profiled_below_one=n_below,
                            minimum_mass_GeV=min((r["mass_GeV"] for r in selected),default=mathnan),
                            maximum_mass_GeV=max((r["mass_GeV"] for r in selected),default=mathnan),
                            minimum_mu95_nominal=min((r["expected_mu95"] for r in active),default=mathnan),
                            minimum_mu95_profiled=best["expected_mu95_mc_profiled"] if best else mathnan,
                            best_mv_GeV=best["mass_GeV"] if best else mathnan,
                            best_gchi=best["gchi"] if best else mathnan,
                            best_gt=best["gt_LZ"] if best else mathnan,
                            best_width_over_mass=best["width_over_mass"] if best else mathnan,
                            best_threshold_distance_over_width=best["threshold_distance_over_width"] if best else mathnan,
                            kappa=float(rr[f"kappa_{label}"]),
                            truth_NSB_at_equal_rate=1.120444105*float(rr["sb_over_roi"]),
                            gaussian_NSB_at_profile=float(rr["gauss_sb_over_roi"]/(1+rr["gauss_sb_over_roi"])),
                            shape_q_truth=0.,shape_q_gauss=0.))
    for k in ("truth","gauss"):
        d = [float(spectrum[row["mchi_GeV"]][f"{k}_shape_density_per_keV"]) for row in summary]
        best_d = max(d)
        for row,v in zip(summary,d,strict=True):
            row[f"shape_q_{k}"]=float(-2*np.log(v/best_d)) if v>0 else float("inf")
    write(RESULTS/f"{label}_mass_summary.csv",summary)
    write(RESULTS/f"{label}_band_cms.csv",all_rows)
    return summary,all_rows


mathnan = float("nan")


def intervals(summary,key):
    groups = []
    last_passed = False
    for row in summary:
        passed = row[key] < 1
        if passed and not last_passed:
            groups.append([row["mchi_GeV"], row["mchi_GeV"]])
        if passed:
            groups[-1][-1] = row["mchi_GeV"]
        last_passed = passed
    return groups


def plot_slices(limits):
    source = RESULTS/"equal"
    recoil = read(source/"lz_mass_normalization.csv")
    roots = read(source/"relic_crossings.csv")
    mv, gc = np.meshgrid(limits.grid,np.geomspace(.1,1.5,241))
    nominal, profiled = limits.lookup(limits.grid)
    fig, axes = plt.subplots(1,3,sharex=True,sharey=True,figsize=(13,4.65),layout="constrained")
    norm = TwoSlopeNorm(vmin=-1,vcenter=0,vmax=1.5)
    for ax,mchi in zip(axes,(35.,40.,44.),strict=True):
        kappa = recoil[recoil["mchi_GeV"] == mchi]["kappa_equal_rate"][0]
        gt = kappa*mv**2/gc
        quark_width = np.zeros_like(mv)
        for mq in (.0022,.0047,.096,1.27,4.18):
            z = (mq/mv)**2
            quark_width += 3*(gt*mq/172)**2*mv/(12*np.pi)*(1+2*z)*np.sqrt(1-4*z)
        invisible = width_dark(mv,mchi,gc)
        total = quark_width+invisible
        valid = (gt<=np.sqrt(4*np.pi))&(total/mv<.03)&((mv-2*mchi-.001)>=5*total)
        scale = np.where(valid,gt**2*invisible/total,np.nan)
        expected = nominal[None,:]/scale
        expected_mc = profiled[None,:]/scale
        heat = ax.pcolormesh(mv,gc,np.log10(expected),shading="auto",cmap="RdBu",
                             norm=norm,rasterized=True)
        ax.contour(mv,gc,expected,[1],colors="#232329",linewidths=1.1)
        ax.contour(mv,gc,expected_mc,[1],colors="#232329",linewidths=1.1,linestyles="--")
        b = roots[roots["mchi_GeV"]==mchi]
        series = {level:{r["gchi"]:r["mass_GeV"] for r in b if r["target_omega_h2"]==level}
                  for level in (.1176,.12,.1224)}
        coupled = sorted(set.intersection(*(set(s) for s in series.values())))
        lo,center,hi = [[series[level][g] for g in coupled] for level in series]
        ax.fill_betweenx(coupled,lo,hi,color="#ffce55",edgecolor="#29272a",linewidth=.5,zorder=5)
        ax.plot(center,coupled,color="#794000",linewidth=.65,zorder=6)
        # The centerline can approach the perturbativity boundary before the upper edge does.
        for g,mass in series[.12].items():
            if g not in coupled:
                ax.scatter(mass,g,color="#ffce55",edgecolor="#29272a",s=7,linewidth=.4,zorder=6)
        ax.set(xlim=(72,200),ylim=(.1,1.5),yscale="log",xlabel=r"$M_V$ [GeV]",
               title=fr"$m_{{\chi_1}}={mchi:g}$ GeV")
        ax.set_facecolor("#eaeaea")
        ax.set_yticks([.1,.2,.3,.5,1,1.5])
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
    axes[0].set_ylabel(r"$g_\chi$")
    axes[0].legend(handles=[
        Patch(facecolor="#ffce55",edgecolor="#29272a",label=r"Planck $\pm2\sigma$"),
        Line2D([],[],color="#232329",label=r"Nominal $\mu_{95}=1$"),
        Line2D([],[],color="#232329",ls="--",label=r"Finite MC profiled $\mu_{95}=1$")
    ],fontsize=8,loc="upper right")
    ticks = [.1,.2,.5,1,2,5,10,20]
    cbar = fig.colorbar(heat,ax=axes,ticks=np.log10(ticks),extend="both",pad=.02)
    cbar.ax.set_yticklabels([f"{v:g}" for v in ticks])
    cbar.set_label(r"Median expected $\mu_{95}$ (nominal)")
    fig.suptitle("How the Planck band moves across the CMS contours with dark mass",fontsize=13)
    for ext in ("png","pdf"):
        fig.savefig(FIGURES/f"mchi_relic_cms_slices.{ext}",dpi=220)
    plt.close(fig)


def plot(cases):
    equal, bands = cases["equal_rate"]
    fig, axes = plt.subplots(2,2,figsize=(12,8),layout="constrained")
    mass_ax, sensitivity, normalize_ax, lz = axes.ravel()
    mv = np.array([r["mass_GeV"] for r in bands])
    mchi = np.array([r["mchi_GeV"] for r in bands])
    mu = np.array([r["expected_mu95_mc_profiled"] for r in bands])
    valid = np.isfinite(mu)
    mass_ax.axhspan(40,72,color=".94",zorder=0)
    mass_ax.axhspan(200,210,color=".94",zorder=0)
    mass_ax.axhline(72,color=".65",ls=":",lw=1)
    mass_ax.axhline(200,color=".65",ls=":",lw=1)
    mass_ax.plot([20,100],[40,200],color=".65",ls="--",lw=1,label=r"$M_V=2m_\chi$")
    mass_ax.scatter(mchi[~valid],mv[~valid],s=4,color=".60",alpha=.6,label="Outside CMS template range / selection")
    sc=mass_ax.scatter(mchi[valid],mv[valid],c=np.log10(mu[valid]),s=9,cmap="RdBu",
                       norm=TwoSlopeNorm(vmin=-1.4,vcenter=0,vmax=1.6),linewidths=0,
                       label="Planck band with CMS templates")
    cb=fig.colorbar(sc,ax=mass_ax,pad=.02,extend="both",ticks=np.log10([.05,.1,.3,1,3,10,30]))
    cb.ax.set_yticklabels(["0.05","0.1","0.3","1","3","10","30"])
    cb.set_label(r"Expected $\mu_{95}$, finite MC profiled")
    mass_ax.set(ylabel=r"$M_V$ [GeV]",ylim=(42,210),title="On-shell Planck band, LZ equal truth rate")
    mass_ax.legend(fontsize=7.1,loc="upper left")

    styles = {"equal_rate":("#2e5e9a","LZ equal truth rate"),
              "gaussian_profile":("#bc592c","LZ one-event Gaussian proxy")}
    for label,(rows,_) in cases.items():
        x = np.array([r["mchi_GeV"] for r in rows])
        color,text=styles[label]
        v = np.array([r["minimum_mu95_profiled"] for r in rows])
        sensitivity.plot(x,v,color=color,lw=2,label=text)
        sensitivity.scatter(x[v<1],v[v<1],s=9,color=color)
        normalize_ax.plot(x,np.array([r["kappa"] for r in rows])/(.0380063/30**2),color=color,lw=2,label=text)
    sensitivity.axhline(1,color=".2",lw=1,ls="--")
    sensitivity.set(yscale="log",ylabel=r"Minimum expected $\mu_{95}$",title=r"Best CMS sensitivity on the band at each $m_\chi$")
    sensitivity.legend(loc="best",fontsize=8)
    normalize_ax.axhline(1,color=".5",ls=":",lw=1)
    normalize_ax.set(yscale="log",ylabel=r"$(g_tg_\chi/M_V^2)/(g_tg_\chi/M_V^2)_{35\,{\rm GeV},\,\rm equal}$",
                     title="LZ normalization recomputed for each dark mass")
    normalize_ax.legend(loc="best",fontsize=8)
    x=[r["mchi_GeV"] for r in equal]
    for field,color,label in (("shape_q_truth","#2e5e9a","Ideal recoil energy"),
                              ("shape_q_gauss","#bc592c","32.5 keV Gaussian proxy")):
        lz.plot(x,[r[field] for r in equal],color=color,lw=2,label=label)
    lz.set(ylabel=r"$2\Delta[-\ln\mathcal{L}_{\rm shape}]$",ylim=(0,13),title="LZ recoil shape and empty sideband")
    lz.legend(loc="upper center",fontsize=8)
    for ax in axes.ravel():
        ax.set(xlim=(20,100),xlabel=r"$m_{\chi_1}$ [GeV]")
        ax.grid(alpha=.17)
        ax.axvline(35,color=".55",ls=":",lw=.8)
    mass_ax.set_xlim(20,55)
    sensitivity.set_xlim(29,52)
    sensitivity.set_yticks([.2,.3,.5,1,2])
    sensitivity.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:g}"))
    sensitivity.yaxis.set_minor_formatter(NullFormatter())
    fig.suptitle(r"Pseudo-Dirac Yukawa-like EFT  |  $\Delta m=1$ MeV, $f_2=0.5$  |  CMS 66-bin Asimov fit",
                 fontsize=13)
    FIGURES.mkdir(exist_ok=True)
    for ext in ("png","pdf"):
        fig.savefig(FIGURES/f"mchi_relic_cms_scan.{ext}",dpi=220)
    plt.close(fig)


def main():
    limits = ReferenceLimits()
    cases = {}
    for label,folder in (("equal_rate","equal"),("gaussian_profile","gaussian")):
        if not (RESULTS/folder/"relic_crossings.csv").is_file():
            continue
        paths = [RESULTS/folder]
        paths.extend(path for path in sorted(RESULTS.glob(f"{folder}_refine*"))
                     if (path/"relic_crossings.csv").is_file())
        cases[label] = load_case(paths,limits,label)
    plot(cases)
    plot_slices(limits)
    for label,(rows,_) in cases.items():
        active = [row for row in rows if row["cms_points"]]
        best = min(active,key=lambda r:r["minimum_mu95_profiled"])
        print(label,"interval on scanned mass nodes",intervals(rows,"minimum_mu95_profiled"),flush=True)
        print("best",json.dumps(best),flush=True)
        for r in rows:
            if r["mchi_GeV"] in (30,34,35,36,37,38,40,42,45,48,50,52,55,60,70,80,90,100):
                print(f"{r['mchi_GeV']:6g} {r['best_mv_GeV']:8.3f} {r['best_gchi']:8.4f}"
                      f" {r['best_gt']:7.3f} {r['minimum_mu95_profiled']:8.4g} "
                      f"{r['relic_points']:4d} {r['cms_points']:4d} {r['cms_profiled_below_one']:4d}",
                      flush=True)


if __name__ == "__main__":
    main()

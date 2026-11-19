"""Use public CMS counts to obtain an observed limit on the existing LZ–Planck plane."""
import csv
import json
import math
import tarfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import NullFormatter

from assess import HERE, RESULTS, FIGURES, ReferenceLimits, read, write
from expected_scan import AsimovFit, POINTS, br, cms_inputs, interpolate, interpolate_covariance, lz_product
from observed_fit import ObservedFit, cls


SOURCE = RESULTS/"observed_inputs"
ARCHIVE = HERE.parents[1]/"tmp/cms_monojet_hepdata_v2.tar.gz"
TABLES = {
    "hepdata_t15_monojet_yields.csv": "Simplifiedlikelihood:Yields(Monojet).csv",
    "hepdata_t14_monojet_covariance.csv": "Simplifiedlikelihood:covariancematrix(Monojet).csv",
}


class PhysicalAsimov(AsimovFit):
    def __init__(self, background, covariance):
        super().__init__(background,covariance)
        self.nonnegative = ObservedFit(background,background,covariance)

    def q(self, amplitude, signal, signal_cov=None):
        if signal_cov is None:
            return super().q(amplitude,signal)
        return self.nonnegative.profile(amplitude,signal,signal_cov).deviance


def source_text(name):
    path = SOURCE/name
    if not path.is_file():
        with tarfile.open(ARCHIVE) as archive:
            member = "HEPData-ins1894408-v2-csv/"+TABLES[name]
            path.write_bytes(archive.extractfile(member).read())
    return path.read_text(encoding="utf-8-sig")


def public_data(records, background, covariance):
    SOURCE.mkdir(exist_ok=True)
    raw = source_text("hepdata_t15_monojet_yields.csv")
    labels = [row["region"].replace("monojet_SR_","monojet_") for row in records]
    pairs = list(csv.reader(raw.splitlines()))
    yields = {}
    for key in ("Background yield","Data yield"):
        start = pairs.index(["Bin",key])+1
        end = pairs.index([],start)
        values = {label:float(value) for label,value in pairs[start:end]}
        assert set(values)==set(labels)
        yields[key] = np.array([values[label] for label in labels])
    n = yields["Data yield"]
    assert np.array_equal(n,np.array([int(row["observed"]) for row in records]))
    assert np.array_equal(n,n.astype(int))
    assert np.allclose(yields["Background yield"],background,rtol=5e-9,atol=1e-8)
    raw = source_text("hepdata_t14_monojet_covariance.csv")
    entries = {(r["First Bin"],r["Second Bin"]):float(r["Covariance"])
               for r in csv.DictReader(line for line in raw.splitlines() if line and not line.startswith("#"))}
    assert len(entries)==len(labels)**2
    matrix = np.array([[entries[(a,b)] for b in labels] for a in labels])
    assert np.allclose(matrix,covariance,rtol=5e-9,atol=1e-8)
    return n


def cross_checks(fitter, expected, conditional, vectors, covariances):
    normal = lambda x: .5*math.erfc(-x/math.sqrt(2))
    for mu in (1.8,3.):
        for estimate in (-1.2,0.,.7):
            qobs = (mu-estimate)**2 if estimate>=0 else mu**2-2*mu*estimate
            assert math.isclose(cls(qobs,mu**2),normal(estimate-mu)/normal(estimate),rel_tol=1e-13)
    background_fit = ObservedFit(expected.b,expected.b,expected.covariance)
    for k in (0,len(vectors)//2,len(vectors)-1):
        signal,cov = vectors[k],covariances[k]
        value = expected.upper(signal,cov)
        observed,hat,_,_ = background_fit.upper(signal,cov,value,expected)
        assert hat==0 and abs(observed/value-1)<1e-6
        # Recover both independent nuisance vectors from the profiled Poisson score.
        check = fitter.profile(value,signal,cov)
        score = 1-fitter.data/check.mean
        d_bkg = -fitter.covariance@score
        d_sig = -value*cov@score
        if check.active_bins==0:
            assert np.allclose(check.mean,fitter.b+value*signal+d_bkg+value*d_sig,rtol=1e-8)
        eps = value*1e-4
        lower = fitter.profile(value-eps,signal,cov).deviance
        upper = fitter.profile(value+eps,signal,cov).deviance
        assert math.isclose((upper-lower)/(2*eps),check.slope,rel_tol=1e-5,abs_tol=1e-7)
        # The conditional Asimov experiment is centered at the background-only fit.
        assert np.array_equal(conditional.b,fitter.profile(0.,signal).mean)


def fitted_limits(fitter, expected, conditional, reference, masses):
    signal = interpolate(masses,reference.nodes,reference.vectors)
    covs = interpolate_covariance(masses,reference.nodes,reference.cov)
    enom,emc = reference.lookup(masses)
    rows = []
    for m,s,c,e,ec_previous in zip(masses,signal,covs,enom,emc,strict=True):
        ec = expected.upper(s,c)
        assert abs(ec/ec_previous-1)<.01
        nominal,hat_nominal,_,_ = fitter.upper(s,None,e,conditional)
        upper,hat,q,qa = fitter.upper(s,c,ec,conditional)
        rows.append(dict(mass_GeV=float(m),expected95=e,expected95_mc=ec,observed95=nominal,observed95_mc=upper,
                         observed_muhat=hat_nominal,observed_muhat_mc=hat,qtilde_at_observed95=q,
                         conditional_qA_at_observed95=qa,observed_to_expected_mc=upper/ec,
                         signal_bins_at_zero=fitter.profile(upper,s,c).active_bins,
                         expected95_mc_previous=ec_previous))
    return rows


def add_benchmark(fitter, expected, conditional):
    if not ARCHIVE.is_file():
        return None
    with tarfile.open(ARCHIVE) as archive:
        member = "HEPData-ins1894408-v2-csv/Signaltemplates,ADD,Monojet.csv"
        raw = archive.extractfile(member).read().decode("utf-8-sig")
    matches = {}
    for block in raw.split("\n\n"):
        if "#: d,,,2\n" not in block or "#: $M_{D}$ [TeV],,,10\n" not in block:
            continue
        year = int(next(line.split(",")[-1] for line in block.splitlines() if line.startswith("#: Data-taking")))
        tab = list(csv.DictReader(line for line in block.splitlines() if line and not line.startswith("#")))
        assert len(tab)==22
        matches[year] = [float(row["Signal yield"]) for row in tab]
    assert set(matches)=={2016,2017,2018}
    s = np.array([v for year in sorted(matches) for v in matches[year]])
    e = expected.upper(s)
    o,hat,_,_ = fitter.upper(s,None,e,conditional)
    return dict(d=2,MD_TeV=10.,bins=len(s),expected_mu95=e,observed_mu95=o,observed_muhat=hat)


def model_plane(source, reference_rows):
    masses = sorted({float(r["mass_GeV"]) for r in source})
    gts = sorted({float(r["gt_LZ"]) for r in source})
    assert len(source)==len(masses)*len(gts)
    ref = {row["mass_GeV"]:row for row in reference_rows}
    fields = source.dtype.names
    out = []
    for row in source:
        record = {key:float(row[key]) for key in fields}
        fit = ref[record["mass_GeV"]]
        k = record["gt_LZ"]**2*record["BR_invisible"]
        obs,obs_mc,hat = [float(fit[key]/k) for key in ("observed95","observed95_mc","observed_muhat_mc")]
        if math.isfinite(k):
            assert abs((fit["expected95_mc_previous"]/k)/record["expected_mu95_mc_profiled"]-1)<2e-7
        record["expected_mu95_mc_profiled"] = float(fit["expected95_mc"]/k)
        record.update(observed_mu95=obs,observed_mu95_mc_profiled=obs_mc,observed_muhat_mc_profiled=hat)
        out.append(record)
    write(RESULTS/"gt_mv_observed_heatmap.csv",out)
    shape = len(masses),len(gts)
    fields = ("expected_mu95_mc_profiled","observed_mu95_mc_profiled")
    exp,obs = [np.array([r[key] for r in out]).reshape(shape).T for key in fields]
    assert np.array_equal(np.array([r["gt_LZ"] for r in out]).reshape(shape)[0],gts)
    assert np.array_equal(np.array([r["mass_GeV"] for r in out]).reshape(shape)[:,0],masses)
    return masses,gts,exp,obs,out


def plot(masses,gts,exp,obs,figure_name="gt_mv_observed_cms_heatmap"):
    fig,axes = plt.subplots(1,2,sharex=True,sharey=True,figsize=(11.9,5.05),layout="constrained")
    norm = TwoSlopeNorm(vmin=np.log10(.16),vcenter=0,vmax=np.log10(40))
    for ax,values,title in zip(axes,(exp,obs),("Median expected","Observed CMS data"),strict=True):
        ax.set_facecolor("#e9ebed")
        heat = ax.pcolormesh(masses,gts,np.log10(values),cmap="RdBu",norm=norm,
                             shading="nearest",rasterized=True)
        ax.contour(masses,gts,values,levels=[1],colors="#222127",linewidths=1.35)
        ax.axhline(gts[-1],color="#7b7d85",lw=.85,ls=":")
        ax.set(xlim=(72,200),ylim=(.1,3.76),yscale="log",xlabel=r"$M_V$ [GeV]",title=title,
               xticks=[75,100,125,150,175,200])
        ax.set_yticks([.1,.2,.4,.7,1,2,np.sqrt(4*np.pi)],
                      labels=["0.1","0.2","0.4","0.7","1","2",r"$\sqrt{4\pi}$"])
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.grid(alpha=.17,lw=.7)
        ax.set_axisbelow(True)
    axes[0].set_ylabel(r"Top coupling $g_t$")
    axes[1].contour(masses,gts,exp,levels=[1],colors="#484b58",linewidths=1.0,linestyles="--")
    axes[1].legend(handles=[Line2D([],[],color="#222127",lw=1.35,label=r"Observed $\mu_{95}=1$"),
                            Line2D([],[],color="#484b58",lw=1.0,ls="--",label=r"Expected $\mu_{95}=1$"),
                            Patch(facecolor="#e9ebed",edgecolor="#bbc0c4",label="No joint solution in scan")],
                   loc="lower right",fontsize=8.3,framealpha=.95)
    ticks = [.2,.35,.6,1,2,5,10,20,40]
    bar = fig.colorbar(heat,ax=axes,ticks=np.log10(ticks),extend="both",pad=.022)
    bar.ax.set_yticklabels([f"{x:g}" for x in ticks])
    bar.set_label(r"Minimum 95% $CL_s$ upper limit on $\mu$")
    fig.suptitle(r"CMS Run 2 monojet on the LZ + Planck plane",fontsize=14,weight="bold")
    fig.supxlabel(r"13 TeV, 137 fb$^{-1}$  |  66 bins, full background covariance and finite signal MC",
                  fontsize=9.5,color="#4c5563")
    for extension in ("png","pdf"):
        fig.savefig(FIGURES/f"{figure_name}.{extension}",dpi=230)
    plt.close(fig)


def main():
    records,original,_ = cms_inputs()
    expected = PhysicalAsimov(original.b,original.covariance)
    data = public_data(records,expected.b,expected.covariance)
    fitter = ObservedFit(data,expected.b,expected.covariance)
    bfit = fitter.profile(0.,np.zeros_like(data)).mean
    conditional = PhysicalAsimov(bfit,expected.covariance)
    write(RESULTS/"cms_monojet_observed_bins.csv",
          [dict(region=row["region"],year=row["year"],met_low_GeV=row["met_low_GeV"],
                met_high_GeV=row["met_high_GeV"],observed=int(data[i]),control_region_background=expected.b[i],
                fitted_background_at_mu0=bfit[i]) for i,row in enumerate(records)])
    source = read(RESULTS/"gt_mv_heatmap.csv")
    masses = np.unique(np.r_[source["mass_GeV"],[mv for mv,_ in POINTS.values()]])
    ref = ReferenceLimits(grid=masses)
    cross_checks(fitter,expected,conditional,ref.vectors,ref.cov)
    node_rows = fitted_limits(fitter,expected,conditional,ref,masses)
    write(RESULTS/"cms_observed_reference_limits.csv",node_rows)
    masses,gts,exp,obs,out = model_plane(source,node_rows)
    k = "observed_mu95_mc_profiled"
    allowed = [r for r in out if math.isfinite(r[k])]
    best = min(allowed,key=lambda r:r[k])
    obs_sensitive = [r for r in allowed if r[k]<1]
    exp_sensitive = [r for r in allowed if r["expected_mu95_mc_profiled"]<1]
    benchmarks = []
    by_mass = {row["mass_GeV"]:row for row in node_rows}
    for name,(mv,gc) in POINTS.items():
        gt = lz_product(mv)/gc
        branch,_ = br(mv,gt,gc)
        scale = gt**2*branch
        row = by_mass[mv]
        s = interpolate([mv],ref.nodes,ref.vectors)[0]
        c = interpolate_covariance(np.array([mv]),ref.nodes,ref.cov)[0]
        alternate,_,_,_ = fitter.upper(s,c,row["expected95_mc"],expected)
        direct,_,_,_ = fitter.upper(s*scale,c*scale**2,row["expected95_mc"]/scale,conditional)
        assert abs(direct/(row["observed95_mc"]/scale)-1)<1e-7
        benchmarks.append(dict(point=name,mass_GeV=mv,gchi=gc,gt=gt,
                               expected_mu95=row["expected95"]/scale,expected_mu95_mc=row["expected95_mc"]/scale,
                               observed_mu95=row["observed95"]/scale,observed_mu95_mc=row["observed95_mc"]/scale,
                               observed_mu95_mc_nominal_asimov=alternate/scale,
                               observed_muhat_mc=row["observed_muhat_mc"]/scale))
    write(RESULTS/"observed_benchmark_limits.csv",benchmarks)
    summary = dict(n_observed=int(data.sum()),control_region_prediction=float(expected.b.sum()),
                   observed_bins=len(data),valid_pixels=len(allowed),expected_sensitive_pixels=len(exp_sensitive),
                   observed_sensitive_pixels=len(obs_sensitive),
                   both_sensitive_pixels=int(np.sum((exp<1)&(obs<1))),
                   observed_first_mass_GeV=min(r["mass_GeV"] for r in obs_sensitive) if obs_sensitive else None,
                   expected_first_mass_GeV=min(r["mass_GeV"] for r in exp_sensitive),
                   masses_with_signal_bins_at_zero=sum(r["signal_bins_at_zero"]>0 for r in node_rows),
                   max_expected_change_from_nonnegative=max(abs(r["expected95_mc"]/r["expected95_mc_previous"]-1)
                                                            for r in node_rows),
                   best_observed=best,benchmarks=benchmarks,
                   add_monojet_crosscheck=add_benchmark(fitter,expected,conditional))
    (RESULTS/"observed_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    plot(masses,gts,exp,obs)


if __name__ == "__main__":
    main()

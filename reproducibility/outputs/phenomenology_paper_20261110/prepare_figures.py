"""Reuse audited figures and calculate the branch-resolved central CMS plane."""

import csv
import json
import math
import shutil
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


HERE=Path(__file__).resolve().parent
FIG=HERE/'figures'
DATA=HERE/'data'
FIG.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
OUTPUTS=HERE.parent
AUDIT=OUTPUTS/'lz_mixing_uncertainty_20261110'
ASSETS={
    '01_xenon_recoil.png':'monojet_manuscript_20261106/figures/lz_recoil.png',
    '02_relic_slope.png':'monojet_manuscript_20261106/figures/relic_slope.png',
    '03_hard_met_cross_sections.png':'truth_xsec_scan_20261106/figures/truth_met200.png',
    '05_collider_uncertainties.png':'lz_mixing_uncertainty_20261110/figures/02_collider_uncertainties.png',
    '06_matching_and_spectra.png':'lz_mixing_uncertainty_20261110/figures/01_lz_matching.png',
    '07_lz_rate_variation.png':'lz_mixing_uncertainty_20261110/figures/03_lz_rate_impact.png',
    '08_top_branches_and_energy.png':'lz_mixing_uncertainty_20261110/figures/05_branches_and_single_top.png',
    'a01_original_recoil.png':'pseudoDiracB_20261004/recoil_spectrum_paper_units.png',
    'a02_timelike_mixing.png':'lz_mixing_uncertainty_20261110/figures/04_timelike_mixing.png',
    'a03_excited_fraction.png':'lz_model_checks_20261110/lz_consistency_checks.png',
    'b01_loose_cross_sections.png':'truth_xsec_scan_20261106/figures/truth_loose.png',
    'b02_lz_slice_cross_sections.png':'truth_xsec_scan_20261106/figures/truth_lz_slice.png',
    'c01_cms_benchmark_limits.png':'monojet_cms_benchmark_20261107/figures/benchmark_limits.png',
    'c02_cms_vector_750.png':'monojet_cms_benchmark_20261107/figures/vector_750_detector_validation.png',
    'c03_cms_vector_100.png':'monojet_cms_benchmark_20261107/figures/vector_100_detector_validation.png',
    'c04_cms_vector_2000.png':'monojet_cms_benchmark_20261107/figures/vector_2000_detector_validation.png',
    'd02_top_truth_met.png':'single_top_pilot_20261110/single_top_truth_met.png',
}
TABLES={
    'branch_uncertainties.csv':'lz_mixing_uncertainty_20261110/branch_uncertainties.csv',
    'benchmark_roots.csv':'lz_mixing_uncertainty_20261110/physical_roots_and_limits.csv',
    'timelike_rate_summary.csv':'lz_mixing_uncertainty_20261110/timelike_rate_summary.csv',
    'relic_numerical_audit.csv':'lz_mixing_uncertainty_20261110/relic_numerical_audit.csv',
    'truth_benchmarks.csv':'truth_xsec_scan_20261106/results/benchmark_cross_sections.csv',
    'template_replica_comparison.csv':'monojet_mchi_scan_20261106/results/gap120/replica_comparison.csv',
    'off_shell_ttmet.csv':'ttmet_branch_map_20261110/off_shell_xsec/cross_sections.csv',
    'light_relic_branches.csv':'ttmet_branch_map_20261110/branches.csv',
    'single_top_expected.csv':'single_top_pilot_20261110/expected_benchmarks.csv',
}


def copy_assets():
    for dest,items in ((FIG,ASSETS),(DATA,TABLES)):
        for name,source in items.items():
            shutil.copyfile(OUTPUTS/source,dest/name)


def fit_grid(cells):
    path=AUDIT/'collider_errors.py'
    source=path.read_text(encoding='utf-8').split('\nrows=list(propagate())',1)[0]
    likelihood={'__file__':str(path),'__name__':'central_grid_likelihood'}
    exec(compile(source,str(path),'exec'),likelihood)
    fits={}
    results=[]
    for cell in cells:
        mv,gt=cell['mv_GeV'],cell['gt']
        for rank,(branch,m,omega,xf,width,gc) in enumerate(cell['roots']['0'],1):
            assert abs(omega-.12)<1.01e-5
            gap=mv-2*m-.001
            assert (gap>0)==(branch=='on')
            nwa=branch=='on' and gap>=5*width and width/mv<.03
            row=dict(mv_GeV=mv,gt=gt,root=rank,branch=branch,mchi_GeV=m,gchi=gc,omega_h2=omega,xf=xf,
                     width_GeV=width,gap_GeV=gap,BR_invisible='',expected_mu95='',observed_mu95='')
            if nwa:
                if mv not in fits:
                    fits[mv]=likelihood['mono_limits'](mv,0.)
                fit=fits[mv]
                br=likelihood['widths'](mv,m,gc,width)
                assert 0<br<=1.001
                row.update(BR_invisible=br,expected_mu95=fit['experimental'][2]/(gt**2*br),
                           observed_mu95=fit['observed']/(gt**2*br))
            results.append(row)
    with (DATA/'center_grid_limits.csv').open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(results[0]))
        out.writeheader();out.writerows(results)
    return results


def grid_plot(cells,rows):
    masses=sorted({c['mv_GeV'] for c in cells})
    couplings=sorted({c['gt'] for c in cells})
    index={(m,g):(i,j) for i,g in enumerate(couplings) for j,m in enumerate(masses)}
    shape=(len(couplings),len(masses))
    mats={name:np.full(shape,np.nan) for name in ('expected_mu95','observed_mu95')}
    off=[]; beyond=[]; multiple=[]
    eligible={}
    for r in rows:
        pair=(r['mv_GeV'],r['gt'])
        if r['expected_mu95']!='':
            eligible.setdefault(pair,[]).append(r)
    for c in cells:
        pair=(c['mv_GeV'],c['gt'])
        if any(r[0]=='off' for r in c['roots']['0']):
            off.append(pair)
        n_on=sum(r[0]=='on' for r in c['roots']['0'])
        selected=eligible.get(pair,[])
        if len(selected)>1:
            multiple.append(pair)
        elif n_on and not selected:
            beyond.append(pair)
        elif selected:
            for key,values in mats.items():
                values[index[pair]]=math.log10(selected[0][key])
    fig,axes=plt.subplots(1,2,sharey=True,figsize=(11.7,5.1),layout='constrained')
    norm=TwoSlopeNorm(vmin=math.log10(.16),vcenter=0,vmax=math.log10(40))
    for ax,(key,values),title in zip(axes,mats.items(),('Median expected','Observed CMS data'),strict=True):
        ax.set_facecolor('#ebedef')
        mesh=ax.pcolormesh(masses,couplings,values,cmap='RdBu',norm=norm,shading='nearest')
        if np.nanmin(values)<0<np.nanmax(values):
            ax.contour(masses,couplings,values,levels=[0],colors='#1e252d',linewidths=1.2)
        for points,marker,color,size in ((off,'.','#252a33',10),(beyond,'x','#4a5361',12),(multiple,'s','#80513d',11)):
            if points:
                x,y=zip(*points)
                ax.scatter(x,y,c=color,marker=marker,s=size,linewidths=.7,zorder=3)
        ax.set(xlim=(72,200),ylim=(.1,3.68),yscale='log',xlabel=r'$M_V$ [GeV]',title=title)
        ax.set_yticks([.1,.2,.4,.7,1,2,math.sqrt(4*math.pi)],['0.1','0.2','0.4','0.7','1','2',r'$\sqrt{4\pi}$'])
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    axes[0].set_ylabel(r'$g_t$')
    values=[.2,.5,1,2,5,10,30]
    bar=fig.colorbar(mesh,ax=axes,pad=.025,ticks=np.log10(values),extend='both')
    bar.ax.set_yticklabels([str(v) for v in values]);bar.set_label(r'$\mu_{95}$')
    keys=[Line2D([],[],c='#1e252d',label=r'$\mu_{95}=1$')]
    if off:
        keys.insert(0,Line2D([],[],ls='none',marker='.',c='#252a33',label='Off-shell root present'))
    if beyond:
        keys.insert(0,Line2D([],[],ls='none',marker='x',c='#4a5361',label='On shell outside NWA'))
    if multiple:
        keys.insert(0,Line2D([],[],ls='none',marker='s',c='#80513d',label='Multiple on-shell roots'))
    fig.legend(handles=keys,loc='outside lower center',ncols=len(keys),frameon=False,fontsize=8.5)
    save(fig,'04_cms_central_plane')
    statistics=dict(cells=len(cells),roots=len(rows),calls=sum(c['calls'] for c in cells),
                    failed_calls=sum(c['failed'] for c in cells),off_cells=len(off),
                    multi_on_cells=len(multiple),outside_nwa_cells=len(beyond),
                    colored_cells=int(np.isfinite(mats['expected_mu95']).sum()),
                    expected_sensitive=int((mats['expected_mu95']<0).sum()),
                    observed_sensitive=int((mats['observed_mu95']<0).sum()))
    for key in mats:
        valid=[r for r in rows if r[key]!='']
        statistics[key+'_minimum']=min(valid,key=lambda r:r[key])
        statistics[key+'_minimum_mass_sensitive']=min(r['mv_GeV'] for r in valid if r[key]<1)
    (DATA/'center_grid_summary.json').write_text(json.dumps(statistics,indent=2),encoding='utf-8')
    print(json.dumps(statistics,indent=2))


def mass_projection(rows):
    fig,ax=plt.subplots(figsize=(7.5,4.6),layout='constrained')
    groups=[('off','#a36153','Off-shell central solution'),('on','#7895aa','On-shell central solution'),
            ('obs','#233e68',r'On-shell with observed $\mu_{95}<1$')]
    for key,color,label in groups:
        if key=='obs':
            subset=[r for r in rows if r['observed_mu95']!='' and r['observed_mu95']<1]
        else:
            subset=[r for r in rows if r['branch']==key]
        if not subset:
            continue
        ax.scatter([r['mchi_GeV'] for r in subset],[r['mv_GeV'] for r in subset],s=10,c=color,label=label,alpha=.75)
    x=np.array([35.9995,99.9995]);ax.plot(x,2*x+.001,'--',color='#343b42',lw=.9,label=r'$M_V=m_1+m_2$')
    ax.set(xlim=(20,100),ylim=(71,201),xlabel=r'$m_\chi$ [GeV]',ylabel=r'$M_V$ [GeV]')
    ax.legend(loc='lower right',frameon=False,fontsize=8.5)
    save(fig,'04b_central_mass_projection')


def sample_validation():
    file=DATA/'template_replica_comparison.csv'
    with file.open(newline='') as f:
        replicas={r['case']:r for r in csv.DictReader(f)}
    with (DATA/'benchmark_roots.csv').open(newline='') as f:
        r=next(r for r in csv.DictReader(f) if r['point']=='MONO_120_0.43' and r['case']=='base'
               and r['branch']=='on' and r['sigma_omega']=='0')
    scale=float(r['gt'])**2*float(r['BR_invisible'])
    kinds=['original','loop_m16','stratified']
    labels=['Original','Independent','Stratified']
    fig,axes=plt.subplots(1,2,figsize=(9.2,3.65),layout='constrained')
    x=np.arange(len(kinds))
    for offset,key,color in ((-.17,'expected_nu95','#4f7f93'),(.17,'observed_nu95','#a4544a')):
        values=[float(replicas[k][key])/scale for k in kinds]
        bar=axes[0].bar(x+offset,values,.32,color=color,label=key.split('_')[0].title())
        axes[0].bar_label(bar,fmt='%.2f',padding=2,fontsize=8)
    axes[0].axhline(1,color='#3e4248',ls='--',lw=.8)
    axes[0].set(ylabel=r'$\mu_{95}$ at the central relic point',ylim=(0,1.48))
    axes[0].legend(frameon=False,loc='upper right',fontsize=8)
    bar=axes[1].bar(x,[int(replicas[k]['selected_above_470']) for k in kinds],color='#4f7f93',width=.54)
    axes[1].bar_label(bar,padding=2,fontsize=8)
    axes[1].set(ylabel=r'Main loop sample events above 470 GeV',ylim=(0,65))
    for ax in axes:
        ax.set_xticks(x,labels)
    save(fig,'c05_loop_mc_validation')


def light_branches():
    with (DATA/'light_relic_branches.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    masses=np.unique([float(r['mv_GeV']) for r in rows])
    couplings=np.unique([float(r['gt']) for r in rows])
    classes=np.full((len(couplings),len(masses)),np.nan)
    for r in rows:
        j=np.searchsorted(masses,float(r['mv_GeV']))
        i=np.searchsorted(couplings,float(r['gt']))
        available=2*bool(int(r['on_count']))+bool(int(r['off_count']))
        classes[i,j]=4 if not available and int(r['n_failed']) else available
    colors=['#edf0f2','#d87939','#4688bc','#8465a7','#929799']
    labels=['No solution found','Off-shell only','On-shell only','Both branches','Solver failure']
    fig,ax=plt.subplots(figsize=(8.5,5.2),layout='constrained')
    ax.pcolormesh(masses,couplings,classes,shading='nearest',cmap=ListedColormap(colors),
                  norm=BoundaryNorm(np.arange(6)-.5,len(colors)))
    ax.set(xlim=(20,100),ylim=(.2,math.sqrt(4*math.pi)),yscale='log',xlabel=r'$M_V$ [GeV]',
           ylabel=r'$g_t$',title=r'Low-mass branches within the Planck $\pm2\sigma$ band')
    ax.set_yticks([.2,.5,1,2,math.sqrt(4*math.pi)],['0.2','0.5','1','2',r'$\sqrt{4\pi}$'])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    handles=[Patch(facecolor=c,label=l) for i,(c,l) in enumerate(zip(colors,labels)) if np.any(classes==i)]
    fig.legend(handles=handles,loc='outside lower center',frameon=False,ncols=4,fontsize=9)
    save(fig,'d01_light_top_branches')


def save(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=215)
    fig.savefig(FIG/(name+'.svg'))
    plt.close(fig)


if __name__=='__main__':
    copy_assets()
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False})
    sample_validation()
    light_branches()
    cells=[json.loads(line) for line in (DATA/'center_grid_roots.jsonl').read_text().splitlines()]
    if len(cells)!=1015:
        raise ValueError(f'Expected a 35 by 29 central grid, received {len(cells)} cells')
    assert len({(c['mv_GeV'],c['gt']) for c in cells})==len(cells)
    rows=fit_grid(cells)
    grid_plot(cells,rows)
    mass_projection(rows)

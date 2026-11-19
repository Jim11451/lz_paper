"""Tabulate branch-by-branch errors and make report figures."""

import csv
import json
import math
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import ndtr


HERE = Path(__file__).resolve().parent
PHYSICS = HERE.parent/'lz_model_checks_20261110/physics_checks.py'
source = PHYSICS.read_text(encoding='utf-8').split('energy = np.linspace',1)[0]
physics = {'__file__':str(PHYSICS)}
exec(compile(source,str(PHYSICS),'exec'),physics)
FIG = HERE/'figures'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def write(path,rows):
    fields=list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=210)
    fig.savefig(FIG/(name+'.svg'))
    plt.close(fig)


def integrate(values,energy):
    return np.trapezoid(values,x=energy)


energy=np.linspace(.5,1000,4000)
roi=(energy>=5.4)&(energy<=269.9)
q2,_=physics['recoil_weights'](35,energy)
slope=physics['photon_slope'](q2)
tree_charge=physics['Q0'][:,None]
q0=tree_charge+54*slope


def spectrum(m,d):
    _,weight=physics['recoil_weights'](m,energy)
    return (weight*(q0+54*d)**2).sum(axis=0)


@lru_cache(maxsize=None)
def density_at_candidate(m,d,r):
    spec=spectrum(m,d)
    return r*1.120444105*integrate(spec*g,energy)/integrate(spec[roi],energy[roi])


fig,axes=plt.subplots(1,2,figsize=(11.3,4.15),layout='constrained')
ax=axes[0]
dgrid=np.linspace(-2.3e-4,1.1e-4,450)
for m in (20,35,44):
    baseline=integrate(spectrum(m,0.)[roi],energy[roi])
    curve=[math.sqrt(baseline/integrate(spectrum(m,d)[roi],energy[roi])) for d in dgrid]
    ax.semilogy(dgrid*1e4,curve,label=f'$m_\u03c7={m}$ GeV')
ax.axvspan(-.07,.07,color='#ccd7e6',alpha=.9,label=r'$|d_\gamma(0)|\leq7\times10^{-6}$')
ax.axhline(1,color='#60666c',lw=.9,ls='--')
ax.set(xlabel=r'$10^4\,d_\gamma(0)$',ylabel=r'$\kappa_{\mathrm{LZ}}/\kappa_{d=0}$',
       title='Signed mixing and xenon cancellation')
ax.legend(loc='upper right',fontsize=8,frameon=False,title='Curves nearly overlap')
ax=axes[1]
shape_rows=[]
sigma=math.hypot(23,23)
g= np.exp(-.5*((248-energy)/sigma)**2)/(sigma*math.sqrt(2*math.pi))
p_window=ndtr((269.9-energy)/sigma)-ndtr((5.4-energy)/sigma)
for m,d in [(20.,0.),(35.,0.),(44.,0.),(35.,7e-6),(35.,-1.49e-4)]:
    spec=spectrum(m,d)
    norm=integrate(spec[roi],energy[roi])/1.120444105
    normalized=spec/norm
    shape_rows.append(dict(mchi_GeV=m,d=d,truth_roi=integrate(normalized[roi],energy[roi]),
                          toy_smeared_roi=integrate(normalized*p_window,energy),
                          toy_candidate_density_per_keV=integrate(normalized*g,energy)))
    if d!=7e-6:
        name=f'{m:g} GeV' if d==0 else '35 GeV, near Xe cancellation'
        ax.plot(energy,normalized,label=name,ls='-' if d==0 else '--')
ax.axvspan(5.4,269.9,color='#f3f2ed',zorder=-2)
ax.axvline(248,color='#bf4a38',lw=1,ls=':')
ax.set(xlim=(0,550),ylim=(0,None),xlabel='True nuclear recoil [keV]',ylabel='Events per keV',
       title='Shapes at the same true ROI rate')
ax.legend(frameon=False,fontsize=8)
save(fig,'01_lz_matching')
write(HERE/'recoil_shape_proxy.csv',shape_rows)


physical=read(HERE/'physical_roots_and_limits.csv')
cells=[json.loads(line) for line in (HERE/'relic_roots.jsonl').read_text().splitlines()]
branches=defaultdict(dict)
root_counts=Counter()
for r in physical:
    branches[tuple(r[key] for key in ('case','point','branch','root'))][int(r['sigma_omega'])]=r
    root_counts[(r['case'],r['point'],r['branch'],int(r['sigma_omega']))]+=1
    for key in ('mono','tj'):
        if r[key+'_exp']:
            quantiles=[float(r[f'{key}_{band}']) for band in ('exp_m2','exp_m1','exp','exp_p1','exp_p2')]
            assert quantiles==sorted(quantiles)

quantities=('mchi_GeV','gchi','mono_exp','mono_observed','tj_exp')
summary=[]
for (case,point,side,rank),targets in branches.items():
    if 0 not in targets:
        continue
    r=targets[0]
    counts={k:root_counts[case,point,side,k] for k in [-2,-1,0,1,2]}
    stable=len(set(counts.values()))==1
    record={key:r[key] for key in ('case','point','mv_GeV','gt','d','rate','f2','branch','root','gap_GeV','BR_invisible')}
    record.update(roots_m2_m1_0_p1_p2='/'.join(str(n) for n in counts.values()),stable_branch_count=stable)
    record['toy_candidate_density_per_keV']=density_at_candidate(*map(float,(r['mchi_GeV'],r['d'],r['rate'])))
    for q in quantities:
        record[q]=r[q]
        for k,name in [(-2,'m2'),(-1,'m1'),(1,'p1'),(2,'p2')]:
            record[f'{q}_Omega_{name}']=targets[k][q] if stable else ''
    summary.append(record)
write(HERE/'branch_uncertainties.csv',summary)

base=[r for r in physical if r['case']=='base' and r['sigma_omega']=='0' and r['branch']=='on']
fig,axes=plt.subplots(1,2,figsize=(12,4.65),layout='constrained')
for ax,channel,title in zip(axes,('mono','tj'),('CMS monojet recast','Single top, 1 TeV truth proxy')):
    subset=[r for r in base if r[channel+'_exp']]
    for i,r in enumerate(subset):
        x=float(r[channel+'_exp'])
        for lo,hi,color,width in [('m2','p2','#96b4c7',2),('m1','p1','#276784',6)]:
            a,z=(float(r[f'{channel}_exp_{k}']) for k in (lo,hi))
            ax.plot([a,z],[i,i],color=color,lw=width,solid_capstyle='round')
        ax.scatter(x,i,s=24,c='white',edgecolor='#183144',zorder=3)
        s=next(t for t in summary if all(t[k]==r[k] for k in ('case','point','branch','root')))
        ends=[s[f'{channel}_exp_Omega_{k}'] for k in ('m2','p2')]
        if all(ends):
            ax.plot(list(map(float,ends)),[i+.17,i+.17],color='#9e491f',lw=2.1,marker='|',ms=5)
        if r[channel+'_observed'] and math.isfinite(float(r[channel+'_observed'])):
            ax.scatter(float(r[channel+'_observed']),i-.17,marker='D',s=20,c='#a9303d')
    ax.set_yticks(range(len(subset)),[f"{float(r['mv_GeV']):g} / {float(r['gt']):.3g}" for r in subset])
    ax.invert_yaxis()
    ax.axvline(1,color='#42454b',ls='--',lw=1)
    ax.set(xscale='log',xlabel=r'$\mu_{95}$',ylabel=r'$M_V$ [GeV] / $g_t$',title=title)
    ax.grid(axis='x',alpha=.2)
axes[0].plot([],[],lw=6,color='#276784',label='Expected ±1σ (±2σ in light blue)')
axes[0].plot([],[],lw=2,color='#9e491f',label='Planck ±2σ mapped to median')
axes[0].plot([],[],lw=0,marker='D',c='#a9303d',label='Observed')
axes[0].legend(frameon=False,fontsize=8,loc='lower right')
save(fig,'02_collider_uncertainties')


fig,axes=plt.subplots(1,2,figsize=(11.6,4.4),layout='constrained')
for ax,channel,title in zip(axes,('mono','tj'),('Monojet','Single top, 1 TeV truth proxy')):
    for r in base:
        if not r[channel+'_exp']:
            continue
        relevant=sorted((v for v in physical if v['point']==r['point'] and v['sigma_omega']=='0' and v['branch']=='on'
                         and v['root']==r['root'] and (v['case']=='base' or v['case'].startswith('rate'))),key=lambda v:float(v['rate']))
        x=[float(v['rate']) for v in relevant]
        y=[float(v[channel+'_exp']) if v[channel+'_exp'] else math.nan for v in relevant]
        ax.plot(x,y,'o-',lw=1.3,ms=3.3,label=f"{float(r['mv_GeV']):g} / {float(r['gt']):.3g}")
    ax.axvspan(.75,1.25,color='#e0e8f0',zorder=-2)
    ax.axhline(1,color='#42454b',ls='--',lw=.9)
    ax.axvline(1,color='#7e848b',ls=':',lw=.9)
    ax.set(yscale='log',xlabel=r'True ROI event-rate factor $r$',ylabel=r'Median expected $\mu_{95}$',title=title)
    ax.legend(title=r'$M_V$ [GeV] / $g_t$',fontsize=8,ncol=3,frameon=False,loc='upper center',
              bbox_to_anchor=(.5,-.18))
save(fig,'03_lz_rate_impact')


fig,axes=plt.subplots(1,2,figsize=(11.6,4.4),layout='constrained')
prior=read(HERE.parent/'truth_xsec_scan_20261106/results/production_nodes_gt1.csv')
probe=defaultdict(dict)
for r in read(HERE/'timelike_tree_probe.csv'):
    probe[float(r['mv_GeV'])][float(r['real_d'])!=0]=r
shift=read(HERE/'timelike_shift.csv')
axes[0].plot([float(r['mv_GeV']) for r in shift],[float(r['real_d'])*1e4 for r in shift],'-o',ms=3,label='Real')
axes[0].plot([float(r['mv_GeV']) for r in shift],[float(r['imag_d'])*1e4 for r in shift],'--',label='Imaginary')
axes[0].axhline(0,c='#818286',lw=.8)
axes[0].set(xlabel=r'$M_V$ [GeV]',ylabel=r'$10^4 [d_\gamma(M_V^2)-d_\gamma(0)]$',title='Heavy-quark timelike contribution')
axes[0].legend(frameon=False)
production=[]
for mv,r in sorted(probe.items()):
    initial,shifted=(float(r[k]['tree_xs_pb']) for k in (False,True))
    einitial,eshifted=(float(r[k]['integration_error_pb']) for k in (False,True))
    loop=np.interp(mv,[float(x['mass_GeV']) for x in prior],[float(x['loop200_pb']) for x in prior])
    production.append(dict(mv_GeV=mv,tree_pb=initial,shifted_tree_pb=shifted,loop_pb=loop,
                           tree_change_pct=100*(shifted/initial-1),
                           tree_change_mc_pct=100*math.hypot(eshifted,shifted/initial*einitial)/initial,
                           total_rate_diagnostic_pct=100*(shifted-initial)/(initial+loop)))
write(HERE/'timelike_rate_summary.csv',production)
mv=[r['mv_GeV'] for r in production]
axes[1].errorbar(mv,[r['tree_change_pct'] for r in production],yerr=[r['tree_change_mc_pct'] for r in production],
                marker='o',color='#276784',capsize=3,ls='none',label='Tree only ± integration error')
axes[1].scatter(mv,[r['total_rate_diagnostic_pct'] for r in production],marker='D',c='#a9303d',s=21,
                label='Tree change / baseline tree + loop')
axes[1].axhline(0,c='#818286',lw=.8)
axes[1].set(xlabel=r'$M_V$ [GeV]',ylabel='Truth cross-section change [%]',title=r'$p_T^j>200$ GeV, $|\eta_j|<4.5$')
axes[1].legend(frameon=False,fontsize=8)
save(fig,'04_timelike_mixing')


fig,axes=plt.subplots(1,2,figsize=(11.8,5.1),layout='constrained')
nominal=[r for r in summary if r['case']=='base']
labels={r['point']:f"{float(r['mv_GeV']):g} / {float(r['gt']):.3g}" for r in nominal}
for i,point in enumerate(labels):
    for r in nominal:
        if r['point']!=point:
            continue
        color,marker=('#276784','o') if r['branch']=='on' else ('#a9303d','D')
        axes[0].scatter(float(r['gap_GeV']),i,c=color,marker=marker,s=25)
axes[0].axvline(0,color='#42454b',ls='--',lw=.9)
axes[0].set_yticks(range(len(labels)),list(labels.values()))
axes[0].invert_yaxis()
axes[0].set(xlabel=r'$M_V-m_1-m_2$ [GeV]',ylabel=r'$M_V$ [GeV] / $g_t$',title='All central relic solutions')
axes[0].scatter([],[],c='#276784',label='On shell')
axes[0].scatter([],[],c='#a9303d',marker='D',label='Off shell')
axes[0].legend(frameon=False,fontsize=8)
for r in base:
    if not r['tj_exp']:
        continue
    values=[float(r['tj_'+k]) for k in ('exp_750','exp','exp_1500','exp_full_energy')]
    y=[v if math.isfinite(v) else math.nan for v in values]
    axes[1].plot(range(4),y,marker='o',ms=4,label=labels[r['point']])
axes[1].set_xticks(range(4),['0.75','1.0','1.5','Full'])
axes[1].axhline(1,color='#42454b',ls='--',lw=.9)
axes[1].set(yscale='log',xlabel=r'Maximum $\sqrt{\hat s}$ [TeV]',ylabel=r'Median expected $\mu_{95}$',
            title='Single-top energy-cut dependence')
axes[1].legend(title=r'$M_V$ [GeV] / $g_t$',frameon=False,fontsize=8)
save(fig,'05_branches_and_single_top')

counts=Counter((r['case'],r['branch']) for r in physical if r['sigma_omega']=='0')
print('Cells',len(cells),'calls',sum(c['calls'] for c in cells),'failed',sum(c['failed'] for c in cells))
print('Root counts at central Planck',sorted(counts.items()))
print('Unstable central branch counts',Counter(r['case'] for r in summary if not r['stable_branch_count']))

"""Compare independent template replicas with the manuscript's CMS recast."""

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


HERE=Path(__file__).resolve().parent
DATA=HERE/'data'
SAMPLES=DATA/'template_validation'
AUDIT=HERE.parent/'lz_mixing_uncertainty_20261110/collider_errors.py'
context={'__file__':str(AUDIT),'__name__':'template_validation_likelihood'}
source=AUDIT.read_text(encoding='utf-8').split('\nrows=list(propagate())',1)[0]
exec(compile(source,str(AUDIT),'exec'),context)
asymov=context['mono_asimov']
observed=context['mono_observed']
conditional=context['conditional_asimov']
cms=context['cms']
to_yields=context['to_yields']
template_covariance=context['template_covariance']
interpolate=context['interpolate']
interpolate_covariance=context['interpolate_covariance']
nodes=context['mono_masses']


def write(path,rows):
    with path.open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def sample(path):
    with np.load(path) as data:
        n,x,e=(data[key] for key in ('counts','cross','cross_error'))
        assert n.sum()>0 and n[1:].sum()>0 and float(data['alignment'])<.005
        signal=to_yields(n,x)
        cov=template_covariance(n,x,e)
        info={k:data[k].item() for k in ('low','high','inside','hard_seed','shower_seed')}
        info.update(events=int(n.sum()),selected=int(n[1:].sum()),cross_pb=float(x),error_pb=float(e))
    return signal,cov,info


def group(mass,replica,prefix,size,low_suffix=''):
    records=[]
    suffixes=[]
    for i in range(size):
        suffix=low_suffix if i==0 else ''
        candidate=SAMPLES/f'{mass:g}_{replica}_{prefix}{i}{suffix}.npz'
        if i==1 and not candidate.is_file():
            suffix='_bulk'
            candidate=SAMPLES/f'{mass:g}_{replica}_{prefix}{i}{suffix}.npz'
        records.append(sample(candidate))
        suffixes.append(suffix)
    info=[r[2] for r in records]
    for suffix,r in zip(suffixes,info,strict=True):
        r['source']=suffix.lstrip('_') if suffix else 'independent'
        r['partitioned']=r['source']=='partition'
    assert all(a['high']==b['low'] for a,b in zip(info,info[1:])) and math.isinf(info[-1]['high'])
    return (sum(r[0] for r in records),sum(r[1] for r in records)),info


def add(a,b):
    return a[0]+b[0],a[1]+b[1]


def old(mass,channel):
    v=interpolate([mass],nodes,np.array(context['signals'][channel]))[0]
    c=interpolate_covariance(np.array([mass]),nodes,np.array(context['covs'][channel]))[0]
    return v,c


def limit(signal,cov,scale):
    full=cov+.016**2*np.outer(signal,signal)
    exp=asymov.upper(signal,full)
    obs=observed.upper(signal,full,exp,conditional)[0]
    return exp/scale,obs/scale


with (DATA/'benchmark_roots.csv').open(newline='') as f:
    benchmarks=list(csv.DictReader(f))
selected={120.:3.073,150.4:3.545,190.4:3.545}
if len(sys.argv)>1:
    selected={m:selected[m] for m in map(float,sys.argv[1:])}
limits=[]; bins=[]; summaries=[]; runs=[]; pooled_templates=[]
low=np.array([float(row['met_low_GeV']) for row in cms])
fig,axes=plt.subplots(2,len(selected),figsize=(4.1*len(selected),5.8),layout='constrained',squeeze=False)
colors={'A':'#216a94','B':'#b16b36','pooled':'#31444d'}
for column,(mass,gt) in enumerate(selected.items()):
    root=next(r for r in benchmarks if r['case']=='base' and r['sigma_omega']=='0' and r['branch']=='on'
              and float(r['mv_GeV'])==mass and abs(float(r['gt'])-gt)<.001)
    scale=float(root['gt'])**2*float(root['BR_invisible'])
    rate_variants=[r for r in benchmarks if r['point']==root['point'] and r['branch']=='on' and r['sigma_omega']=='0'
                   and r['case'] in {'base','rate0.75','rate0.9','rate1.1','rate1.25'}]
    assert len(rate_variants)==5
    rate_scale=[float(root['BR_invisible'])/float(r['BR_invisible']) for r in rate_variants]
    original_loop,original_tree=old(mass,'loop'),old(mass,'tree')
    source_a=next(suffix for suffix in ('','_archive','_bulk','_partition')
                  if (SAMPLES/f'{mass:g}_A_loop0{suffix}.npz').is_file())
    partition=source_a=='_partition'
    loop_a,info_a=group(mass,'A','loop',3,source_a)
    loop_b,info_b=group(mass,'B','loop',3,'_partition' if partition else '')
    new_tree,info_tree=group(mass,'new','tree',2)
    for label,infos in [('A',info_a),('B',info_b),('tree',info_tree)]:
        runs.extend(dict(mv_GeV=mass,replica=label,stratum=i,**row) for i,row in enumerate(infos))
    cross_cov=0.
    if partition:
        a,b=[sample(SAMPLES/f'{mass:g}_{r}_loop0_partition.npz') for r in ('A','B')]
        assert a[2]['hard_seed']==b[2]['hard_seed'] and a[2]['cross_pb']==b[2]['cross_pb']
        cross_cov=np.outer(a[0],b[0])*(a[2]['error_pb']/a[2]['cross_pb'])**2
        cross_cov=cross_cov+cross_cov.T
    pooled_loop=((loop_a[0]+loop_b[0])/2,(loop_a[1]+loop_b[1]+cross_cov)/4)
    templates={'main':add(original_loop,original_tree),'A':add(loop_a,new_tree),'B':add(loop_b,new_tree),
               'pooled':add(pooled_loop,new_tree),'A_with_original_tree':add(loop_a,original_tree),
               'B_with_original_tree':add(loop_b,original_tree)}
    pooled_templates.append(templates['pooled'])
    fits={label:limit(*value,scale) for label,value in templates.items()}
    assert abs(fits['main'][1]-float(root['mono_observed']))<2e-5
    # Rank individual year and MET bins without using observed data or the replicas.
    nominal=templates['main'][0]
    weights=np.linalg.solve(asymov.covariance+np.diag(asymov.b),nominal)
    ranking=np.argsort(-np.abs(nominal*weights))
    rank=np.empty(len(cms),dtype=int)
    rank[ranking]=np.arange(1,len(cms)+1)
    top=ranking[:8]
    compare=loop_a[1]+loop_b[1]-cross_cov
    diff=loop_a[0]-loop_b[0]
    diag=np.diag(compare)
    pulls=np.divide(diff,np.sqrt(diag),out=np.full_like(diff,np.nan),where=diag>0)
    for label,fit in fits.items():
        signal=templates[label][0]
        expected_fixed=asymov.upper(signal)
        observed_fixed=observed.upper(signal,None,expected_fixed,conditional)[0]
        limits.append(dict(mv_GeV=mass,gt=root['gt'],variant=label,expected_mu95=fit[0],observed_mu95=fit[1],
                           expected_fixed_mu95=expected_fixed/scale,observed_fixed_mu95=observed_fixed/scale,
                           observed_r_min=fit[1]*min(rate_scale),observed_r_max=fit[1]*max(rate_scale)))
    for i,r in enumerate(cms):
        row=dict(mv_GeV=mass,year=r['year'],met_low_GeV=low[i],sensitivity_rank=rank[i],
                 observed_count=context['data'][i],background=asymov.b[i],pull_A_minus_B=pulls[i])
        for label,(s,c) in templates.items():
            row[f'{label}_yield']=s[i]*scale
            row[f'{label}_mc_error']=math.sqrt(max(0,c[i,i]))*scale
        bins.append(row)
    for lower,upper in ((470,690),(690,np.inf)):
        mask=(low>=lower)&(low<upper)
        interval_variance=compare[np.ix_(mask,mask)].sum()
        row=dict(mv_GeV=mass,met_low_GeV=lower,met_high_GeV=upper,
                 max_abs_top8_bin_pull=np.nanmax(abs(pulls[top])),
                 interval_pull_A_minus_B=diff[mask].sum()/math.sqrt(interval_variance))
        for label,(s,c) in templates.items():
            row[f'{label}_yield']=s[mask].sum()*scale
            row[f'{label}_mc_error']=math.sqrt(c[np.ix_(mask,mask)].sum())*scale
        summaries.append(row)
    ax=axes[0,column]
    ax.set_title(f'$M_V={mass:g}$ GeV')
    for i,label in enumerate(('A','B','pooled')):
        fit=fits[label]
        ax.scatter([i-.1,i+.1],fit,marker='o',c=['#546c86','#bf5b4c'],s=23)
    ax.axhline(1,ls=':',color='#464c51',lw=.8)
    ax.axhline(fits['main'][1],ls='--',color='#bf5b4c',lw=.85)
    ax.set_xticks(range(3),['A','B','Pooled'])
    ax.set_ylim(0,max(1.05,1.15*max(max(pair) for pair in fits.values())))
    ax=axes[1,column]
    for i,label in enumerate(('A','B','pooled')):
        summary=[r for r in summaries if r['mv_GeV']==mass]
        x=np.arange(2)+(i-1)*.18
        y=[r[f'{label}_yield']/r['main_yield'] for r in summary]
        err=[r[f'{label}_mc_error']/r['main_yield'] for r in summary]
        ax.errorbar(x,y,yerr=err,marker='o',ls='none',capsize=3,color=colors[label],label=label)
    ax.axhline(1,ls='--',color='#646a6e',lw=.85)
    ax.set_xticks([0,1],['470–690','≥690'])
    ax.set_xlabel(r'$p_T^{\rm miss}$ interval [GeV]')
    ax.set_ylim(.62,1.41)
axes[0,0].set_ylabel(r'95% CL limit $\mu_{95}$')
axes[1,0].set_ylabel('Signal yield / main template')
axes[0,-1].scatter([],[],c='#546c86',label='Median expected')
axes[0,-1].scatter([],[],c='#bf5b4c',label='Observed')
axes[0,-1].plot([],[],ls='--',c='#bf5b4c',label='Main observed')
axes[0,-1].legend(frameon=False,fontsize=7.5,loc='center right',bbox_to_anchor=(.99,.76))
axes[1,-1].legend(frameon=False,fontsize=7.5,loc='lower left')
fig.savefig(HERE/'figures/c06_three_template_replicas.png',dpi=210)
fig.savefig(HERE/'figures/c06_three_template_replicas.svg')
write(DATA/'template_validation_limits.csv',limits)
write(DATA/'template_validation_bins.csv',bins)
write(DATA/'template_validation_tail.csv',summaries)
write(DATA/'template_validation_runs.csv',runs)
np.savez_compressed(DATA/'template_validation_pooled.npz',masses=list(selected),
                    signals=np.array([s for s,c in pooled_templates]),covariances=np.array([c for s,c in pooled_templates]))
seeds=[r['hard_seed'] for r in runs]
assert len(seeds)==8*len(selected) and len(set(seeds))==len(seeds)-sum(r['partitioned'] for r in runs)//2
for r in summaries:
    print(json.dumps(r),flush=True)
for r in limits:
    print(json.dumps(r),flush=True)

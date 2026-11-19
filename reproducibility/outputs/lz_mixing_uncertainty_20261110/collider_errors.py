"""Refit CMS templates for each physical root and report distinct uncertainty sources."""

import csv
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist

import numpy as np
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
MONO = HERE.parent/'monojet_expected_lz_scan_20261106'
SINGLE = HERE.parent/'single_top_pilot_20261110'
sys.path.insert(0,str(MONO/'scripts'))
sys.path.insert(0,str(HERE.parent/'monojet_mchi_scan_20261106/scripts'))
from expected_scan import (cms_inputs, interpolate, interpolate_covariance, load_templates,
                           template_covariance, to_yields)
from observed_fit import ObservedFit
from refit_gap120 import load_replica
from scan_observed import PhysicalAsimov, public_data


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


normal=NormalDist()
targets={z:(z-normal.inv_cdf(.05*normal.cdf(z)))**2 for z in [-2,-1,0,1,2]}


def crossing(q,target):
    hi=0.001
    while q(hi)<target:
        hi*=2
        if hi>1e8:
            return math.inf
    return brentq(lambda x:q(x)-target,0.,hi,xtol=1e-8,rtol=1e-8)


def signal_limits(q):
    return [crossing(q,targets[z]) for z in [-2,-1,0,1,2]]


def widths(mv,mchi,gc,width):
    a,b=(mchi/mv)**2,((mchi+.001)/mv)**2
    phase=math.sqrt(max(0.,(1-((2*mchi+.001)/mv)**2)*(1-(.001/mv)**2)))
    spin=1-(a+b)/2-(a-b)**2/2+3*math.sqrt(a*b)
    return (gc/2)**2*mv*phase*spin/(12*math.pi*width)


cms, fit, old=cms_inputs()
mono_b,mono_cov=fit.b,fit.covariance
mono_asimov=PhysicalAsimov(mono_b,mono_cov)
data=public_data(cms,mono_b,mono_cov)
mono_observed=ObservedFit(data,mono_b,mono_cov)
conditional_asimov=PhysicalAsimov(mono_observed.profile(0.,old).mean,mono_cov)
nodes=load_templates(MONO/'templates')
replicas=HERE.parent/'monojet_mchi_scan_20261106/results/gap120/replicas'
nodes[120.].update(loop=load_replica(replicas/'loop_below230.npz'),
                   loop_enriched=load_replica(replicas/'loop_m18.npz'))
mono_masses=np.array(list(nodes))
signals={key:[] for key in ('loop','tree')}
covs={key:[] for key in signals}
for samples in nodes.values():
    for key in signals:
        selected=[v for n,v in samples.items() if ('loop' if n.startswith('loop') else 'tree')==key]
        signals[key].append(sum(to_yields(n,cross) for n,cross,err in selected))
        covs[key].append(sum(template_covariance(*sample) for sample in selected))


@lru_cache(maxsize=None)
def mono_limits(mv,d):
    s={k:interpolate([mv],mono_masses,np.array(v))[0] for k,v in signals.items()}
    c={k:interpolate_covariance(np.array([mv]),mono_masses,np.array(v))[0] for k,v in covs.items()}
    loop=(1+2*d/3)**2
    ratios=[(1+q*d/(m/172))**2 for m,q in [(.0022,2/3),(.0047,-1/3),(.096,-1/3),(1.27,2/3),(4.18,-1/3)]]

    def response(tree):
        return loop*s['loop']+tree*s['tree'],loop**2*c['loop']+tree**2*c['tree']

    s0,c0=response(1.)
    errors=c0+.016**2*np.outer(s0,s0)
    exp=signal_limits(lambda v:mono_asimov.q(v,s0,errors))
    mc_free=mono_asimov.upper(s0)
    tree_tests=[]
    for edge in (min(ratios),max(ratios)):
        st,ct=response(edge)
        tree_tests.append(mono_asimov.upper(st,ct+.016**2*np.outer(st,st)))
    observed=math.nan
    if d==0:
        observed=mono_observed.upper(s0,errors,exp[2],conditional_asimov)[0]
    return dict(experimental=exp,no_signal_uncert=mc_free,tree_tests=tree_tests,
                observed=observed,tree_fraction=s['tree'].sum()/(s['tree']+s['loop']).sum())


cms_tj=json.loads((SINGLE/'hepdata_AH1b1FJ.json').read_text())
group=next(q['group'] for q in cms_tj['qualifiers']['Process'] if q['value']=='$Background$')
selected=[next(y for y in row['y'] if y['group']==group) for row in cms_tj['values']]
b=np.array([float(y['value']) for y in selected])
db=np.array([float(y['errors'][0]['symerror']) for y in selected])
templates=[json.loads(line) for line in (SINGLE/'tj_expected_templates.jsonl').read_text().splitlines()]
on=sorted((r for r in templates if r['benchmark'].startswith('ON')),key=lambda r:float(r['mv_GeV']))
tj_masses=np.array([float(r['mv_GeV']) for r in on])
samples={r['benchmark']:r for r in read(SINGLE/'single_top_pilot.csv')+read(SINGLE/'tj_expected_anchors.csv') if r['channel']=='tj'}


def scale_at_anchor(row):
    mv,gt,mchi,gc=map(float,[row['mv_GeV'],row['gt'],row['mchi_GeV'],row['gchi']])
    partial=sum(3*(gt*m/172)**2*mv*(1+2*(m/mv)**2)*math.sqrt(1-4*(m/mv)**2)/(12*math.pi)
                for m in [.0022,.0047,.096,1.27,4.18])
    invisible=widths(mv,mchi,gc,1.)
    return gt**2*invisible/(invisible+partial)


def tj_template(row,mode):
    sample=samples[row['benchmark']]
    cross=float(sample['sigma_fb'])
    p=np.array(row['fiducial_'+mode])/cross
    factor=138*.674*.70*cross
    signal=factor*p
    # With one MET bin per original event, a Bernoulli covariance is an upper
    # bound for the MC noise of the event-level averaged acceptance weights.
    cov=factor**2*np.diag(p)/int(sample['events'])
    cov+=(float(sample['integration_error_fb'])/cross)**2*np.outer(signal,signal)
    return signal,cov


def diagonal_deviance(mu, signal, signal_var, background_var):
    # Asimov n=b. The nonnegative signal bound is handled bin by bin.
    delta=mu*signal
    var=background_var+mu**2*signal_var
    score=2*delta/(b+delta+var+np.sqrt((b+delta-var)**2+4*b*var))
    relative=score/(1-score)
    free=2*b*(relative-np.log1p(relative))+var*score**2
    bound=signal-mu*signal_var*score<0
    penalty=np.divide(signal**2,signal_var,out=np.zeros_like(signal),where=signal_var>0)
    return np.where(bound,penalty,free).sum()


@lru_cache(maxsize=None)
def single_limits(mv,mode):
    signals,covs=[],[]
    for row in on:
        s,c=tj_template(row,mode)
        factor=scale_at_anchor(row)
        signals.append(s/factor)
        covs.append(c/factor**2)
    s=interpolate([mv],tj_masses,np.array(signals))[0]
    c=interpolate_covariance(np.array([mv]),tj_masses,np.array(covs))[0]
    vstat=np.diag(c)
    exp=signal_limits(lambda mu:diagonal_deviance(mu,s,vstat,db**2))
    no_signal_uncert=crossing(lambda mu:diagonal_deviance(mu,s,0.,db**2),targets[0])
    stat=crossing(lambda mu:diagonal_deviance(mu,s,vstat,0.),targets[0])
    return dict(experimental=exp,no_signal_uncert=no_signal_uncert,stat_only=stat)


def empty_fields(prefix):
    keys=('exp_m2','exp_m1','exp','exp_p1','exp_p2','no_signal_uncert','observed','tree_a','tree_b',
          'tree_fraction','exp_750','exp_1500','exp_full_energy','stat_only')
    return {prefix+'_'+k:'' for k in keys}


def propagate():
    source=HERE/'relic_roots.jsonl'
    audit=read(HERE/'relic_numerical_audit.csv')
    refined=min((r for r in audit if r['kind']=='refine'),key=lambda r:abs(float(r['omega_h2'])-.1212))
    for cell in (json.loads(line) for line in source.read_text().splitlines()):
        if cell['case']=='small_mix_high_rate' and cell['point']=='OFF_60_2' and not cell['roots']['1']:
            keys=('mchi_GeV','omega_h2','xf','width_GeV','gchi')
            cell['roots']['1']=[['off',*(float(refined[k]) for k in keys)]]
        mv,gt,d=(cell[k] for k in ('mv_GeV','gt','d'))
        for k,roots in cell['roots'].items():
            count={'on':0,'off':0}
            for branch,mchi,omega,xf,width,gc in roots:
                count[branch]+=1
                gap=mv-2*mchi-.001
                row={key:cell[key] for key in ('case','d','rate','f2','point','mv_GeV','gt')}
                row.update(sigma_omega=int(k),branch=branch,root=count[branch],mchi_GeV=mchi,gchi=gc,
                           omega_h2=omega,xf=xf,width_GeV=width,gap_GeV=gap,BR_invisible=0.)
                row.update(empty_fields('mono'));row.update(empty_fields('tj'))
                if branch=='on':
                    br=widths(mv,mchi,gc,width)
                    row['BR_invisible']=br
                    if gap>=5*width and width/mv<.03 and abs(d)<=5e-5:
                        if mono_masses[0]<=mv<=mono_masses[-1]:
                            mu=mono_limits(mv,d)
                            scale=gt**2*br
                            for name,value in zip(('exp_m2','exp_m1','exp','exp_p1','exp_p2'),mu['experimental']):
                                row['mono_'+name]=value/scale
                            row['mono_no_signal_uncert']=mu['no_signal_uncert']/scale
                            row['mono_observed']=mu['observed']/scale
                            row['mono_tree_a'],row['mono_tree_b']=(v/scale for v in mu['tree_tests'])
                            row['mono_tree_fraction']=mu['tree_fraction']
                        if tj_masses[0]<=mv<=tj_masses[-1]:
                            # Top radiation controls the nominal weak-process template. The
                            # light/bottom-emission shape change is outside this proxy.
                            scale=gt**2*(1+2*d/3)**2*br
                            mu=single_limits(mv,'1000')
                            for name,value in zip(('exp_m2','exp_m1','exp','exp_p1','exp_p2'),mu['experimental']):
                                row['tj_'+name]=value/scale
                            row['tj_no_signal_uncert']=mu['no_signal_uncert']/scale
                            row['tj_stat_only']=mu['stat_only']/scale
                            for label,mode in [('750','750'),('1500','1500'),('full_energy','full')]:
                                row['tj_exp_'+label]=single_limits(mv,mode)['experimental'][2]/scale
                yield row


rows=list(propagate())
assert all(abs(r['omega_h2']-(.12+.0012*r['sigma_omega']))<1.01e-5 for r in rows)
write(HERE/'physical_roots_and_limits.csv',rows)
print('Evaluated',len(rows),'physical roots',flush=True)

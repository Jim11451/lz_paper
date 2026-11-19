"""Conditional one-event recoil likelihood, not the full LZ S1/S2 analysis.

Nominal: perfect energy reconstruction, unit efficiency, negligible background.
Sensitivity check: a constant Gaussian width sqrt(23^2+23^2) keV.
The latter is an explicit proxy, NOT an official detector resolution matrix.
"""
import csv,json,math,time
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import erf,ndtr
from scipy.optimize import differential_evolution
from scipy.stats import chi2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'pseudoDirac_yukawaLZ_20261020'
RESULT=ROOT/'results';PLOTS=ROOT/'plots'
EXPOSURE=2.84*1000*365.25
EVENT=248.;ROI=(5.4,269.9);SB=(350.,675.)
ARES=np.array([124,126,128,129,130,131,132,134,136])
ABUND=np.array([.00095,.00089,.01910,.26401,.04071,.21232,.26909,.10436,.08857])
MASS=.93149410242*ARES
WEIGHT=ABUND*ARES/np.sum(ABUND*ARES)
QP=(2*.0022+.0047)/172;QN=(.0022+2*.0047)/172
QA=54*QP+(ARES-54)*QN
V0=238.;VE=254.;VESC=544.;CVEL=299792.458
Z=VESC/V0;Y=VE/V0;NORM=erf(Z)-2*Z/np.sqrt(np.pi)*np.exp(-Z*Z)

def eta(vmin):
    x=np.asarray(vmin)/V0
    low=(erf(x+Y)-erf(x-Y)-4*Y/np.sqrt(np.pi)*np.exp(-Z*Z))/(2*NORM*VE)
    high=(erf(Z)-erf(x-Y)-2*(Z-x+Y)/np.sqrt(np.pi)*np.exp(-Z*Z))/(2*NORM*VE)
    return np.maximum(0,np.where(x<Z-Y,low,np.where(x<Z+Y,high,0)))

def fermi_squared(energy):
    # Actual micrOMEGAs FermiFF: radius=1.23*A^(1/3)-0.6 fm,
    # diffuseness=0.52 fm; radial integral ends at radius+5 fm.
    x,w=leggauss(256);out=[]
    for a,mass in zip(ARES,MASS):
        radius=1.23*a**(1/3)-.6
        r=(x+1)*(radius+5)/2;wr=w*(radius+5)/2
        density=r*r/(1+np.exp((r-radius)/.52))
        q=np.sqrt(2*mass*np.asarray(energy)*1e-6)/.197327
        f=np.sinc(q[:,None]*r[None,:]/np.pi)@(density*wr)/np.sum(density*wr)
        out.append(f*f)
    return np.array(out)

def rate_raw(mchi,delta,mv,energy,ff):
    mu=MASS*mchi/(MASS+mchi)
    er=energy[None,:]*1e-6
    vmin=CVEL*np.abs(MASS[:,None]*er/mu[:,None]-delta*1e-6)/np.sqrt(2*MASS[:,None]*er)
    return np.sum((WEIGHT*QA*QA)[:,None]*ff*eta(vmin)/(mv*mv+2*MASS[:,None]*er)**2,axis=0)/mchi

refpath=next((OLD/'results').glob('root_recoil_MV30_*.csv'))
ref=np.genfromtxt(refpath,delimiter=',',names=True,skip_header=3)
eref=ref[ref.dtype.names[0]];rref=ref[ref.dtype.names[1]]
pref=.03800633448666564
raw=rate_raw(35,1000,30,eref,fermi_squared(eref))*pref**2
mask=rref>max(rref)*.01
CONSTANT=float(np.median(rref[mask]/raw[mask]))
relative=np.max(np.abs(CONSTANT*raw[mask]/rref[mask]-1))
print('REFERENCE_MAX_RELATIVE_RATE_DIFFERENCE',relative,flush=True)
assert relative<.003, relative

E=np.unique(np.r_[np.linspace(.1,1000,2001),*ROI,*SB,EVENT])
FF=fermi_squared(E)
W=np.r_[np.diff(E)[0]/2,(E[2:]-E[:-2])/2,np.diff(E)[-1]/2]

def interval_weights(lo,hi):
    selected=(E>=lo)&(E<=hi)
    ix=np.flatnonzero(selected);w=np.zeros_like(E)
    w[ix]=np.r_[np.diff(E[ix])[0]/2,(E[ix][2:]-E[ix][:-2])/2,np.diff(E[ix])[-1]/2]
    return w

CASES={}
for name,sigma in [('ideal',0.),('gaussian_proxy',math.hypot(23,23))]:
    if sigma==0:
        wr=interval_weights(*ROI);ws=interval_weights(*SB)
        we=np.zeros_like(E);we[np.argmin(abs(E-EVENT))]=1
    else:
        wr=W*(ndtr((ROI[1]-E)/sigma)-ndtr((ROI[0]-E)/sigma))
        ws=W*(ndtr((SB[1]-E)/sigma)-ndtr((SB[0]-E)/sigma))
        we=W*np.exp(-.5*((EVENT-E)/sigma)**2)/(sigma*np.sqrt(2*np.pi))
    CASES[name]={'sigma':sigma,'wr':wr,'ws':ws,'we':we}

def evaluate(mchi,delta,mv=87.1833386421,case='ideal'):
    r=CONSTANT*rate_raw(mchi,delta,mv,E,FF)*EXPOSURE
    cfg=CASES[case]
    nr=r@cfg['wr'];ns=r@cfg['ws'];density=r@cfg['we']
    total=nr+ns
    if total<=0 or density<=0:return None
    scale=1/total
    return {'mchi_GeV':float(mchi),'delta_keV':float(delta),'MV_GeV':mv,
            'product_gt_gchi_MLE':float(np.sqrt(scale)),
            'N_ROI_MLE':float(nr/total),'N_SB_MLE':float(ns/total),
            'density_at_248_events_per_keV':float(density/total),
            'shape_nll':float(-np.log(density/total)),'rate_scale':float(scale)}

fitresults={}
scanrows=[]
for case in CASES:
    def objective(x):
        r=evaluate(np.exp(x[0]),x[1],case=case)
        return r['shape_nll'] if r else 1e50
    opt=differential_evolution(objective,[(np.log(10),np.log(1000)),(150,1021.9979)],
                               seed=871,polish=True,tol=2e-8,popsize=12)
    best=evaluate(np.exp(opt.x[0]),opt.x[1],case=case)
    benchmark=evaluate(35,1000,case=case)
    benchmark['two_delta_nll_vs_best']=2*(benchmark['shape_nll']-best['shape_nll'])
    fitresults[case]={'best':best,'benchmark_m35_delta1000':benchmark,
                      'gaussian_width_keV':CASES[case]['sigma']}
    print('FIT',case,json.dumps(fitresults[case]),flush=True)

# Profile-likelihood map: normalize the amplitude analytically at each point.
MG=np.geomspace(10,1000,91);DG=np.linspace(150,1021.9979,121)
for mchi in MG:
    mu=MASS*mchi/(MASS+mchi)
    er=E[None,None,:]*1e-6
    vmin=CVEL*np.abs(MASS[None,:,None]*er/mu[None,:,None]-DG[:,None,None]*1e-6)/np.sqrt(2*MASS[None,:,None]*er)
    shape=np.sum((WEIGHT*QA*QA)[None,:,None]*FF[None,:,:]*eta(vmin)/(87.1833386421**2+2*MASS[None,:,None]*er)**2,axis=1)/mchi
    for case,cfg in CASES.items():
        nr=shape@cfg['wr'];ns=shape@cfg['ws'];de=shape@cfg['we']
        probability=np.divide(de,nr+ns,out=np.zeros_like(de),where=(nr+ns)>0)
        nll=-np.log(np.maximum(probability,1e-300))
        q=2*(nll-fitresults[case]['best']['shape_nll'])
        for delta,value in zip(DG,q):scanrows.append({'case':case,'mchi_GeV':float(mchi),'delta_keV':float(delta),'two_delta_nll':float(value)})
with (RESULT/'shape_profile_scan.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=scanrows[0]);w.writeheader();w.writerows(scanrows)

mu_intervals={}
for cl in [.682689492,.95]:
    alpha=1-cl
    mu_intervals[str(cl)]=[float(.5*chi2.ppf(alpha/2,2)),float(.5*chi2.ppf(1-alpha/2,4))]

points=[('MV30',30.,.127626842306,.297792641421),
        ('MV62_gc03',62.2627568245,.54569366783,.3),
        ('MV87_gc03',87.1833386421,1.06993948302,.3),
        ('MV87_gc02',87.5299315453,1.61769505789,.2),
        ('MV86_gc1',86.0484642982,.312679727321,1.)]
normrows=[]
for case in CASES:
    for name,mv,gt,gc in points:
        r=evaluate(35,1000,mv,case)
        p=r['product_gt_gchi_MLE']
        nold=(gt*gc/p)**2
        row={'case':case,'benchmark':name,'MV_GeV':mv,'gChi_fixed':gc,'gt_original':gt,
             'gt_LZ_only_MLE':p/gc,'product_MLE':p,'N_expected_original':nold,
             'N_ROI_MLE':r['N_ROI_MLE'],'N_SB_MLE':r['N_SB_MLE'],
             'gt_Garwood95_low':p/gc*np.sqrt(mu_intervals['0.95'][0]),
             'gt_Garwood95_high':p/gc*np.sqrt(mu_intervals['0.95'][1])}
        normrows.append(row)
with (RESULT/'current_benchmark_normalization_fits.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=normrows[0]);w.writeheader();w.writerows(normrows)

fitresults['assumptions']={'event_keV':248,'exposure_tonne_year':2.84,'ROI_keV':ROI,'sideband_keV':SB,
    'background':0,'nominal_efficiency':1,'fExc':.5,'rho_total_GeV_cm3':.3,
    'form_factor':'micrOMEGAs numerical two-parameter Fermi, NOT analytic Helm',
    'shape_scan_mchi_GeV':[10,1000],'shape_scan_delta_keV':[150,1021.9979],
    'coupling_constraint':'profile g_t*gChi freely; no relic recomputation at shifted fits',
    'reference_max_relative_rate_difference':float(relative),
    'official_detector_response':False,'official_S1_S2_background_likelihood':False,
    'Gaussian_proxy':'constant sqrt(stat^2+sys^2), illustrative; not measured resolution function'}
fitresults['exact_Poisson_Garwood_mean_intervals']=mu_intervals
(RESULT/'fit_summary.json').write_text(json.dumps(fitresults,indent=2))

# Public data inventory: show the official S1/S2 points without inventing energies.
def public_sample(filename):
    lines=[l for l in (ROOT/'sources'/filename).read_text().splitlines() if l and not l.startswith('#')]
    return np.array([[float(v) for v in row] for row in csv.reader(lines[1:])])
science=public_sample('science_sample.csv')
nearest=np.argmin(abs(science[:,0]-540.1))
inventory={'n_science':len(science),'n_prompt':len(public_sample('prompt_veto_sample.csv')),
           'n_delayed':len(public_sample('delayed_veto_sample.csv')),
           'candidate_nearest_S1':[float(v) for v in science[nearest]],
           'record_tables':len(json.loads((ROOT/'sources/hepdata_record.json').read_text())['data_tables'])}
(RESULT/'public_data_inventory.json').write_text(json.dumps(inventory,indent=2))
print('PUBLIC_DATA',json.dumps(inventory),flush=True)

plt.rcParams.update({'font.size':11,'axes.grid':True,'grid.alpha':.18,'savefig.dpi':180})
spectra_rows=[]
fig,axes=plt.subplots(1,2,figsize=(12,4.6))
ax=axes[0]
for m,d,label,color in [(35,1000,r'Current $m_\chi=35$ GeV, $\delta=1000$ keV','#0072b2'),
                       (fitresults['ideal']['best']['mchi_GeV'],fitresults['ideal']['best']['delta_keV'],'Shape-profile maximum (ideal response)','#d55e00')]:
    r=evaluate(m,d)
    y=CONSTANT*rate_raw(m,d,87.1833386421,E,FF)*r['rate_scale']*1000*365.25
    for energy,value in zip(E,y):spectra_rows.append({'curve':label,'energy_keV':float(energy),'rate_events_per_tonne_year_keV':float(value)})
    ax.plot(E,y,label=label,color=color,lw=2)
ax.axvline(248,color='k',ls=':',label='One candidate at 248 keV')
ax.axvspan(248-math.hypot(23,23),248+math.hypot(23,23),color='grey',alpha=.12,label='Reported energy uncertainty')
ax.axvspan(*ROI,color='#009e73',alpha=.05);ax.axvspan(*SB,color='#d55e00',alpha=.05)
ax.set(xlim=(30,700),ylim=(1e-7,.03),yscale='log',xlabel=r'$E_R$ [keV]',ylabel=r'$dR/dE_R$ [events tonne$^{-1}$ yr$^{-1}$ keV$^{-1}$]',title='Fitted underlying recoil spectra')
ax.legend(fontsize=8,loc='upper right')
ax=axes[1]
bench=fitresults['gaussian_proxy']['benchmark_m35_delta1000']
best=fitresults['gaussian_proxy']['best']
obs=np.arange(20.,701.,2.)
kernel=np.exp(-.5*((obs[:,None]-E[None,:])/math.hypot(23,23))**2)/(math.hypot(23,23)*np.sqrt(2*np.pi))
for r,label,c in [(bench,'Current mass/splitting, fitted amplitude','#0072b2'),(best,'Profile maximum, Gaussian proxy','#d55e00')]:
    y=CONSTANT*rate_raw(r['mchi_GeV'],r['delta_keV'],r['MV_GeV'],E,FF)*r['rate_scale']*EXPOSURE
    folded=kernel@(y*W)
    for energy,value in zip(obs,folded/2.84):spectra_rows.append({'curve':label+' (Gaussian proxy)','energy_keV':float(energy),'rate_events_per_tonne_year_keV':float(value)})
    ax.plot(obs,folded/2.84,label=label,color=c,lw=2)
ax.axvline(248,color='k',ls=':')
ax.axvspan(*ROI,color='#009e73',alpha=.05);ax.axvspan(*SB,color='#d55e00',alpha=.05)
ax.set(xlabel=r'$E_{\rm rec}$ [keV]',ylabel=r'Expected events tonne$^{-1}$ yr$^{-1}$ keV$^{-1}$',xlim=(30,700),title=r'Sensitivity check: Gaussian proxy, $\sigma_E=32.5$ keV')
ax.legend(fontsize=8)
fig.suptitle('Conditional one-candidate fit; no official detector/background likelihood',fontsize=12)
fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(PLOTS/f'fitted_recoil_spectra.{ext}',bbox_inches='tight')
plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(11,4.6),sharey=True)
for ax,case in zip(axes,CASES):
    q=np.array([r['two_delta_nll'] for r in scanrows if r['case']==case]).reshape(len(MG),len(DG))
    im=ax.pcolormesh(MG,DG,np.minimum(q.T,12),cmap='viridis_r',vmin=0,vmax=12,shading='auto')
    contour=ax.contour(MG,DG,q.T,levels=[2.30,6.18],colors=['white','red'])
    ax.clabel(contour,fmt={2.3:'q=2.30',6.18:'q=6.18'},fontsize=8)
    r=fitresults[case]['best']
    ax.plot(r['mchi_GeV'],r['delta_keV'],'*',color='orange',markersize=12,label='Profile maximum')
    ax.plot(35,1000,'x',color='black',ms=8,label='Current 35 GeV / 1 MeV')
    ax.set(xscale='log',xlabel=r'$m_\chi$ [GeV]',title='Ideal reconstruction' if case=='ideal' else 'Gaussian proxy (32.5 keV)')
axes[0].set_ylabel(r'$\delta$ [keV]')
axes[0].legend(fontsize=8,loc='lower left')
fig.suptitle('Shape profile; contours are likelihood references, not calibrated confidence regions',fontsize=11)
fig.subplots_adjust(top=.85,bottom=.14,right=.86,wspace=.1)
cax=fig.add_axes([.89,.14,.018,.71])
fig.colorbar(im,cax=cax,label=r'$q=2\Delta[-\ln\mathcal{L}]$')
for ext in ['png','pdf']:fig.savefig(PLOTS/f'shape_profile_likelihood.{ext}',bbox_inches='tight')
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.5,4.8))
ax.scatter(science[:,0],science[:,1],s=5,c='grey',alpha=.5,label='Official science sample (all components)')
ax.scatter(*science[nearest],s=85,c='#d55e00',marker='*',label='Candidate near S1=540.1 phd')
ax.set(xlabel=r'$S1_c$ [phd]',ylabel=r'$\log_{10}(S2_c/\mathrm{phd})$',title='Published observables; not a nuclear-recoil energy histogram')
ax.legend(fontsize=9)
fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(PLOTS/f'official_science_observables.{ext}',bbox_inches='tight')
plt.close(fig)
with (RESULT/'fitted_spectra.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=spectra_rows[0]);w.writeheader();w.writerows(spectra_rows)
print('DONE',json.dumps({'fits':fitresults,'norm':normrows}),flush=True)

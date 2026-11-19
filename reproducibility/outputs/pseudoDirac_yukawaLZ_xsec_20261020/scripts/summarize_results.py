import csv,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'results';PLOTS=ROOT/'plots'
PLOTS.mkdir(exist_ok=True)
def read(path):
    with path.open() as f:return list(csv.DictReader(f))
rows=read(DATA/'cross_sections.csv')
if (DATA/'extra_ttmet_cross_sections.csv').exists():rows+=read(DATA/'extra_ttmet_cross_sections.csv')
with (DATA/'all_cross_sections.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
for row in rows:
    assert float(row['sigma_fb'])>0,row
    assert int(row['N_generated'])>=2000,row
    assert 0<=float(row['BR_invisible'])<=1,row
    thresholds=[float(row[f'sigma_MET{x}_fb']) for x in [100,150,200,250,300,400,500]]
    assert all(a>=b for a,b in zip(thresholds,thresholds[1:])),row

points=['LZ_M30','LZ_M62_gc0p3','LZ_M86_gc1','LZ_M87_gc0p3','LZ_M87_gc0p1']
labels=[r'$M_V=30$'+'\n'+r'$g_t=0.128,g_\chi=0.298$',r'$M_V=62.3$'+'\n'+r'$g_t=0.546,g_\chi=0.3$',
        r'$M_V=86.0$'+'\n'+r'$g_t=0.313,g_\chi=1$',r'$M_V=87.2$'+'\n'+r'$g_t=1.070,g_\chi=0.3$',
        r'$M_V=87.1$'+'\n'+r'$g_t=3.205,g_\chi=0.1$']
lookup={(r['benchmark'],r['channel'],float(r['sqrt_s_TeV'])):r for r in rows}
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.2,'savefig.dpi':170})
fig,axes=plt.subplots(2,1,figsize=(10,8),sharex=True)
x=np.arange(len(points));bw=.24
for j,(channel,label,color) in enumerate([('ttmet',r'$t\bar t+\mathrm{MET}$','#0072b2'),('bbmet',r'$b\bar b+\mathrm{MET}$','#d55e00'),('monojet',r'$j+\mathrm{MET}$','#009e73')]):
    a=[lookup[(p,channel,13.6)] for p in points]
    for ax,key in zip(axes,['sigma_fb','sigma_MET200_fb']):
        ax.bar(x+(j-1)*bw,[float(r[key]) for r in a],width=bw,color=color,label=label,zorder=3)
        ax.set_yscale('log');ax.set_ylabel(r'$\sigma$ [fb]')
axes[0].set_title('Generation cuts only: stable tops; bottom pT > 25 GeV; jet pT > 200 GeV')
axes[1].set_title(r'Additional dark-pair $p_T^{\rm miss}>200$ GeV')
axes[0].legend(ncol=3)
axes[1].set_xticks(x,labels,fontsize=9)
fig.suptitle(r'LO, $pp$ at 13.6 TeV: tree-level LZ+relic candidate points'+'\n'+r'$m_{\chi_1}=35$ GeV, $\delta=1$ MeV; no detector simulation',fontsize=12)
fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(PLOTS/f'cross_section_comparison.{ext}',bbox_inches='tight')
plt.close(fig)

fig,ax=plt.subplots(figsize=(8,5))
for name,label,color in [('LZ_M87_gc0p3',r'$87.18$ GeV, $g_t=1.070,g_\chi=0.3$','#0072b2'),
                         ('LZ_M86_gc1',r'$86.05$ GeV, $g_t=0.313,g_\chi=1$','#d55e00'),
                         ('LZ_M87_gc0p2',r'$87.53$ GeV, $g_t=1.618,g_\chi=0.2$','#009e73')]:
    r=lookup[(name,'ttmet',13.)]
    mets=json.loads((DATA/f'{r["run_name"]}_MET.json').read_text())
    cuts=np.arange(0,501,10)
    sig=float(r['sigma_fb'])
    vals=[sig*sum(m>cut for m in mets)/len(mets) for cut in cuts]
    ax.step(cuts,vals,where='post',label=label,color=color,lw=2)
ax.set(yscale='log',xlabel=r'Dark-pair $p_T^{\rm miss}$ threshold [GeV]',ylabel=r'$\sigma(p_T^{\rm miss}>p_T^{\rm cut})$ [fb]',
       title=r'$t\bar t+\mathrm{MET}$, 13 TeV; stable tops, LO, no detector response',xlim=(0,500))
ax.legend(fontsize=9)
fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(PLOTS/f'ttmet_cumulative_cross_section.{ext}',bbox_inches='tight')
plt.close(fig)

nwa=read(DATA/'nwa_crosscheck.csv')[0]
full=lookup[('LZ_M87_gc0p3','ttmet',13.)]
ratio=float(nwa['sigma_times_BR_fb'])/float(full['sigma_fb'])
check={'full_2to4_fb':float(full['sigma_fb']),'on_shell_ttV_fb':float(nwa['sigma_fb']),
       'BR_invisible':float(nwa['BR_invisible']),'NWA_fb':float(nwa['sigma_times_BR_fb']),
       'NWA_over_full':ratio}
(DATA/'nwa_validation.json').write_text(json.dumps(check,indent=2))
print('NWA',json.dumps(check))
print('TABLE')
for name in points:
    rr=[lookup[(name,c,13.6)] for c in ['ttmet','bbmet','monojet']]
    print(name,[(r['channel'],float(r['sigma_fb']),float(r['sigma_MET200_fb'])) for r in rr])
print('RUN2')
for r in rows:
    if float(r['sqrt_s_TeV'])==13:print(r['benchmark'],r['sigma_fb'],r['sigma_MET200_fb'])
print('PASS: cross sections, generated counts, cumulative ordering, figures.')

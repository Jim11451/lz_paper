"""Tree-level vector-Yukawa scan; exact isotope recoil normalization.

Each mass fixes gYt*gChi by matching the original paper benchmark recoil
calculation, then solves Omega=0.12 with the independently compiled model.
Physical vertex perturbativity: gYt<sqrt(4pi), gChi/2<sqrt(4pi).
"""
import csv
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
TARGET_OMEGA = 0.12
MAX_GT = math.sqrt(4*math.pi)
MAX_GC = 2*MAX_GT
MASSES = [5,10,15,20,25,28,30,32,34,35,36,40,45,50,55,60,65,68,70,72,75,80,85,90,95,100,110,125,150,200,300,500,700]

def run(args):
    proc = subprocess.run([str(x) for x in args], cwd=ROOT,
                          capture_output=True,text=True,timeout=600)
    if proc.returncode:
        raise RuntimeError(proc.stdout+'\n'+proc.stderr)
    return proc.stdout

def par(path, mv, gt, gc):
    path.write_text(f'Mchi 35\ndM 0.001\nMV {mv:.15g}\ngYt {gt:.15g}\ngChi {gc:.15g}\nfExc 0.5\nrho0 0.3\nv0 238\nvE 254\nvesc 544\n')

original = ROOT.parent / 'pseudoDiracB_build'
# Reproduce the existing original benchmark, rather than importing a rounded count.
ref = run([original/'lz_recoil', original/'benchmark.par', OUT/'reference_recoil.csv'])
(OUT/'reference_recoil.log').write_text(ref)
target_n = float(re.search(r'ROI_5.4_269.9=([\deE.+-]+)',ref)[1])
# Verify this really is the original reference, gB=1.46e-5 and gChi=0.32.
assert re.search(r'gB=1.46e-05\s+gChi=0.32',ref), ref
print('REFERENCE',ref,flush=True)

evaluations=[]
roots=[]
summary=[]
cache={}

def evaluate(mv, product, gc, detail=False):
    key=(mv,gc)
    if key in cache and not detail:
        return cache[key]
    gt=product/gc
    text=run([ROOT/'relic_point',mv,gt,gc,1 if detail else 0])
    vals=dict(re.findall(r'(\w+)=([\deE.+-]+)',text.split('RESULT',1)[1].splitlines()[0]))
    row={k:float(v) for k,v in vals.items()}
    row['Gamma_over_MV']=row['width']/mv
    row['product']=product
    evaluations.append(row)
    with (OUT/'evaluations.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=row);w.writeheader();w.writerows(evaluations)
    cache[key]=row
    if detail:
        (OUT/f'root_MV{mv:g}_gc{gc:.6g}.log').write_text(text)
    return row

for mv in MASSES:
    card=ROOT/'scan_tmp.par'
    par(card,mv,1,1)
    recoil=run([ROOT/'lz_recoil',card,OUT/f'unit_recoil_MV{mv:g}.csv'])
    nunit=float(re.search(r'ROI_5.4_269.9=([\deE.+-]+)',recoil)[1])
    product=math.sqrt(target_n/nunit)
    lo=max(product/MAX_GT,0.008)
    hi=MAX_GC
    if lo>=hi:
        continue
    grid=[lo*(hi/lo)**(i/16) for i in range(17)]
    rows=[evaluate(mv,product,gc) for gc in grid]
    brackets=[(a,b) for a,b in zip(rows,rows[1:]) if (a['Omega']-TARGET_OMEGA)*(b['Omega']-TARGET_OMEGA)<0]
    for a,b in brackets:
        gc_lo,gc_hi=a['gChi'],b['gChi']
        sign=a['Omega']-TARGET_OMEGA
        for _ in range(13):
            gc=math.sqrt(gc_lo*gc_hi)
            r=evaluate(mv,product,gc)
            if sign*(r['Omega']-TARGET_OMEGA)>0:gc_lo=gc
            else:gc_hi=gc
        gc=math.sqrt(gc_lo*gc_hi)
        root=dict(evaluate(mv,product,gc,True))
        par(card,mv,root['gYt'],gc)
        rec=run([ROOT/'lz_recoil',card,OUT/f'root_recoil_MV{mv:g}_gc{gc:.6g}.csv'])
        root['N_ROI_truth']=float(re.search(r'ROI_5.4_269.9=([\deE.+-]+)',rec)[1])
        root['N_SB_truth']=float(re.search(r'SB_350_675=([\deE.+-]+)',rec)[1])
        root['narrow_width_0p3']=int(root['Gamma_over_MV']<0.3)
        roots.append(root)
        print('ROOT',json.dumps(root),flush=True)
    row={'MV':mv,'product':product,'Omega_min_grid':min(x['Omega'] for x in rows),
         'Omega_max_grid':max(x['Omega'] for x in rows),'n_roots':len(brackets)}
    summary.append(row)
    for name,items in [('roots.csv',roots),('mass_summary.csv',summary)]:
        if items:
            with (OUT/name).open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=items[0]);w.writeheader();w.writerows(items)
    print('MASS',json.dumps(row),flush=True)

(OUT/'manifest.json').write_text(json.dumps({'model':'tree-level broken-phase vector Yukawa-like',
    'quark_mass_texture_GeV':{'u':.0022,'d':.0047,'s':.096,'c':1.27,'b':4.18,'t':172},
    'mchi':35,'delta':.001,'fExc':.5,'rho_GeVcm3':.3,'v0_kms':238,'vEarth_kms':254,'vEsc_kms':544,
    'target_Omega':TARGET_OMEGA,'reference_truth_N_ROI':target_n,
    'normalization':'match paper original benchmark rate; no detector response included',
    'mass_grid_GeV':MASSES,'gt_max':MAX_GT,'gchi_max':MAX_GC,
    'loop_matching':False,'full_experimental_constraints':False},indent=2))

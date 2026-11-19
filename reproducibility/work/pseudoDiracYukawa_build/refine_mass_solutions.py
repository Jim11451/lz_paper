import csv,json,math,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
MAX_GT=math.sqrt(4*math.pi)
C=0.03800633448666564/900
all_rows=[]
def point(mv,gc,detail=0,fast=1):
    # finite-propagator correction to this formula is <0.01% at these masses.
    product=C*mv*mv
    gt=product/gc
    p=subprocess.run([str(ROOT/'relic_point'),str(mv),str(gt),str(gc),str(detail),str(fast)],
                     cwd=ROOT,capture_output=True,text=True,timeout=600)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    vals=dict(re.findall(r'(\w+)=([\deE.+-]+)',p.stdout.split('RESULT',1)[1].splitlines()[0]))
    r={k:float(v) for k,v in vals.items()}
    r['Gamma_over_MV']=r['width']/mv
    r['gt_perturbative']=int(gt<MAX_GT)
    r['fast']=fast
    all_rows.append(r)
    if detail:(OUT/f'massroot_MV{mv:.7g}_gc{gc:g}_fast{fast}.log').write_text(p.stdout)
    return r

def solve(gc,lo,hi,label):
    a=point(lo,gc);b=point(hi,gc)
    if (a['Omega']-.12)*(b['Omega']-.12)>0:
        print('NO_BRACKET',gc,label,a,b,flush=True);return None
    for _ in range(20):
        mid=.5*(lo+hi)
        r=point(mid,gc)
        if (a['Omega']-.12)*(r['Omega']-.12)>0:lo=mid;a=r
        else:hi=mid
    r=point((lo+hi)/2,gc,1)
    r['branch']=label
    check=point(r['MV'],gc,1,0)
    r['Omega_fast0']=check['Omega']
    print('MASS_ROOT',json.dumps(r),flush=True)
    return r

roots=[]
for gc in [.06,.08,.1,.2,.3,.5,1,2,3,4,5,6,7]:
    for lo,hi,label in [(60,65,'below_pair_threshold'),(79,90,'above_pair_threshold')]:
        r=solve(gc,lo,hi,label)
        if r:roots.append(r)
    with (OUT/'mass_roots.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=roots[0]);w.writeheader();w.writerows(roots)

for gc in [.25,.3,.5,1,2,4,6,2*MAX_GT]:
    r=solve(gc,5,50,'VV_or_forbidden_VV')
    if r:roots.append(r)
with (OUT/'mass_roots.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=roots[0]);w.writeheader();w.writerows(roots)
print('DONE',len(roots),flush=True)

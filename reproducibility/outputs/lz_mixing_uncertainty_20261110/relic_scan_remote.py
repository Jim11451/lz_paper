"""Workstation-only central and displaced Planck roots with a photon-current EFT."""

import bisect
import json
import math
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue


original = Path(project_path)
master = Path(tempfile.mkdtemp(prefix='YukawaMixingAudit_', dir=original.parent))
for name in ('work', 'lib'):
    shutil.copytree(original/name, master/name, symlinks=True)
shutil.copy2(original/'Makefile', master/'Makefile')
models = master/'work/models'
variables = models/'vars1.mdl'
variables.write_text(variables.read_text().replace('gChi  |', 'dPhot |0.0          |e epsilon_gamma / gYt\ngChi  |', 1))
constraints = models/'func1.mdl'
text = constraints.read_text()
for flavor, ratio in [('u','0.0022/172'),('d','0.0047/172'),('s','0.096/172'),
                      ('c','1.27/172'),('b','4.18/172'),('top','1')]:
    charge = '+2*dPhot/3' if flavor in ('u','c','top') else '-dPhot/3'
    text, count = re.subn(rf'(?m)^(gY{flavor}\s*\|).*$', rf'\g<1>gYt*({ratio}{charge})', text)
    assert count == 1
constraints.write_text(text)
vertices = models/'lgrng1.mdl'
lines = vertices.read_text().splitlines()
index = next(i for i, row in enumerate(lines) if re.match(r'^~x1\s*\|~x2\s*\|V\s*\|',row))
lines[index:index] = [f'{anti:<5}|{lepton:<5}|V    |     |-gYt*dPhot                    |G(m3)'
                      for anti, lepton in [('E','e'),('M','m'),('L','l')]]
vertices.write_text('\n'.join(lines)+'\n')
(master/'mass_relic.c').write_text(c_program.replace('argc != 5','argc != 6').replace(
    '    char name', '    assignValW("dPhot",atof(argv[5]));\n    char name'))
assert 'dPhot' in variables.read_text()
log = master/'audit_build.log'
print('PROJECT '+str(master),flush=True)
with log.open('w') as f:
    for command in (['make','clean'], ['make','main=mass_relic.c']):
        cp = subprocess.run(command, cwd=master, stdout=f, stderr=subprocess.STDOUT, timeout=150)
        if cp.returncode:
            raise RuntimeError(log.read_text()[-5500:])


def execute(directory, m, mv, gt, gc, d=None):
    args = ['./mass_relic',str(m),str(mv),str(gt),str(gc)]
    if d is not None:
        args.append(str(d))
    run = subprocess.run(args, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, timeout=22)
    result = next((s.split() for s in run.stdout.splitlines() if s.startswith('RESULT ')),None)
    if not result or run.returncode or int(result[4]):
        return None
    omega, xf, width = map(float,result[1:4])
    return (omega,xf,width) if math.isfinite(omega) and omega>0 else None


for sample in [(35,87.1833386421,1.06993948302,.3),(35,62.2627568245,.54569366783,.3),
               (25.31,60,.399270925964,.243)]:
    before = execute(original,*sample)
    after = execute(master,*sample,0.)
    assert before and after and all(math.isclose(a,b,rel_tol=1e-7) for a,b in zip(before,after)),(sample,before,after)
    print('VALIDATED '+json.dumps([sample,before,after]),flush=True)
print('VALIDATED '+json.dumps({'strong_mixing_example':execute(master,35,87.1833386421,1.06993948302,.3,.00545169)}),flush=True)

workers = Queue()
workers.put(master)
for i in range(3):
    clone = Path(tempfile.mkdtemp(prefix='YukawaMixingWorker_', dir=original.parent))
    shutil.copytree(master, clone, symlinks=True, dirs_exist_ok=True)
    workers.put(clone)

base = normalizations['mass']
target_omegas = [(k,.12+.0012*k) for k in [-2,-1,0,1,2]]


def coupling_intervals(logs, mv, gt):
    bounds = [math.log(x*gt/mv**2) for x in (.1,1.5)]
    merged = []
    for a,b,fa,fb in zip(base[:-1],base[1:],logs[:-1],logs[1:]):
        if max(fa,fb)<bounds[0] or min(fa,fb)>bounds[1]:
            continue
        if fb != fa:
            ql,qh=sorted((v-fa)/(fb-fa) for v in bounds)
            low,high=a+(b-a)*max(0,ql),a+(b-a)*min(1,qh)
        else:
            low,high=a,b
        if merged and low <= merged[-1][1]+1e-9:
            merged[-1]=(merged[-1][0],high)
        else:
            merged.append((low,high))
    return merged


def bisect_root(a,b,oa,ob,target,callback):
    for iteration in range(25):
        delta = b-a
        frac = (target-oa)/(ob-oa)
        candidate = a+delta*(.5 if iteration%3==2 else min(.9,max(.1,frac)))
        val = callback(candidate)
        if val is None:
            return None
        if abs(val[1]-target)<1e-7:
            return val
        if (oa-target)*(val[1]-target)<0:
            b,ob=candidate,val[1]
        else:
            a,oa=candidate,val[1]
    return val if abs(val[1]-target)<1e-5 else None


def cell(directory, case, anchor):
    name,d,rate,f2=case
    label,mv,gt=anchor
    logs=[x+.5*math.log(rate*.5/f2) for x in normalizations[name]]
    threshold=(mv-.001)/2
    history={}
    def eval_mass(m):
        if m not in history:
            idx=min(len(base)-2,max(0,bisect.bisect_right(base,m)-1))
            frac=(m-base[idx])/(base[idx+1]-base[idx])
            gc=math.exp(logs[idx]+frac*(logs[idx+1]-logs[idx]))*mv**2/gt
            try:
                point=execute(directory,m,mv,gt,gc,d)
            except subprocess.TimeoutExpired:
                point=None
            history[m]=(m,*point,gc) if point else None
        return history[m]

    roots={k:[] for k,_ in target_omegas}
    for low,high in coupling_intervals(logs,mv,gt):
        for side,a,b in [('on',low,min(high,threshold-2e-4)),('off',max(low,threshold+2e-4),high)]:
            if b<a:
                continue
            n=max(1,math.ceil((b-a)/.70))
            knots={a+(b-a)*i/n for i in range(n+1)}
            for center in (threshold,mv,22.):
                for offset in (.0003,.001,.003,.01,.03,.1,.25):
                    knots.update(x for x in (center-offset,center+offset) if a<x<b)
            probes=[eval_mass(m) for m in sorted(knots)]
            for k,target in target_omegas:
                candidates=[r for r in probes if r and abs(r[1]-target)<1e-7]
                for u,v in zip(probes[:-1],probes[1:]):
                    if u is None or v is None or (u[1]-target)*(v[1]-target)>=0:
                        continue
                    r=bisect_root(u[0],v[0],u[1],v[1],target,eval_mass)
                    if r is not None:
                        candidates.append(r)
                for r in sorted(candidates):
                    if not any(old[0]==side and abs(old[1]-r[0])<1e-4 for old in roots[k]):
                        roots[k].append((side,*r))
    return dict(case=name,d=d,rate=rate,f2=f2,point=label,mv_GeV=mv,gt=gt,roots=roots,
                calls=len(history),failed=sum(v is None for v in history.values()))


def run(pair):
    directory=workers.get()
    try:
        return cell(directory,*pair)
    finally:
        workers.put(directory)


with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(run,[(case,point) for case in scenarios for point in points]):
        print('ROOTS '+json.dumps(result),flush=True)

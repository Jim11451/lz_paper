"""Check relic solver precision and a root missed by the coarse brackets."""

import csv
import getpass
import json
import math
from pathlib import Path

import paramiko
from timelike_probe import heavy_shift


HERE = Path(__file__).resolve().parent
master=(HERE/'relic_validation.log').read_text().splitlines()[0].split(' ',1)[1]
code=(HERE.parent/'monojet_mchi_scan_20261106/scripts/mass_relic.c').read_text()
code=code.replace('argc != 5','argc != 8').replace('    char name',
    '    assignValW("dPhot",atof(argv[5]));\n    char name').replace(
    'darkOmega(&xf,0,1e-9,&err)','darkOmega(&xf,atoi(argv[6]),atof(argv[7]),&err)')
with (HERE/'matching_by_mass.csv').open(newline='') as stream:
    matching=[r for r in csv.DictReader(stream) if r['case']=='small_mix_high_rate']
with (HERE.parent/'monojet_mchi_scan_20261106/results/equal/lz_mass_normalization.csv').open(newline='') as stream:
    original=list(csv.DictReader(stream))
knots=[(float(r['mchi_GeV']),math.log(float(r['kappa_equal_rate'])*float(q['kappa_multiplier'])))
       for r,q in zip(original,matching,strict=True)]
mass=range(59700,59860,5)
targets=[]
for m in mass:
    m=m/1000
    a,b=next((a,b) for a,b in zip(knots,knots[1:]) if a[0]<=m<=b[0])
    gc=60**2/2.0036520266739077*math.exp(a[1]+(m-a[0])/(b[0]-a[0])*(b[1]-a[1]))
    targets.append((m,60,2.0036520266739077,gc,-7e-6))
cells=[json.loads(line) for line in (HERE/'relic_roots.jsonl').read_text().splitlines()]
pilot=[]
for label in ('ON_48_0.252','MONO_120_0.43'):
    cell=next(r for r in cells if r['case']=='base' and r['point']==label)
    root=next(root for root in cell['roots']['0'] if root[0]=='on')
    pilot.append((root[1],cell['mv_GeV'],cell['gt'],root[5],cell['d']))
pilot.append((35,87.1833386421,1.06993948302,.3,.00545169))
hard=[]
for label in ('ON_48_0.252','MONO_120_0.43','MONO_150.4_0.1834','MONO_190.4_0.219'):
    cell=next(r for r in cells if r['case']=='base' and r['point']==label)
    root=next(root for root in cell['roots']['0'] if root[0]=='on')
    point=(root[1],cell['mv_GeV'],cell['gt'],root[5])
    hard.extend((kind,(*point,d)) for kind,d in [('hard_base',0.),
                 ('hard_pair_threshold',heavy_shift(2*point[0]+.001).real),
                 ('hard_mediator_pole',heavy_shift(point[1]).real)])
source=(f'master={master!r}\ncode={code!r}\ntargets={targets!r}\npilot={pilot!r}\nhard={hard!r}\n'+r'''
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

source=Path(master)
audit=Path(tempfile.mkdtemp(prefix='YukawaRelicNumerics_',dir=source.parent))
shutil.copytree(source,audit,dirs_exist_ok=True,symlinks=True)
(audit/'mass_precision.c').write_text(code)
cp=subprocess.run(['make','main=mass_precision.c'],cwd=audit,capture_output=True,text=True,timeout=150)
if cp.returncode:
    raise RuntimeError((cp.stdout+cp.stderr)[-5000:])

def evaluation(point,fast,beps):
    args=['./mass_precision',*map(str,point),str(fast),str(beps)]
    run=subprocess.run(args,cwd=audit,check=True,capture_output=True,text=True,timeout=25)
    return tuple(map(float,next(line.split()[1:4] for line in run.stdout.splitlines() if line.startswith('RESULT '))))

def evaluate(point,fast,beps):
    return evaluation(point,fast,beps)[0]

for kind,points in [('pilot',pilot),('local',targets)]:
    for point in points:
        variants=[(0,1e-9),(0,1e-11)]
        if kind=='pilot':
            variants.append((1,1e-9))
        for fast,beps in variants:
            om,xf,width=evaluation(point,fast,beps)
            row=dict(kind=kind,mchi_GeV=point[0],mv_GeV=point[1],gt=point[2],gchi=point[3],
                     d=point[4],fast=fast,beps=beps,omega_h2=om,xf=xf,width_GeV=width)
            print(json.dumps(row),flush=True)

for kind,point in hard:
    om,xf,width=evaluation(point,0,1e-9)
    row=dict(kind=kind,mchi_GeV=point[0],mv_GeV=point[1],gt=point[2],gchi=point[3],
             d=point[4],fast=0,beps=1e-9,omega_h2=om,xf=xf,width_GeV=width)
    print(json.dumps(row),flush=True)

values=[evaluate(p,0,1e-9) for p in targets]
for left,right,olo,ohi in zip(targets,targets[1:],values,values[1:]):
    if (olo-.1212)*(ohi-.1212)>=0:
        continue
    slope=math.log(right[3]/left[3])/(right[0]-left[0])
    lo,hi=left[0],right[0]
    for _ in range(24):
        mid=(lo+hi)/2
        p=(mid,*left[1:3],left[3]*math.exp(slope*(mid-left[0])),left[4])
        om=evaluate(p,0,1e-9)
        if (om-.1212)*(olo-.1212)>0:
            lo=mid
        else:
            hi=mid
    om,xf,width=evaluation(p,0,1e-9)
    print(json.dumps(dict(kind='refine',mchi_GeV=p[0],mv_GeV=p[1],gt=p[2],gchi=p[3],d=p[4],
                          fast=0,beps=1e-9,omega_h2=om,xf=xf,width_GeV=width)),flush=True)
''')
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8',username='cms',password=getpass.getpass('SSH password: '),
                   look_for_keys=False,allow_agent=False,timeout=20)
    stdin,stdout,stderr=client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -',timeout=180)
    stdin.write(source)
    stdin.channel.shutdown_write()
    with (HERE/'relic_numerical_audit.csv').open('w',newline='') as out:
        writer=None
        for line in stdout:
            row=json.loads(line)
            if writer is None:
                writer=csv.DictWriter(out,fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
    diagnostics=stderr.read().decode()
    if stdout.channel.recv_exit_status() or writer is None:
        raise RuntimeError(diagnostics[-7000:])

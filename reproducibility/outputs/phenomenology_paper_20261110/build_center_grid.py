"""Evaluate the central Planck equation on a fresh grid of (M_V, g_t)."""

import csv
import getpass
import math
from pathlib import Path

import numpy as np
import paramiko


HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent/'lz_mixing_uncertainty_20261110'
ORIGINAL=HERE.parent/'monojet_mchi_scan_20261106'


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


original=read(ORIGINAL/'results/equal/lz_mass_normalization.csv')
matching=[r for r in read(AUDIT/'matching_by_mass.csv') if r['case']=='base']
mass=[float(r['mchi_GeV']) for r in original]
assert mass==[float(r['mchi_GeV']) for r in matching]
normalizations={'mass':mass,'base':[math.log(float(r['kappa_equal_rate'])*float(q['kappa_multiplier']))
                                   for r,q in zip(original,matching)]}
points=[(f'm{mi:02d}_g{gi:02d}',float(mv),float(gt))
        for mi,mv in enumerate(sorted(set(range(72,201,4))|{150.4,190.4}))
        for gi,gt in enumerate(np.geomspace(.1,math.sqrt(4*math.pi),29))]
scenarios=[('base',0.,1.,.5)]
master=(AUDIT/'relic_validation.log').read_text().splitlines()[0].split(' ',1)[1]
runner=(AUDIT/'relic_scan_remote.py').read_text(encoding='utf-8')
imports=runner.split('\noriginal =',1)[0]
execute=runner[runner.index('\ndef execute('):runner.index('\nfor sample in ')]
scan=runner[runner.index('\nworkers = Queue()'):]
scan=scan.replace('workers.put(master)\nfor i in range(3):','for i in range(6):')
scan=scan.replace('dir=original.parent','dir=master.parent')
scan=scan.replace('for k in [-2,-1,0,1,2]','for k in [0]').replace('(b-a)/.70','(b-a)/1.10')
scan=scan.replace('max_workers=4','max_workers=6')
source=imports+f'\nmaster=Path({master!r})\nnormalizations={normalizations!r}\npoints={points!r}\nscenarios={scenarios!r}\n'+execute+scan
out=HERE/'data/center_grid_roots.jsonl'
out.parent.mkdir(exist_ok=True)
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8',username='cms',password=getpass.getpass('SSH password: '),
                   look_for_keys=False,allow_agent=False,timeout=20)
    client.get_transport().set_keepalive(15)
    stdin,stdout,stderr=client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -',timeout=900)
    stdin.write(source)
    stdin.channel.shutdown_write()
    count=0
    with out.open('w',encoding='utf-8') as stream:
        for line in stdout:
            if line.startswith('ROOTS '):
                stream.write(line[6:]);stream.flush()
                count+=1
                if count%100==0:
                    print(count,'/',len(points),flush=True)
    diagnostics=stderr.read().decode()
    if stdout.channel.recv_exit_status() or count!=len(points):
        raise RuntimeError(diagnostics[-7000:])
    print('Complete',count,flush=True)

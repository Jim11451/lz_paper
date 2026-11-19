"""Prepare LZ isotope factors and run the Planck-root scan over SSH."""

import csv
import getpass
import json
import math
from pathlib import Path

import numpy as np
import paramiko


here = Path(__file__).resolve().parent
previous = here.parent/'lz_model_checks_20261110'
original = here.parent/'monojet_mchi_scan_20261106'


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


ref = read(previous/'fraction_refit.csv')
points = [[r['benchmark'],float(r['mv_GeV']),float(r['gt'])] for r in ref if r['fraction']=='0.5']
scenarios = [
    ('base',0.,1.,.5), ('dm7e6',-7e-6,1.,.5), ('dp7e6',7e-6,1.,.5),
    ('dm1e5',-1e-5,1.,.5), ('dp1e5',1e-5,1.,.5),
    ('dm5e5',-5e-5,1.,.5), ('dp5e5',5e-5,1.,.5),
    ('near_cancel',-1.49e-4,1.,.5), ('dm_toplog',-.0054516907,1.,.5), ('dp_toplog',.0054516907,1.,.5),
    *[(f'rate{factor:g}',0.,factor,.5) for factor in (.5,.75,.9,1.1,1.25,1.5,2.)],
    ('f045',0.,1.,.45), ('f030',0.,1.,.30),
    ('small_mix_low_rate',7e-6,.75,.5), ('small_mix_high_rate',-7e-6,1.25,.45),
]
norm = read(original/'results/equal/lz_mass_normalization.csv')
mass = [float(row['mchi_GeV']) for row in norm]
ks = np.log([float(row['kappa_equal_rate']) for row in norm])
source = (previous/'physics_checks.py').read_text(encoding='utf-8').split('energy = np.linspace',1)[0]
functions = {'__file__':str(previous/'physics_checks.py')}
exec(compile(source, 'physics_checks.py', 'exec'),functions)
E = np.linspace(5.4,269.9,1501)
q2,_ = functions['recoil_weights'](35,E)
drun = functions['photon_slope'](q2)
q0 = functions['Q0'][:,None]
weights = [functions['recoil_weights'](m,E)[1] for m in mass]
integrals = np.asarray([np.trapezoid(np.sum(w*q0**2,axis=0),E) for w in weights])
all_norms = {'mass':mass}
matching=[]
for name,d,rate,f2 in scenarios:
    q = q0+54*(d+drun)
    # The baseline is the existing low-mixing subtraction including the heavy slope.
    values = np.array([np.trapezoid(np.sum(w*q*q,axis=0),E) for w in weights])/integrals
    all_norms[name]=(ks-.5*np.log(values)).tolist()
    matching.extend(dict(case=name,d=d,rate=rate,f2=f2,mchi_GeV=m,rate_ratio=v,
                         kappa_multiplier=math.sqrt(rate*.5/f2/v)) for m,v in zip(mass,values))
with (here/'matching_by_mass.csv').open('w',newline='',encoding='utf-8') as stream:
    writer=csv.DictWriter(stream,fieldnames=list(matching[0]))
    writer.writeheader()
    writer.writerows(matching)

project='/home/cms/phenomenology/micromegas_7.1.4_el8/PseudoDiracMchiScan_20261106_GQWxsG'
c_program=(original/'scripts/mass_relic.c').read_text(encoding='utf-8')
source = (f'project_path = {project!r}\npoints = {points!r}\nscenarios = {scenarios!r}\n'
          f'normalizations = {all_norms!r}\nc_program = {c_program!r}\n'
          + (here/'relic_scan_remote.py').read_text(encoding='utf-8'))
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8',username='cms',password=getpass.getpass('SSH password: '),
                   look_for_keys=False,allow_agent=False,timeout=20)
    client.get_transport().set_keepalive(15)
    stdin,stdout,stderr=client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -',timeout=480)
    stdin.write(source)
    stdin.channel.shutdown_write()
    count=0
    with (here/'relic_roots.jsonl').open('w',encoding='utf-8') as roots, (here/'relic_validation.log').open('w',encoding='utf-8') as checks:
        for line in stdout:
            if line.startswith('ROOTS '):
                roots.write(line[6:]);roots.flush()
                count+=1
                if count % len(points)==0:
                    print('Completed',count//len(points),'of',len(scenarios),'scenarios',flush=True)
            else:
                checks.write(line);checks.flush()
                print(line.rstrip(),flush=True)
    diagnostics=stderr.read().decode()
    if stdout.channel.recv_exit_status() or count!=len(points)*len(scenarios):
        raise RuntimeError(diagnostics[-7000:])

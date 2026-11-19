"""Finite photon slope and a 13 TeV parton-level tree monojet check."""

import csv
import getpass
import json
import math
from pathlib import Path

import paramiko
from scipy.integrate import quad


HERE = Path(__file__).resolve().parent
ALPHA = 1/137.035999


def heavy_shift(mediator_mass):
    s = mediator_mass**2
    result = 0j
    for mass, charge in ((1.27, 2), (4.18, -1), (172., 2)):
        if s > 4*mass**2:
            low = (1-math.sqrt(1-4*mass**2/s))/2
            high = 1-low
            points = [low, high]
            imag = -math.pi*((high**2-low**2)/2-(high**3-low**3)/3)
        else:
            points, imag = None, 0.
        real = quad(lambda x:x*(1-x)*math.log(abs(1-s*x*(1-x)/mass**2)),
                    0, 1, points=points, epsabs=1e-10)[0]
        result -= (2*ALPHA/math.pi)*(mass/172)*charge*complex(real, imag)
    return result


def run_remote():
    masses = (48.,60.,80.,87.1833386421,100.,120.,150.4,190.4,200.)
    shifts = {m:heavy_shift(m) for m in masses}
    with (HERE/'timelike_shift.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['mv_GeV','real_d','imag_d'])
        writer.writerows((m,d.real,d.imag) for m,d in shifts.items())
    prior = HERE.parent/'truth_xsec_scan_20261106/scripts/run_scan.py'
    source = prior.read_text(encoding='utf-8').split('\ndef main(',1)[0]
    source = '__file__ = "/home/cms/phenomenology/truth_xsec_scan_20261106/scripts/run_scan.py"\n'+source
    jobs = [(m,d) for m in (87.1833386421,120.,150.4,190.4) for d in (0j,shifts[m])]
    source += f'\njobs = {jobs!r}\n'+(HERE/'timelike_probe_remote.py').read_text(encoding='utf-8')
    with paramiko.SSHClient() as client:
        client.load_host_keys('work/fudancms_known_hosts')
        client.connect('100.120.169.8',username='cms',password=getpass.getpass('SSH password: '),
                       look_for_keys=False,allow_agent=False,timeout=20)
        client.get_transport().set_keepalive(15)
        stdin,stdout,stderr=client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -',timeout=600)
        stdin.write(source)
        stdin.channel.shutdown_write()
        rows=[]
        for line in stdout:
            print(line.rstrip(),flush=True)
            if line.startswith('RESULT '):
                rows.append(json.loads(line[7:]))
                with (HERE/'timelike_tree_probe.csv').open('w',newline='') as file:
                    writer=csv.DictWriter(file,fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
        diagnostic=stderr.read().decode()
        if stdout.channel.recv_exit_status() or len(rows)!=len(jobs):
            raise RuntimeError(diagnostic[-8000:])


if __name__=='__main__':
    run_remote()

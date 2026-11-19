"""Re-solve the project LZ rate and relic roots near xenon cancellation."""

import csv
import getpass
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'work/lz_ssh_deps'))
import paramiko

physics = ROOT / 'outputs/lz_model_checks_20261110/physics_checks.py'
source = physics.read_text(encoding='utf-8').split('energy = np.linspace', 1)[0]
source = source.replace('import matplotlib.pyplot as plt', '')
source = source.replace('from scipy.special import erf', 'erf = np.vectorize(math.erf)')
context = {'__file__': str(physics)}
exec(compile(source, str(physics), 'exec'), context)
with (ROOT / 'lz-phenomenology-paper/data/lz_mass_normalization.csv').open() as stream:
    reference = list(csv.DictReader(stream))
mass = [float(row['mchi_GeV']) for row in reference]
log_kappa = np.log([float(row['kappa_equal_rate']) for row in reference])
energies = np.linspace(5.4, 269.9, 1501)
q2, _ = context['recoil_weights'](35, energies)
running = context['photon_slope'](q2)
charge = context['Q0'][:, None]
weights = [context['recoil_weights'](m, energies)[1] for m in mass]
reference_integrals = np.array([
    np.trapezoid(np.sum(w * charge**2, axis=0), energies) for w in weights
])
d_values = [0, -5e-5, -1e-4, -1.2e-4, -1.3e-4, -1.4e-4,
            -1.49e-4, -1.6e-4, -1.8e-4, -2e-4, -2.5e-4, -3e-4]
scenarios = [(f'd_{d:.8g}', d, 1., .5) for d in d_values]
normalizations = {'mass': mass}
matching = []
for name, d, rate, fraction in scenarios:
    new_charge = charge + 54 * (d + running)
    ratio = np.array([
        np.trapezoid(np.sum(w * new_charge**2, axis=0), energies) for w in weights
    ]) / reference_integrals
    normalizations[name] = (log_kappa - .5 * np.log(ratio)).tolist()
    matching.extend(dict(case=name, d=d, mchi_GeV=m, rate_ratio=k,
                         kappa_multiplier=1/math.sqrt(k)) for m, k in zip(mass, ratio))
with (HERE / 'matching.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(matching[0]))
    writer.writeheader()
    writer.writerows(matching)

points = [('M60_g04', 60., .3992709259641317), ('M60_g1', 60., 1.),
          ('M100_g126', 100., 1.2637577710370478), ('M100_g2', 100., 2.)]
previous = ROOT / 'outputs/lz_mixing_uncertainty_20261110/relic_scan_remote.py'
body = previous.read_text(encoding='utf-8')
execute = body.split('def execute(', 1)[1].split('\n\nfor sample', 1)[0]
scan = body.split('base = normalizations', 1)[1]
scan = 'base = normalizations' + scan
scan = scan.replace('target_omegas = [(k,.12+.0012*k) for k in [-2,-1,0,1,2]]',
                    'target_omegas = [(0,.12)]')
scan = scan.replace('ThreadPoolExecutor(max_workers=4)', 'ThreadPoolExecutor(max_workers=2)')
remote = (
    'import bisect,json,math,subprocess,shutil,tempfile\n'
    'from pathlib import Path\nfrom queue import Queue\n'
    'from concurrent.futures import ThreadPoolExecutor\n'
    f'points={points!r}\nscenarios={scenarios!r}\nnormalizations={normalizations!r}\n'
    'master=Path("/home/cms/phenomenology/micromegas_7.1.4_el8/YukawaMixingAudit_yoqoevzd")\n'
    'assert (master/"mass_relic").exists()\n'
    'workers=Queue()\n'
    'for i in range(2):\n'
    ' clone=Path(tempfile.mkdtemp(prefix="XenonCancel20261118_",dir=master.parent))\n'
    ' shutil.copytree(master,clone,symlinks=True,dirs_exist_ok=True)\n'
    ' workers.put(clone)\n'
    ' print("WORKER "+str(clone),flush=True)\n'
    'def execute(' + execute + '\n\n' + scan
)
(HERE / 'remote_scan.py').write_text(remote, encoding='utf-8')
with paramiko.SSHClient() as client:
    client.load_host_keys(str(ROOT / 'work/fudancms_known_hosts'))
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('CMS password: '),
                   look_for_keys=False, allow_agent=False, timeout=30)
    client.get_transport().set_keepalive(15)
    stdin, stdout, stderr = client.exec_command(
        '/home/cms/miniconda3/envs/public/bin/python -u -', timeout=240)
    stdin.write(remote)
    stdin.channel.shutdown_write()
    with (HERE / 'roots.jsonl').open('w', encoding='utf-8') as output:
        for line in stdout:
            if line.startswith('ROOTS '):
                output.write(line[6:])
                output.flush()
                result = json.loads(line[6:])
                print(result['case'], result['point'], result['roots']['0'], flush=True)
            else:
                print(line.rstrip(), flush=True)
    diagnostic = stderr.read().decode()
    if stdout.channel.recv_exit_status():
        raise RuntimeError(diagnostic[-5000:])
    print('COMPLETED', flush=True)

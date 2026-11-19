"""Run the validated full ttbar chi1 chi2 amplitude at three off-shell scan points."""

import csv
import getpass
import json
from pathlib import Path

import paramiko


folder = Path(__file__).resolve().parent
earlier = folder.parent / 'pseudoDirac_yukawaLZ_xsec_20261020' / 'scripts'
driver = (earlier / 'run_lz_points.py').read_text(encoding='utf-8').split('\nwith ThreadPoolExecutor', 1)[0]
utilities = (earlier / 'pilot_utilities.py').read_text(encoding='utf-8')
with (folder / 'branches.csv').open(newline='') as file:
    grid = list(csv.DictReader(file))
points = []
for mass, coupling in [(30, .4), (46, .4), (60, 2.)]:
    row = min((row for row in grid if float(row['mv_GeV']) == mass),
              key=lambda row: abs(float(row['gt']) - coupling))
    assert row['on_count'] == '0' and int(row['off_count']) > 0
    points.append([f'OFF_M{mass}', mass, float(row['gt']), float(row['off_gchi']),
                   float(row['off_mchi_GeV'])])

job = '''
import json
import sys
import tempfile
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

module = types.ModuleType('pilot_utilities')
exec(compile(utilities, 'pilot_utilities.py', 'exec'), module.__dict__)
sys.modules[module.__name__] = module
root = Path(tempfile.mkdtemp(prefix='ttmet_off_shell_', dir='/home/cms/phenomenology'))
print('OUTPUT', root, flush=True)

def run_point(item):
    index, values = item
    label, mv, gt, gchi, mchi = values
    work = root / label
    old_root = '/home/cms/phenomenology/PseudoDiracYukawaLZ_xsec_20261020'
    namespace = {'__name__': 'driver_' + label}
    exec(compile(driver.replace(old_root, str(work)), 'run_lz_points.py', 'exec'), namespace)
    namespace['MCHI'] = mchi
    namespace['CHANNELS']['ttmet']['nevents'] = 12000
    proc = namespace['clone']('ttmet')
    row = namespace['run_one'](proc, 'ttmet', (label, mv, gt, gchi), 13.0, 600 + index)
    return row

with ThreadPoolExecutor(max_workers=3) as workers:
    rows = list(workers.map(run_point, enumerate(points)))
print('RESULT', json.dumps(rows), flush=True)
'''
source = f'utilities = {utilities!r}\ndriver = {driver!r}\npoints = {points!r}\n' + job
destination = folder / 'off_shell_xsec'
destination.mkdir(exist_ok=True)
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('SSH password: '),
                   look_for_keys=False, allow_agent=False, timeout=12)
    client.get_transport().set_keepalive(15)
    stdin, stdout, stderr = client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -', timeout=240)
    stdin.write(source)
    stdin.channel.shutdown_write()
    rows = None
    for line in stdout:
        print(line.rstrip(), flush=True)
        if line.startswith('OUTPUT '):
            remote = line.split()[1]
        if line.startswith('RESULT '):
            rows = json.loads(line.removeprefix('RESULT '))
    diagnostics = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0 or rows is None:
        raise RuntimeError(diagnostics[-5000:])
    with (destination / 'cross_sections.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with client.open_sftp() as sftp:
        for row in rows:
            run = row['run_name']
            evidence = f'{remote}/{row["benchmark"]}/evidence/{run}'
            for name in sftp.listdir(evidence):
                sftp.get(f'{evidence}/{name}', str(destination / f'{row["benchmark"]}_{name}'))

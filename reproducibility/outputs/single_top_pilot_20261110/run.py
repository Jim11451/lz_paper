"""Run 13 TeV single-top pilot points with the existing flavor-vector UFO."""

import csv
import getpass
import json
import sys
from pathlib import Path

import paramiko


folder = Path(__file__).resolve().parent
earlier = folder.parent / 'pseudoDirac_yukawaLZ_xsec_20261020' / 'scripts'
utilities = (earlier / 'pilot_utilities.py').read_text(encoding='utf-8')
driver = (earlier / 'run_lz_points.py').read_text(encoding='utf-8').split('\nwith ThreadPoolExecutor', 1)[0]
with (folder.parent / 'ttmet_branch_map_20261110' / 'branches.csv').open(newline='') as file:
    grid = list(csv.DictReader(file))


def point(mv, gt, side):
    row = min((r for r in grid if float(r['mv_GeV']) == mv), key=lambda r: abs(float(r['gt']) - gt))
    return [f'{side.upper()}_M{mv}', mv, float(row['gt']), float(row[f'{side}_gchi']),
            float(row[f'{side}_mchi_GeV'])]


points = [['ON_M87', 87.1833386421, 1.06993948302, .3, 35.0], point(48, .4, 'on'),
          point(60, 2., 'off'), point(30, .4, 'off')]
tt_check = sys.argv[1:2] == ['tt48']
anchors = sys.argv[1:2] == ['anchors']
resume = sys.argv[2] if len(sys.argv) == 3 and sys.argv[1] in ('resume', 'tt48', 'anchors') else ''
if tt_check:
    points = [points[1]]
if anchors:
    points = [point(64, .8, 'on'), point(76, .9, 'on'), point(100, 1.26, 'on'),
              point(46, .4, 'off'), point(70, 3.18, 'off')]
filename = 'ttbar_M48.csv' if tt_check else 'tj_expected_anchors.csv' if anchors else 'single_top_pilot.csv'
source = f'utilities = {utilities!r}\ndriver = {driver!r}\npoints = {points!r}\ntt_check = {tt_check!r}\nanchors = {anchors!r}\nresume = {resume!r}\n'
source += (folder / 'pilot_remote.py').read_text(encoding='utf-8')
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('SSH password: '),
                   look_for_keys=False, allow_agent=False, timeout=12)
    client.get_transport().set_keepalive(15)
    stdin, stdout, stderr = client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -', timeout=480)
    stdin.write(source)
    stdin.channel.shutdown_write()
    rows = []
    for line in stdout:
        print(line.rstrip(), flush=True)
        if line.startswith('OUTPUT '):
            remote = line.split()[1]
        if line.startswith('RESULT '):
            rows.append(json.loads(line.removeprefix('RESULT ')))
            with (folder / filename).open('w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    diagnostics = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0 or len(rows) != (len(points) if tt_check or anchors else 2 * len(points)):
        raise RuntimeError(diagnostics[-6000:])
    if not anchors:
        with client.open_sftp() as sftp:
            names = ('tt.mg5', 'tt_build.log') if tt_check else ('tj.mg5', 'tW.mg5', 'tj_build.log', 'tW_build.log')
            for name in names:
                sftp.get(f'{remote}/{name}', str(folder / name))

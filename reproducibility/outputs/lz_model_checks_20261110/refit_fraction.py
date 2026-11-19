"""Refit LZ+Planck benchmarks at several late excited-state fractions."""

import csv
import getpass
import json
from pathlib import Path

import paramiko


folder = Path(__file__).resolve().parent
branch_folder = folder.parent / 'ttmet_branch_map_20261110'
mono_file = folder.parent / 'monojet_mchi_scan_20261106/results/gt_mv_observed_heatmap.csv'
with (branch_folder / 'branches.csv').open(newline='') as file:
    branch_rows = list(csv.DictReader(file))
with mono_file.open(newline='') as file:
    mono_rows = [r for r in csv.DictReader(file) if float(r['n_intervals']) > 0]


def pick(mv, gt, side):
    row = min((r for r in branch_rows if float(r['mv_GeV']) == mv and int(r[side+'_count']) > 0),
              key=lambda r: abs(float(r['gt'])-gt))
    return [f'{side.upper()}_{mv}_{gt:g}', mv, float(row['gt']), side, float(row[side+'_mchi_GeV'])]


points = [pick(48, .252, 'on'), pick(48, .399, 'off'), pick(60, .399, 'on'), pick(60, 2., 'off'),
          pick(80, .503, 'on'), pick(100, 1.264, 'on'), pick(30, .399, 'off')]
for mass, target in [(120., .43), (150.4, 1.), (150.4, .1834), (190.4, .219)]:
    row = min((r for r in mono_rows if float(r['mass_GeV']) == mass),
              key=lambda r: abs(float(r['expected_mu95_mc_profiled'])-target))
    points.append([f'MONO_{mass:g}_{target:g}', mass, float(row['gt_LZ']), 'on', float(row['mchi_best_GeV'])])

solver = (branch_folder / 'scan.py').read_text(encoding='utf-8').split("if __name__ == '__main__':",1)[0]
project = '/home/cms/phenomenology/micromegas_7.1.4_el8/PseudoDiracMchiScan_20261106_GQWxsG'
source = f'project = {project!r}\npoints = {points!r}\n' + solver + '''
import json
project = Path(project)
base = read_normalization(project)
for fraction in (.5, .49, .45, .4, .3, .1, .05, .01):
    shift = .5*math.log(.5/fraction)
    norm = [(m, value+shift) for m, value in base]
    for label, mv, gt, side, reference in points:
        found, calls, failures = scan_cell(project, norm, mv, gt, .6)
        best = min(found[side], key=lambda row: abs(row[0]-reference), default=(None,)*5)
        out = dict(benchmark=label, mv_GeV=mv, gt=gt, fraction=fraction, branch=side,
                   on_exists=bool(found['on']), off_exists=bool(found['off']),
                   mchi_GeV=best[0], gchi=best[1], omega_h2=best[2], width_GeV=best[3],
                   gap_GeV=best[4], calls=calls, failures=failures)
        print(json.dumps(out), flush=True)
'''
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('SSH password: '),
                   look_for_keys=False, allow_agent=False, timeout=20)
    client.get_transport().set_keepalive(15)
    stdin, stdout, stderr = client.exec_command(f'cd {project} && python3 -u -', timeout=180)
    stdin.write(source)
    stdin.channel.shutdown_write()
    with (folder / 'fraction_refit.csv').open('w', newline='', encoding='utf-8') as file:
        for index, line in enumerate(stdout):
            row = json.loads(line)
            if index == 0:
                writer = csv.DictWriter(file, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            file.flush()
            if index % len(points) == len(points)-1:
                print('Finished fraction', row['fraction'], flush=True)
    diagnostics = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0 or index+1 != len(points)*8:
        raise RuntimeError(diagnostics[-4500:])

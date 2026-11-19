"""Inspect a small generator-level sample from each shared Delphes ROOT file."""

import getpass
import sys
from pathlib import Path

import paramiko


source = '''
import json
import sys
from pathlib import Path

try:
    import uproot
except ModuleNotFoundError:
    benchmark = Path('/home/cms/phenomenology/monojet_cms_benchmark_20261107')
    candidates = [benchmark / 'deps']
    locations = benchmark / 'awkward_locations.txt'
    if locations.exists():
        candidates.extend(Path(line).parents[1] for line in locations.read_text().splitlines())
    sys.path[:0] = [str(path) for path in candidates]
    import uproot

import awkward as ak
import numpy as np

directory = Path('/home/cms/data')
for path in ([] if compare_only else sorted(directory.glob('signal_*/*.root'))):
    with uproot.open(path) as root:
        tree = root['Delphes']
        a = tree.arrays(['Particle.PID', 'Particle.Status', 'Particle.Mass',
                         'Particle.E', 'Particle.Px', 'Particle.Py', 'Particle.Pz'],
                        entry_stop=100, library='ak', how=dict)
        pid, status = a['Particle.PID'], a['Particle.Status']
        row = {'file': str(path.relative_to(directory)), 'entries': tree.num_entries,
               'sampled': len(pid), 'events_with_top_pair': int(ak.sum(ak.any(pid == 6, axis=1) & ak.any(pid == -6, axis=1)))}
        for name, number in [('chi1', 100051), ('chi2', 100052), ('V', 9900032)]:
            mask = abs(pid) == number
            masses = ak.to_numpy(ak.flatten(a['Particle.Mass'][mask]))
            row[name + '_events'] = int(ak.sum(ak.any(mask, axis=1)))
            if len(masses):
                row[name + '_mass_GeV'] = [float(np.min(masses)), float(np.median(masses)), float(np.max(masses))]
        pair_mask = (status == 1) & ((abs(pid) == 100051) | (abs(pid) == 100052))
        valid = ak.sum(pair_mask, axis=1) == 2
        if ak.any(valid):
            energy, px, py, pz = (ak.sum(a['Particle.' + key][pair_mask], axis=1)[valid]
                                  for key in ['E', 'Px', 'Py', 'Pz'])
            masses = ak.to_numpy(np.sqrt(np.maximum(0, energy**2 - px**2 - py**2 - pz**2)))
            row['stable_chi_pair_mass_GeV'] = [float(np.min(masses)), float(np.median(masses)), float(np.max(masses))]
        row['event_branches'] = [key for key in tree.keys() if key.startswith('Event.') or key.startswith('Weight.')]
        print(json.dumps(row), flush=True)

if compare_only:
    def dark_vectors(path):
        with uproot.open(path) as root:
            tree = root['Delphes']
            components = ['Particle.' + key for key in ['E', 'Px', 'Py', 'Pz']]
            chunks = []
            for a in tree.iterate(['Particle.PID', 'Particle.Status', *components], step_size=250,
                                  library='ak', how=dict):
                masks = [(a['Particle.Status'] == 1) & (abs(a['Particle.PID']) == number)
                         for number in [100051, 100052]]
                assert all(ak.all(ak.sum(mask, axis=1) == 1) for mask in masks)
                chunks.append(np.column_stack([ak.to_numpy(ak.firsts(a[key][mask]))
                                               for mask in masks for key in components]))
            return np.concatenate(chunks)

    paths = [directory / 'signal_mchi35' / f'sig_MV{mass}.root' for mass in (72, 90, 110)]
    baseline = dark_vectors(paths[0])
    for path in paths[1:]:
        other = dark_vectors(path)
        print(json.dumps({'reference': paths[0].name, 'comparison': path.name,
                          'events_compared': len(baseline),
                          'same_dark_four_vectors': int(np.sum(np.all(baseline == other, axis=1))),
                          'max_component_difference_GeV': float(np.max(np.abs(baseline - other)))}), flush=True)
'''
compare_only = sys.argv[1:] == ['compare']
source = f'compare_only = {compare_only!r}\n' + source
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('SSH password: '),
                   look_for_keys=False, allow_agent=False, timeout=12)
    client.get_transport().set_keepalive(15)
    stdin, stdout, stderr = client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -', timeout=120)
    stdin.write(source)
    stdin.channel.shutdown_write()
    lines = []
    for line in stdout:
        print(line.rstrip(), flush=True)
        lines.append(line)
    diagnostics = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0:
        raise RuntimeError(diagnostics[-5000:])
    folder = Path(__file__).resolve().parent / 'off_shell_xsec'
    name = 'group_root_comparison.jsonl' if compare_only else 'group_root_metadata.jsonl'
    (folder / name).write_text(''.join(lines), encoding='utf-8')

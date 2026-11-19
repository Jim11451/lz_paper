"""Read only the generator-level information needed for the expected pilot."""

import csv
import getpass
import sys
from pathlib import Path

import paramiko


folder = Path(__file__).resolve().parent
names = ['single_top_pilot.csv']
if sys.argv[1:] == ['all']:
    names.append('tj_expected_anchors.csv')
samples = []
for name in names:
    with (folder / name).open(newline='') as file:
        samples.extend(r for r in csv.DictReader(file) if r['channel'] == 'tj')
source = f'samples = {samples!r}\n' + (folder / 'tj_expected_templates.py').read_text(encoding='utf-8')
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('SSH password: '),
                   look_for_keys=False, allow_agent=False, timeout=20)
    client.get_transport().set_keepalive(15)
    stdin, stdout, stderr = client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -', timeout=150)
    stdin.write(source)
    stdin.channel.shutdown_write()
    lines = []
    for line in stdout:
        lines.append(line)
    diagnostics = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0 or len(lines) != len(samples):
        raise RuntimeError(diagnostics[-6000:])
    (folder / 'tj_expected_templates.jsonl').write_text(''.join(lines), encoding='utf-8')
    print(f'Computed {len(lines)} signal templates')

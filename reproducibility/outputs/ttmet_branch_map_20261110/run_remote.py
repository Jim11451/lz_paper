"""Run the branch scan on the workstation and save streamed results locally."""

import csv
import getpass
import sys
from pathlib import Path

import paramiko


folder = Path(__file__).resolve().parent
project = '/home/cms/phenomenology/micromegas_7.1.4_el8/PseudoDiracMchiScan_20261106_GQWxsG'
benchmark = sys.argv[1:] == ['benchmark']
source = (folder / 'scan.py').read_text(encoding='utf-8')
destination = folder / ('benchmark.csv' if benchmark else 'branches.csv')
start = 0
if not benchmark and destination.exists():
    with destination.open(encoding='utf-8', newline='') as file:
        start = sum(1 for row in csv.DictReader(file) if row.get('n_failed') is not None)
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8', username='cms', password=getpass.getpass('SSH password: '),
                   look_for_keys=False, allow_agent=False, timeout=12)
    client.get_transport().set_keepalive(15)
    command = f'cd {project} && python3 -u - {project}' + (' benchmark' if benchmark else f' {start}')
    stdin, stdout, stderr = client.exec_command(command, timeout=180)
    stdin.write(source)
    stdin.channel.shutdown_write()
    with destination.open('a' if start else 'w', encoding='utf-8', newline='') as file:
        for i, line in enumerate(stdout):
            if i == 0 and start:
                continue
            file.write(line)
            file.flush()
            if benchmark or (i > 0 and (i + start) % 100 == 0):
                print(line.strip() if benchmark else f'Received {i + start} cells', flush=True)
    diagnostics = stderr.read().decode()
    if stdout.channel.recv_exit_status() != 0:
        raise RuntimeError(diagnostics[-4000:])
    print(destination, flush=True)

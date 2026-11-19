"""Run and collect independent hard-event and shower replicas on the workstation."""

import getpass
import sys
from pathlib import Path

import paramiko


HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'truth_xsec_scan_20261106/scripts/run_scan.py'
REMOTE=HERE/'template_validation_remote.py'
mode=sys.argv[1:]
payload=('mg_source = '+repr(PRIOR.read_text(encoding='utf-8'))+'\nvalidation_mode = '+repr(mode)+'\n'
         +REMOTE.read_text(encoding='utf-8'))
out=HERE/'data/template_validation'
out.mkdir(exist_ok=True)
with paramiko.SSHClient() as client:
    client.load_host_keys('work/fudancms_known_hosts')
    client.connect('100.120.169.8',username='cms',password=getpass.getpass('SSH password: '),
                   look_for_keys=False,allow_agent=False,timeout=20)
    client.get_transport().set_keepalive(15)
    stdin,stdout,stderr=client.exec_command('/home/cms/miniconda3/envs/public/bin/python -u -',timeout=1800)
    stdin.write(payload)
    stdin.channel.shutdown_write()
    with client.open_sftp() as sftp:
        for line in stdout:
            line=line.strip()
            print(line,flush=True)
            if line.startswith('TEMPLATE '):
                remote=line.split()[1]
                sftp.get(remote,str(out/Path(remote).name))
        remote_dir='/home/cms/phenomenology/monojet_three_template_replicas_20261111/templates'
        for name in sftp.listdir(remote_dir):
            if name.endswith('.npz') and not (out/name).exists():
                sftp.get(f'{remote_dir}/{name}',str(out/name))
    diagnostics=stderr.read().decode()
    if stdout.channel.recv_exit_status():
        raise RuntimeError(diagnostics[-7000:])

"""Workstation-side matrix-element generation and truth-level event analysis."""

import gzip
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import types
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


module = types.ModuleType('pilot_utilities')
exec(compile(utilities, 'pilot_utilities.py', 'exec'), module.__dict__)
sys.modules[module.__name__] = module
root = Path(resume) if resume else Path(tempfile.mkdtemp(prefix='single_top_pilot_', dir='/home/cms/phenomenology'))
print('OUTPUT', root, flush=True)
mg = '/home/cms/MG5_aMC_v3_6_6/bin/mg5_aMC'
model = '/home/cms/phenomenology/PseudoDiracFlavorEFT_20261020/PseudoDiracFlavorEFT_UFO-full'
processes = {
    'tj': ['p5 p5 > t j4 chi1 chi2 QCD=0 QED=2 PDB=2',
           'p5 p5 > t~ j4 chi1 chi2 QCD=0 QED=2 PDB=2'],
    'tW': ['p5 p5 > t w- chi1 chi2 QCD=1 QED=1 PDB=2',
           'p5 p5 > t~ w+ chi1 chi2 QCD=1 QED=1 PDB=2'],
}
if globals().get('tt_check', False):
    processes = {'tt': ['p5 p5 > t t~ chi1 chi2 QCD=2 QED=0 PDB=2']}
if globals().get('anchors', False):
    processes = {'tj': processes['tj']}


def build(channel):
    target = root / ('template_' + channel)
    if (target / 'bin/generate_events').is_file():
        return target
    card = root / (channel + '.mg5')
    first, *conjugates = processes[channel]
    config = ['set automatic_html_opening False', 'import model ' + model,
              'define p5 = g u c d s b u~ c~ d~ s~ b~', 'define j4 = u c d s u~ c~ d~ s~',
              'generate ' + first, *('add process ' + process for process in conjugates), f'output {target} -f']
    card.write_text('\n'.join(config) + '\n')
    log = root / (channel + '_build.log')
    print('BUILD', channel, flush=True)
    with log.open('w') as handle:
        subprocess.run([sys.executable, mg, str(card)], cwd=root, stdout=handle,
                       stderr=subprocess.STDOUT, timeout=240, check=True)
    if not (target / 'bin/generate_events').is_file():
        raise RuntimeError(log.read_text()[-4000:])
    return target


def truth_events(path):
    met, parton_energy, spectator_eta = [], [], []
    inside = False
    with gzip.open(path, 'rt') as file:
        for raw in file:
            line = raw.strip()
            if line == '<event>':
                inside = True
                px = py = incoming_e = incoming_pz = 0.0
                eta = math.nan
            elif line == '</event>':
                met.append(math.hypot(px, py))
                parton_energy.append(math.sqrt(max(0, incoming_e**2 - incoming_pz**2)))
                spectator_eta.append(eta)
                inside = False
            elif not inside or not line or line[0] in '<#':
                continue
            else:
                fields = line.split()
                if len(fields) != 13:
                    continue
                pdg, status = map(int, fields[:2])
                if status == -1:
                    incoming_e += float(fields[9])
                    incoming_pz += float(fields[8])
                if status == 1 and abs(pdg) in (100051, 100052):
                    px += float(fields[6])
                    py += float(fields[7])
                if status == 1 and 1 <= abs(pdg) <= 4:
                    eta = math.asinh(float(fields[8]) / math.hypot(float(fields[6]), float(fields[7])))
    return met, parton_energy, spectator_eta


def run(channel, template, index, point):
    label, mv, gt, gc, mchi = point
    process = root / f'{channel}_{label}'
    prior = [process, *sorted(root.glob(f'{process.name}_retry_*'), reverse=True)]
    for candidate in prior:
        if (candidate / 'Events/pilot/unweighted_events.lhe.gz').is_file():
            return summarize(candidate, channel, point, root / f'{channel}_{label}.log')
    if process.exists():
        process = Path(tempfile.mkdtemp(prefix=process.name + '_retry_', dir=root))
    shutil.copytree(template, process, symlinks=True, dirs_exist_ok=True)
    config = process / 'Cards/me5_configuration.txt'
    config.write_text(config.read_text() + '\nrun_mode = 0\nnb_core = 2\nautomatic_html_opening = False\n')
    old_root = '/home/cms/phenomenology/PseudoDiracYukawaLZ_xsec_20261020'
    namespace = {'__name__': 'driver_' + channel + label}
    exec(compile(driver.replace(old_root, str(process)), 'run_lz_points.py', 'exec'), namespace)
    namespace['MCHI'] = mchi
    param_path = process / 'Cards/param_card.dat'
    param = param_path.read_text()
    for code, mass in enumerate(namespace['MASSES'].values(), 1):
        param = module.set_block(param, 'flavcoup', code, gt * mass / 172.)
    for code, value in [(4, 0.), (5, 0.), (100051, mchi), (9900032, mv)]:
        param = module.set_block(param, 'mass', code, value)
    param = module.set_block(param, 'pdbinputs', 2, gc)
    param = module.set_block(param, 'pdbinputs', 3, .001)
    width = namespace['width'](mv, gt, gc)[2]
    param = module.set_decay(param, 9900032, f'{width:.12e}')
    param_path.write_text(module.set_decay(param, 100052, '0.0'))
    card_path = process / 'Cards/run_card.dat'
    card = card_path.read_text()
    settings = dict(nevents=5000, iseed=711000 + index + 30 * (channel == 'tW'),
                    ebeam1=6500, ebeam2=6500, pdlabel='nn23lo1', use_syst='False')
    if channel == 'tj':
        settings.update(ptj=30, etaj=4.0)
    for key, value in settings.items():
        if re.search(rf'^\s*[^!\n]+\s*=\s*{key}\b', card, re.MULTILINE):
            card = module.set_run_value(card, key, value)
        else:
            card += f'\n{value} = {key}\n'
    card_path.write_text(card)
    log = root / f'{channel}_{label}.log'
    print('START', channel, label, flush=True)
    with log.open('w') as handle:
        completed = subprocess.run([str(process / 'bin/generate_events'), 'pilot', '-f'], cwd=process,
                                   stdout=handle, stderr=subprocess.STDOUT, timeout=500)
    if completed.returncode:
        raise RuntimeError(f'{log}\n{log.read_text()[-4000:]}')
    return summarize(process, channel, point, log)


def summarize(process, channel, point, log):
    label, mv, gt, gc, mchi = point
    event_dir = process / 'Events/pilot'
    banner = next(event_dir.glob('*banner.txt'))
    sigma, error = module.cross_section_from_banner(banner)
    if math.isnan(error):
        matches = re.findall(r'Cross-section\s*:\s*[\deE.+-]+\s*\+-\s*([\deE.+-]+)', log.read_text())
        error = float(matches[-1]) if matches else error
    met, shat, eta = truth_events(event_dir / 'unweighted_events.lhe.gz')
    assert len(met) == 5000 and all(x > 0 for x in shat)
    if channel == 'tj':
        assert all(math.isfinite(x) for x in eta)
    row = dict(channel=channel, benchmark=label, mv_GeV=mv, gt=gt, gchi=gc, mchi_GeV=mchi,
               sigma_fb=sigma*1000, integration_error_fb=error*1000, events=len(met))
    for cut in (100, 150, 200, 250, 300, 400, 500):
        row[f'n_MET{cut}'] = sum(x > cut for x in met)
        row[f'sigma_MET{cut}_fb'] = sigma*1000*row[f'n_MET{cut}']/len(met)
    for limit in (750, 1000, 1500):
        row[f'sigma_MET250_shat_lt{limit}_fb'] = sigma*1000*sum(
            x > 250 and e < limit for x, e in zip(met, shat))/len(met)
    row['sigma_MET250_forward_fb'] = sigma*1000*sum(x > 250 and 2.4 < abs(y) < 4.0 for x, y in zip(met, eta))/len(met) if channel == 'tj' else None
    row['banner'] = str(banner)
    return row


templates = {channel: build(channel) for channel in processes}
errors = []
with ThreadPoolExecutor(max_workers=4) as workers:
    tasks = [workers.submit(run, channel, template, i, point)
             for i, point in enumerate(points) for channel, template in templates.items()]
    for task in as_completed(tasks):
        try:
            print('RESULT', json.dumps(task.result()), flush=True)
        except Exception as exc:
            errors.append(str(exc))
if errors:
    raise RuntimeError('\n'.join(errors))

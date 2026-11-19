"""Offline reconstruction of the paper's numerical analysis from archived inputs."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
BUILD = REPO / 'build/reproducibility'


def verify():
    entries = json.loads((HERE/'manifest.json').read_text())
    for item in entries:
        path = HERE/item['path']
        if not path.is_file():
            raise RuntimeError(f'Missing input: {item["path"]}')
        payload=path.read_bytes()
        if item.get('normalization')=='lf':
            payload=payload.replace(b'\r\n',b'\n')
        if hashlib.sha256(payload).hexdigest() != item['sha256']:
            raise RuntimeError(f'Missing or changed input: {item["path"]}')
    print(f'Verified {len(entries)} archived source and input files.')


def likelihood():
    script = HERE/'outputs/lz_mixing_uncertainty_20261110/collider_errors.py'
    context = {'__file__':str(script), '__name__':'reproducible_likelihood'}
    source = script.read_text(encoding='utf-8').split('\nrows=list(propagate())')[0]
    exec(compile(source, str(script), 'exec'), context)
    return context


def benchmarks():
    fit = likelihood()
    with (REPO/'data/benchmark_roots.csv').open(newline='') as stream:
        points = [r for r in csv.DictReader(stream)
                  if r['case']=='base' and r['sigma_omega']=='0' and r['branch']=='on'
                  and r['point'] in ('MONO_120_0.43','MONO_150.4_0.1834','MONO_190.4_0.219')]
    assert len(points)==3
    results=[]
    for row in points:
        mv, gt, br = (float(row[k]) for k in ('mv_GeV','gt','BR_invisible'))
        calculated = fit['mono_limits'](mv, 0.)
        result = dict(mv_GeV=mv, gt=gt,
                      expected_mu95=calculated['experimental'][2]/(gt**2*br),
                      observed_mu95=calculated['observed']/(gt**2*br))
        for field, archived in [('expected_mu95','mono_exp'),('observed_mu95','mono_observed')]:
            if not math.isclose(result[field], float(row[archived]), rel_tol=3e-4):
                raise RuntimeError(f'Benchmark mismatch: {result}, {archived}={row[archived]}')
        results.append(result)
        print(json.dumps(result), flush=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD/'benchmarks.json').write_text(json.dumps(results, indent=2))


def archived_job(name):
    # All regenerated files go into an isolated copy of the archived analysis.
    workspace = BUILD/'workspace'
    if not workspace.exists():
        shutil.copytree(HERE/'outputs', workspace/'outputs')
    if name=='cms-benchmark':
        shutil.copytree(HERE/'tmp',workspace/'tmp',dirs_exist_ok=True)
        subprocess.run([sys.executable,str(workspace/'outputs/monojet_cms_benchmark_20261107/scripts/benchmark_fit.py')],
                       cwd=workspace,check=True)
        return
    if name=='cancellation':
        shutil.copytree(REPO/'data',workspace/'lz-phenomenology-paper/data',dirs_exist_ok=True)
        shutil.copytree(REPO/'ttbar/data',workspace/'lz-phenomenology-paper/ttbar/data',dirs_exist_ok=True)
        subprocess.run([sys.executable,str(workspace/'outputs/ttbar_photon_cancellation_20261118/summarize.py')],
                       cwd=workspace,check=True)
        return
    paper = workspace/'outputs/phenomenology_paper_20261110'
    jobs = {'validation':'fit_template_validation.py',
            'contour':'check_contour_templates.py', 'figures':'prepare_figures.py'}
    if name=='contour' and not (paper/'data/template_validation_pooled.npz').exists():
        raise RuntimeError('Run validation first to construct pooled templates.')
    subprocess.run([sys.executable, str(paper/jobs[name])], cwd=workspace, check=True)
    print(f'Regenerated results: {paper}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['verify','benchmarks','validation','contour','figures','cms-benchmark','cancellation','all'])
    stage=parser.parse_args().stage
    if stage in ('verify','all'):
        verify()
    if stage in ('benchmarks','all'):
        benchmarks()
    for job in ('validation','contour','figures','cms-benchmark','cancellation'):
        if stage in (job,'all'):
            archived_job(job)


if __name__=='__main__':
    main()

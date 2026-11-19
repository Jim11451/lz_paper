"""Workstation-side independent monojet samples at the three paper benchmarks."""

import shutil
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np


base=Path('/home/cms/phenomenology')
previous=base/'monojet_expected_lz_scan_20261106'
root=base/'monojet_three_template_replicas_20261111'
locations=base/'monojet_cms_benchmark_20261107/awkward_locations.txt'
paths=locations.read_text().splitlines() if locations.exists() else []
if not any(Path(p).is_file() for p in paths):
    paths=subprocess.run(['find',str(base),'/tmp','-maxdepth','5','-path','*/awkward/__init__.py'],
                         capture_output=True,text=True).stdout.splitlines()
for path in reversed(paths):
    if Path(path).is_file():
        sys.path.insert(0,str(Path(path).parent.parent))
sys.path.insert(0,str(previous/'scripts'))
import build_templates as detector

for name in ('logs','production','results','detector','templates'):
    (root/name).mkdir(exist_ok=True,parents=True)
compiler=root/'bin/gfortran'
compiler.parent.mkdir(exist_ok=True)
compiler.write_text('#!/bin/sh\nexec /home/cms/miniconda3/envs/public/bin/gfortran -fallow-argument-mismatch "$@" -lstdc++\n')
compiler.chmod(0o755)
os.environ['FC']=str(compiler)
os.environ['PATH']=str(compiler.parent)+':'+os.environ['PATH']
print('WORKSPACE',root,flush=True)
detector.HERE=root


def low_partition(mass,index):
    import inspect

    key=f'loop_m{index}'
    source=root/'production'/key/'Events'/key/'unweighted_events.lhe.gz'
    record=detector.record(root/'results'/f'{key}.csv')
    saved=root/'detector'/key
    pt=detector.uncompress_and_read(source,saved/'partition_source.lhe',mass)
    shuffled=np.random.default_rng(4190+index).permutation(len(pt))
    first=np.zeros(len(pt),dtype=bool)
    first[shuffled[:len(pt)//2]]=True
    original=inspect.getsource(detector.detector_bins)
    original=original.replace('selected &= (hard_pt >= lo) & (hard_pt < hi)',
                              'selected &= (hard_pt >= lo) & (hard_pt < hi) & subset[offset:offset+len(met)]')
    assert original!=inspect.getsource(detector.detector_bins)
    for label,mask,high in [('A',first,230),('B',~first,260)]:
        env={**detector.detector_bins.__globals__,'STITCH':{'loop':(100,high)},'subset':mask}
        exec(compile(original,'partition_selector.py','exec'),env)
        counts,alignment=env['detector_bins'](saved/'events.root',pt,mass,'loop')
        counts[0]-=(~mask).sum()
        assert counts[0]>=0 and counts.sum()==mask.sum()
        path=root/'templates'/f'{mass:g}_{label}_loop0_partition.npz'
        np.savez_compressed(path,counts=counts,mass=mass,cross=float(record['cross_pb']),
                            cross_error=float(record['error_pb']),channel='loop',alignment=alignment,
                            low=100,high=high,inside=int(np.sum(mask&(pt<high))),replica=label,
                            stratum='loop0',hard_seed=620000+10*index,shower_seed=180000+index)
        print(f'TEMPLATE {path}',flush=True)


def run(index,mass,node,replica,stratum,channel,low,high,count):
    label=f'{mass:g}_{replica}_{stratum}'
    destination=root/'templates'/f'{label}.npz'
    if destination.exists():
        return destination
    source=mg_source.replace('nb_core = 3','nb_core = '+('6' if stratum.endswith('_bulk') else '2'))
    mg={'__file__':str(base/'truth_xsec_scan_20261106/scripts/run_scan.py'),'__name__':'validation_driver'}
    exec(compile(source,'run_scan.py','exec'),mg)
    mg['HERE']=root
    mg['SPECS']={channel:(low,4.5,count)}
    edit=mg['change_run']
    def change_run(card,edits):
        if np.isfinite(high) and not stratum.endswith('_bulk') and re.search(r'=\s*ptjmax\b',card):
            edits={**edits,'ptjmax':high}
        return edit(card,edits)
    mg['change_run']=change_run
    key=f'{channel}_m{index:02d}'
    proc=root/'production'/key
    if not proc.exists():
        shutil.copytree(previous/'production'/f'{channel}_m{node:02d}',proc,symlinks=True,
                        ignore=shutil.ignore_patterns('Events','HTML'))
    if channel.startswith('loop'):
        config=proc/'Cards/me5_configuration.txt'
        text=config.read_text()
        if not re.search(r'(?m)^\s*fortran_compiler\s*=\s*'+re.escape(str(compiler))+r'\s*$',text):
            text=re.sub(r'(?m)^\s*fortran_compiler\s*=.*$', '', text)
            config.write_text(text+f'\nfortran_compiler = {compiler}\n')
    print('START',label,count,flush=True)
    record=mg['execute'](index,mass,channel,base/'truth_xsec_scan_20261106/tree_template')
    print('GENERATED',label,record['events'],flush=True)
    event_dir=proc/'Events'/key
    detector_dir=root/'detector'/key
    detector_dir.mkdir(exist_ok=True)
    lhe=detector_dir/'hard.lhe'
    pt=detector.uncompress_and_read(event_dir/'unweighted_events.lhe.gz',lhe,mass)
    assert np.all(pt>=low-0.001) and len(pt)==int(record['events'])
    output=detector.run_detector(detector_dir,key,lhe,mass,len(pt),180000+index)
    # Each task gets a private selector, with the original CMS selection and its own range.
    from types import FunctionType
    select=FunctionType(detector.detector_bins.__code__,{**detector.detector_bins.__globals__,
                        'STITCH':{channel:(low,high)}},detector.detector_bins.__name__)
    counts,alignment=select(output,pt,mass,channel)
    np.savez_compressed(destination,counts=counts,mass=mass,cross=float(record['cross_pb']),
                        cross_error=float(record['error_pb']),channel=channel,alignment=alignment,
                        low=low,high=high,inside=int(np.sum((pt>=low)&(pt<high))),
                        replica=replica,stratum=stratum,hard_seed=620000+10*index,shower_seed=180000+index)
    print('SELECTED',label,int(counts[1:].sum()),flush=True)
    return destination


def archived_120():
    paths=subprocess.run(['find',str(base),'-path','*/detector/loop_m16/events.root'],
                         capture_output=True,text=True).stdout.splitlines()
    for path in map(Path,paths):
        case=path.parents[2]
        record_file=case/'results/loop_m16.csv'
        source=case/'production/loop_m16/Events/loop_m16/unweighted_events.lhe.gz'
        if not record_file.is_file() or not source.is_file():
            continue
        record=detector.record(record_file)
        if float(record['mass_GeV'])!=120 or int(record['events'])!=10800:
            continue
        pt=detector.uncompress_and_read(source,root/'detector/archived_120.lhe',120.)
        detector.STITCH['loop']=(100,230)
        counts,alignment=detector.detector_bins(path,pt,120.,'loop')
        output=root/'templates/120_A_loop0_archive.npz'
        np.savez_compressed(output,counts=counts,mass=120.,cross=float(record['cross_pb']),
                            cross_error=float(record['error_pb']),channel='loop',alignment=alignment,
                            low=100,high=230,inside=int(np.sum(pt<230)),replica='A',stratum='loop0',
                            hard_seed=620160,shower_seed=970160)
        print(f'TEMPLATE {output}',flush=True)
        return
    print('The archived 120 GeV reconstruction was unavailable.',flush=True)


jobs=[]
if validation_mode==['--partition-low']:
    for mass,index in ((120.,203),(150.4,211)):
        low_partition(mass,index)
    sys.exit(0)
if validation_mode==['--independent-low']:
    with ThreadPoolExecutor(max_workers=3) as workers:
        tasks=[workers.submit(archived_120)]
        if not (root/'templates/150.4_A_loop0.npz').exists():
            tasks.append(workers.submit(run,300,150.4,8,'A','loop0_bulk','loop',100,230,4800))
        if not (root/'templates/190.4_B_loop1.npz').exists():
            tasks.append(workers.submit(run,301,190.4,10,'B','loop1_bulk','loop',260,520,3400))
        for task in as_completed(tasks):
            path=task.result()
            if path:
                print(f'TEMPLATE {path}',flush=True)
    sys.exit(0)

for mass,node in ((120.,6),(150.4,8),(190.4,10)):
    for replica,edges in (('A',(100,230,480)),('B',(100,260,520))):
        for i,(lower,upper) in enumerate(zip(edges,(*edges[1:],np.inf))):
            jobs.append((mass,node,replica,f'loop{i}','loop' if i<2 else 'loop_hard',lower,upper,(6600,4000,3200)[i]))
    for i,(lower,upper) in enumerate(((100,350),(350,np.inf))):
        jobs.append((mass,node,'new',f'tree{i}','jet_tree' if i==0 else 'jet_tree_hard',lower,upper,(12000,4500)[i]))

errors=[]
with ThreadPoolExecutor(max_workers=6) as workers:
    future={workers.submit(run,200+i,*job):job for i,job in enumerate(jobs)}
    for task in as_completed(future):
        try:
            print('TEMPLATE',task.result(),flush=True)
        except Exception as exc:
            errors.append((future[task],repr(exc)))
            print('FAILED',errors[-1],flush=True)
if errors:
    raise RuntimeError(errors)

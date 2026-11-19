"""Direct MG5 cross sections for tree-level LZ+relic solutions.

Reuse audited full generated amplitudes in separate process copies. Three
independent channels may run concurrently; no shared parameter cards change.
"""
import csv
import gzip
import json
import math
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pilot_utilities import set_block,set_decay,set_run_value,cross_section_from_banner

BASE=Path('/home/cms/phenomenology/PseudoDiracFlavorEFT_20261020')
ROOT=Path('/home/cms/phenomenology/PseudoDiracYukawaLZ_xsec_20261020')
RESULT=ROOT/'results'
LOG=ROOT/'logs'
RESULT.mkdir(parents=True,exist_ok=True);LOG.mkdir(exist_ok=True)
MCHI=35.;DM=.001
MASSES={'gVu':.0022,'gVd':.0047,'gVs':.096,'gVc':1.27,'gVb':4.18,'gVt':172.}
POINTS=[
    ('LZ_M87_gc0p3',87.1833386421,1.06993948302,.3),
    ('LZ_M86_gc1',86.0484642982,.312679727321,1.),
    ('LZ_M62_gc0p3',62.2627568245,.54569366783,.3),
    ('LZ_M30',30.,.127626842306,.297792641421),
    ('LZ_M87_gc0p1',87.1148047447,3.20477402409,.1),
]
CHANNELS={
    'ttmet':{'source':'proc_ttmet','nevents':3000,'cuts':{}},
    'bbmet':{'source':'proc_bbmet','nevents':2000,'cuts':{'ptb':25.,'etab':2.5,'drbb':.4}},
    'monojet':{'source':'proc_monojet','nevents':3000,'cuts':{'ptj':200.,'etaj':4.5}},
}

def width(mv,gt,gc):
    wq=0.
    for m in MASSES.values():
        if mv<=2*m:continue
        r=(m/mv)**2;g=gt*m/172
        wq+=g*g*mv/(4*math.pi)*(1+2*r)*math.sqrt(1-4*r)
    wi=0.
    if mv>2*MCHI+DM:
        r1=(MCHI/mv)**2;r2=((MCHI+DM)/mv)**2
        lam=1+r1*r1+r2*r2-2*r1-2*r2-2*r1*r2
        form=1-(r1+r2)/2-(r1-r2)**2/2+3*math.sqrt(r1*r2)
        wi=(gc/2)**2*mv/(12*math.pi)*math.sqrt(max(0,lam))*form
    return wq,wi,wq+wi

def clone(channel):
    cfg=CHANNELS[channel];source=BASE/cfg['source'];dest=ROOT/cfg['source']
    if not dest.exists():
        shutil.copytree(source,dest,symlinks=False,
                        ignore=shutil.ignore_patterns('Events','HTML','crossx.html','index.html','madevent.tar.gz'))
        (dest/'Events').mkdir();(dest/'HTML').mkdir()
    # Bound the load on the shared workstation. All settings are private copies.
    path=dest/'Cards/me5_configuration.txt'
    config=path.read_text()
    config+='\nrun_mode = 0\nnb_core = 2\nautomatic_html_opening = False\n'
    path.write_text(config)
    return dest

def met_events(path):
    opener=gzip.open if path.suffix=='.gz' else open
    vals=[];inside=False;header=False;px=py=0
    with opener(path,'rt') as f:
        for raw in f:
            line=raw.strip()
            if line=='<event>':inside=True;header=False;px=py=0;continue
            if line=='</event>':
                vals.append(math.hypot(px,py));inside=False;continue
            if not inside or not line or line.startswith('#'):continue
            if not header:header=True;continue
            fields=line.split()
            if len(fields)<10:continue
            if int(fields[1])==1 and abs(int(fields[0])) in [100051,100052]:
                px+=float(fields[6]);py+=float(fields[7])
    return vals

def run_one(proc,channel,point,energy,index):
    name,mv,gt,gc=point;cfg=CHANNELS[channel]
    runname=f'{name}_{channel}_{energy:g}TeV'.replace('.','p')
    banner_dir=proc/'Events'/runname
    param=(BASE/cfg['source']/'Cards/param_card.dat').read_text()
    run=(BASE/cfg['source']/'Cards/run_card.dat').read_text()
    for code,(key,m) in enumerate(MASSES.items(),1):
        param=set_block(param,'flavcoup',code,gt*m/172)
    param=set_block(param,'pdbinputs',2,gc)
    param=set_block(param,'pdbinputs',3,DM)
    for pdg,value in [(4,0.),(5,0.),(100051,MCHI),(9900032,mv)]:
        param=set_block(param,'mass',pdg,value)
    wq,wi,wt=width(mv,gt,gc)
    param=set_decay(param,100052,'0.0')
    param=set_decay(param,9900032,f'{wt:.12e}')
    settings={'nevents':cfg['nevents'],'iseed':730000+index,
              'ebeam1':energy*500,'ebeam2':energy*500,'use_syst':'False',**cfg['cuts']}
    for key,value in settings.items():run=set_run_value(run,key,value)
    (proc/'Cards/param_card.dat').write_text(param)
    (proc/'Cards/run_card.dat').write_text(run)
    path=LOG/f'{runname}.log'
    print('START',runname,flush=True)
    start=time.monotonic()
    if not list(banner_dir.glob('*_banner.txt')):
        with path.open('w') as f:
            cp=subprocess.run([str(proc/'bin/generate_events'),runname,'-f'],cwd=proc,
                              stdout=f,stderr=subprocess.STDOUT,timeout=5400)
        if cp.returncode:raise RuntimeError(f'{runname}: return {cp.returncode}; see {path}')
    banners=list(banner_dir.glob('*_banner.txt'))
    if not banners:raise RuntimeError(f'{runname}: no banner')
    cross,error=cross_section_from_banner(banners[-1])
    text=path.read_text(errors='replace')
    if math.isnan(error):
        pairs=re.findall(r'Cross-section\s*:\s*([\deE.+-]+)\s*\+-\s*([\deE.+-]+)',text)
        if pairs:error=float(pairs[-1][1])
    lhe=list(banner_dir.glob('*unweighted*.lhe.gz'))+list(banner_dir.glob('*unweighted*.lhe'))
    if not lhe:lhe=list(banner_dir.glob('*.lhe.gz'))+list(banner_dir.glob('*.lhe'))
    mets=met_events(lhe[0]) if lhe else []
    (RESULT/f'{runname}_MET.json').write_text(json.dumps(mets))
    dest=ROOT/'evidence'/runname;dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(banners[-1],dest/banners[-1].name)
    shutil.copy2(proc/'Cards/param_card.dat',dest/'param_card.dat')
    shutil.copy2(proc/'Cards/run_card.dat',dest/'run_card.dat')
    row={'benchmark':name,'channel':channel,'sqrt_s_TeV':energy,'MV_GeV':mv,
         'gt':gt,'gChi':gc,'Mchi_GeV':MCHI,'delta_GeV':DM,
         'sigma_fb':cross*1000,'integration_error_fb':error*1000,
         'width_GeV':wt,'BR_invisible':wi/wt,'N_generated':len(mets),
         'runtime_s':time.monotonic()-start,'run_name':runname}
    for cut in [100,150,200,250,300,400,500]:
        n=sum(x>cut for x in mets)
        row[f'N_MET{cut}']=n
        row[f'sigma_MET{cut}_fb']=cross*1000*n/len(mets) if mets else float('nan')
    print('DONE',json.dumps(row),flush=True)
    return row

def run_channel(channel):
    proc=clone(channel);rows=[]
    # First give the CMS Run-2 energy for the two leading candidates, then
    # keep the 13.6 TeV scan consistent with the previous channel pilot.
    tasks=[]
    if channel=='ttmet':
        tasks.extend((p,13.) for p in POINTS[:2])
    tasks.extend((p,13.6) for p in POINTS)
    for i,(point,energy) in enumerate(tasks):
        row=run_one(proc,channel,point,energy,i+100*list(CHANNELS).index(channel))
        rows.append(row)
        with (RESULT/f'{channel}_cross_sections.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    return rows

with ThreadPoolExecutor(max_workers=3) as pool:
    futures={pool.submit(run_channel,c):c for c in CHANNELS}
    allrows=[]
    for future in as_completed(futures):
        rows=future.result();allrows.extend(rows)
        with (RESULT/'cross_sections.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=allrows[0]);w.writeheader();w.writerows(allrows)
print('COMPLETE',len(allrows),flush=True)

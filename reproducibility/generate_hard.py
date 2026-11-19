"""Generate fresh 13 TeV hard events with the archived Ward-tested UFO."""

import argparse
import importlib.util
import math
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mg5',type=Path,required=True)
    p.add_argument('--channel',choices=['loop','tree','ttbar','ttbar-offshell'],required=True)
    p.add_argument('--mv',type=float,required=True)
    p.add_argument('--gt',type=float,required=True)
    p.add_argument('--gchi',type=float,required=True)
    p.add_argument('--mchi',type=float,required=True)
    p.add_argument('--width',type=float,required=True,help='Total mediator width in GeV from the same parameter point')
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--nevents',type=int,default=10000)
    p.add_argument('--ptj',type=float,default=200.)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if min(a.mv,a.gt,a.gchi,a.mchi,a.width,a.nevents,a.seed)<=0:
        p.error('Positive parameters, event count and seed are required.')
    output=a.out.resolve()
    if output.exists():
        p.error('Choose a fresh output directory.')
    output.parent.mkdir(parents=True,exist_ok=True)
    model=HERE/'outputs/monojet_loop_20261103/model/PseudoDiracFlavorEFT_UFO_loop_R2fix'
    process={'loop':'g g > Vb g PDB=1 QED=0 [noborn=QCD]',
             'tree':'p5 p5 > Vb j5 PDB=1 QCD=1 QED=0',
             'ttbar':'p5 p5 > t t~ Vb PDB=1 QED=0',
             'ttbar-offshell':'p5 p5 > t t~ chi1 chi2 PDB=2 QED=0'}[a.channel]
    commands=output.parent/(output.name+'.mg5')
    commands.write_text(f'import model {model}-full\ndefine p5 = g u c d s b u~ c~ d~ s~ b~\n'
                        f'define j5 = p5\ngenerate {process}\noutput {output}\nquit\n')
    subprocess.run([str(a.mg5.resolve()),str(commands)],cwd=output.parent,check=True)
    script=HERE/'outputs/truth_xsec_scan_20261106/scripts/run_scan.py'
    spec=importlib.util.spec_from_file_location('archived_cards',script)
    cards=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cards)
    param=output/'Cards/param_card.dat'
    text=param.read_text()
    for i,m in enumerate(cards.QUARKS,1):
        text=cards.change_param(text,'flavcoup',i,a.gt*m/172)
    for block,index,value in [('pdbinputs',2,a.gchi),('pdbinputs',3,.001),
                              ('mass',100051,a.mchi),('mass',9900032,a.mv)]:
        text=cards.change_param(text,block,index,value)
    import re
    text,count=re.subn(r'(?im)^DECAY\s+9900032\s+\S+',f'DECAY 9900032 {a.width:.12e}',text)
    assert count==1
    param.write_text(text)
    run=output/'Cards/run_card.dat'
    changes=dict(nevents=a.nevents,iseed=a.seed,ebeam1=6500,ebeam2=6500,
                 use_syst='False',pdlabel="'nn23lo1'")
    if a.channel in ('tree','loop'):
        changes.update(ptj=a.ptj,etaj=4.5)
    run.write_text(cards.change_run(run.read_text(),changes))
    subprocess.run([str(output/'bin/generate_events'),'reproduction','-f'],cwd=output,check=True)
    print('On-shell channels produce V. Multiply by its invisible branching fraction for truth MET rates.')
    print('Shower, invisible decay and reconstruction recipes are in the archived template-generation scripts.')


if __name__=='__main__':
    main()

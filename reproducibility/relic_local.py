"""Search LZ rate-matched relic roots with a locally built micrOMEGAs model."""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True,help='micrOMEGAs project containing mass_relic')
    parser.add_argument('--mv',type=float,required=True)
    parser.add_argument('--gt',type=float,required=True)
    parser.add_argument('--d',type=float,default=0.)
    parser.add_argument('--rate',type=float,default=1.)
    parser.add_argument('--fraction',type=float,default=.5)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.mv<=0 or args.gt<=0 or args.rate<=0 or not 0<args.fraction<=1:
        parser.error('Positive mass, coupling and rate, and 0 < fraction <= 1 are required.')
    if not (args.project/'mass_relic').is_file():
        parser.error('Build the model using build_model.py first.')
    physics=HERE/'outputs/lz_model_checks_20261110/physics_checks.py'
    source=physics.read_text().split('energy = np.linspace',1)[0]
    context={'__file__':str(physics)}
    exec(compile(source,str(physics),'exec'),context)
    reference=HERE/'outputs/monojet_mchi_scan_20261106/results/equal/lz_mass_normalization.csv'
    with reference.open() as stream:
        rows=list(csv.DictReader(stream))
    masses=[float(r['mchi_GeV']) for r in rows]
    energies=np.linspace(5.4,269.9,1501)
    q2,_=context['recoil_weights'](35,energies)
    q0=context['Q0'][:,None]
    charge=q0+54*(args.d+context['photon_slope'](q2))
    logs=[]
    for mass,row in zip(masses,rows):
        _,w=context['recoil_weights'](mass,energies)
        ratio=np.trapezoid(np.sum(w*charge**2,axis=0),energies)/np.trapezoid(np.sum(w*q0**2,axis=0),energies)
        logs.append(math.log(float(row['kappa_equal_rate']))-.5*math.log(ratio))
    runner=HERE/'outputs/lz_mixing_uncertainty_20261110/relic_scan_remote.py'
    text=runner.read_text()
    imports=text.split('\noriginal =',1)[0]
    execute=text[text.index('\ndef execute('):text.index('\nfor sample in ')]
    scan=text[text.index('\nbase = normalizations'):text.index('\ndef run(pair):')]
    namespace={'project_path':str(args.project.resolve()),
               'normalizations':{'mass':masses,'selected':logs}}
    exec(compile(imports+execute+scan,str(runner),'exec'),namespace)
    point=namespace['cell'](args.project.resolve(),('selected',args.d,args.rate,args.fraction),
                            ('local',args.mv,args.gt))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(point,indent=2))
    print(json.dumps(point,indent=2))


if __name__=='__main__':
    main()

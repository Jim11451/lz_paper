"""Create a micrOMEGAs 7.1.4 project from the validated photon-current sources."""

import argparse
from pathlib import Path
import shutil
import subprocess

HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--micromegas',type=Path,required=True)
    p.add_argument('--name',default='LZPhotonReproduction')
    a=p.parse_args()
    base=a.micromegas.resolve()
    if Path(a.name).name!=a.name or a.name in ('.','..'):
        p.error('Use a single new project directory name.')
    project=base/a.name
    if project.exists():
        p.error(f'Project already exists: {project}. Choose a new name.')
    subprocess.run([str(base/'newProject'),a.name],cwd=base,check=True)
    source=HERE/'models/micromegas_photon'
    for path in source.glob('*.mdl'):
        shutil.copy2(path,project/'work/models'/path.name)
    shutil.copy2(source/'mass_relic.c',project/'mass_relic.c')
    subprocess.run(['make','main=mass_relic.c'],cwd=project,check=True)
    print(f'Built {project}/mass_relic')


if __name__=='__main__':
    main()

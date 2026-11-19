import subprocess,time,shutil
from pathlib import Path
ROOT=Path('/home/cms/phenomenology/monojet_loop_20261103')
for _ in range(600):
    if (ROOT/'driver.log').exists() and 'START B' in (ROOT/'driver.log').read_text():break
    time.sleep(2)
else:raise RuntimeError('No benchmark card ready')
card=ROOT/'check_B.dat'
shutil.copy2(ROOT/'ggVg/Cards/param_card.dat',card)
for label,model in [('fixed',str(ROOT/'PseudoDiracFlavorEFT_UFO_loop_R2fix')),('uploaded','/home/cms/PseudoDiracFlavorEFT_UFO_loop')]:
    f=ROOT/f'check_{label}.mg5'
    f.write_text(f'import model {model}-full\ncheck brs {card} g g > Vb g PDB=1 QED=0 [noborn=QCD] --energy=1000 --reduction=1\nquit\n')
    with (ROOT/f'logs/check_{label}.log').open('w') as log:
        p=subprocess.run(['/home/cms/MG5_aMC_v3_6_6/bin/mg5_aMC',str(f)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
    print(label,p.returncode,flush=True)

"""Fresh independent 2->3 ttV amplitude for a narrow-width cross check."""
from pathlib import Path
namespace={'__name__':'lz_driver_definitions'}
source=Path(__file__).with_name('run_lz_points.py').read_text()
exec(compile(source.split('\nwith ThreadPoolExecutor',1)[0],'run_lz_points.py','exec'),namespace)
ROOT=namespace['ROOT'];BASE=namespace['BASE'];subprocess=namespace['subprocess'];json=namespace['json'];csv=namespace['csv']
proc=ROOT/'proc_ttv_nwa'
if not proc.exists():
    command=ROOT/'build_ttv_nwa.mg5'
    command.write_text(f'''import model {BASE}/PseudoDiracFlavorEFT_UFO-full
define p5 = g u c d s b u~ c~ d~ s~ b~
generate p5 p5 > t t~ Vb PDB=1 QCD=2 QED=0
output {proc}
quit
''')
    with (ROOT/'logs/build_ttv_nwa.log').open('w') as f:
        subprocess.run(['/home/cms/MG5_aMC_v3_6_6/bin/mg5_aMC',str(command)],cwd=ROOT,
                       stdout=f,stderr=subprocess.STDOUT,check=True,timeout=600)
config=proc/'Cards/me5_configuration.txt'
config.write_text(config.read_text()+'\nrun_mode = 0\nnb_core = 2\nautomatic_html_opening = False\n')
gamma=proc/'Source/PDF/gammaUPC'
if gamma.exists():
    with (ROOT/'logs/build_ttv_gamma.log').open('w') as f:
        subprocess.run(['make','-j1'],cwd=gamma,stdout=f,stderr=subprocess.STDOUT,check=True)
namespace['CHANNELS']['ttv_nwa']={'source':str(proc),'nevents':3000,'cuts':{}}
point=('LZ_M87_gc0p3',87.1833386421,1.06993948302,.3)
r=namespace['run_one'](proc,'ttv_nwa',point,13.,950)
r['sigma_times_BR_fb']=r['sigma_fb']*r['BR_invisible']
with (ROOT/'results/nwa_crosscheck.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=r);w.writeheader();w.writerow(r)
print('NWA_CHECK',json.dumps(r),flush=True)

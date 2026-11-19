"""An additional LZ+relic point near the largest top-production proxy.

Load definitions only from the main driver, then use a fourth private process
copy. The quark/dark width balance favors a gChi between 0.1 and 0.3.
"""
from pathlib import Path
namespace={'__name__':'lz_driver_definitions'}
source=Path(__file__).with_name('run_lz_points.py').read_text()
exec(compile(source.split('\nwith ThreadPoolExecutor',1)[0],str(Path(__file__).with_name('run_lz_points.py')),'exec'),namespace)
ROOT=namespace['ROOT'];BASE=namespace['BASE'];shutil=namespace['shutil'];csv=namespace['csv']
proc=ROOT/'proc_extra_ttmet'
if not proc.exists():
    shutil.copytree(BASE/'proc_ttmet',proc,symlinks=False,
                    ignore=shutil.ignore_patterns('Events','HTML','crossx.html','index.html','madevent.tar.gz'))
    (proc/'Events').mkdir();(proc/'HTML').mkdir()
config=proc/'Cards/me5_configuration.txt'
config.write_text(config.read_text()+'\nrun_mode = 0\nnb_core = 2\nautomatic_html_opening = False\n')
point=('LZ_M87_gc0p2',87.5299315453,1.61769505789,.2)
rows=[]
for i,energy in enumerate([13.,13.6]):
    rows.append(namespace['run_one'](proc,'ttmet',point,energy,990+i))
    with (ROOT/'results/extra_ttmet_cross_sections.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
print('EXTRA COMPLETE',flush=True)

"""Render saved numerical results without repeating the likelihood search."""
from pathlib import Path
import csv,json
path=Path(__file__).with_name('fit_recoil.py')
source=path.read_text()
ns={'__name__':'render_saved','__file__':str(path)}
exec(compile(source.split('\nfitresults={}')[0],str(path),'exec'),ns)
root=ns['ROOT'];np=ns['np']
ns['fitresults']=json.loads((root/'results/fit_summary.json').read_text())
with (root/'results/shape_profile_scan.csv').open() as f:
    ns['scanrows']=[{k:(v if k=='case' else float(v)) for k,v in r.items()} for r in csv.DictReader(f)]
ns['MG']=np.geomspace(10,1000,91)
ns['DG']=np.linspace(150,1021.9979,121)
lines=[l for l in (root/'sources/science_sample.csv').read_text().splitlines() if l and not l.startswith('#')]
ns['science']=np.array([[float(v) for v in row] for row in csv.reader(lines[1:])])
ns['nearest']=np.argmin(abs(ns['science'][:,0]-540.1))
plots='plt.rcParams.update'+source.split('plt.rcParams.update',1)[1]
plots=plots.split("print('DONE'",1)[0]
exec(compile(plots,str(path),'exec'),ns)
print('Rendered three saved figure pairs.')

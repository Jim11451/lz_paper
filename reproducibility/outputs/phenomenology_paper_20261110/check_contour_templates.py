"""Refit the original physical grid with the independent pooled template nodes."""

import csv
import json
from pathlib import Path

import numpy as np


HERE=Path(__file__).resolve().parent
DATA=HERE/'data'
validation=HERE/'fit_template_validation.py'
functions={'__file__':str(validation),'__name__':'template_contour_check'}
source=validation.read_text(encoding='utf-8').split("with (DATA/'benchmark_roots.csv')",1)[0]
exec(compile(source,str(validation),'exec'),functions)

nodes={m:tuple(functions['add'](functions['old'](m,'loop'),functions['old'](m,'tree')))
       for m in functions['nodes']}
with np.load(DATA/'template_validation_pooled.npz') as new:
    assert list(new['masses'])==[120.,150.4,190.4]
    del nodes[150.]
    nodes.update({m:(s,c) for m,s,c in zip(new['masses'],new['signals'],new['covariances'],strict=True)})
axis=np.array(sorted(nodes))
yields=np.array([nodes[m][0] for m in axis])
covariances=np.array([nodes[m][1] for m in axis])

with (DATA/'center_grid_limits.csv').open(newline='') as f:
    rows=[r for r in csv.DictReader(f) if r['observed_mu95']]
limits={}
output=[]
for row in rows:
    m=float(row['mv_GeV'])
    if m not in limits:
        signal=functions['interpolate']([m],axis,yields)[0]
        cov=functions['interpolate_covariance'](np.array([m]),axis,covariances)[0]
        limits[m]=functions['limit'](signal,cov,1.)
    scale=float(row['gt'])**2*float(row['BR_invisible'])
    output.append({**row,'updated_expected_mu95':limits[m][0]/scale,'updated_observed_mu95':limits[m][1]/scale})
functions['write'](DATA/'template_contour_refit.csv',output)
summary={}
for key in ('expected','observed'):
    original=[float(r[f'{key}_mu95'])<1 for r in output]
    updated=[r[f'updated_{key}_mu95']<1 for r in output]
    summary[key]={'original_count':sum(original),'updated_count':sum(updated),
                  'points_changing_side':sum(a!=b for a,b in zip(original,updated,strict=True)),
                  'original_minimum_mass':min(float(r['mv_GeV']) for r,x in zip(output,original) if x),
                  'updated_minimum_mass':min(float(r['mv_GeV']) for r,x in zip(output,updated) if x)}
(DATA/'template_contour_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2),flush=True)

"""At fixed M_V and g_t, rescale the previous on-shell templates after an f2 refit."""

import csv
import math
from pathlib import Path


folder = Path(__file__).resolve().parent


def read(path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file))


def branching(row):
    mv, mchi, gc, width = [float(row[k]) for k in ('mv_GeV','mchi_GeV','gchi','width_GeV')]
    r1, r2 = (mchi/mv)**2, ((mchi+.001)/mv)**2
    phase = math.sqrt((1-((2*mchi+.001)/mv)**2)*(1-(.001/mv)**2))
    spin = 1-(r1+r2)/2-(r1-r2)**2/2+3*math.sqrt(r1*r2)
    return (gc/2)**2*mv*phase*spin/(12*math.pi*width)


def key(mv, gt):
    return round(float(mv), 6), round(float(gt), 8)


fits = read(folder/'fraction_refit.csv')
baseline = {r['benchmark']:r for r in fits if r['fraction']=='0.5'}
mono = read(folder.parent/'monojet_mchi_scan_20261106/results/gt_mv_observed_heatmap.csv')
single = read(folder.parent/'single_top_pilot_20261110/expected_on_shell_grid.csv')
mono = {key(r['mass_GeV'],r['gt_LZ']):float(r['expected_mu95_mc_profiled']) for r in mono
        if float(r['n_intervals'])>0}
single = {key(r['mv_GeV'],r['gt']):float(r['mu95_1000']) for r in single}
out=[]
for row in fits:
    if row['branch']!='on':
        continue
    channel, prior = ('monojet',mono) if row['benchmark'].startswith('MONO') else ('single_top',single)
    previous = prior[key(row['mv_GeV'],row['gt'])]
    output={k:row[k] for k in ('benchmark','fraction','mv_GeV','gt','mchi_GeV','gchi')}
    output.update(channel=channel,BR_invisible='',mu95_expected_proxy='')
    if row['mchi_GeV']:
        if float(row['gap_GeV'])>=5*float(row['width_GeV']) and float(row['width_GeV'])/float(row['mv_GeV'])<.03:
            br = branching(row)
            output.update(BR_invisible=br,mu95_expected_proxy=previous*branching(baseline[row['benchmark']])/br)
    out.append(output)
with (folder/'fraction_expected_rescaling.csv').open('w', newline='') as file:
    writer=csv.DictWriter(file, fieldnames=list(out[0]))
    writer.writeheader()
    writer.writerows(out)

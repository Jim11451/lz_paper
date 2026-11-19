import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/cross_sections.csv').open() as f:rows=list(csv.DictReader(f))
tree={'B':33.4684014,'C':3.25219801}
table=[]
for r in rows:
    out=dict(r)
    if r['label'] in tree:
        out['tree_fb']=tree[r['label']]
        out['loop_over_tree']=float(r['sigma_monojet_NWA_fb'])/out['tree_fb']
        out['tree_plus_loop_fb']=out['tree_fb']+float(r['sigma_monojet_NWA_fb'])
    table.append(out)
(ROOT/'results/comparison.json').write_text(json.dumps(table,indent=2))
for r in table:print(json.dumps(r))

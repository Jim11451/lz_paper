import csv,json,math,re,subprocess,shutil,time
from pathlib import Path
from pilot_utilities import set_block,set_decay,set_run_value,cross_section_from_banner
ROOT=Path('/home/cms/phenomenology/monojet_loop_20261103')
MODEL=ROOT/'PseudoDiracFlavorEFT_UFO_loop_R2fix'
MG='/home/cms/MG5_aMC_v3_6_6/bin/mg5_aMC'
PROC=ROOT/'ggVg'
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'logs').mkdir(exist_ok=True)
if not PROC.exists():
    cmd=ROOT/'build.mg5'
    cmd.write_text(f'import model {MODEL}-full\ngenerate g g > Vb g PDB=1 QED=0 [noborn=QCD]\noutput {PROC}\nquit\n')
    with (ROOT/'logs/build.log').open('w') as f:
        subprocess.run([MG,str(cmd)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
if not (PROC/'Cards/run_card.dat').exists():raise RuntimeError('Process generation failed')
conf=PROC/'Cards/me5_configuration.txt'
conf.write_text(conf.read_text()+'\nrun_mode = 2\nnb_core = 4\nautomatic_html_opening = False\n')
template=(PROC/'Cards/param_card.dat').read_text()
rtemplate=(PROC/'Cards/run_card.dat').read_text()
def width(mv,gt,gc):
    wq=0
    for m in [.0022,.0047,.096,1.27,4.18,172.]:
        if mv>2*m:
            z=(m/mv)**2;wq+=(gt*m/172)**2*mv/(4*math.pi)*(1+2*z)*math.sqrt(1-4*z)
    r1=(35/mv)**2;r2=(35.001/mv)**2
    wi=(gc/2)**2*mv/(12*math.pi)*math.sqrt(max(0,1+r1*r1+r2*r2-2*r1-2*r2-2*r1*r2))*(1-(r1+r2)/2-(r1-r2)**2/2+3*math.sqrt(r1*r2))
    return wq+wi,wi/(wq+wi)
points=[('B',87.1833386421,1.06993948302,.3,13.6,False),
        ('B_toponly',87.1833386421,1.06993948302,.3,13.6,True),
        ('B_13TeV',87.1833386421,1.06993948302,.3,13.,False),
        ('A',87.5299315453,1.61769505789,.2,13.6,False),
        ('C',86.0484642982,.312679727321,1.,13.6,False)]
rows=[]
for i,(label,mv,gt,gc,energy,toponly) in enumerate(points):
    param=template
    for code,m in enumerate([.0022,.0047,.096,1.27,4.18,172.],1):
        param=set_block(param,'flavcoup',code,gt*m/172 if not toponly or code==6 else 0.)
    for block,code,value in [('pdbinputs',2,gc),('mass',100051,35),('mass',9900032,mv),('pdbinputs',3,.001)]:
        param=set_block(param,block,code,value)
    wt,br=width(mv,gt,gc)
    param=set_decay(param,9900032,str(wt))
    run=rtemplate
    for k,v in {'nevents':1000,'iseed':411000+i,'ebeam1':energy*500,'ebeam2':energy*500,'ptj':200.,'etaj':4.5,'use_syst':'False','pdlabel':'nn23lo1'}.items():
        run=set_run_value(run,k,v)
    (PROC/'Cards/param_card.dat').write_text(param);(PROC/'Cards/run_card.dat').write_text(run)
    print('START',label,flush=True)
    with (ROOT/f'logs/{label}.log').open('w') as f:
        cp=subprocess.run([str(PROC/'bin/generate_events'),label,'-f'],cwd=PROC,stdout=f,stderr=subprocess.STDOUT,timeout=7200)
    if cp.returncode:raise RuntimeError(label+' failed')
    banner=next((PROC/'Events'/label).glob('*_banner.txt'))
    cross,err=cross_section_from_banner(banner)
    log=(ROOT/f'logs/{label}.log').read_text(errors='replace')
    match=re.findall(r'Cross-section\s*:\s*([\deE.+-]+)\s*\+-\s*([\deE.+-]+)',log)
    if match:err=float(match[-1][1])
    row=dict(label=label,MV=mv,gt=gt,gChi=gc,sqrt_s_TeV=energy,top_only=toponly,
             sigma_Vj_fb=cross*1000,error_Vj_fb=err*1000,BR_invisible=br,
             sigma_monojet_NWA_fb=cross*1000*br,error_NWA_fb=err*1000*br)
    rows.append(row)
    evidence=ROOT/'results'/label;evidence.mkdir(exist_ok=True)
    for path in [banner,PROC/'Cards/param_card.dat',PROC/'Cards/run_card.dat']:shutil.copy2(path,evidence/path.name)
    with (ROOT/'results/cross_sections.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=row);w.writeheader();w.writerows(rows)
    print('DONE',json.dumps(row),flush=True)
print('COMPLETE',flush=True)

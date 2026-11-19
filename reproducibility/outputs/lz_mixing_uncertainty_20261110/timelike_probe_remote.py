import json
import tempfile


old = HERE
HERE = Path(tempfile.mkdtemp(prefix='timelike_monojet_audit_',dir='/home/cms/phenomenology'))
(HERE/'logs').mkdir()
template = old/'tree_template'
if not (template/'Cards/run_card.dat').is_file():
    template = make_tree()
print('OUTPUT',HERE,flush=True)


def probe(index, mv, d):
    key=f'point_{index}'
    proc=HERE/key
    shutil.copytree(template,proc,symlinks=True,ignore=shutil.ignore_patterns('Events','HTML'))
    for sub in ('Events','HTML'):
        (proc/sub).mkdir(exist_ok=True)
    cards=proc/'Cards'
    param=(cards/'param_card.dat').read_text()
    for code,(m,q) in enumerate(zip(QUARKS,[2/3,-1/3,-1/3,2/3,-1/3,2/3]),1):
        # For a pure tree channel with one flavor-diagonal V insertion, its
        # cross section depends only on the squared modulus of that coupling.
        param=change_param(param,'flavcoup',code,abs(m/172+q*d))
    param=change_param(param,'mass',9900032,mv)
    (cards/'param_card.dat').write_text(param)
    card=(cards/'run_card.dat').read_text()
    pdf=('pdlabel1','pdlabel2') if re.search(r'=\s*pdlabel1\b',card) else ('pdlabel',)
    settings=dict(nevents=1200,iseed=881020+index,ebeam1=6500,ebeam2=6500,
                  ptj=200,etaj=4.5,use_syst='False',dynamical_scale_choice=-1)
    settings.update(dict.fromkeys(pdf,'nn23lo1'))
    (cards/'run_card.dat').write_text(change_run(card,settings))
    conf=cards/'me5_configuration.txt'
    config=re.sub(r'(?m)^\s*(run_mode|nb_core|automatic_html_opening)\s*=.*$','',conf.read_text())
    conf.write_text(config+'\nrun_mode = 2\nnb_core = 2\nautomatic_html_opening = False\n')
    log=HERE/'logs'/f'{key}.log'
    with log.open('w') as stream:
        run=subprocess.run([str(proc/'bin/generate_events'),key,'-f'],cwd=proc,
                           stdout=stream,stderr=subprocess.STDOUT,timeout=480)
    report=log.read_text(errors='replace')
    if run.returncode:
        raise RuntimeError(f'{log}\n{report[-3500:]}')
    event=proc/'Events'/key
    banner=next(event.glob('*_banner.txt')).read_text()
    xs=float(re.search(r'Integrated weight \(pb\)\s*:\s*([.\dEe+\-]+)',banner)[1])
    error=float(re.findall(r'Cross-section\s*:\s*[.\dEe+\-]+\s*\+\-\s*([.\dEe+\-]+)',report)[-1])
    n, cuts=recoil_counts(event/'unweighted_events.lhe.gz')
    assert n>=1140 and n==cuts[2] and xs>0
    return dict(mv_GeV=mv,real_d=d.real,imag_d=d.imag,tree_xs_pb=xs,integration_error_pb=error,events=n)


with ThreadPoolExecutor(max_workers=4) as workers:
    tasks=[workers.submit(probe,i,mv,d) for i,(mv,d) in enumerate(jobs)]
    for task in as_completed(tasks):
        print('RESULT',json.dumps(task.result()),flush=True)

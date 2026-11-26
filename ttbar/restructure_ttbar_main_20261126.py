"""Rebuild the imported Markdown manuscript around the supplied ttbar results."""
from pathlib import Path
import importlib.util
import json
import re
import shutil

REPO=Path(__file__).resolve().parents[1]
HERE=REPO/'ttbar_paper_update_20261126'
BACKUP=HERE/'before_ttbar_main'


def main():
    BACKUP.mkdir(exist_ok=True)
    for name in ('xenon_monojet_ttbar.md','xenon_monojet_ttbar_改动标记.md','变更说明_中文.md','comparison_manifest.json'):
        if not (BACKUP/name).exists(): shutil.copy2(HERE/name,BACKUP/name)
    old=(BACKUP/'xenon_monojet_ttbar.md').read_text(encoding='utf-8')
    def eq(label):
        return next(m[0] for m in re.finditer(r'\$\$.*?\$\$',old,re.S) if '\\label{'+label+'}' in m[0])
    def fig(label):
        return re.search(r'<figure id="'+re.escape(label)+r'".*?</figure>',old,re.S)[0]
    def part(a,b): return old[old.index(a):old.index(b)]

    title='Xenon recoils and top-pair missing-momentum sensitivity to exothermic pseudo-Dirac dark matter'
    abstract=r'''We study whether top-pair production with missing transverse momentum can probe an exothermic pseudo-Dirac dark matter model motivated by the high-energy xenon recoil candidate reported by LUX-ZEPLIN. A vector mediator couples to quarks in proportion to their masses, linking the light-quark recoil amplitude to tree-level top-associated production. We match a reference truth-level recoil yield and solve for the dark matter mass and coupling that reproduce the central Planck abundance. An all-hadronic CMS-inspired recast with 15 missing-momentum bins gives median expected signal-strength limits below unity at 381 of 470 sampled on-shell points, including all retained points with mediator masses of at least 100 GeV. At low mediator masses, the invisible branching fraction produces a turnover at large top coupling. Template statistics remove the single nominal crossing at 20 GeV, while tested scale variations shift the limits by up to about 30%. These results identify a region of strong expected sensitivity under a simplified post-fit background model. A supplementary monojet analysis and its validation are presented in the appendices.'''
    intro_first=part('In an extended recoil window','# Effective model').split('\n\nThe quark couplings')[0]
    intro=intro_first+r'''

The quark flavor structure connects this recoil interpretation to collider production. In a mass-weighted vector model, the up- and down-quark currents determine the leading coherent nuclear response, while the top coupling can produce a mediator in association with a top-quark pair at tree level. Earlier work studied loop-induced and top-associated production of top-philic vector mediators. Du, Huang, and Xie instead considered endothermic scattering in a gauge-complete leptophobic $U(1)_B$ model with a TeV-scale benchmark whose invisible two-body decay is closed. We focus on lighter mediators with open invisible decays and ask whether the recoil-yield and thermal-abundance conditions leave parameters that can be tested through $t\bar t+\mathrm{MET}$, where MET denotes missing transverse momentum. [@cox2016; @du2026]

We solve the recoil and relic conditions at fixed mediator mass and top coupling and reconstruct the all-hadronic top-pair signal. The main result is its median expected sensitivity in a 15-bin approximation to the CMS category. We examine the turnover with coupling and the dependence on template statistics, the thermal-abundance measurement, and perturbative scales. The monojet analysis uses a separate physical grid and a different public likelihood input; its methods, limits, and validation are collected in Appendix A. The two channels are not statistically combined.
'''
    model=part('We take $m_1=', 'For xenon recoils, we first match')
    model+=r'''
The off-diagonal vector interaction converts the heavier state into the lighter one in nuclear scattering and produces the two states together at colliders. The present local excited fraction is fixed to $f_2=0.5$ and the splitting to $\Delta m=1$ MeV. We use $\rho_\chi=0.3\ \mathrm{GeV\,cm^{-3}}$ and halo speeds $v_0=238$, $v_E=254$, and $v_{\rm esc}=544\ \mathrm{km\,s^{-1}}$.

The primary top-pair scan uses $20\le M_V\le200$ GeV, $0.1\le g_t\le\sqrt{4\pi}$, and $0<g_\chi\le\sqrt{4\pi}$. The dark mass is solved in $8~\mathrm{GeV}\le m_\chi\le\min(47.8~\mathrm{GeV},M_V/2)$. Retained roots satisfy $\Gamma_V/M_V<0.03$ and $M_V-m_1-m_2\ge5\Gamma_V$. These coupling bounds define the scan; the largest couplings require higher-order uncertainty estimates. The supplementary monojet grid has different bounds, specified in Appendix A.

The model is an effective description in the electroweak-broken phase. Additional matching operators or new particles can change the recoil amplitude, the width, or annihilation channels. Charged-current single-top production also depends on electroweak cancellations and is retained only as an exploratory calculation in Appendix C. [@kahlhoefer2016; @deramo2016]
'''
    recoils=part('At zero momentum transfer, the vector current','<figure id="fig:recoil"')
    recoils=recoils.replace('We compute $F_A$ from a two-parameter Fermi density.','For the primary top-pair grid we use a Helm form factor [@engel1991]. The supplementary monojet matching uses a two-parameter Fermi density and retains a finite spacelike photon-mixing term, as specified in Appendix A.')
    recoils+=fig('fig:reference_recoil')+r'''

At fixed dark mass and splitting, the contact-limit yield is proportional to $f_2\kappa^2$, where $\kappa=g_tg_\chi/M_V^2$. We impose

$$
N_{\rm ROI}^{\rm truth}(m_\chi,M_V,g_t,g_\chi)=N_0=1.12044,
\qquad g_\chi=\frac{M_V^2}{g_t}\kappa_{\rm LZ}(m_\chi).
$$

This is a reference-rate matching condition inspired by the LZ candidate. It does not define an LZ confidence region or require that every rate-matched spectrum peak at 248 keV. In particular, the low dark masses retained in part of the grid require a separate spectral assessment before interpreting the candidate energy. The collider upper limits below are conditional on this rate-matched slice and the thermal-abundance assumption. Appendix B discusses photon matching and the present excited fraction.
'''
    thermal=part('We assume a standard thermal history','At fixed $m_\\chi$, Eq.')
    # Replace obsolete numerical appendix references in the retained prose.
    thermal=re.sub(r'\(Appendix\s*\[9\].*?\)\.', '(Appendix B).',thermal,flags=re.S)
    thermal+=r'''
The abundance depends on the coupling product and the mediator width. The quark coannihilation rate contains

$$
\frac{(g_tg_\chi)^2}{(M_V^2-s)^2+M_V^2\Gamma_V^2(g_t,g_\chi)}.
$$

Holding the product fixed therefore does not in general fix the abundance. At each $(M_V,g_t)$ we substitute the recoil-matched $g_\chi(m_\chi)$ and search for $\Omega_\chi h^2=0.1200$ on the on-shell branch using the actual couplings and width. Of 616 trial coordinates, 470 pass the root and width criteria, 51 have no root within the search range, and 95 fail the width requirement. The retained masses span 8.42–46.59 GeV. Missing roots are not assigned a collider limit. Other mass branches, including off-shell solutions, are outside this primary projection and are discussed in Appendix C.

We propagate the Planck measurement by solving again at $\Omega_\chi h^2=0.1176$ and 0.1224. The resulting changes in the top-pair signal are reported with the main results. The endpoint test probes abundance uncertainty at fixed reference recoil yield; it does not profile over that yield or the late-time excited fraction.
'''
    ttbar=part('# CMS top-pair production','# Conclusions')
    ttbar=ttbar.replace('The monojet grid uses the recoil prescription described in [the xenon section](#sec:recoils) and includes the finite spacelike photon-mixing term in the central scan. The grids therefore implement the same reference yield with channel-specific recoil prescriptions.','The supplementary monojet prescription differs in its nuclear form factor and finite photon-mixing term (Appendix A). The two grids implement the same reference yield without defining an identical point-by-point parameter slice.')
    ttbar=ttbar.replace('The off-shell rates and the exploratory single-top estimates are given in [the top-associated appendix](#sec:top).','The off-shell rates and exploratory single-top estimates are given in Appendix C.')
    ttbar=ttbar.replace('CMS extracts its signal using neural-network score bins and combines lepton categories.','The full CMS analysis combines signal and control regions across several lepton categories.')
    # Keep the figure and point information without repeating the grid definition.
    a=ttbar.index('At fixed $(M_V,g_t)$, the recoil integral')
    b=ttbar.index('<figure id="fig:ttbar_grid">')
    ttbar=ttbar[:a]+r'The retained grid is shown in Fig. [the physical-grid projections](#fig:ttbar_grid). The invisible branching fractions range from $1.7\times10^{-5}$ to unity.'+'\n\n'+ttbar[b:]
    split=ttbar.index('## Expected limits and their stability')
    methods=ttbar[:split].replace('# CMS top-pair production with missing transverse momentum {#sec:ttbar_recast}', '# Top-pair signal and statistical method {#sec:ttbar_recast}')
    methods=methods.replace('## Recoil normalization and physical grid','## Physical grid and signal projection')
    results='# Expected sensitivity and stability {#sec:ttbar_results}\n\n'+ttbar[split+len('## Expected limits and their stability'):].strip()
    results=results.replace('The median expected limit falls below unity at 381', '## Sensitive region and coupling dependence\n\nThe median expected limit falls below unity at 381',1)
    results=results.replace('We propagate template statistics at all 132', '## Template, scale, and abundance tests\n\nWe propagate template statistics at all 132',1)
    conclusions=r'''We have identified substantial expected sensitivity to a recoil-rate-matched, thermally produced pseudo-Dirac dark sector in the all-hadronic top-pair channel. The mass-weighted vector coupling links the light-quark nuclear response to tree-level top-associated production. Within the retained on-shell grid, the median expected limit is below the nominal signal strength at 381 of 470 sampled points, including all retained points with $M_V\ge100$ GeV. The high-coupling turnover at light mediator masses follows the competition between production, invisible branching fraction, and acceptance.

The 20 GeV crossing is not stable against template statistics. Perturbative-scale variations of up to about 30% are larger than the reported median effect of the Planck abundance uncertainty. The limits use one all-hadronic category and a simplified model of a published post-fit background projection, so the main inference is expected sensitivity rather than an observed experimental exclusion. A calibrated observed limit requires suitable independent background constraints and a treatment of the relevant shape uncertainties. The supplementary monojet results in Appendix A provide a separate collider test; a joint analysis would require compatible parameter grids and shared uncertainties.
'''
    availability=part('# Data availability','# Xenon recoil and matching checks')
    availability=availability.replace('with the archived version','with the earlier archived version')
    mono=r'''# Appendix A. Supplementary monojet analysis {#sec:monojet_method}

## Grid, production, and reconstructed signal {#sec:monojet_grid}

The supplementary CMS EXO-20-004 recast uses a separate rate-matched grid with $72\le M_V\le200$ GeV, $20\le m_\chi\le100$ GeV, $0.10\le g_\chi\le1.50$, and $0.1\le g_t\le\sqrt{4\pi}$. Its recoil calculation uses a two-parameter Fermi density, $d_\gamma(0)=0$, and the finite spacelike $c,b,t$ photon-mixing contribution. It searches each side of the invisible threshold and assigns an on-shell template only where a unique root meets the narrow-width requirements. The 1015 coordinates yield 434 retained central-abundance on-shell solutions. This is a different slice from the primary top-pair grid.

The hard signal includes tree-level $q\bar q\to gV$ and $qg\to qV$ channels and their charge conjugates, plus the finite heavy-quark-loop channel $gg\to gV$. The three-point pure-vector $gg\to V$ amplitude cancels. We calculate the distinct initial states separately with MadGraph5_aMC@NLO 3.6.6 and `nn23lo1` at 13 TeV and sum their rates. The loop UFO includes the rational $gggV$ term obtained from `loop_sm`, with coefficient $i g_{Vq}g_s^3/(48\pi^2)$ per flavor and color structure $d^{abc}$. Its Ward/BRS test ratio is about $6.3\times10^{-24}$ at the tested 87.18 GeV mediator point and 1 TeV partonic energy. [@alwall2014; @hirschi2015; @cox2016]

On-shell production is normalized as $\sigma_X=\sigma_X^{\rm prod}(g_t=1)g_t^2\mathrm{BR}(V\to\chi_1\chi_2)$. Pythia 8.312 and Delphes 3.5.0 treat the mediator as invisible. Nominal samples start at generator $p_T^j=100$ GeV, with additional tree and loop samples above 350 and 480 GeV, respectively, combined in mutually exclusive intervals. The 120 GeV loop node also uses a 230 GeV boundary. Reconstructed cuts require a leading AK4 jet with $p_T>100$ GeV and $|\eta|<2.4$, $p_T^{\rm miss}>250$ GeV, jet azimuthal cuts, and lepton, photon, and heavy-flavor-related vetoes, including the 2018 HEM treatment. The 2016–2018 data contain 22 bins per year and about $137\ \mathrm{fb}^{-1}$. [@pythia2022; @delphes2014; @cmsmonojet; @albert2021]

## Likelihood and central limits {#sec:monojet_results}

The public control-region background prediction and covariance, observed counts, and simulated signal define

'''+eq('eq:likelihood')+r'''

The signal covariance contains finite-template counting correlations, integration errors, and a common 1.6% luminosity uncertainty, retaining correlations across years that share events. Yields are linearly interpolated in mass and independent covariances combined with squared weights. We profile nonnegative signal yields and positive Poisson means and solve asymptotic $CL_s=0.05$. Expected limits use a background Asimov data set, and observed limits use the measured counts with a conditional background Asimov construction. [@cmscovariance; @cmsyields; @cmssimplified; @cowan2011; @read2002]

Reference templates give 208 expected and 151 observed sampled points with $\mu_{95}<1$; the lowest sampled mediator masses are 92 and 104 GeV. The smallest observed reference-template limit is 0.181 at $(M_V,g_t)=(200\,\mathrm{GeV},\sqrt{4\pi})$. The following three reference benchmarks remain below unity under the prescribed yield variations.

| $M_V$ [GeV] | $g_t$ | Expected $\mu_{95}$ | Observed $\mu_{95}$ | Observed, $r=0.75$–$1.25$ |
|---:|---:|---:|---:|---:|
| 120 | 3.073 | 0.412 | 0.607 | 0.570–0.664 |
| 150.4 | 3.545 | 0.184 | 0.340 | 0.329–0.357 |
| 190.4 | 3.545 | 0.219 | 0.273 | 0.270–0.277 |

'''+fig('fig:exclusion')+r'''

At the representative points tested, changing the Planck target by $\pm2\sigma$ changes the median expected limit by at most 0.44%. The yield test $r=0.75$–1.25 changes it by at most 9.4%; reducing $f_2$ to 0.45 or 0.30 changes it by up to 3.0% or 12.8%. The tested $|d_\gamma(0)|\le7\times10^{-6}$ variation changes it by at most 2.8%. These are monojet checks on its own grid, not uncertainty estimates for the primary top-pair map. At $r=2$, the three benchmark observed limits remain below unity at 0.507, 0.310, and 0.265. A lower-coupling 150.4 GeV point remains above unity, and some low-abundance roots disappear at the dark-coupling scan boundary.

## Official benchmark and template validation {#sec:validation}

Using official CMS vector templates, the reconstructed expected and observed mediator mass boundaries are 2.208 and 1.941 TeV, compared with official values of 2.198 and 1.957 TeV. Individual observed limits disagree more at low mass. This checks the statistical reconstruction using official templates. [@cmsmonojet; @cmssignal]

'''+fig('fig:cms_official')+r'''

Independent LO plus Delphes simulation gives 62.9% of the official 2017 100 GeV vector signal yield. The independent and official samples differ in generation and reconstruction settings. The discrepancy limits validation of absolute acceptance, including heavy-flavor-related selections, and remains relevant to the inferred exclusion boundary.

'''+fig('fig:cms_100')+r'''

Independent loop replicas and stratified tail samples test three sensitive nodes. The templates agree within about 1.7 Monte Carlo standard deviations in the key bins and combined high-MET intervals. Across the tested templates and yield targets, all three exclusion decisions persist, with a largest observed limit of 0.680. However, pooled-template limits at 150.4 and 190.4 GeV are about 31% and 27% below the reference values, respectively. Replacing the relevant mass templates changes the full-grid counts to 199 expected and 162 observed sampled points below unity, while the lowest sampled masses remain 92 and 104 GeV. Finite-template and acceptance effects therefore remain material to numerical contours.

'''+fig('fig:independent_samples')+'\n'
    matching=r'''# Appendix B. Recoil matching and late-state assumptions {#sec:matching}

## Photon matching {#sec:low_energy}

Photon kinetic mixing adds an electromagnetic-current coupling. We define $d_\gamma=e\epsilon_\gamma/g_t$; its zero-momentum value is an independent matching input. Relative to zero momentum, the retained heavy-quark term is

'''+eq('eq:finite_mixing')+r'''

With a common Helm form factor, the nuclear charge shifts by $g_tZ[d_\gamma(0)+\delta d_{cbt}(-q^2)]$. For $^{131}$Xe, $Q_A/g_t\simeq8.05\times10^{-3}$, so cancellation occurs near $d_\gamma(0)=-1.49\times10^{-4}$. At 35 GeV and zero matching input, the retained finite spacelike term reduces the integrated rate by about 0.077%. Varying the matching input to $\mp7\times10^{-6}$ changes the fixed-coupling rate to 0.908 or 1.095 times the tree result, requiring $\kappa/\kappa_0=1.050$ or 0.956. Near cancellation this ratio reaches about 56.5. These matching checks motivate stating the prescription separately for the two collider grids. [@deramo2016; @forner2026]

'''+fig('fig:mixing')+r'''

## Present excited fraction

The main scan fixes $f_2=0.5$. After freeze-out, conversion is modeled by

$$
\dot f_2=-n_\chi\langle\sigma v\rangle_{22\to11}
[f_2^2-e^{-2\Delta m/T_\chi}(1-f_2)^2].
$$

Born contact-scattering estimates with varied kinetic-decoupling assumptions give a minimum near 0.45 at the tested on-shell benchmarks and about 0.30 at some off-shell benchmarks, assuming additional decay is suppressed. The 1 MeV splitting closes the electron-pair decay channel; independent $V$–$Z$ mixing or a transition dipole can alter the excited-state lifetime. These calculations define thermal-history benchmarks, not a determination of $f_2$ across the full top-pair grid. The top-pair abundance-endpoint tests keep $f_2$ fixed. [@gemmell2026; @carrillo2022]

'''+fig('fig:fraction')+'\n'
    other=r'''# Appendix C. Off-shell and single-top checks {#sec:top}

At the same $(M_V,g_t)$, the yield and abundance equations can admit more than one dark mass. In a low-mass scan, $(M_V,g_t)=(48\,\mathrm{GeV},0.252)$ has central-abundance roots at 20.445, 25.260, and 45.878 GeV; the lightest is on shell. The primary top-pair map retains only its defined on-shell branch. Below the invisible threshold, production must be calculated with the full four-body amplitude rather than an on-shell rate times a branching fraction.

At three off-shell benchmarks with mediator masses 30, 46, and 60 GeV, full matrix elements with truth $p_T^{\rm miss}>250$ GeV give top-pair cross sections of 0.033, 0.041, and 1.13 fb. These truth-level rates do not define an off-shell exclusion; top decays, reconstruction, and an appropriate likelihood would be needed. [@cmstop]

'''+fig('fig:low_mass')+r'''

The exploratory single-top calculation uses the 15-bin CMS AH $1b\,1\mathrm{FJ}$ projection with diagonal background uncertainties, truth cuts, simplified top decays, and approximate $b$ tagging. At $(M_V,g_t)=(60\,\mathrm{GeV},0.399)$, partonic-energy cuts $\sqrt{\hat s}<1.5,1.0,0.75$ TeV give median expected limits of 0.052, 0.337, and 3.43. This strong variation reflects the sensitivity of longitudinal charged-current amplitudes to electroweak cancellations with unequal top and bottom vector couplings. It limits the result to an exploratory estimate and is not used in the primary sensitivity map. [@kahlhoefer2016; @cmstop; @cmsahdata]

'''+fig('fig:single_top_cut')+'\n'

    sections=[('# Introduction {#sec:introduction}',intro),('# Effective model {#sec:model}',model),
              ('# Xenon recoils and the reference yield {#sec:recoils}',recoils),
              ('# Thermal abundance and the on-shell projection {#sec:abundance}',thermal)]
    doc='---\ntitle: "'+title+'"\nbibliography: references.bib\nabstract: |\n  '+abstract+'\n---\n\n'
    doc+='\n\n'.join(h+'\n\n'+v.strip() for h,v in sections)+'\n\n'+methods.strip()+'\n\n'+results+'\n\n# Conclusions {#sec:conclusions}\n\n'+conclusions+'\n'+availability+'\n'+mono+'\n'+matching+'\n'+other
    # Replace stale numeric Pandoc references with stable named links.
    doc=re.sub(r'(?:Section|Appendix|Fig\.|Table|Eq\.)[\s\u00a0]*\[([^\]]*(?:\\\][^\]]*)?)\]\(#([^)]*)\)\{[^}]*\}',
               lambda m:'[the relevant '+('appendix' if m[2].startswith('sec:') else 'figure' if m[2].startswith('fig:') else 'equation')+'](#'+m[2]+')',doc,flags=re.S)
    # Remove residual HTML/Pandoc numeric link attributes in imported captions.
    doc=re.sub(r'\{reference-type=[^}]*\}','',doc,flags=re.S)
    (HERE/'xenon_monojet_ttbar.md').write_text(doc,encoding='utf-8')

    spec=importlib.util.spec_from_file_location('importer',REPO/'ttbar/import_manuscript_20261126.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    readable='# '+title+'\n\n## Abstract\n\n'+abstract+'\n\n'+doc.split('---',2)[2].strip()
    readable=mod.reading_format(readable)
    # A clean reading copy and a structure-marked copy share the same prose.
    (HERE/'xenon_monojet_ttbar_阅读版.md').write_text(readable+'\n',encoding='utf-8')
    blocks=re.split(r'\n\s*\n',readable)
    marked=[]
    for block in blocks:
        if block.startswith('## ') and not block.startswith('###'):
            action='移至附录并压缩' if 'Appendix' in block else '正文主线重构'
            marked.append(f'> [!info] {action}\n> 本轮以顶对预期灵敏度为主结果；具体迁移见 [[结构调整说明_中文]]。')
        marked.append(block)
    (HERE/'xenon_monojet_ttbar_改动标记.md').write_text('\n\n'.join(marked)+'\n',encoding='utf-8')
    def words(s):return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*",s))
    audit={'before_total_words':words(old),'after_total_words':words(doc),
           'before_monojet_methods_results_words':words(part('# LHC production','# Discussion of top-associated')),
           'after_monojet_appendix_words':words(mono),
           'before_monojet_validation_words':words(part('# Validation of the CMS monojet recast','# Top-associated channels')),
           'source_backup':'before_ttbar_main',
           'primary_statistic':'381 of 470 retained on-shell points have median expected mu95 < 1',
           'no_new_simulations':True}
    (HERE/'restructure_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()

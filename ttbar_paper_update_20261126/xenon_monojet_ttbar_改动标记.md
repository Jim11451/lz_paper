# Xenon recoils and CMS monojet and top-pair constraints on exothermic pseudo-Dirac dark matter

> [!info] 改动标记说明
> 黄色高亮及“新增／改写”旁注标出正文变化。新增的顶对正文整节标记；公式、表格和图片使用旁注。换行、交叉引用转换及章节顺延不计为科研新增。详见 [[变更说明_中文]]。

> [!info] 改写 C01 标题
> 标题新增 top-pair，将顶对通道纳入文章主题。

## Abstract

> [!info] 改写 C02 摘要
> 增加 470 点中 381 点达到名义预期灵敏度，以及简化背景模型的适用范围；原摘要末尾关于三个单喷注代表点的稳健性句子在此处删去。

==We investigate whether CMS searches for jets and missing transverse momentum can test an exothermic pseudo-Dirac dark matter model motivated by the high-energy xenon recoil candidate reported by LUX-ZEPLIN. In the ==electroweak-broken==🟡 effective model, a vector mediator couples to quarks in proportion to their masses. Light quarks set the leading coherent xenon response, while heavy-quark couplings drive collider production. We match a reference truth-level yield in the LUX-ZEPLIN recoil window and solve for the dark matter mass and coupling that reproduce the central Planck abundance. ==In the 66-bin CMS Run 2 monojet recast, the observed 95% confidence-level limits exclude a subset of the on-shell solutions that satisfy the narrow-width criteria. ==🟡In a separate all-hadronic top-pair recast using 15 bins of the published missing-transverse-momentum projection, the median expected limit falls below the nominal signal strength at 381 of 470 sampled on-shell points. The top-pair result estimates expected sensitivity under a simplified background model.==

<a id="sec:introduction"></a>

## Introduction

In an extended recoil window with an exposure of $2.84$ tonne yr, the
LUX-ZEPLIN (LZ) Collaboration reported a candidate consistent with a
nuclear recoil energy of $E_R=248\pm23_{\rm stat}\pm23_{\rm syst}$ keV.
Across the models tested by LZ, the excess over the background-only
hypothesis had a global significance of $2.6\sigma$ and a maximum local
significance of $3.4\sigma$. In exothermic scattering, the heavier dark
state releases energy as it transitions to the lighter state. Dark
matter with a mass of tens of GeV can therefore produce energetic
nuclear recoils. Gemmell, Hooper, and Krnjaic studied this mechanism and
the Galactic Center gamma-ray excess using a flavor-universal quark
vector current. We use their exothermic benchmark to set a reference
yield for our study of xenon recoils, thermal freeze-out, and LHC
signatures. [lz2026](#ref-lz2026) · [gemmell2026](#ref-gemmell2026)

The quark couplings determine how the mediator is produced, and the
invisible decay threshold determines whether it can produce a dark pair
on shell. Du, Huang, and Xie studied endothermic scattering in a
gauge-complete leptophobic $U(1)_B$ model. At their $1.44$ TeV
benchmark, the two-body invisible decay is kinematically closed and
dijet searches provide the main collider test. Earlier work also
examined loop-induced and top-associated production of top-philic vector
mediators. Here we ask whether missing-momentum searches can probe
mediators with masses from tens to about two hundred GeV once we impose
the exothermic recoil yield and the thermal abundance. At each
$(M_V,g_t)$, we solve for $(m_\chi,g_\chi)$ that reproduce the reference
recoil yield and thermal abundance. We then apply the monojet search to
solutions that meet the on-shell narrow-width criteria. Off-shell
solutions can also occur at lower mediator masses. [du2026](#ref-du2026) · [cox2016](#ref-cox2016)

> [!tip] 新增 A01
> 相对本地 PRD 旧稿。

==We also estimate the expected sensitivity of the CMS all-hadronic top-pair category on a separate on-shell grid. The monojet and top-pair analyses probe different production mechanisms and use different public likelihood inputs.==

<a id="sec:model"></a>

## Effective model

We take $m_1=m_\chi$ and $m_2=m_\chi+\Delta m$. A spin-1 mediator
$V_\mu$ couples to the off-diagonal vector current of the two dark
states. The benchmark interaction in the electroweak-broken basis is

$$

\mathcal L_{\rm int}=V_\mu\left[\sum_q g_{Vq}\bar q\gamma^\mu q
+i\frac{g_\chi}{2}\bar\chi_1\gamma^\mu\chi_2\right].
$$

Here $g_{Vq}=g_t\widehat m_q/(172\,\mathrm{GeV})$. In the order
$(u,d,s,c,b,t)$, the reference masses $\widehat m_q$ are
$(0.0022,0.0047,0.096,1.27,4.18,172)$ GeV.

At zero mixing, $g_t$ is the coefficient of the $Vt\bar t$ vertex, and
the dark transition coupling has magnitude $g_\chi/2$. We adopt
$g_{Vq}\propto\widehat m_q$ in an effective model for the electroweak
broken phase. The reference masses $\widehat m_q$ fix the ratios of
quark couplings. A complete $U(1)_X$ theory would also specify the
charges, the mechanism of fermion mass generation, and the matching
conditions. For purely vector couplings, different coefficients for the
up- and down-type members of a left-handed weak doublet require
electroweak-breaking operators or additional mixing.
[kahlhoefer2016](#ref-kahlhoefer2016) · [deramo2016](#ref-deramo2016)

For xenon recoils, we first match the quark couplings in
Eq. [\[eq:interaction\]](#eq:interaction) to effective proton and neutron couplings.
Section [3](#sec:recoils)
gives the tree-level matching. Photon mixing also requires a
zero-momentum input $d_\gamma(0)$. We set $d_\gamma(0)=0$ in the main
scan (Section [6.2](#sec:low_energy)).

For collider production, the closed-quark-loop amplitude for $gg\to gV$
passes the numerical QCD Ward test described in
Appendix [10](#sec:production_checks). The relic-density and monojet
predictions depend on the operators, particles, and kinematically open
channels of the effective model. Additional $V$--$Z$ mixing, matching
operators, or new particles could change the recoil amplitude,
annihilation rates, mediator width, or production rates. Charged-current
processes also depend on electroweak cancellations in the longitudinal
amplitudes, as the single-top study in
Appendix [12](#sec:top)
illustrates. [kahlhoefer2016](#ref-kahlhoefer2016) · [deramo2016](#ref-deramo2016)

| Quantity | Benchmark or range |
| --- | --- |
| Mass splitting and present local excited fraction | $\Delta m=1$ MeV, $f_2=0.5$ |
| Local dark matter density | $\rho_\chi=0.3\ \mathrm{GeV\,cm^{-3}}$ |
| Halo speeds $(v_0,v_E,v_{\rm esc})$ | $(238,254,544)\ \mathrm{km\,s^{-1}}$ |
| Dark mass and dark coupling | $20\le m_\chi\le100$ GeV, $0.10\le g_\chi\le1.50$ |
| CMS monojet grid | $72\le M_V\le200$ GeV, $0.1\le g_t\le\sqrt{4\pi}$ |
| On-shell template requirements | $M_V-m_1-m_2\ge5\Gamma_V$, $\Gamma_V/M_V<0.03$ |

We set the upper scan boundary at $g_t=\sqrt{4\pi}$, where
$g_t^2/(4\pi)=1$. An assessment of higher-order corrections is needed
near that boundary. For top-associated production, we scan the relic
branches separately over $M_V=20$--100 GeV.

<a id="sec:recoils"></a>

## Xenon recoils and the LZ yield condition

At zero momentum transfer, the vector current measures the net number of
quarks of each flavor in a nucleon. A proton contains two net up quarks
and one net down quark, and a neutron contains one net up quark and two
net down quarks. The tree-level couplings are therefore
$f_p=2g_{Vu}+g_{Vd}$ and $f_n=g_{Vu}+2g_{Vd}$.
Eq. [\[eq:interaction\]](#eq:interaction) gives $f_p/g_t=5.29\times10^{-5}$ and
$f_n/g_t=6.74\times10^{-5}$. For a nucleus with $Z$ protons and $A-Z$
neutrons, the nucleon amplitudes add coherently to give the effective
vector charge $Q_A=Zf_p+(A-Z)f_n$.

Let $m_A$ be the nuclear mass and $\mu_A=m_2m_A/(m_2+m_A)$ the reduced
mass of the incident dark state and the nucleus. Energy and momentum
conservation give the minimum incident speed $v_{\min}$ required for a
recoil of energy $E_R$. This speed and the differential truth-level
recoil rate are

$$

\begin{aligned}
v_{\min}(E_R)&=\frac{|m_A E_R/\mu_A-\Delta m|}{\sqrt{2m_A E_R}},\\
\frac{dR}{dE_R}&=\frac{f_2\rho_\chi}{m_2}\sum_A w_A\,
\frac{(g_\chi Q_A/2)^2 F_A^2(q)}{2\pi(M_V^2+q^2)^2}\,\eta(v_{\min}).
\end{aligned}
$$

Here $q^2=2m_AE_R$, and $w_A$ is the mass fraction of each isotope in
natural xenon. We compute $F_A$ from a two-parameter Fermi density. The
velocity integral is
$\eta(v_{\min})=\int_{v>v_{\min}}d^3v\,f_{\rm lab}(\mathbf v)/v$. We
approximate the dark masses as degenerate in the flux and reduced mass
and retain the splitting in $v_{\min}$. The recoil energy at zero
incident speed is $E_R^\star=\Delta m\,\mu_A/m_A$. The location of the
spectral peak also depends on the velocity distribution and nuclear form
factors [gemmell2026](#ref-gemmell2026) · [deramo2016](#ref-deramo2016).

We recalculate the yield at the benchmark in Fig. 6 of
Ref. [gemmell2026](#ref-gemmell2026), with $m_\chi=35$ GeV, $M_V=30$ GeV,
$g_B=1.46\times10^{-5}$, $g_\chi=0.32$, and $g_{Vq}=g_B/6$. We obtain
$N_0=1.12044$ expected truth-level events in the signal window
$[5.4,269.9]$ keV and $7.39\times10^{-4}$ in the sideband $[350,675]$
keV. Including the detector response, the reference paper reports about
1 and $8\times10^{-4}$ events, respectively. We adjust the couplings of
the mass-weighted model to predict the same yield $N_0$ in the same
truth-level signal window. The LZ event-level analysis uses corrected S1
and S2 signals from 1710 events in its science sample
[lz2026](#ref-lz2026) · [gemmell2026](#ref-gemmell2026) · [lzdata](#ref-lzdata).

<a id="fig:recoil"></a>

![](./figures/01_xenon_recoil.png)

Truth-level differential recoil rates in events kg<span
class="math inline"><sup>−1</sup></span> day<span
class="math inline"><sup>−1</sup></span> keV<span
class="math inline"><sup>−1</sup></span>. Both models use <span
class="math inline"><em>m</em><sub><em>χ</em></sub> = 35</span> GeV and
<span class="math inline"><em>M</em><sub><em>V</em></sub> = 30</span>
GeV. For the mass-weighted model, <span
class="math inline"><em>g</em><sub><em>t</em></sub> = 0.12763</span> and
<span
class="math inline"><em>g</em><sub><em>χ</em></sub> = 0.29779</span>
reproduce the reference yield. The vertical line marks the reconstructed
recoil energy of the LZ candidate, and shading marks the integration
windows.

Eq. [\[eq:recoil\]](#eq:recoil) determines the normalization of the recoil
spectrum. In the contact limit $q\ll M_V$, the squared propagator gives
$1/M_V^4$, and the tree-level nuclear coupling $Q_A$ is proportional to
$g_t$. At fixed $m_\chi$, mass splitting, and halo model, the integrated
yield therefore scales as $f_2\kappa^2$, where $\kappa=g_tg_\chi/M_V^2$
and $f_2$ is the present-day local fraction of dark matter in the
heavier state.

For each $m_\chi$, let $\kappa_0(m_\chi)$ be the coupling combination
that gives $N_0=1.12044$ truth-level events at tree level with
$f_2=0.5$. The target yield in units of $N_0$ is
$r=N_{\rm ROI}^{\rm truth}/N_0$. We define $K_\gamma(m_\chi,d_\gamma)$
as the ratio of the integrated yield with photon mixing to the
tree-level yield in the same window, with $m_\chi$, $\kappa$, and $f_2$
held fixed.

$$
\frac{N_{\rm ROI}^{\rm truth}}{N_0}=\frac{f_2}{0.5}\left[\frac{\kappa}{\kappa_0(m_\chi)}\right]^2K_\gamma(m_\chi,d_\gamma).
$$

Setting the yield ratio to the chosen $r$ and solving for $\kappa$ gives

$$

\kappa=\kappa_0(m_\chi)\sqrt{\frac{r}{K_\gamma(m_\chi,d_\gamma)}\frac{0.5}{f_2}},\qquad
g_\chi=\frac{M_V^2}{g_t}\kappa.
$$

Integrating the spectrum separately at each mass gives
$\kappa_0(35,40,44\,\mathrm{GeV})=(4.223,5.665,7.202)\times10^{-5}\ \mathrm{GeV}^{-2}$.
As the dark matter mass increases, the characteristic recoil energy
approaches the upper edge of the window, and a larger coupling product
is needed to reproduce the reference yield. At fixed spectral shape, the
normalization scales with $r/f_2$. We set $r=1$ for the reference yield
and vary it over the prescribed range $r\in[0.75,1.25]$ to test the
effect of the normalization. This range carries no LZ confidence level.
We obtain the 95% CL limits by fitting the CMS monojet likelihood in
Section [5](#sec:monojet_method).

<a id="sec:abundance"></a>

## Thermal abundance and physical branches

We assume a standard thermal history and chemical equilibrium between
the two states during freeze-out. Their total number density $n=n_1+n_2$
obeys

$$

\begin{aligned}
\dot n+3Hn&=-\langle\sigma_{\rm eff}v\rangle[n^2-(n^{\rm eq})^2],\\
\langle\sigma_{\rm eff}v\rangle
&=\sum_{i,j=1,2}\frac{n_i^{\rm eq}n_j^{\rm eq}}{(n^{\rm eq})^2}\langle\sigma_{ij}v\rangle .
\end{aligned}
$$

The two dark states have the same spin degeneracy. In the
nonrelativistic limit their equilibrium number densities satisfy

$$
\frac{n_2^{\rm eq}}{n_1^{\rm eq}}\simeq\left(\frac{m_2}{m_1}\right)^{3/2}e^{-\Delta m/T}.
$$

The freeze-out temperature $T_f$ is much larger than the splitting
$\Delta m$, so the Boltzmann factor $e^{-\Delta m/T_f}$ is close to
unity. Each state therefore contributes about half of the equilibrium
number density at freeze-out. The present-day local fraction $f_2$ also
depends on late state conversion and the lifetime of the heavier state
(Appendix [9](#sec:matching)).

Each coannihilation through $\chi_1\chi_2\to V^*\to b\bar b,c\bar c$
consumes one particle of each state and reduces the total number by two.
The $(1,2)$ and $(2,1)$ terms in
Eq. [\[eq:boltzmann\]](#eq:boltzmann) together contribute
$2n_1^{\rm eq}n_2^{\rm eq}\langle\sigma_{12}v\rangle/(n^{\rm eq})^2$, or
about $\langle\sigma_{12}v\rangle/2$ for equal equilibrium fractions. As
the Universe cools and the actual density exceeds its equilibrium value,
a larger coannihilation rate removes dark particles faster and lowers
the relic abundance. Coannihilation is enhanced near the mediator
resonance, making the abundance sensitive to $M_V$. At one on-shell
benchmark with $m_\chi=35$ GeV, $b\bar b$ accounts for about $92\%$ of
the coannihilation rate. Annihilation of two particles in the same dark
state to $VV$ can set the abundance when that channel opens.
[griest1991](#ref-griest1991) · [gondolo1991](#ref-gondolo1991)

We compute the cross sections and solve for the total abundance with
CalcHEP and micrOMEGAs 7.1.4, using `Fast=0` and `Beps=1e-9`. We assume
that the two states together account for the full Planck dark matter
abundance $\Omega_ch^2=0.1200\pm0.0012$. [micromegas2024](#ref-micromegas2024) · [planck2020](#ref-planck2020)

At fixed $m_\chi$, Eq. [\[eq:yield\]](#eq:yield) gives the coupling and propagator factor for
coannihilation as

$$

\frac{(g_tg_\chi)^2}{(M_V^2-s)^2+M_V^2\Gamma_V^2}
=\frac{\kappa^2 M_V^4}{(M_V^2-s)^2+M_V^2\Gamma_V^2}.
$$

Changing $g_\chi$ affects the thermal average through the mediator
width. Changing $M_V$ also shifts the resonance relative to the energies
accessible at freeze-out. At $m_\chi=35$ GeV, $g_\chi=0.18$, and
$M_V\simeq87.56$ GeV, the local logarithmic slope of the abundance with
respect to the mediator mass is about $0.158\ \mathrm{GeV}^{-1}$. In
this slice, the Planck $\pm2\sigma$ interval corresponds to
$M_V\simeq87.43$--$87.68$ GeV. When we vary $m_\chi$ as well, the yield
and abundance conditions define multiple two-dimensional surfaces in the
four-dimensional parameter space. More than one dark matter mass can
satisfy both conditions at the same $(M_V,g_t)$.

<a id="fig:relic"></a>

![](./figures/02_relic_slope.png)

The left panel fixes <span
class="math inline"><em>m</em><sub><em>χ</em></sub> = 35</span> GeV. The
right panel shows the contribution of the pole neighborhood to the
instantaneous thermal average. Open symbols mark the freeze-out
temperatures at the individual points.

The main grid uses $r=1$, $f_2=0.5$, and $d_\gamma(0)=0$ and includes
the finite spacelike photon-mixing contribution from $c,b,t$ quarks. At
each $(M_V,g_t)$, we eliminate $g_\chi$ with
Eq. [\[eq:yield\]](#eq:yield) and look for crossings of $\Omega_\chi h^2=0.1200$
on both sides of $M_V-2m_\chi-\Delta m=0$. The grid contains 35 mediator
masses and 29 top couplings. We bracket roots at dark mass intervals of
at most $1.10$ GeV and sample more finely near threshold.

We approximate the Planck measurement $\Omega_ch^2=0.1200\pm0.0012$ with
a Gaussian. The difference in $-2\ln\mathcal L_\Omega$ from its value at
the center is the squared deviation in units of the measurement
uncertainty.

$$
-2\ln\frac{\mathcal L_\Omega(\Omega_\chi h^2)}{\mathcal L_\Omega(0.1200)}
=\left(\frac{\Omega_\chi h^2-0.1200}{0.0012}\right)^2.
$$

For example, $0.1188$ and $0.1176$ lie $1\sigma$ and $2\sigma$ below the
center, giving 1 and 4, respectively. To propagate the measurement
uncertainty to the collider limits, we use five abundance targets,
$0.1176,0.1188,0.1200,0.1212,0.1224$, at each of 11 representative
coordinates. For each target we hold $(M_V,g_t)$ and the LZ yield ratio
$r$ fixed, scan $m_\chi$, and use
Eq. [\[eq:yield\]](#eq:yield) to obtain $g_\chi$ at each trial mass. We record
the parameters of each branch where the calculated abundance reaches the
target. We record a missing solution when a branch has no root within
the scan range at that target.
Section [5](#sec:monojet_method) defines the CMS limit for solutions that
meet the on-shell template criteria.
Section [6](#sec:monojet_results) reports the effects of varying the
abundance and the target recoil yield.

<a id="sec:monojet_method"></a>

## LHC production, reconstruction, and statistical analysis

### Truth cross sections and reconstruction

The monojet signal includes the tree-level channels $q\bar q\to gV$ and
$qg\to qV$ and their charge conjugates, as well as the finite
closed-quark-loop contribution $gg\to gV$. For a pure vector current,
the three-point amplitude $gg\to V$ cancels. With an extra gluon, the
four-point amplitude can be nonzero. We sum the tree and loop cross
sections because these contributions have distinct initial states. We
calculate $pp\to t\bar tV$ at tree level. We use MadGraph5_aMC@NLO 3.6.6
with `nn23lo1` at 13 TeV and evaluate 11 values of $M_V$. In the
narrow-width approximation, the cross section for final state $X$ is

$$

\sigma_X=\sigma_X^{\rm prod}(M_V;g_t=1)\,g_t^2\,\mathrm{BR}(V\to\chi_1\chi_2).
$$

The hard-cut truth-level cross sections and the comparison with top-pair
production are given in Appendix [12](#sec:top). [cox2016](#ref-cox2016) · [alwall2014](#ref-alwall2014) · [hirschi2015](#ref-hirschi2015)

We build reconstructed monojet templates with Pythia 8.312 and Delphes
3.5.0, treating the on-shell $V$ as invisible. Both samples start at
generator-level $p_T^j=100$ GeV. To increase statistics in the tails, we
generate additional tree and loop samples starting at 350 and 480 GeV,
respectively, then combine the samples in mutually exclusive
generator-level intervals. At $M_V=120$ GeV we add a loop-sample
boundary at 230 GeV. Our reconstruction cuts approximate CMS EXO-20-004.
We require the leading AK4 jet to satisfy $p_T>100$ GeV and
$|\eta|<2.4$, and require $p_T^{\rm miss}>250$ GeV. We apply jet
azimuthal cuts, lepton and photon vetoes, and heavy-flavor-related
vetoes, and account for the 2018 HEM region. The data span three years
and about $137\ \mathrm{fb}^{-1}$, with 22 monojet signal bins per year.
[pythia2022](#ref-pythia2022) · [delphes2014](#ref-delphes2014) · [cmsmonojet](#ref-cmsmonojet) · [albert2021](#ref-albert2021)

### The 66-bin profile likelihood

We use the public observations $n_i$, the background-only control-region
prediction $\mathbf b$, its covariance $C_b$, and the signal $\mathbf s$
at each point to construct

$$

\begin{aligned}
\mathcal L(\mu,\mathbf b',\mathbf s') &=
\prod_{i=1}^{66}\operatorname{Pois}(n_i\mid b_i'+\mu s_i')\\
&\quad\times G(\mathbf b';\mathbf b,C_b)\,G(\mathbf s';\mathbf s,C_s).
\end{aligned}
$$

We constrain the signal yields to be nonnegative and the Poisson means
to be positive. The signal covariance $C_s$ includes the multinomial
covariance of the simulated counts, cross-section integration errors,
and a common $1.6\%$ luminosity uncertainty. We retain correlations
across years when they share simulated events. Between mass nodes, we
interpolate yields linearly and combine the covariances of independent
samples with squared interpolation weights. For each branch, $\mu=1$
denotes its nominal prediction. We obtain $\mu_{95}$ by solving the
asymptotic condition $CL_s=0.05$. The expected limits use an Asimov data
set built from the central background prediction. The observed limits
use the measured $n_i$ and a conditional background Asimov data set. The
five expected quantiles describe background fluctuations. We propagate
the relic-density uncertainty by solving again for each physical root.
[cmscovariance](#ref-cmscovariance) · [cmsyields](#ref-cmsyields) · [cmssimplified](#ref-cmssimplified) · [cowan2011](#ref-cowan2011) · [read2002](#ref-read2002)

We use the one-sided profile likelihood ratio

$$
\tilde q_\mu=-2\ln\frac{\mathcal L(\mu,\widehat{\widehat{\boldsymbol\theta}}_\mu)}{\mathcal L(\widehat\mu,\widehat{\boldsymbol\theta})}.
$$

We set it to zero when $\widehat\mu>\mu$ and constrain
$\widehat\mu\ge0$. With $a=\sqrt{\tilde q_{\mu,A}}$, the observed
asymptotic statistic is

$$

\begin{aligned}
CL_s(\mu)&=\frac{\Phi(-z_\mu)}{\Phi(a-z_\mu)},\\
z_\mu&=\begin{cases}\sqrt{\tilde q_\mu},&\tilde q_\mu\le a^2,\\
(\tilde q_\mu+a^2)/(2a),&\tilde q_\mu>a^2.\end{cases}
\end{aligned}
$$

For the expected bands, we solve $a=z-\Phi^{-1}[0.05\Phi(z)]$ on the
nominal background Asimov data set for $z=-2,-1,0,1,2$. [cowan2011](#ref-cowan2011)

Appendix [11](#sec:validation) compares the 66-bin fit using official CMS
vector templates with the published fit. It also compares the cutflow,
acceptance, and MET spectra from independent simulation. CMS reports
expected and observed vector mass boundaries of 2.198 and 1.957 TeV. The
66-bin reconstruction gives 2.208 and 1.941 TeV. The discrepancies are
larger for individual observed limits at low masses. At the 2017 CMS
vector benchmark with a 100 GeV mediator, independent fast simulation
gives 62.9% of the official absolute signal yield. This comparison
limits the precision with which we can validate the acceptance used to
locate the exclusion contour.

<a id="sec:monojet_results"></a>

## ==🔴Monojet results and stability

### Branch-resolved results at the central relic abundance

At the reference yield $r=1$ with $f_2=0.5$ and $d_\gamma(0)=0$,
Eq. [\[eq:yield\]](#eq:yield) fixes $g_\chi=g_\chi(m_\chi;M_V,g_t)$. Let
$\mathcal D_\chi$ be the set of masses $20\le m_\chi\le100$ GeV for
which Eq. [\[eq:yield\]](#eq:yield) gives $0.10\le g_\chi\le1.50$. At each $(M_V,g_t)$
we define

$$
\begin{gathered}
\mathcal S_{\rm on}(M_V,g_t) = \{m_\chi\in\mathcal D_\chi:\ \Omega_\chi h^2=0.1200,\\
M_V-m_1-m_2\ge5\Gamma_V,\quad \Gamma_V/M_V<0.03\}.
\end{gathered}
$$

Where $\mathcal S_{\rm on}$ contains exactly one solution, the color
shows the 95% CL limit $\mu_{95}$ from CMS data alone for that branch.
The black contour marks $\mu_{95}=1$. Gray marks coordinates without a
unique on-shell solution satisfying the narrow-width criteria in the
scan. An off-shell monojet limit would require templates from the full
$pp\to j\chi_1\chi_2$ matrix element.

<a id="fig:exclusion"></a>

![](./figures/04_cms_central_plane.png)

Expected and observed CMS monojet 95% confidence-level
limits on the unique branch satisfying the recoil-yield,
central-abundance, and narrow-width conditions. The black contour marks
<span class="math inline"><em>μ</em><sub>95</sub> = 1</span>. Gray
denotes coordinates with no unique in-scope solution.

Of the 1,015 grid coordinates, 434 have a unique on-shell solution at
the central relic abundance that satisfies the template requirements.
With the reference templates in
Fig. [3](#fig:exclusion), the expected and observed limits fall below
unity at 208 and 151 points, respectively. The lowest sampled masses
with $\mu_{95}<1$ are 92 and 104 GeV. These counts and masses depend on
the grid spacing. At the interior point
$(M_V,g_t)=(112\,\mathrm{GeV},2.747)$, the solution
$(m_\chi,g_\chi)=(40.055\,\mathrm{GeV},0.260)$ gives expected and
observed limits of $0.513$ and $0.540$. The smallest observed limit with
the reference templates is $0.181$ at $(200\,\mathrm{GeV},\sqrt{4\pi})$.
With pooled templates at three mass nodes, the number of observed limits
below unity rises to 162, with 11 grid points crossing the exclusion
contour (Appendix [11](#sec:validation)).
Section [7](#sec:discussion) discusses the off-shell roots at lower
masses.

At some mediator masses, monojet sensitivity is confined to a finite
interval in $g_t$. At fixed masses and LZ yield,
$g_\chi\propto g_t^{-1}$, so $\Gamma_{\chi_1\chi_2}=A/g_t^2$ and
$\Gamma_{\rm SM}=Bg_t^2$, with $A,B$ constant on the slice. The signal
factor in Eq. [\[eq:nwa\]](#eq:nwa) is $g_t^2/(1+(B/A)g_t^4)$ and peaks where the two
widths are equal. At larger $g_t$, the invisible branching fraction can
decrease enough to offset the increase in production.

| $M_V$ \[GeV\] | $g_t$ | $m_\chi$ \[GeV\] | $g_\chi$ | Expected $\mu_{95}$ | Observed $\mu_{95}$ | Observed, $r=0.75$--$1.25$ |
| --- | --- | --- | --- | --- | --- | --- |
| 80 | 0.503 | 33.027 | 0.482 | 6.891 | 15.58 | 15.55--15.64 |
| 100 | 1.264 | 38.065 | 0.400 | 1.333 | 2.305 | 2.276--2.352 |
| 120 | 3.073 | 41.116 | 0.284 | 0.412 | 0.607 | 0.570--0.664 |
| 150.4 | 1.260 | 43.896 | 1.286 | 0.986 | 1.822 | 1.820--1.824 |
| 150.4 | 3.545 | 43.896 | 0.457 | 0.184 | 0.340 | 0.329--0.357 |
| 190.4 | 3.545 | 45.854 | 0.823 | 0.219 | 0.273 | 0.270--0.277 |

<a id="fig:uncertainties"></a>

![](./figures/05_collider_uncertainties.png)

Blue intervals show the <span
class="math inline">±1<em>σ</em></span> and <span
class="math inline">±2<em>σ</em></span> expected quantiles from
background fluctuations. Brown marks show the effect of the Planck <span
class="math inline">±2<em>σ</em></span> measurement uncertainty on the
median expected limit. Red diamonds mark observed limits.

Using the procedure in Section [4](#sec:abundance), we find that varying the Planck abundance by
$\pm2\sigma$ changes the median expected monojet $\mu_{95}$ by at most
$0.44\%$ relative to the central-abundance result at the reference
on-shell benchmarks. For example, at $M_V=150.4$ GeV, $g_t=1.260$, and
$r=1$, the targets $0.1188,0.1200,0.1212$ give
$(m_\chi/{\rm GeV},g_\chi)=(43.945,1.290),(43.896,1.286),(43.848,1.282)$,
respectively. Across all five abundance targets, the median expected
$\mu_{95}$ for this branch ranges from $0.98589$ to $0.98606$.

At the 120 GeV point in
Fig. [4](#fig:uncertainties), propagating the abundance uncertainty
gives median expected limits from $0.41056$ to $0.41415$. Background
fluctuations give a $1\sigma$ expected band of $[0.295,0.581]$.
Accounting for finite signal statistics and luminosity weakens the
median expected limits by about $1.4\%$--$6.6\%$ compared with fits that
fix the signal template. A model-specific covariance for scale and PDF
uncertainties, production matching, and detector efficiencies remains to
be determined.

<a id="sec:low_energy"></a>

### Low-energy photon mixing, the rate target, and the excited fraction

Kinetic mixing with the photon gives the mediator $V$ an additional
coupling to the electromagnetic current. We define
$d_\gamma=e\epsilon_\gamma/g_t$, so the effective proton coupling
receives a shift of $g_t d_\gamma$. The zero-momentum value
$d_\gamma(0)$ is an independent matching input, which we set to zero in
the main scan. Charged-quark loops give a finite correction relative to
zero momentum. We retain the $c,b,t$ contribution $\delta d_{cbt}(-q^2)$
from Appendix [9](#sec:matching). [deramo2016](#ref-deramo2016) · [forner2026](#ref-forner2026)

With a common Helm form factor, only the protons contribute to the
electric charge term, so photon mixing shifts $Q_A/g_t$ by
$Z[d_\gamma(0)+\delta d_{cbt}(-q^2)]$. For $^{131}$Xe, the tree-level
charge is $Q_A/g_t\simeq8.05\times10^{-3}$ and $Z=54$. The mixing
contribution can therefore nearly cancel the tree-level amplitude at
$d_\gamma(0)\simeq-1.49\times10^{-4}$. At the reference value
$d_\gamma(0)=0$ and $m_\chi=35$ GeV, the retained momentum-dependent
correction reduces the integrated rate in the recoil window by about
$0.077\%$.

At $m_\chi=35$ GeV and fixed couplings, $d_\gamma(0)=-7\times10^{-6}$
and $+7\times10^{-6}$ give rates of $0.908$ and $1.095$ times the
tree-level rate, respectively. Matching the same reference yield then
requires $\kappa/\kappa_0=1.050$ and $0.956$, respectively. Near
cancellation, this ratio rises to about $56.5$. In that case we find no
solution at the central Planck abundance within the scanned coupling
ranges at the 11 coordinates tested.

Figure [8](#fig:mixing)
compares the required coupling and the recoil spectra.

Varying the target yield over $r=0.75$--$1.25$ changes the median
expected monojet limit by at most $9.4\%$ at the points tested. Reducing
$f_2$ alone to 0.45 or 0.30 changes it by up to $3.0\%$ and $12.8\%$,
respectively. Varying only the low-energy mixing within
$|d_\gamma(0)|\le7\times10^{-6}$ changes it by at most $2.8\%$. At the
120 GeV benchmark, the choices
$(d_\gamma(0),r,f_2)=(+7\times10^{-6},0.75,0.50)$ and
$(-7\times10^{-6},1.25,0.45)$ give median expected limits of $0.465$ and
$0.367$, respectively. Appendix [9](#sec:matching) discusses how late downscattering and the
excited-state lifetime affect the present-day fraction.

In a separate check at $r=2$, we solve again for the central Planck
abundance. The three sensitive benchmarks in
Table [\[tab:benchmarks\]](#tab:benchmarks) at $M_V=120,150.4,190.4$ GeV still give
observed $\mu_{95}<1$, with limits of $0.507,0.310,0.265$, respectively.

At the other representative point with $M_V=150.4$ GeV and $g_t=1.260$,
increasing $r$ from 1 to 2 moves the central-abundance solution to
$g_\chi=1.498$, close to the scan boundary $g_\chi=1.50$. The invisible
branching fraction rises from $0.9922$ to $0.9944$, and the observed
$\mu_{95}$ changes from $1.822$ to $1.818$, remaining above the
exclusion threshold. At $r=2$ we find no solution on this branch within
the scan range for the lower abundance targets $0.1188$ and $0.1176$, so
no CMS limits are available at those two targets.

Figure [9](#fig:rate) shows
how the limits vary with the target yield.

<a id="sec:discussion"></a>

## Discussion of top-associated production

At a fixed $(M_V,g_t)$, the on-shell and off-shell relic solutions can
give different signals in $t\bar t+\mathrm{MET}$. We compute the full
four-body final state below the invisible-decay threshold and give
representative truth-level rates in
Appendix [12](#sec:top). A CMS
exclusion in the all-hadronic two-$b$-tag category requires signal
acceptance after top decays and a likelihood with background constraints
independent of the signal-region counts. The single-top estimate in
Appendix [12](#sec:top) is
sensitive to the partonic-energy cut. [cmstop](#ref-cmstop)

> [!question] 新增 A02.01
> 相对本地 PRD 旧稿。

<a id="sec:ttbar_recast"></a>

## CMS top-pair production with missing transverse momentum

> [!tip] 新增 A02.02
> 相对本地 PRD 旧稿。

==The top-quark coupling also produces a dark pair in association with a top-quark pair. We estimate the expected sensitivity of the CMS all-hadronic $0\ell2b$ category at $\sqrt{s}=13$ TeV with $138~\mathrm{fb}^{-1}$ [cmstop](#ref-cmstop). This extends the truth-level top-pair discussion to reconstructed events on an on-shell grid. The off-shell rates and the exploratory single-top estimates are given in [the top-associated appendix](#sec:top).==

> [!tip] 新增 A02.03
> 相对本地 PRD 旧稿。

### Recoil normalization and physical grid

> [!tip] 新增 A02.04
> 相对本地 PRD 旧稿。

==We use the yukawa-like quark couplings and the same reference truth-level yield of 1.12044 events in the $5.4$–$269.9$ keV recoil window. The top-pair grid uses tree-level recoil matching with a Helm form factor [engel1991](#ref-engel1991), $f_2=0.5$, and $\Delta m=1$ MeV. The monojet grid uses the recoil prescription described in [the xenon section](#sec:recoils) and includes the finite spacelike photon-mixing term in the central scan. The grids therefore implement the same reference yield with channel-specific recoil prescriptions.==

> [!warning] 新增 A02.05
> 相对本地 PRD 旧稿。

==At fixed $(M_V,g_t)$, the recoil integral fixes $\kappa(m_\chi)=g_tg_\chi/M_V^2$, and the central Planck abundance fixes $m_\chi$ on the on-shell branch. The root search covers $8~\mathrm{GeV}\le m_\chi\le\min(47.8~\mathrm{GeV},M_V/2)$ and uses micrOMEGAs. We require $0<g_\chi\le\sqrt{4\pi}$, $\Gamma_V/M_V<0.03$, and $M_V-m_1-m_2\ge5\Gamma_V$. We retain 470 points from 14 mediator masses between 20 and 200 GeV and 44 trial couplings per mass. Of the other 146 trial nodes, 51 have no root within the scan and 95 fail the width requirement. The retained dark masses range from 8.42 to 46.59 GeV, and the invisible branching fractions range from $1.7\times10^{-5}$ to unity.==

> [!question] 新增 A02.06
> 相对本地 PRD 旧稿。

<a id="fig:ttbar_grid"></a>

![](./figures/fig1_v10.png)

On-shell top-pair grid after the recoil-yield, central-abundance, and narrow-width requirements. The left panel shows dark matter mass versus mediator mass, colored by the dark coupling. The right panel shows the dark coupling versus dark matter mass, colored by mediator mass. The line in the left panel marks the approximate invisible-decay threshold.

> [!question] 新增 A02.07
> 相对本地 PRD 旧稿。

### Signal generation and expected likelihood

> [!tip] 新增 A02.08
> 相对本地 PRD 旧稿。

==We generate the $pp\to t\bar t\chi_1\chi_2$ signal at leading order with MadGraph5_aMC@NLO, decay both top quarks hadronically, shower the events with Pythia 8, and apply a CMS-like Delphes detector simulation. We generate $8\times10^3$–$2\times10^4$ events per point, about $8.3\times10^6$ in total. The generated cross section $\sigma_{\rm vis}$ includes the hadronic decays and the invisible decay through the mediator propagator. The signal-region yield is $\mathcal L\,\varepsilon_{\rm SR}\sigma_{\rm vis}$. Selection efficiencies range from $0.66\%$ to $6.59\%$.==

> [!warning] 新增 A02.09
> 相对本地 PRD 旧稿。

==We veto electrons and muons with $p_T>10$ GeV and $|\eta|<2.4$ and require at least three jets with $p_T>30$ GeV and $|\eta|<2.4$, including at least two $b$ tags. We require $p_T^{\rm miss}>250$ GeV, $p_T(j_1)/H_T<0.5$, $\min\Delta\phi(j_{1,2},p_T^{\rm miss})>0.8$, and $m_T^b>140$ GeV, using the highest-$p_T$ tagged jet for $m_T^b$. The detector model uses parameterized $b$ tagging, a jet radius of 0.5, and no simulated pileup.==

> [!tip] 新增 A02.10
> 相对本地 PRD 旧稿。

==We use the 15 bins of the published post-fit $p_T^{\rm miss}$ projection, with 20 GeV bins from 250 to 530 GeV and an overflow bin. CMS extracts its signal using neural-network score bins and combines lepton categories. We use one category and take its published post-fit background yields $b_i$ as the background-only Asimov data, $n_i=b_i$. A coherent Gaussian normalization nuisance $\theta$, with width $w=0.03198$, gives==

> [!tip] 新增 A02.11
> 相对本地 PRD 旧稿。

$$
-2\ln L(\mu,\theta)=2\sum_{i=1}^{15}
\left[\nu_i-n_i\ln\nu_i\right]+\left(\frac{\theta}{w}\right)^2,
\qquad \nu_i=b_i(1+\theta)+\mu s_i.
$$

> [!tip] 新增 A02.12
> 相对本地 PRD 旧稿。

==Here $s_i$ is the signal yield in bin $i$. We profile $\theta$ and solve $\mathrm{CL}_s=0.05$ for the median expected upper limit $\mu_{95}$. The post-fit inputs and the approximate background covariance limit this interpretation to expected sensitivity. We do not fit the observed counts or combine the likelihood with the monojet analysis.==

> [!tip] 新增 A02.13
> 相对本地 PRD 旧稿。

### Expected limits and their stability

> [!tip] 新增 A02.14
> 相对本地 PRD 旧稿。

==The median expected limit falls below unity at 381 of the 470 sampled points, including all sampled points with $M_V\ge100$ GeV. Between 50 and 90 GeV the lower boundary lies near $g_t=0.17$. At 30 and 40 GeV the limit rises above unity again near $g_t=2.7$ and 3.0, respectively. The single nominal crossing at 20 GeV is within the template Monte Carlo uncertainty.==

> [!tip] 新增 A02.15
> 相对本地 PRD 旧稿。

| $M_V$ [GeV] | Sampled points | Expected $\mu_{95}<1$ | Expected $\mu_{95}$ range |
|---:|---:|---:|---:|
| 20 | 44 | 1 | 0.938 to $>60$ |
| 30 | 44 | 34 | 0.099–2.93 |
| 40 | 44 | 36 | 0.105–3.21 |
| 50 | 44 | 37 | 0.085–2.58 |
| 60 | 44 | 38 | 0.055–3.11 |
| 70 | 44 | 37 | 0.031–2.67 |
| 80 | 43 | 37 | 0.023–2.70 |
| 90 | 38 | 36 | 0.017–1.05 |
| 100 | 34 | 34 | 0.011–0.61 |
| 120 | 27 | 27 | 0.007–0.20 |
| 140 | 22 | 22 | 0.005–0.10 |
| 160 | 17 | 17 | 0.003–0.04 |
| 180 | 14 | 14 | 0.004–0.03 |
| 200 | 11 | 11 | 0.003–0.02 |

> [!warning] 新增 A02.16
> 相对本地 PRD 旧稿。

<a id="fig:ttbar_map"></a>

![](./figures/fig2_v10.png)

Median expected 95% CL signal-strength limits from the all-hadronic top-pair recast. Each colored cell represents one sampled point. The line joins the nominal unity crossings of neighboring mass columns where the crossings are close enough to connect. Gray cells have no retained solution on the scanned branch.

> [!warning] 新增 A02.17
> 相对本地 PRD 旧稿。

==At low coupling, the production rate falls and the expected limit weakens. At large coupling, the quark width can reduce the invisible branching fraction enough to reverse this trend. The selected yield depends on both the cross section and the acceptance. At 30 and 40 GeV the turnover takes the yield below the level needed for the expected limit to reach unity. At 50 GeV the higher selection efficiency keeps the expected limit below unity at the largest scanned coupling.==

> [!tip] 新增 A02.18
> 相对本地 PRD 旧稿。

<a id="fig:ttbar_curves"></a>

![](./figures/fig3_v10.png)

Median expected upper limits as a function of the top-quark coupling at six mediator masses. The dashed line marks unity. Open markers indicate points beyond the numerical scan cap of 60.

> [!question] 新增 A02.19
> 相对本地 PRD 旧稿。

<a id="fig:ttbar_visible"></a>

![](./figures/fig4_v10.png)

Generated hadronic signal cross section (left axis) and invisible branching fraction (right axis) for four mediator masses. Vertical lines mark the nominal unity crossings of the expected limit. The high-coupling boundary depends on the selected yield and the missing-momentum template.

> [!tip] 新增 A02.20
> 相对本地 PRD 旧稿。

==🔴We propagate template statistics at all 132 sampled points with $M_V=20$–40 GeV. Requiring $\mu_{95}+2\sigma_{\rm MC}<1$ changes the counts at 20, 30, and 40 GeV from 1, 34, and 36 to 0, 32, and 32. The renormalization- and factorization-scale envelope tested at three representative points shifts the expected limits by $-29\%$ to $+28\%$. This is the largest theory variation tested.==

> [!tip] 新增 A02.21
> 相对本地 PRD 旧稿。

==🔴We solve the relic equation again at $\Omega_\chi h^2=0.1176$ and 0.1224. All 470 central points remain admissible at both edges. Rescaling the signal by the change in invisible branching fraction shifts the median limit by $0.02\%$. One point crosses unity, by $0.05\%$, within its template statistical uncertainty. Dedicated endpoint samples at four nodes give efficiencies consistent with the central samples within their statistical precision. The endpoint simulations directly test those four nodes.==

<a id="sec:conclusions"></a>

## Conclusions

In this broken-phase vector model, light-quark couplings set the leading
coherent xenon recoil amplitude, and heavy-quark couplings drive
production at the LHC. For small photon mixing, fixed dark-state
splitting, and a standard thermal history, the CMS Run 2 monojet recast
excludes some on-shell solutions that reproduce the reference recoil
yield and central Planck abundance. Their observed 95% CL limits satisfy
$\mu_{95}<1$. The three sensitive benchmarks remain excluded when the
truth-level yield target varies by $25\%$. For lighter mediators,
on-shell and off-shell relic solutions can occur at the same mediator
mass and top coupling. The strong dependence on the partonic-energy cut
limits the single-top result to an exploratory estimate. A joint
confidence region would require an event-level LZ likelihood for the
model, theoretical uncertainties on the abundance, and profiling over
shared parameters.

> [!tip] 新增 A03
> 相对本地 PRD 旧稿。

==The all-hadronic top-pair recast provides a complementary estimate of expected sensitivity. The median expected upper limit falls below unity at 381 of 470 sampled on-shell points, including all sampled points with $M_V\ge100$ GeV. At 30 and 40 GeV the upper coupling boundary follows the reduction in the invisible branching fraction. At 20 GeV the single nominal crossing lies within the template statistical uncertainty. The top-pair likelihood uses a single signal category and a post-fit missing-momentum projection. A joint collider result would require compatible signal grids and a treatment of shared systematic uncertainties.==

<a id="data-availability"></a>

## Data availability

> [!info] 改写 C03
> 相对本地 PRD 旧稿。

==The experimental inputs are available through the LUX-ZEPLIN and CMS public data releases [lzdata](#ref-lzdata) · [cmscovariance](#ref-cmscovariance) · [cmsyields](#ref-cmsyields) · [cmssignal](#ref-cmssignal) · [cmscutflow](#ref-cmscutflow). The model files, analysis code, public-input snapshots, binned signal templates, numerical scans, and reproduction instructions are available at <https://github.com/Jim11451/lz_paper>, with the archived version [`reproducibility-2026.11.19`](https://github.com/Jim11451/lz_paper/tree/reproducibility-2026.11.19).==

<a id="sec:matching"></a>

## Xenon recoil and matching checks

<a id="fig:reference_recoil"></a>

![](./figures/a01_original_recoil.png)

Independent reproduction of the universal-vector reference
benchmark, used to check the recoil shape and units.

After subtraction at zero momentum, the finite heavy-quark contribution
to photon mixing is

$$

\begin{aligned}
\delta d_{cbt}(s)&=-\frac{2\alpha}{\pi}\sum_{q=c,b,t}N_cQ_q\frac{\widehat m_q}{m_t}\\
&\quad\times\int_0^1 dx\,x(1-x)\log\left[1-\frac{s x(1-x)}{\widehat m_q^2}-i0\right].
\end{aligned}
$$

<a id="fig:timelike"></a>

![](./figures/a02_timelike_mixing.png)

At four on-shell masses we include <span
class="math inline"><em>δ</em><em>d</em><sub><em>c</em><em>b</em><em>t</em></sub>(<em>M</em><sub><em>V</em></sub><sup>2</sup>)</span>
in the <span
class="math inline"><em>p</em><em>p</em> → <em>V</em><em>j</em></span>
tree amplitude. For <span
class="math inline"><em>p</em><sub><em>T</em></sub><sup><em>j</em></sup> &gt; 200</span>
GeV, the tree cross section changes by about <span
class="math inline">2%</span> or less. Relative to the original
tree-plus-loop cross section, the shift is below <span
class="math inline">0.4%</span>. For the relic calculation, we
approximate the finite term by its real part evaluated at the dark-pair
threshold or at the mediator pole. The largest shifts in <span
class="math inline"><em>Ω</em><em>h</em><sup>2</sup></span> across the
four points are <span class="math inline">1.12 × 10<sup>−4</sup></span>
and <span class="math inline">4.64 × 10<sup>−4</sup></span>,
respectively. Lowering <code>Beps</code> by two orders of magnitude
changes the abundance by less than <span
class="math inline">2 × 10<sup>−11</sup></span> at three numerical
benchmarks.

<a id="fig:fraction"></a>

![](./figures/a03_excited_fraction.png)

The conversion <span
class="math inline"><em>χ</em><sub>2</sub><em>χ</em><sub>2</sub> ↔︎ <em>χ</em><sub>1</sub><em>χ</em><sub>1</sub></span>
can change the excited-state fraction after chemical freeze-out. In the
standard thermal histories tested, with additional decay suppressed and
the Standard Model bath included, the minimum at the on-shell benchmarks
is <span class="math inline"><em>f</em><sub>2</sub> ≃ 0.45</span> and
falls to about <span class="math inline">0.30</span> at some off-shell
benchmarks. The splitting <span
class="math inline"><em>Δ</em><em>m</em> &lt; 2<em>m</em><sub><em>e</em></sub></span>
closes the electron-pair decay channel. Independent <span
class="math inline"><em>V</em></span>–<span
class="math inline"><em>Z</em></span> mixing or a transition dipole can
still affect the lifetime. <span class="citation"
data-cites="gemmell2026 carrillo2022"></span>

After the total abundance freezes out, detailed balance for dark-state
conversion gives
$\dot f_2=-n_\chi\langle\sigma v\rangle_{22\to11}[f_2^2-e^{-2\Delta m/T_\chi}(1-f_2)^2]$,
where $T_\chi$ is the dark-sector kinetic temperature. We model
conversion with Born contact scattering and vary the assumptions about
kinetic decoupling. The resulting $f_2$ values serve as benchmarks for
those thermal histories.

<a id="fig:mixing"></a>

![](./figures/06_matching_and_spectra.png)

The left panel shows how photon mixing changes the coupling
required to match the yield. The right panel compares spectra with the
same integrated truth-level yield. After Gaussian smoothing with a width
of 32.5 keV, the signal densities near 248 keV at <span
class="math inline"><em>m</em><sub><em>χ</em></sub> = 20, 35, 44</span>
GeV are approximately <span
class="math inline">2.75 × 10<sup>−4</sup></span>, <span
class="math inline">4.54 × 10<sup>−3</sup></span>, and <span
class="math inline">6.98 × 10<sup>−3</sup></span> events/keV. The
energy-spectrum approximation uses Gaussian smoothing alone. The LZ
S1/S2 response and backgrounds enter an event-level
analysis.

<a id="fig:rate"></a>

![](./figures/07_lz_rate_variation.png)

We solve for the central Planck abundance and compute the
CMS limit for each on-shell point at each fixed target yield. The shaded
interval <span class="math inline"><em>r</em> = 0.75</span>–<span
class="math inline">1.25</span> is the prescribed range for the
normalization test, corresponding to <span
class="math inline">0.84</span>–<span class="math inline">1.40</span>
expected truth-level events.

<a id="sec:production_checks"></a>

## Cross-section cuts and the mass projection

The UFO for the closed quark loop includes a rational $R_2$ vertex for
$gggV$ for each quark flavor. We replace the photon vector coupling in
`loop_sm` to obtain the coefficient $i g_{Vq}g_s^3/(48\pi^2)$ per
flavor, with color structure $d^{abc}$. Including this term gives a
numerical Ward/BRS test ratio of about $6.3\times10^{-24}$ for
$gg\to gV$ at $M_V=87.18$ GeV and a partonic energy of 1 TeV.
[hirschi2015](#ref-hirschi2015)

<a id="fig:loose"></a>

![](./figures/b01_loose_cross_sections.png)

The jet selection is <span
class="math inline"><em>p</em><sub><em>T</em></sub><sup><em>j</em></sup> &gt; 20</span>
GeV and <span
class="math inline">|<em>η</em><sub><em>j</em></sub>| &lt; 6</span>, and
the top-pair final state has no truth MET cut. Comparison with Fig. [19](#fig:hard_met) shows the effect of the selection
threshold.

<a id="fig:equal_rate_xsec"></a>

![](./figures/b02_lz_slice_cross_sections.png)

We fix <span
class="math inline"><em>m</em><sub><em>χ</em></sub> = 35</span> GeV and
determine <span
class="math inline"><em>g</em><sub><em>t</em></sub></span> from the
tree-level equal-rate condition. A, B, and C are separate relic-density
benchmarks. The remaining colors show cross sections subject to the
equal-rate condition alone.

<a id="fig:mass_projection"></a>

![](./figures/04b_central_mass_projection.png)

Projection of the central relic grid onto <span
class="math inline">(<em>m</em><sub><em>χ</em></sub>, <em>M</em><sub><em>V</em></sub>)</span>.
Dark blue marks on-shell roots with observed <span
class="math inline"><em>μ</em><sub>95</sub> &lt; 1</span>. Multiple
coupling solutions can overlap in the mass projection.

<a id="sec:validation"></a>

## ==🔴Validation of the CMS monojet recast

<a id="fig:cms_official"></a>

![](./figures/c01_cms_benchmark_limits.png)

Comparison of limits obtained using official CMS signal
templates. For scalar and pseudoscalar benchmarks between 50 and 800
GeV, the expected limits from the 66-bin fit differ from the published
combination by at most about <span class="math inline">9%</span>. The
largest difference in observed limits is about <span
class="math inline">48%</span>. The mass boundaries provide a separate
check of the overall reach for the official vector benchmark. <span
class="citation" data-cites="cmsmonojet cmssignal"></span>

<a id="fig:cms_750"></a>

![](./figures/c02_cms_vector_750.png)

Cutflow and MET spectrum for the 750 GeV CMS vector
benchmark.

<a id="fig:cms_100"></a>

![](./figures/c03_cms_vector_100.png)

Cutflow and MET spectrum for the 100 GeV CMS vector
benchmark. Comparison of independent LO event generation and fast
detector simulation with official CMS vector benchmarks. For the 100 GeV
benchmark in 2017, the efficiency after the MET cut is <span
class="math inline">76.91%</span> for CMS and <span
class="math inline">77.76%</span> in our simulation. The absolute QCD
signal yield in our simulation is 0.629 times the CMS yield. The two
samples use different generator and reconstruction settings, including
NLO matching in the official sample. We compare the normalized shapes
and the absolute yields separately. <span class="citation"
data-cites="cmscutflow"></span>

<a id="fig:cms_2000"></a>

![](./figures/c04_cms_vector_2000.png)

Cutflow and MET spectrum for the 2000 GeV CMS vector
benchmark.

<a id="fig:small_sample"></a>

![](./figures/c05_loop_mc_validation.png)

Of the 3,600 events in the original loop sample, 17 pass the
reconstructed selection and fall in MET bins above 470 GeV. At the same
central relic solution, the original sample gives an observed <span
class="math inline"><em>μ</em><sub>95</sub></span> of about 1.30. An
independent sample gives 0.67, and a stratified sample gives 0.61. The
main analysis uses the stratified template and all observed
counts.

### Independent template test at three sensitive benchmarks

We keep $(M_V,g_t,m_\chi,g_\chi)$ fixed at the 120, 150.4, and 190.4 GeV
benchmarks in
Table [\[tab:benchmarks\]](#tab:benchmarks), along with the 66-bin CMS likelihood and
background covariance. Loop templates A and B use independent
hard-process and shower samples, with generator-level jet $p_T$
boundaries of $(100,230,480)$ and $(100,260,520)$ GeV, respectively. The
three strata typically contain 6,600, 4,000, and 3,200 generated events.
For the lowest stratum of A at 120 and 150.4 GeV, we use an independent
archived sample of 10,800 events and a new sample of 4,800 events,
respectively, and retain events with $100\le p_T^j<230$ GeV. Both fits
share a newly generated tree template. We also repeat both fits with the
original tree template. We average the loop templates with equal
weights, combine the Monte Carlo covariances with squared weights, and
count the common tree uncertainty once.

We rank the year-specific MET bins using
$|s_i[(C_b+\operatorname{diag}\mathbf b)^{-1}\mathbf s]_i|$, evaluated
with the reference signal and the background-only information. In the
eight highest-ranked bins, we compare the yield differences with the
Monte Carlo uncertainties of the independent loop samples. We also sum
yields across years in the 470--690 GeV and above-690 GeV intervals and
refit the upper limits using all 66 bins.

| $M_V$ \[GeV\] | Expected A / B / pooled | Observed A / B / pooled | Max. difference ($\sigma_{\rm MC}$) |
| --- | --- | --- | --- |
| 120 | 0.389 / 0.407 / 0.408 | 0.527 / 0.621 / 0.561 | 1.05 |
| 150.4 | 0.230 / 0.243 / 0.242 | 0.219 / 0.254 / 0.234 | 0.88 |
| 190.4 | 0.174 / 0.178 / 0.179 | 0.200 / 0.200 / 0.198 | 1.68 |

Comparison of independent signal templates for the three sensitive benchmarks. The final column gives the largest discrepancy in one of the eight key bins in units of the Monte Carlo (MC) uncertainty.

<a id="fig:independent_samples"></a>

![](./figures/c06_three_template_replicas.png)

The top panels show the CMS 95% CL limits. The dashed lines
mark the reference observed limits from Table [[tab:benchmarks]](#tab:benchmarks). The lower panels
show the yield of each template divided by the reference yield in two
combined MET intervals. The error bars represent the Monte Carlo
uncertainty of each template. The accompanying analysis tables give
yields by year and bin.

The two templates agree within about $1.7$ Monte Carlo standard
deviations in the key bins and combined high-MET intervals. All three
benchmarks give observed $\mu_{95}<1$. Across templates and target
yields in the range $r=0.75$--$1.25$, the largest observed limit is
$0.680$. At 120 and 150.4 GeV, the two stratifications still give
observed limits that differ by about $16\%$ and $15\%$ of their mean,
respectively. At 150.4 and 190.4 GeV, the pooled limits are about $31\%$
and $27\%$ below the reference values in
Table [\[tab:benchmarks\]](#tab:benchmarks). The three exclusion decisions are stable
across the sampling schemes tested, while the numerical limits retain
some dependence on Monte Carlo statistics and template shape.

We refit the original grid with the three pooled templates, replacing
the 120 and 150 GeV nodes and adding the 190.4 GeV node. After
interpolation, the number of points with expected $\mu_{95}<1$ changes
from 208 to 199, and the observed count changes from 151 to 162. The
lowest sampled masses remain 92 and 104 GeV, respectively. The absolute
yield discrepancy in Fig. [15](#fig:cms_100) still limits the validation of the signal
acceptance.

<a id="sec:top"></a>

## Top-associated channels for light mediators

### Top-pair production

With the loose jet cut $p_T^j>20$ GeV, the truth-level $j+\mathrm{MET}$
cross section is comparable to the inclusive $t\bar t+\mathrm{MET}$
cross section near $M_V\simeq118$ GeV. Applying $p_T^{\rm miss}>200$ GeV
to both channels gives a cross-section ratio
$\sigma(j+\mathrm{MET})/\sigma(t\bar t+\mathrm{MET})$ of
$0.135$--$0.149$. For example, at
$(m_\chi,M_V,g_t,g_\chi)=(35,87.18,1.070,0.30)$ the two cross sections
are $0.166$ and $1.23$ pb, respectively. We treat the top quarks as
stable, so $p_T^{\rm miss}=p_T(V)$.
[cox2016](#ref-cox2016) · [alwall2014](#ref-alwall2014) · [hirschi2015](#ref-hirschi2015)

<a id="fig:hard_met"></a>

![](./figures/03_hard_met_cross_sections.png)

Truth-level cross sections in pb and their ratio for <span
class="math inline"><em>m</em><sub><em>χ</em></sub> = 35</span> GeV and
<span class="math inline"><em>g</em><sub><em>χ</em></sub> = 0.30</span>.
The dashed curve shows the tree-level LZ yield-matching condition. The
monojet cross section includes the leading tree channels and the <span
class="math inline"><em>g</em><em>g</em> → <em>g</em><em>V</em></span>
loop contribution.

The large top-quark coupling $g_t$ makes
$pp\to t\bar tV^{(*)}\to t\bar t\chi_1\chi_2$ another possible collider
probe. On-shell enhancement can occur when $M_V>2m_\chi+\Delta m$. Below
this threshold we generate the four-body final state directly. In the
low-mass scan, $(M_V,g_t)=(48\,\mathrm{GeV},0.252)$ has three solutions
at the central abundance, with $m_\chi=20.445,25.260,45.878$ GeV. The
lightest solution is on shell. At off-shell benchmarks with
$M_V=30,46,60$ GeV, the full matrix element at 13 TeV gives
$t\bar t+\mathrm{MET}$ cross sections of $0.033$, $0.041$, and $1.13$
fb, respectively, for truth-level $p_T^{\rm miss}>250$ GeV. Limits in
the CMS all-hadronic two-$b$-tag category also require the acceptance
after top decays, the binned signal yields, and the background
correlations. [cmstop](#ref-cmstop)

### Single-top sensitivity

For the single-top channel $pp\to tj\chi_1\chi_2$, we estimate the
expected sensitivity in the 15 bins of the CMS AH $1b\,1\mathrm{FJ}$
category. We approximate the backgrounds with the published central
values and bin uncertainties from the fit with a 100 GeV scalar signal,
keeping only the diagonal covariance. For the signal we use truth-level
cuts, simplified top decays, and approximate $b$ tagging. At
$(M_V,g_t)=(60\,\mathrm{GeV},0.399)$, the cuts
$\sqrt{\hat s}<1.5,1.0,0.75$ TeV give median expected limits of
$0.052,0.337,3.43$, respectively. The strong dependence on this cut is
related to the charged weak current connecting up- and down-type quarks
with unequal vector couplings. We use the cut variation to test the
contribution of high-energy events. A quantitative exclusion requires an
electroweak completion and validation of the reconstructed signal and
background constraints. [kahlhoefer2016](#ref-kahlhoefer2016) · [cmstop](#ref-cmstop) · [cmsahdata](#ref-cmsahdata)

<a id="fig:single_top_cut"></a>

![](./figures/08_top_branches_and_energy.png)

The left panel shows <span
class="math inline"><em>M</em><sub><em>V</em></sub> − <em>m</em><sub>1</sub> − <em>m</em><sub>2</sub></span>
at representative central relic solutions. The right panel shows how the
expected single-top sensitivity varies with the partonic-energy cut for
on-shell solutions. The charged weak current connects top and bottom
quarks with different <span class="math inline"><em>V</em></span>
couplings, so the high-energy behavior of longitudinal weak-boson
amplitudes depends on cancellations in the electroweak completion.
Varying the cut probes that dependence. Missing markers at 0.75 TeV
indicate samples for which the approximate likelihood gives no finite
limit.

### Low-mass branches and truth-level rates

<a id="fig:low_mass"></a>

![](./figures/d01_light_top_branches.png)

Independent low-mass scan with tree-level yield matching.
Colors identify the relic branches found within the Planck <span
class="math inline">±2<em>σ</em></span> band. Purple indicates that both
on-shell and off-shell solutions are present.

<a id="fig:top_truth_met"></a>

![](./figures/d02_top_truth_met.png)

Cross sections in fb above different truth-level MET
thresholds for dark-pair production with <span
class="math inline"><em>t</em><em>j</em></span>, <span
class="math inline"><em>t</em><em>W</em></span>, or <span
class="math inline"><em>t</em><em>t̄</em></span> at four on-shell or
off-shell benchmarks. Deriving experimental limits requires simulating
top decays and validating reconstruction and selection efficiencies at
the same parameter points.

For $m_\chi\ge20$ GeV and $M_V\le40.001$ GeV, dark-pair production
proceeds through an off-shell mediator. To derive a top-pair exclusion
from fully simulated samples, one must check $m_\chi$, the decay
threshold, and the template normalization at each point with a common
reference yield. The published CMS backgrounds come from a simultaneous
fit that includes signal-region data. An observed recast requires
background constraints independent of the signal-region counts.
[cmstop](#ref-cmstop)

## References

<a id="ref-lz2026"></a>

[lz2026] [Search for Dark Matter Particle Interactions in an Extended Nuclear Recoil Energy Window with the LUX-ZEPLIN (LZ) Experiment](https://arxiv.org/abs/2609.02823). 2026.

<a id="ref-gemmell2026"></a>

[gemmell2026] [A Simple Dark Matter Model to Explain the LZ Event and Galactic Center Excess](https://arxiv.org/abs/2609.26570). 2026.

<a id="ref-du2026"></a>

[du2026] [Pseudo-Dirac Inelastic Dark Matter in the Leptophobic $U(1)_B$ Model: Confronting the LUX-ZEPLIN High-Recoil Event with Collider Searches](https://arxiv.org/abs/2609.07225). 2026.

<a id="ref-cox2016"></a>

[cox2016] [Novel Collider and Dark Matter Phenomenology of a Top-philic $Z'$](https://doi.org/10.1007/JHEP06(2016)110). 2016.

<a id="ref-kahlhoefer2016"></a>

[kahlhoefer2016] [Implications of Unitarity and Gauge Invariance for Simplified Dark Matter Models](https://doi.org/10.1007/JHEP02(2016)016). 2016.

<a id="ref-deramo2016"></a>

[deramo2016] [You Can Hide but You Have to Run: Direct Detection with Vector Mediators](https://doi.org/10.1007/JHEP08(2016)111). 2016.

<a id="ref-lzdata"></a>

[lzdata] [extended nuclear-recoil search, HEPData record](https://doi.org/10.17182/hepdata.182472.v1). 2026.

<a id="ref-griest1991"></a>

[griest1991] [Three Exceptions in the Calculation of Relic Abundances](https://doi.org/10.1103/PhysRevD.43.3191). 1991.

<a id="ref-gondolo1991"></a>

[gondolo1991] [Cosmic Abundances of Stable Particles: Improved Analysis](https://doi.org/10.1016/0550-3213(91)90438-4). 1991.

<a id="ref-micromegas2024"></a>

[micromegas2024] [micrOMEGAs 6.0: N-Component Dark Matter](https://doi.org/10.1016/j.cpc.2024.109133). 2024.

<a id="ref-planck2020"></a>

[planck2020] [Planck 2018 Results. VI. Cosmological Parameters](https://doi.org/10.1051/0004-6361/201833910). 2020.

<a id="ref-alwall2014"></a>

[alwall2014] [The Automated Computation of Tree-Level and Next-to-Leading Order Differential Cross Sections, and Their Matching to Parton Shower Simulations](https://doi.org/10.1007/JHEP07(2014)079). 2014.

<a id="ref-hirschi2015"></a>

[hirschi2015] [Automated Event Generation for Loop-Induced Processes](https://doi.org/10.1007/JHEP10(2015)146). 2015.

<a id="ref-pythia2022"></a>

[pythia2022] [A Comprehensive Guide to the Physics and Usage of PYTHIA 8.3](https://doi.org/10.21468/SciPostPhysCodeb.8). 2022.

<a id="ref-delphes2014"></a>

[delphes2014] [DELPHES 3: A Modular Framework for Fast Simulation of a Generic Collider Experiment](https://doi.org/10.1007/JHEP02(2014)057). 2014.

<a id="ref-cmsmonojet"></a>

[cmsmonojet] [Search for New Particles in Events with Energetic Jets and Large Missing Transverse Momentum in Proton-Proton Collisions at $\sqrt{s}=13$ TeV](https://doi.org/10.1007/JHEP11(2021)153). 2021.

<a id="ref-albert2021"></a>

[albert2021] [Implementation of a Search for New Phenomena in Events Featuring Energetic Jets and Missing Transverse Energy (137 fb$^{-1}$, 13 TeV, CMS EXO-20-004)](https://doi.org/10.14428/DVN/IRF7ZL). 2021.

<a id="ref-cmscovariance"></a>

[cmscovariance] [public monojet background covariance, HEPData Table 14](https://doi.org/10.17182/hepdata.106115.v2/t14). 2021.

<a id="ref-cmsyields"></a>

[cmsyields] [observed and background yields, HEPData Table 15](https://doi.org/10.17182/hepdata.106115.v2/t15). 2021.

<a id="ref-cmssimplified"></a>

[cmssimplified] [Simplified Likelihood for the Re-Interpretation of Public CMS Results](https://cds.cern.ch/record/2242860). 2017.

<a id="ref-cowan2011"></a>

[cowan2011] [Asymptotic Formulae for Likelihood-Based Tests of New Physics](https://doi.org/10.1140/epjc/s10052-011-1554-0). 2011.

<a id="ref-read2002"></a>

[read2002] [Presentation of Search Results: The $CL_s$ Technique](https://doi.org/10.1088/0954-3899/28/10/313). 2002.

<a id="ref-forner2026"></a>

[forner2026] [Renormalization of $U(1)$ Gauge Boson Kinetic Mixing](https://doi.org/10.1103/tqw9-zm9x). 2026.

<a id="ref-cmstop"></a>

[cmstop] [Search for Dark Matter Produced in Association with One or Two Top Quarks in Proton-Proton Collisions at $\sqrt{s}=13$ TeV](https://doi.org/10.1007/JHEP08(2025)085). 2025.

<a id="ref-cmsahdata"></a>

[cmsahdata] [AH $1b\,1\mathrm{FJ}$ post-fit MET spectrum, HEPData Table 2](https://doi.org/10.17182/hepdata.154755.v1/t2). 2025.

<a id="ref-carrillo2022"></a>

[carrillo2022] [Cosmology and Signals of Light Pseudo-Dirac Dark Matter](https://doi.org/10.1007/JHEP04(2022)060). 2022.

<a id="ref-cmssignal"></a>

[cmssignal] [public spin-1 signal templates, HEPData Table 1](https://doi.org/10.17182/hepdata.106115.v2/t1). 2021.

<a id="ref-cmscutflow"></a>

[cmscutflow] [public monojet cutflow, HEPData Table 20](https://doi.org/10.17182/hepdata.106115.v2/t20). 2021.

> [!tip] 新增 A04 参考文献
> 新增 Engel 1991 核形状因子文献。

<a id="ref-engel1991"></a>

[engel1991] [Nuclear form factors and WIMP-nucleus elastic scattering](https://doi.org/10.1016/0370-2693(91)90712-Y). 1991.

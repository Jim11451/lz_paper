# Xenon Recoils and LHC Missing-Momentum Tests of Exothermic Pseudo-Dirac Dark Matter

**Authors and affiliations to be confirmed**

## Abstract

We study exothermic pseudo-Dirac dark matter coupled to quarks through a mass-weighted vector mediator. The suppression of light-quark couplings makes xenon recoils and collider production sensitive to different flavors. We match the truth-level event yield of a reference model motivated by the high-energy LZ recoil candidate, then solve the Planck relic-density equation on each on-shell and off-shell branch. We reconstruct CMS-only 95% CL signal-strength limits on the reference-yield slice from the 66 public CMS Run 2 monojet bins. For small low-energy photon mixing and a narrow mediator, the monojet data exclude a subset of the on-shell solutions in this recast. Three sensitive benchmarks have observed $\mu_{95}=0.607$, $0.340$, and $0.273$, and all three limits remain below unity when the target LZ yield is varied by $25\%$ in either direction. These benchmarks have large top couplings, and two lie at the upper coupling boundary of the scan. We quantify separately the effects of low-energy mixing, the local excited-state fraction, the relic-density measurement, and finite signal statistics. We also study the complementary reach of top-associated production at lower mediator masses.

## 1. Introduction

The LUX-ZEPLIN (LZ) Collaboration reported a nuclear-recoil-like event compatible with $E_R=248\pm23_{\rm stat}\pm23_{\rm syst}$ keV in an extended recoil window with an exposure of $2.84$ tonne yr. The global significance of the departure from the background-only hypothesis was $2.6\sigma$ over the model set tested by LZ, with a maximum local significance of $3.4\sigma$. Exothermic inelastic scattering releases energy as the heavier dark state transitions to the lighter one, allowing dark matter with a mass of tens of GeV to produce energetic nuclear recoils. Gemmell, Hooper, and Krnjaic studied this mechanism and the Galactic Center gamma-ray excess with a flavor-universal quark vector current. We use their exothermic benchmark to define a reference yield and study xenon recoils, thermal freeze-out, and LHC signatures. [1](https://arxiv.org/html/2609.02823) · [2](https://arxiv.org/html/2609.26570v1)

Collider sensitivity depends on both the flavor structure and the invisible decay threshold of the mediator. Du, Huang, and Xie studied endothermic scattering in a gauge-complete leptophobic $U(1)_B$ model. The two-body invisible decay is closed at their $1.44$ TeV benchmark, which is primarily tested by dijet searches. Loop-induced and top-associated production of top-philic vector mediators have also been studied independently. Here we examine the overlap of two conditions: the low-energy coupling product required by exothermic xenon scattering and the missing-momentum signatures driven by heavy-flavor production for mediator masses from tens to about two hundred GeV. We apply the relic and collider conditions at the same four-dimensional parameter points and track off-shell solutions in the two-dimensional projection. [3](https://arxiv.org/html/2609.07225) · [4](https://arxiv.org/abs/1512.00471)

## 2. Effective model

We take $m_1=m_\chi$ and $m_2=m_\chi+\Delta m$. A spin-1 mediator $V_\mu$ couples to the off-diagonal vector current of the two dark states. The benchmark interaction in the electroweak-broken basis is

$$
\mathcal L_{\rm int}=V_\mu\left[\sum_{q=u,d,s,c,b,t}g_t\frac{\widehat m_q}{172\,\mathrm{GeV}}\bar q\gamma^\mu q
+i\frac{g_\chi}{2}\bar\chi_1\gamma^\mu\chi_2\right],\qquad
\widehat m_q=(0.0022,0.0047,0.096,1.27,4.18,172)\,\mathrm{GeV}.
\tag{1}
$$

Here $g_t$ is the $Vt\bar t$ vertex coefficient at zero mixing, and the transition vertex has magnitude $g_\chi/2$. We work with an effective model in the electroweak broken phase and take $g_{Vq}\propto\widehat m_q$ as a phenomenological flavor ansatz. The reference masses $\widehat m_q$ fix the flavor ratios by assumption. The charges, fermion mass generation, and matching in a complete $U(1)_X$ theory require independent specification. For purely vector couplings, unequal up- and down-type coefficients within a left-handed weak doublet require electroweak-breaking operators or additional mixing. [5](https://arxiv.org/abs/1510.02110) · [6](https://arxiv.org/abs/1605.04917)

Given the low-energy matching coefficients, the recoil kinematics and leading coherent rate follow directly from Eq. (1). The closed-quark-loop $gg\to gV$ amplitude retained here satisfies the QCD Ward identity with the specified vertices. The numerical relic-density and monojet predictions are conditional on the stated operators, particle content, and open channels. An electroweak completion can alter recoil amplitudes, annihilation, mediator widths, and production through additional $V$–$Z$ mixing, matching operators, or new particles. Processes with charged weak currents also depend on electroweak cancellations in longitudinal amplitudes. Section 7 examines this dependence. [5](https://arxiv.org/abs/1510.02110) · [6](https://arxiv.org/abs/1605.04917)

| Quantity | Benchmark or range |
|---|---|
| Mass splitting and present local excited fraction | $\Delta m=1$ MeV, $f_2=0.5$ |
| Local dark matter density | $\rho_\chi=0.3\ \mathrm{GeV\,cm^{-3}}$ |
| Halo speeds $(v_0,v_E,v_{\rm esc})$ | $(238,254,544)\ \mathrm{km\,s^{-1}}$ |
| Dark mass and dark coupling | $20\le m_\chi\le100$ GeV, $0.10\le g_\chi\le1.50$ |
| CMS monojet grid | $72\le M_V\le200$ GeV, $0.1\le g_t\le\sqrt{4\pi}$ |
| On-shell template requirements | $M_V-m_1-m_2\ge5\Gamma_V$, $\Gamma_V/M_V<0.03$ |

The scan boundary $g_t=\sqrt{4\pi}$ corresponds to $g_t^2/(4\pi)=1$. Results near it merit a separate assessment of higher-order effects. The lower-mass top-associated study uses an independent branch scan over $M_V=20$–100 GeV.

## 3. Xenon recoils and the LZ yield condition

At leading order in the vector-charge matching, $f_p=2g_{Vu}+g_{Vd}$ and $f_n=g_{Vu}+2g_{Vd}$, giving $f_p/g_t=5.29\times10^{-5}$ and $f_n/g_t=6.74\times10^{-5}$. The coherent charge of a nucleus of mass number $A$ is $Q_A=Zf_p+(A-Z)f_n$. With nuclear mass $m_A$ and reduced mass $\mu_A=m_2m_A/(m_2+m_A)$, the minimum incident speed and the differential truth-level rate are

$$
\begin{aligned}
v_{\min}(E_R)&=\frac{|m_A E_R/\mu_A-\Delta m|}{\sqrt{2m_A E_R}},\
\frac{dR}{dE_R}&=\frac{f_2\rho_\chi}{m_2}\sum_A w_A\,
\frac{(g_\chi Q_A/2)^2 F_A^2(q)}{2\pi(M_V^2+q^2)^2}\,\eta(v_{\min}),
\qquad q^2=2m_AE_R .
\end{aligned}
\tag{2}
$$

Here $w_A$ are the natural xenon isotope mass fractions, $F_A$ comes from a numerical two-parameter Fermi density, and $\eta(v_{\min})=\int_{v>v_{\min}}d^3v\,f_{\rm lab}(\mathbf v)/v$. The numerical calculation uses the degenerate-mass approximation in the flux and reduced mass and keeps the splitting in $v_{\min}$. At zero incident speed the accessible recoil energy is $E_R^\star=\Delta m\,\mu_A/m_A$. The velocity distribution and nuclear form factors also determine the position of the spectral maximum. [2](https://arxiv.org/html/2609.26570v1) · [6](https://arxiv.org/abs/1605.04917)

We reproduce the benchmark in Fig. 6 of Ref. [2] at $(m_\chi,M_V,g_B,g_\chi)=(35\,\mathrm{GeV},30\,\mathrm{GeV},1.46\times10^{-5},0.32)$ with $g_{Vq}=g_B/6$. We obtain $N_0=1.12044$ truth-level events in $[5.4,269.9]$ keV and $7.39\times10^{-4}$ in the $[350,675]$ keV sideband. The reference paper obtains about 1 and $8\times10^{-4}$ after folding the response. We require the new flavor structure to yield $N_0$ in the same truth-level calculation. The LZ science sample contains 1710 events, and its full analysis uses corrected S1 and S2. Our equal-rate condition transfers the signal scale motivated by the candidate into the model parameters. [1](https://arxiv.org/html/2609.02823) · [2](https://arxiv.org/html/2609.26570v1) · [7](https://doi.org/10.17182/hepdata.182472.v1)

![Figure 1. Nuclear recoil spectra in natural xenon](figures/01_xenon_recoil.png)

**Figure 1.** Truth-level differential rates for the reference model and the mass-weighted vector model, in events kg$^{-1}$ day$^{-1}$ keV$^{-1}$. Both use $m_\chi=35$ GeV and $M_V=30$ GeV. The equal-rate solution uses $g_t=0.12763$ and $g_\chi=0.29779$. The vertical line marks the reconstructed recoil energy of the LZ candidate. Shading indicates the integration windows.

In the contact limit $q\ll M_V$, the rate depends on the coupling combination $\kappa=g_tg_\chi/M_V^2$. Let $\kappa_0(m_\chi)$ denote the tree-level equal-rate solution for the baseline halo and $f_2=0.5$. Define $r=N_{\rm ROI}^{\rm truth}/N_0$ and let $K_\gamma$ denote the ratio of the photon-corrected to the tree-level rate at fixed parameters. Then

$$
\kappa=\kappa_0(m_\chi)\sqrt{\frac{r}{K_\gamma(m_\chi,d_\gamma)}\frac{0.5}{f_2}},\qquad
g_\chi=\frac{M_V^2}{g_t}\kappa.
\tag{3}
$$

Integrating at each mass gives $\kappa_0(35,40,44\,\mathrm{GeV})=(4.223,5.665,7.202)\times10^{-5}\ \mathrm{GeV}^{-2}$. Increasing the dark matter mass moves the characteristic recoil toward the upper edge of the window and requires a larger coupling product to maintain the same yield. At fixed spectral shape the normalization depends on $r/f_2$. **The value $r=1$ specifies the reference truth yield motivated by the LZ candidate. The prescribed variation $r\in[0.75,1.25]$ has no LZ confidence-level assignment.** The 95% CL limits reported here come from the CMS monojet likelihood in Section 5.

## 4. Thermal abundance and physical branches

We assume a standard thermal history and chemical equilibrium between the two states during freeze-out. Their total number density $n=n_1+n_2$ obeys

$$
\dot n+3Hn=-\langle\sigma_{\rm eff}v\rangle(n^2-n_{\rm eq}^2),\qquad
\langle\sigma_{\rm eff}v\rangle=\sum_{i,j=1,2}\frac{n_i^{\rm eq}n_j^{\rm eq}}{(n^{\rm eq})^2}\langle\sigma_{ij}v\rangle .
\tag{4}
$$

Since $\Delta m\ll T_f$, the two states have nearly equal equilibrium weights near freeze-out. We solve for the total abundance with CalcHEP and micrOMEGAs 7.1.4, using `Fast=0` and `Beps=1e-9`, and require both states together to saturate the Planck abundance $\Omega_ch^2=0.1200\pm0.0012$. Coannihilation through $\chi_1\chi_2\to V^*\to b\bar b,c\bar c$ makes the relic density sensitive to $M_V$ near the resonance. At one on-shell benchmark with $m_\chi=35$ GeV, $b\bar b$ contributes about $92\%$ of the coannihilation rate. When same-state annihilation to $VV$ becomes kinematically accessible, the dark final state can control the abundance. [8](https://doi.org/10.1103/PhysRevD.43.3191) · [9](https://doi.org/10.1016/0550-3213%2891%2990438-4) · [10](https://arxiv.org/abs/2312.14894) · [11](https://arxiv.org/abs/1807.06209)

At fixed $m_\chi$, imposing Eq. (3) gives the following coupling and propagator factor for coannihilation:

$$
\frac{(g_tg_\chi)^2}{(M_V^2-s)^2+M_V^2\Gamma_V^2}
=\frac{\kappa^2 M_V^4}{(M_V^2-s)^2+M_V^2\Gamma_V^2}.
\tag{5}
$$

Changing $g_\chi$ affects the thermal average through the width, while changing $M_V$ also moves the pole relative to the thermally accessible region. For $m_\chi=35$ GeV, $g_\chi=0.18$, and $M_V\simeq87.56$ GeV, the local logarithmic slope of the abundance is about $0.158\ \mathrm{GeV}^{-1}$. The Planck $\pm2\sigma$ interval maps to $M_V\simeq87.43$–$87.68$ GeV in this slice. Once $m_\chi$ is allowed to vary, the two conditions define multiple two-dimensional solution surfaces in the four-dimensional parameter space. A given $(M_V,g_t)$ coordinate can have more than one root.

![Figure 2. Relic-density slope and resonant thermal average](figures/02_relic_slope.png)

**Figure 2.** The left panel fixes $m_\chi=35$ GeV. The right panel shows the contribution of the pole neighborhood to the instantaneous thermal average. Open symbols mark the freeze-out temperatures at the individual points.

The main grid uses $r=1$, $f_2=0.5$, and $d_\gamma(0)=0$, retaining the finite spacelike $c,b,t$ photon contribution to the recoil. For each $(M_V,g_t)$, we eliminate $g_\chi$ using Eq. (3) and search for crossings of $\Omega_\chi h^2=0.1200$ separately on either side of $M_V-2m_\chi-\Delta m=0$. We use 35 mediator masses and 29 top couplings. Mass brackets are spaced by at most $1.10$ GeV with additional samples near thresholds. At 11 representative coordinates we propagate the abundance error by solving separately at $0.1176,0.1188,0.1200,0.1212,0.1224$. Each root retains its own parameters and limits.

The propagation corresponds to a Gaussian measurement term, $-2\ln\mathcal L_\Omega=[(\Omega_\chi h^2-0.1200)/0.0012]^2+\mathrm{const.}$. Each abundance target is retained separately if a branch disappears or is truncated by the scan boundaries. For example, at $M_V=150.4$ GeV and $g_t=1.260$, the central solution for $r=2$ requires $g_\chi=1.498$, while the two lower abundance targets have no root within $g_\chi\le1.50$. The Gaussian term represents the observational uncertainty on the abundance.

## 5. LHC production, reconstruction, and statistical analysis

### 5.1 Truth cross sections and reconstruction

The monojet signal includes $q\bar q\to gV$, $qg\to qV$, and charge-conjugate tree amplitudes, together with the finite closed-quark-loop amplitude $gg\to gV$. The three-point $gg\to V$ amplitude cancels for a pure vector current, while the four-point amplitude with an associated gluon can be nonzero. We add the tree and gluon-loop contributions, which have distinct initial states at the orders retained. Associated top-pair production $pp\to t\bar tV$ is calculated at tree level. We use MadGraph5_aMC@NLO 3.6.6 at 13 TeV with `nn23lo1` and 11 $M_V$ nodes. In the narrow-width approximation the rate for final state $X$ is

$$
\sigma_X=\sigma_X^{\rm prod}(M_V;g_t=1)\,g_t^2\,\mathrm{BR}(V\to\chi_1\chi_2).
\tag{6}
$$

For a loose jet selection of $p_T^j>20$ GeV, the $j+\mathrm{MET}$ truth cross section becomes comparable to inclusive $t\bar t+\mathrm{MET}$ near $M_V\simeq118$ GeV. With a common truth requirement $p_T^{\rm miss}>200$ GeV, the ratio $\sigma(j+\mathrm{MET})/\sigma(t\bar t+\mathrm{MET})$ is $0.135$–$0.149$. For $(m_\chi,M_V,g_t,g_\chi)=(35,87.18,1.070,0.30)$ the two cross sections are $0.166$ and $1.23$ pb, respectively. The tops are stable in this comparison and $p_T^{\rm miss}=p_T(V)$. Decays, reconstructed selections, and backgrounds determine the experimental sensitivity. [4](https://arxiv.org/abs/1512.00471) · [12](https://arxiv.org/abs/1405.0301) · [13](https://arxiv.org/abs/1507.00020)

![Figure 3. Truth cross sections after a hard MET requirement](figures/03_hard_met_cross_sections.png)

**Figure 3.** The two final states and their ratio for $m_\chi=35$ GeV and $g_\chi=0.30$, with cross sections in pb. The dashed curve is the tree-level LZ equal-rate condition. The monojet prediction includes the leading tree channels and the $gg\to gV$ loop contribution.

We use Pythia 8.312 and Delphes 3.5.0 to reconstruct the monojet templates, treating the on-shell $V$ as invisible. The tree and loop samples start at generator-level $p_T^j=100$ GeV. Separate hard samples begin at 350 and 480 GeV, respectively, and are combined in mutually exclusive generator-level intervals. An additional 230 GeV boundary stratifies the loop sample at $M_V=120$ GeV. The reconstructed selection approximates CMS EXO-20-004, with a leading AK4 jet of $p_T>100$ GeV and $|\eta|<2.4$, $p_T^{\rm miss}>250$ GeV, azimuthal cuts, lepton, photon and heavy-flavor-related vetoes, and the 2018 HEM treatment. The three years provide about $137\ \mathrm{fb}^{-1}$, with 22 monojet signal bins per year. [14](https://arxiv.org/abs/2203.11601) · [15](https://arxiv.org/abs/1307.6346) · [16](https://arxiv.org/abs/2107.13021) · [17](https://doi.org/10.14428/DVN/IRF7ZL)

### 5.2 The 66-bin profile likelihood

We use the public observations $n_i$, the background-only control-region prediction $\mathbf b$, its covariance $C_b$, and the signal $\mathbf s$ at each point to construct

$$
\mathcal L(\mu,\mathbf b',\mathbf s')=
\prod_{i=1}^{66}{\rm Pois}(n_i\mid b_i'+\mu s_i')
\,G(\mathbf b';\mathbf b,C_b)\,G(\mathbf s';\mathbf s,C_s).
\tag{7}
$$

Signal yields are constrained to be nonnegative and Poisson means to be positive. The signal covariance $C_s$ includes the multinomial covariance of the simulated counts, cross-section integration errors, and a common $1.6\%$ signal luminosity nuisance. Correlations are retained when the same simulated events contribute to different years. Yields are interpolated linearly between mass nodes and covariances from independent samples are interpolated with squared weights. The nominal prediction for each branch corresponds to $\mu=1$. We obtain $\mu_{95}$ using a one-sided profile-likelihood statistic and asymptotic $CL_s=0.05$. The expected limits use a background-only Asimov data set, and the observed limits use the measured $n_i$ with a conditional background Asimov data set. The five expected quantiles describe background fluctuations. The relic-density uncertainty is propagated by recalculating each physical root. [18](https://doi.org/10.17182/hepdata.106115.v2/t14) · [19](https://doi.org/10.17182/hepdata.106115.v2/t15) · [20](https://cds.cern.ch/record/2242860) · [21](https://arxiv.org/abs/1007.1727) · [22](https://doi.org/10.1088/0954-3899/28/10/313)

We use $\tilde q_\mu=-2\ln[\mathcal L(\mu,\widehat{\widehat{\boldsymbol\theta}}_\mu)/\mathcal L(\widehat\mu,\widehat{\boldsymbol\theta})]$, set it to zero when $\widehat\mu>\mu$, and constrain $\widehat\mu\ge0$. With $a=\sqrt{\tilde q_{\mu,A}}$, the observed asymptotic statistic is

$$
CL_s(\mu)=\frac{\Phi(-z_\mu)}{\Phi(a-z_\mu)},\qquad
z_\mu=\begin{cases}\sqrt{\tilde q_\mu},&\tilde q_\mu\le a^2,\\
(\tilde q_\mu+a^2)/(2a),&\tilde q_\mu>a^2.\end{cases}
\tag{8}
$$

For the expected bands, we solve $a=z-\Phi^{-1}[0.05\Phi(z)]$ on the nominal background Asimov data set for $z=-2,-1,0,1,2$. [21](https://arxiv.org/abs/1007.1727)

Appendix C validates the 66-bin statistical reconstruction with official CMS vector templates and checks the cutflow, acceptance, and MET spectra with independent simulation. The published expected and observed vector mass boundaries are 2.198 and 1.957 TeV. The 66-bin reconstruction gives 2.208 and 1.941 TeV. Pointwise observed limits at low mediator masses and the absolute yields from independent simulation show larger differences. We therefore report a recast of the public likelihood inputs together with its validation range.

## 6. Monojet results and stability

### 6.1 Branch-resolved results at the central relic abundance

![Figure 4. CMS monojet limits at the reference yield and central relic abundance](figures/04_cms_central_plane.png)

**Figure 4.** At the reference yield $r=1$ with $f_2=0.5$ and $d_\gamma(0)=0$, Eq. (3) fixes $g_\chi=g_\chi(m_\chi;M_V,g_t)$. Let $\mathcal D_\chi$ be the set of masses $20\le m_\chi\le100$ GeV for which Eq. (3) gives $0.10\le g_\chi\le1.50$. At each $(M_V,g_t)$ we define

$$
\mathcal S_{\rm on}(M_V,g_t)=\left\{m_\chi\in\mathcal D_\chi:\ \Omega_\chi h^2=0.1200,\quad M_V-m_1-m_2\ge5\Gamma_V,\quad \Gamma_V/M_V<0.03\right\}.
$$

Where $\mathcal S_{\rm on}$ contains exactly one solution, the color gives its CMS-only 95% CL limit $\mu_{95}$. The black contour denotes $\mu_{95}=1$. A gray cell has no solution to color in this scan. The plotted value applies only to that on-shell branch. Other dark-mass solutions at the same coordinate require separate limits, with the full $pp\to j\chi_1\chi_2$ amplitude for off-shell solutions.

We find 434 central relic solutions on the 1,015-point grid. Each is a unique on-shell root satisfying the template requirements. With the reference templates in Fig. 4, the expected and observed limits fall below unity at 208 and 151 points, respectively. The lowest sampled masses with $\mu_{95}<1$ are 92 and 104 GeV. Both the counts and the first crossings depend on the grid spacing. An interior point at $(M_V,g_t)=(112\,\mathrm{GeV},2.747)$ has $(m_\chi,g_\chi)=(40.055\,\mathrm{GeV},0.260)$ and expected and observed limits of $0.513$ and $0.540$. The smallest observed limit with the reference templates is $0.181$ at $(200\,\mathrm{GeV},\sqrt{4\pi})$. Refitting these roots with three pooled template nodes gives 162 observed points below unity, with 11 grid points crossing the boundary. Appendix C gives the comparison. Section 7 discusses off-shell roots in the lower-mass extension.

At some masses the sensitive interval has both lower and upper boundaries in $g_t$. At fixed masses and LZ yield, $g_\chi\propto g_t^{-1}$, so $\Gamma_{\chi_1\chi_2}=A/g_t^2$ and $\Gamma_{\rm SM}=Bg_t^2$, where $A,B$ are fixed on the slice. The signal factor in Eq. (6) becomes $g_t^2/(1+(B/A)g_t^4)$ and peaks where the two partial widths are equal. At larger $g_t$, the decreasing invisible branching fraction can offset the increasing production rate.

| $M_V$ [GeV] | $g_t$ | $m_\chi$ [GeV] | $g_\chi$ | Expected $\mu_{95}$ | Observed $\mu_{95}$ | Observed for $r=0.75$–$1.25$ |
|---:|---:|---:|---:|---:|---:|---:|
| 80 | 0.503 | 33.027 | 0.482 | 6.891 | 15.58 | 15.55–15.64 |
| 100 | 1.264 | 38.065 | 0.400 | 1.333 | 2.305 | 2.276–2.352 |
| 120 | 3.073 | 41.116 | 0.284 | 0.412 | 0.607 | 0.570–0.664 |
| 150.4 | 1.260 | 43.896 | 1.286 | 0.986 | 1.822 | 1.820–1.824 |
| 150.4 | 3.545 | 43.896 | 0.457 | 0.184 | 0.340 | 0.329–0.357 |
| 190.4 | 3.545 | 45.854 | 0.823 | 0.219 | 0.273 | 0.270–0.277 |

**Table 2.** Representative on-shell branches. The central columns use $r=1$, $f_2=0.5$, $d_\gamma(0)=0$, and the central Planck value. The last column re-solves the abundance for each rate target. The value $g_t=3.545$ is the scan boundary. The point at $M_V=150.4$ GeV and $g_t=1.260$ illustrates how the expected sensitivity can differ from the observed exclusion.

![Figure 5. CMS background fluctuations and the propagated abundance uncertainty](figures/05_collider_uncertainties.png)

**Figure 5.** Blue intervals show the $\pm1\sigma$ and $\pm2\sigma$ expected quantiles from background fluctuations. Brown marks show the effect of the Planck $\pm2\sigma$ measurement uncertainty on the median expected limit. Red diamonds mark observed limits. The single-top panel uses the $\sqrt{\hat s}<1$ TeV truth-level proxy described in Section 7.

At the representative points, the Planck measurement uncertainty moves the median monojet $\mu_{95}$ by at most $0.44\%$. Profiling the finite signal statistics and the luminosity nuisance weakens the median limits by about $1.4\%$–$6.6\%$ relative to fixed templates. For the 120 GeV point, the propagated relic uncertainty gives $0.41056$–$0.41415$, while the $1\sigma$ expected band from background fluctuations is $[0.295,0.581]$. These intervals quantify different sources. Model-specific covariance from scales, PDFs, production matching, and detector efficiencies remains to be determined.

### 6.2 Low-energy photon mixing, the rate target, and the excited fraction

We define $d_\gamma=e\epsilon_\gamma/g_t$, with positive $d_\gamma$ increasing the proton vertex by $g_t d_\gamma$. The constant kinetic-mixing term $d_\gamma(0)$ is an independent matching input. At fixed quark couplings the charged-quark loops determine a finite momentum-dependent difference. In a common Helm approximation, $Q_A/g_t$ is shifted by $Z[d_\gamma(0)+\delta d_{cbt}(-q^2)]$. For $^{131}$Xe the tree-level charge is $Q_A/g_t\simeq8.05\times10^{-3}$, which leads to cancellation near $d_\gamma(0)\simeq-1.49\times10^{-4}$. At $m_\chi=35$ GeV, $d_\gamma(0)=\pm7\times10^{-6}$ changes the rate to $0.908$–$1.095$ times the tree-level rate and gives $\kappa/\kappa_0=0.956$–$1.050$. Near cancellation, the required $\kappa/\kappa_0$ is about 56.5. We find no central root in that scenario at the 11 test coordinates within the coupling ranges used here. [6](https://arxiv.org/abs/1605.04917) · [23](https://doi.org/10.1103/tqw9-zm9x)

![Figure 6. Signed low-energy mixing and equal-rate spectral shapes](figures/06_matching_and_spectra.png)

**Figure 6.** The left panel shows how low-energy mixing changes the coupling required to reproduce the target yield. The right panel compares shapes at a common truth-level yield. After smoothing with a constant 32.5 keV Gaussian, the signal densities near 248 keV at $m_\chi=20,35,44$ GeV are approximately $2.75\times10^{-4}$, $4.54\times10^{-3}$, and $6.98\times10^{-3}$ events/keV. This energy proxy omits the LZ S1/S2 response and backgrounds.

For the tested rate targets in $r=0.75$–$1.25$, the median monojet limit changes by at most $9.4\%$. Reducing $f_2$ alone to 0.45 or 0.30 produces maximum shifts of $3.0\%$ and $12.8\%$, respectively. Varying only the low-energy mixing within $|d_\gamma(0)|\le7\times10^{-6}$ moves the median by at most $2.8\%$. For the 120 GeV benchmark, $(d_\gamma(0),r,f_2)=(+7\times10^{-6},0.75,0.50)$ and $(-7\times10^{-6},1.25,0.45)$ give median limits of $0.465$ and $0.367$. These are fixed scenario variations. The present excited fraction also depends on late downscattering and the lifetime of the excited state, as discussed in Appendix A.

![Figure 7. Variation of the truth-level LZ yield](figures/07_lz_rate_variation.png)

**Figure 7.** Each on-shell point is recalculated at the central Planck abundance for every rate target. The shaded interval $r=0.75$–$1.25$ is prescribed for the normalization test and corresponds to $0.84$–$1.40$ expected truth-level events. The CMS limit is calculated separately at each fixed rate target.

## 7. Top-associated production

The hierarchy between $g_t$ and the light-quark vertices motivates a separate study of $pp\to t\bar tV^{(*)}\to t\bar t\chi_1\chi_2$. On-shell enhancement is possible for $M_V>2m_\chi+\Delta m$. Below threshold the four-body final state must be generated directly. In the low-mass scan, $(M_V,g_t)=(48\,\mathrm{GeV},0.252)$ has central roots at $m_\chi=20.445,25.260,45.878$ GeV. Only the first is on shell. For three representative off-shell points the full matrix element at 13 TeV gives $t\bar t+\mathrm{MET}$ cross sections of $0.033$, $0.041$, and $1.13$ fb after a truth cut $p_T^{\rm miss}>250$ GeV at $M_V=30,46,60$ GeV, respectively. Across the threshold, the selected dark mass and the propagator must be checked for each point. Quantitative limits in the CMS all-hadronic two-$b$-tag category require top-decay acceptances, binned signals, and correlated backgrounds. [24](https://arxiv.org/abs/2505.05300)

For $pp\to tj\chi_1\chi_2$, we use the CMS AH $1b\,1\mathrm{FJ}$ category for a 15-bin expected sensitivity estimate. We use the public background central values and bin errors from the fit with a 100 GeV scalar signal as a proxy, retaining only the diagonal covariance. Signal yields use truth-level selections, simplified top decays, and approximate $b$ tagging. The result depends strongly on the partonic-energy cut. At $(M_V,g_t)=(60\,\mathrm{GeV},0.399)$, the cuts $\sqrt{\hat s}<1.5,1.0,0.75$ TeV give median limits of $0.052,0.337,3.43$, respectively. This dependence is related to the weak current connecting up- and down-type quarks with unequal vector couplings. These cuts test the sensitivity of the effective interaction to high-energy events. Quantitative exclusion in this channel requires an electroweak completion and validated signal and background treatments. [5](https://arxiv.org/abs/1510.02110) · [24](https://arxiv.org/abs/2505.05300) · [25](https://doi.org/10.17182/hepdata.154755.v1/t2)

![Figure 8. Relic branches and the single-top energy-cut test](figures/08_top_branches_and_energy.png)

**Figure 8.** The left panel shows $M_V-m_1-m_2$ at representative central roots. The right panel shows the exploratory on-shell single-top sensitivity as a function of the partonic-energy cut. The charged weak current connects top and bottom quarks with unequal $V$ couplings. The high-energy behavior of the longitudinal weak-boson amplitudes depends on the cancellations required by the electroweak completion. The energy cuts serve as diagnostics. The exclusions reported in the main text come from monojet. Missing markers at 0.75 TeV indicate samples for which the proxy likelihood does not yield a finite limit.

## 8. Conclusions

With the mass-weighted vector ansatz in the electroweak broken phase, xenon recoils probe the coherent light-quark amplitude, and the LHC probes heavy-flavor production. With small photon mixing, a fixed splitting, and a standard thermal history, the CMS Run 2 monojet recast gives CMS-only observed 95% CL limits with $\mu_{95}<1$ on a subset of the on-shell solutions selected by the reference yield and central relic abundance. The three sensitive benchmarks retain this property under the tested $25\%$ variations of the truth-level yield. At lower mediator masses, on-shell and off-shell relic roots can coexist. The single-top energy-cut test provides an exploratory sensitivity estimate. A joint experimental confidence region requires the event-level LZ likelihood for this model, theoretical uncertainties on the abundance, and profiling over shared parameters.

## Appendix A. Xenon recoil and matching checks

![Figure A1. Recoil spectrum in the units of the reference paper](figures/a01_original_recoil.png)

**Figure A1.** Independent reproduction of the universal-vector reference benchmark, used to check the recoil shape and units.

After subtraction at zero momentum, the finite heavy-quark contribution to photon mixing is

$$
\delta d_{cbt}(s)=-\frac{2\alpha}{\pi}\sum_{q=c,b,t}N_cQ_q\frac{\widehat m_q}{m_t}
\int_0^1 dx\,x(1-x)\log\left[1-\frac{s x(1-x)}{\widehat m_q^2}-i0\right].
\tag{A1}
$$

![Figure A2. Timelike mixing and the truth cross-section test](figures/a02_timelike_mixing.png)

**Figure A2.** Inserting $\delta d_{cbt}(M_V^2)$ in the $pp\to Vj$ tree amplitude changes the tree cross section by about $2\%$ or less at the four on-shell test masses for $p_T^j>200$ GeV. The shift divided by the original tree-plus-loop rate is below $0.4\%$. This check concerns the specified finite photon term. Replacing the real part by a constant evaluated at the dark-pair threshold or at the mediator pole shifts $\Omega h^2$ by up to $1.12\times10^{-4}$ and $4.64\times10^{-4}$, respectively. Reducing `Beps` by two orders of magnitude moves the abundance by less than $2\times10^{-11}$ at three numerical benchmarks. [Timelike rates](data/timelike_rate_summary.csv) · [Relic numerical audit](data/relic_numerical_audit.csv)

![Figure A3. Matching and excited-state self-conversion checks](figures/a03_excited_fraction.png)

**Figure A3.** After chemical freeze-out, $\chi_2\chi_2\leftrightarrow\chi_1\chi_1$ can continue to change the excited-state fraction. In the tested standard thermal histories with suppressed additional decay, a stress test including the Standard Model bath yields a minimum $f_2\simeq0.45$ at the on-shell benchmarks and values near $0.30$ at some off-shell benchmarks. The splitting $\Delta m<2m_e$ closes electron-pair decay. Independent $V$–$Z$ mixing or a transition dipole can still affect the lifetime. [2](https://arxiv.org/html/2609.26570v1) · [26](https://arxiv.org/abs/2108.13422)

After freeze-out of the total abundance, detailed balance for dark self-conversion gives $\dot f_2=-n_\chi\langle\sigma v\rangle_{22\to11}[f_2^2-e^{-2\Delta m/T_\chi}(1-f_2)^2]$, where $T_\chi$ is the dark-sector kinetic temperature. The thermal-history check uses Born contact scattering and varies the kinetic decoupling assumption. The resulting $f_2$ values are used as conditional benchmarks.

## Appendix B. Cross-section cuts and the mass projection

The closed-quark-loop UFO contains flavor-resolved rational $R_2$ vertices for $gggV$. With the $d^{abc}$ color structure, the per-flavor coefficient is $i g_{Vq}g_s^3/(48\pi^2)$, obtained by replacing the photon vector coupling in `loop_sm`. At the $M_V=87.18$ GeV benchmark and a partonic energy of 1 TeV, the numerical Ward/BRS ratio with this term is about $6.3\times10^{-24}$. This test validates the $gg\to gV$ amplitude retained here. [13](https://arxiv.org/abs/1507.00020)

![Figure B1. The two missing-momentum final states with loose cuts](figures/b01_loose_cross_sections.png)

**Figure B1.** The jet selection is $p_T^j>20$ GeV and $|\eta_j|<6$, and the top-pair final state has no truth MET cut. Comparison with Fig. 3 shows the effect of the selection threshold.

![Figure B2. Truth cross sections along the LZ equal-rate surface](figures/b02_lz_slice_cross_sections.png)

**Figure B2.** We fix $m_\chi=35$ GeV and determine $g_t$ from the tree-level equal-rate condition. A, B, and C are separate relic-density benchmarks. The remaining colors show cross sections subject to the equal-rate condition alone. [Cross-section table](data/truth_benchmarks.csv)

![Figure B3. Mass projection at the central Planck value](figures/04b_central_mass_projection.png)

**Figure B3.** Projection of the central relic grid onto $(m_\chi,M_V)$. Dark blue marks on-shell roots with observed $\mu_{95}<1$. Multiple coupling solutions can overlap in the mass projection.

## Appendix C. Validation of the CMS monojet recast

![Figure C1. Expected and observed limits with official CMS templates](figures/c01_cms_benchmark_limits.png)

**Figure C1.** Limit comparison using official signal templates. For scalar and pseudoscalar benchmarks between 50 and 800 GeV, the 66-bin expected limits differ from the published combination by at most about $9\%$. The largest observed difference is about $48\%$. The vector mass-boundary agreement tests the overall reach for that official benchmark. [16](https://arxiv.org/abs/2107.13021) · [27](https://doi.org/10.17182/hepdata.106115.v2/t1)

![Figure C2. Cutflow and MET spectrum for the 750 GeV CMS vector benchmark](figures/c02_cms_vector_750.png)

![Figure C3. Cutflow and MET spectrum for the 100 GeV CMS vector benchmark](figures/c03_cms_vector_100.png)

![Figure C4. Cutflow and MET spectrum for the 2000 GeV CMS vector benchmark](figures/c04_cms_vector_2000.png)

**Figures C2–C4.** Comparison of independent LO generation and fast simulation with official CMS benchmarks. For 100 GeV in 2017, the efficiencies conditional on the MET cut are $76.91\%$ for CMS and $77.76\%$ for this calculation. The absolute QCD signal yield is 0.629 times the CMS yield. The independent sample and the official matched NLO sample use different generator and reconstruction settings. The normalized shape and absolute efficiency provide separate tests. [28](https://doi.org/10.17182/hepdata.106115.v2/t20)

![Figure C5. Independent loop simulation at 120 GeV](figures/c05_loop_mc_validation.png)

**Figure C5.** Of the 3,600 events in the original main loop sample, 17 pass reconstruction and enter MET bins above 470 GeV. At a fixed central relic solution, an independent sample and a stratified sample give observed $\mu_{95}$ of about 0.67 and 0.61, compared with 1.30 for the original sample. The main result uses the stratified template and all observed counts. [Template comparisons](data/template_replica_comparison.csv)

### Independent template test at three sensitive benchmarks

We fix $(M_V,g_t,m_\chi,g_\chi)$ at the sensitive 120, 150.4, and 190.4 GeV benchmarks in Table 2 and keep the 66-bin CMS likelihood and background covariance fixed. Loop templates A and B use generator-level jet-$p_T$ boundaries $(100,230,480)$ and $(100,260,520)$ GeV, respectively, with independent hard-process and shower samples. Their three strata usually use 6,600, 4,000, and 3,200 generated events. For the lowest stratum of A at 120 and 150.4 GeV, we use an independent archived sample of 10,800 events and a newly generated sample of 4,800 events, respectively, retaining $100\le p_T^j<230$ GeV. Both fits use a newly generated tree template, and we repeat the fits with the original tree template. We pool the loop templates with equal weights, propagate their Monte Carlo covariances with squared weights, and include the common tree-template uncertainty once.

We rank the year-specific MET bins by $|s_i[(C_b+\operatorname{diag}\mathbf b)^{-1}\mathbf s]_i|$ using the reference signal and the background-only information. We compare the replica differences with the independent loop Monte Carlo errors in the eight highest-ranked bins. We also compare the pooled-year yields in the 470–690 GeV and above-690 GeV intervals and refit the upper limits with all 66 bins.

| $M_V$ [GeV] | Expected A / B / pooled | Observed A / B / pooled | Largest key-bin difference in MC standard deviations |
|---:|---:|---:|---:|
| 120 | 0.389 / 0.407 / 0.408 | 0.527 / 0.621 / 0.561 | 1.05 |
| 150.4 | 0.230 / 0.243 / 0.242 | 0.219 / 0.254 / 0.234 | 0.88 |
| 190.4 | 0.174 / 0.178 / 0.179 | 0.200 / 0.200 / 0.198 | 1.68 |

![Figure C6. Independent template test at three sensitive benchmarks](figures/c06_three_template_replicas.png)

**Figure C6.** The top panels show CMS 95% CL limits. Dashed lines mark the reference observed limits in Table 2. The lower panels show yield ratios relative to the reference templates in two combined MET intervals. The error bars show the Monte Carlo uncertainty of each template. Year-specific bin yields are provided separately. [66-bin yields and errors](data/template_validation_bins.csv) · [Sample sizes and seeds](data/template_validation_runs.csv) · [Fitted limits](data/template_validation_limits.csv)

The key bins and combined high-MET intervals agree between the two templates within about $1.7$ Monte Carlo standard deviations. All three points retain observed $\mu_{95}<1$. Applying the tested $r=0.75$–$1.25$ variations to each template gives a largest observed limit of $0.680$. The observed limits at 120 and 150.4 GeV still differ between the two stratifications by about $16\%$ and $15\%$, respectively, relative to their mean. The pooled limits at 150.4 and 190.4 GeV are about $31\%$ and $27\%$ below the reference values in Table 2. The exclusion decision at the three benchmarks is stable under the tested sampling changes. The numerical limits remain sensitive to finite Monte Carlo statistics and template shape.

We refit the original grid of physical roots with the three pooled templates, replacing the 120 and 150 GeV nodes and adding a node at 190.4 GeV. The number of points with $\mu_{95}<1$ changes from 208 to 199 for the expected limit and from 151 to 162 for the observed limit. The lowest sampled masses remain 92 and 104 GeV, respectively. The comparison covers the three nodes and their effect through interpolation. The absolute yield discrepancy in Fig. C3 remains relevant to the validation of signal acceptance. [Grid limits after the template refit](data/template_contour_refit.csv)

## Appendix D. Top-associated channels for light mediators

![Figure D1. Relic branches within the abundance band for light mediators](figures/d01_light_top_branches.png)

**Figure D1.** Independent low-mass scan with tree-level equal-rate matching. Colors classify the on-shell and off-shell branches found within the Planck $\pm2\sigma$ band. Purple cells contain both types of branch. Colors indicate branch availability.

![Figure D2. Truth MET distributions in top-associated production](figures/d02_top_truth_met.png)

**Figure D2.** Cross sections in fb for dark-pair production with $tj$, $tW$, and $t\bar t$ above different truth MET thresholds at four on-shell or off-shell benchmarks. Experimental limits require top decays, reconstruction, and validation of the analysis selection at the same parameter points. [Off-shell top-pair cross sections](data/off_shell_ttmet.csv) · [Single-top sensitivity estimate](data/single_top_expected.csv)

Within the scan range $m_\chi\ge20$ GeV, dark-pair production at $M_V\le40.001$ GeV requires an off-shell mediator. A quantitative top-pair exclusion using full-chain samples requires checking $m_\chi$, the threshold, and the template normalization point by point under a common reference-yield convention. The published CMS background yields come from a simultaneous fit that includes signal-region data. An observed recast therefore requires background constraints that can be used independently of the signal-region counts. [24](https://arxiv.org/html/2505.05300v1)

## Data and reproducibility

[Root-by-root grid limits](data/center_grid_limits.csv) · [Grid summary](data/center_grid_summary.json) · [Benchmark roots at all targets](data/benchmark_roots.csv) · [Benchmark uncertainty summary](data/branch_uncertainties.csv) · [Figure and data provenance](FIGURE_SOURCES.md)

## References

1. LZ Collaboration, *Search for Dark Matter Particle Interactions in an Extended Nuclear Recoil Energy Window with the LUX-ZEPLIN (LZ) Experiment*. [arXiv:2609.02823](https://arxiv.org/abs/2609.02823)
2. C. Gemmell, D. Hooper, and G. Krnjaic, *A Simple Dark Matter Model to Explain the LZ Event and Galactic Center Excess*. [arXiv:2609.26570](https://arxiv.org/abs/2609.26570)
3. X.-Y. Du, W. Huang, and K. Xie, *Pseudo-Dirac Inelastic Dark Matter in the Leptophobic $U(1)_B$ Model: Confronting the LUX-ZEPLIN High-Recoil Event with Collider Searches*. [arXiv:2609.07225](https://arxiv.org/abs/2609.07225)
4. P. Cox, A. D. Medina, T. S. Ray, and A. Spray, *Novel Collider and Dark Matter Phenomenology of a Top-philic $Z'$*. [arXiv:1512.00471](https://arxiv.org/abs/1512.00471)
5. F. Kahlhoefer, K. Schmidt-Hoberg, T. Schwetz, and S. Vogl, *Implications of Unitarity and Gauge Invariance for Simplified Dark Matter Models*. [arXiv:1510.02110](https://arxiv.org/abs/1510.02110)
6. F. D’Eramo, B. J. Kavanagh, and P. Panci, *You Can Hide but You Have to Run: Direct Detection with Vector Mediators*. [arXiv:1605.04917](https://arxiv.org/abs/1605.04917)
7. LZ Collaboration, extended nuclear-recoil search, HEPData record. [doi:10.17182/hepdata.182472.v1](https://doi.org/10.17182/hepdata.182472.v1)
8. K. Griest and D. Seckel, *Three Exceptions in the Calculation of Relic Abundances*, Phys. Rev. D **43**, 3191 (1991). [doi:10.1103/PhysRevD.43.3191](https://doi.org/10.1103/PhysRevD.43.3191)
9. P. Gondolo and G. Gelmini, *Cosmic Abundances of Stable Particles: Improved Analysis*, Nucl. Phys. B **360**, 145–179 (1991). [doi:10.1016/0550-3213(91)90438-4](https://doi.org/10.1016/0550-3213%2891%2990438-4)
10. G. Alguero et al., *micrOMEGAs 6.0: N-Component Dark Matter*. [arXiv:2312.14894](https://arxiv.org/abs/2312.14894)
11. Planck Collaboration, *Planck 2018 Results. VI. Cosmological Parameters*. [arXiv:1807.06209](https://arxiv.org/abs/1807.06209)
12. J. Alwall et al., *The Automated Computation of Tree-Level and Next-to-Leading Order Differential Cross Sections, and Their Matching to Parton Shower Simulations*. [arXiv:1405.0301](https://arxiv.org/abs/1405.0301)
13. V. Hirschi and O. Mattelaer, *Automated Event Generation for Loop-Induced Processes*. [arXiv:1507.00020](https://arxiv.org/abs/1507.00020)
14. C. Bierlich et al., *A Comprehensive Guide to the Physics and Usage of PYTHIA 8.3*. [arXiv:2203.11601](https://arxiv.org/abs/2203.11601)
15. DELPHES 3 Collaboration, *DELPHES 3: A Modular Framework for Fast Simulation of a Generic Collider Experiment*. [arXiv:1307.6346](https://arxiv.org/abs/1307.6346)
16. CMS Collaboration, *Search for New Particles in Events with Energetic Jets and Large Missing Transverse Momentum in Proton-Proton Collisions at $\sqrt{s}=13$ TeV*, JHEP **11** (2021) 153. [arXiv:2107.13021](https://arxiv.org/abs/2107.13021)
17. A. Albert, *Implementation of a Search for New Phenomena in Events Featuring Energetic Jets and Missing Transverse Energy (137 fb$^{-1}$, 13 TeV, CMS EXO-20-004)*, MadAnalysis 5 (2021). [doi:10.14428/DVN/IRF7ZL](https://doi.org/10.14428/DVN/IRF7ZL) · [Implementation and validation description](https://doi.org/10.21468/SciPostPhys.14.1.009)
18. CMS EXO-20-004, public monojet background covariance, HEPData Table 14. [doi:10.17182/hepdata.106115.v2/t14](https://doi.org/10.17182/hepdata.106115.v2/t14)
19. CMS EXO-20-004, observed and background yields, HEPData Table 15. [doi:10.17182/hepdata.106115.v2/t15](https://doi.org/10.17182/hepdata.106115.v2/t15)
20. CMS Collaboration, *Simplified Likelihood for the Re-Interpretation of Public CMS Results*. [CMS-NOTE-2017-001](https://cds.cern.ch/record/2242860)
21. G. Cowan, K. Cranmer, E. Gross, and O. Vitells, *Asymptotic Formulae for Likelihood-Based Tests of New Physics*. [arXiv:1007.1727](https://arxiv.org/abs/1007.1727)
22. A. L. Read, *Presentation of Search Results: The $CL_s$ Technique*, J. Phys. G **28**, 2693–2704 (2002). [doi:10.1088/0954-3899/28/10/313](https://doi.org/10.1088/0954-3899/28/10/313)
23. F. Forner and F. Tellander, *Renormalization of $U(1)$ Gauge Boson Kinetic Mixing*, Phys. Rev. D **113**, 056015 (2026). [doi:10.1103/tqw9-zm9x](https://doi.org/10.1103/tqw9-zm9x) · [arXiv:2512.14836](https://arxiv.org/abs/2512.14836)
24. CMS Collaboration, *Search for Dark Matter Produced in Association with One or Two Top Quarks in Proton-Proton Collisions at $\sqrt{s}=13$ TeV*. [arXiv:2505.05300](https://arxiv.org/abs/2505.05300)
25. CMS top-associated search, AH $1b\,1\mathrm{FJ}$ post-fit MET spectrum, HEPData Table 2. [doi:10.17182/hepdata.154755.v1/t2](https://doi.org/10.17182/hepdata.154755.v1/t2)
26. M. Carrillo González and N. Toro, *Cosmology and Signals of Light Pseudo-Dirac Dark Matter*. [arXiv:2108.13422](https://arxiv.org/abs/2108.13422)
27. CMS EXO-20-004, public spin-1 signal templates, HEPData Table 1. [doi:10.17182/hepdata.106115.v2/t1](https://doi.org/10.17182/hepdata.106115.v2/t1)
28. CMS EXO-20-004, public monojet cutflow, HEPData Table 20. [doi:10.17182/hepdata.106115.v2/t20](https://doi.org/10.17182/hepdata.106115.v2/t20)

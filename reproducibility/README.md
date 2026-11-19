# Numerical reproduction

This directory contains the LZ recoil calculation, relic model and root search, tree and loop UFO sources, event-generation and detector-analysis code, public CMS inputs, binned signal templates, likelihood implementation, independent signal replicas, uncertainty scans, and plotting sources used in the manuscript. The dated analysis directories preserve the original computation order.

## Offline reproduction

Use Python 3.12. Run from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r reproducibility/requirements.txt
python reproducibility/reproduce.py verify
python reproducibility/reproduce.py benchmarks
python reproducibility/reproduce.py validation
python reproducibility/reproduce.py contour
python reproducibility/reproduce.py figures
python reproducibility/reproduce.py cms-benchmark
python reproducibility/reproduce.py cancellation
```

On Windows activate with `.venv\Scripts\Activate.ps1`. `all` runs these stages in order. Outputs are written under `build/reproducibility/`. The archive is copied before full refits so regeneration preserves the distributed inputs.

The benchmark command recomputes the 66-bin CMS expected and observed likelihood limits from the signal counts, cross sections, luminosities and background covariance. It checks the three original-template results against the archived values with a relative tolerance of 0.03%. `validation` recomputes the independent A/B/pooled template fits and all MET-bin comparisons. `contour` refits the physical grid with the pooled templates. `figures` rebuilds the central projection and assembles the archived figures. Some original plots are copied from the original analysis products, as recorded in `FIGURE_SOURCES.md`; this command does not rerun their event generation.

`cms-benchmark` recomputes 184 official-template fits and 594 spectrum bins. `cancellation` reproduces the conditional ttbar expected limits from the archived central relic roots. Those roots can be recalculated individually using `relic_local.py`. A Chinese guide is available in [README_zh.md](README_zh.md).

Expected original-template benchmark values are

| $M_V$ [GeV] | $g_t$ | expected $\mu_{95}$ | observed $\mu_{95}$ |
|---:|---:|---:|---:|
| 120 | 3.0734116611 | 0.41236009 | 0.60707938 |
| 150.4 | 3.5449077018 | 0.18411177 | 0.34019377 |
| 190.4 | 3.5449077018 | 0.21943851 | 0.27316625 |

These values identify the original templates. The independent pooled-template results and changed contours are separate outputs. The archived pooled grid has 199 expected and 162 observed excluded sampled points, with lowest sampled excluded masses of 92 and 104 GeV, respectively.

## Recompute LZ and thermal roots on Linux

Install micrOMEGAs **7.1.4** from [the authors' distribution](https://lapth.cnrs.fr/micromegas/), with a C/Fortran toolchain and its CalcHEP dependencies. The default micrOMEGAs model project structure is used. The five files in `models/micromegas_photon/` and `mass_relic.c` define the archived photon-current model. The baseline recoil implementation is `work/pseudoDiracYukawa_build/lz_recoil.c`.

```bash
python reproducibility/build_model.py --micromegas /path/to/micromegas_7.1.4
python reproducibility/relic_local.py \
  --project /path/to/micromegas_7.1.4/LZPhotonReproduction \
  --mv 60 --gt 0.3992709259641317 --d 0 \
  --out build/relic_60.json
```

The local runner recomputes the photon correction to the LZ rate, uses the archived baseline recoil integral, and brackets both on-shell and off-shell roots. It calls `darkOmega` for every trial mass with `Fast=0`, `Beps=1e-9`. The default mass domain is 20–100 GeV and the coupling domain is 0.1–1.5, inherited from the paper scan. These bounds affect root availability. Each output records the roots, call count and failed evaluations. The same command can be looped over `(M_V,g_t,d,rate,fraction)` to rebuild the physical slices. Original full-grid orchestration and all raw root searches are included in the dated directories.

For a fresh baseline recoil table, build `lz_recoil.c` as a micrOMEGAs main in the baseline model, then use the `recoil` function in `outputs/monojet_mchi_scan_20261106/scripts/scan.py`. It writes each parameter card, differential recoil CSV and integrated truth yield. Baseline halo parameters are $\rho=0.3$ GeV/cm$^3$, $v_0=238$, $v_E=254$, $v_{esc}=544$ km/s. Exposure is 2.84 tonne-years, the truth window is 5.4–269.9 keV, $\Delta m=1$ MeV and $f_2=0.5$. The reference target is 1.120444105 truth events. Photon matching is defined by $d_\gamma(0)=e\epsilon_\gamma(0)/g_t$.

## Generate fresh collider samples

Use **MadGraph5_aMC@NLO 3.6.6** from [the official distribution](https://launchpad.net/mg5amcnlo), including its loop providers. The audited fixed UFO is `outputs/monojet_loop_20261103/model/PseudoDiracFlavorEFT_UFO_loop_R2fix/`. Its counterterms and Ward-test evidence are included. Preserve the `-full` restriction and massive heavy-quark loop parameters. See `MODEL_AUDIT.md` and `BUILD_NOTES.md` for the R2 repair and compiler compatibility fixes.

```bash
python reproducibility/generate_hard.py --mg5 /path/to/MG5_aMC_v3_6_6/bin/mg5_aMC \
  --channel loop --mv 120 --gt 3.0734116610746134 \
  --gchi 0.2839125266054045 --mchi 41.11620411048844 \
  --width 0.115961734014 --seed 119001 --nevents 10000 \
  --out build/mg_loop120
```

Other channels are `tree`, `ttbar`, and `ttbar-offshell`. On-shell hard generation exports an undecayed V. Invisible decay, shower and selection must be applied before constructing detector templates. The total width must correspond to the same model point. Fresh events fluctuate statistically and will not reproduce archived numbers event by event.

The complete original shower/reconstruction workflow is in `outputs/monojet_analysis_20261106/scripts/` and `outputs/monojet_expected_lz_scan_20261106/scripts/`. Independent stratification boundaries, seeds, hard/shower settings and NPZ packing are in `outputs/phenomenology_paper_20261110/template_validation_remote.py`. These historical orchestration scripts retain their original workstation paths. Adapt those paths to the installed MadGraph/Pythia8/Delphes executables before running. Install optional Python readers using `requirements-simulation.txt`. The run banners and parameter cards preserve the PDF, cuts and scales used in each archived sample.

## Analysis map

| Calculation | Sources and inputs |
|---|---|
| Original reference-paper recoil reproduction | `outputs/pseudoDiracB_20261004/`, `work/pseudoDiracB_build/` |
| Yukawa-like LZ recoil and baseline matching | `work/pseudoDiracYukawa_build/`, `outputs/monojet_mchi_scan_20261106/scripts/scan.py` |
| micrOMEGAs and Planck roots | `models/micromegas_photon/`, `relic_local.py`, `outputs/lz_mixing_uncertainty_20261110/` |
| Truth cross sections, mass scans, MET shapes | `outputs/truth_xsec_scan_20261106/`, `outputs/pseudoDirac_yukawaLZ_xsec_20261020/` |
| Loop model, Ward identity, R2 repair | `outputs/monojet_loop_20261103/` |
| Detector selection and 66-bin templates | `outputs/monojet_analysis_20261106/`, `outputs/monojet_expected_lz_scan_20261106/` |
| Expected/observed profile likelihood | `outputs/monojet_mchi_scan_20261106/scripts/observed_fit.py`, `outputs/lz_mixing_uncertainty_20261110/collider_errors.py` |
| Official CMS benchmarks and detector cutflow checks | `outputs/monojet_cms_benchmark_20261107/` |
| Independent signal replicas and pooled contour | `outputs/phenomenology_paper_20261110/` |
| Photon matching, LZ yield, Planck and excited fraction variations | `outputs/lz_mixing_uncertainty_20261110/`, `outputs/lz_model_checks_20261110/` |
| Off-shell ttbar matrix elements and branch audit | `outputs/ttmet_branch_map_20261110/` |
| ttbar cancellation-point expected estimates | `outputs/ttbar_photon_cancellation_20261118/`, repository `ttbar/` |
| Exploratory single-top energy dependence | `outputs/single_top_pilot_20261110/` |

Public monojet background/yield inputs are from [CMS EXO-20-004](https://arxiv.org/abs/2107.13021), [HEPData v2](https://doi.org/10.17182/hepdata.106115.v2). Covariance and yield tables are 14 and 15. The input archive and parsed numerical tables are distributed with this package. The ttbar supplementary framework uses [CMS EXO-22-014](https://arxiv.org/abs/2505.05300). Background post-fit reuse, cutflow differences, finite signal statistics, mass-dependent template limitations and the broken-phase model scope are documented in the manuscript and supplementary audits.

## Validation scope and provenance

`manifest.json` records SHA-256 and byte counts for the archived inputs. `VALIDATION.json` records this release's actual checks. The public CI reruns integrity checks and the three monojet benchmark fits. Fresh micrOMEGAs/MadGraph/Delphes builds are external-software jobs and are tracked separately from the offline fit checks.

LZ matching is a prescribed truth-rate slice. CMS 95% CL limits are calculated on that slice after imposing the abundance equation. The published products retain separate original and pooled templates and distinguish on-shell and off-shell solutions. The single-top and supplementary ttbar results carry their stated validation scope.

Large LHE/ROOT event streams, compiler binaries and installed third-party distributions are regenerated using the supplied scripts. Binned counts, covariance inputs, cross sections, cards, seeds and independent replicas required for the offline likelihood reconstruction are included.

The manuscript repository is [Jim11451/lz_paper](https://github.com/Jim11451/lz_paper). Cite the exact Git commit used for a result. A permanent DOI can be added after the collaboration archives a release.

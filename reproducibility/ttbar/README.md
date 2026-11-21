# ttbar + MET paper — reproducible package

Everything needed to rebuild the numerical results of the `ttbar/` paper
(CMS EXO-22-014 recast: $pp\to t\bar tV$, $V\to\chi_1\chi_2$) from the
archived public inputs.  Total size: 0.5 MB.

```
inputs/     archived inputs (read-only)
  hepdata/          22 tables from HEPData ins2919645 (11 SR + 8 CR + limits)
  lz_points.csv     the 14 relic-band points (M_V, m_chi, g_chi)
  sigma_MV.csv      exact MG5 cross sections at the 14 M_V nodes
  kappa_lz_gN.csv   LZ normalisation kappa(m_chi), 36 points
  mm_gN.csv         micrOMEGAs relic grid (286 points)
  channels.csv      partonic-channel decomposition of sigma(ttbarV)
  templates.json    15-bin shapes + efficiencies of the 14 signal columns
  grid_final.npz    44 x 14 exclusion grid (mu95 expected/observed)
code/
  build_workspace.py  HEPData yaml -> pyhf workspace (11 SR + 8 CR)
  fit_cr.py           profile-likelihood fit, CLs crossings, kappa hats
  sys_likelihood.py   single-region (15-bin) asymptotic CLs, used for cross-checks
expected/
  expected.json       archived values the rebuild must reproduce
run.py                verify | limits | stamp
```

## Run

```bash
pip install -r requirements.txt
python run.py verify     # sha256 of all 32 archived files
python run.py limits     # rebuild the workspace and refit
```

`limits` prints, for both models (with and without the 8 control regions):

```
case   quantity       reproduced   archived
withCR muhat             0.36431    0.36431
withCR m95_obs           0.51172    0.51172
withCR m95_exp           0.16016    0.16016
noCR   muhat             0.38082    0.38082
noCR   m95_obs           0.53516    0.53516
noCR   m95_exp           0.16797    0.16797
```

## What is reproduced, and what is not

Reproduced from the archived inputs (exactly, 5 digits):
- the 19-channel (11 SR + 8 CR) and 11-SR-only profile-likelihood fits,
  their $\hat\mu$, $Z$ and $\mu_{95}$ (observed and expected);
- the per-background normalisation factors $\hat\kappa$;
- everything downstream that depends only on these files: the
  $\mu_{95}$-vs-$(M_V,g_t)$ exclusion grid (`inputs/grid_final.npz`),
  the cross-section table and the partonic-channel decomposition.

**Not** reproducible here, by construction:
- **event generation.**  The 15-bin signal shapes in `templates.json` were
  produced from 14 x 50k Delphes samples (247 GB) generated with
  MadGraph5_aMC@NLO 3.6.6 + Pythia8 + Delphes.  Those samples are not
  archived; `templates.json` is the distilled product and is itself
  hash-checked, so the *use* of the templates is reproducible but their
  *generation* is not.
- **the expected limit's absolute normalisation.**  The public HEPData
  tables carry only post-fit per-bin errors; the JES, b-tagging and
  $t\bar t$-shape systematics that control the expected limit are not
  published.  Our expected $\mu_{95}=0.160$ versus the CMS 0.277 is a
  42% gap that cannot be closed from public information.
- **pre-fit control-region predictions.**  Published CR numbers are
  post-fit ($N/B=1.000$–$1.009$), so the CRs carry almost no constraining
  power; this is why adding them moves $\mu_{95}^{\rm obs}$ by only 4%.

## Provenance

| input | source |
|---|---|
| `hepdata/*.yaml` | HEPData record ins2919645 (CMS-EXO-22-014), downloaded 2026-11 |
| `lz_points.csv`, `kappa_lz_gN.csv`, `mm_gN.csv` | micrOMEGAs 7.1 scan + LZ rate normalisation, see the paper's section 4 |
| `sigma_MV.csv` | MadGraph5_aMC@NLO 3.6.6, `p p > t t~ vb`, 14 M_V nodes, g_t = 1 |
| `templates.json` | Delphes 3.5 CMS card, 14 x 50k events at the relic-band m_chi |
| `grid_final.npz` | `mu95` on the 44 x 14 $(g_t,M_V)$ grid from the above |

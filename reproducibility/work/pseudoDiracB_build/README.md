# Pseudo-Dirac U(1)_B model for micrOMEGAs

This is a mass-basis CalcHEP/micrOMEGAs implementation of the benchmark in
arXiv:2609.26570v1, built from the conventions and field organization of the
`niDM_feynrules` package (arXiv:2405.08081).

The retained interaction is

```text
L_int = (1/2) V_mu [ gChi chi_bar gamma^mu chi
                     + gB sum_q (1/3) q_bar gamma^mu q ]
```

and in the pseudo-Dirac mass basis

```text
L_int contains (i gChi/2) V_mu chi1_bar gamma^mu chi2 .
```

`chi1` is the light state and `chi2` the excited state, with
`Mchi2=Mchi+dM`. There are no diagonal `V chi_i chi_i` vertices. The vector
couples universally to quark baryon number with the paper's overall `1/2`
normalization, so the CalcHEP quark vertex is `gB/6`.

The anomalons, the U(1)_B-breaking scalar, and loop-induced kinetic/mass
mixing with electroweak gauge bosons are not included. This is sufficient for
the paper's tree-level relic-density channels and exothermic xenon scattering,
but it is not a complete anomaly-free collider model.

Benchmark (`benchmark.par`):

```text
Mchi = 35 GeV
dM   = 0.001 GeV
MV    = 30 GeV
gB    = 1.46e-5
gChi  = 0.32
fExc  = 0.5
```

Paper targets:

- `sigma(chi_i chi_i -> VV) v = 4.4e-26 cm^3/s`;
- total thermal abundance near `Omega h^2 = 0.12`;
- `N_ROI = 1` and `N_SB = 8e-4` after the LZ efficiency and resolution.

Validated on the Tailscale workstation with the official micrOMEGAs 7.1.10
tarball (SHA-256
`c9fd03a341304ec8f8d03a1544da0f67a7b7ad058ee0729593cb8e9872b1ebe2`).
Run inside a micrOMEGAs 7.1.10 root:

```bash
make main=main.c
./main benchmark.par

make main=lz_recoil.c
./lz_recoil benchmark.par recoil.csv
```

The recoil executable uses micrOMEGAs' Maxwell halo and xenon recoil machinery,
then replaces the elastic velocity threshold by the exothermic expression in
Eq. (22) and restores the finite mediator propagator. Its event integrals are
truth-level because the public LZ HEPData record does not contain a numerical
efficiency/resolution table.

Validation results:

- The CalcHEP single-state low-velocity rate is
  `4.2403e-26 cm^3/s`, versus `4.2419e-26 cm^3/s` from Eq. (13), validating
  the off-diagonal Majorana-vector normalization.
- The exact thermal average at freeze-out is `3.2860e-26 cm^3/s`, larger than
  the paper's non-relativistic effective estimate `2.1209e-26 cm^3/s` because
  the benchmark is close to the `VV` threshold. Consequently micrOMEGAs gives
  `Omega h^2=0.09184` for the literal paper card.
- `micromegas_relic.par` uses `gChi=0.2981` and gives
  `Omega h^2=0.120018` with the same masses and `gB`.
- For the literal paper card the truth-level 2.84 tonne-year counts are
  `N_ROI=1.12044` and `N_SB=7.3879e-4`; the paper quotes `1` and `8e-4` after
  applying the LZ detector efficiency and energy resolution.
- For the micrOMEGAs relic-density card the truth-level counts are
  `N_ROI=0.97233` and `N_SB=6.4113e-4`.

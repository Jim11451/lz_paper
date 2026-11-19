# Pseudo-Dirac U(1)_B model and LZ-event reproduction

Date: 2026-10-04

## Deliverables

- `PseudoDiracB_micromegas_7.1.10.zip`: CalcHEP/micrOMEGAs model, parameter
  cards, FeynRules mass-basis source, recoil calculator, and validation script.
  SHA-256: `78563551507D83BF672496AEB27C68DADA341AF31E9DA2FB367C90C864D01C9F`.
- `recoil_benchmark.csv`: truth-level natural-xenon spectrum for the literal
  paper benchmark.
- `recoil_micromegas_relic.csv`: spectrum after retuning `gChi` to the relic
  density calculated by micrOMEGAs 7.1.10.
- `recoil_spectrum.png` and `.svg`: comparison plot.
- `recoil_spectrum_paper_units.png` and `.svg`: Fig. 6-style benchmark plot in
  the paper's original differential-rate units,
  `(kg day keV)^-1`, without multiplying by detector exposure.
- `validation_*.log` and `recoil_*.log`: workstation results.

## Model implemented

The model is the mass-basis form of arXiv:2609.26570v1:

```text
qbar q V:       gB/6 gamma^mu
chi1 chi2 V:    i gChi/2 gamma^mu
Mchi2:          Mchi + dM
```

`chi1` and `chi2` are self-conjugate Majorana fields. There are no diagonal
`V chi_i chi_i` vertices. The anomalons, U(1)_B-breaking scalar, and the
loop-induced electroweak kinetic/mass mixing are decoupled, as in the paper's
tree-level relic-density and xenon-scattering calculation.

The package was organized from the supplied `niDM_feynrules` conventions, but
the original niDM dark-photon/dark-Higgs interactions were intentionally not
retained because they describe a different model.

## Workstation environment

- Host: the Tailscale 9950X AlmaLinux 8.10 workstation (`dxr` account).
- Remote model path:
  `/home/dxr/lz-event/src/micromegas_7.1.10/PseudoDiracB`
- micrOMEGAs: official version 7.1.10.
- Tarball SHA-256:
  `c9fd03a341304ec8f8d03a1544da0f67a7b7ad058ee0729593cb8e9872b1ebe2`
- The pre-existing `/home/cms` installation was not modified.

## Numerical validation

| Quantity | Paper / analytic target | Literal paper card | micrOMEGAs relic card |
|---|---:|---:|---:|
| `gChi` | 0.32 | 0.32 | 0.2981 |
| single-state `sigma v` at low velocity [cm^3/s] | 4.4e-26 | 4.24033e-26 | 3.19336e-26 |
| Eq. (13) result [cm^3/s] | 4.4e-26 | 4.24187e-26 | 3.19452e-26 |
| effective `sigma v` near the degenerate limit [cm^3/s] | about 2e-26 | 2.13625e-26 | 1.60879e-26 |
| thermal average at freeze-out [cm^3/s] | not tabulated | 3.28596e-26 | 2.48128e-26 |
| `Omega h^2` | about 0.12 | 0.0918386 | 0.120018 |
| truth-level `N_ROI`, 5.4--269.9 keV | 1 after detector response | 1.12044 | 0.972331 |
| truth-level `N_SB`, 350--675 keV | 8e-4 after detector response | 7.38787e-4 | 6.41126e-4 |

The CalcHEP low-velocity result agrees with Eq. (13) to about 0.04%, which
validates the off-diagonal Majorana-vector normalization. The literal paper
card gives a smaller relic abundance in micrOMEGAs because the exact thermal
average at freeze-out is enhanced relative to the paper's non-relativistic
estimate near the `mChi=35 GeV`, `mV=30 GeV` threshold. Retuning only `gChi`
to 0.2981 restores `Omega h^2=0.120018`.

The recoil calculation uses the nine natural xenon isotopes, the micrOMEGAs
Maxwell halo and Helm form factor, the finite mediator propagator, and the
exothermic minimum speed. For Xe-131, the zero of `vmin` is 222.89 keV.

## Detector-response boundary

The public LZ HEPData release does not provide a numerical efficiency or
energy-resolution table. The collaboration paper reports 50% efficiency at
5.4 and 269.9 keV and an average 96% efficiency from 14 to 250 keV. Therefore
the CSV spectra and counts here are explicitly truth-level. Their agreement
with the paper's response-folded `N_ROI=1` and `N_SB=8e-4` is already at the
expected efficiency-level accuracy, but no unpublished response curve was
invented.

The halo card uses `vEarth=254 km/s`; the phenomenology paper states `v0=238`
and `vesc=544 km/s` but does not explicitly tabulate `vEarth`.

## Running

Extract the zip as `PseudoDiracB` inside a micrOMEGAs 7.1.10 root and run:

```bash
cd PseudoDiracB
bash run_validation.sh
```

The FeynRules source is included for transparency, but the delivered CalcHEP
tables are the artifacts actually compiled and numerically validated. A fresh
FeynRules export should be compared vertex-by-vertex before replacing them.

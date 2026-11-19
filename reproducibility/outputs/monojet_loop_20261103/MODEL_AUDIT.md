# Uploaded loop UFO audit

Date: 2026-11-03. Uploaded model: `/home/cms/PseudoDiracFlavorEFT_UFO_loop`.

The upload imports loop_sm QCD UV/R2 objects and supports loop-induced
process generation, but contains no counterterm vertex with the new particle
`P.Vb`. In particular, its existing `V_GGGA` has a nonzero symmetric-colour
`d(1,2,3)` rational term; the corresponding `gggVb` term is absent.

An isolated copy `PseudoDiracFlavorEFT_UFO_loop_R2fix` adds six flavour-resolved
gggV rational vertices. This is the exact substitution `VectorAUp/Down -> gVq`
in the supplied loop_sm photon vertex, with identical colour and Lorentz parts:

$$
C_{R_2,gggV}^{(q)}=\frac{i g_{Vq}g_s^3}{48\pi^2},\qquad
\mathrm{colour}=d^{abc}.
$$

The added Lorentz structure is the existing `L.R2_GGVV`. Quark-loop flavour
tags are separate, so unequal couplings and a top-only test remain meaningful.
The original upload and its tarball are preserved unchanged. This repair is
limited to the finite vector-current closed-quark-loop `gg -> gV` amplitude;
it does not claim a general NLO completion of the entire dark-sector model.

The production task uses `gg -> gV` and multiplies by the physical invisible
branching ratio, i.e. the narrow-width approximation. No off-shell result is
implied by this calculation. The selected 86–88 GeV points have narrow widths.

Numerical Ward/BRS checks and production integration are run separately, with
their logs archived. Only validated results should be used as physics numbers.

Recorded Ward test at the B benchmark and 1 TeV partonic energy:

| Model | Matrix | BRS | Ratio | Result |
|---|---:|---:|---:|---|
| Uploaded | 2.3500210935e-3 | 1.0366304921e2 | 4.4111539890e4 | Failed |
| R2-fixed | 1.9859347425e-3 | 1.2457442593e-26 | 6.2728358221e-24 | Passed |

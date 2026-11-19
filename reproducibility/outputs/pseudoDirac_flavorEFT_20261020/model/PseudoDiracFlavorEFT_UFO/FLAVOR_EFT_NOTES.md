# PseudoDiracFlavorEFT UFO

This UFO is an independent flavor-nonuniversal simplified-model branch of the
audited `PseudoDiracB_UFO_fixed_20261005`.  It contains only `Vb`, `chi1`, and
`chi2` beyond the Standard Model; no anomalons or symmetry-breaking scalar are
present.

The interaction convention is

```text
L_int = V_mu sum_q gVq qbar gamma^mu q
        + i gChi/2 V_mu chi1bar gamma^mu chi2 + h.c.
```

The six actual vector-current coefficients are external parameters in block
`FLAVCOUP`:

```text
1 gVu, 2 gVd, 3 gVs, 4 gVc, 5 gVb, 6 gVt.
```

The default value of every `gVq` is `1.46e-5/6`, so the original universal
PseudoDiracB benchmark is reproduced exactly.  To reproduce a universal
benchmark conventionally labelled by `gB`, set every `gVq = gB/6`.

These independent coefficients are EFT/simplified-model inputs, not charges of
an anomaly-free gauged baryon number.

Import this model in MadGraph with the suffix `-full`.  The ordinary default
restriction sees the six equal default coefficients and merges them into one
parameter, which defeats a flavor scan.

Width `WV` must be recomputed at every scan point.  In this old FeynRules-1.7
export MadWidth does not expose `Vb` and silently writes a zero width, so do
**not** use `set decay 9900032 Auto`.  The scan scripts use analytic two-body
widths for `Vb -> q q~` and `Vb -> chi1 chi2` instead.

The old stored `fixed_pp_chi1chi2` process is not a valid numerical regression
target for a newly generated process.  Its generated Fortran still contains
`ColorOne(), CF=1`, whereas a fresh process from the repaired
`Identity(1,2)` vertex contains the physical quark color sum `CF=3`.  Thus the
freshly generated original benchmark is three times the legacy stored result;
this is a correction of stale generated code, not a coupling redefinition.


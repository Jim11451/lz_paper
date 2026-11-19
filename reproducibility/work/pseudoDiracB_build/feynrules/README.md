# FeynRules source

`PseudoDiracB.fr` is the transparent mass-basis definition corresponding to
the CalcHEP model in `../work/models`.

It uses the Standard Model class names `uq`, `dq`, and `LSM` from the
`SM.fr` shipped in `niDM_feynrules`. The intended load order is therefore:

```mathematica
LoadModel["SM.fr", "PseudoDiracB.fr"]
```

The current CalcHEP files were written explicitly to keep the paper's factors
of one half visible. A fresh FeynRules export must be compared vertex by vertex
before replacing them, especially the off-diagonal Majorana-vector rule.

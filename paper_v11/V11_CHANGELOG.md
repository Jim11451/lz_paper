# V11 changelog — targeted corrections

Base: V10 (16 pp, `PAPER_V10_FINAL.pdf`) → V11 (17 pp, `PAPER_V11_FINAL.pdf`).
No simulation, no likelihood change, no new points. 470 points and 381/89 unchanged.

## Scientific corrections

1. **κ relation (P2, Eq. (2) below).** "the recoil cross section scales as $g_\chi^2/M_V^4$"
   → "$\sigma_{\rm recoil}\propto g_\chi^2g_t^2/M_V^4=\kappa^2$, so at fixed $\kappa$ it no longer
   depends on $g_\chi$, $g_t$ and $M_V$ separately."
2. **Same omission in §3.1 (P4).** "depends on $g_\chi$ and $M_V$ only through $g_\chi^2/M_V^4$"
   → "only through $g_\chi^2g_t^2/M_V^4=\kappa^2$".
3. **"rather than changing the structure of the map" deleted.** Changing $f_2$ changes $\kappa$,
   hence the relic solution, the width and $\mathrm{BR_{inv}}$; no shape invariance is claimed.
4. **Eq. (6) convergence.** The relic solve now states the bisection residual ($<10^{-5}$ in
   $\Omega_\chi h^2$) and the acceptance tolerance ($|\Omega/{\rm target}-1|<5\times10^{-3}$).
5. **§4.1 binning.** Now says explicitly that the fifteen $p_T^{\rm miss}$ edges are the binning of
   the published post-fit distribution, not the binning in which CMS fits (it uses network score bins).
6. **§5.2 splitting.** "the splitting required by the xenon normalisation" → "the fixed splitting
   $\Delta m=1$~MeV used in the recoil normalisation" (both in text and Fig. 2 caption).
7. **§5.3 reversed explanation.** "where the yield still exceeds what the likelihood excludes"
   → "where the yield falls below the level the likelihood excludes at 95% CL and the expected
   limit returns above unity."
8. **"kinematic limit"** for the top of the coloured region → "the upper end of the scanned
   coupling range, $g_t=\sqrt{4\pi}$". The invisibility-penalty sentence now says the penalty
   closes the window only at 30 and 40 GeV.
9. **§6.3 node 468.** "insensitive at the 0.5% level" (false) → "moves from 0.0365 to 0.0380 and
   0.0422, a 4–16% change that leaves all three values deep in the excluded region."
10. **§6.4 coverage.** The four-node efficiency test is no longer presented as supporting the full
    grid: the paper states that the 470-node statement rests on the branching-ratio change alone
    and that the four samples only license treating $\varepsilon$ as unchanged elsewhere.
11. **Table 3 caption.** States that the Poisson resampling is of the fifteen bin contents, so it
    includes the total-yield fluctuation as well as the shape, and that the efficiency error is
    separate.
12. **Table 4 κ entry — recomputed, not restated.** The old value (9.1%) came from
    `V3_STEP66_SYSTEMATICS/step66_envelopes.py`, which applies a flat ±10% factor to the signal.
    That is the wrong propagation: κ enters the collider signal only through $\mathrm{BR_{inv}}$.
    Propagating $\kappa\to g_\chi\to\mathrm{BR_{inv}}\to\sigma$ at fixed $m_\chi$ gives
    $\Delta\sigma/\sigma = 0.2\%$ where $\mathrm{BR_{inv}}\simeq1$ and up to $21\%$ where
    $\mathrm{BR_{inv}}\ll1$. The table now quotes that range, the caption says how it was obtained,
    and §7.1 notes that eleven points (three each at 20, 30, 40 GeV, two at 50 GeV, all with
    $\mathrm{BR_{inv}}\le0.68$) lie within the shift, while the points nearest unity elsewhere have
    $\mathrm{BR_{inv}}\simeq1$ and move by less than 0.1%.
13. **Planck window wording.** "Planck permits 0.1176 ≤ …" → "We adopt the abundance window …",
    so the interval is ours, not an official Planck confidence interval.
14. **Unverified claims removed.** The "biased low by about 10%" sentence in §7.1 (no dedicated
    study behind the factor); "what is and is not recomputed" in §3; "the LHC already excludes"
    → "excludes at 95% CL"; "; We adopt" punctuation; Table 6 caption "fourth to sixth columns"
    → "third column"; conclusion "the plane is excluded" → "within the scanned range".

## Figures

* **Fig. 2** — colour legend now reads "excluded ($\mu_{95}<1$)" / "not excluded ($\mu_{95}>1$)" /
  "no admissible solution" / "$\mu_{95}=1$"; the "one computed grid point" entry is gone; the
  superfluous colorbar annotation was dropped after it collided with the tick labels.
* **Fig. 3** — capped points marked with open circles and a "scan cap" annotation; 100 and 200 GeV
  recoloured (orange / dark red) for contrast; $\mu_{95}=1$ label moved clear of the curves.
* **Fig. 4** — larger canvas (7.6×5.4 in), mass label above each panel instead of inside it, more
  space between panels; the shared legend stays at the top.

## Layout

Figures 2, 3 and 4 now sit on pp. 8, 9 and 10 respectively, each with the text that discusses it
(`\FloatBarrier` at the end of Section 5). 17 pages.

## Open

* Author list and affiliation still placeholders.
* The κ systematic is now propagated at fixed $m_\chi$; a full joint re-solve of the relic
  equation for a shifted κ is not attempted and is not claimed.

## V11.1 — figure censoring marks and cap value (2026-11-26)

- Figure 2: cells pinned at the likelihood cap ($\mu_{95}=64$) are now marked with
  open circles and a legend entry; previously they were coloured as ordinary data even
  though they set the darkest part of the $M_V=20$ GeV strip.
- Figure 2: width 0.93 -> 0.88 to keep the float on one page; caption shortened by
  moving the censoring statement into a single clause.
- Text: the cap is quoted as $\mu_{95}=64$ instead of $>60$ (Section 5.1, Table 2 row
  and caption, Fig. 3 caption). The value is pinned exactly at 64 by the scan.
- Comment fix in `make_fig2_v10.py`: the $M_V=20$ GeV nominal island is quoted as
  $\mu_{95}=0.94$--$1.00$, not 0.85--0.89.
- An interpolated $M_V=25$ GeV curve was added to Fig. 3 for inspection and then
  removed after review: it contradicted the statement that no line is drawn across the
  20--30 GeV interval, and its plateau was set by the cap rather than by data.
- Cross-check: `column_stats.csv` in `review/fig23/` reproduces every column statistic
  from `data/GRID_V10.csv`.

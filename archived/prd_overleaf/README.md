# PRD manuscript

Upload the project ZIP using **New Project → Upload Project** in Overleaf. Set the main document to main.tex and select **pdfLaTeX**. The project uses REVTeX 4.2 and BibTeX. A local TeX Live installation can build it with latexmk -pdf main.tex.

The paper is in main.tex, the technical material and top-associated results are in appendices.tex, and the bibliography is in references.bib. The project includes all figures required for compilation.

The manuscript is based on phenomenology_en.md in the parent repository. Numerical tables are in the parent repository's data directory, with provenance recorded in FIGURE_SOURCES.md. The files center_grid_limits.csv and benchmark_roots.csv contain the limits per relic root and the abundance and recoil-rate variations. The files template_validation_limits.csv and template_contour_refit.csv give the independent-template checks. The monojet-only panel in the body uses a cropped view of the existing uncertainty figure.

Before submission, fill in the author and affiliation fields, corresponding author, acknowledgments and funding information, and the archival release link in the data availability statement. Review any disclosure required by the [PRD author guidance](https://journals.aps.org/prd/authors).

The observed exclusion contour uses the reference fast-simulation templates. Appendix C gives the official benchmark acceptance comparison and the independent-template refits. The expected and observed values are those of the existing analysis.

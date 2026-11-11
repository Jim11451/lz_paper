# 图与数据来源 · Figure and data provenance

[中文初稿](phenomenology_zh.md) · [English draft](phenomenology_en.md)

中英文稿使用同一组图、参考文献和参数。`figures` 内含论文中引用的图，`data` 内含中心丰度网格、代表点、截面及数值验证。两版正文均用标准 Markdown 图链接和 `$` 数学标记。

Both drafts share the figures, bibliography, and parameter choices. The `figures` directory contains the graphics cited in the drafts. The `data` directory contains the central relic grid, benchmarks, cross sections, and validation tables.

| Figure | Source analysis and role |
|---|---|
| 1 | `monojet_manuscript_20261106/MANUSCRIPT.md`. Truth spectrum in the two flavor textures. |
| 2 | `monojet_mchi_scan_20261106/REPORT.md`. Fixed-mass slope and pole contributions to the thermal average. |
| 3, B1, B2 | `truth_xsec_scan_20261106/REPORT.md`. Common hard MET selection, loose selection, and the LZ rate slice. |
| 4, B3 | [New central relic grid](data/center_grid_limits.csv). Both projections use roots at $\Omega_\chi h^2=0.1200$. The scan includes both kinematic branches and returns only on-shell roots in this main mass grid. |
| 5–8, A2 | `lz_mixing_uncertainty_20261110/REPORT.md`. Expected bands, measured abundance propagation, mixing, LZ rate variation, and the single-top energy test. |
| A1 | `pseudoDiracB_20261004/REPRODUCTION_REPORT.md`. Independent calculation in the units of the reference paper. |
| A3 | `lz_model_checks_20261110/CHECKS.md`. Conditional estimate of the local excited-state fraction. |
| C1–C4 | `monojet_cms_benchmark_20261107/REPORT.md`. Public signal templates, independent cutflow, and reconstructed MET. |
| C5 | [Loop template replicas](data/template_replica_comparison.csv). Replot at one fixed central relic point using the reference-template limits and the same signal scale for all replicas. |
| C6 | [Three-benchmark template refits](data/template_validation_limits.csv) and [all 66 bins per benchmark](data/template_validation_bins.csv). Independent loop generation with different stratification boundaries and a fresh tree sample. |
| D1–D2 | [Low-mass branch scan](data/light_relic_branches.csv) and [single-top simulation](data/single_top_pilot.csv). Branch availability within the abundance band and truth shapes. |

代码格式标出的分析报告路径相对于原研究工作区的 `outputs/` 目录。Paths shown as code refer to reports in the original analysis workspace under `outputs/`.

## 本次换图与范围 · Updated figures and scope

- 新的图 4、B3 使用 Planck 中心丰度重新逐点求根，图 C5 固定同一个中心丰度点比较三套模板。丰度误差和 LZ 率变化单列在图 5、图 7 和对应的数据表中。
- The earlier $t\bar t+\mathrm{MET}$ exclusion contours depend on branch assignments and a background treatment that still need validation. The drafts use the independently simulated truth cross sections and the verified branch structure for the top-pair discussion.
- 作者名单、单位和致谢等待课题组确认。正式联合 LZ 似然、顶夸克通道的实测上限和模型专属探测器系统误差属于后续发表核对项。

## 分析脚本与数据 · Analysis scripts and data

原分析脚本位于研究工作区的 `outputs/phenomenology_paper_20261110/`，依赖该工作区的模型和拟合代码。The analysis scripts are in `outputs/phenomenology_paper_20261110/` in the analysis workspace, where their model and likelihood inputs are available.

- `build_center_grid.py` builds the central relic grid using the CalcHEP/micrOMEGAs model and the audited photon subtraction.
- `prepare_figures.py` assembles the shared figures from the grid, the CMS fit and the archived plots.
- [Raw central root search](data/center_grid_roots.jsonl) · [Central limits per root](data/center_grid_limits.csv) · [Summary](data/center_grid_summary.json)
- [Benchmark roots and limits](data/benchmark_roots.csv) · [Uncertainty propagation](data/branch_uncertainties.csv) · [Off-shell truth cross sections](data/off_shell_ttmet.csv)
- `run_template_validation.py` prepares independent templates and `fit_template_validation.py` refits the CMS limits.
- [Sample statistics](data/template_validation_runs.csv) · [Combined MET intervals](data/template_validation_tail.csv) · [Contour refit](data/template_contour_refit.csv)

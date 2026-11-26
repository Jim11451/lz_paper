# LZ 高能核反冲与伪 Dirac 暗物质唯象

本文研究一个质量加权矢量中介子模型，比较 LZ 高能核反冲参考率、Planck 热丰度条件和 CMS monojet 搜索的灵敏度。当前版本包含三个 monojet 代表点的独立模板检验及对顶夸克伴随产生的复核。

- 中文论文 [Markdown](archived/phenomenology_zh.md) · [PDF](phenomenology_zh.pdf)
- English manuscript [Markdown](archived/phenomenology_en.md) · [PDF](phenomenology_en.pdf)
- [图表与数据来源](archived/FIGURE_SOURCES.md)
- [组员的顶夸克伴随产生报告复核](archived/ttbar_report_review_zh.md)
- [PRD LaTeX / Overleaf 稿件](archived/prd_overleaf/README.md) · [对应中文稿](phenomenology_prd_zh.md)
- 加入顶对结果的新稿（2026-11-26） [改动标记版](ttbar_paper_update_20261126/xenon_monojet_ttbar_改动标记.md) · [中文变更说明](ttbar_paper_update_20261126/变更说明_中文.md) · [英文原稿](ttbar_paper_update_20261126/xenon_monojet_ttbar.md)

中英文稿共用 `figures/` 中的图片和 `data/` 中的扫描结果与验证数据。修改正文时编辑 Markdown 源稿，换图时同步更新两版 PDF 和图表来源。

完整计算代码、模型、公开 CMS 输入、分箱信号模板及运行说明见 [可复现计算包](reproducibility/README.md)。离线拟合入口为 `python reproducibility/reproduce.py all`，先按包内说明安装依赖。文件完整性与三个 monojet 基准点由 GitHub Actions 自动核对。

The [reproduction package](reproducibility/README.md) includes analysis sources, model files, numerical inputs, and commands for offline likelihood reconstruction and fresh external-software jobs. Validation records distinguish the tested offline calculations from external simulation builds.

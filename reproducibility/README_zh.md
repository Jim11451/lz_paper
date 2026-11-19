# 论文计算复现指南

本计算包覆盖参考论文的 LZ 谱复现、质量加权矢量模型、光子混合后的 LZ 归一化、Planck 丰度求根、树级和圈图信号生成、Delphes 切选、CMS 分箱似然、官方基准验证、独立样本与合并模板、二维投影及误差分析。ttbar 与 single-top 的补充计算保留各自的验证范围。

## 从 GitHub 下载后的运行

在仓库根目录使用 Python 3.12 创建虚拟环境，安装 `reproducibility/requirements.txt`。然后运行

```bash
python reproducibility/reproduce.py verify
python reproducibility/reproduce.py all
```

`verify` 核对归档代码和输入的 SHA-256。`all` 实际重算三个 monojet 点的 expected/observed 上限、独立 A/B/合并模板的逐 bin 产额与拟合、434 个物理解的合并模板上限、中央投影、官方 CMS benchmark 和 ttbar 光子相消附近的固定模板 expected 结果。生成文件保存在 `build/reproducibility/`，原始输入保存在 `reproducibility/outputs/`。

也可单独运行 `benchmarks`、`validation`、`contour`、`figures`、`cms-benchmark` 和 `cancellation`。`figures` 对部分历史图片执行归档拼装，其数值来源和原始出图脚本已随计算包保存。

## 从模型重新计算

使用 Linux、micrOMEGAs 7.1.4 和可用的 C/Fortran 编译器，通过 `build_model.py` 在指定的 micrOMEGAs 目录创建新项目。该命令使用已归档的模型文件。`relic_local.py` 接收项目路径、$M_V$、$g_t$、$d_\gamma$、LZ 率倍率和激发态比例，在本地逐次调用 `darkOmega` 求解丰度。

```bash
python reproducibility/build_model.py --micromegas /path/to/micromegas_7.1.4
python reproducibility/relic_local.py \
  --project /path/to/micromegas_7.1.4/LZPhotonReproduction \
  --mv 100 --gt 2 --d=-0.00013 --out build/relic_example.json
```

该例的已有参考解为 $m_\chi=20.811786$ GeV、$g_\chi=0.977323$。默认求根范围为 $20\le m_\chi\le100$ GeV 和 $0.1\le g_\chi\le1.5$，同时记录在壳、离壳根。扫描范围是数值设置，相消附近无根的解释必须保留这一范围。

零光子混合的直接核反冲实现位于 `work/pseudoDiracYukawa_build/lz_recoil.c`，参考模型实现位于 `work/pseudoDiracB_build/`。前者可在 micrOMEGAs 内编译后重新生成质量归一化表。`relic_local.py` 使用随包保存的基准表，并重新计算光子混合的同位素积分修正。

## 信号模拟及完整切选

圈图 UFO、R2 修正、Ward 检验源代码与日志均在 `outputs/monojet_loop_20261103/`。`generate_hard.py` 为 MadGraph5_aMC@NLO 3.6.6 提供新的树图、圈图、ttbar 在壳和离壳生成入口。Pythia8 8.312、Delphes 3.5.0 的重建脚本、不可见粒子设置、AK4 喷注定义、逐步切选和 NPZ 模板打包实现均已保存。原始运行卡、随机种子、分层边界及参考截面一起归档。

这些外部软件需要按英文指南安装。历史任务脚本保留工作站安装路径，完整外部模拟需要在新机器上配置软件路径，并重新生成大型 LHE/ROOT 文件。本次移植已实际验证离线统计和出图入口，尚未在全新 Linux 软件环境下完成从模型编译到探测器模拟的整条重跑。这个验证范围记录于 `VALIDATION.json`。

## 论文使用时的范围

LZ 条件匹配真值参考率，丰度条件逐分支求根。CMS 的置信上限在这些参数切片上计算。独立样本结果、合并模板结果及原模板结果分别保存。ttbar 固定模板灵敏度继承组员的效率和背景处理，single-top 保留高能切口的探索性检验。详细物理和数值限制见主稿、ttbar 核查与各计算报告。

仓库已包含统计复算所需的分箱计数、协方差、截面、公开数据和独立样本摘要。安装的软件二进制和大型逐事件文件需要由代码生成。论文引用时记录最终使用的 Git commit；长期 DOI 可在正式归档 release 后补入。

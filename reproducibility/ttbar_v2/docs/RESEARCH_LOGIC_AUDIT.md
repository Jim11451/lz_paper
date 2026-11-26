# 研究逻辑审计：LZ-event / PseudoDirac × CMS-EXO-22-014

日期：2026-11-21　性质：只读审计。未运行生成、未修改代码/数据/冻结结果。

## 0. 总表

| # | 研究环节 | 当前完成程度 | 证据（文件） | 缺失内容 | 对最终结论的影响 |
|---|---|---|---|---|---|
| 1 | UFO / 模型参数 | **已完成** | `PseudoDiracFlavourEFT.fr`、`PseudoDiracFlavorEFT_UFO_loop/`（137 顶点）、`STEP53_CHECKS.md` | 味加权 $g_{Vq}=g_t m_q/172$ 是模型假设，非 CMS 简化模型 | 我们的模型与 CMS benchmark 不同，不能直接对比 |
| 2 | $\kappa_{\rm LZ}$ | **已完成** | `data/relic/kappa_lz_gN_v2.csv`、`lz_recoil2.c`、`kappa_from_lz2.py` | 无（8 点闭合 1.0005；$\Gamma$ 闭合 $4\times10^{-7}$） | — |
| 3 | 遗迹丰度 | **已完成（网格）** | `band_v2.csv`(70)、`band_v2_ext.csv`(126)、`solve_band_v2.py` | $g_t$ 只扫 5 个值（非 35×29） | 排除图分辨率受 $g_t$ 网格限制 |
| 4 | 宽度 / BR$_{\rm inv}$ | **已完成** | `widths_v2.csv`(70)、`validate_widths.py`、`width_validation.csv` | 无（244 点 $\max|\Delta\Gamma|=3.9\times10^{-5}$） | — |
| 5 | 信号产生 | **已完成（统计）** | `phase14/root/*.root`、`SIGNAL_REPRO_ALL_POINTS.md` | 逐事件不可复现（种子未存） | 只能做统计比较 |
| 6 | Delphes 重建 | **仅近似** | `Delphes 3.5.1` + `delphes_card_CMS.tcl` | 非 PUPPI / DeepJet，无 b-tag SF、JES/JER 修正 | 效率与 CMS 不同，绝对产额有偏 |
| 7 | CMS 对象定义 | **仅近似** | `final_plot.py: shape()`：jet $p_T>30$、$|\eta|<2.4$、`Jet.BTag>0` | PUPPI、DeepJet WP、SF、JES/JER、$\eta<4.0$ 的前向 jet 计数 | 与 CMS 的 $n_{\rm jet},n_b$ 定义不完全一致 |
| 8 | CMS 选择切 | **部分完成** | 同上：无轻子、$n_j\ge3$、$n_b\ge2$、MET>250、$m_T^b>140$ | **多出两条论文 SR 表里没有的切**：$p_{T,0}/\sum p_T<0.5$ 与 $\min\Delta\phi({\rm jet},{\rm MET})>0.8$ | 我们的效率偏低、形状被改动 |
| 9 | SR / CR 定义 | **部分完成** | `build_workspace.py`：11 SR + 8 CR，名字与 CMS 区域一致 | CR 直接取 HEPData 计数，未自己实现；CR 表无信号行（CMS 在 CR 里也放信号） | CR 约束与 CMS 不等价 |
| 10 | Binning | **已完成** | AH 15×20 GeV（250–550），与 `postfit_*SR.yaml` 一致 | SL/DL 只引用表，无自家模板 | 仅 AH 2b 有完整链 |
| 11 | HEPData 背景输入 | **仅近似** | `build_workspace.py: read()` 只取 `value`，`errors` 从不读 | 无 pre-fit、无 bin 级误差、无相关 | 背景不确定度被低估 |
| 12 | HEPData 信号 benchmark | **可用但未用于校验** | `postfit_*SR.yaml` 有 `Signal (scalar, mφ=100 GeV)` 行 | 我们只在似然里用它，没拿它校对我们的接受度 | 少了一次能做的 B 层检验 |
| 13 | 我们的 signal templates | **部分完成** | `sig_MV*.root` → `fp.shape()`，15 bin | **只做了 AH 0ℓ2b 一个区**；SL 6 区、DL 2 区没有自家模板 | 排除网格只覆盖一个区 |
| 14 | 信号效率 | **已完成（自洽）** | `SIGNAL_REPRO_ALL_POINTS.md`：$R_\varepsilon=0.972\pm0.027$，14 点闭合 | 非 CMS 效率（对象定义不同） | 不能与 CMS 的 $\varepsilon$ 直接比 |
| 15 | 统计模型 | **近似** | `phase12/fit_cr.py`：泊松 + 6 个高斯归一化 | 无形状 nuisance、无相关矩阵 | expected limit 不可比 |
| 16 | Nuisance 参数 | **近似** | `NORM_FREE` 6 个 × 10% 平直惩罚 | CMS 有上百个（JES、b-tag、形状…） | 灵敏度被高估 |
| 17 | 系统误差 | **未完成** | 无 | JES/JER、b-tag、$\ttbar$ 形状、亮度、PDF、理论 | 42% 差距的主因 |
| 18 | Expected limit | **仅有近似实现，且对象错位** | `0.170 pb = 0.16016×1.06241` | Asimov + post-fit + CMS benchmark 信号 | **不是我们模型的预期限值** |
| 19 | Observed limit | **部分完成** | `0.544 pb = 0.5117×1.06241`，CMS 0.532（+2.2%） | 同 18 | 是 CMS benchmark 信号的观测限值 |
| 20 | 最终 exclusion grid | **部分完成** | `grid_v2.npz`(616 点，244 有效)、`map_v2.py` | **单区（AH 2b）15-bin 似然**，非 19 通道；绝对标定未验证 | 与我们自己报的 0.544 不是同一个统计对象 |

## 1. 三个层次

### A. Signal generation reproducibility —— **完成**

证据：14 点全部从 UFO 走完 MG5 3.6.6 → Pythia 8.312 → Delphes 3.5.1，σ 一致到 1%，
效率比加权平均 $-4.4\%\pm3.6\%$，MET/领头喷注形状 $p>0.1$（`SIGNAL_REPRO_ALL_POINTS.md`）。

局限：逐事件不可复现；jet 多重数在任何点都无法检验；$M_V=40$ 的 2k 样本量不足（18 个 SR 事例）。

### B. CMS analysis recasting —— **未完成**

- 对象定义是 Delphes 的 CMS 卡近似，不是 PUPPI + DeepJet + SF；
- 选择比论文的 SR 定义**多两条切**（$\alpha_T$ 式与 $\Delta\phi$），会系统性压低效率；
- 只实现了 AH 0ℓ2b 一个区；SL 六个区、DL 两个区没有自家模板；
- CR 是直接引用 HEPData 的计数，不是我们自己选出来的。

**结论：B 层只做到了"一个区、近似对象、近似选择"，不能称为完成 recast。**

### C. CMS statistical reproduction —— **未完成**

- 似然只有 6 个归一化 nuisance（±10% 平直），CMS 是上百个含形状与相关的 nuisance；
- 输入全是 **post-fit**，且 CR 被二次使用；
- expected 用单个背景-only Asimov，没有伪实验、没有能带；
- 输入没有 pre-fit 模板、没有 MC 统计误差、没有形状变化。

**唯一可以说的**：在"CMS 自己的 benchmark 信号 + CMS 自己的 post-fit 背景 + 我们的简化似然"下，
observed 限值 0.544 pb 与 CMS 0.532 pb 差 2.2%——这是一个**统计机器**的旁证，不是 C 层复现。

## 2. 一个必须先纠正的身份错位

`cmsrepro/phase12/build_workspace.py` 的信号样本来自 HEPData 表的
`Signal (scalar, mφ=100 GeV)` 行（第 78–80 行：`elif raw.startswith("Signal"): sig = v`），
然后在第 100–103 行把它作为 `mu` 的模板放进 19 个通道。

**因此 0.544 pb 与 0.170 pb 是"CMS benchmark 标量中介子（$m_\phi=100$ GeV）"的限值，
不是我们 PseudoDirac 模型（矢量 $V_b$ + 伪狄拉克费米子）的限值。**

这与排除网格（`map_v2.py`）是两套完全不同的对象：

| | 信号 | 统计模型 | 数值 |
|---|---|---|---|
| 论文里报的限值 | CMS benchmark（$m_\phi=100$） | 19 通道 + 6 个 10% nuisance | 0.544 / 0.170 pb |
| 排除网格 | 我们的模型（14 个 $M_V$ 点） | **单区 AH 2b，15 bin** | $\mu_{95}$ 逐点 |

两者不能互相引用，也不能说"我们的模型被 CMS 排除到某个 $\sigma$"。

## 3. HEPData 与 pre-fit

### 3.1 22 张表分别是什么

| 组 | 张数 | 内容 |
|---|---|---|
| AH SR | 3 | 0FJ、1FJ、2b，MET 15 bin |
| AH CR | 4 | QCD、tt(1ℓ)、W+jets、Z(2ℓ) |
| SL SR | 6 | 0FJ($t\le0$)、0FJ($t>0$)、1FJ($t\le0$)、1FJ($t>0$)、2b($t\le0$)、2b($t>0$) |
| SL CR | 2 | W+jets、tt(2ℓ) |
| DL SR | 4 | NN 分布：ttDM DF/SF、tDM DF/SF |
| DL CR | 2 | ttZ（$N_{\rm jet}$–$N_b$）、DY（NN） |
| 极限 | 1 | 标量/赝标量的 observed、expected、±1σ、±2σ |

我们用掉的：11 SR（AH 3 + SL 6 + DL ttDM 2）+ 8 CR = 19 通道；跳过 DL tDM 两张
（"different signal model"，`build_workspace.py` 里显式打印 skip）。

### 3.2 post-fit 还是 pre-fit

- **21 张产额表全部是 post-fit**：命名、逐 bin 分项和 = `$Background$`（21/21 比值 1.0000）、
  8 个 CR 的 Data/Background = 0.9997–1.0087；
- 每张表同时给 **Data**（观测计数）与 **benchmark 信号**（SR 表有，CR 表没有）；
- **没有 pre-fit 的逐 bin 模板**（2025 记录）；2019 记录（ins1712378，35.9 fb⁻¹）有 pre-fit 总数，
  但亮度、分 bin、选择都不同，不能移植。

### 3.3 HEPData 提供了什么、没提供什么

| 项目 | 是否提供 |
|---|---|
| 逐 bin 背景（post-fit，10 个过程 + 总数） | ✅ |
| 逐 bin 观测数据 | ✅ |
| benchmark 信号逐 bin | ✅（仅 SR） |
| pre-fit 逐 bin | ❌ |
| MC 统计误差（单独） | ❌（只有一个 `bkgSum` 合并误差） |
| 系统误差的形状变化（±1σ 模板） | ❌ |
| nuisance 相关矩阵 | ❌ |
| 官方 workspace / datacard / likelihood | ❌ |

### 3.4 0.170 与 0.544 用的到底是什么

```
0.544 pb = 0.5117 (μ95_obs) × 1.06241 pb
0.170 pb = 0.16016 (μ95_exp) × 1.06241 pb
```

输入：11 SR + 8 CR 的 **post-fit** 分项；信号 = **CMS benchmark**（$m_\phi=100$）；
误差 = 6 个归一化因子各 ±10% 高斯；expected = **背景-only Asimov 单点**；
CR 中的信号为零（表里没有信号行）。

### 3.5 为什么与 CMS 差 42%

| 因素 | 量级 |
|---|---|
| 缺 JES / b-tag / $\ttbar$ 形状 / 亮度 / 理论误差 | **主导** |
| post-fit 背景代替 pre-fit | 少量（同实验 2019 记录实测 SR 只差 +3.7%） |
| CR 二次使用 + 只有 10% 平直先验 | 使背景不确定度被低估 |
| expected 只有中位 Asimov、无伪实验能带 | 无法给 ±1σ |

## 4. 我们真正缺什么

### A. 公开可得（现在就能补）
1. 论文的 SR 定义表（已有 PDF/ar5iv）——用来逐条对齐选择；
2. HEPData 的 benchmark 信号逐 bin（已有）——用来校验接受度；
3. 2019 记录的 pre-fit/post-fit 对照（已有）——用来量化 post-fit 偏差；
4. 论文的接受度/产额表（若有）——用于 B 层对账。

### B. 需向作者申请
1. 完整协方差矩阵或 pyhf workspace；
2. pre-fit 逐 bin 模板与 MC 统计误差；
3. 形状系统误差的 ±1σ 模板；
4. 各 SR 的信号接受度（按 $m_\phi$、$m_\chi$）。

没有 B，expected limit 只能做到"合理"，做不到"官方"。

### C. 我们自己的代码可以独立完成
1. 精确化对象定义（PUPPI/DeepJet 的近似实现、SF、JES 修正）；
2. 让选择与论文 SR 表逐条对齐（去掉/论证两条多余切）；
3. 把信号模板扩到 11 个 SR；
4. 把排除网格从"单区"换成 19 通道似然（用我们自己的信号）；
5. 用 HEPData 的 benchmark 信号做一次接受度对账。

### D. 只能近似
1. 与 CMS 可比的 expected limit；
2. 由系统误差驱动的能带；
3. 背景形状的完整相关。

## 5. 建议的执行顺序（最短路径）

1. **先纠正身份**（半天）：在代码与论文里把"CMS benchmark 限值"与"我们模型的网格"彻底分开命名；
   论文里凡引用 0.544/0.170 的地方必须写清是 benchmark 信号。
2. **B 层对账**（1–2 天）：用 HEPData 的 benchmark 信号行，比较我们在同一 SR 的接受度
   （$s_{\rm bin}$ 形状与总数）；这一步不需要新样本，只需要已有 ROOT 重算选择。
3. **选择对齐**（1 天）：逐条对照论文 SR 表，确认两条多余切的来源；
   给出"去掉它们后效率变化多少"的定量结论。
4. **统计对象统一**（2–3 天）：把网格的 $\mu_{95}$ 从单区换成 19 通道（用我们的信号），
   这样论文里的限值与网格才是同一个统计量。
5. 只有在 1–4 完成后，才讨论是否增加样本或数字化 pre-fit 图。

## 6. 直接回答

1. **我们真正完成了什么？**
   完成了 A 层（信号产生链的统计复现），以及模型侧的一整套自洽计算（$\kappa_{\rm LZ}$、丰度带、宽度、BR$_{\rm inv}$），
   外加一个能复现 CMS observed limit 到 2.2% 的**简化似然**。

2. **是否完成 CMS analysis recasting？**
   **没有。** 对象定义是近似，选择多两条切，只覆盖 1 个 SR，CR 直接引用表。

3. **是否复现 CMS 官方 expected limit？**
   **没有。** 0.170 vs 0.295（−42%），且它描述的是 CMS 的 benchmark 信号，不是我们的模型。

4. **是否验证了自己的物理 exclusion grid？**
   **没有。** 网格用的是单区 15-bin 似然，与我们自己报的 19 通道限值不是同一个统计量；
   绝对标定（$\sigma$、$\varepsilon$、BR）虽自洽，但未与 CMS 做过同区对账。

5. **当前最关键的三个阻塞问题？**
   ① **信号身份错位**（benchmark vs 我们的模型混在同一套数字里）；
   ② **选择/对象未与 CMS 对齐**（两条多余切 + 近似对象定义）；
   ③ **缺系统误差与相关**，导致 expected limit 不可比。

6. **下一步唯一最值得优先做的工作？**
   把身份错位在代码与文档里清除，并用 HEPData 的 benchmark 信号做一次**同区接受度对账**——
   这是唯一能用公开数据检验 B 层的动作，也是后面所有结论的前提。

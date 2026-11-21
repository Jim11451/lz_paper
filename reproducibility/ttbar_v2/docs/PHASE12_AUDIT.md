# PHASE 12 expected limit 审计

审计对象：`cmsrepro/phase12/{build_workspace.py, fit_cr.py, phase12_results.json}`。
结论先行：**0.170 pb 不是 CMS 意义上的 expected limit**，它是"用公开 post-fit 表 + 6 个 10% 归一化先验 + 背景-only Asimov"算出的灵敏度估计。四条质疑全部属实。

## 1. 四条说法的核对

| # | 说法 | 核对 | 代码依据 |
|---|---|---|---|
| 1 | `build_workspace.py` 只读中心值，不导入逐 bin 误差 | **属实** | `read()` 只取 `x["value"]`，从未读 `x["errors"]`；`fit_cr.py` 里也没有 bin 级约束 |
| 2 | 6 个高斯归一化约束（10%），其余背景固定 | **属实** | `NORM_FREE = [tt1l,tt2l,Wjets,QCD,Zll,Znn]`；`profile()` 手写惩罚 `((k−1)/0.10)²`；`singlet/VV/ttV/other` 不进似然 |
| 3 | 模板是 post-fit，CR 观测又被放进同时拟合 | **属实** | 输入全部是 `postfit_*.yaml`；`channels` 同时含 SR 与 CR |
| 4 | expected 用背景-only Asimov，不是伪实验 | **属实** | `b_pars = (mu=0, 所有 k=1)` → `model.expected_data(...)` → 单点 `crossing()` |

## 2. CR 信息是否被双重使用

**是，而且是两层叠加：**

1. **隐式**：SR/CR 的逐过程模板本身就是 CMS 用这些控制区做同时拟合后的**后拟合值**。CR 的信息已经"固化"在模板里。
2. **显式**：我们的似然又把同一批 CR 的计数放进 `observations`，用 6 个自由归一化因子去约束它们。

后果：

- $\hat\kappa$ 全在 0.998–1.038，**不是因为数据约束强，而是因为模板已经是拟合结果**——似然在 $\kappa=1$ 附近本来就是极小值；
- 加 CR 只把 observed 从 0.535 拉到 0.512（−4%），说明 CR 的"再约束"几乎不提供新信息；
- 更关键的是：post-fit 模板已经把 CR 的约束**预支**了，我们再叠加 10% 平直先验，等于**把同一份约束算了两遍**，使背景不确定度被系统性低估。

这不是"用法错误"，而是**公开数据的固有限制**：只要输入是 post-fit，就无法避免。

## 3. Asimov 期望限值的统计一致性

方法本身是标准的：背景-only Asimov + 渐近 CLs 给出**中位**期望限值；`qmu`/`qb` 的实现与 Cowan–Cranmer–Gross–Vitells 公式一致（`cls()`、`crossing()`）。

问题不在统计，在输入与完备性：

| 项 | 状况 |
|---|---|
| Asimov 数据集 | 用**后拟合**预期构造 ⇒ 不是"看到数据之前的可实现样本" |
| 涨落 | 中位 Asimov 本身无泊松涨落；限值几乎完全由 10% 平直先验撑起 |
| 能带 | 只有中位数，**没有 ±1σ/±2σ 带**（CMS 的 0.277 是带能带的中位值） |
| 模型 | 无形状系统 ⇒ 似然对 bin 间的数据-MC 差异几乎没有惩罚 |

所以：**统计公式无误，输入不满足"expected limit"的前提**。

## 4. 误差清单

| 来源 | 是否包含 |
|---|---|
| 6 个归一化的 10% 高斯（tt1l, tt2l, Wjets, QCD, Zll, Znn；跨 bin 全相关） | ✅ |
| 泊松 bin 统计 | ✅（但 Asimov 中位样本无涨落） |
| HEPData 的逐 bin stat+syst | ❌ **完全未使用** |
| JES / JER | ❌ |
| b-tagging（含味依赖） | ❌ |
| $t\bar t$ 形状 / 重化-分解标度 | ❌ |
| W+jets 形状 | ❌ |
| QCD 估计方法误差 | ❌ |
| 亮度 1.6% | ❌ |
| PDF、ISR/FSR、pileup | ❌ |
| MC 统计、信号接受度、理论截面 | ❌ |
| 区域间相关矩阵 | ❌（10% 先验是全相关的最粗替身） |

## 5. 0.170 pb 该叫什么

**不能叫 expected limit。** 准确表述：

> "在公开 post-fit 表、6 个 10% 归一化先验、无形状系统误差、背景-only Asimov 的简化模型下得到的**中位期望灵敏度估计**。"

它**不可**与 CMS 的 0.277（0.295 pb）比较，也不应写成"我们比 CMS 敏感 1.7 倍"——那是误差模型差异，不是物理。

## 6. 对两份文档的更正

| 文件 | 原文 | 更正 |
|---|---|---|
| `READM_0p170.md` §4 | "每个 SR 的 bin 间误差用 HEPData 的 stat+syst 逐 bin 误差，独立处理" | **错**。19 通道拟合**完全没有**使用 bin 级误差，只有泊松 + 6 个 10% 先验（逐 bin 误差只在 PHASE 11 的 `sys_likelihood` 15-bin 版本里用过） |
| 同上 | 未提 Asimov/伪实验 | 补："expected 为背景-only Asimov 的中位值，无 ±1σ 带" |
| `PHASE12_REPORT.md` | 只写"缺 JES/b-tag/形状" | 补一节"方法学限制"：post-fit 模板 + CR 双重使用 + 无 bin 级误差 + Asimov 单点 |

（两份文件都是说明文档，不是冻结结果；`phase12_results.json` 与网格未动。）

## 7. 数字化 CMS pre-fit 图（Fig. 3/4）值不值得

| 能得到 | 不能得到 |
|---|---|
| 每个 SR 的**总**背景 pre-fit 逐 bin 值（AH 15 bin、SL 5 bin） | 逐过程分解（无法重建 CR 约束） |
| 图分辨率约 1–3%（AH）、3–5%（SL，对数轴） | 逐 bin 系统误差及其相关 |
| post-fit 与 pre-fit 总产额的差值（稳健性检查） | 形状系统（JES/b-tag/tt̄ 形状） |

定量估计：SR 的 post-fit 相对 pre-fit 只差 $\kappa\approx1.00$–$1.04$，即 **1–4%**；把总背景换回 pre-fit，$\mu_{95}^{\rm exp}$ 大约从 0.160 变到 ~0.165，**与 0.277 仍差 40%**。

**实测锚点（新增）**：CMS 2019 年的同通道分析（HEPData **ins1712378**，35.9 fb⁻¹，JHEP 03 (2019) 141）
在同一张表里**同时公布 pre-fit 与 post-fit**：

| 区域 | pre-fit（首 bin） | post-fit | 变化 | Data |
|---|---|---|---|---|
| AH 2b SR | 744.5 | 771.9 | **+3.7%** | 782 |
| SL 1μ W CR | 3963.2 | 4526.0 | **+14.2%** | 4582 |

SR 的 3.7% 对应 $\mu_{95}^{\rm exp}$ 仅 +2%（0.160→0.163）；CR 的 14% 说明"post-fit 贴数据"在
控制区确实很大，但它不直接进入 SR 的期望产额。

**结论：作为"闭合 42% 缺口"的手段，不值得做**（实测上限 ~2%）；作为"post-fit 与 pre-fit 总产额差
3–4%"的一句稳健性说明，可以直接引用 ins1712378 的数字，不必自己数字化。

## 8. 建议

1. **论文只报 observed**（0.544 pb，加 CR；或 0.535 pb，只用 SR），expected 放附录并明确标注"公开 post-fit 输入下的灵敏度估计，不可与 CMS 0.277 比较"；
2. 不要花时间数字化 Fig. 3/4（收益 <5%，无法触及主因）；
3. 若审稿人坚持要可比 expected，唯一现实路径是拿到 CMS 的内部协方差/系统误差表（非公开），公开渠道做不到。

# 最新 UFO 的 monojet 圈图截面

2026-11-03。使用 MadGraph5_aMC@NLO 3.6.6，完整夸克圈质量依赖；PDF 为 `nn23lo1`。计算采用此前的树级 LZ＋relic 候选参数，不是后来仅更新 LZ 强度的参数。

## 1. 上传模型检查

已找到 `/home/cms/PseudoDiracFlavorEFT_UFO_loop` 和同名压缩包。原版虽然能够生成圈图，但缺少新矢量媒介子的 $gggV$ 有理项。原件保留，在独立副本中参照同模型的光子 $ggg\gamma$ 反项，增加六个独立味耦合的对应项：

$$
C_{R_2}^{(q)}=\frac{i g_{Vq}g_s^3}{48\pi^2},\qquad \mathrm{colour}=d^{abc}.
$$

在 B 点、1 TeV 部分子能量的胶子 Ward/BRS 检查中：

| 模型 | MadGraph 报告的 BRS/matrix 比值 | 结果 |
|---|---:|---|
| 上传原版 | $4.41\times10^4$ | 未通过 |
| 独立 R2 修正副本 | $6.27\times10^{-24}$ | 通过 |

因此下列物理结果使用修正副本。该修正只针对本次闭合夸克圈矢量流过程，不声称完成整个模型的通用 NLO 构造。原始和修正模型都保存在 `model/`；检查日志保存在归档内。

## 2. 计算过程和切选

计算

$$
gg\to gV,\qquad V\to\chi_1\chi_2,
$$

MadGraph 生成命令为

```text
generate g g > Vb g PDB=1 QED=0 [noborn=QCD]
```

采用窄宽度近似

$$
\sigma_{\rm loop}^{\rm monojet}
=\sigma(gg\to gV)\,\mathrm{BR}(V\to\chi_1\chi_2).
$$

这次未直接积分离壳 $gg\to g\chi_1\chi_2$。所选 86–88 GeV 点满足不可见衰变阈值且宽度较窄。固定 $m_{\chi_1}=35$ GeV、$\delta=1$ MeV，实际暗顶点为 $g_\chi/2$；夸克纹理与此前一致：$g_{Vq}=g_t\widehat m_q/(172\ \mathrm{GeV})$。

所有样本要求 $p_T^g>200$ GeV、$\lvert\eta_g\rvert<4.5$。在本两体产生、不可见衰变近似下，暗物质对 MET 等于 $p_T^V=p_T^g$。每点生成 1000 个事件，下面的误差仅为积分误差，不包括尺度、PDF、高阶或探测器不确定度。

## 3. 已完成的主要结果

13.6 TeV 下：

| 点 | $M_V$ [GeV] | $g_t$ | $g_\chi$ | $\sigma(gg\to gV)$ [fb] | 不可见分支比 | 圈图 monojet [fb] |
|---|---:|---:|---:|---:|---:|---:|
| A | 87.530 | 1.61770 | 0.200 | $393.51\pm2.47$ | 0.60994 | $240.02\pm1.51$ |
| B | 87.183 | 1.06994 | 0.300 | $171.60\pm1.27$ | 0.88890 | $152.54\pm1.13$ |
| C | 86.048 | 0.31268 | 1.000 | $14.575\pm0.091$ | 0.99902 | $14.560\pm0.090$ |

同一 B 点在 **13 TeV** 下的圈图 monojet 为

$$
\sigma_{\rm loop}^{\rm monojet}=135.15\pm0.73\ \mathrm{fb}.
$$

只保留顶夸克生产耦合、保持 B 点用于换算的物理不可见分支比不变，13.6 TeV 的结果为 $145.15\pm1.36$ fb。与完整六味的 152.54 fb 相比，确认了顶圈主导。这个对照包含味间振幅干涉；其差值不能简单解释成其他味独立截面的和，也不是另一个已自洽重算衰变与 relic 的模型点。

## 4. 与此前树级 monojet 比较

B 点、13.6 TeV、同样的硬 jet 选择下：

$$
\sigma_{\rm tree}=33.47\ \mathrm{fb},\qquad
\sigma_{gg\ \rm loop}=152.54\ \mathrm{fb},
$$

$$
\sigma_{\rm tree}+\sigma_{gg\ \rm loop}=186.01\ \mathrm{fb}.
$$

圈图约为原树级结果的 4.56 倍；加入该通道后约为原树级的 5.56 倍。$gg$ 圈图与这里的 $qg,q\bar q$ 树级通道初态不同，可在上述精度下相加；这个和不是完整 NLO 预测。

C 点的原树级结果为 3.252 fb，加入圈图后为 17.813 fb。A 点此前未单独生成树级 monojet，因此本次只报告其直接算得的圈图贡献，没有用未验证的缩放值补表。

相比之下，同一 B 点此前的 $t\bar t+$MET 在 13.6 TeV、暗物质对 MET $>200$ GeV 后约为 1550 fb。因此圈图显著提高了 monojet，但本次计算还不足以比较两类实验搜索的最终灵敏度。

## 5. 结果边界和交付

没有加入 shower、匹配、重建 jet、探测器效率或 CMS/ATLAS 似然；不能将这里的产生截面直接等同于实验可见截面或排除结果。这次生产圈图计算也没有完成低能 LZ 耦合的环图/动能混合匹配。

- `results/cross_sections.csv`：原始积分结果，包含顶圈对照与 13 TeV 对照。
- `results/comparison.json`：与已有树级结果的数值比较。
- `remote_results.tar.gz`：参数卡、运行卡、banner、Ward 检查和积分日志。
- `model/`：上传原件和独立修正副本。
- `MODEL_AUDIT.md`：反项修正及 Ward 检查详情。
- `BUILD_NOTES.md`：编译器兼容设置和私有过程的构建修正。

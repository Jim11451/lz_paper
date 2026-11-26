# PHASE 12 近似复现：副本重跑报告

日期：2026-11-21　目录：`cmsrepro/phase12_rerun/`　原 `cmsrepro/phase12/` 未被改动

## 结论

**逐字节复现成功。** 副本重跑生成的 `workspace.json`、`workspace_nocr.json`、`phase12_results.json`
三个文件的 MD5 与原始文件**完全相同**，JSON 结构比较也完全相等。

| 量 | 历史值 | 本次重跑 |
|---|---|---|
| withCR $\hat\mu$ | 0.36431 | 0.36431 |
| withCR $\mu_{95}^{\rm obs}$ | 0.51172 | 0.51172 |
| withCR $\mu_{95}^{\rm exp}$ | 0.16016 | 0.16016 |
| noCR $\mu_{95}^{\rm obs}$ | 0.53516 | 0.53516 |
| noCR $\mu_{95}^{\rm exp}$ | 0.16797 | 0.16797 |
| 极限（withCR） | 0.5437 / 0.1701 pb | 0.5437 / 0.1701 pb |
| 极限（noCR） | 0.5686 / 0.1785 pb | 0.5686 / 0.1785 pb |

## Phase A：隔离副本

```bash
cd /home/yy/lz-event/phenomenology/cmsrepro
cp -r phase12 phase12_rerun
```

复制后逐文件 MD5 比较（`diff` 两个 md5 清单）：**IDENTICAL**。

| 文件 | md5（原 = 副本） |
|---|---|
| build_workspace.py | `978bffa8cf0c473fda4937052319a9b4` |
| fit_cr.py | `2d93ac2f8ae099597ab058ac400314c5` |
| dump_curves.py | `3dd9d952dc9cfe53694e83f62660100a` |
| plot_cr.py | `069d2531ce8d357b2410e68ac561836b` |
| workspace.json | `692de31a409b6fbfdbf8f13c1eaaeb3e` |
| workspace_nocr.json | `01844971626ca4ee97e62bfd5aaa3c65` |
| phase12_results.json | `62ba8fbe24a7e750f8560a6396c3e83a` |
| phase12_curves.json | `1970baa0ae44423d3ba0c0306ca71ae6` |

## Phase B：运行路径检查

两个脚本都用

```python
HERE = os.path.dirname(os.path.abspath(__file__))
```

定位输出，所有写入都是 `os.path.join(HERE, ...)`：

| 脚本 | 写入 | 隔离性 |
|---|---|---|
| build_workspace.py | `HERE/workspace.json`、`HERE/workspace_nocr.json` | ✅ 落在 `phase12_rerun/` |
| fit_cr.py | `HERE/phase12_results.json`；读 `HERE/workspace*.json` | ✅ |

`build_workspace.py` 的 `ROOT = HERE/../..` 只用于**读** `data/cms/hepdata`（输入，只读）。

**未修改任何脚本**：没有硬编码的绝对输出路径，也不需要改。
唯一出现 "phase12" 字样的地方是 `fit_cr.py` 第 12 行的用法示例（docstring，不执行、不写盘）。

其他潜在写盘点已逐一检查：`json.dump` 3 处、`open(...,"w")` 3 处、无 `savefig`、无 `to_csv`。
`dump_curves.py` 未运行（本阶段不需要）。

## Phase C：重跑

环境：`/home/yy/lz-event/phenomenology/tools/pyhfenv/bin/python`（Python 3.11.13、pyhf 0.7.6、iminuit 2.33.0、numpy 2.4.6）

```bash
cd /home/yy/lz-event/phenomenology
tools/pyhfenv/bin/python cmsrepro/phase12_rerun/build_workspace.py
tools/pyhfenv/bin/python cmsrepro/phase12_rerun/fit_cr.py
```

中间检查（build 之后）：

```
SR: 11  CR: 8
skip (different signal model): NN_distribution_DL_tDM_DF
skip (different signal model): NN_distribution_DL_tDM_SF
withCR channels 19  bins 187
noCR   channels 11  bins 99
```

输出时间戳：workspace 07:42:55，results 07:43:04。`fit_cr.py` 自身实测 **2.06 s**（`time` 输出），
时间戳间隔的 9 秒含解释器启动与文件 I/O。

## Phase D：对账

| 检查项 | 结果 |
|---|---|
| workspace.json MD5 | **相同** `692de31a…` |
| workspace_nocr.json MD5 | **相同** `018449716…` |
| phase12_results.json MD5 | **相同** `62ba8fbe…` |
| workspace 结构（`==`） | **True** |
| results 结构（`==`） | **True** |
| 通道 / bin | 19 / 187；11 / 99 |
| 每通道样本数 | 11（10 背景 + 1 信号） |
| NaN / Inf | **无** |
| withCR $\hat\kappa$ 范围 | 0.9977–1.0380（6 个，全部有限） |
| noCR $\hat\kappa$ 范围 | 0.8855–1.0839 |

原始目录未被改动（重跑后复核）：

```
978bffa8…  phase12/build_workspace.py
2d93ac2f…  phase12/fit_cr.py
692de31a…  phase12/workspace.json
62ba8fbe…  phase12/phase12_results.json
```

## 科学边界（必须保留的限定）

1. 本次复现使用的信号仍是 **CMS scalar benchmark（$m_\phi=100$ GeV）**，
   来自 HEPData 产额表的 `Signal` 行，**不是我们自己的暗物质模型信号**。
2. 因此 0.170 pb 是"该 benchmark 信号在我们的简化似然下的期望灵敏度"，**不是** CMS 官方
   expected limit（官方 0.295 pb），也**不是**我们模型的 exclusion limit。
3. 本次只证明了：**同一份输入、同一套脚本、同一环境，能逐字节重出同一组数字**。
   它验证的是流程的可重复性，不是物理正确性，也不构成 CMS 统计复现。

## 文件

```
cmsrepro/phase12_rerun/         副本（本次全部输出）
cmsrepro/phase12_rerun/workspace.json         md5 692de31a…
cmsrepro/phase12_rerun/workspace_nocr.json    md5 018449716…
cmsrepro/phase12_rerun/phase12_results.json   md5 62ba8fbe…
cmsrepro/phase12/               原始目录（未改动）
```

未运行 dump_curves.py；未生成信号/背景；未访问 pre-fit；未 git 操作。

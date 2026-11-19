# 从多电子薛定谔方程到密度泛函理论：Hohenberg–Kohn 定理与 Kohn–Sham 方程的完整推导

> **目标**：严格回答两个问题：**(1) 为什么基态能量是电子密度的泛函？(2) Kohn–Sham 方程究竟如何推导出来？** 逻辑顺序是：多电子问题 → Rayleigh–Ritz 变分 → 密度与约束搜索 → Hohenberg–Kohn 定理 → 密度变分的 Euler 方程 → 非相互作用参考系 → Kohn–Sham 轨道变分 → 自洽计算。最后说明理论精确性、实际近似和适用边界。
>
> **约定**：以下除特别标注外使用原子单位制，$\hbar=m_e=e=4\pi\varepsilon_0=1$；先讨论固定核（Born–Oppenheimer 近似）、非相对论、无外磁场、固定电子数 $N$ 的零温基态。自旋在需要时显式保留。周期性晶体、非共线磁性、温度、简并和激发态会在后文解释。

---

## 0. 全局逻辑图：两个不同的“变分”

```text
真实相互作用多电子 Hamiltonian H = T + W + V_ext
          │
          ├─ Rayleigh–Ritz: E0 = min_Ψ ⟨Ψ|H|Ψ⟩
          │        （自变量最初是多体波函数 Ψ）
          ▼
电子密度 n(r) = ⟨Ψ|n̂(r)|Ψ⟩
          │
          ├─ Levy 约束搜索：先固定 n，在所有 Ψ→n 中最小化 T+W
          │        F[n] = min_{Ψ→n} ⟨Ψ|T+W|Ψ⟩
          │
          ├─ HK 定理：基态密度决定外势（至多差一个常数）
          ▼
E0 = min_n { F[n] + ∫ v_ext(r)n(r)dr }
          │
          ├─ 密度变分：δF/δn + v_ext = μ
          │        （这是形式上的精确基态方程，但 F[n] 难求）
          ▼
Kohn–Sham 构造：F[n] = T_s[n] + E_H[n] + E_xc[n]
          │
          ├─ 引入辅助非相互作用轨道 φ_i，n = Σ_i f_i|φ_i|²
          ├─ 对轨道作正交归一约束下的变分
          ▼
[−∇²/2 + v_ext + v_H[n] + v_xc[n]] φ_i = ε_i φ_i
          │
          └─ 因 v_eff 依赖 n，形成自洽场（SCF）迭代
```

**关键纠误**：不能仅凭“能量满足变分原理”就推出“$E$ 是 $n$ 的泛函”。前者只保证 $E_0$ 是对波函数变分的极小值；后者依赖 **HK 定理**或更一般的 **Levy–Lieb 约束搜索构造**。而 **KS 方程**不是把多电子薛定谔方程直接做变量替换得到的，它来自一个辅助无相互作用体系的**轨道变分**。

---

## 1. 从 $N$ 电子哈密顿量开始

固定核位置 $\{\mathbf R_A\}$ 后（核间排斥能 $E_{NN}$ 是常数，可在最后加回），电子 Hamiltonian 为

$$
\hat H = \hat T + \hat W + \hat V_{\mathrm{ext}},
$$

$$
\hat T=-\frac12\sum_{i=1}^N\nabla_i^2,\qquad
\hat W=\sum_{i<j}\frac{1}{|\mathbf r_i-\mathbf r_j|},\qquad
\hat V_{\mathrm{ext}}=\sum_{i=1}^N v_{\mathrm{ext}}(\mathbf r_i).
$$

库仑核势是 $v_{\mathrm{ext}}(\mathbf r)=-\sum_A Z_A/|\mathbf r-\mathbf R_A|$。多体波函数 $\Psi(x_1,\ldots,x_N)$ 中 $x_i=(\mathbf r_i,\sigma_i)$ 包含空间与自旋；$\Psi$ 对交换两个电子必须反对称，且归一化。

Rayleigh–Ritz 变分原理：

$$
\boxed{E_0=\min_{\Psi,\,\langle\Psi|\Psi\rangle=1}
\langle\Psi|\hat H|\Psi\rangle.}\tag{1}
$$

这是对 $3N$ 个空间变量（以及自旋）的**多体波函数**做变分。为什么不能直接说“让 $n(\mathbf r)$ 变化就行”？因为不同的 $\Psi$ 可以有相同的密度，但不同的动能、交换和关联能：**密度并不显然唯一确定任意量子态的全部信息**。需要引入更强的结构。

定义密度算符与电子密度：

$$
\hat n(\mathbf r)=\sum_{i=1}^N\delta(\mathbf r-\mathbf r_i),\qquad
n_\Psi(\mathbf r)=\langle\Psi|\hat n(\mathbf r)|\Psi\rangle.
$$

满足 $n\ge0,\ \int n(\mathbf r)\,d^3r=N$。外势能特别简单：

$$
\langle\Psi|\hat V_{\mathrm{ext}}|\Psi\rangle
=\int v_{\mathrm{ext}}(\mathbf r)n_\Psi(\mathbf r)\,d^3r.\tag{2}
$$

这一点是 DFT 结构的起点：**外势与密度线性耦合**，而 $\hat T+\hat W$ 的算符形式不依赖所选择的外势。

---

## 2. 先给出最一般、最清楚的证明：Levy 约束搜索

对于一个可由某个归一化反对称 $N$ 电子波函数产生的密度 $n$，定义

$$
\boxed{F[n]=\inf_{\Psi\mapsto n}\langle\Psi|\hat T+\hat W|\Psi\rangle.}\tag{3}
$$

$\Psi\mapsto n$ 表示限制到所有产生给定 $n$ 的多体态。为保证数学上最小值是否存在不成为障碍，一般写 $\inf$；在适当条件下可以取到极小值。这称 **Levy constrained search**。$F[n]$ 之所以“普适”，是因为它不显含 $v_{\mathrm{ext}}$（但仍依赖电子的动力学与相互作用形式、$N$ 等）。

现在把式 (1) 的极小化分成两层：先固定密度在同密度的波函数中搜索，再改变密度：

$$
\begin{aligned}
E_0
&=\inf_\Psi\left\{\langle\Psi|\hat T+\hat W|\Psi\rangle
+\int v_{\mathrm{ext}}n_\Psi\,d^3r\right\}\\
&=\inf_{n\in\mathcal D_N}\left\{
\inf_{\Psi\mapsto n}\langle\Psi|\hat T+\hat W|\Psi\rangle
+\int v_{\mathrm{ext}}n\,d^3r\right\}\\
&=\boxed{\inf_{n\in\mathcal D_N}\left\{F[n]+\int v_{\mathrm{ext}}(\mathbf r)n(\mathbf r)\,d^3r\right\}.}
\end{aligned}\tag{4}
$$

这里 $\mathcal D_N$ 是允许的 $N$ 电子密度集合。**这才是严格意义上把波函数变分问题变成密度泛函变分问题的步骤。** 对固定的外势，定义总能量泛函

$$
\boxed{E_v[n]\equiv F[n]+\int v_{\mathrm{ext}}(\mathbf r)n(\mathbf r)\,d^3r.}\tag{5}
$$

其最小值才是 $E_0$。切勿混淆：$E_v[n]$ 对试探密度有定义，$E_0$ 是一个**数**；当且仅当 $n$ 是某个基态密度时（在此上下文），$E_v[n]=E_0$。

### 2.1 为什么式 (4) 并不是空洞的重命名？

因为它将“外势改变”与“内部电子物理”分离：对同一电子相互作用，换材料、换晶格核构型等只会改变 $v_{\mathrm{ext}}$，而不必重新定义 $F[n]$。但这只是**存在性**定理：并没有告诉我们如何计算精确的 $F[n]$。

### 2.2 $N$-representability 与 $v$-representability

- **$N$-representable**：存在合法反对称 $N$ 电子态产生这个密度。Levy 约束搜索只要求这一点。
- **$v$-representable**：这个密度恰好是某个局域外势的基态密度。原始 HK 论述通常从这类密度出发，数学上更受限。
- **Noninteracting $v$-representable**：密度还能由某个**无相互作用**局域势的基态产生；标准 KS 构造需注意这一假设或用更广义的系综/数学框架处理。

更严格的数学形式可用 Lieb 的系综泛函（对密度矩阵搜索）并利用凸分析，但上面的纯态约束搜索已足够理解主体物理。

---

## 3. Hohenberg–Kohn 定理：为什么基态密度承载了基态信息？

第一 HK 定理的标准表述：对于固定粒子数、固定相互作用且**非简并**的基态，基态密度 $n_0(\mathbf r)$ 唯一决定外势 $v(\mathbf r)$（最多差一个加性常数），继而确定 Hamiltonian 和其基态。简并情况需要更谨慎的表述，通常用系综 DFT。

### 3.1 反证法推导（非简并基态）

假定存在两个不同且不只相差常数的外势 $v$ 和 $v'$，它们产生**同一个**基态密度 $n_0$，对应 Hamiltonian $H,H'$、归一化非简并基态 $\Psi,\Psi'$ 和基态能量 $E_0,E'_0$。

由严格的 Rayleigh–Ritz 不等式，若两基态不相同：

$$
\begin{aligned}
E_0 &< \langle\Psi'|H|\Psi'\rangle\\
&=\langle\Psi'|H'|\Psi'\rangle+
\int (v-v')n_0\,d^3r\\
&=E'_0+\int(v-v')n_0\,d^3r.\tag{6}
\end{aligned}
$$

同理交换两个体系：

$$
E'_0<E_0+\int(v'-v)n_0\,d^3r.\tag{7}
$$

将 (6) 与 (7) 相加：$E_0+E'_0<E_0+E'_0$，矛盾。因此两个不同外势不能有相同非简并基态密度。若相同波函数同时是两个 Hamiltonian 的本征态，那么相减得到 $\sum_i(v-v')(\mathbf r_i)=\mathrm{const}$（在该态支持集及适当正则性条件下），亦只能允许外势相差常数。

**物理含义**：不是说“任意多体态都能由密度唯一决定”；只是在给定相互作用和 $N$ 的前提下，**基态密度**足以在原理上确定对应外势以及基态可观测量。

### 3.2 第二 HK 定理 / 变分性质

基于上述普适泛函，对合法密度有

$$
E_v[n]\ge E_v[n_0]=E_0.\tag{8}
$$

用约束搜索可对更广的密度集合直接得到这一变分形式，无需先假设每个试探密度都是某个外势的基态。

**逻辑顺序要记住**：

1. Rayleigh–Ritz 仅告诉你“对 $\Psi$ 的能量极小化”。
2. 约束搜索证明“可以严格重组为对 $n$ 的泛函极小化”。
3. HK 唯一性定理解释“为什么基态密度具有如此丰富的信息”。
4. 这些结论都**没有给出精确的 $F[n]$ 的可计算公式**。

---

## 4. 对密度做变分：精确但尚不可用的 Euler 方程

对 $E_v[n]$ 最小化，同时约束 $\int n=N$，引入拉格朗日乘子 $\mu$（其与化学势有关）：

$$
\mathcal L[n]=F[n]+\int v_{\mathrm{ext}}n\,d^3r
-\mu\left(\int n\,d^3r-N\right).
$$

取一阶泛函变分：

$$
\delta\mathcal L=
\int d^3r\left[
\frac{\delta F[n]}{\delta n(\mathbf r)}+v_{\mathrm{ext}}(\mathbf r)-\mu
\right]\delta n(\mathbf r).
$$

在允许的内点、泛函可微以及可作自由一阶变分等条件下，得到

$$
\boxed{\frac{\delta F[n]}{\delta n(\mathbf r)}
+v_{\mathrm{ext}}(\mathbf r)=\mu.}\tag{9}
$$

注意如果在不可微点或密度集合边界，更严格的语言是**次梯度（subgradient）及变分不等式**，不能总是直接写普通导数等于常数。

式 (9) 看起来已经解决了问题，但其主要难题仍是 $F[n]$ 未知，尤其真实相互作用体系的动能不能简单表示成局域的 $n$ 函数。Kohn–Sham 方法正为解决这一困境而设计。

---

## 5. Kohn–Sham 的关键构造：保留准确的轨道动能

引入一个**辅助无相互作用的费米子体系**，要求其基态密度与真实相互作用体系一样。它并不声称真实电子不相互作用：相互作用会通过有效势中的交换关联部分恢复。

对于占据的正交归一辅助单粒子轨道 $\{\phi_i\}$，定义

$$
n(\mathbf r)=\sum_i f_i|\phi_i(\mathbf r)|^2,
\qquad \langle\phi_i|\phi_j\rangle=\delta_{ij}.\tag{10}
$$

$f_i$ 表示占据数：在最简单的零温非简并纯态 KS 中为 0 或 1（若把每个空间轨道的两种自旋合并计数，可为 0、1、2；这里默认含自旋轨道）。系综 KS 可以允许分数占据。

定义**无相互作用的动能泛函**

$$
\boxed{T_s[n]=\inf_{\{\phi_i\}\mapsto n}
\left(-\frac12\sum_i f_i\langle\phi_i|\nabla^2|\phi_i\rangle\right).}\tag{11}
$$

它依旧是密度泛函，但**通过轨道来精确评估辅助体系的动能**，不必猜 $T_s[n]$ 的简单局域表达式。

定义经典 Hartree 能量

$$
\boxed{E_H[n]=\frac12\iint\frac{n(\mathbf r)n(\mathbf r')}
{|\mathbf r-\mathbf r'|}\,d^3r\,d^3r'.}\tag{12}
$$

然后**通过定义**引入交换关联能：

$$
\boxed{E_{xc}[n]\equiv F[n]-T_s[n]-E_H[n].}\tag{13}
$$

即

$$
\boxed{F[n]=T_s[n]+E_H[n]+E_{xc}[n].}\tag{14}
$$

若所有泛函精确并且 KS 参考体系存在，这个分解在相应定义域上是**严格恒等式**，不是近似。$E_{xc}$ 吸收两类东西：

$$
E_{xc}[n]=\underbrace{(T[n]-T_s[n])}_{\text{动能关联贡献}}
+\underbrace{(W[n]-E_H[n])}_{\text{交换与电子关联贡献}},\tag{15}
$$

其中 $T[n],W[n]$ 指在约束搜索极小态上对应的期望值（若极小态有多重选择，分项的表述需留意）；重要的是 $E_{xc}$ **不只是电子的库仑交换能**，它还含有非相互作用体系与真实体系之间的动能差。

因此，完整的 KS 能量表达为

$$
\boxed{
E_v[\{\phi_i\}]
=\sum_i f_i\left\langle\phi_i\left|-\frac12\nabla^2\right|\phi_i\right\rangle
+\int v_{\mathrm{ext}}n\,d^3r
+E_H[n]+E_{xc}[n].}\tag{16}
$$

$\phi_i$ 进入后，$n$ 始终由式 (10) 给出。严格来说，这一步从密度泛函变分切换为**KS 轨道变分**，引入了正交约束。

---

## 6. Kohn–Sham 方程的逐项变分推导（最核心部分）

先为简明假设有 $N$ 个占据自旋轨道且 $f_i=1$。给轨道加拉格朗日乘子矩阵 $\Lambda_{ij}$ 保证正交归一：

$$
\mathcal L[\{\phi_i\}]
=E_v[\{\phi_i\}]
-\sum_{i,j}\Lambda_{ij}
\big(\langle\phi_i|\phi_j\rangle-\delta_{ij}\big).\tag{17}
$$

将 $\phi_i$ 与 $\phi_i^*$ 视为变分上独立的复变量，对 $\phi_i^*(\mathbf r)$ 取泛函导数。

### 6.1 动能项的变分

$$
\frac{\delta T_s}{\delta\phi_i^*(\mathbf r)}
=-\frac12\nabla^2\phi_i(\mathbf r).\tag{18}
$$

### 6.2 外势能项的变分

因 $n=\sum_j\phi_j^*\phi_j$，故 $\delta n(\mathbf r)/\delta\phi_i^*(\mathbf x)=\phi_i(\mathbf r)\delta(\mathbf r-\mathbf x)$，于是

$$
\frac{\delta}{\delta\phi_i^*(\mathbf r)}\int v_{\mathrm{ext}}n\,d^3r'
=v_{\mathrm{ext}}(\mathbf r)\phi_i(\mathbf r).\tag{19}
$$

### 6.3 Hartree 项的变分

从双重积分式 (12)：

$$
\begin{aligned}
\delta E_H&=\frac12\iint\frac{\delta n(\mathbf r)n(\mathbf r')+n(\mathbf r)\delta n(\mathbf r')}
{|\mathbf r-\mathbf r'|}\,d^3r\,d^3r'\\
&=\int d^3r\,\delta n(\mathbf r)
\underbrace{\int\frac{n(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d^3r'}_{v_H(\mathbf r)}.
\end{aligned}
$$

因此

$$
\boxed{v_H(\mathbf r)=\frac{\delta E_H}{\delta n(\mathbf r)}
=\int\frac{n(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d^3r'.}\tag{20}
$$

并有 $\delta E_H/\delta\phi_i^*=v_H\phi_i$。

### 6.4 交换关联项的变分

定义（在导数存在时）

$$
\boxed{v_{xc}(\mathbf r)=\frac{\delta E_{xc}[n]}{\delta n(\mathbf r)}.}\tag{21}
$$

利用链式法则：

$$
\frac{\delta E_{xc}}{\delta\phi_i^*(\mathbf r)}
=\int\frac{\delta E_{xc}}{\delta n(\mathbf r')}
\frac{\delta n(\mathbf r')}{\delta\phi_i^*(\mathbf r)}\,d^3r'
=v_{xc}(\mathbf r)\phi_i(\mathbf r).\tag{22}
$$

### 6.5 正交约束项的变分

$$
\frac{\delta}{\delta\phi_i^*(\mathbf r)}
\sum_{jk}\Lambda_{jk}\langle\phi_j|\phi_k\rangle
=\sum_k\Lambda_{ik}\phi_k(\mathbf r).\tag{23}
$$

把式 (18)—(23) 代入 $\delta\mathcal L/\delta\phi_i^*=0$：

$$
\left[-\frac12\nabla^2+v_{\mathrm{ext}}(\mathbf r)+v_H(\mathbf r)+v_{xc}(\mathbf r)\right]\phi_i(\mathbf r)
=\sum_j\Lambda_{ij}\phi_j(\mathbf r).\tag{24}
$$

由于占据轨道的酉变换不改变总密度、动能和能量，可对厄米乘子矩阵 $\Lambda$ 在占据子空间做酉对角化，选择 **canonical orbitals**，得到

$$
\boxed{
\left[-\frac12\nabla^2+v_{\mathrm{eff}}[n](\mathbf r)\right]\phi_i(\mathbf r)
=\varepsilon_i\phi_i(\mathbf r),
}\tag{25}
$$

$$
\boxed{v_{\mathrm{eff}}[n]=v_{\mathrm{ext}}+v_H[n]+v_{xc}[n],
\quad n(\mathbf r)=\sum_{i\in\mathrm{occ}}|\phi_i(\mathbf r)|^2.}\tag{26}
$$

**这就是 Kohn–Sham 方程的推导。** 所谓“单电子方程”是辅助轨道在共同、密度依赖的有效局域势中运动；多体效应主要进入 $v_{xc}$。它是**非线性自洽特征值问题**，不是 $N$ 个真实电子各自独立的精确薛定谔方程。

> **自旋的细节**：在无磁、闭壳层计算里，可以以空间轨道与双重占据描述；自旋极化 DFT 改为 $E[n_\uparrow,n_\downarrow]$，产生不同的 $v_{xc,\uparrow}$ 和 $v_{xc,\downarrow}$。非共线磁性及 SOC 需要二维自旋量轨道、更一般的自旋密度矩阵及有效磁场。

---

## 7. 与密度 Euler 方程的等价关系

从 (14) 出发，对密度（假设可微）作变分：

$$
\frac{\delta T_s}{\delta n}
+v_{\mathrm{ext}}+v_H+v_{xc}=\mu.\tag{27}
$$

而辅助非相互作用体系本身的密度 Euler 方程是

$$
\frac{\delta T_s}{\delta n}+v_s=\mu_s.\tag{28}
$$

因此只要设

$$
v_s(\mathbf r)=v_{\mathrm{ext}}(\mathbf r)+v_H(\mathbf r)+v_{xc}(\mathbf r)
+\text{constant},\tag{29}
$$

两个 Euler 方程便能匹配，辅助体系与真实体系可共享相同基态密度（在所需存在性条件下）。而 KS 轨道方程 (25) 正是这个 $v_s$ 下无相互作用粒子的本征方程。

**概念上两条推导路线一致**：

- **密度路线**：约束搜索 → $E_v[n]$ → $\delta E_v/\delta n=\mu$ → 用 $T_s$ 与 $E_{xc}$ 分解。
- **轨道路线**：把 $n$ 表成 KS 轨道的密度 → 对轨道和正交约束变分 → KS 本征方程。

轨道路线通常更适合直接理解计算程序如何实施。

---

## 8. 为什么要做自洽迭代（SCF）？

式 (25) 的哈密顿量含 $v_H[n]$ 与 $v_{xc}[n]$，但 $n$ 又由式 (25) 的本征轨道构造，所以不能简单进行一次矩阵对角化。

典型流程：

1. 用叠加原子密度等方式猜测 $n^{(0)}$。
2. 由 $n^{(k)}$ 构造 $v_H[n^{(k)}]$ 和近似 $v_{xc}[n^{(k)}]$。
3. 解 $H_{KS}[n^{(k)}]\phi_i^{(k+1)}=\varepsilon_i^{(k+1)}\phi_i^{(k+1)}$。
4. 构造输出密度 $n_{\mathrm{out}}^{(k+1)}=\sum_i f_i|\phi_i^{(k+1)}|^2$。
5. 对输入与输出密度进行 mixing（可用线性混合、Pulay/DIIS、Broyden 等），更新 $n^{(k+1)}$。
6. 检查密度残差、总能量、力等是否收敛；若未收敛继续。

$$
n^{(k+1)}=(1-\alpha)n^{(k)}+\alpha n_{\mathrm{out}}^{(k+1)}\qquad
\text{（最简单的混合示意）}.\tag{30}
$$

**SCF 收敛不自动保证全局基态**：磁性、多轨道体系可能存在多个局域自洽解，需比较不同磁序、初始构型的总能量与稳定性。

---

## 9. KS 本征值不是直接的多电子激发能；总能量怎么算？

把 KS 方程乘以 $\phi_i^*$ 积分并对占据轨道求和：

$$
\sum_i f_i\varepsilon_i
=T_s+\int(v_{\mathrm{ext}}+v_H+v_{xc})n\,d^3r.\tag{31}
$$

又 $\int v_H n=2E_H$，因此式 (16) 可以重写为

$$
\boxed{
E_{\mathrm{tot}}=\sum_i f_i\varepsilon_i-E_H[n]
+E_{xc}[n]-\int v_{xc}(\mathbf r)n(\mathbf r)\,d^3r+E_{NN}.
}\tag{32}
$$

这说明**不能把所有 KS 本征值直接相加当作真实总能量**：电子相互作用会被重复计数，需要修正。

更加重要的是：普通 KS 轨道能量差 $\varepsilon_a-\varepsilon_i$ 一般**不严格等于**真实中性激发能；真实准粒子带隙也一般不同于 KS 带隙。对于精确泛函，最高占据 KS 本征值在常见条件下满足 $\varepsilon_{\mathrm{HOMO}}=-I$；而真实基本带隙满足

$$
\boxed{E_g^{\mathrm{fund}}=(\varepsilon_{\mathrm{LUMO}}-\varepsilon_{\mathrm{HOMO}})+\Delta_{xc},}\tag{33}
$$

其中 $\Delta_{xc}$ 是交换关联势的导数不连续性。普通半局域近似通常未能正确给出这一贡献，是其低估半导体带隙的重要原因之一。注意真实材料中还需区分**基本带隙**与包含激子束缚能的**光学带隙**。

---

## 10. 精确理论与实际近似到底发生在哪里？

理论上，HK/Levy 结构及 KS 分解并不引入近似（在适用域与假设下）。**实际近似主要出现在交换关联泛函 $E_{xc}[n]$**，此外还有赝势/PAW、基组截断、$k$ 点采样、数值网格、结构和磁序选择等误差。

### 10.1 LDA（局域密度近似）

$$
E_{xc}^{\mathrm{LDA}}[n]=\int n(\mathbf r)\,
\epsilon_{xc}^{\mathrm{HEG}}(n(\mathbf r))\,d^3r.\tag{34}
$$

把每一点当成均匀电子气，其交换关联能密度只依赖当地密度。对缓慢变化密度较自然。

### 10.2 GGA（广义梯度近似）

$$
E_{xc}^{\mathrm{GGA}}[n]=\int f(n(\mathbf r),\nabla n(\mathbf r))\,d^3r.\tag{35}
$$

常见 PBE 即属于 GGA。Meta-GGA 可进一步依赖动能密度等，杂化泛函引入部分确切交换（因而一般已不是单纯显式密度泛函），需要更广义的轨道泛函变分或 generalized KS 框架。

### 10.3 DFT+$U$ 与强关联问题

对局域 $d/f$ 轨道加入 Hubbard 型修正，改善某些电子局域化与磁性的描述。但 $U$ 的选取、投影轨道定义、双计数处理会影响结果；它不是无条件精确的“相关修复器”。DMFT、量子蒙特卡罗或精确对角化等方法可更充分地研究多体效应。

---

## 11. 晶体中怎么接到能带和拓扑计算？

周期外势下，KS 轨道满足 Bloch 定理：

$$
\phi_{n\mathbf k}(\mathbf r)=e^{i\mathbf k\cdot\mathbf r}u_{n\mathbf k}(\mathbf r).
$$

因此

$$
\boxed{H_{KS}(\mathbf k)u_{n\mathbf k}
=\varepsilon_{n\mathbf k}u_{n\mathbf k}.}\tag{36}
$$

DFT 可以提供：能带、态密度、轨道成分、磁矩、总能量、应变响应等。若要判断拓扑，需要继续从周期性波函数或 Wannier 低能模型计算 Berry 联络、曲率与拓扑不变量：

$$
\mathbf A_n(\mathbf k)=i\langle u_{n\mathbf k}|\nabla_\mathbf k u_{n\mathbf k}\rangle,
\qquad \boldsymbol\Omega_n=\nabla_\mathbf k\times\mathbf A_n,
$$

$$
C=\frac{1}{2\pi}\sum_{n\in\mathrm{occ}}\int_{\mathrm{BZ}}\Omega_{n,z}(\mathbf k)\,d^2k.\tag{37}
$$

注意：对普通弱关联绝缘体，KS / Wannier 有效能带拓扑通常很有用；但是对 Mott 绝缘体、分数量子霍尔/分数 Chern 态等本质多体拓扑现象，**单粒子 KS 能带的 Chern 数本身不足以证明多体拓扑序**。需要多体基态简并、谱流、纠缠谱、分数化响应等进一步诊断。

在磁性材料中还要检查：所假设的磁序是否稳定？SOC 是否打开全局能隙？计算出的 Chern 数对应真正的费米能附近绝缘体，还是仅某条局域能带间隙？实验温度下磁有序是否可能存在？

---

## 12. 常见误区集中澄清

**误区 A：「因为 $E_0=\min_\Psi\langle H\rangle$，所以 $E$ 必须是 $n$ 的泛函。」**

不成立。变分原理的自变量原本是 $\Psi$，密度映射是多对一。必须引入 HK 唯一性或 Levy 约束搜索，才能完成逻辑转换。

**误区 B：「基态电子密度唯一决定任何态。」**

不成立。HK 定理讨论适当条件下的**基态**，不允许任意激发态和任意波函数都由同一密度唯一指定。

**误区 C：「KS 轨道就是真实多电子波函数分解出来的单电子波函数。」**

一般不成立。KS 轨道属于辅助体系，其首要任务是给出正确的密度；并非真实相互作用体系中的可直接测得的独立电子状态。

**误区 D：「KS 把相互作用忽略了。」**

不成立。Hartree 项保留经典库仑贡献；$E_{xc}$ 封装剩下的交换关联与动能差。真正难题是能否得到足够准确的 $E_{xc}$。

**误区 E：「DFT 是严格理论，因此 DFT 结果都严格。」**

不成立。理论结构可以严格，具体计算的近似泛函、磁序、赝势、基组和数值收敛都可能产生误差。

**误区 F：「DFT 能带交叉打开后算出 Chern 数，就证明材料有可观测 QAH。」**

不充分。还需考虑真正费米能处是否存在全局能隙、磁性稳定性、缺陷及温度等条件；多体关联很强时须另做诊断。

---

## 13. 三道自检题（附简答）

**题 1：为什么外势是 $\int v_{\mathrm{ext}}n$，但动能不能直接写成类似 $\int t(\mathbf r)n(\mathbf r)$ 的精确局域形式？**

因为外势算符本身是单粒子局域乘法算符，可直接由一体密度决定其期望值；动能含空间导数，对密度和相位/轨道细节高度敏感。其精确密度泛函一般非局域且难构造，故 KS 保留轨道表示的 $T_s$。

**题 2：推导 KS 方程时，为什么会出现一组 $\varepsilon_i$ 而非一个乘子 $\mu$？**

因为直接对每个轨道变分必须维持所有轨道的相互正交约束，最初引入矩阵 $\Lambda_{ij}$；选定对角轨道基底才获得每轨道的特征值 $\varepsilon_i$。密度变分中的 $\mu$ 则对应固定粒子数的一个乘子，两者处于不同层级。

**题 3：如果精确 $E_{xc}$ 完全已知，KS 方程是否意味着真实电子变成无相互作用粒子？**

不意味着。辅助体系的密度与真实基态密度相同，但真实多体态的关联、激发谱和多体响应仍不等同于一个 Slater 行列式；许多可观测量需要额外泛函、时间依赖 DFT 或多体理论。

---

## 14. 一页总结：回答最初的两个“为什么”

**Q1. 为什么 $E$ 是 $n$ 的泛函？**

严格说，是对每个可实现密度定义 $F[n]=\inf_{\Psi\to n}\langle T+W\rangle$，然后因为 $\langle V_{\mathrm{ext}}\rangle=\int vn$，可精确重写

$$
\boxed{E_0=\inf_n\left(F[n]+\int vn\right).}
$$

HK 定理则进一步说明适当条件下基态密度决定外势和基态。**这两个步骤不能只用 Rayleigh–Ritz 一步带过。**

**Q2. Kohn–Sham 方程怎么得到？**

将未知的普适泛函分解为辅助无相互作用轨道动能、经典 Hartree 能和剩余的交换关联能：

$$
\boxed{F[n]=T_s[n]+E_H[n]+E_{xc}[n].}
$$

再用 $n=\sum f_i|\phi_i|^2$，对 $\phi_i^*$ 做正交归一约束下的变分，得到

$$
\boxed{\left[-\frac{\nabla^2}{2}+v_{\mathrm{ext}}+v_H[n]+v_{xc}[n]\right]\phi_i
=\varepsilon_i\phi_i.}
$$

唯一未知的核心物理输入是 $E_{xc}$ 的精确形式；实际 DFT 的主要近似即出现在这里。

---

## 15. 推荐原始文献与学习资料

1. **P. Hohenberg & W. Kohn (1964)**, *Inhomogeneous Electron Gas*, Physical Review **136**, B864. DOI: [10.1103/PhysRev.136.B864](https://doi.org/10.1103/PhysRev.136.B864). HK 定理的原始论文。
2. **W. Kohn & L. J. Sham (1965)**, *Self-Consistent Equations Including Exchange and Correlation Effects*, Physical Review **140**, A1133. DOI: [10.1103/PhysRev.140.A1133](https://doi.org/10.1103/PhysRev.140.A1133). KS 方程原始论文。
3. **M. Levy (1979)**, *Universal variational functionals of electron densities, first-order density matrices, and natural spin-orbitals and solution of the v-representability problem*, PNAS **76**, 6062–6065. DOI: [10.1073/pnas.76.12.6062](https://doi.org/10.1073/pnas.76.12.6062). 约束搜索方法。
4. **E. H. Lieb (1983)**, *Density functionals for Coulomb systems*, International Journal of Quantum Chemistry **24**, 243–277. DOI: [10.1002/qua.560240302](https://doi.org/10.1002/qua.560240302). 严格数学基础和凸泛函形式。
5. **R. M. Martin**, *Electronic Structure: Basic Theory and Practical Methods*（Cambridge University Press）. 从 DFT 到晶体计算的经典教材。
6. **R. G. Parr & W. Yang**, *Density-Functional Theory of Atoms and Molecules*（Oxford University Press）. 密度泛函理论的系统教材。


import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
from matplotlib.colors import LogNorm, TwoSlopeNorm
from matplotlib.ticker import FuncFormatter, NullFormatter


HERE = Path(__file__).resolve().parent.parent
M1, M2 = 35.0, 35.001
MASS_B = 87.1833386421
GT_MAX = math.sqrt(4 * math.pi)
GC_FIXED = 0.30
POINTS = {"A": (87.5299315453, 0.20), "B": (MASS_B, 0.30), "C": (86.0484642982, 1.00)}
CHANNELS = ("jet_tree", "jet_tree_hard", "loop", "loop_hard", "tops")
RATE_NORM = LogNorm(1e-4, 100)
RATIO_NORM = TwoSlopeNorm(vmin=-1.4, vcenter=0, vmax=0.55)


def write_table(path, fields, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        writer.writerows(rows)


def read_integrals(path):
    groups = {}
    with path.open() as stream:
        for row in csv.DictReader(stream):
            mass = float(row["mass_GeV"])
            group = groups.setdefault(mass, {})
            assert row["channel"] not in group
            n, n20, n100, n200 = (int(row[key]) for key in ("events", "pass20", "pass100", "pass200"))
            assert n >= n20 >= n100 >= n200 >= 0
            assert float(row["cross_pb"]) > 0 and float(row["error_pb"]) > 0
            group[row["channel"]] = row
    assert len(groups) == 11 and all(set(group) == set(CHANNELS) for group in groups.values())
    return sorted(groups.items())


def rate(row, after_cut=False):
    sigma, error = (float(row[key]) for key in ("cross_pb", "error_pb"))
    if not after_cut:
        return sigma, error
    n = int(row["events"])
    p = int(row["pass200"]) / n
    assert 0 < p < 1
    return sigma*p, math.hypot(error*p, sigma*math.sqrt(p*(1-p)/n))


def node_table(groups):
    for mass, rows in groups:
        tree20, e_tree20 = rate(rows["jet_tree"])
        tree200, e_tree200 = rate(rows["jet_tree_hard"])
        loop20, e_loop20 = rate(rows["loop"])
        loop200, e_loop200 = rate(rows["loop_hard"])
        tops, e_tops = rate(rows["tops"])
        tops200, e_tops200 = rate(rows["tops"], after_cut=True)
        yield (mass, tree20, e_tree20, loop20, e_loop20, tops, e_tops,
               tree200, e_tree200, loop200, e_loop200, tops200, e_tops200)


def br(mass, gt, gc):
    quarks = (0.0022, 0.0047, 0.096, 1.27, 4.18, 172.0)
    width_quarks = np.zeros_like(mass + gt)
    for mq in quarks:
        z = (mq/mass)**2
        width_quarks += 3*(gt*mq/172)**2 * mass/(12*np.pi) * (1+2*z) * np.sqrt(np.maximum(0, 1-4*z))
    r1, r2 = (M1/mass)**2, (M2/mass)**2
    phase = np.sqrt(np.maximum(0, (1-((M1+M2)/mass)**2)*(1-((M1-M2)/mass)**2)))
    spin = 1-(r1+r2)/2-(r1-r2)**2/2+3*np.sqrt(r1*r2)
    width_dark = (gc/2)**2 * mass/(12*np.pi) * phase * spin
    return width_dark/(width_quarks+width_dark), (width_quarks+width_dark)/mass


def lz_product(mass):
    return 0.0380063 * (mass/30)**2


def interpolated(mass, nodes):
    curves = {}
    for i, name in enumerate(("tree20", "loop20", "tt20", "tree200", "loop200", "tt200")):
        values = nodes[:, 1 + 2*i]
        curves[name] = np.exp(np.interp(mass, nodes[:, 0], np.log(values)))
    return curves


def scan(masses, couplings, curves, lz):
    x, y = np.meshgrid(masses, couplings)
    gt = lz_product(x)/y if lz else y
    gc = y if lz else np.full_like(y, GC_FIXED)
    branch, relative_width = br(x, gt, gc)
    valid = (gt <= GT_MAX*(1 + 1e-12)) & (relative_width < 0.03)
    production = {key: np.where(valid, val[None, :]*gt**2*branch, np.nan)
                  for key, val in curves.items()}
    for region in ("20", "200"):
        production["jet"+region] = production["tree"+region] + production["loop"+region]
        production["ratio"+region] = production["jet"+region] / production["tt"+region]
    return x, y, gt, gc, branch, relative_width, production


def axes_format(ax, lz=False):
    ax.set_yscale("log")
    ax.set_xlabel(r"$M_V$ [GeV]")
    ax.set_ylabel(r"$g_\chi$" if lz else r"$g_t$")
    ax.set_xticks([75, 100, 125, 150, 175, 200])
    ax.set_yticks([0.1, 0.2, 0.3, 0.5, 1, 1.5] if lz else [0.08, 0.15, 0.3, 0.6, 1, 2, 3.5])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(direction="out", length=3.5)
    ax.set_facecolor("#ededed")


def mark(ax, mass, coupling, label, text_offset=(7, 4)):
    ax.scatter([mass], [coupling], s=35, linewidth=1, color="white", edgecolor="#151515", zorder=6)
    ax.annotate(label, (mass, coupling), xytext=text_offset, textcoords="offset points",
                fontsize=9, color="white", weight="bold",
                bbox={"boxstyle": "round,pad=.15", "facecolor": "#1d2130", "alpha": .78, "linewidth": 0})


def save_figure(fig, base):
    for extension in ("png", "pdf"):
        fig.savefig(HERE / "figures" / f"{base}.{extension}", dpi=230)
    plt.close(fig)


def fixed_plot(data, region):
    x, y, _, _, _, _, production = data
    fig, axes = plt.subplots(1, 3, figsize=(14.4, 5.1), layout="constrained")
    for ax, channel, title in zip(axes, ("jet", "tt", "ratio"),
                                  (r"$j+\mathrm{MET}$", r"$t\bar{t}+\mathrm{MET}$",
                                   r"$\sigma(j+\mathrm{MET})/\sigma(t\bar{t}+\mathrm{MET})$"), strict=True):
        values = production[channel+region]
        if channel == "ratio":
            ratio_plot = ax.pcolormesh(x, y, np.log10(values), cmap="RdBu_r", norm=RATIO_NORM,
                                       shading="auto", rasterized=True)
            ratio_ticks = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 3])
            bar = fig.colorbar(ratio_plot, ax=ax, ticks=np.log10(ratio_ticks), fraction=.052, pad=.03)
            bar.ax.set_yticklabels([f"{t:g}" for t in ratio_ticks])
            bar.set_label("Cross-section ratio")
            if np.nanmin(values) < 1 < np.nanmax(values):
                ax.contour(x, y, values, levels=[1], colors="#222222", linewidths=1.3)
            ax.text(.96, .05, f"Range: {np.nanmin(values):.3g} to {np.nanmax(values):.3g}",
                    transform=ax.transAxes, ha="right", fontsize=9, color="#141621",
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": .86, "pad": 4})
        else:
            rate_plot = ax.pcolormesh(x, y, values, cmap="viridis", norm=RATE_NORM,
                                      shading="auto", rasterized=True)
            levels = [v for v in (.001, .01, .1, 1, 10, 100) if np.nanmin(values) < v < np.nanmax(values)]
            if levels:
                contours = ax.contour(x, y, values, levels=levels, colors="#ffffff",
                                      alpha=.55, linewidths=.65)
                ax.clabel(contours, fmt=lambda value: f"{value:g}", fontsize=7)
        axes_format(ax)
        ax.set_title(title, fontsize=12)
        ax.plot(x[0], lz_product(x[0])/GC_FIXED, "--", color="white", linewidth=1.3, label="LZ rate match",
                path_effects=[path_effects.Stroke(linewidth=2.15, foreground="#323643", alpha=.55),
                              path_effects.Normal()])
        mark(ax, MASS_B, lz_product(MASS_B)/GC_FIXED, "B")
        ax.set(xlim=(x.min(), x.max()), ylim=(y.min(), y.max()))
    axes[0].legend(loc="upper left", labelcolor="white", facecolor="#282b38", edgecolor="none", fontsize=8.5)
    fig.colorbar(rate_plot, ax=list(axes[:2]), label="Cross section [pb]", fraction=.033, pad=.028)
    selection = (r"Loose jet selection: $p_T^j>20$ GeV, $|\eta_j|<6$; inclusive $t\bar{t}$ recoil"
                 if region == "20" else
                 r"Common $p_T^{\rm miss}>200$ GeV; jet $|\eta_j|<4.5$")
    fig.suptitle(rf"13 TeV pseudo-Dirac vector mediator  |  $g_\chi={GC_FIXED}$" + "\n" + selection, fontsize=14)
    save_figure(fig, "truth_loose" if region == "20" else "truth_met200")


def lz_plot(data):
    x, y, _, _, _, _, production = data
    fig, axes = plt.subplots(2, 2, figsize=(10.3, 8), layout="constrained")
    titles = {
        ("jet", "20"): r"$j+\mathrm{MET}$  |  $p_T^j>20$ GeV",
        ("tt", "20"): r"$t\bar{t}+\mathrm{MET}$  |  inclusive",
        ("jet", "200"): r"$j+\mathrm{MET}$  |  $p_T^{\rm miss}>200$ GeV",
        ("tt", "200"): r"$t\bar{t}+\mathrm{MET}$  |  $p_T^{\rm miss}>200$ GeV",
    }
    for ax, key in zip(axes.flat, titles, strict=True):
        image = ax.pcolormesh(x, y, production["".join(key)], cmap="viridis", norm=RATE_NORM,
                              shading="auto", rasterized=True)
        ax.plot(x[0], lz_product(x[0])/GT_MAX, "-", color="#515969", linewidth=1.15)
        for name, (mass, coupling) in POINTS.items():
            mark(ax, mass, coupling, name, (7, -4))
        axes_format(ax, lz=True)
        ax.set_title(titles[key], fontsize=11)
        ax.set(xlim=(x.min(), x.max()), ylim=(y.min(), y.max()))
    fig.colorbar(image, ax=list(axes.flat), label="Cross section [pb]", fraction=.036, pad=.03)
    fig.suptitle("13 TeV  |  LZ benchmark rate matched  |  A, B, C also match thermal relic density\n"
                 r"Gray region: $g_t>\sqrt{4\pi}$", fontsize=13)
    save_figure(fig, "truth_lz_slice")


def write_grid(name, data):
    x, y, gt, gc, branch, width, production = data
    fields = ["mass_GeV", "gt", "gchi", "BR_invisible", "width_over_mass", *production]
    columns = [x, gt, gc, branch, width, *production.values()]
    rows = zip(*(column.ravel() for column in columns), strict=True)
    write_table(HERE / "results" / name, fields,
                ([f"{value:.9g}" if np.isfinite(value) else "" for value in row] for row in rows))


def write_benchmarks(nodes):
    rows = []
    for name, (mass, gc) in POINTS.items():
        gt = lz_product(mass)/gc
        branch, _ = br(np.array(mass), np.array(gt), np.array(gc))
        norm = gt**2 * branch
        production = interpolated(np.array([mass]), nodes)
        for cut, definition in (("20", "loose"), ("200", "met200")):
            tree, loop, tops = [float(production[channel+cut][0]) * norm
                                for channel in ("tree", "loop", "tt")]
            rows.append((name, mass, gt, gc, branch, definition, tree, loop, tree+loop, tops, (tree+loop)/tops))
    write_table(HERE / "results" / "benchmark_cross_sections.csv",
                ("point", "mass_GeV", "gt", "gchi", "BR_invisible", "selection", "jet_tree_pb",
                 "jet_loop_pb", "jet_total_pb", "tt_pb", "jet_to_tt"), rows)


def main():
    (HERE / "figures").mkdir(exist_ok=True)
    groups = read_integrals(HERE / "results" / "madgraph_integrals.csv")
    nodes = np.array(list(node_table(groups)))
    fields = ["mass_GeV"]
    for name in ("tree20", "loop20", "tt_inclusive", "tree200", "loop200", "tt200"):
        fields.extend([f"{name}_pb", f"{name}_stat_error_pb"])
    write_table(HERE / "results" / "production_nodes_gt1.csv", fields, nodes)
    masses = np.unique(np.r_[np.linspace(72, 200, 257), nodes[:, 0]])
    curves = interpolated(masses, nodes)
    fixed = scan(masses, np.geomspace(.08, 3.5, 141), curves, lz=False)
    lz = scan(masses, np.geomspace(.10, 1.50, 141), curves, lz=True)
    for region in ("20", "200"):
        fixed_plot(fixed, region)
    lz_plot(lz)
    write_grid("grid_fixed_gchi_0p30.csv", fixed)
    write_grid("grid_lz_normalized.csv", lz)
    write_benchmarks(nodes)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Make fixed-point comparison figures using Pillow."""

from pathlib import Path
import math

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "remote_results"
PLOTS = ROOT / "plots"
PLOTS.mkdir(exist_ok=True)

LABELS = {
    "universal_gB0p1": "universal: gVq = 0.1/6",
    "firstgen_only_gB0p1": "1st gen.: gVu = gVd = 0.1/6",
    "thirdgen_gq0p1": "3rd gen.: gVb = gVt = 0.1",
    "mfv_top0p1": "Yukawa-like: gVt = 0.1",
}
CHANNELS = ["inclusive", "monojet", "monophoton", "monozll",
            "bbmet", "ttmet", "dijet"]
CHANNEL_LABELS = ["chi1 chi2", "j + MET", "gamma + MET", "Z(ll) + MET",
                  "bb + MET", "tt + MET", "V -> jj"]
COLORS = ["#0072B2", "#56B4E9", "#D55E00", "#009E73"]
FONT_PATH = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD_PATH = Path(r"C:\Windows\Fonts\arialbd.ttf")


def font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_PATH
    return ImageFont.truetype(str(path), size)


def text_center(draw, xy, value, fnt, fill="black"):
    box = draw.textbbox((0, 0), value, font=fnt)
    draw.text((xy[0] - (box[2]-box[0])/2, xy[1] - (box[3]-box[1])/2),
              value, font=fnt, fill=fill)


def log_y(value, ymin, ymax, top, bottom):
    fraction = (math.log10(value) - math.log10(ymin)) / (
        math.log10(ymax) - math.log10(ymin))
    return bottom - fraction * (bottom - top)


data = pd.read_csv(DATA / "pilot_channel_cross_sections.csv")
data["cross_section_fb"] = 1000.0 * data["cross_section_pb"]

# Figure 1: absolute generated rates.
img = Image.new("RGB", (1900, 1120), "white")
d = ImageDraw.Draw(img)
left, right, top, bottom = 150, 1840, 190, 840
ymin, ymax = 1e-5, 3e3
for exponent in range(-5, 4):
    value = 10.0 ** exponent
    y = log_y(value, ymin, ymax, top, bottom)
    d.line((left, y, right, y), fill="#d7d7d7", width=2)
    d.text((25, y-17), f"10^{exponent}", font=font(30), fill="black")
d.line((left, top, left, bottom), fill="black", width=3)
d.line((left, bottom, right, bottom), fill="black", width=3)

group_w = (right-left) / len(CHANNELS)
bar_w = group_w * 0.18
for j, (benchmark, label) in enumerate(LABELS.items()):
    sub = data[data.benchmark == benchmark].set_index("channel")
    for i, channel in enumerate(CHANNELS):
        value = float(sub.loc[channel, "cross_section_fb"])
        x0 = left + (i+0.5)*group_w + (j-2)*bar_w
        y = log_y(max(value, ymin), ymin, ymax, top, bottom)
        d.rectangle((x0, y, x0+bar_w*0.9, bottom), fill=COLORS[j],
                    outline="black", width=1)
for i, label in enumerate(CHANNEL_LABELS):
    text_center(d, (left+(i+0.5)*group_w, bottom+42), label, font(27))

d.text((30, 35), "Pseudo-Dirac flavor EFT: fixed-point channel comparison",
       font=font(43, True), fill="black")
d.text((30, 95), "sqrt(s)=13.6 TeV; MV=500 GeV; mchi1=35 GeV; delta m=1 MeV; gchi=0.32",
       font=font(30), fill="black")
d.text((25, 145), "LO parton-level cross section [fb] (log scale)",
       font=font(27, True), fill="black")
legend_y = 925
for j, label in enumerate(LABELS.values()):
    x = 520 + (j % 2)*650
    y = legend_y + (j // 2)*55
    d.rectangle((x, y, x+42, y+28), fill=COLORS[j], outline="black")
    d.text((x+55, y-4), label, font=font(27), fill="black")
img.save(PLOTS / "fixed_point_cross_sections.png")
img.save(PLOTS / "fixed_point_cross_sections.pdf", "PDF", resolution=150.0)

# Figure 2: actual monojet limit proxy plus pre-detector yields.
best = pd.read_csv(DATA / "monojet_best_bin_proxy.csv").set_index("benchmark")
acceptance = pd.read_csv(DATA / "truth_acceptance_and_sensitivity.csv")
zrows = acceptance[acceptance.channel == "monozll"].set_index("benchmark")
benchmarks = list(LABELS)
short = ["universal", "1st gen.", "3rd gen.", "Yukawa-like"]

img = Image.new("RGB", (1900, 1480), "white")
d = ImageDraw.Draw(img)
d.text((30, 25), "First-pass sensitivity screening (not a detector-level recast)",
       font=font(43, True), fill="black")

left, right, top, bottom = 160, 1840, 145, 620
ymin, ymax = 1e-5, 2.0
for exponent in range(-5, 1):
    value = 10.0 ** exponent
    y = log_y(value, ymin, ymax, top, bottom)
    d.line((left, y, right, y), fill="#d7d7d7", width=2)
    d.text((25, y-16), f"10^{exponent}", font=font(28), fill="black")
y_one = log_y(1.0, ymin, ymax, top, bottom)
d.line((left, y_one, right, y_one), fill="black", width=4)
d.text((right-520, y_one-38), "ATLAS observed visible-rate limit",
       font=font(25), fill="black")
slot = (right-left)/4
for i, benchmark in enumerate(benchmarks):
    value = float(best.loc[benchmark, "signal_to_limit"])
    x0 = left+(i+0.27)*slot
    x1 = left+(i+0.73)*slot
    y = log_y(value, ymin, ymax, top, bottom)
    d.rectangle((x0, y, x1, bottom), fill=COLORS[i], outline="black", width=2)
    text_center(d, ((x0+x1)/2, bottom+35), short[i], font(27))
d.text((18, 92), "Best monojet truth rate / published visible-rate limit",
       font=font(30, True), fill="black")

left, right, top, bottom = 160, 1840, 820, 1310
ymin, ymax = 1e-3, 1e5
for exponent in range(-3, 6):
    value = 10.0 ** exponent
    y = log_y(value, ymin, ymax, top, bottom)
    d.line((left, y, right, y), fill="#d7d7d7", width=2)
    d.text((25, y-16), f"10^{exponent}", font=font(28), fill="black")
screen_channels = ["monophoton", "monozll", "bbmet", "ttmet"]
screen_labels = ["gamma+MET raw", "Z(ll)+MET CMS-like", "bb+MET raw", "tt+MET raw"]
screen_colors = ["#CC79A7", "#E69F00", "#0072B2", "#009E73"]
slot = (right-left)/4
bar_w = slot*0.19
for i, benchmark in enumerate(benchmarks):
    for j, channel in enumerate(screen_channels):
        if channel == "monozll":
            value = float(zrows.loc[benchmark, "events_at_137fb"])
        else:
            sigma = data[(data.benchmark == benchmark) &
                         (data.channel == channel)].cross_section_fb.iloc[0]
            value = float(sigma)*137.0
        x0 = left+(i+0.1)*slot+j*bar_w
        y = log_y(max(value, ymin), ymin, ymax, top, bottom)
        d.rectangle((x0, y, x0+bar_w*0.9, bottom), fill=screen_colors[j],
                    outline="black", width=1)
    text_center(d, (left+(i+0.5)*slot, bottom+35), short[i], font(27))
d.text((18, 760), "Events in 137 fb^-1 before detector effects",
       font=font(30, True), fill="black")
for j, label in enumerate(screen_labels):
    x = 310+(j%2)*720
    y = 1370+(j//2)*45
    d.rectangle((x, y, x+42, y+26), fill=screen_colors[j], outline="black")
    d.text((x+55, y-5), label, font=font(26), fill="black")
img.save(PLOTS / "first_pass_sensitivity.png")
img.save(PLOTS / "first_pass_sensitivity.pdf", "PDF", resolution=150.0)

widths = (data.groupby("benchmark", sort=False)[
    ["width_quarks_GeV", "width_chi_GeV", "width_total_GeV"]].first())
widths["width_over_mass"] = widths.width_total_GeV / 500.0
widths.to_csv(DATA / "benchmark_widths.csv")

print(PLOTS / "fixed_point_cross_sections.png")
print(PLOTS / "first_pass_sensitivity.png")

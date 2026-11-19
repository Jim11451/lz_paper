#!/usr/bin/env python3
"""Pilot cross-section comparison for the flavor-nonuniversal pseudo-Dirac UFO.

The six gVq entries are the actual coefficients of V_mu qbar gamma^mu q.
All results are LO parton level at 13.6 TeV.  The script preserves a pristine
parameter-card template in memory for every generated process and recomputes
the V width analytically at every point.
"""

from __future__ import annotations

import csv
import math
import re
import subprocess
from pathlib import Path


ROOT = Path("/home/cms/phenomenology/PseudoDiracFlavorEFT_20261020")
OUT = ROOT / "results"
LOG = ROOT / "logs"
OUT.mkdir(exist_ok=True)
LOG.mkdir(exist_ok=True)

MV = 500.0
MCHI = 35.0
DM = 0.001
GCHI = 0.32

G0 = 0.1 / 6.0
BENCHMARKS = {
    # Exact continuation of the former gB=0.1 convention.
    "universal_gB0p1": dict(gVu=G0, gVd=G0, gVs=G0, gVc=G0, gVb=G0, gVt=G0),
    "firstgen_only_gB0p1": dict(gVu=G0, gVd=G0, gVs=0.0, gVc=0.0, gVb=0.0, gVt=0.0),
    # A deliberately third-generation-philic simplified benchmark.
    "thirdgen_gq0p1": dict(gVu=0.0, gVd=0.0, gVs=0.0, gVc=0.0, gVb=0.1, gVt=0.1),
    # Phenomenological MFV/Yukawa-like hierarchy, normalized to gVt=0.1.
    "mfv_top0p1": dict(
        gVu=0.1 * 0.0022 / 172.0,
        gVd=0.1 * 0.0047 / 172.0,
        gVs=0.1 * 0.096 / 172.0,
        gVc=0.1 * 1.27 / 172.0,
        gVb=0.1 * 4.18 / 172.0,
        gVt=0.1,
    ),
}

CHANNELS = {
    "inclusive": dict(proc="proc_inclusive_full", nevents=1000, cuts={}),
    "monojet": dict(proc="proc_monojet", nevents=1000,
                    cuts={"ptj": 200.0, "etaj": 4.5}),
    "monophoton": dict(proc="proc_monophoton", nevents=1000,
                       cuts={"pta": 150.0, "etaa": 2.5}),
    "monozll": dict(proc="proc_monozll", nevents=1000, cuts={}),
    "bbmet": dict(proc="proc_bbmet", nevents=600,
                  cuts={"ptb": 25.0, "etab": 2.5, "drbb": 0.4}),
    "ttmet": dict(proc="proc_ttmet", nevents=400, cuts={}),
    "dijet": dict(proc="proc_dijet", nevents=1000, cuts={}),
}


def set_block(text: str, block: str, code: int, value: float) -> str:
    lines = text.splitlines()
    active = False
    found = False
    head = re.compile(r"^\s*block\s+(\S+)", re.I)
    item = re.compile(r"^(\s*)(\d+)(\s+)(\S+)(.*)$")
    for i, line in enumerate(lines):
        match = head.match(line)
        if match:
            active = match.group(1).lower() == block.lower()
            continue
        if active and (line.lstrip().lower().startswith("decay") or
                       line.lstrip().lower().startswith("block")):
            active = False
        if active:
            match = item.match(line)
            if match and int(match.group(2)) == code:
                lines[i] = f"{match.group(1)}{code}{match.group(3)}{value:.12e}{match.group(5)}"
                found = True
                break
    if not found:
        raise RuntimeError(f"missing {block}[{code}]")
    return "\n".join(lines) + "\n"


def set_decay(text: str, pdg: int, value: str) -> str:
    pattern = re.compile(rf"^(\s*DECAY\s+{pdg}\s+)(\S+)(.*)$", re.I | re.M)
    updated, count = pattern.subn(rf"\g<1>{value}\g<3>", text, count=1)
    if count != 1:
        raise RuntimeError(f"missing DECAY {pdg}")
    return updated


def set_run_value(text: str, key: str, value) -> str:
    pattern = re.compile(rf"^(\s*)[^!\n]+(\s*=\s*{re.escape(key)}\b.*)$", re.I | re.M)
    updated, count = pattern.subn(lambda m: f"{m.group(1)}{value}{m.group(2)}", text, count=1)
    if count != 1:
        raise RuntimeError(f"missing run-card key {key}")
    return updated


def cross_section_from_banner(path: Path) -> tuple[float, float]:
    text = path.read_text(errors="replace")
    # MG5 can retain a stale first block when a run name is regenerated.  The
    # final MGGenerationInfo block belongs to the just-completed run.
    matches = re.findall(r"Integrated weight \(pb\)\s*:\s*([0-9.eE+\-]+)", text)
    if not matches:
        raise RuntimeError(f"cross section absent in {path}")
    cross = float(matches[-1])
    err_matches = re.findall(
        r"Integrated weight uncertainty \(pb\)\s*:\s*([0-9.eE+\-]+)", text
    )
    return cross, float(err_matches[-1]) if err_matches else float("nan")


def mediator_width(couplings: dict[str, float]) -> tuple[float, float, float]:
    """Return (quark, chi1-chi2, total) widths in GeV.

    The UFO coefficients gVq are the full vector couplings.  The dark UFO
    vertex has gDM=gChi/2.  This analytic width is used because the inherited
    FeynRules-1.7 decay table does not expose Vb to MadWidth.
    """
    quark_masses = dict(gVu=0.0022, gVd=0.0047, gVs=0.096,
                        gVc=1.27, gVb=4.18, gVt=172.0)
    width_q = 0.0
    for name, mass in quark_masses.items():
        if MV <= 2.0 * mass:
            continue
        r = (mass / MV) ** 2
        width_q += (3.0 * couplings[name] ** 2 * MV / (12.0 * math.pi)
                    * (1.0 + 2.0 * r) * math.sqrt(1.0 - 4.0 * r))

    m1, m2 = MCHI, MCHI + DM
    width_chi = 0.0
    if MV > m1 + m2:
        r1, r2 = (m1 / MV) ** 2, (m2 / MV) ** 2
        lam = max(0.0, 1.0 + r1*r1 + r2*r2 - 2.0*r1 - 2.0*r2 - 2.0*r1*r2)
        form = 1.0 - (r1+r2)/2.0 - (r1-r2)**2/2.0 + 3.0*math.sqrt(r1*r2)
        gdm = GCHI / 2.0
        width_chi = gdm * gdm * MV / (12.0 * math.pi) * math.sqrt(lam) * form
    return width_q, width_chi, width_q + width_chi


def run_point(channel: str, benchmark: str, idx: int) -> dict:
    cfg = CHANNELS[channel]
    proc = ROOT / cfg["proc"]
    param_path = proc / "Cards" / "param_card.dat"
    run_path = proc / "Cards" / "run_card.dat"
    param = param_path.read_text()
    run = run_path.read_text()

    for code, name in enumerate(("gVu", "gVd", "gVs", "gVc", "gVb", "gVt"), 1):
        param = set_block(param, "flavcoup", code, BENCHMARKS[benchmark][name])
    param = set_block(param, "pdbinputs", 2, GCHI)
    param = set_block(param, "pdbinputs", 3, DM)
    param = set_block(param, "mass", 4, 0.0)
    param = set_block(param, "mass", 5, 0.0)
    param = set_block(param, "mass", 100051, MCHI)
    param = set_block(param, "mass", 9900032, MV)
    param = set_decay(param, 100052, "0.0")
    width_q, width_chi, width_total = mediator_width(BENCHMARKS[benchmark])
    param = set_decay(param, 9900032, f"{width_total:.12e}")

    run = set_run_value(run, "nevents", cfg["nevents"])
    run = set_run_value(run, "iseed", 52000 + idx)
    run = set_run_value(run, "ebeam1", 6800.0)
    run = set_run_value(run, "ebeam2", 6800.0)
    run = set_run_value(run, "use_syst", "False")
    for key, value in cfg["cuts"].items():
        run = set_run_value(run, key, value)

    param_path.write_text(param)
    run_path.write_text(run)
    run_name = f"{benchmark}__{channel}"
    log_path = LOG / f"{run_name}.log"
    command = [str(proc / "bin" / "generate_events"), run_name, "-f"]
    with log_path.open("w") as handle:
        completed = subprocess.run(command, cwd=proc, stdout=handle,
                                   stderr=subprocess.STDOUT, timeout=3600)
    if completed.returncode:
        raise RuntimeError(f"{run_name} failed; see {log_path}")
    banners = sorted((proc / "Events" / run_name).glob("*_banner.txt"))
    if not banners:
        raise RuntimeError(f"no banner for {run_name}")
    cross, error = cross_section_from_banner(banners[-1])
    return dict(
        benchmark=benchmark, channel=channel, sqrt_s_TeV=13.6,
        MV_GeV=MV, Mchi1_GeV=MCHI, deltaM_GeV=DM, gChi=GCHI,
        **BENCHMARKS[benchmark], cross_section_pb=cross,
        integration_error_pb=error, nevents=cfg["nevents"],
        width_quarks_GeV=width_q, width_chi_GeV=width_chi,
        width_total_GeV=width_total,
        run_name=run_name,
    )


def main() -> None:
    # Pre-build serially to avoid a race in MG5's bundled gammaUPC Fortran
    # modules when multiple subprocesses compile at once.
    for cfg in CHANNELS.values():
        gamma_upc = ROOT / cfg["proc"] / "Source" / "PDF" / "gammaUPC"
        if gamma_upc.exists():
            subprocess.run(["make", "-j1"], cwd=gamma_upc, check=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT)

    output = OUT / "pilot_channel_cross_sections.csv"
    fields = None
    rows = []
    idx = 0
    for benchmark in BENCHMARKS:
        for channel in CHANNELS:
            idx += 1
            print(f"[{idx}/{len(BENCHMARKS)*len(CHANNELS)}] {benchmark} {channel}", flush=True)
            row = run_point(channel, benchmark, idx)
            rows.append(row)
            fields = list(row)
            with output.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            print(f"  sigma = {row['cross_section_pb']:.6e} pb", flush=True)


if __name__ == "__main__":
    main()

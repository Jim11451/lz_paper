#!/usr/bin/env python3
"""Validate the flavor-EFT UFO against the audited original benchmark."""

from pathlib import Path
import re
import subprocess


ROOT = Path("/home/cms/phenomenology/PseudoDiracFlavorEFT_20261020")
PROC = ROOT / "proc_inclusive_full"
RUN_NAME = "original_pseudodirac_benchmark"


def set_block(text, block, code, value):
    lines = text.splitlines()
    active = False
    for i, line in enumerate(lines):
        head = re.match(r"^\s*block\s+(\S+)", line, re.I)
        if head:
            active = head.group(1).lower() == block.lower()
            continue
        if active and line.lstrip().lower().startswith(("block", "decay")):
            active = False
        item = re.match(r"^(\s*)(\d+)(\s+)(\S+)(.*)$", line)
        if active and item and int(item.group(2)) == code:
            lines[i] = (f"{item.group(1)}{code}{item.group(3)}"
                        f"{value:.12e}{item.group(5)}")
            return "\n".join(lines) + "\n"
    raise RuntimeError(f"missing {block}[{code}]")


def set_decay(text, pdg, value):
    pattern = re.compile(rf"^(\s*DECAY\s+{pdg}\s+)(\S+)(.*)$", re.I | re.M)
    updated, count = pattern.subn(rf"\g<1>{value:.12e}\g<3>", text, count=1)
    if count != 1:
        raise RuntimeError(f"missing DECAY {pdg}")
    return updated


def set_run(text, key, value):
    pattern = re.compile(rf"^(\s*)[^!\n]+(\s*=\s*{key}\b.*)$", re.I | re.M)
    updated, count = pattern.subn(lambda m: f"{m.group(1)}{value}{m.group(2)}",
                                  text, count=1)
    if count != 1:
        raise RuntimeError(f"missing run-card key {key}")
    return updated


param_path = PROC / "Cards" / "param_card.dat"
run_path = PROC / "Cards" / "run_card.dat"
param = param_path.read_text()
gq = 1.46e-5 / 6.0
for code in range(1, 7):
    param = set_block(param, "flavcoup", code, gq)
param = set_block(param, "pdbinputs", 2, 0.32)
param = set_block(param, "pdbinputs", 3, 0.001)
param = set_block(param, "mass", 100051, 35.0)
param = set_block(param, "mass", 9900032, 30.0)
# Dark decay is kinematically closed.  Five effectively massless flavors give
# 5 * 3*gq^2*MV/(12*pi); retain the audited 7e-11 GeV UFO default.
param = set_decay(param, 9900032, 7.0e-11)
param_path.write_text(param)

run = run_path.read_text()
for key, value in (("nevents", 2000), ("iseed", 52999),
                   ("ebeam1", 6800.0), ("ebeam2", 6800.0),
                   ("use_syst", "False")):
    run = set_run(run, key, value)
run_path.write_text(run)

log = ROOT / "logs" / f"{RUN_NAME}.log"
with log.open("w") as handle:
    result = subprocess.run([str(PROC / "bin" / "generate_events"), RUN_NAME, "-f"],
                            cwd=PROC, stdout=handle, stderr=subprocess.STDOUT,
                            timeout=3600)
if result.returncode:
    raise SystemExit(f"run failed; see {log}")

banner = sorted((PROC / "Events" / RUN_NAME).glob("*_banner.txt"))[-1]
weights = re.findall(r"Integrated weight \(pb\)\s*:\s*([0-9.eE+\-]+)",
                     banner.read_text(errors="replace"))
if not weights:
    raise SystemExit("cross section missing")
sigma = float(weights[-1])
legacy_reference = 5.737e-10
# The 2026-10-05 stored process directory was generated before the UFO color
# tensor was repaired: its matrix code says ColorOne() and CF=1.  Regenerating
# from the repaired Identity(1,2) vertex gives the physical color sum CF=3.
corrected_reference = 3.0 * legacy_reference
relative = (sigma - corrected_reference) / corrected_reference
out = ROOT / "results" / "original_benchmark_validation.txt"
out.write_text(
    f"new_ufo_sigma_pb={sigma:.12e}\n"
    f"legacy_stale_process_sigma_pb={legacy_reference:.12e}\n"
    f"physical_color_corrected_reference_pb={corrected_reference:.12e}\n"
    f"relative_difference_from_color_corrected={relative:.6e}\n"
    f"new_over_legacy={sigma/legacy_reference:.6e}\n"
)
print(out.read_text(), end="")

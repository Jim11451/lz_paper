"""kappa(m_chi) from the LZ requirement N_ROI = 1.12044  (v2, corrected).

Differences from kappa_from_lz.py (v1, kept for the record):
  * runs PDmq/lz_recoil2 instead of lz_recoil;
  * lz_recoil2 uses sigma_eff(A) = sigma_N * [2 f_A / (A gB)]^2 with
    f_A = Z f_p + (A-Z) f_n, so the 1/16pi prefactor and the proton/neutron
    split are both handled inside the program;
  * the normalisation target is 1.12044 events (the main paper's value), not 1.

    g_chi^lim = sqrt(N_target / N_ref),   kappa = g_chi^lim / M_V_ref^2

Inputs : gB = f_p = 5.291e-05 (g_t = 1), M_V_ref = 100 GeV, gChi = 1.
Output : data/relic/kappa_lz_gN_v2.csv  (mchi, N_ref, gchi_lim, kappa)
         data/relic/kappa_lz_gN_v2.log  (full provenance)
"""
import csv
import hashlib
import os
import re
import subprocess
import sys
import time

PD = "/home/yy/lz-event/phenomenology/tools/micromegas_7.1.10/PDmq"
BIN = os.path.join(PD, "lz_recoil2")
OUT = "/home/yy/lz-event/phenomenology/data/relic/kappa_lz_gN_v2.csv"
LOG = "/home/yy/lz-event/phenomenology/data/relic/kappa_lz_gN_v2.log"
MV_REF = 100.0
GP = 5.291e-05       # f_p for g_t = 1 (2 gVu + gVd, gVq = m_q/172)
TARGET = 1.12044     # LZ ROI events (main paper normalisation)


def run(mchi):
    par = os.path.join(PD, "lz2scan_%g.par" % mchi)
    with open(par, "w") as f:
        f.write("Mchi %.6g\ndM 0.001\nMV %.6g\ngChi 1.0\n" % (mchi, MV_REF))
        f.write("gB %.9e\n" % GP)
        f.write("fExc 0.5\nrho0 0.3\nv0 238\nvE 254\nvesc 544\n")
    r = subprocess.run([BIN, par, "/tmp/lz2_%g.csv" % mchi],
                       capture_output=True, text=True, cwd=PD)
    m = re.search(r"ROI_5\.4_269\.9=([\d.eE+-]+)", r.stdout)
    return (float(m.group(1)) if m else None), par


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    masses = [float(x) for x in sys.argv[1:]]
    if not masses:
        rows = list(csv.DictReader(open("/home/yy/lz-event/phenomenology/data/relic/kappa_lz_gN.csv")))
        masses = sorted(float(r["mchi"]) for r in rows)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mchi", "N_ref", "gchi_lim", "kappa"])
        with open(LOG, "w") as lg:
            lg.write("kappa v2 — corrected LZ normalisation\n")
            lg.write("binary   %s\nsha256   %s\n" % (BIN, sha(BIN)))
            lg.write("MV_ref   %.1f GeV\nf_p      %.6e\nN_target %.5f\n\n" % (MV_REF, GP, TARGET))
            lg.write("mchi,N_ref,gchi_lim,kappa,dN_rel\n")
            for m in masses:
                t0 = time.time()
                n, par = run(m)
                if not n or n <= 0:
                    lg.write("%.4f,FAILED,,,\n" % m)
                    print("m=%g FAILED" % m, flush=True)
                    continue
                glim = (TARGET / n) ** 0.5
                kap = glim / MV_REF ** 2
                w.writerow(["%.4f" % m, "%.6g" % n, "%.6e" % glim, "%.6e" % kap])
                lg.write("%.4f,%.6g,%.6e,%.6e,\n" % (m, n, glim, kap))
                lg.flush()
                print("m=%-7.4g N=%9.4f  kappa=%.4e  (%.0fs)" % (m, n, kap, time.time() - t0), flush=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

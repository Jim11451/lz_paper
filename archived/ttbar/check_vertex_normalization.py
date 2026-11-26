"""Independent spin-trace check of the recoil coefficient for the archived vertex.

This checks the analytic scattering kernel, not a new MadGraph/CalcHEP run.
The point target represents the leading coherent vector charge of a nucleus.
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def main():
    ufo = REPO / 'reproducibility/outputs/monojet_loop_20261103/model/PseudoDiracFlavorEFT_UFO_loop_R2fix/couplings.py'
    calchep = REPO / 'reproducibility/models/micromegas_photon/lgrng1.mdl'
    assert "value = '-gChi/2.'" in ufo.read_text()
    assert 'gChi/2' in next(line for line in calchep.read_text().splitlines()
                           if '~x1' in line and '~x2' in line)

    eye2, zero = np.eye(2), np.zeros((2, 2))
    pauli = [np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]),
             np.array([[1, 0], [0, -1]])]
    gamma = [np.block([[eye2, zero], [zero, -eye2]])]
    gamma += [np.block([[zero, s], [-s, zero]]) for s in pauli]
    metric = np.array([1, -1, -1, -1])
    identity = np.eye(4)

    def slash(p):
        return sum(metric[i] * p[i] * gamma[i] for i in range(4))

    rows = []
    gc, f, mv, velocity = .32, 5.291e-5, 100., 1e-3
    coefficient = (gc / 2) * f / mv**2
    for mass in (21., 36.1, 47.8):
        for target in (.939, .93149410242 * 131):
            for delta in (0., .001):
                m1, m2 = mass, mass + delta
                reduced = m2 * target / (m2 + target)
                p = reduced * velocity
                e1, e2 = math.hypot(m2, p), math.hypot(target, p)
                sqrts = e1 + e2
                s = sqrts**2
                p_out = math.sqrt((s - (m1 + target)**2) * (s - (m1 - target)**2)) / (2*sqrts)
                angle = .7
                a = np.array([e1, 0, 0, p])
                b = np.array([e2, 0, 0, -p])
                c = np.array([math.hypot(m1, p_out), p_out*math.sin(angle), 0, p_out*math.cos(angle)])
                d = np.array([math.hypot(target, p_out), -c[1], 0, -c[3]])
                total = 0j
                for mu in range(4):
                    for nu in range(4):
                        dark = np.trace((slash(c)+m1*identity) @ gamma[mu] @
                                        (slash(a)+m2*identity) @ gamma[nu])
                        nuclear = np.trace((slash(d)+target*identity) @ gamma[mu] @
                                           (slash(b)+target*identity) @ gamma[nu])
                        total += metric[mu]*metric[nu]*dark*nuclear
                matrix_squared = coefficient**2 * total.real / 4
                # d sigma/dt = |M|^2/(64 pi s p_in^2); |dt/dER| = 2 m_target.
                exact = matrix_squared * target / (32*math.pi*s*p*p)
                leading = target * coefficient**2 / (2*math.pi*velocity**2)
                ratio = exact / leading
                # Inelastic point-target corrections include delta/m_target.
                assert abs(ratio-1) < 2e-3, (mass, target, delta, ratio)
                rows.append(dict(mchi_GeV=mass, target_GeV=target, delta_GeV=delta,
                                 spin_trace_over_NR_recoil_kernel=ratio))

    fp, fn, z, a = .0091/172, .0116/172, 54, 131
    isospin = (z*fp + (a-z)*fn) / (a*fp)
    result = dict(
        dark_vertex_magnitude='gChi/2 in both archived UFO and CalcHEP',
        physical_nucleon_cross_section='mu_N^2 * gChi^2 * f_N^2 / (4*pi*MV^4)',
        recoil_kernel='m_A * gChi^2 * Q_A^2 / (8*pi*v^2*MV^4)',
        original_universal_mapping='gVq=gB/6 implies f_p=f_n=gB/2',
        original_cross_section='mu_N^2 * gChi^2 * gB^2 / (16*pi*MV^4)',
        Xe131_isospin_amplitude_ratio=isospin,
        predicted_kappa_correction_factor=2*isospin,
        numerical_scope='Dirac-matrix spin traces using the already declared transition vertex; no event generator run.',
        checks=rows)
    out = HERE / 'review_20261120/vertex_normalization.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}, indent=2))
    print('Spin-trace checks passed:', len(rows))
    print('Maximum relative correction:', max(abs(r['spin_trace_over_NR_recoil_kernel']-1) for r in rows))


if __name__ == '__main__':
    main()

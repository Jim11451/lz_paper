"""Leading photon matching and late conversion checks for the Yukawa-vector benchmarks."""

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erf


HERE = Path(__file__).resolve().parent
ALPHA = 1/137.035999
E_CHARGE = math.sqrt(4*math.pi*ALPHA)
DELTA = .001
MPLANCK = 1.22089e19
HBAR = 6.582119569e-25
AGE = 4.35e17
Z = 54
A = np.array([124,126,128,129,130,131,132,134,136])
ABUNDANCE = np.array([.00095,.00089,.01910,.26401,.04071,.21232,.26909,.10436,.08857])
FP, FN = .0091/172, .0116/172
Q0 = Z*FP+(A-Z)*FN
Q131 = float(Q0[A == 131][0])


def read(path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file))


def write(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def photon_log(scale):
    return 2*ALPHA/(3*math.pi)*math.log((scale/172)**2)


def photon_slope(q2):
    x, weight = np.polynomial.legendre.leggauss(24)
    x, weight = (x+1)/2, weight/2
    xx = x*(1-x)
    value = np.zeros_like(q2)
    for mass, charge in ((1.27, 2.), (4.18, -1.), (172., 2.)):
        value -= (2*ALPHA/math.pi)*(mass/172)*charge*np.sum(
            weight*xx*np.log1p(q2[..., None]*xx/mass**2), axis=-1)
    return value


def recoil_weights(mchi, energy):
    mass = .93149410242*A[:,None]
    q2 = 2*mass*energy[None,:]*1e-6
    mu = mchi*mass/(mchi+mass)
    vmin = 299792.458*np.abs(q2/(2*mu)-DELTA)/np.sqrt(q2)
    x, y, z = vmin/238., 254./238., 544./238.
    eta = np.where(x < z-y, erf(x+y)-erf(x-y)-4*y*np.exp(-z*z)/math.sqrt(math.pi),
                   np.where(x < z+y, erf(z)-erf(x-y)-2*(z-x+y)*np.exp(-z*z)/math.sqrt(math.pi), 0.))
    rn = np.sqrt((1.23*A[:,None]**(1/3)-.60)**2+7*math.pi**2*.52**2/3-5*.9**2)
    q = np.sqrt(q2)/.19732698
    qr = q*rn
    helm = 3*(np.sin(qr)-qr*np.cos(qr))/qr**3*np.exp(-.5*(q*.9)**2)
    return q2, ABUNDANCE[:,None]*A[:,None]*np.maximum(eta,0.)*helm**2


energy = np.linspace(5.4,269.9,1600)
q2, _ = recoil_weights(35, energy)
drun = photon_slope(q2)
loop_rows = []
for mass in (20,35,50,80,100):
    q2, weight = recoil_weights(mass, energy)
    tree = weight*Q0[:,None]**2
    base_integral = np.trapezoid(tree.sum(axis=0),energy)
    if base_integral == 0:
        continue
    for name, shift in [('heavy_subtracted_at_Q0',0.),('positive_d_1e-5',1e-5),
                        ('negative_d_1e-5',-1e-5),('photon_only_top_log_constructive',photon_log(1000)),
                        ('photon_only_top_log_destructive',-photon_log(1000)),('Xe131_cancellation',-Q131/Z)]:
        changed = weight*(Q0[:,None]+Z*(shift+drun))**2
        rate_ratio = np.trapezoid(changed.sum(axis=0),energy)/base_integral
        loop_rows.append(dict(mchi_GeV=mass, scenario=name, delta_gp0_over_gt=shift,
                              ROI_rate_ratio=rate_ratio, lz_required_kappa_ratio=rate_ratio**-.5))
    strange = (0.096/172)*(.0043/.19732698**2)*q2/6
    changed = weight*(Q0[:,None]+A[:,None]*strange)**2
    rate_ratio = np.trapezoid(changed.sum(axis=0),energy)/base_integral
    loop_rows.append(dict(mchi_GeV=mass, scenario='direct_strange_radius_only', delta_gp0_over_gt=0.,
                          ROI_rate_ratio=rate_ratio, lz_required_kappa_ratio=rate_ratio**-.5))
write(HERE/'loop_matching.csv',loop_rows)


base = read(HERE.parent/'ttmet_branch_map_20261110/branches.csv')
extra = read(HERE.parent/'monojet_mchi_scan_20261106/results/gt_mv_observed_heatmap.csv')
bench = read(HERE/'fraction_refit.csv')
thermal_points = []
for r in base:
    if float(r['gt']) > math.sqrt(4*math.pi):
        continue
    for side in ('on','off'):
        if r[f'{side}_mchi_GeV']:
            thermal_points.append((side, float(r['mv_GeV']), float(r['gt']), float(r[f'{side}_mchi_GeV']),
                                   float(r[f'{side}_gchi']), 'light_grid'))
for r in extra:
    if float(r['n_intervals']) > 0:
        thermal_points.append(('on',float(r['mass_GeV']),float(r['gt_LZ']),float(r['mchi_best_GeV']),
                               float(r['gchi_best']),'monojet_grid'))
mv, gt, mass, gc = np.array([p[1:5] for p in thermal_points]).T
eos = np.loadtxt(HERE/'eos2020.dat')[1:]
ln_eos = np.log(eos[:,0])


def gs(T):
    return np.interp(np.log(T), ln_eos, eos[:,1])


def evolve(tkd, use_bath_bound=False):
    start = mass/25
    time_grid = np.linspace(-math.log(start.max()), -math.log(1.e-6), 2200)
    f = 1/(1+np.exp(DELTA/start))
    # Yield fixed to Omega h^2 = 0.12 after annihilation freeze-out.
    total_yield = .12*1.053672e-5/(2891.2*mass)
    prefactor = (gc/2)**4*mass**2/(8*math.pi*mv**4)
    kappa = gt*gc/mv**2
    ce_upper = 2*(kappa/2)*Q131/Z
    for left, right in zip(time_grid, time_grid[1:]):
        t = math.exp(-(left+right)/2)
        active = t <= start
        geff = np.interp(math.log(t), ln_eos, eos[:,2])
        H = 1.66054*math.sqrt(geff)*t*t/MPLANCK
        dt = ((right-left)+math.log(gs(math.exp(-left))/gs(math.exp(-right)))/3)/H
        td = np.minimum(t, t*t/tkd*(gs(t)/gs(tkd))**(2/3))
        number = total_yield*(2*math.pi**2/45)*gs(t)*t**3
        sigma_v = prefactor*np.sqrt((6*td+8*DELTA)/mass)
        a = dt*number*sigma_v*active
        rr = np.exp(-2*DELTA/td)
        B = 1+2*a*rr
        c = f+a*rr
        f = 2*c/(B+np.sqrt(B**2+4*a*(1-rr)*c))
        if use_bath_bound and t >= .020:
            f = np.where(active, np.minimum(f, 1/(1+np.exp(DELTA/t))), f)
        elif use_bath_bound:
            # Fast SM equilibrium at T >= 20 MeV, and a deliberately enlarged
            # downward-only estimate below it, with no tuned Xe cancellation.
            bath = .366*t**3*(16/math.pi)*ce_upper**2*(t+DELTA+.000511)**2
            for hadron, dof, charge in ((.13957,2.,.0025/172),(.494,4.,.0938/172),(.938,8.,FN)):
                density = 2*dof*(hadron*t/(2*math.pi))**1.5*math.exp(-hadron/t)
                if hadron > .9:
                    density += 6.2e-10*.244*t**3
                bath += density*(4/math.pi)*((kappa/2)*charge+ce_upper)**2*hadron**2
            f *= np.exp(-bath*dt)
    return f


f_self = evolve(mass/25)
f_bath = evolve(mass/25, use_bath_bound=True)
f_late = evolve(np.full_like(mass, .10))
# 10% population loss through Z mass mixing or a transition dipole.
gamma10 = -math.log(.9)*HBAR/AGE
g_weak, cw, mz = .653, .8815, 91.1876
mix = (gamma10*640*math.pi**3*cw**2*mz**4*mv**4/(g_weak**2*gc**2*DELTA**5))**.25
ce_upper = gt*gc/mv**2*Q131/Z
gamma_3g = (17*(2*ce_upper/E_CHARGE)**2*ALPHA**4/(5472967500*math.pi**5)
            *DELTA**13/.000510999**8)
halo = .3/mass*((gc/2)**4*mass**2/(8*math.pi*mv**4))*np.sqrt(8*DELTA/mass)*1.16733e-17*AGE
results=[]
for i,p in enumerate(thermal_points):
    results.append(dict(branch=p[0],mv_GeV=p[1],gt=p[2],mchi_GeV=p[3],gchi=p[4],source=p[5],
                        f2_self_early_kd=f_self[i],f2_self_late_kd=f_late[i],f2_with_bath_stress=f_bath[i],
                        VZ_massmix_10pct_MeV=1000*mix[i], photon3_lifetime_EH_s=HBAR/gamma_3g[i],
                        halo_self_optical_depth=halo[i]))
write(HERE/'thermal_fraction.csv',results)

fig, axes = plt.subplots(1,2,figsize=(9.3,4.0),layout='constrained')
d = np.linspace(-.00045,.00045,500)
axes[0].plot(d*1e4,(1+Z*d/Q131)**2,color='#356c9d')
axes[0].axhline(1,color='#6d7377',ls=':')
axes[0].axvline(-Q131/Z*1e4,color='#b26235',ls='--')
axes[0].set(xlabel=r'$10^4\,e\epsilon_\gamma(0)/g_t$', ylabel=r'$R_{\mathrm{Xe131}}/R_{\rm tree}$',
            title='Coherent photon interference')
axes[0].set_ylim(0,17)
for group,color in [('on','#356c9d'),('off','#bc7446')]:
    selected=[i for i,p in enumerate(thermal_points) if p[0]==group]
    axes[1].scatter(mv[selected],f_bath[selected],s=4,alpha=.38,color=color,label=group+'-shell')
axes[1].axhline(.5,color='#6d7377',ls=':')
axes[1].set(xlabel=r'$M_V$ [GeV]',ylabel=r'$f_2$ after scattering',title='Early kinetic decoupling stress test')
axes[1].legend(frameon=False)
fig.savefig(HERE/'lz_consistency_checks.png',dpi=210)

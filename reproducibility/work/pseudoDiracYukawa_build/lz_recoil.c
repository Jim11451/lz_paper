#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/micromegas.h"
#include "../include/micromegas_aux.h"
#include "lib/pmodel.h"

#define OUT_DIM 700
#define OUT_EMIN_KEV 1.0
#define OUT_EMAX_KEV 1000.0

static double maxwell_over_v(double v)
{
    /* Match micrOMEGAs' regularized f(v)/v kernel (directDet.c:vfv). */
    if (v < 1.0) return v*Maxwell(1.0);
    return Maxwell(v)/v;
}

static double eta_above(double vmin)
{
    const double vmax = vEsc + vEarth;
    if (vmin >= vmax) return 0.0;
    if (vmin < 0.0) vmin = 0.0;
    return simpson(maxwell_over_v, vmin, vmax, 1.0e-5, NULL);
}

static double integrate_window(const double *energy, const double *rate,
                               double lo, double hi)
{
    double sum = 0.0;
    for (int i = 0; i + 1 < OUT_DIM; ++i) {
        const double x1 = energy[i];
        const double x2 = energy[i+1];
        if (x2 <= lo || x1 >= hi) continue;
        const double a = x1 < lo ? lo : x1;
        const double b = x2 > hi ? hi : x2;
        if (b <= a) continue;
        const double ya = rate[i] + (rate[i+1]-rate[i])*(a-x1)/(x2-x1);
        const double yb = rate[i] + (rate[i+1]-rate[i])*(b-x1)/(x2-x1);
        sum += 0.5*(ya+yb)*(b-a);
    }
    return sum;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s PARAM_CARD OUTPUT_CSV\n", argv[0]);
        return 2;
    }

    int err = readVar(argv[1]);
    if (err) {
        fprintf(stderr, "readVar failed: %d\n", err);
        return 3;
    }
    char cdmName[32] = "";
    err = sortOddParticles(cdmName);
    if (err) {
        fprintf(stderr, "sortOddParticles failed for %s: %d\n", cdmName, err);
        return 4;
    }

    const double dm = findValW("dM");
    const double mV = findValW("MV");
    const double gYt = findValW("gYt");
    const double fpN = gYt*(2*0.0022+0.0047)/172.0;
    const double fnN = gYt*(0.0022+2*0.0047)/172.0;
    const double gchi = findValW("gChi");
    const double fexc = findValW("fExc");
    rhoDM = findValW("rho0");
    vRot = findValW("v0");
    vEarth = findValW("vE");
    vEsc = findValW("vesc");

    /* Leading conserved vector charges. The dark vertex is gChi/2;
       sigma_p,n = mu_N^2 (gChi*f_p,n)^2 / (4*pi*MV^4).
       This reduces to the original formula for f_p=f_n=gB/2. */
    const double mn = 0.939;
    const double pb_per_GeV2 = 3.89379372e8;
    const double muN = mn*Mcdm/(mn+Mcdm);
    const double sigmaP_pb = muN*muN*fpN*fpN*gchi*gchi
                             /(4.0*M_PI*pow(mV,4))*pb_per_GeV2;
    const double sigmaN_pb = muN*muN*fnN*fnN*gchi*gchi
                             /(4.0*M_PI*pow(mV,4))*pb_per_GeV2;

    const int niso = 9;
    const int A[9] = {124,126,128,129,130,131,132,134,136};
    const int Z = 54;
    const double abundance[9] = {
        0.00095,0.00089,0.01910,0.26401,0.04071,
        0.21232,0.26909,0.10436,0.08857
    };
    double energy[OUT_DIM];
    double rate[OUT_DIM];
    for (int i = 0; i < OUT_DIM; ++i) {
        energy[i] = OUT_EMIN_KEV*pow(OUT_EMAX_KEV/OUT_EMIN_KEV,
                                     (double)i/(OUT_DIM-1));
        rate[i] = 0.0;
    }

    double meanA = 0.0;
    for (int k = 0; k < niso; ++k) meanA += abundance[k]*A[k];

    for (int k = 0; k < niso; ++k) {
        double elastic_iso[RE_DIM];
        const double mass_fraction = abundance[k]*A[k]/meanA;
        const double mA = 0.93149410242*A[k];
        const double muA = mA*Mcdm/(mA+Mcdm);

        nucleusRecoil0CS(Maxwell, A[k], Z, 0.0, 0.0, 0.0,
                         sigmaP_pb, sigmaN_pb, 0.0, 0.0, elastic_iso);

        /* micrOMEGAs' built-in recoil table ends below 100 keV.  Extract its
           absolute normalization at the first elastic grid point, then use
           the same Helm form factor to extend Eq. (20) through 1 MeV. */
        const double er_ref = RE_START*1.0e-6;
        const double mA_dd = 0.94*A[k];
        const double muA_dd = mA_dd*Mcdm/(mA_dd+Mcdm);
        const double vmin_ref = 299792.458*sqrt(mA_dd*er_ref/
                                               (2.0*muA_dd*muA_dd));
        const double p_ref = sqrt(2.0*mA_dd*er_ref)/0.197327;
        const double eta_ref = eta_above(vmin_ref);
        const double ff2_ref = pow(FermiFF(A[k], p_ref), 2.0);
        if (eta_ref <= 0.0 || ff2_ref <= 0.0 || elastic_iso[0] <= 0.0) {
            fprintf(stderr, "failed recoil normalization for Xe-%d\n", A[k]);
            return 5;
        }
        const double norm = elastic_iso[0]/(eta_ref*ff2_ref);

        for (int i = 0; i < OUT_DIM; ++i) {
            const double er = energy[i]*1.0e-6;
            const double q2 = 2.0*mA*er;
            const double vmin_ex = 299792.458*fabs(mA*er/muA-dm)
                                   /sqrt(2.0*mA*er);
            const double eta_ex = eta_above(vmin_ex);
            const double p = sqrt(q2)/0.197327;
            const double ff2 = pow(FermiFF(A[k], p), 2.0);
            const double propagator = pow(mV,4)/pow(mV*mV+q2,2);
            rate[i] += fexc*mass_fraction*norm*ff2*eta_ex*propagator;
        }
    }

    FILE *fp = fopen(argv[2], "w");
    if (!fp) {
        perror(argv[2]);
        return 5;
    }
    fprintf(fp, "# pseudo-Dirac U(1)_B exothermic xenon recoil, arXiv:2609.26570v1\n");
    fprintf(fp, "# Mchi_GeV=%.9g delta_keV=%.9g MV_GeV=%.9g gYt=%.9g gChi=%.9g fExc=%.9g sigmaP_pb=%.9e sigmaN_pb=%.9e\n",
            Mcdm, 1.0e6*dm, mV, gYt, gchi, fexc, sigmaP_pb, sigmaN_pb);
    fprintf(fp, "# rho0=%.9g v0=%.9g vEarth=%.9g vEsc=%.9g\n",
            rhoDM, vRot, vEarth, vEsc);
    fprintf(fp, "ER_keV,dRdER_events_per_kg_day_keV\n");
    for (int i = 0; i < OUT_DIM; ++i)
        fprintf(fp, "%.9e,%.9e\n", energy[i], rate[i]);
    fclose(fp);

    const double exposure_kg_day = 2.84e3*365.25;
    const double nroi = integrate_window(energy, rate, 5.4, 269.9)*exposure_kg_day;
    const double nsb = integrate_window(energy, rate, 350.0, 675.0)*exposure_kg_day;
    const double nwide = integrate_window(energy, rate, 1.0, 1000.0)*exposure_kg_day;
    const double mA131 = 0.93149410242*131.0;
    const double muA131 = mA131*Mcdm/(mA131+Mcdm);
    const double zero131 = 1.0e6*dm*muA131/mA131;

    printf("MODEL pseudo-Dirac U(1)_B exothermic xenon recoil\n");
    printf("CDM=%s Mchi=%.9g GeV delta=%.9g keV MV=%.9g GeV\n",
           CDM[1], Mcdm, 1.0e6*dm, mV);
    printf("COUPLINGS gYt=%.9g gChi=%.9g fp=%.9e fn=%.9e sigmaP=%.9e_pb sigmaN=%.9e_pb\n",
           gYt, gchi, fpN, fnN, sigmaP_pb, sigmaN_pb);
    printf("HALO rho_total=%.9g fExc=%.9g rho_exc=%.9g GeV/cm3 v0=%.9g vEarth=%.9g vEsc=%.9g km/s\n",
           rhoDM, fexc, rhoDM*fexc, vRot, vEarth, vEsc);
    printf("KINEMATICS Xe131_vmin_zero_ER=%.9g keV\n", zero131);
    printf("TRUTH_EVENTS exposure=2.84_tonne_year ROI_5.4_269.9=%.9e SB_350_675=%.9e wide_1_1000=%.9e\n",
           nroi, nsb, nwide);
    printf("NOTE detector efficiency and energy resolution are not applied in these integrals\n");
    return 0;
}

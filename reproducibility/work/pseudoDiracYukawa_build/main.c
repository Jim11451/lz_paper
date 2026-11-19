#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/micromegas.h"
#include "../include/micromegas_aux.h"
#include "lib/pmodel.h"

static void show_width(const char *name)
{
    txtList channels = NULL;
    const double width = pWidth((char *)name, &channels);
    printf("WIDTH %-4s %.9e GeV\n", name, width);
    if (channels) printTxtList(channels, stdout);
}

static double paper_sigma_v(double mchi, double mV, double gchi)
{
    const double r = (mV*mV)/(mchi*mchi);
    if (r >= 1.0) return 0.0;
    return pow(gchi, 4)/(256.0*M_PI*mchi*mchi)
           * pow(1.0-r, 1.5)/pow(1.0-r/2.0, 2.0);
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s benchmark.par\n", argv[0]);
        return 2;
    }

    int err = readVar(argv[1]);
    if (err == -1) {
        fprintf(stderr, "cannot open %s\n", argv[1]);
        return 3;
    }
    if (err > 0) {
        fprintf(stderr, "bad parameter file line %d\n", err);
        return 4;
    }

    char cdmName[32] = "";
    err = sortOddParticles(cdmName);
    if (err) {
        fprintf(stderr, "sortOddParticles failed for %s: %d\n", cdmName, err);
        return 5;
    }

    const double mchi = findValW("Mchi");
    const double dm = findValW("dM");
    const double m2 = findValW("Mchi2");
    const double mV = findValW("MV");
    const double gYt = findValW("gYt");
    const double gchi = findValW("gChi");
    const double fexc = findValW("fExc");
    const int inputOK = mchi > 0.0 && dm > 0.0 && mV > 0.0 &&
                        gYt > 0.0 && gchi > 0.0 &&
                        fexc >= 0.0 && fexc <= 1.0;
    const int massOK = fabs(m2-(mchi+dm)) < 1.0e-10;

    printf("MODEL pseudo-Dirac U(1)_B mass-basis benchmark (arXiv:2609.26570v1)\n");
    printf("CDM %s  Mchi1=%.9g GeV  Mchi2=%.9g GeV  delta=%.9g GeV (%.9g keV)\n",
           CDM[1], mchi, m2, dm, 1.0e6*dm);
    printf("MEDIATOR MV=%.9g GeV  gYt=%.9g  gChi=%.9g\n",
           mV, gYt, gchi);
    printf("YUKAWA_VECTOR gYu=%.9g gYd=%.9g gYs=%.9g gYc=%.9g gYb=%.9g gYt=%.9g\n",
           gYt*0.0022/172, gYt*0.0047/172, gYt*0.096/172,
           gYt*1.27/172, gYt*4.18/172, gYt);
    printf("HALO excited_fraction=%.9g  rho0=%.9g GeV/cm^3  v0=%.9g  vEarth=%.9g  vEsc=%.9g km/s\n",
           fexc, findValW("rho0"), findValW("v0"),
           findValW("vE"), findValW("vesc"));
    printf("CHECK input=%s  mass_relation=%s  delta_below_2me=%s\n",
           inputOK ? "PASS" : "FAIL",
           massOK ? "PASS" : "FAIL",
           dm < 2.0*0.00051099895 ? "PASS" : "FAIL");
    if (!inputOK || !massOK) return 6;

    printMasses(stdout, 1);
    show_width("V");
    show_width("~x2");

    /* Eq. (13) of arXiv:2609.26570v1. This is the single-species
       chi_i chi_i -> VV rate; sigma_eff is one half in the degenerate limit. */
    const double gev2_to_cm3s = 0.389379338e-27 * 2.99792458e10;
    const double sv = paper_sigma_v(mchi, mV, gchi)*gev2_to_cm3s;
    printf("PAPER_SIGMAV chi_i_chi_i_to_VV=%.9e cm^3/s  sigma_eff=%.9e cm^3/s\n",
           sv, 0.5*sv);

    double Xf = 0.0;
    const int fast = 1;
    const double Beps = 1.0e-5;
    const double cut = 0.005;
    const double omega = darkOmega(&Xf, fast, Beps, &err);
    printf("RELIC err=%d Xf=%.8g Omega_h2=%.9e\n", err, Xf, omega);
    if (!err && omega > 0.0) {
        const double pb_to_cm3s = 2.99792458e-26;
        const double vs_fo_pb = vSigmaA(mchi/Xf, fast, Beps);
        const double vs_degenerate_pb = vSigmaA(1.0e-2, fast, Beps);
        const double vs_single_pb = vSigmaA(1.0e-4, fast, Beps);
        printf("MICROMEGAS_VSIGMA freezeout_T=%.9e_GeV value=%.9e_pb value=%.9e_cm3/s\n",
               mchi/Xf, vs_fo_pb, vs_fo_pb*pb_to_cm3s);
        printf("MICROMEGAS_VSIGMA near_degenerate_T=1.000000000e-02_GeV value=%.9e_pb value=%.9e_cm3/s\n",
               vs_degenerate_pb, vs_degenerate_pb*pb_to_cm3s);
        printf("MICROMEGAS_VSIGMA single_state_T=1.000000000e-04_GeV value=%.9e_pb value=%.9e_cm3/s\n",
               vs_single_pb, vs_single_pb*pb_to_cm3s);
        printf("CHANNELS contributing more than %.3g percent to 1/Omega\n", 100.0*cut);
        printChannels(Xf, cut, Beps, 1, stdout);
    }
    return err ? 10 : 0;
}

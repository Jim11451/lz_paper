#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../include/micromegas.h"
#include "../include/micromegas_aux.h"
#include "lib/pmodel.h"

int main(int argc, char **argv) {
    if (argc != 6) return 2;
    assignValW("Mchi",atof(argv[1]));
    assignValW("dM",0.001);
    assignValW("MV",atof(argv[2]));
    assignValW("gYt",atof(argv[3]));
    assignValW("gChi",atof(argv[4]));
    assignValW("dPhot",atof(argv[5]));
    char name[32]="";
    if (sortOddParticles(name)) return 3;

    int err=0;
    double xf=0, omega=darkOmega(&xf,0,1e-9,&err);
    double width=pWidth("V",NULL);
    printf("RESULT %.12g %.12g %.12g %d\n",omega,xf,width,err);
    return err ? 4 : 0;
}

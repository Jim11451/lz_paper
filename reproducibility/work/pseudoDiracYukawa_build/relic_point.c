#include <stdio.h>
#include <stdlib.h>
#include "../include/micromegas.h"
#include "../include/micromegas_aux.h"
#include "lib/pmodel.h"

int main(int argc, char **argv) {
    if (argc != 5 && argc != 6) return 2;
    assignValW("Mchi",35.0); assignValW("dM",0.001);
    assignValW("MV",atof(argv[1]));
    assignValW("gYt",atof(argv[2]));
    assignValW("gChi",atof(argv[3]));
    char name[32]="";
    int err=sortOddParticles(name);
    if(err) {printf("ERROR sort=%d\n",err); return 3;}
    int fast=argc==6 ? atoi(argv[5]):1;
    double xf=0, omega=darkOmega(&xf,fast,1e-5,&err);
    double width=pWidth("V",NULL);
    printf("RESULT MV=%.12g gYt=%.12g gChi=%.12g Omega=%.12g Xf=%.12g width=%.12g err=%d\n",
           findValW("MV"),findValW("gYt"),findValW("gChi"),omega,xf,width,err);
    if(!err && atoi(argv[4])) printChannels(xf,0.005,1e-5,1,stdout);
    return err ? 4:0;
}

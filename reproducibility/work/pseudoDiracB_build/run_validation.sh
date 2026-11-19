#!/usr/bin/env bash
set -euo pipefail
make main=main.c
./main benchmark.par | tee validation_benchmark.log
./main micromegas_relic.par | tee validation_micromegas_relic.log
make main=lz_recoil.c
./lz_recoil benchmark.par recoil_benchmark.csv | tee recoil_benchmark.log
./lz_recoil micromegas_relic.par recoil_micromegas_relic.csv | tee recoil_micromegas_relic.log

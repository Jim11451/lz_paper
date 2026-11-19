#!/bin/sh
# Set LZ_GFORTRAN to the installed compiler path when it differs from /usr/bin/gfortran.
exec "${LZ_GFORTRAN:-/usr/bin/gfortran}" -fallow-argument-mismatch "$@" -lstdc++

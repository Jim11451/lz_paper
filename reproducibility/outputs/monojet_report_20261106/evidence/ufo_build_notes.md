# Build notes, 2026-11-03

Host environment uses conda GCC/gfortran 14.3.0. The installed MG5 3.6.6 had
not previously built its loop reduction providers. MG5 installed OneLOop,
Ninja and COLLIER and compiled vendor CutTools and IREGI during process export.

Three build-only compatibility issues were addressed inside this task:

1. Legacy scalar/array argument calls need `-fallow-argument-mismatch`.
2. Linking the Ninja static archive from Fortran needs the C++ runtime; the
   private compiler wrapper appends `-lstdc++`.
3. Both CutTools and MadEvent's generic `setrun.f` define `DDILOG`. In the
   private process, only the generic helper and its same-file calls are renamed
   to `MGDDILOG`, avoiding duplicate symbols without changing loop physics.

The compiler wrapper is under the private task `bin/`, selected via environment
`FC` and `FFLAGS`; the shared compiler executable was not modified. A temporary
local CutTools archive experiment was reverted to the full original contents.
The original generic `setrun.f` is preserved in the task root.

Ward checks compiled independently of event integration. At the recorded
benchmark/phase-space point, the fixed model passed with BRS/matrix ratio
6.2728358221e-24; the original upload failed with ratio 4.4111539890e+04.
See the archived logs for the actual test and settings.

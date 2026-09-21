# Structural FEA screening

This lane adds a real finite-element solver check for the most load-sensitive
printed pendulum member: `PENDULUM_ARM.stl`.

## Evidence level

A successful run emits:

`STRUCTURAL_FEA_SCREENING_PASS`

It deliberately does **not** emit `STRUCTURAL_ANALYSIS_PASS`.

The tracked STL is meshed and solved, but printed PETG is currently represented
as an assumed isotropic solid. The real part uses walls + infill and has
direction-dependent FDM properties. Coupon-backed properties and a release load
case are required before structural release authority.

## Pipeline

```
tracked PENDULUM_ARM.stl
  -> Gmsh 4.15.2 surface classification
  -> first-order tetrahedral volume mesh
  -> CalculiX C3D4 static solve
  -> integration-point stress
  -> nodal displacement
  -> fail-closed screening report
```

The solver uses N/mm/MPa units.

## Load case

The screening load uses the maximum configured ballast mass plus the current
assumed pendulum-extra mass, multiplies it by a 5 g shock factor, and assigns
half to one arm. The root end is fixed and the force is distributed over the
opposite end in the weakest bending direction.

This is intentionally conservative, but it is still an abstraction of the real
two-bolt hub and ballast-saddle interfaces.

## Local run

Ubuntu/Debian dependencies:

```bash
sudo apt-get install calculix-ccx libglu1-mesa
python -m pip install -r mechanical/spherical_robot/fea/requirements-fea.txt
python mechanical/spherical_robot/fea/run_structural_fea.py
```

The report always retains `physical_accepted=false`.

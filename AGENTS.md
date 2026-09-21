# ESP32-P4-M3 agent rules

## Scope and authority

This is one product repository. For spherical-robot work stay in project scope and do not create a second CAD, task, simulation or parameter authority.

Canonical mechanical root: `mechanical/spherical_robot`.
Canonical dimensional authority: `mechanical/spherical_robot/config/dimensions.json`.

`3D-model/fiish.*` is historical/non-authoritative for the current robot. Generated `build/`, managed vendor components and Playwright artifacts are not normal mutation targets.

## Required engineering route

For a functional robot task use the tracked system skills for:

- production 3D modeling;
- CAD assembly visualization;
- FDM/DfAM and print reality projection;
- robotics physics simulation.

Keep these evidence layers distinct:

`parameters -> analytic screening -> CAD collision sweep -> multibody dynamics -> independent dynamics cross-check -> FEA -> controller-in-loop -> HIL -> physical subassembly -> physical system -> repeated validation`.

Never call Blender animation, analytical equations, MuJoCo, FEA or HIL a physical test.

## Parameter discipline

Every physical input must remain classified as measured, datasheet, calculated, assumed, placeholder or identified from test. Do not remove `_PLACEHOLDER` semantics just to make a model look complete.

When a measured component changes:

1. update `config/dimensions.json`;
2. run the dependency-free tests and sizing report;
3. regenerate CAD/collision evidence when Blender is available;
4. regenerate/re-run the applicable simulation layer;
5. invalidate downstream evidence whose inputs changed.

Do not hand-copy canonical dimensions into solver models when generation can bind them automatically.

## Verification

Minimum source checks for spherical-robot mutations:

```bash
python -m unittest discover -s mechanical/spherical_robot/tests -p 'test_*.py'
python mechanical/spherical_robot/calculations.py --json
git diff --check
```

If the change affects CAD, also run the Blender build/validation when the tool is available. If it affects release-critical dynamics, MuJoCo execution and an independent multibody cross-check remain required before design freeze. If it affects load-bearing geometry, run the applicable structural analysis.

## Completion truth

Source prepared, CI green, solver-verified, HIL-verified and physically accepted are separate states. Missing real measurements or unavailable solver/tooling must stay explicit blockers; never fabricate results.

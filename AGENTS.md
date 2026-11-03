# ESP32-P4-M3 agent rules

## Product identity

This repository contains one spherical-robot product plus legacy ESP32-P4 bench infrastructure.

Do not conflate these two control systems:

- `components/app/src/app_control.c` + `app_stepper.c` is the legacy L293D/IMU bench stabilization path;
- spherical-robot product control must use semantic robot inputs/outputs and must not inherit the dual-drive L293D model by accident.

A task about the sphere, pendulum, steering, physical enclosure, dynamics, HIL, or robot controller is a **spherical-robot product task**.

## Canonical authorities

Never create a second source of truth when one already exists.

- mechanical root: `mechanical/spherical_robot/`;
- dimensions + physical evidence status: `mechanical/spherical_robot/config/dimensions.json`;
- analytical sizing: `mechanical/spherical_robot/calculations.py`;
- CAD: `mechanical/spherical_robot/blender/`;
- simulation: `mechanical/spherical_robot/simulation/`;
- structural analysis: `mechanical/spherical_robot/fea/`;
- firmware defaults: `sdkconfig.defaults`;
- ESP-IDF version: pinned `esp-idf` gitlink and `dependencies.lock`;
- managed ESP-IDF dependencies: `main/idf_component.yml` + `dependencies.lock`;
- repository invariants: `scripts/verify_repo_contract.py`.

`3D-model/fiish.*` is historical and non-authoritative.

## Context-loading discipline

For a broad task, read in this order:

1. `AGENTS.md`;
2. `README.md`;
3. the canonical config for the affected domain;
4. only the relevant source/component files;
5. the matching tests/workflow;
6. detailed Obsidian/coursework docs only if the task actually needs them.

Do not spend context traversing generated or vendored state.

Normal mutation targets exclude:

- `build/`;
- `managed_components/`;
- `.playwright-mcp/`;
- `sdkconfig` and `sdkconfig.old`;
- `__pycache__` / `*.pyc`;
- Blender `*.blend1` backups;
- Node `node_modules/` and `dist/`.

## Evidence ladder

Keep these states distinct:

`parameters -> analytic screening -> CAD collision -> primary multibody -> independent multibody cross-check -> FEA -> controller-in-loop -> HIL -> physical subassembly -> physical system -> repeated validation`.

Never call analytical equations, Blender animation, MuJoCo, Project Chrono, FEA, or HIL a physical test.

A successful upstream layer does not automatically validate downstream layers.

## Parameter discipline

Every physical input must remain classified as measured, datasheet-backed, calculated, specified, assumed, placeholder, user-reported, or identified from test.

Do not remove `_PLACEHOLDER` semantics just to make a model look complete.

When a physical input changes:

1. update `config/dimensions.json` and its status;
2. run the repository contract and analytical sizing;
3. regenerate CAD/collision evidence if geometry/envelopes changed;
4. rerun affected multibody/FEA/controller evidence;
5. invalidate downstream evidence whose source hashes or assumptions changed.

Do not hand-copy canonical dimensions into solver/controller configs when they can be read from the canonical source.

## Actuator/controller rule

Component selection and controller tuning are separate problems.

The drive requirement is the worst configured ballast/radius result from `calculations.py`, not a nominal hand-copied value.

If the current actuator is `PLACEHOLDER` or fails the mechanical torque screen:

- keep that blocker explicit;
- do not lower controller acceptance thresholds to make CI green;
- do not claim controller readiness;
- do not tune against invented torque-speed data.

Controller-in-loop becomes meaningful only after actuator parameters are datasheet-bound or measured.

## Firmware rules

Firmware bring-up should be fail-soft where safe:

- loss of an optional sensor must not prevent unrelated networking or bench-control initialization;
- failed subsystem initialization must be visible in status/telemetry;
- a subsystem tick should not run unless its initialization succeeded;
- recovery/diagnostic code must restore shared peripheral state before returning.

System identity and app mode must come from the actual build/runtime configuration, never stale example strings.

## Verification

Minimum checks for any non-trivial mutation:

```bash
python scripts/verify_repo_contract.py
python -m unittest discover -s mechanical/spherical_robot/tests -p 'test_*.py'
python mechanical/spherical_robot/calculations.py --json
git diff --check
```

For firmware changes, require the ESP32-P4 firmware build workflow.

For CAD changes, regenerate and validate Blender outputs when available.

For release-critical dynamics, run the one-shot multibody entrypoint so MuJoCo, Chrono, and comparison share one exact worktree/sandbox lifetime.

For load-bearing geometry, run structural screening/analysis appropriate to the evidence level.

For controller changes, require controller-in-loop and preserve actuator/hardware limitations explicitly.

## Completion truth

These are different statements and must never be collapsed:

- source prepared;
- static/unit checks pass;
- firmware compiles;
- CAD regenerated;
- solver verified;
- controller-in-loop verified;
- HIL verified;
- physical subassembly verified;
- full robot physically accepted.

Missing measurements, unavailable solvers, red CI, placeholder actuator data, or absent hardware binding are blockers, not wording problems.

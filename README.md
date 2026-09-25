# ESP32-P4-M3 — spherical robot

This repository contains the mechanical, simulation, firmware, telemetry, and operator-tooling work for a pendulum-driven steerable spherical robot built around ESP32-P4-M3.

The repository also contains an older ESP32-P4 laboratory/bench control stack. That bench code is useful infrastructure, but it is **not** the product controller authority for the spherical robot.

## Engineering truth model

Do not create a second authority for the same information.

| Domain | Canonical source |
|---|---|
| Mechanical dimensions and physical-input status | `mechanical/spherical_robot/config/dimensions.json` |
| Analytical sizing | `mechanical/spherical_robot/calculations.py` |
| CAD generation and collision validation | `mechanical/spherical_robot/blender/` |
| Printable outputs | `mechanical/spherical_robot/exports/stl/` + `exports/print_manifest.json` |
| Multibody model and solver configuration | `mechanical/spherical_robot/simulation/` |
| Structural screening | `mechanical/spherical_robot/fea/` |
| ESP-IDF version | pinned `esp-idf` git submodule + `dependencies.lock` |
| Firmware defaults | `sdkconfig.defaults` |
| ESP-IDF component dependencies | `main/idf_component.yml` + `dependencies.lock` |
| Agent/change policy | `AGENTS.md` |
| Repository invariants | `scripts/verify_repo_contract.py` |

The historical `3D-model/fiish.*` files are non-authoritative for the current robot.

## Current engineering state

The current source has strong virtual evidence, but it is not a physically accepted product.

- generated CAD parts are manifold and the tracked collision report passes the current virtual sweep;
- reduced-order analytical screening exists;
- MuJoCo 3.13.0 primary dynamics and Project Chrono 10.0.0 independent cross-check exist;
- `PENDULUM_ARM` has CalculiX structural screening;
- `physical_accepted` intentionally remains `false`;
- multiple component envelopes and actuator properties remain `PLACEHOLDER` or `ASSUMED`;
- the current placeholder pendulum actuator does **not** meet the worst-configured continuous torque screen from `calculations.py`;
- the legacy `app_control.c + app_stepper.c` path is a bench stabilization demo, not the release spherical-robot controller;
- real pendulum encoder, steering actuator/sensor, HIL, and full physical rolling evidence are still required.

Do not weaken tests or tune a controller around placeholder actuator data just to obtain a green result.

## Fast verification

Run this first after checkout and before a broad review:

```bash
python scripts/verify_repo_contract.py
python -m unittest discover -s mechanical/spherical_robot/tests -p 'test_*.py'
python mechanical/spherical_robot/calculations.py --json
git diff --check
```

The sizing report is the quickest way to see unresolved physical inputs and the current actuator torque margin.

## Mechanical / simulation verification

Dependency-free baseline:

```bash
python mechanical/spherical_robot/simulation/run_sweep.py --output /tmp/spherical-sweep.json
python mechanical/spherical_robot/simulation/mujoco_model.py --output /tmp/spherical-robot.xml
```

Full geometry regeneration requires Blender:

```bash
blender --background --factory-startup \
  --python mechanical/spherical_robot/blender/build_robot.py
```

Full multibody evidence requires MuJoCo and Project Chrono. CI and bounded agents use one product-owned entrypoint:

```bash
python mechanical/spherical_robot/simulation/run_multibody_crosscheck.py \
  --output /tmp/multibody-crosscheck.json
```

Structural screening:

```bash
python mechanical/spherical_robot/fea/run_structural_fea.py \
  --output /tmp/structural-fea.json
```

A solver pass is not a physical test.

## Firmware

Production source lives under `main/` and `components/`.

The current bench firmware provides:

- I2C and MPU-9250 bring-up;
- L293D motor bench control;
- UART control;
- Wi-Fi AP/STA support;
- HTTP/WebSocket telemetry/control;
- BLE status/control infrastructure;
- a cooperative 5 ms application tick.

Firmware CI builds the project for `esp32p4` with pinned ESP-IDF 5.5.2.

For local development, initialize the pinned submodule:

```bash
git submodule update --init --recursive esp-idf
direnv allow
idf.py build
```

`.envrc` prefers the repository-pinned ESP-IDF and falls back to `$HOME/esp/esp-idf` only when the submodule is unavailable.

## Physical build gate

Before final-fit printing or design freeze:

1. measure/bind the critical inputs listed in `mechanical/spherical_robot/NEEDS_MEASUREMENT.md`;
2. replace the corresponding `PLACEHOLDER` / `ASSUMED` values with measured or datasheet-backed evidence;
3. regenerate CAD and collision evidence;
4. rerun sizing and relevant solver layers;
5. characterize the actual motor/driver/encoder on the pendulum test stand;
6. rerun controller-in-loop using the measured actuator contract;
7. bind the controller to real firmware drivers;
8. perform HIL and physical subassembly tests;
9. only then perform full-sphere rolling tests.

## Repository hygiene

Generated state is intentionally not source:

- `build/`;
- `managed_components/`;
- `.playwright-mcp/`;
- `sdkconfig` / `sdkconfig.old`;
- Python caches;
- Blender `*.blend1` backups;
- Node build/dependency outputs.

`dependencies.lock`, the ESP-IDF submodule, source code, canonical CAD inputs, and intentional engineering exports remain tracked.

The repository contract workflow fails if generated state or stale legacy identity returns.

# ESP32-P4-M3 — spherical robot

This repository contains the ESP32-P4-M3 firmware/control stack and the current mechanical source for a pendulum-driven steerable spherical robot.

## Current engineering source of truth

The active mechanical project is:

`mechanical/spherical_robot/`

Key sources:

- `config/dimensions.json` — canonical mechanical dimensions, component envelopes and evidence status;
- `calculations.py` — deterministic sizing/load/traction screening;
- `blender/build_robot.py` + `blender/validate_robot.py` — exact assembly generation, topology and collision sweep;
- `simulation/` — reduced-order digital twin plus generated MuJoCo model contract;
- `DIGITAL_TWIN.md` — evidence ladder and commands;
- `NEEDS_MEASUREMENT.md` — physical measurements still required before final fits;
- `ASSEMBLY.md` and `PRINTING.md` — staged physical build path.

The historical `3D-model/fiish.*` files are not the current spherical-robot CAD authority.

## Verification

Dependency-free digital checks:

```bash
python -m unittest discover -s mechanical/spherical_robot/tests -p 'test_*.py'
python mechanical/spherical_robot/calculations.py --json
python mechanical/spherical_robot/simulation/run_sweep.py
python mechanical/spherical_robot/simulation/mujoco_model.py --output /tmp/spherical_robot.xml
```

Full geometry regeneration requires Blender:

```bash
blender --background --factory-startup --python mechanical/spherical_robot/blender/build_robot.py
```

MuJoCo, Project Chrono and FreeCAD/CalculiX are higher evidence layers. Their absence must be reported as pending/blocked; generated XML or Blender animation is not solver evidence and no simulation is physical validation.

## Firmware

ESP-IDF application code lives under `main/` and `components/`. The current repository includes MPU-9250, I2C, stepper/control, Wi-Fi/network and telemetry code.

Local/generated `sdkconfig` and `build/` remain ignored because they may contain machine-local configuration.

# Spherical robot digital twin

## Goal

The digital twin binds the existing exact mechanical parameter/CAD pipeline to dynamics and later firmware/HIL evidence. It does **not** replace physical measurements or tests.

## Evidence ladder

1. `PARAMETER_CONTRACT_VALIDATED`
2. `ANALYTIC_BASELINE_PASS`
3. `CAD_COLLISION_SWEEP_PASS`
4. `PRIMARY_MULTIBODY_PASS` — MuJoCo execution
5. `INDEPENDENT_DYNAMICS_CROSSCHECK_PASS` — Project Chrono
6. `STRUCTURAL_ANALYSIS_PASS` — FreeCAD FEM/CalculiX when applicable
7. `CONTROLLER_IN_LOOP_PASS`
8. `HARDWARE_IN_LOOP_PASS`
9. `PHYSICAL_SUBASSEMBLY_PASS`
10. `PHYSICAL_SYSTEM_PASS`
11. `REPEATED_VALIDATION`

The current repository can deterministically produce levels 1–2 and the existing Blender pipeline produces geometry/collision evidence for level 3. Higher states require the corresponding tool/runtime and exact execution evidence.

## Reduced-order model

`simulation/reduced_order.py` models one rolling plane using:

- sphere translation constrained to shell rotation;
- body translational + rotational inertia;
- absolute pendulum angle;
- equal/opposite motor torque between pendulum and body;
- gravity;
- damping/rolling-drag screening;
- motor torque-speed saturation;
- required floor contact force and normal-force estimate.

The model assumes no-slip rolling but computes a friction margin. Negative margin means that assumption is self-inconsistent and the scenario must be escalated to the contact solver; the code does not hide the violation by silently clamping it.

This model is deliberately not the authority for yaw/steering, contact compliance, shell deformation, backlash, battery sag, thermal behavior or real FDM material behavior.

## Reproducible baseline

```bash
python mechanical/spherical_robot/calculations.py --json
python -m unittest discover -s mechanical/spherical_robot/tests -p 'test_*.py'
python mechanical/spherical_robot/simulation/run_sweep.py
```

The sweep varies the existing ballast masses, arm radii and configured friction assumptions. Its output is provisional while the repository still contains `PLACEHOLDER`/`ASSUMED` inputs.

## MuJoCo

Generate an MJCF input artifact directly from canonical dimensions:

```bash
python mechanical/spherical_robot/simulation/mujoco_model.py \
  --output /tmp/spherical_robot.xml
```

This validates XML generation and binds hashes, but **does not execute MuJoCo**. A future solver execution receipt must record the exact MuJoCo version, model hash, scenario matrix, solver settings and numeric results before `PRIMARY_MULTIBODY_PASS`.

The MuJoCo model contains:

- free spherical body/contact shell;
- internal steering-yaw joint;
- pendulum hinge and ballast;
- bounded motor actuators;
- floor contact/friction;
- IMU-like accelerometer/gyro plus joint sensors.

## Independent cross-check and FEA

Release-critical dynamics must be cross-checked with Project Chrono (or another independently implemented multibody method). Load-bearing geometry requiring more than analytical screening must use FreeCAD FEM/CalculiX or a justified equivalent, with loads bound to the dynamics evidence.

## Controller and HIL

The next software layer should expose a stable semantic interface:

- IMU acceleration/angular velocity;
- pendulum angle/speed;
- steering angle;
- requested pendulum torque/speed;
- requested steering actuation;
- health/saturation/watchdog state.

The real control algorithm should first run controller-in-loop against the simulated plant. After that, the ESP32-P4-M3 can run HIL against the same interface. HIL still does not prove real floor friction, printed fit, RF, battery, thermal or wear behavior.

## Physical calibration loop

After the first safe subassembly/rolling tests, feed measured values back into the model:

- actual total/component masses and COM;
- actual motor torque-speed-current behavior;
- backlash/deadband;
- floor/grip friction;
- rolling resistance;
- IMU bias/noise/latency;
- battery sag;
- real pendulum and steering limits.

Every calibration update invalidates dependent simulation evidence until rerun.

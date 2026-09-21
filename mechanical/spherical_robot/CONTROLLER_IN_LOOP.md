# Controller-in-loop

The spherical robot now has a production-intended, ESP-IDF-independent C
controller core under `components/spherical_control`.

The host test compiles that exact C source into a shared library and runs it
against the same MuJoCo plant used by the multibody evidence lane.

## Controller

The straight-line controller is a cascade:

`shell speed error -> desired pendulum angle -> pendulum torque`

Shell speed is estimated from the shell-frame IMU gyro using rolling kinematics:

`v = R * omega_y`

The pendulum encoder is relative to the rolling shell, so the controller first
forms the gravity-referenced pendulum state:

`absolute pendulum angle = unwrapped shell roll + encoder relative angle`

and the matching angular velocity from shell gyro + relative encoder speed.
The inner loop controls that absolute pendulum state and applies the configured
torque-speed motor limit.

Steering is deliberately a semantic output channel with zero command until the
steering actuator and steering-angle sensor are physically selected/measured.

## Evidence boundary

A green run is only:

`CONTROLLER_IN_LOOP_SCREENING_PASS`

It cannot become `CONTROLLER_IN_LOOP_PASS` yet because:

- the pure-C core is not yet wired into the ESP-IDF app loop;
- the pendulum encoder firmware driver is absent;
- the steering actuator/sensor firmware path is absent;
- motor torque-speed data is still placeholder;
- simulated IMU/encoder data are idealized.

The existing `app_control.c` + `app_stepper.c` remains a legacy dual-drive
stabilization demo. It is not treated as the spherical robot controller.

## Scenario matrix

The CI runs:

- 3 ballast masses;
- 3 arm radii;
- 3 floor-friction assumptions;
- both forward and reverse targets.

That is 54 closed-loop scenarios on one exact source revision.

Every scenario checks finite state, direction, minimum tracking response,
pendulum-angle limit, actuator saturation bounds, floor contact and absence of
unexpected internal contacts.

`physical_accepted` is always false.

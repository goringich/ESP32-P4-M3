# Stabilized Sphere TT80 — P0

## Goal

Build the first physical self-stabilizing spherical robot from hardware already proven on the bench:

- ESP32-P4-M3;
- MPU-9250;
- two TT/BO geared DC motors;
- two user-owned 80 mm wheels;
- existing dual H-bridge hardware for the first experiment;
- rechargeable battery;
- FDM-printed spherical shell.

This is deliberately **not** the existing pendulum/steering-ring robot in `mechanical/spherical_robot/`.
That design is preserved as a higher-performance research path. P0 is an internal-drive-unit (IDU)
prototype intended to reach physical closed-loop motion with the fewest new parts.

## Mechanical principle

The printed sphere is the external wheel. A compact two-motor drive unit is free inside the shell.

The IDU has:

1. two powered rubber wheels acting on the inner surface of the sphere;
2. its centre of mass deliberately below the sphere centre / principal drive axis;
3. ESP32-P4-M3 and MPU-9250 rigidly mounted to the IDU;
4. the battery as the lowest heavy component;
5. a low-friction upper guide / compliant preload mechanism to prevent loss of traction and chassis tumble.

Gravity provides passive restoring torque. The IMU measures IDU attitude and angular rate. Motor torque
actively damps pitch motion, restores the requested attitude and rolls the shell.

## P0 scope

P0 is intentionally one-dimensional first:

- self-centre / recover from a small pitch disturbance;
- controlled forward and reverse rolling;
- controlled stop without the IDU tumbling;
- low-speed differential steering only after straight-line stabilization works.

Do not optimize for autonomous navigation, camera, high speed or product enclosure before these gates pass.

## Reuse from the existing repository

Reusable now:

- ESP-IDF project and ESP32-P4-M3 support;
- MPU-9250 driver and telemetry;
- Wi-Fi/BLE/HTTP operator paths;
- known motor direction mapping;
- shell diameter family and segmented-print experience.

Do **not** reuse as the controller for this mechanism:

- pendulum-specific `components/spherical_control` from PR #10;
- the current pendulum + steering-ring dynamics contract;
- the legacy on/off stabilization behaviour in `app_stepper.c`.

The IDU needs PWM motor effort, not only direction switching.

## Control architecture

First physical controller:

```text
MPU-9250 accel + gyro
        |
        v
complementary attitude estimate
        |
        v
pitch target / rate damping
        |
        v
PID effort u_pitch
        |
        +---- steering delta u_yaw (P0-C)
        |
        v
left/right PWM
        |
        v
TT motors -> inner shell -> sphere rolls
```

Initial safe limits:

- control period: 5-10 ms target;
- PWM command cap: 25% for first closed-shell runs;
- pitch target: 0 deg for hold;
- locomotion target bias: start within +/- 5 deg;
- hard motor cut if abs(pitch) exceeds 35 deg;
- hard motor cut on stale/invalid IMU data;
- physical emergency stop available during all first runs.

Exact gains are not release constants; tune them on the real IDU.

## Hardware-driver strategy

For the fastest prototype, keep the existing L293D only if both enable channels are accessible.
Drive EN1,2 and EN3,4 with hardware PWM instead of tying them HIGH.

If the existing board does not expose usable PWM enables, move P0 to a DRV8833 or TB6612-class
dual H-bridge before closed-loop tuning. Do not emulate motor effort by slow on/off direction pulses.

## Mechanical release gates

Before a full print is called fit-ready:

- measure the actual 80 mm wheel width, hub depth and shaft fit;
- measure both TT motors including shaft position;
- measure battery envelope and mass;
- measure ESP32-P4-M3 connector keep-outs;
- verify wheel-to-shell contact in CAD across tolerance;
- verify IDU cannot jam against the shell at expected pitch angles;
- print motor/wheel contact coupons before the full IDU;
- test the assembled IDU in an open shell / cradle before closing the sphere.

## Prototype stages

### P0-A — drive module

Print only the central IDU frame, motor clamps and battery cradle.
Verify motor polarity, PWM, IMU orientation and centre-of-mass location.

### P0-B — open-shell stabilization

Place the IDU in one shell section / test cradle.
Tune attitude damping and verify recovery without closing the sphere.

### P0-C — closed sphere

Assemble the complete shell, start with a low PWM cap and verify:

- hold;
- forward;
- stop;
- reverse;
- repeated recovery.

### P0-D — steering

Add differential left/right command only after P0-C is repeatable.

## Product direction

Once P0 is physically repeatable, replace the oversized development electronics with a small controller
board and measured motor/driver/battery contract. The geometry and controller interface should remain
compatible so the same sphere can become a kit rather than a one-off coursework prototype.

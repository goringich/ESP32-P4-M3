# P0 control contract

## What is being stabilized

The rotating outer shell is not expected to keep an absolute orientation while the robot rolls.
P0 stabilizes the **internal drive unit attitude** relative to gravity and uses that controlled
internal attitude / motor reaction to command sphere motion.

If a future product requires a camera or top module to remain visually level while the shell rolls,
that is a separate gimbal / magnetic-head problem and is outside P0.

## State

Required every control tick:

- pitch angle of the IDU relative to gravity;
- pitch angular velocity;
- sensor timestamp / freshness;
- requested forward command;
- requested steering command.

Optional later:

- left/right wheel encoder velocity;
- shell velocity estimate;
- battery voltage;
- driver current / fault.

## First controller

Use a complementary filter for pitch:

```text
pitch = alpha * (pitch + gyro_y * dt)
      + (1 - alpha) * accel_pitch
```

Then:

```text
error = target_pitch - pitch
u_pitch = Kp * error - Kd * pitch_rate + Ki * integral(error)

left_pwm  = clamp(u_pitch - u_yaw)
right_pwm = clamp(u_pitch + u_yaw)
```

For P0-A/P0-B set `u_yaw = 0`.

Start without integral action. Add Ki only if a real steady bias remains after mechanical COM and
motor asymmetry are corrected.

## Locomotion

Do not map the phone's FORWARD button directly to 100% motor duty.

For the first physical controller, map a forward request to a small pitch bias, bounded by the
configured initial limit. The attitude loop then generates the motor effort needed to reach/hold it.

Later, when wheel/shell velocity is observable, use a cascade:

```text
speed error -> target pitch -> pitch PID -> motor PWM
```

## Safety states

Motor output must become zero when any of these is true:

- IMU sample invalid or too old;
- control loop timestamp discontinuity exceeds the allowed bound;
- abs(pitch) exceeds emergency cutoff;
- emergency stop asserted;
- driver fault asserted when supported.

On boot and after a fault, require an explicit re-arm before enabling closed-loop output.

## Firmware migration

The existing `app_stepper.c` proves motor direction and operator plumbing but is not the final P0
control layer. Replace its motor abstraction with signed PWM per side while preserving the existing
HTTP/BLE/UART command surface where practical.

The P0 controller must not depend on the pendulum-specific semantic inputs from PR #10.

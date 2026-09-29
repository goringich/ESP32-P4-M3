# Physical test plan — Stabilized Sphere TT80 P0

## Gate 1 — measurements

Record before final CAD:

- wheel diameter at the tire, width, hub depth and shaft engagement;
- left/right TT motor envelope and shaft position;
- battery dimensions + mass;
- ESP32-P4-M3 highest component and cable keep-outs;
- MPU-9250 board envelope and mounting geometry.

## Gate 2 — motor PWM on bench

With wheels off the ground:

- verify 0%, low, medium and capped-high PWM on each channel;
- verify forward/reverse sign independently;
- verify STOP disables both channels;
- verify emergency stop overrides every command;
- run long enough to check driver and motor temperature qualitatively before closing the sphere.

Do not tune stabilization with EN pins permanently tied HIGH.

## Gate 3 — IMU orientation

Rigidly mount the MPU-9250 to the IDU.

Verify:

- level reads approximately 0 deg pitch after calibration;
- known forward tilt produces the documented sign;
- known backward tilt produces the opposite sign;
- gyro sign matches the angle derivative;
- stale-data path cuts motor output.

## Gate 4 — open-shell / cradle

Use an open shell or printed cradle so the IDU cannot run away.

Sequence:

1. PWM cap 10%;
2. Kp only;
3. add Kd to suppress oscillation;
4. increase cap gradually up to 25% only if stable;
5. disturb the IDU by hand and verify it returns without sustained oscillation;
6. repeat with battery at minimum and maximum intended state of charge.

## Gate 5 — closed sphere

Use a clear test area with soft barriers.

Pass criteria for the first milestone:

- five consecutive start -> hold -> stop cycles;
- five forward -> stop cycles;
- five reverse -> stop cycles;
- no IDU-shell jam;
- no wire enters a wheel/contact path;
- no uncontrolled full-duty command;
- electronics and battery remain mechanically retained after repeated rolling.

## Gate 6 — steering

Only after straight-line closed-loop behaviour is repeatable:

- introduce a bounded differential PWM term;
- test left/right at very low speed;
- verify steering does not defeat pitch stabilization;
- add yaw-rate damping from the IMU if needed.

No product / kit claim is made until the same physical configuration passes repeated tests.

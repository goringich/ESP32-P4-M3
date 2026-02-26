# GY-9250 / MPU-9250 on JC-ESP32P4-M3 (hello_p4)

## Confirmed (software-verified)

The current working connection is confirmed by runtime logs:

- `SDA = GPIO1`
- `SCL = GPIO2`
- I2C address = `0x68` (so `AD0/SDO` is tied to `GND`)

Verification evidence (latest successful run):

- `logs/monitor/latest.log` contains `i2c_bus: scan: found 0x68`
- `logs/monitor/latest.log` contains `app: mpu: addr=0x68 WHO_AM_I=0x71 (MPU-9250)`

## Module wiring (logical)

For `GY-9250` in I2C mode:

- `VCC -> 3.3V`
- `GND -> GND`
- `SDA/SDI -> GPIO1`
- `SCL/SCLK -> GPIO2`
- `NCS -> 3.3V` (required for I2C mode)
- `AD0/SDO -> GND` (address `0x68`)
- `INT` not required
- `FSYNC` not required
- `EDA/ECL` not required for basic IMU access

## Your 2x13 header coordinates (as provided)

These are your user-side coordinates on the unlabeled `2x13` header (matrix style), not official silkscreen names.

Current interpreted setup:

- `SCL` is on the contact that maps to `GPIO2`
- `SDA` is on the contact that maps to `GPIO1`

Important:

- The software can confirm only the resulting GPIO mapping (`GPIO1/GPIO2`) and address (`0x68`).
- It cannot directly prove the physical `2x13` coordinate labels without a meter/schematic.

## How to verify quickly (project-local)

Run with log capture:

```bash
direnv exec . ./scripts/idf_monitor_log.sh -p /dev/ttyUSB0 -b 115200 flash monitor
```

Success indicators in `logs/monitor/latest.log`:

- `i2c_bus: scan: found 0x68`
- `mpu: addr=0x68 WHO_AM_I=0x..`
- `i2c_bus_diag:` lines appear only if normal detection failed (fallback pin sweep)

## Notes

- `MPU-6500` and `MPU-9250` both typically answer on `0x68/0x69`.
- `WHO_AM_I` helps distinguish variants:
  - `0x70` -> likely `MPU-6500`
  - `0x71` -> likely `MPU-9250`
  - `0x73` -> likely `MPU-9255/variant`
- If `NCS` is not tied high, the module may not respond over I2C.

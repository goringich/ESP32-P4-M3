#!/usr/bin/env python3
"""
Collect stabilization telemetry from ESP32-P4 and compute quality metrics.
Usage: python3 collect_stabilization_data.py [/dev/ttyUSB0] [duration_s]
"""
import sys, json, time, math, statistics
import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
DURATION = int(sys.argv[2]) if len(sys.argv) > 2 else 45

DEAD_ZONE_DEG = 1.0   # matches sdkconfig APP_CONTROL_DEAD_ZONE_DEG_X10=10

print(f"[collect] Открываю {PORT} @ 115200, длительность {DURATION}s")
ser = serial.Serial(PORT, 115200, timeout=0.5)
time.sleep(0.3)

# Activate stabilizer
ser.write(b"g\n")
time.sleep(0.1)
print("[collect] Отправлена команда 'g' — режим стабилизации включён")
print(f"[collect] Идёт запись {DURATION}s. НАКЛОНИ ПЛАТФОРМУ примерно через 10 секунд!")
print("=" * 60)

records = []
t0 = time.time()
msg_count = 0

while time.time() - t0 < DURATION:
    line = ser.readline()
    if not line:
        continue
    try:
        text = line.decode("utf-8", errors="replace").strip()
    except Exception:
        continue

    if text.startswith("@telemetry") and '"kind":"control"' in text:
        try:
            payload = json.loads(text[len("@telemetry "):])
        except Exception:
            continue
        ts = time.time() - t0
        payload["_ts"] = round(ts, 3)
        records.append(payload)
        msg_count += 1
        if msg_count % 50 == 0:
            print(f"  t={ts:.1f}s  angle={payload.get('angle_deg', '?'):.2f}°  "
                  f"active={payload.get('active')}", flush=True)

ser.write(b"s\n")
ser.close()

print("=" * 60)
print(f"[collect] Записано {len(records)} сообщений за {DURATION}s")

if len(records) < 10:
    print("[ERROR] Слишком мало данных, проверь подключение платы")
    sys.exit(1)

# ── Metrics ──────────────────────────────────────────────────────────────────

# Telemetry frequency
total_time = records[-1]["_ts"] - records[0]["_ts"]
freq_hz = (len(records) - 1) / total_time if total_time > 0 else 0

# Baseline: first 8 seconds (platform at rest before disturbance)
baseline = [r for r in records if r["_ts"] < 8.0]
if baseline:
    baseline_angles = [r["angle_deg"] for r in baseline]
    angle_target = statistics.mean(baseline_angles)
    steady_rms = math.sqrt(statistics.mean((a - angle_target)**2 for a in baseline_angles))
else:
    angle_target = records[0]["angle_deg"]
    steady_rms = 0.0

# Detect disturbance: first moment when |angle - target| > 3°
disturbance_t = None
for r in records:
    if abs(r["angle_deg"] - angle_target) > 3.0:
        disturbance_t = r["_ts"]
        break

max_deviation = 0.0
settling_time = None
overshoot_pct = 0.0

if disturbance_t is not None:
    post_dist = [r for r in records if r["_ts"] >= disturbance_t]

    # Max deviation
    max_deviation = max(abs(r["angle_deg"] - angle_target) for r in post_dist)

    # Settling time: first time after disturbance when |error| < DEAD_ZONE for ≥1s
    SETTLE_WINDOW = 1.0
    settled_start = None
    settled_t = None
    for r in post_dist:
        err = abs(r["angle_deg"] - angle_target)
        if err < DEAD_ZONE_DEG:
            if settled_start is None:
                settled_start = r["_ts"]
            if r["_ts"] - settled_start >= SETTLE_WINDOW:
                settled_t = settled_start
                break
        else:
            settled_start = None
    if settled_t:
        settling_time = round(settled_t - disturbance_t, 2)

    # Overshoot: max angle on the "recovery side" past the target
    recovery = [r for r in post_dist if r["_ts"] > disturbance_t + 0.5]
    if recovery and max_deviation > 0:
        max_recovery = max(abs(r["angle_deg"] - angle_target) for r in recovery
                          if r["angle_deg"] > angle_target + DEAD_ZONE_DEG
                          or r["angle_deg"] < angle_target - DEAD_ZONE_DEG)
        if max_recovery < max_deviation:
            overshoot_pct = round(max_recovery / max_deviation * 100, 1)

# Stability after settling (last 5 seconds)
last_5s = [r for r in records if r["_ts"] > records[-1]["_ts"] - 5.0]
if last_5s:
    last_angles = [r["angle_deg"] for r in last_5s]
    final_rms = math.sqrt(statistics.mean((a - angle_target)**2 for a in last_angles))
else:
    final_rms = steady_rms

# Repeated disturbances
disturbance_count = 0
in_dist = False
for r in records:
    over = abs(r["angle_deg"] - angle_target) > 3.0
    if over and not in_dist:
        disturbance_count += 1
        in_dist = True
    elif not over:
        in_dist = False

# ── Output ────────────────────────────────────────────────────────────────────
result = {
    "telemetry_freq_hz": round(freq_hz, 1),
    "angle_target_deg": round(angle_target, 2),
    "steady_state_rms_deg": round(steady_rms, 3),
    "final_rms_deg": round(final_rms, 3),
    "max_deviation_deg": round(max_deviation, 1),
    "settling_time_s": settling_time,
    "overshoot_pct": overshoot_pct,
    "disturbance_count": disturbance_count,
    "total_records": len(records),
    "duration_s": round(total_time, 1),
}

print("\n=== РЕЗУЛЬТАТЫ ===")
print(json.dumps(result, ensure_ascii=False, indent=2))

# Save raw data too
out_path = "/tmp/stab_raw.jsonl"
with open(out_path, "w") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")
print(f"\n[collect] Сырые данные сохранены: {out_path}")
print(f"[collect] Результаты: /tmp/stab_metrics.json")
with open("/tmp/stab_metrics.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

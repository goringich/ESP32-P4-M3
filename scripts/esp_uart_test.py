#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

import serial


def read_for(ser: serial.Serial, seconds: float, sink: dict) -> None:
    end = time.time() + seconds
    while time.time() < end:
      line = ser.readline()
      if not line:
          continue

      text = line.decode("utf-8", errors="ignore").strip()
      if not text:
          continue

      sink["raw_lines"].append(text)

      if (
          "app_wifi:" in text
          or "wifi station" in text
          or "Station mode:" in text
          or "AP ready" in text
          or "STA ready" in text
          or "connect retry" in text
          or "STA profile" in text
      ):
          sink["wifi_lines"].append(text)

      if not text.startswith("@telemetry "):
          continue

      try:
          payload = json.loads(text.split(" ", 1)[1])
      except Exception:
          continue

      payload["_ts"] = time.time()
      sink["records"].append(payload)

      kind = payload.get("kind")
      if kind == "stepper":
          sink["stepper_events"].append(payload)
      elif kind == "control":
          sink["control_events"].append(payload)


def summarize(sink: dict) -> dict:
    active_control = [r for r in sink["control_events"] if r.get("active")]
    summary = {
        "wifi_lines": sink["wifi_lines"][-60:],
        "mode_changes": [
            {
                "reason": e.get("reason"),
                "mode": e.get("mode"),
                "left_direction": e.get("left_direction"),
                "right_direction": e.get("right_direction"),
                "left_state": e.get("left_state"),
                "right_state": e.get("right_state"),
                "steps_per_second": e.get("steps_per_second"),
                "last_command": e.get("last_command"),
            }
            for e in sink["stepper_events"]
            if e.get("reason") == "mode_change"
        ],
        "active_control_samples": len(active_control),
    }

    if active_control:
        errors = [abs(r.get("error_deg", 0.0)) for r in active_control if "error_deg" in r]
        outputs = [abs(r.get("output", 0.0)) for r in active_control if "output" in r]
        angles = [r.get("angle_deg", 0.0) for r in active_control if "angle_deg" in r]
        summary["control_metrics"] = {
            "target_deg": active_control[0].get("target_deg", 0.0),
            "samples": len(active_control),
            "mean_abs_error_deg": sum(errors) / len(errors) if errors else None,
            "max_abs_error_deg": max(errors) if errors else None,
            "mean_abs_output": sum(outputs) / len(outputs) if outputs else None,
            "angle_span_deg": (max(angles) - min(angles)) if angles else None,
        }
    else:
        summary["control_metrics"] = None

    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--boot-seconds", type=float, default=18.0)
    parser.add_argument("--stabilize-seconds", type=float, default=3.0)
    parser.add_argument("--out-json", default="/tmp/esp_uart_test_summary.json")
    parser.add_argument("--out-log", default="/tmp/esp_uart_raw.log")
    parser.add_argument("--out-control-jsonl", default="/tmp/stab_raw.jsonl")
    args = parser.parse_args()

    sink = {
        "records": [],
        "stepper_events": [],
        "control_events": [],
        "wifi_lines": [],
        "raw_lines": [],
    }

    ser = serial.Serial(args.port, args.baud, timeout=0.2)
    try:
        ser.reset_input_buffer()

        print("READ_BOOT")
        read_for(ser, args.boot_seconds, sink)

        sequence = [
            ("f", 0.8),
            ("s", 0.6),
            ("r", 0.8),
            ("s", 0.6),
            ("2", 0.8),
            ("s", 0.6),
            ("1", 0.8),
            ("s", 0.6),
            ("g", args.stabilize_seconds),
            ("s", 0.6),
        ]

        for cmd, delay in sequence:
            ser.write(cmd.encode("ascii"))
            ser.flush()
            read_for(ser, delay, sink)
    finally:
        ser.close()

    control_lines = [r for r in sink["control_events"] if r.get("active")]
    Path(args.out_control_jsonl).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in control_lines)
        + ("\n" if control_lines else ""),
        encoding="utf-8",
    )
    Path(args.out_log).write_text("\n".join(sink["raw_lines"]) + "\n", encoding="utf-8")

    summary = summarize(sink)
    Path(args.out_json).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Печать P0.1

Принтер: Anycubic Kobra 2 Pro, рабочее поле 220×220×250 мм. Единицы STL — миллиметры. Машиночитаемая таблица по каждому файлу: `exports/print_manifest.json`; ниже — компактная инструкция для всех экспортов.

Общие правила: сопло 0.4 мм, слой 0.20 мм; minimum local wall 1.2 мм; shell 2.8 мм; structural wall ≥2.4 мм. Сначала напечатать `M3_TEST_COUPON`, `BEARING_FIT_COUPON`, `HEAT_INSERT_TEMPLATE` и `SPHERICAL_JOINT_TEST_FRAGMENT`. Не масштабировать посадочные детали в slicer.

| STL-файл(ы) | Материал | Ориентация | Стенки | Infill | Supports | Brim | Кол-во |
|---|---|---|---:|---:|---|---|---:|
| `SHELL_SEGMENT_01_POS_X` … `06_NEG_Z` | PETG; PLA для первого fit | rim на стол, внешняя поверхность вверх | 5 | 18% gyroid | нет | да, 5 мм | по 1 |
| `SERVICE_HATCH` | PETG/PLA | внутренней плоскостью на стол | 5 | 30% | нет | нет | 1 |
| `EQUATOR_EDGE_CLIP_01` | PETG | плоским боком | 6 | 60% | нет | нет | 12 |
| `SEGMENT_ALIGNMENT_KEY` | PETG | наибольшей плоскостью | 5 | 80% | нет | нет | 12 |
| `TPU_GRIP_01_POS_X` | TPU 95A | внешней плоскостью на стол | 3 | 100% | нет | нет | 24 |
| `FIXED_FRAME_RING_QUADRANT_01` | PETG | плоско | 6 | 45% | нет | нет | 4 |
| `FIXED_FRAME_TOP`, `FIXED_FRAME_BOTTOM` | PETG | плоско | 6 | 45% | нет | нет | по 1 |
| `FRAME_STRUT_TOP_01` | PETG | горизонтально, ось параллельно столу | 6 | 45% | нет | да | 8 |
| `STEERING_RING` | PETG | плоско | 7 | 45% | нет | да, 5 мм | 1 |
| `SHAFT_SUPPORT_LEFT`, `SHAFT_SUPPORT_RIGHT` | PETG | широкой боковой плоскостью | 7 | 55% | нет | нет | по 1 |
| `MOTOR_MOUNT` | PETG | основанием на стол | 6 | 45% | нет | нет | 1 |
| `MOTOR_CLAMP` | PETG | широкой плоскостью | 6 | 50% | нет | нет | 1 |
| `STEERING_ACTUATOR_MOUNT` | PETG | основанием на стол | 6 | 45% | нет | нет | 1 |
| `ENCODER_GUARD` | PETG | открытой стороной вверх | 5 | 35% | нет | нет | 1 |
| `PENDULUM_ENCODER_GUARD` | PETG | широкой плоскостью | 5 | 40% | нет | нет | 1 |
| `PENDULUM_ARM` | PETG | широкой боковой плоскостью | 8 | 70% | нет | да | 1 |
| `BALLAST_HOLDER` | PETG | закрытым торцом на стол | 7 | 50% | нет | нет | 1 |
| `BALLAST_LID` | PETG | плоско | 5 | 60% | нет | нет | 1 |
| `PCB_TRAY` | PETG | плоско | 5 | 35% | нет | нет | 1 |
| `BATTERY_TRAY` | PETG | основанием на стол | 6 | 40% | нет | нет | 1 |
| `IMU_MOUNT` | PETG | широкой плоскостью | 5 | 50% | нет | нет | 1 |
| `DRIVER_TRAY` | PETG | широкой плоскостью | 5 | 35% | нет | нет | 1 |
| `SWITCH_HOLDER`, `CHARGE_PORT_HOLDER` | PETG | плоско | 5 | 45% | нет | нет | по 1 |
| `CABLE_CLIP_01` | PETG | плоско | 4 | 60% | нет | нет | 8 |
| `BALL_STAND` | PETG/PLA | плоско | 5 | 25% | нет | да | 1 |
| `BALANCE_STAND_SIDE` | PETG/PLA | широкой плоскостью | 6 | 25% | нет | да | 2 |
| `PENDULUM_TEST_STAND_BASE` | PETG/PLA | плоско | 5 | 25% | нет | нет | 1 |
| `PENDULUM_TEST_STAND_UPRIGHT` | PETG/PLA | широкой плоскостью | 6 | 40% | нет | да | 2 |
| `SEGMENT_ALIGNMENT_TEMPLATE` | PETG/PLA | плоско | 5 | 35% | нет | нет | 1 |
| `M3_TEST_COUPON`, `BEARING_FIT_COUPON`, `HEAT_INSERT_TEMPLATE` | материал будущей детали | плоско | 5–6 | 80% | нет | нет | по 1 |
| `SPHERICAL_JOINT_TEST_FRAGMENT` | материал оболочки | торцом дуги на стол | 5 | 25% | нет | да при необходимости | 1 |

Крупнейшая shell panel после re-import: 183.85×183.85×56.56 мм. С brim 5 мм и краевым запасом 8 мм расчётный footprint ≈209.85 мм. Steering ring Ø190 мм с теми же ограничениями занимает 216 мм; размещать строго по центру стола.

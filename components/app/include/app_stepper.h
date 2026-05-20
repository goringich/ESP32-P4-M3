#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

typedef struct {
  const char *mode;
  const char *sweep_state;
  const char *left_motor_state;
  const char *right_motor_state;
  uint32_t step_delay_ms;
  float steps_per_second;
  uint32_t phase_index;
  uint32_t total_steps;
  uint32_t sweep_steps;
  bool coils_enabled;
  bool uart_ready;
  char last_command[3];
  int8_t left_direction;
  int8_t right_direction;
  uint8_t in1_level;
  uint8_t in2_level;
  uint8_t in3_level;
  uint8_t in4_level;
  int in1_gpio;
  int in2_gpio;
  int in3_gpio;
  int in4_gpio;
  int led_gpio;
} app_stepper_snapshot_t;

esp_err_t app_stepper_init(void);
void app_stepper_tick(void);
esp_err_t app_stepper_command_char(char cmd);
void app_stepper_get_snapshot(app_stepper_snapshot_t *snapshot);

/* Set velocity for stabilization mode (steps/s; positive=forward, negative=reverse, 0=stop). */
void app_stepper_set_stabilize_velocity(float steps_per_second);

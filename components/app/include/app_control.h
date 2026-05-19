#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef struct {
  float kp;
  float ki;
  float kd;
  float alpha;
  float dead_zone_deg;
  float max_output_sps;
  float dt_s;
} app_control_params_t;

void  app_control_init(void);
void  app_control_get_params(app_control_params_t *out);
void  app_control_set_target_deg(float deg);
float app_control_get_angle_deg(void);
bool  app_control_is_active(void);
void  app_control_set_active(bool active);

/* Returns velocity in steps/s (positive = forward, negative = reverse). */
float app_control_tick(float ax_g, float ay_g, float az_g,
                       float gx_dps, float gy_dps, float gz_dps,
                       uint32_t now_ms);

#include "app_control.h"

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "sdkconfig.h"

#define RAD_TO_DEG 57.29578f

static const app_control_params_t s_params = {
  .kp            = CONFIG_APP_CONTROL_KP_X100  / 100.0f,
  .ki            = CONFIG_APP_CONTROL_KI_X100  / 100.0f,
  .kd            = CONFIG_APP_CONTROL_KD_X100  / 100.0f,
  .alpha         = CONFIG_APP_CONTROL_ALPHA_X100 / 100.0f,
  .dead_zone_deg = CONFIG_APP_CONTROL_DEAD_ZONE_DEG_X10 / 10.0f,
  .max_output_sps = (float)CONFIG_APP_CONTROL_MAX_OUTPUT_SPS,
  .dt_s          = CONFIG_APP_CONTROL_DT_MS / 1000.0f,
};

static float    s_angle_deg  = 0.0f;
static float    s_target_deg = 0.0f;
static float    s_integral   = 0.0f;
static float    s_prev_error = 0.0f;
static bool     s_active     = false;
static bool     s_first_tick = true;
static uint32_t s_last_ms    = 0;

void app_control_init(void) {
  s_angle_deg  = 0.0f;
  s_target_deg = 0.0f;
  s_integral   = 0.0f;
  s_prev_error = 0.0f;
  s_active     = false;
  s_first_tick = true;
  s_last_ms    = 0;

  printf("@telemetry {\"kind\":\"control_params\","
         "\"kp\":%.2f,\"ki\":%.2f,\"kd\":%.2f,"
         "\"alpha\":%.2f,\"dead_zone_deg\":%.1f,"
         "\"max_output_sps\":%.0f,\"dt_ms\":%d}\n",
         (double)s_params.kp,
         (double)s_params.ki,
         (double)s_params.kd,
         (double)s_params.alpha,
         (double)s_params.dead_zone_deg,
         (double)s_params.max_output_sps,
         CONFIG_APP_CONTROL_DT_MS);
}

void app_control_get_params(app_control_params_t *out) {
  if (out) {
    *out = s_params;
  }
}

void app_control_set_target_deg(float deg) {
  s_target_deg = deg;
  s_integral   = 0.0f;
  s_prev_error = 0.0f;
}

float app_control_get_angle_deg(void) {
  return s_angle_deg;
}

bool app_control_is_active(void) {
  return s_active;
}

void app_control_set_active(bool active) {
  if (active && !s_active) {
    s_target_deg = s_angle_deg;
    s_integral   = 0.0f;
    s_prev_error = 0.0f;
  }
  s_active = active;
}

float app_control_tick(float ax_g, float ay_g, float az_g,
                       float gx_dps, float gy_dps, float gz_dps,
                       uint32_t now_ms) {
  (void)ay_g;
  (void)gz_dps;

  /* Compute actual dt from real wall time, clamped to [1ms, 200ms]. */
  float dt = s_params.dt_s;
  if (!s_first_tick && s_last_ms > 0) {
    const uint32_t elapsed = now_ms - s_last_ms;
    if (elapsed >= 1U && elapsed <= 200U) {
      dt = (float)elapsed / 1000.0f;
    }
  }
  s_last_ms = now_ms;

  /* Accel-based roll angle around Y-axis (tilt in X-Z plane). */
  const float accel_angle = atan2f(ax_g, az_g) * RAD_TO_DEG;

  /* Complementary filter. */
  if (s_first_tick) {
    s_angle_deg  = accel_angle;
    s_first_tick = false;
  } else {
    s_angle_deg = s_params.alpha * (s_angle_deg + gy_dps * dt)
                + (1.0f - s_params.alpha) * accel_angle;
  }

  if (!s_active) {
    printf("@telemetry {\"kind\":\"control\","
           "\"active\":false,\"angle_deg\":%.2f,\"target_deg\":%.2f}\n",
           (double)s_angle_deg, (double)s_target_deg);
    return 0.0f;
  }

  /* PID controller. */
  const float error      = s_target_deg - s_angle_deg;
  float       p_term     = 0.0f;
  float       i_term     = 0.0f;
  float       d_term     = 0.0f;
  float       output     = 0.0f;

  if (fabsf(error) > s_params.dead_zone_deg) {
    s_integral        += error * dt;
    const float deriv  = (error - s_prev_error) / dt;
    p_term             = s_params.kp * error;
    i_term             = s_params.ki * s_integral;
    d_term             = s_params.kd * deriv;
    output             = p_term + i_term + d_term;

    if (output >  s_params.max_output_sps) { output =  s_params.max_output_sps; }
    if (output < -s_params.max_output_sps) { output = -s_params.max_output_sps; }
  } else {
    s_integral = 0.0f;
  }
  s_prev_error = error;

  printf("@telemetry {\"kind\":\"control\","
         "\"active\":true,\"angle_deg\":%.2f,\"target_deg\":%.2f,\"error_deg\":%.2f,"
         "\"p\":%.3f,\"i\":%.3f,\"d\":%.3f,\"output\":%.2f,\"dt_ms\":%.1f}\n",
         (double)s_angle_deg, (double)s_target_deg, (double)error,
         (double)p_term, (double)i_term, (double)d_term,
         (double)output, (double)(dt * 1000.0f));

  return output;
}

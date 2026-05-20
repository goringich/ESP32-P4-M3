#include "app_control.h"

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "sdkconfig.h"

#define RAD_TO_DEG 57.29578f
#define APP_CONTROL_ACCEL_NORM_MIN 0.80f
#define APP_CONTROL_ACCEL_NORM_MAX 1.20f
#define APP_CONTROL_D_FILTER_ALPHA 0.72f
#define APP_CONTROL_OUTPUT_SMOOTH_ALPHA 0.65f

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
static float    s_prev_output = 0.0f;
static float    s_d_filtered  = 0.0f;
static bool     s_active     = false;
static bool     s_first_tick = true;
static uint32_t s_last_ms    = 0;

static float app_control_clampf(float value, float min_value, float max_value) {
  if (value < min_value) {
    return min_value;
  }
  if (value > max_value) {
    return max_value;
  }
  return value;
}

static float app_control_unwrap_deg(float reference_deg, float measured_deg) {
  while ((measured_deg - reference_deg) > 180.0f) {
    measured_deg -= 360.0f;
  }
  while ((measured_deg - reference_deg) < -180.0f) {
    measured_deg += 360.0f;
  }
  return measured_deg;
}

void app_control_init(void) {
  s_angle_deg  = 0.0f;
  s_target_deg = 0.0f;
  s_integral   = 0.0f;
  s_prev_error = 0.0f;
  s_prev_output = 0.0f;
  s_d_filtered  = 0.0f;
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
  s_prev_output = 0.0f;
  s_d_filtered  = 0.0f;
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
    s_prev_output = 0.0f;
    s_d_filtered  = 0.0f;
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
  const float accel_norm = sqrtf((ax_g * ax_g) + (ay_g * ay_g) + (az_g * az_g));
  const bool accel_reliable =
    accel_norm >= APP_CONTROL_ACCEL_NORM_MIN && accel_norm <= APP_CONTROL_ACCEL_NORM_MAX;
  const float accel_angle_raw = atan2f(ax_g, az_g) * RAD_TO_DEG;
  const float accel_angle = s_first_tick
    ? accel_angle_raw
    : app_control_unwrap_deg(s_angle_deg, accel_angle_raw);

  /* Complementary filter. */
  if (s_first_tick) {
    s_angle_deg  = accel_angle;
    s_first_tick = false;
  } else {
    const float predicted_angle = s_angle_deg + gy_dps * dt;
    s_angle_deg = accel_reliable
      ? (s_params.alpha * predicted_angle) + ((1.0f - s_params.alpha) * accel_angle)
      : predicted_angle;
  }

  if (!s_active) {
    printf("@telemetry {\"kind\":\"control\","
           "\"active\":false,\"angle_deg\":%.2f,\"target_deg\":%.2f,\"accel_norm\":%.3f,"
           "\"accel_reliable\":%s}\n",
           (double)s_angle_deg, (double)s_target_deg, (double)accel_norm,
           accel_reliable ? "true" : "false");
    return 0.0f;
  }

  /* PID controller. */
  const float error      = s_target_deg - s_angle_deg;
  float       p_term     = 0.0f;
  float       i_term     = 0.0f;
  float       d_term     = 0.0f;
  float       output_raw = 0.0f;
  float       output     = 0.0f;

  if (fabsf(error) > s_params.dead_zone_deg) {
    if (s_params.ki > 0.0f) {
      const float integral_limit = s_params.max_output_sps / s_params.ki;
      s_integral = app_control_clampf(
        s_integral + (error * dt),
        -integral_limit,
        integral_limit
      );
    }

    const float deriv  = (error - s_prev_error) / dt;
    s_d_filtered       = (APP_CONTROL_D_FILTER_ALPHA * s_d_filtered)
                       + ((1.0f - APP_CONTROL_D_FILTER_ALPHA) * deriv);
    p_term             = s_params.kp * error;
    i_term             = s_params.ki * s_integral;
    d_term             = s_params.kd * s_d_filtered;
    output_raw         = p_term + i_term + d_term;
    output_raw         = app_control_clampf(
      output_raw,
      -s_params.max_output_sps,
      s_params.max_output_sps
    );
    output             = (APP_CONTROL_OUTPUT_SMOOTH_ALPHA * s_prev_output)
                       + ((1.0f - APP_CONTROL_OUTPUT_SMOOTH_ALPHA) * output_raw);
  } else {
    s_integral = 0.0f;
    s_d_filtered = 0.0f;
    output = s_prev_output * 0.4f;
  }
  s_prev_error = error;
  s_prev_output = output;

  printf("@telemetry {\"kind\":\"control\","
         "\"active\":true,\"angle_deg\":%.2f,\"target_deg\":%.2f,\"error_deg\":%.2f,"
         "\"p\":%.3f,\"i\":%.3f,\"d\":%.3f,\"output\":%.2f,\"output_raw\":%.2f,"
         "\"dt_ms\":%.1f,\"accel_norm\":%.3f,\"accel_reliable\":%s}\n",
         (double)s_angle_deg, (double)s_target_deg, (double)error,
         (double)p_term, (double)i_term, (double)d_term,
         (double)output, (double)output_raw, (double)(dt * 1000.0f),
         (double)accel_norm, accel_reliable ? "true" : "false");

  return output;
}

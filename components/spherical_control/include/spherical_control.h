#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  float sphere_radius_m;
  float speed_to_tilt_gain_rad_per_m_s;
  float maximum_tilt_rad;
  float pendulum_kp_nm_per_rad;
  float pendulum_kd_nms_per_rad;
  float motor_torque_nm;
  float motor_no_load_rad_s;
} spherical_control_params_t;

typedef struct {
  float shell_gyro_y_rad_s;
  float pendulum_angle_rad;
  float pendulum_speed_rad_s;
} spherical_control_sensors_t;

typedef struct {
  float target_shell_speed_m_s;
  float target_steering_angle_rad;
} spherical_control_target_t;

typedef struct {
  float estimated_shell_speed_m_s;
  float speed_error_m_s;
  float desired_pendulum_angle_rad;
  float available_motor_torque_nm;
  float pendulum_torque_nm;
  float pendulum_command_normalized;
  float steering_command_normalized;
  bool torque_saturated;
  bool valid;
} spherical_control_output_t;

bool spherical_control_validate_params(const spherical_control_params_t *params);

void spherical_control_step(
  const spherical_control_params_t *params,
  const spherical_control_sensors_t *sensors,
  const spherical_control_target_t *target,
  spherical_control_output_t *output
);

#ifdef __cplusplus
}
#endif

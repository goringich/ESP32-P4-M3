#include "spherical_control.h"

#include <math.h>
#include <stddef.h>

static float spherical_control_clampf(float value, float minimum, float maximum) {
  if (value < minimum) {
    return minimum;
  }
  if (value > maximum) {
    return maximum;
  }
  return value;
}

bool spherical_control_validate_params(const spherical_control_params_t *params) {
  if (params == NULL) {
    return false;
  }
  return isfinite(params->sphere_radius_m)
    && isfinite(params->speed_to_tilt_gain_rad_per_m_s)
    && isfinite(params->maximum_tilt_rad)
    && isfinite(params->pendulum_kp_nm_per_rad)
    && isfinite(params->pendulum_kd_nms_per_rad)
    && isfinite(params->motor_torque_nm)
    && isfinite(params->motor_no_load_rad_s)
    && params->sphere_radius_m > 0.0f
    && params->speed_to_tilt_gain_rad_per_m_s > 0.0f
    && params->maximum_tilt_rad > 0.0f
    && params->pendulum_kp_nm_per_rad > 0.0f
    && params->pendulum_kd_nms_per_rad >= 0.0f
    && params->motor_torque_nm > 0.0f
    && params->motor_no_load_rad_s > 0.0f;
}

void spherical_control_step(
  const spherical_control_params_t *params,
  const spherical_control_sensors_t *sensors,
  const spherical_control_target_t *target,
  spherical_control_output_t *output
) {
  if (output == NULL) {
    return;
  }

  *output = (spherical_control_output_t){0};
  if (!spherical_control_validate_params(params)
      || sensors == NULL
      || target == NULL
      || !isfinite(sensors->shell_roll_angle_rad)
      || !isfinite(sensors->shell_gyro_y_rad_s)
      || !isfinite(sensors->pendulum_relative_angle_rad)
      || !isfinite(sensors->pendulum_relative_speed_rad_s)
      || !isfinite(target->target_shell_speed_m_s)
      || !isfinite(target->target_steering_angle_rad)) {
    return;
  }

  const float estimated_speed =
    params->sphere_radius_m * sensors->shell_gyro_y_rad_s;
  const float speed_error =
    target->target_shell_speed_m_s - estimated_speed;
  const float desired_pendulum = spherical_control_clampf(
    -params->speed_to_tilt_gain_rad_per_m_s * speed_error,
    -params->maximum_tilt_rad,
    params->maximum_tilt_rad
  );

  const float relative_speed =
    fabsf(sensors->pendulum_relative_speed_rad_s);
  const float absolute_pendulum_angle =
    sensors->shell_roll_angle_rad
    + sensors->pendulum_relative_angle_rad;
  const float absolute_pendulum_speed =
    sensors->shell_gyro_y_rad_s
    + sensors->pendulum_relative_speed_rad_s;
  const float speed_fraction = spherical_control_clampf(
    relative_speed / params->motor_no_load_rad_s,
    0.0f,
    1.0f
  );
  const float available_torque =
    params->motor_torque_nm * (1.0f - speed_fraction);

  const float raw_torque =
    params->pendulum_kp_nm_per_rad
      * (desired_pendulum - absolute_pendulum_angle)
    - params->pendulum_kd_nms_per_rad
      * absolute_pendulum_speed;
  const float torque = spherical_control_clampf(
    raw_torque,
    -available_torque,
    available_torque
  );

  output->estimated_shell_speed_m_s = estimated_speed;
  output->speed_error_m_s = speed_error;
  output->desired_pendulum_angle_rad = desired_pendulum;
  output->absolute_pendulum_angle_rad = absolute_pendulum_angle;
  output->absolute_pendulum_speed_rad_s = absolute_pendulum_speed;
  output->available_motor_torque_nm = available_torque;
  output->pendulum_torque_nm = torque;
  output->pendulum_command_normalized =
    params->motor_torque_nm > 0.0f
      ? torque / params->motor_torque_nm
      : 0.0f;

  /*
   * Steering remains an explicit semantic channel, but this controller does
   * not invent a steering law before the steering actuator and angle sensor
   * are measured and firmware-bound.
   */
  output->steering_command_normalized = 0.0f;
  output->torque_saturated =
    fabsf(raw_torque) > (available_torque + 1.0e-6f);
  output->valid = true;
}

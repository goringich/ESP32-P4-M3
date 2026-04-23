# Function index

Entry points:

- [[04-functions/app_main]]
- [[04-functions/app_init]]
- [[04-functions/app_tick]]
- [[04-functions/app_tick_delay_ms]]

App helpers:

- [[04-functions/app_log_color_block]]
- [[04-functions/app_mpu_whoami_check]]
- [[04-functions/app_emit_system_telemetry]]

Wi-Fi:

- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_wifi_get_status]]
- [[04-functions/app_wifi_event_handler_common]]
- [[04-functions/app_wifi_event_handler]]
- [[04-functions/app_wifi_log_scan_results]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_wifi_nvs_init_once]]
- [[04-functions/app_wifi_refresh_status_locked]]
- [[04-functions/app_wifi_auth_to_str]]
- [[04-functions/app_wifi_log_block]]

HTTP/WebSocket:

- [[04-functions/app_net_start]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_extract_command]]
- [[04-functions/app_net_command_handler]]
- [[04-functions/app_net_ws_handler]]
- [[04-functions/app_net_queue_ws_send]]
- [[04-functions/app_net_ws_send_work]]
- [[04-functions/app_net_telemetry_handler]]
- [[04-functions/app_net_wifi_handler]]
- [[04-functions/app_net_options_handler]]
- [[04-functions/app_net_set_cors]]

Stepper:

- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[04-functions/app_stepper_command_char]]
- [[04-functions/app_stepper_get_snapshot]]
- [[04-functions/app_stepper_gpio_init]]
- [[04-functions/app_stepper_uart_init]]
- [[04-functions/app_stepper_handle_uart]]
- [[04-functions/app_stepper_apply_phase]]
- [[04-functions/app_stepper_release]]
- [[04-functions/app_stepper_step_forward_once]]
- [[04-functions/app_stepper_step_reverse_once]]
- [[04-functions/app_stepper_set_mode]]
- [[04-functions/app_stepper_apply_named_phase]]
- [[04-functions/app_stepper_delay_adjust_delta_ms]]
- [[04-functions/app_stepper_emit_telemetry]]
- [[04-functions/app_stepper_log_block]]
- [[04-functions/app_stepper_mode_to_str]]
- [[04-functions/app_stepper_steps_per_second]]
- [[04-functions/app_stepper_sweep_state_to_str]]
- [[04-functions/app_stepper_cmd_to_str]]
- [[04-functions/app_stepper_log_timing]]
- [[04-functions/app_stepper_print_help]]
- [[04-functions/app_stepper_print_status]]
- [[04-functions/app_stepper_led_init]]
- [[04-functions/app_stepper_led_set]]
- [[04-functions/app_stepper_led_toggle]]

MPU:

- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_mpu_pretty_log_line]]
- [[04-functions/app_mpu_i16be]]
- [[04-functions/app_mpu_accel_lsb_per_g]]
- [[04-functions/app_mpu_gyro_lsb_per_dps]]
- [[04-functions/app_mpu_emit_telemetry_ready]]
- [[04-functions/app_mpu_emit_telemetry_error]]
- [[04-functions/mpu9250_probe_addr]]
- [[04-functions/mpu9250_read_whoami]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/mpu9250_whoami_name]]

I2C:

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_deinit]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/i2c_bus_probe_addr]]
- [[04-functions/i2c_bus_read]]
- [[04-functions/i2c_bus_write]]
- [[04-functions/i2c_bus_open_device]]
- [[04-functions/i2c_bus_read_lines]]
- [[04-functions/i2c_bus_log_lines]]
- [[04-functions/i2c_bus_log_scan_table]]
- [[04-functions/i2c_bus_selfcheck_gpio]]
- [[04-functions/i2c_bus_diag_sweep_mpu_pairs]]
- [[04-functions/i2c_bus_diag_probe_pair]]


#include "app_net.h"

#include <stdbool.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "esp_http_server.h"
#include "esp_log.h"
#include "sdkconfig.h"

#include "app.h"
#include "app_ble.h"
#include "app_mpu_pretty.h"
#include "app_wifi.h"
#include "app_stepper.h"

static const char *TAG = "app_net";

#define APP_NET_WS_PUSH_PERIOD_MS 1000U
#define APP_NET_JSON_MAX 2048U
#define APP_NET_BODY_MAX 128U

typedef struct {
  httpd_handle_t server;
  int fd;
  char payload[APP_NET_JSON_MAX];
} app_net_ws_msg_t;

static httpd_handle_t s_server;
static uint32_t s_last_push_ms;

static char *app_net_alloc_json_buffer(void) {
  return calloc(1, APP_NET_JSON_MAX);
}

static void app_net_set_cors(httpd_req_t *req) {
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
}

static const char *app_net_json_str(const char *value, char *buf, size_t len) {
  if (value == NULL || value[0] == '\0') {
    return "null";
  }

  snprintf(buf, len, "\"%s\"", value);
  return buf;
}

static size_t app_net_build_json(char *buf, size_t len) {
  app_stepper_snapshot_t stepper = {0};
  app_stepper_get_snapshot(&stepper);
  app_wifi_status_t wifi = {0};
  app_wifi_get_status(&wifi);
  app_system_status_t system = {0};
  app_get_system_status(&system);
  app_mpu_status_t mpu = {0};
  app_mpu_get_status(&mpu);
  app_i2c_status_t i2c = {0};
  app_get_i2c_status(&i2c);
  app_ble_status_t ble = {0};
  app_get_ble_status(&ble);

  char i2c_devices[48] = "[]";
  if (i2c.device_count > 0 && i2c.devices[0][0] != '\0') {
    snprintf(i2c_devices, sizeof(i2c_devices), "[\"%s\"]", i2c.devices[0]);
  }

  char system_error_json[48];
  char mpu_error_json[48];
  char mpu_address_json[16];
  char mpu_whoami_json[16];
  char mpu_model_json[40];
  char mpu_uptime_json[16];
  char i2c_detected_json[16];
  char i2c_summary_json[64];
  char i2c_error_json[48];
  char wifi_error_json[48];
  char ble_error_json[48];

  const char *system_error = app_net_json_str(system.last_error, system_error_json, sizeof(system_error_json));
  const char *mpu_error = app_net_json_str(mpu.error, mpu_error_json, sizeof(mpu_error_json));
  const char *mpu_address = app_net_json_str(mpu.address, mpu_address_json, sizeof(mpu_address_json));
  const char *mpu_whoami = app_net_json_str(mpu.whoami, mpu_whoami_json, sizeof(mpu_whoami_json));
  const char *mpu_model = app_net_json_str(mpu.model, mpu_model_json, sizeof(mpu_model_json));
  const char *mpu_uptime = app_net_json_str(mpu.uptime, mpu_uptime_json, sizeof(mpu_uptime_json));
  const char *i2c_detected = app_net_json_str(i2c.detected_mpu_address, i2c_detected_json, sizeof(i2c_detected_json));
  const char *i2c_summary = app_net_json_str(i2c.last_scan_summary, i2c_summary_json, sizeof(i2c_summary_json));
  const char *i2c_error = app_net_json_str(i2c.error, i2c_error_json, sizeof(i2c_error_json));
  const char *wifi_error = (wifi.last_error == ESP_OK)
    ? "null"
    : app_net_json_str(esp_err_to_name(wifi.last_error), wifi_error_json, sizeof(wifi_error_json));
  const char *ble_error = app_net_json_str(ble.last_error, ble_error_json, sizeof(ble_error_json));
  const char *wifi_ip = wifi.sta_ip[0] != '\0'
    ? wifi.sta_ip
    : (wifi.ap_ip[0] != '\0' ? wifi.ap_ip : "0.0.0.0");

  int written = snprintf(buf,
                         len,
                         "{\"ok\":true,\"telemetry\":{\"system\":{"
                         "\"uptimeMs\":%" PRIu32 ",\"tick\":%" PRIu32 ",\"tickDelayMs\":%" PRIu32 ","
                         "\"firmware\":\"%s\",\"appMode\":\"%s\",\"lastError\":%s},"
                         "\"mpu\":{\"ready\":%s,\"error\":%s,\"address\":%s,\"whoAmI\":%s,"
                         "\"model\":%s,\"uptimeLabel\":%s,"
                         "\"accel\":{\"x\":%.3f,\"y\":%.3f,\"z\":%.3f},"
                         "\"gyro\":{\"x\":%.2f,\"y\":%.2f,\"z\":%.2f},\"tempC\":%.2f},"
                         "\"i2c\":{\"ready\":%s,\"devices\":%s,\"detectedMpuAddress\":%s,"
                         "\"lastScanSummary\":%s,\"error\":%s},"
                         "\"stepper\":{"
                         "\"mode\":\"%s\",\"sweepState\":\"%s\",\"delayMs\":%" PRIu32 ","
                         "\"stepsPerSecond\":%.2f,\"phaseIndex\":%" PRIu32 ","
                         "\"totalSteps\":%" PRIu32 ",\"coilsEnabled\":%s,"
                         "\"sweepSteps\":%" PRIu32 ",\"uartReady\":%s,"
                         "\"lastCommand\":\"%s\","
                         "\"pins\":{\"in1\":%u,\"in2\":%u,\"in3\":%u,\"in4\":%u},"
                         "\"gpioPins\":{\"in1\":%d,\"in2\":%d,\"in3\":%d,\"in4\":%d},"
                         "\"ledGpio\":%d},\"wifi\":{"
                         "\"enabled\":%s,\"connected\":%s,\"ssid\":\"%s\",\"ip\":\"%s\","
                         "\"mac\":null,\"lastError\":%s,"
                         "\"initialized\":%s,\"apStarted\":%s,\"staAttempted\":%s,"
                         "\"staConnected\":%s,\"apSsid\":\"%s\",\"apIp\":\"%s\","
                         "\"staIp\":\"%s\"},\"ble\":{"
                         "\"initialized\":%s,\"controllerEnabled\":%s,\"advertising\":%s,"
                         "\"connected\":%s,\"notifyEnabled\":%s,\"deviceName\":\"%s\","
                         "\"address\":%s,\"lastError\":%s}}}",
                         system.uptime_ms,
                         system.tick,
                         system.tick_delay_ms,
                         system.firmware,
                         system.app_mode,
                         system_error,
                         mpu.ready ? "true" : "false",
                         mpu_error,
                         mpu_address,
                         mpu_whoami,
                         mpu_model,
                         mpu_uptime,
                         (double)mpu.accel_x_g,
                         (double)mpu.accel_y_g,
                         (double)mpu.accel_z_g,
                         (double)mpu.gyro_x_dps,
                         (double)mpu.gyro_y_dps,
                         (double)mpu.gyro_z_dps,
                         (double)mpu.temp_c,
                         i2c.ready ? "true" : "false",
                         i2c_devices,
                         i2c_detected,
                         i2c_summary,
                         i2c_error,
                         stepper.mode,
                         stepper.sweep_state,
                         stepper.step_delay_ms,
                         (double)stepper.steps_per_second,
                         stepper.phase_index,
                         stepper.total_steps,
                         stepper.coils_enabled ? "true" : "false",
                         stepper.sweep_steps,
                         stepper.uart_ready ? "true" : "false",
                         stepper.last_command,
                         (unsigned)stepper.in1_level,
                         (unsigned)stepper.in2_level,
                         (unsigned)stepper.in3_level,
                         (unsigned)stepper.in4_level,
                         stepper.in1_gpio,
                         stepper.in2_gpio,
                         stepper.in3_gpio,
                         stepper.in4_gpio,
                         stepper.led_gpio,
                         wifi.initialized ? "true" : "false",
                         (wifi.sta_connected || wifi.ap_started) ? "true" : "false",
                         wifi.ap_ssid,
                         wifi_ip,
                         wifi_error,
                         wifi.initialized ? "true" : "false",
                         wifi.ap_started ? "true" : "false",
                         wifi.sta_attempted ? "true" : "false",
                         wifi.sta_connected ? "true" : "false",
                         wifi.ap_ssid,
                         wifi.ap_ip[0] != '\0' ? wifi.ap_ip : "0.0.0.0",
                         wifi.sta_ip[0] != '\0' ? wifi.sta_ip : "0.0.0.0",
                         ble.initialized ? "true" : "false",
                         ble.controller_enabled ? "true" : "false",
                         ble.advertising ? "true" : "false",
                         ble.connected ? "true" : "false",
                         ble.notify_enabled ? "true" : "false",
                         ble.device_name,
                         ble.address[0] != '\0' ? ble.address : "null",
                         ble_error);
  if (written < 0) {
    buf[0] = '\0';
    return 0;
  }
  if ((size_t)written >= len) {
    return len - 1U;
  }
  return (size_t)written;
}

static bool app_net_extract_command(const char *body, char *cmd) {
  if (body == NULL || cmd == NULL) {
    return false;
  }

  const char *command = strstr(body, "\"command\"");
  if (command != NULL) {
    const char *colon = strchr(command, ':');
    if (colon == NULL) {
      return false;
    }
    const char *quote = strchr(colon, '"');
    if (quote == NULL || quote[1] == '\0') {
      return false;
    }
    *cmd = quote[1];
    return true;
  }

  for (const char *p = body; *p != '\0'; p++) {
    if (*p != ' ' && *p != '\r' && *p != '\n' && *p != '\t' && *p != '"') {
      *cmd = *p;
      return true;
    }
  }

  return false;
}

static esp_err_t app_net_options_handler(httpd_req_t *req) {
  app_net_set_cors(req);
  httpd_resp_send(req, NULL, 0);
  return ESP_OK;
}

static esp_err_t app_net_telemetry_handler(httpd_req_t *req) {
  char *json = app_net_alloc_json_buffer();
  if (json == NULL) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "no memory");
    return ESP_ERR_NO_MEM;
  }

  app_net_build_json(json, APP_NET_JSON_MAX);

  app_net_set_cors(req);
  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, json);
  free(json);
  return ESP_OK;
}

static esp_err_t app_net_wifi_handler(httpd_req_t *req) {
  app_wifi_status_t wifi = {0};
  app_wifi_get_status(&wifi);

  char *json = app_net_alloc_json_buffer();
  if (json == NULL) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "no memory");
    return ESP_ERR_NO_MEM;
  }

  int written = snprintf(json,
                         APP_NET_JSON_MAX,
                         "{\"ok\":true,\"wifi\":{\"initialized\":%s,\"apStarted\":%s,"
                         "\"staAttempted\":%s,\"staConnected\":%s,\"apSsid\":\"%s\","
                         "\"apIp\":\"%s\",\"staIp\":\"%s\",\"lastError\":\"%s\"}}",
                         wifi.initialized ? "true" : "false",
                         wifi.ap_started ? "true" : "false",
                         wifi.sta_attempted ? "true" : "false",
                         wifi.sta_connected ? "true" : "false",
                         wifi.ap_ssid,
                         wifi.ap_ip[0] != '\0' ? wifi.ap_ip : "0.0.0.0",
                         wifi.sta_ip[0] != '\0' ? wifi.sta_ip : "0.0.0.0",
                         esp_err_to_name(wifi.last_error));
  if (written < 0) {
    free(json);
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "json encode failed");
    return ESP_FAIL;
  }

  app_net_set_cors(req);
  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, json);
  free(json);
  return ESP_OK;
}

static esp_err_t app_net_command_handler(httpd_req_t *req) {
  char body[APP_NET_BODY_MAX] = {0};
  int received = httpd_req_recv(req, body, sizeof(body) - 1U);
  if (received <= 0) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "empty command");
    return ESP_FAIL;
  }

  body[received] = '\0';

  char cmd = 0;
  if (!app_net_extract_command(body, &cmd)) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "missing command");
    return ESP_FAIL;
  }

  esp_err_t err = app_stepper_command_char(cmd);
  if (err != ESP_OK) {
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, esp_err_to_name(err));
    return err;
  }

  return app_net_telemetry_handler(req);
}

static void app_net_ws_send_work(void *arg) {
  app_net_ws_msg_t *msg = (app_net_ws_msg_t *)arg;
  httpd_ws_frame_t frame = {
    .final = true,
    .fragmented = false,
    .type = HTTPD_WS_TYPE_TEXT,
    .payload = (uint8_t *)msg->payload,
    .len = strlen(msg->payload),
  };

  esp_err_t err = httpd_ws_send_frame_async(msg->server, msg->fd, &frame);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "ws send failed fd=%d: %s", msg->fd, esp_err_to_name(err));
  }
  free(msg);
}

static esp_err_t app_net_queue_ws_send(int fd, const char *payload) {
  if (s_server == NULL || payload == NULL) {
    return ESP_ERR_INVALID_STATE;
  }

  app_net_ws_msg_t *msg = calloc(1, sizeof(*msg));
  if (msg == NULL) {
    return ESP_ERR_NO_MEM;
  }

  msg->server = s_server;
  msg->fd = fd;
  strlcpy(msg->payload, payload, sizeof(msg->payload));

  esp_err_t err = httpd_queue_work(s_server, app_net_ws_send_work, msg);
  if (err != ESP_OK) {
    free(msg);
  }
  return err;
}

static esp_err_t app_net_ws_handler(httpd_req_t *req) {
  if (req->method == HTTP_GET) {
    ESP_LOGI(TAG, "ws connected fd=%d", httpd_req_to_sockfd(req));
    return ESP_OK;
  }

  httpd_ws_frame_t frame = {
    .type = HTTPD_WS_TYPE_TEXT,
  };
  esp_err_t err = httpd_ws_recv_frame(req, &frame, 0);
  if (err != ESP_OK) {
    return err;
  }

  char *payload = calloc(1, frame.len + 1U);
  if (payload == NULL) {
    return ESP_ERR_NO_MEM;
  }

  frame.payload = (uint8_t *)payload;
  err = httpd_ws_recv_frame(req, &frame, frame.len);
  if (err == ESP_OK && frame.type == HTTPD_WS_TYPE_TEXT && frame.len > 0) {
    char cmd = 0;
    if (app_net_extract_command(payload, &cmd)) {
      app_stepper_command_char(cmd);
    }
  }
  free(payload);

  char *json = app_net_alloc_json_buffer();
  if (json == NULL) {
    return ESP_ERR_NO_MEM;
  }

  app_net_build_json(json, APP_NET_JSON_MAX);
  httpd_ws_frame_t response = {
    .final = true,
    .fragmented = false,
    .type = HTTPD_WS_TYPE_TEXT,
    .payload = (uint8_t *)json,
    .len = strlen(json),
  };
  err = httpd_ws_send_frame(req, &response);
  free(json);
  return err;
}

esp_err_t app_net_start(void) {
  if (s_server != NULL) {
    return ESP_OK;
  }

  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.max_uri_handlers = 8;

  esp_err_t err = httpd_start(&s_server, &config);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "http server start failed: %s", esp_err_to_name(err));
    return err;
  }

  const httpd_uri_t telemetry_get = {
    .uri = "/api/telemetry",
    .method = HTTP_GET,
    .handler = app_net_telemetry_handler,
  };
  const httpd_uri_t wifi_get = {
    .uri = "/api/wifi",
    .method = HTTP_GET,
    .handler = app_net_wifi_handler,
  };
  const httpd_uri_t command_post = {
    .uri = "/api/command",
    .method = HTTP_POST,
    .handler = app_net_command_handler,
  };
  const httpd_uri_t options = {
    .uri = "/*",
    .method = HTTP_OPTIONS,
    .handler = app_net_options_handler,
  };
  const httpd_uri_t ws = {
    .uri = "/ws",
    .method = HTTP_GET,
    .handler = app_net_ws_handler,
    .is_websocket = true,
  };

  ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &telemetry_get));
  ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &wifi_get));
  ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &command_post));
  ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &options));
  ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &ws));

  ESP_LOGI(TAG, "http/ws server listening on port %d", config.server_port);
  return ESP_OK;
}

void app_net_tick(void) {
  if (s_server == NULL) {
    return;
  }

  const uint32_t now_ms = esp_log_timestamp();
  if ((now_ms - s_last_push_ms) < APP_NET_WS_PUSH_PERIOD_MS) {
    return;
  }
  s_last_push_ms = now_ms;

  size_t clients = CONFIG_LWIP_MAX_SOCKETS;
  int client_fds[CONFIG_LWIP_MAX_SOCKETS];
  if (httpd_get_client_list(s_server, &clients, client_fds) != ESP_OK) {
    return;
  }

  char *json = app_net_alloc_json_buffer();
  if (json == NULL) {
    ESP_LOGW(TAG, "json alloc failed");
    return;
  }

  app_net_build_json(json, APP_NET_JSON_MAX);

  for (size_t i = 0; i < clients; i++) {
    if (httpd_ws_get_fd_info(s_server, client_fds[i]) == HTTPD_WS_CLIENT_WEBSOCKET) {
      esp_err_t err = app_net_queue_ws_send(client_fds[i], json);
      if (err != ESP_OK) {
        ESP_LOGW(TAG, "queue ws send failed: %s", esp_err_to_name(err));
      }
    }
  }

  free(json);
}

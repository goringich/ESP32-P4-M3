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

#include "app_wifi.h"
#include "app_stepper.h"

static const char *TAG = "app_net";

#define APP_NET_WS_PUSH_PERIOD_MS 1000U
#define APP_NET_JSON_MAX 768U
#define APP_NET_BODY_MAX 128U

typedef struct {
  httpd_handle_t server;
  int fd;
  char payload[APP_NET_JSON_MAX];
} app_net_ws_msg_t;

static httpd_handle_t s_server;
static uint32_t s_last_push_ms;

static void app_net_set_cors(httpd_req_t *req) {
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
}

static size_t app_net_build_json(char *buf, size_t len) {
  app_stepper_snapshot_t stepper = {0};
  app_stepper_get_snapshot(&stepper);
  app_wifi_status_t wifi = {0};
  app_wifi_get_status(&wifi);

  int written = snprintf(buf,
                         len,
                         "{\"ok\":true,\"telemetry\":{\"stepper\":{"
                         "\"mode\":\"%s\",\"sweepState\":\"%s\",\"delayMs\":%" PRIu32 ","
                         "\"stepsPerSecond\":%.2f,\"phaseIndex\":%" PRIu32 ","
                         "\"totalSteps\":%" PRIu32 ",\"coilsEnabled\":%s,"
                         "\"sweepSteps\":%" PRIu32 ",\"uartReady\":%s,"
                         "\"lastCommand\":\"%s\","
                         "\"pins\":{\"in1\":%d,\"in2\":%d,\"in3\":%d,\"in4\":%d},"
                         "\"ledGpio\":%d},\"wifi\":{"
                         "\"initialized\":%s,\"apStarted\":%s,\"staAttempted\":%s,"
                         "\"staConnected\":%s,\"apSsid\":\"%s\",\"apIp\":\"%s\","
                         "\"staIp\":\"%s\",\"lastError\":\"%s\"}}}",
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
                         stepper.in1_gpio,
                         stepper.in2_gpio,
                         stepper.in3_gpio,
                         stepper.in4_gpio,
                         stepper.led_gpio,
                         wifi.initialized ? "true" : "false",
                         wifi.ap_started ? "true" : "false",
                         wifi.sta_attempted ? "true" : "false",
                         wifi.sta_connected ? "true" : "false",
                         wifi.ap_ssid,
                         wifi.ap_ip[0] != '\0' ? wifi.ap_ip : "0.0.0.0",
                         wifi.sta_ip[0] != '\0' ? wifi.sta_ip : "0.0.0.0",
                         esp_err_to_name(wifi.last_error));
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
  char json[APP_NET_JSON_MAX];
  app_net_build_json(json, sizeof(json));

  app_net_set_cors(req);
  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, json);
  return ESP_OK;
}

static esp_err_t app_net_wifi_handler(httpd_req_t *req) {
  app_wifi_status_t wifi = {0};
  app_wifi_get_status(&wifi);

  char json[APP_NET_JSON_MAX];
  int written = snprintf(json,
                         sizeof(json),
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
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "json encode failed");
    return ESP_FAIL;
  }

  app_net_set_cors(req);
  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, json);
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

  char json[APP_NET_JSON_MAX];
  app_net_build_json(json, sizeof(json));
  httpd_ws_frame_t response = {
    .final = true,
    .fragmented = false,
    .type = HTTPD_WS_TYPE_TEXT,
    .payload = (uint8_t *)json,
    .len = strlen(json),
  };
  return httpd_ws_send_frame(req, &response);
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

  char json[APP_NET_JSON_MAX];
  app_net_build_json(json, sizeof(json));

  for (size_t i = 0; i < clients; i++) {
    if (httpd_ws_get_fd_info(s_server, client_fds[i]) == HTTPD_WS_CLIENT_WEBSOCKET) {
      esp_err_t err = app_net_queue_ws_send(client_fds[i], json);
      if (err != ESP_OK) {
        ESP_LOGW(TAG, "queue ws send failed: %s", esp_err_to_name(err));
      }
    }
  }
}

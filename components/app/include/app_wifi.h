#pragma once

#include <stdbool.h>

#include "esp_err.h"

typedef struct {
  bool initialized;
  bool ap_started;
  bool sta_attempted;
  bool sta_connected;
  char ap_ssid[33];
  char ap_ip[16];
  char sta_ip[16];
  esp_err_t last_error;
} app_wifi_status_t;

esp_err_t app_wifi_smoke_run(void);
void app_wifi_get_status(app_wifi_status_t *status);

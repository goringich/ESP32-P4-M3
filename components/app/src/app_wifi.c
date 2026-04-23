#include "app_wifi.h"

#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

static const char *TAG = "app_wifi";

#define APP_WIFI_COLOR_RESET "\x1b[0m"
#define APP_WIFI_COLOR_HDR "\x1b[38;5;45m"
#define APP_WIFI_COLOR_OK "\x1b[38;5;82m"
#define APP_WIFI_COLOR_WARN "\x1b[38;5;220m"
#define APP_WIFI_COLOR_AP "\x1b[38;5;117m"
#define APP_WIFI_COLOR_RSSI "\x1b[38;5;213m"

static const char *app_wifi_auth_to_str(wifi_auth_mode_t authmode);
static void app_wifi_log_block(const char *title);
static esp_err_t app_wifi_nvs_init_once(void);
static void app_wifi_refresh_status_locked(void);
static void app_wifi_build_ap_ssid(char *ssid, size_t ssid_len, const uint8_t mac[6]);

#if CONFIG_APP_WIFI_CONNECT
#define APP_WIFI_MAX_RETRIES 10
static int s_wifi_retries;
#endif

static esp_netif_t *s_sta_netif;
static esp_netif_t *s_ap_netif;
static bool s_wifi_started;
static app_wifi_status_t s_status = {
  .initialized = false,
  .ap_started = false,
  .sta_attempted = false,
  .sta_connected = false,
  .ap_ssid = {0},
  .ap_ip = {0},
  .sta_ip = {0},
  .last_error = ESP_OK,
};

static const char *app_wifi_auth_to_str(wifi_auth_mode_t authmode) {
  switch (authmode) {
    case WIFI_AUTH_OPEN:
      return "OPEN";
    case WIFI_AUTH_WEP:
      return "WEP";
    case WIFI_AUTH_WPA_PSK:
      return "WPA-PSK";
    case WIFI_AUTH_WPA2_PSK:
      return "WPA2-PSK";
    case WIFI_AUTH_WPA_WPA2_PSK:
      return "WPA/WPA2";
    case WIFI_AUTH_WPA2_ENTERPRISE:
      return "WPA2-ENT";
    case WIFI_AUTH_WPA3_PSK:
      return "WPA3-PSK";
    case WIFI_AUTH_WPA2_WPA3_PSK:
      return "WPA2/WPA3";
    case WIFI_AUTH_WAPI_PSK:
      return "WAPI";
    default:
      return "UNKNOWN";
  }
}

static void app_wifi_log_block(const char *title) {
  static const char divider[] = "----------------------------------------";

  ESP_LOGI(TAG, "%s%s%s", APP_WIFI_COLOR_HDR, divider, APP_WIFI_COLOR_RESET);
  if (title != NULL && title[0] != '\0') {
    ESP_LOGI(TAG, "%s  %s  %s", APP_WIFI_COLOR_HDR, title, APP_WIFI_COLOR_RESET);
  }
  ESP_LOGI(TAG, "%s%s%s", APP_WIFI_COLOR_HDR, divider, APP_WIFI_COLOR_RESET);
}

static esp_err_t app_wifi_nvs_init_once(void) {
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
  return err;
}

static void app_wifi_build_ap_ssid(char *ssid, size_t ssid_len, const uint8_t mac[6]) {
  if (ssid == NULL || ssid_len == 0) {
    return;
  }

  if (mac != NULL) {
    snprintf(ssid,
             ssid_len,
             "%s-%02X%02X%02X",
             CONFIG_APP_WIFI_AP_SSID_PREFIX,
             mac[3],
             mac[4],
             mac[5]);
    return;
  }

  strlcpy(ssid, CONFIG_APP_WIFI_AP_SSID_PREFIX, ssid_len);
}

static void app_wifi_refresh_status_locked(void) {
  if (s_sta_netif != NULL) {
    esp_netif_ip_info_t sta_ip = {0};
    if (esp_netif_get_ip_info(s_sta_netif, &sta_ip) == ESP_OK) {
      snprintf(s_status.sta_ip,
               sizeof(s_status.sta_ip),
               IPSTR,
               IP2STR(&sta_ip.ip));
    }
  }

  if (s_ap_netif != NULL) {
    esp_netif_ip_info_t ap_ip = {0};
    if (esp_netif_get_ip_info(s_ap_netif, &ap_ip) == ESP_OK) {
      snprintf(s_status.ap_ip,
               sizeof(s_status.ap_ip),
               IPSTR,
               IP2STR(&ap_ip.ip));
    }
  }
}

static void app_wifi_log_scan_results(void) {
  uint16_t ap_count = CONFIG_APP_WIFI_SCAN_MAX_AP;
  wifi_ap_record_t *records = calloc(ap_count, sizeof(wifi_ap_record_t));
  if (records == NULL) {
    ESP_LOGE(TAG, "scan record alloc failed");
    s_status.last_error = ESP_ERR_NO_MEM;
    return;
  }

  wifi_scan_config_t scan_cfg = {
      .ssid = NULL,
      .bssid = NULL,
      .channel = 0,
      .show_hidden = true,
  };

  app_wifi_log_block("WIFI SCAN RESULTS");

  esp_err_t err = esp_wifi_scan_start(&scan_cfg, true);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "scan start failed: %s", esp_err_to_name(err));
    s_status.last_error = err;
    free(records);
    return;
  }

  err = esp_wifi_scan_get_ap_records(&ap_count, records);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "scan get records failed: %s", esp_err_to_name(err));
    s_status.last_error = err;
    free(records);
    return;
  }

  ESP_LOGI(TAG,
           "scan complete: %s%" PRIu16 " AP%s",
           (ap_count > 0) ? APP_WIFI_COLOR_OK : APP_WIFI_COLOR_WARN,
           ap_count,
           APP_WIFI_COLOR_RESET);

  if (ap_count == 0) {
    ESP_LOGW(TAG, "%sNo AP found. Check antenna / country / channel plan%s", APP_WIFI_COLOR_WARN, APP_WIFI_COLOR_RESET);
  }

  for (uint16_t i = 0; i < ap_count; i++) {
    const char *ssid = (const char *)records[i].ssid;
    if (ssid[0] == '\0') {
      ssid = "<hidden>";
    }

    ESP_LOGI(TAG,
             "%s[%02" PRIu16 "]%s %-24s | %sRSSI%s %4d dBm | CH %2u | %s",
             APP_WIFI_COLOR_AP,
             i,
             APP_WIFI_COLOR_RESET,
             ssid,
             APP_WIFI_COLOR_RSSI,
             APP_WIFI_COLOR_RESET,
             records[i].rssi,
             records[i].primary,
             app_wifi_auth_to_str(records[i].authmode));
  }

  free(records);
}

#if CONFIG_APP_WIFI_CONNECT
static void app_wifi_event_handler(void *arg,
                                   esp_event_base_t event_base,
                                   int32_t event_id,
                                   void *event_data) {
  (void)arg;

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
    s_status.sta_attempted = true;
    if (strlen(CONFIG_APP_WIFI_SSID) > 0) {
      esp_wifi_connect();
    }
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
    s_status.sta_connected = false;
    s_status.last_error = ESP_FAIL;

    if (strlen(CONFIG_APP_WIFI_SSID) == 0) {
      return;
    }

    if (s_wifi_retries < APP_WIFI_MAX_RETRIES) {
      s_wifi_retries++;
      ESP_LOGW(TAG, "connect retry %d/%d", s_wifi_retries, APP_WIFI_MAX_RETRIES);
      esp_wifi_connect();
    }
    return;
  }

  if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
    const ip_event_got_ip_t *event = (const ip_event_got_ip_t *)event_data;
    s_status.sta_connected = true;
    s_status.last_error = ESP_OK;
    snprintf(s_status.sta_ip, sizeof(s_status.sta_ip), IPSTR, IP2STR(&event->ip_info.ip));
    ESP_LOGI(TAG, "got ip: " IPSTR, IP2STR(&event->ip_info.ip));
  }
}
#endif

static void app_wifi_event_handler_common(void *arg,
                                          esp_event_base_t event_base,
                                          int32_t event_id,
                                          void *event_data) {
  (void)arg;
  (void)event_data;

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_START) {
    s_status.ap_started = true;
    app_wifi_refresh_status_locked();
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STOP) {
    s_status.ap_started = false;
    return;
  }

  if (event_base == IP_EVENT && event_id == IP_EVENT_AP_STAIPASSIGNED) {
    app_wifi_refresh_status_locked();
    return;
  }

#if CONFIG_APP_WIFI_CONNECT
  app_wifi_event_handler(arg, event_base, event_id, event_data);
#endif
}

esp_err_t app_wifi_smoke_run(void) {
#if !(CONFIG_ESP_WIFI_ENABLED || CONFIG_ESP_HOST_WIFI_ENABLED)
  ESP_LOGW(TAG,
           "Wi-Fi stack is not enabled in sdkconfig (enable ESP_HOST_WIFI_ENABLED for ESP32-P4 + C6)");
  return ESP_ERR_NOT_SUPPORTED;
#else
  if (s_wifi_started) {
    return ESP_OK;
  }

  app_wifi_log_block("WIFI BRINGUP");

  esp_err_t err = app_wifi_nvs_init_once();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "nvs init failed: %s", esp_err_to_name(err));
    s_status.last_error = err;
    return err;
  }

  err = esp_netif_init();
  if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
    ESP_LOGE(TAG, "esp_netif_init failed: %s", esp_err_to_name(err));
    s_status.last_error = err;
    return err;
  }

  err = esp_event_loop_create_default();
  if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
    ESP_LOGE(TAG, "event loop init failed: %s", esp_err_to_name(err));
    s_status.last_error = err;
    return err;
  }

  if (s_sta_netif == NULL) {
    s_sta_netif = esp_netif_create_default_wifi_sta();
  }
  if (s_ap_netif == NULL) {
    s_ap_netif = esp_netif_create_default_wifi_ap();
  }

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  err = esp_wifi_init(&cfg);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "esp_wifi_init failed: %s", esp_err_to_name(err));
    s_status.last_error = err;
    return err;
  }

  esp_event_handler_instance_t wifi_any_id;
  esp_event_handler_instance_t ip_any_id;
  ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &app_wifi_event_handler_common, NULL, &wifi_any_id));
  ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT, ESP_EVENT_ANY_ID, &app_wifi_event_handler_common, NULL, &ip_any_id));
  (void)wifi_any_id;
  (void)ip_any_id;

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));

  uint8_t ap_mac[6] = {0};
  if (esp_wifi_get_mac(WIFI_IF_AP, ap_mac) != ESP_OK) {
    memset(ap_mac, 0, sizeof(ap_mac));
  }
  app_wifi_build_ap_ssid(s_status.ap_ssid, sizeof(s_status.ap_ssid), ap_mac);

  wifi_config_t ap_cfg = {0};
  strlcpy((char *)ap_cfg.ap.ssid, s_status.ap_ssid, sizeof(ap_cfg.ap.ssid));
  ap_cfg.ap.ssid_len = strlen((const char *)ap_cfg.ap.ssid);
  ap_cfg.ap.channel = CONFIG_APP_WIFI_AP_CHANNEL;
  ap_cfg.ap.max_connection = 4;
  ap_cfg.ap.beacon_interval = 100;

  const size_t ap_password_len = strlen(CONFIG_APP_WIFI_AP_PASSWORD);
  if (ap_password_len >= 8U) {
    strlcpy((char *)ap_cfg.ap.password, CONFIG_APP_WIFI_AP_PASSWORD, sizeof(ap_cfg.ap.password));
    ap_cfg.ap.authmode = WIFI_AUTH_WPA2_PSK;
  } else {
    ap_cfg.ap.authmode = WIFI_AUTH_OPEN;
    if (ap_password_len > 0U) {
      ESP_LOGW(TAG, "AP password too short for WPA2, starting open AP instead");
    }
  }

  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &ap_cfg));

#if CONFIG_APP_WIFI_CONNECT
  s_status.sta_attempted = true;
  s_wifi_retries = 0;
  if (strlen(CONFIG_APP_WIFI_SSID) > 0) {
    wifi_config_t sta_cfg = {0};
    strlcpy((char *)sta_cfg.sta.ssid, CONFIG_APP_WIFI_SSID, sizeof(sta_cfg.sta.ssid));
    strlcpy((char *)sta_cfg.sta.password, CONFIG_APP_WIFI_PASSWORD, sizeof(sta_cfg.sta.password));
    sta_cfg.sta.threshold.authmode = (strlen(CONFIG_APP_WIFI_PASSWORD) == 0) ? WIFI_AUTH_OPEN : WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta_cfg));
    ESP_LOGI(TAG, "STA connect configured for '%s'", CONFIG_APP_WIFI_SSID);
  } else {
    ESP_LOGW(TAG, "APP_WIFI_CONNECT enabled, but APP_WIFI_SSID is empty. Running AP only.");
  }
#endif

  ESP_ERROR_CHECK(esp_wifi_start());
  ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));

  app_wifi_refresh_status_locked();

  uint8_t sta_mac[6] = {0};
  err = esp_wifi_get_mac(WIFI_IF_STA, sta_mac);
  if (err == ESP_OK) {
    ESP_LOGI(TAG,
             "%sSTA MAC%s %02X:%02X:%02X:%02X:%02X:%02X",
             APP_WIFI_COLOR_OK,
             APP_WIFI_COLOR_RESET,
             sta_mac[0],
             sta_mac[1],
             sta_mac[2],
             sta_mac[3],
             sta_mac[4],
             sta_mac[5]);
  } else {
    ESP_LOGW(TAG, "esp_wifi_get_mac(STA) failed: %s", esp_err_to_name(err));
  }

  ESP_LOGI(TAG,
           "%sAP ready%s ssid='%s' ip='%s' channel=%d auth=%s",
           APP_WIFI_COLOR_OK,
           APP_WIFI_COLOR_RESET,
           s_status.ap_ssid,
           s_status.ap_ip[0] != '\0' ? s_status.ap_ip : "192.168.4.1",
           CONFIG_APP_WIFI_AP_CHANNEL,
           ap_cfg.ap.authmode == WIFI_AUTH_OPEN ? "OPEN" : "WPA2-PSK");

  app_wifi_log_scan_results();

  s_status.initialized = true;
  s_status.last_error = ESP_OK;
  s_wifi_started = true;
  return ESP_OK;
#endif
}

void app_wifi_get_status(app_wifi_status_t *status) {
  if (status == NULL) {
    return;
  }

  *status = s_status;
  app_wifi_refresh_status_locked();
  status->ap_started = s_status.ap_started;
  status->sta_attempted = s_status.sta_attempted;
  status->sta_connected = s_status.sta_connected;
  status->initialized = s_status.initialized;
  status->last_error = s_status.last_error;
  strlcpy(status->ap_ssid, s_status.ap_ssid, sizeof(status->ap_ssid));
  strlcpy(status->ap_ip, s_status.ap_ip, sizeof(status->ap_ip));
  strlcpy(status->sta_ip, s_status.sta_ip, sizeof(status->sta_ip));
}

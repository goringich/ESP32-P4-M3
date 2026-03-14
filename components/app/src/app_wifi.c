#include "app_wifi.h"

#include <stdlib.h>
#include <string.h>

#include <inttypes.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

#if CONFIG_APP_WIFI_CONNECT
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#endif

static const char *TAG = "app_wifi";

#define APP_WIFI_COLOR_RESET "\x1b[0m"
#define APP_WIFI_COLOR_HDR "\x1b[38;5;45m"
#define APP_WIFI_COLOR_OK "\x1b[38;5;82m"
#define APP_WIFI_COLOR_WARN "\x1b[38;5;220m"
#define APP_WIFI_COLOR_AP "\x1b[38;5;117m"
#define APP_WIFI_COLOR_RSSI "\x1b[38;5;213m"

static const char *app_wifi_auth_to_str(wifi_auth_mode_t authmode);
static void app_wifi_log_block(const char *title);

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

#if CONFIG_APP_WIFI_CONNECT
#define APP_WIFI_CONNECTED_BIT BIT0
#define APP_WIFI_FAIL_BIT      BIT1
#define APP_WIFI_MAX_RETRIES   10

static EventGroupHandle_t s_wifi_event_group;
static int s_wifi_retries;

static void app_wifi_event_handler(void *arg,
                                   esp_event_base_t event_base,
                                   int32_t event_id,
                                   void *event_data) {
  (void)arg;

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
    esp_wifi_connect();
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
    if (s_wifi_retries < APP_WIFI_MAX_RETRIES) {
      s_wifi_retries++;
      ESP_LOGW(TAG, "connect retry %d/%d", s_wifi_retries, APP_WIFI_MAX_RETRIES);
      esp_wifi_connect();
    } else {
      xEventGroupSetBits(s_wifi_event_group, APP_WIFI_FAIL_BIT);
    }
    return;
  }

  if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
    const ip_event_got_ip_t *event = (const ip_event_got_ip_t *)event_data;
    ESP_LOGI(TAG, "got ip: " IPSTR, IP2STR(&event->ip_info.ip));
    xEventGroupSetBits(s_wifi_event_group, APP_WIFI_CONNECTED_BIT);
  }
}
#endif

static esp_err_t app_wifi_nvs_init_once(void) {
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
  return err;
}

esp_err_t app_wifi_smoke_run(void) {
#if !(CONFIG_ESP_WIFI_ENABLED || CONFIG_ESP_HOST_WIFI_ENABLED)
  ESP_LOGW(TAG,
           "Wi-Fi stack is not enabled in sdkconfig (enable ESP_HOST_WIFI_ENABLED for ESP32-P4 + C6)");
  return ESP_ERR_NOT_SUPPORTED;
#else
  app_wifi_log_block("WIFI SMOKE START");

  esp_err_t err = app_wifi_nvs_init_once();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "nvs init failed: %s", esp_err_to_name(err));
    return err;
  }

  err = esp_netif_init();
  if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
    ESP_LOGE(TAG, "esp_netif_init failed: %s", esp_err_to_name(err));
    return err;
  }

  err = esp_event_loop_create_default();
  if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
    ESP_LOGE(TAG, "event loop init failed: %s", esp_err_to_name(err));
    return err;
  }

  esp_netif_create_default_wifi_sta();

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  err = esp_wifi_init(&cfg);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "esp_wifi_init failed: %s", esp_err_to_name(err));
    return err;
  }

#if CONFIG_APP_WIFI_CONNECT
  s_wifi_event_group = xEventGroupCreate();
  if (s_wifi_event_group == NULL) {
    ESP_LOGE(TAG, "cannot create event group");
    return ESP_ERR_NO_MEM;
  }

  ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &app_wifi_event_handler, NULL));
  ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &app_wifi_event_handler, NULL));
#endif

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_start());

  uint8_t mac[6] = {0};
  err = esp_wifi_get_mac(WIFI_IF_STA, mac);
  if (err == ESP_OK) {
    ESP_LOGI(TAG,
             "%sSTA MAC%s %02X:%02X:%02X:%02X:%02X:%02X",
             APP_WIFI_COLOR_OK,
             APP_WIFI_COLOR_RESET,
             mac[0],
             mac[1],
             mac[2],
             mac[3],
             mac[4],
             mac[5]);
    if ((mac[0] | mac[1] | mac[2] | mac[3] | mac[4] | mac[5]) == 0) {
      ESP_LOGW(TAG,
               "%sMAC is all zeros -> check host-wireless link to ESP32-C6%s",
               APP_WIFI_COLOR_WARN,
               APP_WIFI_COLOR_RESET);
    }
  } else {
    ESP_LOGW(TAG, "esp_wifi_get_mac failed: %s", esp_err_to_name(err));
  }

  uint16_t ap_count = CONFIG_APP_WIFI_SCAN_MAX_AP;
  wifi_ap_record_t *records = calloc(ap_count, sizeof(wifi_ap_record_t));
  if (records == NULL) {
    ESP_LOGE(TAG, "scan record alloc failed");
    return ESP_ERR_NO_MEM;
  }

  wifi_scan_config_t scan_cfg = {
      .ssid = NULL,
      .bssid = NULL,
      .channel = 0,
      .show_hidden = true,
  };

  app_wifi_log_block("WIFI SCAN RESULTS");

  ESP_ERROR_CHECK(esp_wifi_scan_start(&scan_cfg, true));
  ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&ap_count, records));
  ESP_LOGI(TAG,
           "scan complete: %s%" PRIu16 " AP%s",
           (ap_count > 0) ? APP_WIFI_COLOR_OK : APP_WIFI_COLOR_WARN,
           ap_count,
           APP_WIFI_COLOR_RESET);

  if (ap_count == 0) {
    ESP_LOGW(TAG,
             "%sNo AP found. Check antenna / country / channel plan / C6 host link%s",
             APP_WIFI_COLOR_WARN,
             APP_WIFI_COLOR_RESET);
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

#if CONFIG_APP_WIFI_CONNECT
  if (strlen(CONFIG_APP_WIFI_SSID) == 0) {
    ESP_LOGW(TAG, "APP_WIFI_CONNECT enabled, but APP_WIFI_SSID is empty. Connect phase skipped.");
    return ESP_OK;
  }

  wifi_config_t wifi_cfg = {0};
  strncpy((char *)wifi_cfg.sta.ssid, CONFIG_APP_WIFI_SSID, sizeof(wifi_cfg.sta.ssid) - 1);
  strncpy((char *)wifi_cfg.sta.password, CONFIG_APP_WIFI_PASSWORD, sizeof(wifi_cfg.sta.password) - 1);

  if (strlen(CONFIG_APP_WIFI_PASSWORD) == 0) {
    wifi_cfg.sta.threshold.authmode = WIFI_AUTH_OPEN;
  } else {
    wifi_cfg.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
  }

  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg));
  ESP_ERROR_CHECK(esp_wifi_connect());

  EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                         APP_WIFI_CONNECTED_BIT | APP_WIFI_FAIL_BIT,
                                         pdFALSE,
                                         pdFALSE,
                                         pdMS_TO_TICKS(20000));

  if (bits & APP_WIFI_CONNECTED_BIT) {
    ESP_LOGI(TAG, "connect success to '%s'", CONFIG_APP_WIFI_SSID);
    return ESP_OK;
  }

  if (bits & APP_WIFI_FAIL_BIT) {
    ESP_LOGE(TAG, "connect failed to '%s'", CONFIG_APP_WIFI_SSID);
    return ESP_FAIL;
  }

  ESP_LOGE(TAG, "connect timeout to '%s'", CONFIG_APP_WIFI_SSID);
  return ESP_ERR_TIMEOUT;
#else
  return ESP_OK;
#endif
#endif
}

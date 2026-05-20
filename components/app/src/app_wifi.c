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
static wifi_mode_t app_wifi_pick_mode(void);
static size_t app_wifi_profile_count(void);
static bool app_wifi_profile_is_valid(size_t index);
static esp_err_t app_wifi_apply_sta_profile(size_t index, bool announce);
static bool app_wifi_advance_sta_profile(void);
static const char *app_wifi_disconnect_reason_to_str(wifi_err_reason_t reason);
static bool app_wifi_disconnect_should_switch_now(wifi_err_reason_t reason);
static bool app_wifi_pick_visible_profile(size_t *index_out, int *rssi_out, int exclude_index);

#if CONFIG_APP_WIFI_CONNECT
#define APP_WIFI_MAX_RETRIES 3
static int s_wifi_retries;
static size_t s_wifi_profile_index;

typedef struct {
  const char *ssid;
  const char *password;
} app_wifi_profile_t;

static const app_wifi_profile_t s_wifi_profiles[] = {
  {
    .ssid = CONFIG_APP_WIFI_SSID,
    .password = CONFIG_APP_WIFI_PASSWORD,
  },
  {
    .ssid = CONFIG_APP_WIFI_SSID_SECONDARY,
    .password = CONFIG_APP_WIFI_PASSWORD_SECONDARY,
  },
};
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
  .sta_ssid = {0},
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

static wifi_mode_t app_wifi_pick_mode(void) {
  return WIFI_MODE_AP;
}

#if CONFIG_APP_WIFI_CONNECT
static size_t app_wifi_profile_count(void) {
  return sizeof(s_wifi_profiles) / sizeof(s_wifi_profiles[0]);
}

static bool app_wifi_profile_is_valid(size_t index) {
  if (index >= app_wifi_profile_count()) {
    return false;
  }

  return s_wifi_profiles[index].ssid != NULL && s_wifi_profiles[index].ssid[0] != '\0';
}

static esp_err_t app_wifi_apply_sta_profile(size_t index, bool announce) {
  if (!app_wifi_profile_is_valid(index)) {
    return ESP_ERR_INVALID_ARG;
  }

  wifi_config_t sta_cfg = {0};
  const app_wifi_profile_t *profile = &s_wifi_profiles[index];
  strlcpy((char *)sta_cfg.sta.ssid, profile->ssid, sizeof(sta_cfg.sta.ssid));
  strlcpy((char *)sta_cfg.sta.password, profile->password, sizeof(sta_cfg.sta.password));
  sta_cfg.sta.threshold.authmode = (strlen(profile->password) == 0)
    ? WIFI_AUTH_OPEN
    : WIFI_AUTH_WPA2_PSK;

  esp_err_t err = esp_wifi_set_config(WIFI_IF_STA, &sta_cfg);
  if (err != ESP_OK) {
    return err;
  }

  s_wifi_profile_index = index;
  strlcpy(s_status.sta_ssid, profile->ssid, sizeof(s_status.sta_ssid));
  s_status.sta_attempted = true;

  if (announce) {
    ESP_LOGI(TAG,
             "STA profile %u/%u selected: '%s'",
             (unsigned)(index + 1U),
             (unsigned)app_wifi_profile_count(),
             profile->ssid);
  }

  return ESP_OK;
}

static bool app_wifi_advance_sta_profile(void) {
  const size_t count = app_wifi_profile_count();
  if (count == 0) {
    return false;
  }

  for (size_t offset = 1; offset <= count; offset++) {
    const size_t candidate = (s_wifi_profile_index + offset) % count;
    if (!app_wifi_profile_is_valid(candidate)) {
      continue;
    }

    if (candidate == s_wifi_profile_index && offset != count) {
      continue;
    }

    if (app_wifi_apply_sta_profile(candidate, true) == ESP_OK) {
      return true;
    }
  }

  return false;
}

static const char *app_wifi_disconnect_reason_to_str(wifi_err_reason_t reason) {
  switch (reason) {
    case WIFI_REASON_BEACON_TIMEOUT:
      return "BEACON_TIMEOUT";
    case WIFI_REASON_NO_AP_FOUND:
      return "NO_AP_FOUND";
    case WIFI_REASON_AUTH_FAIL:
      return "AUTH_FAIL";
    case WIFI_REASON_ASSOC_FAIL:
      return "ASSOC_FAIL";
    case WIFI_REASON_4WAY_HANDSHAKE_TIMEOUT:
      return "4WAY_HANDSHAKE_TIMEOUT";
    case WIFI_REASON_HANDSHAKE_TIMEOUT:
      return "HANDSHAKE_TIMEOUT";
    case WIFI_REASON_CONNECTION_FAIL:
      return "CONNECTION_FAIL";
    case WIFI_REASON_NO_AP_FOUND_W_COMPATIBLE_SECURITY:
      return "NO_AP_FOUND_W_COMPATIBLE_SECURITY";
    case WIFI_REASON_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD:
      return "NO_AP_FOUND_IN_AUTHMODE_THRESHOLD";
    case WIFI_REASON_NO_AP_FOUND_IN_RSSI_THRESHOLD:
      return "NO_AP_FOUND_IN_RSSI_THRESHOLD";
    default:
      return "OTHER";
  }
}

static bool app_wifi_disconnect_should_switch_now(wifi_err_reason_t reason) {
  switch (reason) {
    case WIFI_REASON_NO_AP_FOUND:
    case WIFI_REASON_AUTH_FAIL:
    case WIFI_REASON_ASSOC_FAIL:
    case WIFI_REASON_4WAY_HANDSHAKE_TIMEOUT:
    case WIFI_REASON_HANDSHAKE_TIMEOUT:
    case WIFI_REASON_CONNECTION_FAIL:
    case WIFI_REASON_NO_AP_FOUND_W_COMPATIBLE_SECURITY:
    case WIFI_REASON_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD:
    case WIFI_REASON_NO_AP_FOUND_IN_RSSI_THRESHOLD:
      return true;
    default:
      return false;
  }
}

static bool app_wifi_pick_visible_profile(size_t *index_out, int *rssi_out, int exclude_index) {
  uint16_t ap_count = CONFIG_APP_WIFI_SCAN_MAX_AP;
  wifi_ap_record_t *records = calloc(ap_count, sizeof(wifi_ap_record_t));
  if (records == NULL) {
    ESP_LOGE(TAG, "scan record alloc failed");
    s_status.last_error = ESP_ERR_NO_MEM;
    return false;
  }

  const wifi_scan_config_t scan_cfg = {
      .ssid = NULL,
      .bssid = NULL,
      .channel = 0,
      .show_hidden = true,
  };

  bool found = false;
  size_t best_index = 0U;
  int best_rssi = -127;

  esp_err_t err = esp_wifi_scan_start(&scan_cfg, true);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "scan start failed while selecting STA profile: %s", esp_err_to_name(err));
    s_status.last_error = err;
    free(records);
    return false;
  }

  err = esp_wifi_scan_get_ap_records(&ap_count, records);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "scan get records failed while selecting STA profile: %s", esp_err_to_name(err));
    s_status.last_error = err;
    free(records);
    return false;
  }

  for (uint16_t i = 0; i < ap_count; i++) {
    const char *scan_ssid = (const char *)records[i].ssid;
    if (scan_ssid[0] == '\0') {
      continue;
    }

    for (size_t profile_index = 0; profile_index < app_wifi_profile_count(); profile_index++) {
      if (!app_wifi_profile_is_valid(profile_index)) {
        continue;
      }
      if (exclude_index >= 0 && (int)profile_index == exclude_index) {
        continue;
      }
      if (strcmp(scan_ssid, s_wifi_profiles[profile_index].ssid) != 0) {
        continue;
      }

      if (!found || records[i].rssi > best_rssi) {
        found = true;
        best_index = profile_index;
        best_rssi = records[i].rssi;
      }
    }
  }

  free(records);

  if (!found) {
    return false;
  }

  if (index_out != NULL) {
    *index_out = best_index;
  }
  if (rssi_out != NULL) {
    *rssi_out = best_rssi;
  }
  return true;
}
#endif

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
    if (app_wifi_profile_count() > 0U && app_wifi_profile_is_valid(s_wifi_profile_index)) {
      size_t visible_index = 0U;
      int visible_rssi = -127;
      if (app_wifi_pick_visible_profile(&visible_index, &visible_rssi, -1)
          && visible_index != s_wifi_profile_index
          && app_wifi_apply_sta_profile(visible_index, true) == ESP_OK) {
        ESP_LOGI(TAG,
                 "STA startup selected visible SSID '%s' (RSSI %d dBm)",
                 s_status.sta_ssid,
                 visible_rssi);
      }
      esp_wifi_connect();
    }
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
    const wifi_event_sta_disconnected_t *event = (const wifi_event_sta_disconnected_t *)event_data;
    const wifi_err_reason_t reason = event != NULL ? event->reason : WIFI_REASON_UNSPECIFIED;
    s_status.sta_connected = false;
    s_status.last_error = ESP_FAIL;
    s_status.sta_ip[0] = '\0';

    if (app_wifi_profile_count() == 0U) {
      return;
    }

    ESP_LOGW(TAG,
             "Station mode: Disconnected from '%s', reason=%s (%d)",
             s_status.sta_ssid[0] != '\0' ? s_status.sta_ssid : "<unknown>",
             app_wifi_disconnect_reason_to_str(reason),
             (int)reason);

    if (app_wifi_disconnect_should_switch_now(reason)) {
      size_t visible_index = 0U;
      int visible_rssi = -127;
      if (app_wifi_pick_visible_profile(&visible_index, &visible_rssi, (int)s_wifi_profile_index)
          && app_wifi_apply_sta_profile(visible_index, true) == ESP_OK) {
        s_wifi_retries = 0;
        ESP_LOGW(TAG,
                 "Switching immediately to visible fallback SSID '%s' (RSSI %d dBm)",
                 s_status.sta_ssid,
                 visible_rssi);
        esp_wifi_connect();
        return;
      }
    }

    if (s_wifi_retries < APP_WIFI_MAX_RETRIES) {
      s_wifi_retries++;
      ESP_LOGW(TAG,
               "connect retry %d/%d for '%s' after %s",
               s_wifi_retries,
               APP_WIFI_MAX_RETRIES,
               s_status.sta_ssid[0] != '\0' ? s_status.sta_ssid : "<unknown>",
               app_wifi_disconnect_reason_to_str(reason));
      esp_wifi_connect();
      return;
    }

    ESP_LOGW(TAG,
             "STA profile '%s' exhausted retries, switching fallback network",
             s_status.sta_ssid[0] != '\0' ? s_status.sta_ssid : "<unknown>");
    s_wifi_retries = 0;

    size_t visible_index = 0U;
    int visible_rssi = -127;
    if (app_wifi_pick_visible_profile(&visible_index, &visible_rssi, (int)s_wifi_profile_index)
        && app_wifi_apply_sta_profile(visible_index, true) == ESP_OK) {
      ESP_LOGW(TAG,
               "Switched to visible fallback SSID '%s' (RSSI %d dBm)",
               s_status.sta_ssid,
               visible_rssi);
      esp_wifi_connect();
      return;
    }

    if (app_wifi_advance_sta_profile()) {
      esp_wifi_connect();
      return;
    }

    esp_wifi_connect();
    return;
  }

  if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
    const ip_event_got_ip_t *event = (const ip_event_got_ip_t *)event_data;
    s_status.sta_connected = true;
    s_status.last_error = ESP_OK;
    s_wifi_retries = 0;
    snprintf(s_status.sta_ip, sizeof(s_status.sta_ip), IPSTR, IP2STR(&event->ip_info.ip));
    ESP_LOGI(TAG,
             "STA ready ssid='%s' ip=" IPSTR,
             s_status.sta_ssid[0] != '\0' ? s_status.sta_ssid : "<unknown>",
             IP2STR(&event->ip_info.ip));
  }
}
#endif

static void app_wifi_event_handler_common(void *arg,
                                          esp_event_base_t event_base,
                                          int32_t event_id,
                                          void *event_data) {
  (void)arg;

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_START) {
    s_status.ap_started = true;
    s_status.last_error = ESP_OK;
    app_wifi_refresh_status_locked();
    ESP_LOGI(TAG,
             "%sAP event: started%s ssid='%s' ip='%s'",
             APP_WIFI_COLOR_OK,
             APP_WIFI_COLOR_RESET,
             s_status.ap_ssid,
             s_status.ap_ip[0] != '\0' ? s_status.ap_ip : "192.168.4.1");
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STOP) {
    s_status.ap_started = false;
    s_status.last_error = ESP_FAIL;
    s_status.ap_ip[0] = '\0';
    ESP_LOGW(TAG, "%sAP event: stopped unexpectedly%s", APP_WIFI_COLOR_WARN, APP_WIFI_COLOR_RESET);
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STACONNECTED) {
    const wifi_event_ap_staconnected_t *event = (const wifi_event_ap_staconnected_t *)event_data;
    ESP_LOGI(TAG,
             "%sAP client joined%s mac=%02X:%02X:%02X:%02X:%02X:%02X aid=%d",
             APP_WIFI_COLOR_AP,
             APP_WIFI_COLOR_RESET,
             event->mac[0],
             event->mac[1],
             event->mac[2],
             event->mac[3],
             event->mac[4],
             event->mac[5],
             event->aid);
    return;
  }

  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STADISCONNECTED) {
    const wifi_event_ap_stadisconnected_t *event = (const wifi_event_ap_stadisconnected_t *)event_data;
    ESP_LOGW(TAG,
             "%sAP client left%s mac=%02X:%02X:%02X:%02X:%02X:%02X aid=%d",
             APP_WIFI_COLOR_WARN,
             APP_WIFI_COLOR_RESET,
             event->mac[0],
             event->mac[1],
             event->mac[2],
             event->mac[3],
             event->mac[4],
             event->mac[5],
             event->aid);
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
#if !(CONFIG_ESP_WIFI_ENABLED || CONFIG_ESP_HOST_WIFI_ENABLED || CONFIG_ESP_WIFI_REMOTE_ENABLED)
  ESP_LOGW(TAG,
           "Wi-Fi stack is not enabled in sdkconfig (enable ESP_WIFI_REMOTE_ENABLED or ESP_HOST_WIFI_ENABLED for ESP32-P4 + C6)");
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

  const wifi_mode_t wifi_mode = app_wifi_pick_mode();
  ESP_ERROR_CHECK(esp_wifi_set_mode(wifi_mode));

  wifi_config_t ap_cfg = {0};
  app_wifi_build_ap_ssid(s_status.ap_ssid, sizeof(s_status.ap_ssid), NULL);
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
  s_wifi_retries = 0;
  s_wifi_profile_index = 0U;
  ESP_LOGI(TAG, "Running AP-only Wi-Fi mode");
#else
  ESP_LOGI(TAG, "Running AP-only Wi-Fi mode");
#endif

  ESP_ERROR_CHECK(esp_wifi_start());
  ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));

  app_wifi_refresh_status_locked();

  ESP_LOGI(TAG,
           "%sAP ready%s ssid='%s' ip='%s' channel=%d auth=%s",
           APP_WIFI_COLOR_OK,
           APP_WIFI_COLOR_RESET,
           s_status.ap_ssid,
           s_status.ap_ip[0] != '\0' ? s_status.ap_ip : "192.168.4.1",
           CONFIG_APP_WIFI_AP_CHANNEL,
           ap_cfg.ap.authmode == WIFI_AUTH_OPEN ? "OPEN" : "WPA2-PSK");

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
  strlcpy(status->sta_ssid, s_status.sta_ssid, sizeof(status->sta_ssid));
  strlcpy(status->sta_ip, s_status.sta_ip, sizeof(status->sta_ip));
}

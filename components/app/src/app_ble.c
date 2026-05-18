#include "app_ble.h"

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "esp_hosted.h"
#include "esp_log.h"
#include "host/ble_gatt.h"
#include "host/ble_hs.h"
#include "host/ble_store.h"
#include "host/ble_uuid.h"
#include "host/util/util.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

#include "app_stepper.h"
#include "app_wifi.h"

static const char *TAG = "app_ble";
static const ble_uuid128_t APP_BLE_SERVICE_UUID =
  BLE_UUID128_INIT(0x32, 0xf7, 0x11, 0x6d, 0x88, 0x3e, 0x49, 0x91,
                   0x8c, 0xe8, 0xd5, 0x6d, 0x50, 0x4a, 0xe1, 0x10);
static const ble_uuid128_t APP_BLE_COMMAND_UUID =
  BLE_UUID128_INIT(0x33, 0xf7, 0x11, 0x6d, 0x88, 0x3e, 0x49, 0x91,
                   0x8c, 0xe8, 0xd5, 0x6d, 0x50, 0x4a, 0xe1, 0x10);
static const ble_uuid128_t APP_BLE_STATUS_UUID =
  BLE_UUID128_INIT(0x34, 0xf7, 0x11, 0x6d, 0x88, 0x3e, 0x49, 0x91,
                   0x8c, 0xe8, 0xd5, 0x6d, 0x50, 0x4a, 0xe1, 0x10);
static const char *APP_BLE_ADV_NAME = "JC-P4-BLE";

#define APP_BLE_STATUS_MAX 192U
#define APP_BLE_NOTIFY_PERIOD_MS 1000U

static app_ble_status_t s_ble = {
  .initialized = false,
  .controller_enabled = false,
  .advertising = false,
  .connected = false,
  .notify_enabled = false,
  .device_name = "JC-ESP32P4M3-BLE",
  .address = "",
  .last_error = "",
};
static uint16_t s_status_handle;
static bool s_nimble_started;
static uint16_t s_conn_handle = BLE_HS_CONN_HANDLE_NONE;
static uint32_t s_last_notify_ms;
static char s_status_payload[APP_BLE_STATUS_MAX];

void ble_store_config_init(void);

static void app_ble_set_error(const char *error);
static void app_ble_build_status_payload(void);
static void app_ble_advertise(void);
static int app_ble_gap_event(struct ble_gap_event *event, void *arg);
static void app_ble_on_sync(void);
static void app_ble_on_reset(int reason);
static void app_ble_host_task(void *param);
static int app_ble_gatt_access(uint16_t conn_handle,
                               uint16_t attr_handle,
                               struct ble_gatt_access_ctxt *ctxt,
                               void *arg);

static const struct ble_gatt_svc_def s_gatt_services[] = {
  {
    .type = BLE_GATT_SVC_TYPE_PRIMARY,
    .uuid = &APP_BLE_SERVICE_UUID.u,
    .characteristics = (struct ble_gatt_chr_def[]) {
      {
        .uuid = &APP_BLE_COMMAND_UUID.u,
        .access_cb = app_ble_gatt_access,
        .flags = BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_NO_RSP,
      },
      {
        .uuid = &APP_BLE_STATUS_UUID.u,
        .access_cb = app_ble_gatt_access,
        .flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY,
        .val_handle = &s_status_handle,
      },
      {0},
    },
  },
  {0},
};

static void app_ble_set_error(const char *error) {
  if (error == NULL || error[0] == '\0') {
    s_ble.last_error[0] = '\0';
    return;
  }

  strlcpy(s_ble.last_error, error, sizeof(s_ble.last_error));
}

static void app_ble_build_status_payload(void) {
  app_stepper_snapshot_t stepper = {0};
  app_stepper_get_snapshot(&stepper);
  app_wifi_status_t wifi = {0};
  app_wifi_get_status(&wifi);
  app_system_status_t system = {0};
  app_get_system_status(&system);

  snprintf(s_status_payload,
           sizeof(s_status_payload),
           "mode=%s;steps=%lu;coils=%s;wifi=%s;ip=%s;uptime=%lu",
           stepper.mode,
           (unsigned long)stepper.total_steps,
           stepper.coils_enabled ? "on" : "off",
           wifi.ap_started ? "ap" : (wifi.sta_connected ? "sta" : "down"),
           wifi.ap_ip[0] != '\0' ? wifi.ap_ip : "0.0.0.0",
           (unsigned long)system.uptime_ms);
}

static void app_ble_advertise(void) {
  struct ble_gap_adv_params adv_params = {0};
  struct ble_hs_adv_fields fields = {0};

  fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
  fields.name = (uint8_t *)APP_BLE_ADV_NAME;
  fields.name_len = strlen(APP_BLE_ADV_NAME);
  fields.name_is_complete = 1;

  int rc = ble_gap_adv_set_fields(&fields);
  if (rc != 0) {
    ESP_LOGE(TAG, "ble_gap_adv_set_fields failed: rc=%d", rc);
    app_ble_set_error("adv_fields_failed");
    return;
  }

  adv_params.conn_mode = BLE_GAP_CONN_MODE_UND;
  adv_params.disc_mode = BLE_GAP_DISC_MODE_GEN;
  rc = ble_gap_adv_start(BLE_OWN_ADDR_PUBLIC,
                         NULL,
                         BLE_HS_FOREVER,
                         &adv_params,
                         app_ble_gap_event,
                         NULL);
  if (rc != 0) {
    ESP_LOGE(TAG, "ble_gap_adv_start failed: rc=%d", rc);
    app_ble_set_error("adv_start_failed");
    s_ble.advertising = false;
    return;
  }

  s_ble.advertising = true;
  app_ble_set_error(NULL);
  ESP_LOGI(TAG, "advertising started as '%s'", s_ble.device_name);
}

static int app_ble_gap_event(struct ble_gap_event *event, void *arg) {
  (void)arg;

  switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
      if (event->connect.status == 0) {
        s_conn_handle = event->connect.conn_handle;
        s_ble.connected = true;
        s_ble.advertising = false;
        ESP_LOGI(TAG, "ble central connected handle=%u", s_conn_handle);
      } else {
        s_ble.connected = false;
        s_conn_handle = BLE_HS_CONN_HANDLE_NONE;
        app_ble_advertise();
      }
      return 0;

    case BLE_GAP_EVENT_DISCONNECT:
      s_ble.connected = false;
      s_ble.notify_enabled = false;
      s_conn_handle = BLE_HS_CONN_HANDLE_NONE;
      ESP_LOGI(TAG, "ble central disconnected reason=%d", event->disconnect.reason);
      app_ble_advertise();
      return 0;

    case BLE_GAP_EVENT_SUBSCRIBE:
      if (event->subscribe.attr_handle == s_status_handle) {
        s_ble.notify_enabled = event->subscribe.cur_notify != 0;
        ESP_LOGI(TAG, "ble notify %s", s_ble.notify_enabled ? "enabled" : "disabled");
      }
      return 0;

    case BLE_GAP_EVENT_ADV_COMPLETE:
      s_ble.advertising = false;
      app_ble_advertise();
      return 0;

    default:
      return 0;
  }
}

static void app_ble_on_sync(void) {
  uint8_t addr_val[6] = {0};
  int rc = ble_hs_util_ensure_addr(0);
  if (rc != 0) {
    ESP_LOGE(TAG, "ble_hs_util_ensure_addr failed: rc=%d", rc);
    app_ble_set_error("addr_ensure_failed");
    return;
  }

  rc = ble_hs_id_copy_addr(BLE_OWN_ADDR_PUBLIC, addr_val, NULL);
  if (rc == 0) {
    snprintf(s_ble.address,
             sizeof(s_ble.address),
             "%02X:%02X:%02X:%02X:%02X:%02X",
             addr_val[5],
             addr_val[4],
             addr_val[3],
             addr_val[2],
             addr_val[1],
             addr_val[0]);
  }

  app_ble_advertise();
}

static void app_ble_on_reset(int reason) {
  ESP_LOGW(TAG, "nimble reset reason=%d", reason);
  s_ble.connected = false;
  s_ble.notify_enabled = false;
  s_ble.advertising = false;
}

static void app_ble_host_task(void *param) {
  (void)param;
  ESP_LOGI(TAG, "nimble host task started");
  nimble_port_run();
  nimble_port_freertos_deinit();
}

static int app_ble_gatt_access(uint16_t conn_handle,
                               uint16_t attr_handle,
                               struct ble_gatt_access_ctxt *ctxt,
                               void *arg) {
  (void)arg;

  if (attr_handle == s_status_handle && ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR) {
    app_ble_build_status_payload();
    int rc = os_mbuf_append(ctxt->om, s_status_payload, strlen(s_status_payload));
    return rc == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
  }

  if (ctxt->op == BLE_GATT_ACCESS_OP_WRITE_CHR) {
    char payload[32] = {0};
    uint16_t len = 0;
    int rc = ble_hs_mbuf_to_flat(ctxt->om, payload, sizeof(payload) - 1U, &len);
    if (rc != 0 || len == 0) {
      return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
    }

    char cmd = 0;
    for (uint16_t i = 0; i < len; i++) {
      if (payload[i] != ' ' && payload[i] != '\r' && payload[i] != '\n' && payload[i] != '\t') {
        cmd = payload[i];
        break;
      }
    }
    if (cmd == 0) {
      return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
    }

    esp_err_t err = app_stepper_command_char(cmd);
    if (err != ESP_OK) {
      app_ble_set_error(esp_err_to_name(err));
      return BLE_ATT_ERR_UNLIKELY;
    }

    app_ble_build_status_payload();
    if (s_ble.notify_enabled && conn_handle != BLE_HS_CONN_HANDLE_NONE) {
      ble_gatts_chr_updated(s_status_handle);
    }
    return 0;
  }

  return BLE_ATT_ERR_UNLIKELY;
}

esp_err_t app_ble_init(void) {
  if (s_ble.initialized) {
    return ESP_OK;
  }

  app_ble_build_status_payload();

  esp_err_t err = esp_hosted_bt_controller_init();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "esp_hosted_bt_controller_init failed: %s", esp_err_to_name(err));
    app_ble_set_error("bt_ctrl_init_failed");
    return err;
  }

  err = esp_hosted_bt_controller_enable();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "esp_hosted_bt_controller_enable failed: %s", esp_err_to_name(err));
    app_ble_set_error("bt_ctrl_enable_failed");
    return err;
  }

  s_ble.controller_enabled = true;
  nimble_port_init();
  ble_svc_gap_init();
  ble_svc_gatt_init();
  ble_svc_gap_device_name_set(s_ble.device_name);
  ble_hs_cfg.reset_cb = app_ble_on_reset;
  ble_hs_cfg.sync_cb = app_ble_on_sync;
  ble_hs_cfg.store_status_cb = ble_store_util_status_rr;

  int rc = ble_gatts_count_cfg(s_gatt_services);
  if (rc != 0) {
    app_ble_set_error("gatt_count_failed");
    return ESP_FAIL;
  }

  rc = ble_gatts_add_svcs(s_gatt_services);
  if (rc != 0) {
    app_ble_set_error("gatt_add_failed");
    return ESP_FAIL;
  }

  ble_store_config_init();
  nimble_port_freertos_init(app_ble_host_task);
  s_nimble_started = true;
  s_ble.initialized = true;
  app_ble_set_error(NULL);
  ESP_LOGI(TAG, "ble bridge initialized");
  return ESP_OK;
}

void app_ble_tick(void) {
  if (!s_nimble_started || !s_ble.notify_enabled || s_conn_handle == BLE_HS_CONN_HANDLE_NONE) {
    return;
  }

  uint32_t now_ms = esp_log_timestamp();
  if ((now_ms - s_last_notify_ms) < APP_BLE_NOTIFY_PERIOD_MS) {
    return;
  }
  s_last_notify_ms = now_ms;

  app_ble_build_status_payload();
  ble_gatts_chr_updated(s_status_handle);
}

void app_ble_get_status(app_ble_status_t *status) {
  if (status == NULL) {
    return;
  }

  *status = s_ble;
}

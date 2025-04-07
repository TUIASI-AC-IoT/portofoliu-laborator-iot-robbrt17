/***************************************************************************//**
 * @file
 * @brief Core application logic.
 *******************************************************************************
 * # License
 * <b>Copyright 2020 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * SPDX-License-Identifier: Zlib
 *
 * The licensor of this software is Silicon Laboratories Inc.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 ******************************************************************************/
#include "em_common.h"
#include "app_assert.h"
#include "sl_bluetooth.h"
#include "app.h"

#include "em_cmu.h"
#include "em_gpio.h"

#include "gatt_db.h"

// The advertising set handle allocated from Bluetooth stack.
static uint8_t advertising_set_handle = 0xff;

bool button_io_notification_enabled;
uint8_t button_state;

void GPIO_ODD_IRQHandler(void)
{
  // Stergere flag intrerupere
  uint32_t interruptMask = GPIO_IntGet();
  GPIO_IntClear(interruptMask);
  button_state = GPIO_PinInGet(gpioPortC, 7);
  sl_bt_gatt_server_write_attribute_value(gattdb_BUTTON_IO, 0, sizeof(button_state), &button_state);
    if (button_io_notification_enabled) {
      sl_bt_gatt_server_notify_all(gattdb_BUTTON_IO, sizeof(button_state), &button_state);
    }
}

/**************************************************************************//**
 * Application Init.
 *****************************************************************************/
SL_WEAK void app_init(void)
{
  /////////////////////////////////////////////////////////////////////////////
  // Put your additional application init code here!                         //
  // This is called once during start-up.                                    //
  /////////////////////////////////////////////////////////////////////////////

  // Activare ramura clock periferic GPIO
  CMU_ClockEnable(cmuClock_GPIO, true);
  // Configurare GPIOA 04 ca iesire (LED)
  GPIO_PinModeSet(gpioPortA, 4, gpioModePushPull, 1);
  // Configurare GPIOC 07 ca intrare (buton)
  GPIO_PinModeSet(gpioPortC, 7, gpioModeInputPullFilter, 1);
  // Configurare intrerupere pentru buton pe ambele fronturi
  GPIO_ExtIntConfig(gpioPortC, 7, 7,true, true, true);
  // Activare intrerupere
  NVIC_ClearPendingIRQ(GPIO_ODD_IRQn);
  NVIC_EnableIRQ(GPIO_ODD_IRQn);

}



/**************************************************************************//**
 * Application Process Action.
 *****************************************************************************/
SL_WEAK void app_process_action(void)
{
  /////////////////////////////////////////////////////////////////////////////
  // Put your additional application code here!                              //
  // This is called infinitely.                                              //
  // Do not call blocking functions from here!                               //
  /////////////////////////////////////////////////////////////////////////////

}

/**************************************************************************//**
 * Bluetooth stack event handler.
 * This overrides the dummy weak implementation.
 *
 * @param[in] evt Event coming from the Bluetooth stack.
 *****************************************************************************/
void sl_bt_on_event(sl_bt_msg_t *evt)
{
  sl_status_t sc;
  uint8_t recv_val;
  size_t recv_len;
//  bool button_io_notification_enabled;

  switch (SL_BT_MSG_ID(evt->header)) {
    // -------------------------------
    // This event indicates the device has started and the radio is ready.
    // Do not call any stack command before receiving this boot event!
    case sl_bt_evt_system_boot_id:
      // Create an advertising set.
      sc = sl_bt_advertiser_create_set(&advertising_set_handle);
      app_assert_status(sc);

      // Generate data for advertising
      sc = sl_bt_legacy_advertiser_generate_data(advertising_set_handle,
                                                 sl_bt_advertiser_general_discoverable);
      app_assert_status(sc);

      // Set advertising interval to 100ms.
      sc = sl_bt_advertiser_set_timing(
        advertising_set_handle,
        160, // min. adv. interval (milliseconds * 1.6)
        160, // max. adv. interval (milliseconds * 1.6)
        0,   // adv. duration
        0);  // max. num. adv. events
      app_assert_status(sc);
      // Start advertising and enable connections.
      sc = sl_bt_legacy_advertiser_start(advertising_set_handle,
                                         sl_bt_advertiser_connectable_scannable);
      app_assert_status(sc);
      break;

    // -------------------------------
    // This event indicates that a new connection was opened.
    case sl_bt_evt_connection_opened_id:
      break;

    // -------------------------------
    // This event indicates that a connection was closed.
    case sl_bt_evt_connection_closed_id:
      // Generate data for advertising
      sc = sl_bt_legacy_advertiser_generate_data(advertising_set_handle,
                                                 sl_bt_advertiser_general_discoverable);
      app_assert_status(sc);

      // Restart advertising after client has disconnected.
      sc = sl_bt_legacy_advertiser_start(advertising_set_handle,
                                         sl_bt_advertiser_connectable_scannable);
      app_assert_status(sc);
      break;

    ///////////////////////////////////////////////////////////////////////////
    // Add additional event handlers here as your application requires!      //
    ///////////////////////////////////////////////////////////////////////////
    ///
    /// La scrierea caracteristicii LED cu o valoare diferit˘a de zero, LED-ul va fi aprins, iar la scrierea valorii 0, LED-ul va fi stins.

    case sl_bt_evt_gatt_server_attribute_value_id:

      if (gattdb_LED_IO == evt->data.evt_gatt_server_characteristic_status.characteristic) {
        sl_bt_gatt_server_read_attribute_value(gattdb_LED_IO, 0, sizeof(recv_val), &recv_len, &recv_val);
        if (recv_val) {
            GPIO_PinOutSet(gpioPortA, 4);
            app_log("LED ON\r\n");
        }
        else {
            GPIO_PinOutClear(gpioPortA, 4);
            app_log("LED ON\r\n");
        }
        app_log("LED= %d\r\n", recv_val);
      }
      break;

    case sl_bt_evt_gatt_server_characteristic_status_id:
      if (gattdb_BUTTON_IO == evt->data.evt_gatt_server_characteristic_status.characteristic) {
        if (evt->data.evt_gatt_server_characteristic_status.client_config_flags & sl_bt_gatt_notification) {
          app_log("Notificare activata pentru caracteristica BUTTON\r\n");
          // Setare flag care va fi folosit in logica aplicatiei
          // pentru generarea de notificari
          button_io_notification_enabled = true;
        }
        else {
          app_log("Notificare dezactivata pentru caracteristica BUTTON\r\n");
          // Resetare flag
          button_io_notification_enabled = false;
        }
      }
    break;

    // -------------------------------
    // Default event handler.
    default:
      break;
  }
}

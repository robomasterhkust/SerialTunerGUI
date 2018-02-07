/**
 * Edward ZHANG
 * @file    shellcfg.c
 * @brief   definitions of shell command functions
 */
#include "main.h"
#include "shell.h"
#include <string.h>

#define SHELL_USE_USB

#if !defined(SHELL_USE_USB)
  #define SHELL_SERIAL_UART &SD3

  static const SerialConfig shell_serial_conf = {
  115200,               //Baud Rate
  0,         //CR1 Register
  0,      //CR2 Register
  0                     //CR3 Register
};
#endif

/**
 * @brief array of shell commands, put the corresponding command and functions below
 * {"command", callback_function}
 */
static const ShellCommand commands[] =
{
  #ifdef PARAMS_USE_USB
    {"\xFD",cmd_param_scale},
    {"\xFB",cmd_param_update},
    {"\xFA",cmd_param_tx},
    {"\xF9",cmd_param_rx},
  #endif
  {NULL, NULL}
};

static const ShellConfig shell_cfg1 =
{
  (BaseSequentialStream *)&SDU1,
  commands
};

/**
 * @brief start the shell service
 * @require enable the corresponding serial ports in mcuconf.h and board.h
 *          Select the SERIAL_CMD port in main.h
 *
 * @api
 */
void shellStart(void)
{
  /*
   * Initializes a serial-over-USB CDC driver.
   */
  #ifdef SHELL_USE_USB
    sduObjectInit(&SDU1);
    sduStart(&SDU1, &serusbcfg);

  /*
   * Activates the USB driver and then the USB bus pull-up on D+.
   * Note, a delay is inserted in order to not have to disconnect the cable
   * after a reset.
   */


   usbDisconnectBus(serusbcfg.usbp);
   chThdSleepMilliseconds(1500);

   usbStart(serusbcfg.usbp, &usbcfg);
   usbConnectBus(serusbcfg.usbp);
  #else
    sdStart(SHELL_SERIAL_UART, shell_serial_conf);
  #endif

  shellInit();

  shellCreateStatic(&shell_cfg1, Shell_thread_wa,
      sizeof(Shell_thread_wa), NORMALPRIO);

}

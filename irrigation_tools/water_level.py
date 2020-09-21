import gc
import utime
from micropython import schedule
import uasyncio as asyncio
import logging
from machine import Pin
from irrigation_tools import smartthings_handler, libraries
from irrigation_tools.conf import WATER_LEVEL_SENSOR_PIN

_logger = logging.getLogger("water level")


#class WaterLevel:
#    def __init__(self, pin, callback=None, debounce_ms=5000, falling=True):
#        self.last_time_ms = 0
#        self.callback = callback
#        self.debounce_ms = debounce_ms
#        pin.irq(handler=self._irq_cb, trigger=Pin.IRQ_FALLING if falling else Pin.IRQ_RISING)
#
#    def _irq_cb(self, pin):
#        t = utime.ticks_ms()
#        diff = t - self.last_time_ms
#        if abs(diff) < self.debounce_ms:
#            return
#        self.last_time_ms = t
#        if self.callback:
#            self.callback(pin)
#
#
#async def confirm_int(pin):
#    global irq_state
#
#    trigger_state = pin.value()
#    await asyncio.sleep(2)
#    current_state = pin.value()
#
#    if current_state == trigger_state:
#        _logger.info("Confirmed interruption - {}: {}".format(pin, current_state))
#        st_conf = libraries.get_smartthings_configuration()
#        smartthings = smartthings_handler.SmartThings(st_ip=st_conf["st_ip"], st_port=st_conf["st_port"])
#        try:
#            if current_state == "empty":
#                libraries.stop_all_pumps()
#
#            payload = {
#                "type": "water_level_status",
#                "body": {
#                    "status": get_watter_level(current_state)
#                }
#            }
#            smartthings.notify(payload)
#
#        except Exception as e:
#            _logger.exc(e, "Fail to confirm the interruption")
#        finally:
#            gc.collect()
#    else:
#        _logger.info("False interruption")
#        gc.collect()
#
#
#def water_level_interruption_function(pin):
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(confirm_int(pin))
#
#
#def water_level_interruption_handler(pin):
#    _logger.info("interruption has been triggered - {}: {}".format(pin, pin.value()))
#    schedule(water_level_interruption_function, pin)


def get_watter_level(value=None):
    if not value:
        value = libraries.read_gpio(WATER_LEVEL_SENSOR_PIN)
    return "empty" if value else "good"

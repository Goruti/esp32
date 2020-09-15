import utime
import micropython
import gc
import sys
import logging
import uasyncio as asyncio
from irrigation_tools import smartthings_handler, libraries, conf

_logger = logging.getLogger("Irrigation")

lo
class WaterLevel:
    def __init__(self, pin, callback=None, debounce_ms=5000, falling=True):
        self.last_time_ms = 0
        self.callback = callback
        self.debounce_ms = debounce_ms
        pin.irq(handler=self._irq_cb, trigger=pin.IRQ_FALLING if falling else pin.IRQ_RISING)

    def _irq_cb(self, pin):
        t = utime.ticks_ms()
        diff = t - self.last_time_ms
        if abs(diff) < self.debounce_ms:
            return
        self.last_time_ms = t
        if self.callback:
            self.callback(pin)


def water_level_interruption_function(pin):
    #loop = asyncio.get_event_loop()

    value = pin.value()
    #utime.sleep(5)
    #if pin.value() != value:
    _logger.info("Confirmed interruption - {}: {}".format(pin, value))
    st_conf = libraries.get_smartthings_configuration()
    smartthings = smartthings_handler.SmartThings(st_ip=st_conf["st_ip"], st_port=st_conf["st_port"])
    try:
        if value:
            libraries.stop_all_pumps()
        #irrigation_config = manage_data.get_irrigation_config()
        #irrigation_config.update({"water_level": "empty"})
        #manage_data.save_irrigation_config(**irrigation_config)

        payload = {
            "type": "water_level_status",
            "body": {
                "status": get_watter_level(value)
            }
        }
        smartthings.notify(payload)

    except Exception as e:
        _logger.exc(e, "Fail to confirm the interruption")
    finally:
        gc.collect()


def water_level_interruption_handler(pin):
    #value = pin.value()
    _logger.info("interruption has been triggered - {}: {}".format(pin, pin.value()))
    #utime.sleep(5)
    #if pin.value() == value:
    micropython.schedule(water_level_interruption_function, pin)


def get_watter_level(value=None):
    if not value:
        value = libraries.read_gpio(conf.WATER_LEVEL_SENSOR_PIN)
    return "empty" if value else "good"

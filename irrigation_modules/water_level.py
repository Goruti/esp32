import utime
import micropython
import gc
import sys

from irrigation_tools.libraries import stop_all_pumps
from irrigation_tools import smartthings_handler


class WaterLevel:
    def __init__(self, pin, callback=None, debounce_ms=1000, falling=True):
        self.last_time_ms = 0
        self.callback = callback
        self.debounce_ms = debounce_ms
        pin.irq(handler=self._irq_cb, trigger=pin.IRQ_FALLING if falling else pin.IRQ_RISING)

    def _irq_cb(self, pin):
        t = utime.ticks_ms()
        if abs(utime.ticks_diff(t, self.last_time_ms)) < self.debounce_ms:
            return
        self.last_time_ms = t
        if self.callback:
            self.callback(pin)


def water_level_interruption_function(pin):
    print("interruption has been triggered - {}: {}".format(pin, pin.value()))
    smartthings = smartthings_handler.SmartThings()
    try:
        if not pin.value():
            stop_all_pumps()
        #irrigation_config = manage_data.get_irrigation_config()
        #irrigation_config.update({"water_level": "empty"})
        #manage_data.save_irrigation_config(**irrigation_config)

        payload = {
            "type": "water_level_status",
            "body": {
                "status": "empty" if pin.value() else "good"
            }
        }
        # smartthings.notify(payload})
        print(payload)

    except Exception as e:
        sys.print_exception(e)
    finally:
        gc.collect()


def water_level_interruption_handler(pin):
    #state = machine.disable_irq()
    micropython.schedule(water_level_interruption_function, pin)
    #machine.enable_irq(state)
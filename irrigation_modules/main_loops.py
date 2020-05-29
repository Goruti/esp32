import utime
import uasyncio as asyncio
import gc
import sys

from irrigation_tools import wifi, libraries, conf, manage_data


async def initialize_rtc(frequency_loop=3600):
    while True:
        try:
            if wifi.is_connected():
                try:
                    from ntptime import settime
                    settime()
                    print("DateTime(UTC): {}".format(libraries.datetime_to_iso(utime.localtime())))
                except Exception as e:
                    print("Failed to initialize RTC: Error: {}".format(e))
            else:
                print("Device is Offline")
        except BaseException as e:
            sys.print_exception(e)
        finally:
            gc.collect()
            await asyncio.sleep(frequency_loop)


async def reading_moister(frequency_loop=3600):
    while True:
        systems_info = manage_data.get_irrigation_config()
        try:
            for key, values in systems_info["pump_info"].items():
                moisture = libraries.read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))

                if moisture > values["moisture_threshold"]:
                    libraries.start_irrigation(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump"),\
                                               conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"),\
                                               moisture,\
                                               values["moisture_threshold"])
        except BaseException as e:
            sys.print_exception(e)
        finally:
            gc.collect()
            await asyncio.sleep(frequency_loop)
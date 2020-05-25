import machine
import utime
import uasyncio as asyncio
import gc

from irrigation_tools.wifi import is_connected
from irrigation_tools.libraries import datetime_to_iso


async def initialize_rtc(frequency_loop=3600):
    while True:
        try:
            if is_connected():
                try:
                    from ntptime import settime
                    settime()
                    print("DateTime(UTC): {}".format(datetime_to_iso(utime.localtime())))
                except Exception as e:
                    print("Failed to initialize RTC: Error: {}".format(e))
            else:
                print("Device is Offline")
        except Exception as e:
            pass
        finally:
            gc.collect()
            await asyncio.sleep(frequency_loop)


async def reading_process(frequency_loop=3600):
    pin = machine.Pin(2, machine.Pin.OUT)
    # adc_objects = [{"pin": moisture_sensor, "adc_object": adc}]
    while True:
        #for moisture_sensor in adc_objects:
        #    moisture = moisture_sensor["adc_object"].read()
        #    if moisture > conf.sensor_pump_relation[moisture_sensor["pin"]]["moisture_threshold"]:
        #        pass

        utime.sleep(1)
        pin(1)
        utime.sleep(1)
        #print("{}-off".format("light_sensor"))
        pin(0)
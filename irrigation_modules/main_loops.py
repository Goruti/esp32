import utime
import uasyncio as asyncio
import gc
import sys

from irrigation_tools import wifi, libraries, conf, manage_data, smartthings_handler


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


async def reading_moister(frequency_loop=300, report_freq_s=600):
    try:
        smartthings = smartthings_handler.SmartThings()
        systems_info = libraries.get_irrigation_configuration()
    except BaseException as e:
        sys.print_exception(e)
        gc.collect()
    else:
        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            t = utime.time()
            while True:
                try:
                    moisture_status = {}
                    for key, values in systems_info["pump_info"].items():
                        moisture = libraries.read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                        moisture_status[values["connected_to_port"]] = moisture
                        if moisture > values["moisture_threshold"]:
                            libraries.start_irrigation(pump_pin=conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump"),
                                                       sensor_pin=conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"),
                                                       moisture=moisture,
                                                       threshold=values["moisture_threshold"],
                                                       max_irrigation_time_s=10)

                    if utime.ticks_diff(utime.time(), t) >= report_freq_s:
                        t = utime.time()
                        payload = {
                            "type": "moisture_status",
                            "body": moisture_status
                        }
                        print(payload)
                        # smartthings.notify(payload)

                except BaseException as e:
                    print("reading_moister Exception - key: {}, values: {}".format(key, values))
                    sys.print_exception(e)
                finally:
                    gc.collect()
                    await asyncio.sleep(frequency_loop)


#async def reading_water_level(frequency_loop=3600):
#    previous_water_level = "empty"
#    smartthings = smartthings_handler.SmartThings()
#    while True:
#        try:
#            water_level = "empty" if libraries.read_gpio(conf.WATER_LEVEL_SENSOR_PIN) else "good"
#            if water_level != previous_water_level:
#                payload = {
#                    "type": "water_level_status",
#                    "body": {
#                        "status": water_level
#                    }
#                }
#                # smartthings.notify(payload})
#                print(payload)
#                previous_water_level = water_level
#
#        except BaseException as e:
#            sys.print_exception(e)
#        finally:
#            gc.collect()
#            await asyncio.sleep(frequency_loop)
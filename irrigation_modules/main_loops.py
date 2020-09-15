import utime
import uasyncio as asyncio
import gc
import logging
from irrigation_tools import wifi, libraries, conf, manage_data, smartthings_handler

_logger = logging.getLogger("Irrigation")


async def initialize_rtc(frequency_loop=3600):
    while True:
        gc.collect()
        try:
            if wifi.is_connected():
                try:
                    from ntptime import settime
                    settime()
                    _logger.debug("DateTime(UTC): {}".format(libraries.datetime_to_iso(utime.localtime())))
                except Exception as e:
                    _logger.exc(e, "Fail to set time")
            else:
                _logger.info("Device is Offline")
        except BaseException as e:
            _logger.exc(e, "Fail to Initialize RTC")
        finally:
            gc.collect()
            await asyncio.sleep(frequency_loop)


async def reading_moister(frequency_loop_ms=300000, report_freq_ms=1800000):
    try:
        systems_info = libraries.get_irrigation_configuration()
    except BaseException as e:
        _logger.exc(e, "Fail to Read Systems Information RTC")
        manage_data.save_irrigation_state(**{"running": False})
        gc.collect()
    else:
        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            report_time = -1*report_freq_ms
            while True:
                gc.collect()
                try:
                    moisture_status = {}
                    for key, values in systems_info["pump_info"].items():
                        moisture = libraries.read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                        moisture_status[values["connected_to_port"]] = moisture
                        if moisture > values["moisture_threshold"]:
                            libraries.start_irrigation(
                                                    port=values["connected_to_port"],
                                                    moisture=moisture,
                                                    threshold=values["moisture_threshold"],
                                                    max_irrigation_time_ms=10000
                                            )

                    if utime.ticks_diff(utime.ticks_ms(), report_time) > 0:
                        report_time = utime.ticks_add(utime.ticks_ms(), report_freq_ms)
                        payload = {
                            "type": "moisture_status",
                            "body": moisture_status
                        }
                        libraries.notify_st(payload)

                except BaseException as e:
                    _logger.exc(e, "Fail to get current Moisture status")
                finally:
                    gc.collect()
                    await asyncio.sleep_ms(frequency_loop_ms)


#async def reading_water_level(frequency_loop=3600):
#    previous_water_level = "empty"
#    st_conf = libraries.get_smartthings_configuration()
#    smartthings = smartthings_handler.SmartThings(st_ip=st_conf["st_ip"], st_port=st_conf["st_port"])
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
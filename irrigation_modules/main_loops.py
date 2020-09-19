import gc
import utime
import uasyncio as asyncio
import logging
from irrigation_tools import wifi, libraries, conf, manage_data

_logger= logging.getLogger("Irrigation")


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
                    pass
            else:
                _logger.info("Device is Offline")
                pass
        except BaseException as e:
            _logger.exc(e, "Fail to Initialize RTC")
            pass
        finally:
            gc.collect()
            await asyncio.sleep(frequency_loop)


async def reading_moister(frequency_loop_ms=300000, report_freq_ms=1800000):
    _logger.debug("Start Reading Moister Loop")
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
                    _logger.debug("reading_moister - inside while true")
                    moisture_status = {}
                    for key, values in systems_info["pump_info"].items():
                        _logger.debug("reading_moister - evaluating port: {}".format(values["connected_to_port"]))

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
                    _logger.debug("moisture_status: {}".format(moisture_status))
                    gc.collect()
                    await asyncio.sleep_ms(frequency_loop_ms)

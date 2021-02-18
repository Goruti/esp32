import gc
import utime
import uasyncio as asyncio
import logging
from machine import Pin, reset
from irrigation_tools import libraries
from irrigation_tools.wifi import is_connected
from irrigation_tools.conf import PORT_PIN_MAPPING, WATER_LEVEL_SENSOR_PIN
from irrigation_tools.manage_data import save_irrigation_state
gc.collect()

_logger = logging.getLogger("main loops")


async def initialize_rtc(frequency_loop=3600):
    while True:
        gc.collect()
        try:
            if is_connected():
                try:
                    from ntptime import settime
                    settime()
                    _logger.debug("DateTime(UTC): {}".format(libraries.datetime_to_iso(utime.localtime())))
                except Exception as e:
                    _logger.exc(e, "Fail to set time")
            else:
                _logger.info("Device is Offline")
                _logger.info("restarting the system")
                reset()

        except BaseException as e:
            _logger.exc(e, "Fail to Initialize RTC")
        finally:
            gc.collect()
            await asyncio.sleep(frequency_loop)


async def reading_moister(frequency_loop_ms=300000, report_freq_ms=1800000):
    _logger.debug("Start Reading Moister Loop")
    try:
        systems_info = libraries.get_irrigation_configuration()
        st = libraries.get_st_handler(retry_num=5, retry_sec=1)
    except BaseException as e:
        _logger.exc(e, "Fail to Read Systems Information RTC")
        save_irrigation_state(**{"running": False})
        gc.collect()
    else:
        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            report_time = -1*report_freq_ms
            while True:
                gc.collect()
                try:
                    _logger.debug("reading_moister - Start a new reading")
                    moisture_status = {}
                    for key, values in systems_info["pump_info"].items():
                        #_logger.debug("reading_moister - evaluating port: {}".format(values["connected_to_port"]))

                        moisture = libraries.read_adc(PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                        #moisture_status[values["connected_to_port"]] = libraries.moisture_to_hum(values["connected_to_port"], moisture)
                        moisture_status[values["connected_to_port"]] = moisture
                        if moisture > values["moisture_threshold"]:
                            libraries.start_irrigation(
                                                    port=values["connected_to_port"],
                                                    moisture=moisture,
                                                    threshold=values["moisture_threshold"],
                                                    max_irrigation_time_ms=7000
                                            )

                    if st and utime.ticks_diff(utime.ticks_ms(), report_time) > 0:
                        report_time = utime.ticks_add(utime.ticks_ms(), report_freq_ms)
                        payload = {
                            "type": "moisture_status",
                            "body": moisture_status
                        }
                        _logger.info("Notifying SmartThings ")
                        st.notify(payload)

                except BaseException as e:
                    _logger.exc(e, "Fail to get current Moisture status")
                finally:
                    _logger.info("moisture_status: {}".format(moisture_status))
                    gc.collect()
                    await asyncio.sleep_ms(frequency_loop_ms)


async def wait_pin_change(pin, bounces=5):
    # wait for pin to change value
    # it needs to be stable for a continuous 5sec
    cur_value = pin.value()
    active = 0
    while active < bounces:
        if pin.value() != cur_value:
            active += 1
        else:
            active = 0
        await asyncio.sleep(1)


async def reading_water_level():
    pin = Pin(WATER_LEVEL_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
    st = libraries.get_st_handler(retry_num=5, retry_sec=1)
    while True:
        try:
            await wait_pin_change(pin)
            w_level = libraries.get_watter_level(pin.value())
            if w_level == "empty":
                libraries.stop_all_pumps()
            if st:
                payload = {
                    "type": "water_level_status",
                    "body": {
                        "status": w_level
                    }
                }
                st.notify(payload)

        except BaseException as e:
            _logger.exc(e, "failed to read water level")
        finally:
            gc.collect()

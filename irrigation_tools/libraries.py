# from machine import Pin, ADC
import machine
import micropython
import utime
import gc
import sys
import webrepl
import os
import uio
import logging
from logging.handlers import RotatingFileHandler
from collections import OrderedDict

from irrigation_tools import manage_data, conf, water_level, smartthings_handler
from irrigation_tools.wifi import is_connected, get_mac_address

micropython.alloc_emergency_exception_buf(100)
_logger = logging.getLogger("Irrigation")


def get_net_configuration():
    try:
        ip = is_connected()
        if ip:
            data = {"connected": True, "ssid": manage_data.get_network_config().get('ssid', {}), "ip": ip}
        else:
            data = {"connected": False, "ssid": None, "ip": None}
        data["mac"] = get_mac_address()
    except Exception as e:
        data = {"connected": False, "ssid": None, "ip": None, "mac": None}
    finally:
        gc.collect()
        return data


def get_irrigation_configuration():
    try:
        conf = manage_data.read_irrigation_config()
        if not conf:
            conf = {
                "total_pumps": 0,
                "pump_info": {},
                "water_level": None
            }
    except Exception as e:
        conf = {
            "total_pumps": 0,
            "pump_info": {},
            "water_level": None
        }
    finally:
        gc.collect()
        return conf


def get_web_repl_configuration():
    try:
        conf = manage_data.read_webrepl_config()
        if not conf:
            conf = {
                "enabled": False
            }
    except Exception as e:
        conf = {
            "enabled": False
        }
    finally:
        gc.collect()
        return conf


def get_smartthings_configuration():
    try:
        conf = manage_data.read_smartthings_config()
        if not conf or not conf["enabled"]:
            conf = {
                "enabled": False,
                "st_ip": None,
                "st_port": None
            }
    except Exception as e:
        conf = {
            "enabled": False,
            "st_ip": None,
            "st_port": None
        }
    finally:
        gc.collect()
        return conf


def get_irrigation_status():
    systems_info = get_irrigation_configuration()

    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = "On" if read_gpio(
                conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump")) else "Off"
            moisture = read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
            systems_info["pump_info"][key]["moisture"] = moisture
            systems_info["pump_info"][key]["humidity"] = moisture_to_hum(values["connected_to_port"], moisture)
            systems_info["pump_info"][key]["threshold_pct"] = moisture_to_hum(values["connected_to_port"], values["moisture_threshold"])

    systems_info["water_level"] = water_level.get_watter_level()
    gc.collect()
    return systems_info


def moisture_to_hum(port, moisture):
    try:
        dry = conf.PORT_PIN_MAPPING.get(port).get("dry_value")
        wet = conf.PORT_PIN_MAPPING.get(port).get("water_value")
        if moisture >= dry:
            hum = 0.0
        elif moisture <= wet:
            hum = 100.0
        else:
            hum = 100*((moisture-dry)/(wet-dry))
    except Exception as e:
        hum = -1.0
    finally:
        gc.collect()
        return round(hum, 1)


def start_irrigation(port, moisture, threshold, max_irrigation_time_ms=15000):
    pump_pin = conf.PORT_PIN_MAPPING.get(port).get("pin_pump"),
    sensor_pin = conf.PORT_PIN_MAPPING.get(port).get("pin_sensor"),

    started = start_pump(pump_pin)
    if started:
        payload = {
            "type": "pump_status",
            "body": {
                port: "on"
            }
        }
        notify_st(payload, retry_num=1, retry_sec=1)

        t = utime.ticks_ms()
        while ((moisture > threshold * 0.9 and abs(utime.ticks_diff(utime.ticks_ms(), t)) < max_irrigation_time_ms)
                or
                (abs(utime.ticks_diff(utime.ticks_ms(), t)) < 5000)):
            moisture = read_adc(sensor_pin)
            utime.sleep_ms(100)
        if started:
            stop_pump(pump_pin)
            payload = {
                "type": "pump_status",
                "body": {
                    port: "off"
                }
            }
            notify_st(payload, retry_num=1, retry_sec=1)


def read_gpio(pin):
    gc.collect()
    return machine.Pin(pin).value()


def read_adc(pin):
    adc = machine.ADC(machine.Pin(pin))  # create ADC object on ADC pin
    adc.atten(machine.ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.3v)
    adc.width(machine.ADC.WIDTH_12BIT)
    read = 0
    for i in range(0, 8):
        read += adc.read()
        utime.sleep_ms(10)

    gc.collect()
    return int(read / 8)
    #return adc.read()


def initialize_irrigation_app():
    _logger.info("Initializing Ports")
    try:
        #  Initialize Water Sensor as IN_PUT and set low water interruption
        pir = machine.Pin(conf.WATER_LEVEL_SENSOR_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        # pir.irq(handler=water_level.water_level_interruption_handler, trigger=pir.IRQ_FALLING | pir.IRQ_RISING)
        # high_water_level = water_level.WaterLevel(pin=pir, callback=water_level.water_level_interruption_handler, falling=True)
        low_water_level = water_level.WaterLevel(pin=pir, callback=water_level.water_level_interruption_handler,
                                                 falling=False)

        for key, value in conf.PORT_PIN_MAPPING.items():
            #  Initialize Pumps pin as OUT_PUTS
            machine.Pin(value["pin_pump"], machine.Pin.OUT, value=0)

        #  TODO (uncomment the following line)
        # webrepl.stop()
        # manage_data.save_webrepl_config(**{"enabled": False})

        #  TODO (Comment the following line)
        webrepl.start(password=conf.WEBREPL_PWD)
        manage_data.save_webrepl_config(**{"enabled": True})

        manage_data.save_irrigation_state(**{"running": True})

    except Exception as e:
        manage_data.save_irrigation_state(**{"running": False})
        #save_last_error(e)
        _logger.exc(e, "Cannot initialize Irrigation APP")
        raise RuntimeError("Cannot initialize Irrigation APP: error: {}".format(e))
    finally:
        gc.collect()


def start_pump(pin):
    started = False
    try:
        if water_level.get_watter_level() != "empty":
            _logger.info("Starting pump: {}".format(pin))
            machine.Pin(pin).on()
            started = True
        else:
            _logger.info("cannot start pump {} since tank is empty".format(pin))
            gc.collect()
    except Exception as e:
        _logger.exc(e, "Failed Starting Pump")
    finally:
        gc.collect()
        return started


def stop_pump(pin):
    try:
        _logger.info("Stopping pump: {}".format(pin))
        machine.Pin(pin).off()
    except Exception as e:
        _logger.exc(e, "Failed Stopping Pump")
    finally:
        gc.collect()


def stop_all_pumps():
    try:
        _logger.info("Stopping all pumps")
        for key, value in conf.PORT_PIN_MAPPING.items():
            stop_pump(value["pin_pump"])
    except Exception as e:
        _logger.exc(e, "Failed Stopping ALL Pump. It will stop the whole application")
        manage_data.save_irrigation_state(**{"running": False})
        sys.exit()
    finally:
        gc.collect()


def test_irrigation_system():
    try:
        systems_info = get_irrigation_configuration()

        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            systems_info["pump_info"] = OrderedDict(sorted(systems_info["pump_info"].items(), key=lambda t: t[0]))
            for key, values in systems_info["pump_info"].items():
                _logger.exc("testing port {}".format(values["connected_to_port"]))
                moisture = read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                _logger.exc("moisture_port_{}: {}".format(values["connected_to_port"], moisture))
                if start_pump(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump")):
                    utime.sleep(4)
                    stop_pump(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump"))
    except BaseException as e:
        _logger.exc(e, "Failed Test Irrigation System")
    finally:
        gc.collect()


def notify_st(body, retry_sec=5, retry_num=1):
    try:
        st_conf = get_smartthings_configuration()
        smartthings = smartthings_handler.SmartThings(st_ip=st_conf["st_ip"],
                                                      st_port=st_conf["st_port"],
                                                      retry_sec=retry_sec,
                                                      retry_num=retry_num)
        smartthings.notify(body)
    except Exception as e:
        _logger.exc(e, "Failed Notify ST")
    finally:
        gc.collect()


def save_last_error(error):
    try:
        body = {
            "error": error,
            "ts": datetime_to_iso(utime.localtime())
        }
        manage_data.save_last_error(**body)
    except Exception as e:
        _logger.exc(e, "Failed Save Last Error")
    finally:
        gc.collect()


def get_irrigation_state():
    try:
        state = manage_data.read_irrigation_state()
        if not state:
            state = {
                "running": None
            }
    except Exception as e:
        _logger.exc(e, "Failed Getting Irrigation State")
        state = {
            "running": None
        }
    finally:
        gc.collect()
        return state


def get_last_error():
    try:
        last_error = manage_data.read_last_error()
        if not last_error:
            last_error = {
                "error": None,
                "ts": None
            }
    except Exception as e:
        _logger.exc(e, "Failed Getting last Error")
        last_error = {
            "error": None,
            "ts": None
        }
    finally:
        gc.collect()
        return last_error


def initialize_loggers(level):
    try:
        _logger = logging.getLogger("Irrigation")
        _logger.setLevel(level)
        fmt = logging.Formatter("%(asctime)s,%(name)s,%(levelname)s,%(message)s")

        if conf.LOG_DIR not in os.listdir():
            os.mkdir(conf.LOG_DIR)
        rfh = RotatingFileHandler("{}/{}".format(conf.LOG_DIR, conf.LOG_FILENAME), maxBytes=5*1024, backupCount=2)
        rfh.setFormatter(fmt)
        _logger.addHandler(rfh)

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        _logger.addHandler(sh)
    except Exception as e:
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        raise RuntimeError("Cannot Initialize loggers.\nError: {}".format(buf.getvalue()))
    else:
        return _logger
    finally:
        gc.collect()


def datetime_to_iso(time):
    return "{}-{}-{}T{}:{}:{}".format(time[0], time[1], time[2], time[3], time[4], time[5])

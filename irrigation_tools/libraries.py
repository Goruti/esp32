import gc
import machine
import utime
import sys
import uos
import uio
import logging
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
from irrigation_tools import manage_data, smartthings_handler, libraries
from irrigation_tools import conf as mod_conf
from irrigation_tools.wifi import is_connected, get_mac_address

_logger = logging.getLogger("libraries")


def get_net_configuration():
    gc.collect()
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
    gc.collect()
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
    gc.collect()
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
    gc.collect()
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
    gc.collect()
    systems_info = get_irrigation_configuration()

    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = "on" if read_gpio(
                mod_conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump")) else "off"
            moisture = read_adc(mod_conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
            systems_info["pump_info"][key]["moisture"] = moisture
            systems_info["pump_info"][key]["humidity"] = moisture_to_hum(values["connected_to_port"], moisture)
            systems_info["pump_info"][key]["threshold_pct"] = moisture_to_hum(values["connected_to_port"], values["moisture_threshold"])

    systems_info["water_level"] = libraries.get_watter_level()
    gc.collect()
    return systems_info


def moisture_to_hum(port, moisture):
    gc.collect()
    try:
        dry = mod_conf.PORT_PIN_MAPPING.get(port).get("dry_value")
        wet = mod_conf.PORT_PIN_MAPPING.get(port).get("water_value")
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
    gc.collect()
    sensor_pin = mod_conf.PORT_PIN_MAPPING.get(port).get("pin_sensor"),
    started = start_pump(port)
    if started:
        t = utime.ticks_ms()
        while ((moisture > threshold * 0.9 and abs(utime.ticks_diff(utime.ticks_ms(), t)) < max_irrigation_time_ms)
                or
                (abs(utime.ticks_diff(utime.ticks_ms(), t)) < 5000)):
            moisture = read_adc(sensor_pin)
            utime.sleep_ms(100)

        stop_pump(port)


def read_gpio(pin):
    gc.collect()
    return machine.Pin(pin).value()


def read_adc(pin):
    gc.collect()
    adc = machine.ADC(machine.Pin(pin))  # create ADC object on ADC pin
    adc.atten(machine.ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.3v)
    adc.width(machine.ADC.WIDTH_12BIT)
    read = 0
    for i in range(0, 8):
        read += adc.read()
        utime.sleep_ms(10)

    gc.collect()
    return int(read / 8)


def initialize_irrigation_app():
    gc.collect()
    _logger.info("Initializing Ports")
    try:
        for key, value in mod_conf.PORT_PIN_MAPPING.items():
            #  Initialize Pumps pin as OUT_PUTS
            machine.Pin(value["pin_pump"], machine.Pin.OUT, value=0)

        #  TODO (uncomment the following line)
        # webrepl.stop()
        # manage_data.save_webrepl_config(**{"enabled": False})

        #  TODO (Comment the following line)
        import webrepl
        webrepl.start(password=mod_conf.WEBREPL_PWD)
        manage_data.save_webrepl_config(**{"enabled": True})
        manage_data.save_irrigation_state(**{"running": True})

    except Exception as e:
        manage_data.save_irrigation_state(**{"running": False})
        _logger.exc(e, "Cannot initialize Irrigation APP")
        raise RuntimeError("Cannot initialize Irrigation APP: error: {}".format(e))
    finally:
        gc.collect()


def start_pump(port, notify=True):
    gc.collect()
    started = False
    pin = mod_conf.PORT_PIN_MAPPING.get(port).get("pin_pump")
    try:
        if libraries.get_watter_level() != "empty":
            _logger.info("Starting Port {} in Pin: {}".format(port, pin))
            machine.Pin(pin).on()
            started = True
            if notify:
                payload = {"type": "pump_status", "body": {port: "on"}}
                notify_st(payload, retry_num=1, retry_sec=1)
        else:
            _logger.info("cannot start pump {} since tank is empty".format(port))
            gc.collect()
    except Exception as e:
        _logger.exc(e, "Failed Starting Pump")
    finally:
        gc.collect()
        return started


def stop_pump(port, notify=True):
    gc.collect()
    pin = mod_conf.PORT_PIN_MAPPING.get(port).get("pin_pump")
    try:
        _logger.info("Stopping Port {} in Pin {}".format(port, pin))
        if machine.Pin(pin).value():
            machine.Pin(pin).off()
            if notify:
                payload = {"type": "pump_status", "body": {port: "off"}}
                notify_st(payload, retry_num=1, retry_sec=1)
    except Exception as e:
        _logger.exc(e, "Failed Stopping Pump")
    finally:
        gc.collect()


def stop_all_pumps():
    gc.collect()
    try:
        _logger.info("Stopping all pumps")
        for key, value in mod_conf.PORT_PIN_MAPPING.items():
            stop_pump(key)
    except Exception as e:
        _logger.exc(e, "Failed Stopping ALL Pump. It will stop the whole application")
    finally:
        gc.collect()


def test_irrigation_system():
    gc.collect()
    try:
        systems_info = get_irrigation_configuration()

        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            systems_info["pump_info"] = OrderedDict(sorted(systems_info["pump_info"].items(), key=lambda t: t[0]))
            for key, values in systems_info["pump_info"].items():
                _logger.info("testing port {}".format(values["connected_to_port"]))
                moisture = read_adc(mod_conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                _logger.info("moisture_port_{}: {}".format(values["connected_to_port"], moisture))
                if start_pump(values["connected_to_port"], notify=False):
                    utime.sleep(4)
                    stop_pump(values["connected_to_port"], notify=False)
    except BaseException as e:
        _logger.exc(e, "Failed Test Irrigation System")
    finally:
        gc.collect()


def notify_st(body, retry_sec=5, retry_num=1):
    gc.collect()
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


def get_irrigation_state():
    gc.collect()
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


def get_log_files_names():
    gc.collect()
    files = []
    try:
        files = uos.listdir(mod_conf.LOG_DIR)
    except Exception as e:
        _logger.exc(e, "cannot get the log files name")
    finally:
        gc.collect()
        return files


def initialize_root_logger(level):
    gc.collect()
    try:
        logging.basicConfig(level=level)

        _logger = logging.getLogger()
        rfh = RotatingFileHandler("{}/{}".format(mod_conf.LOG_DIR, mod_conf.LOG_FILENAME), maxBytes=10*1024, backupCount=3)
        _logger.addHandler(rfh)

    except Exception as e:
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        raise RuntimeError("Cannot Initialize loggers.\nError: {}".format(buf.getvalue()))
    finally:
        gc.collect()


def mount_sd_card():
    gc.collect()
    if mod_conf.SD_MOUNTING and str(mod_conf.SD_MOUNTING) != "":
        try:
            sd = machine.SDCard(slot=2, freq=80000000)
        except Exception:
            raise
        finally:
            gc.collect()

        try:
            uos.mount(sd, "/{}".format(mod_conf.SD_MOUNTING))
        except Exception as e:
            sd.deinit()
            buf = uio.StringIO()
            sys.print_exception(e, buf)
            raise RuntimeError("Cannot Mount SD Card.\nError: {}".format(buf.getvalue()))
        finally:
            gc.collect()


def get_watter_level(value=None):
    if not value:
        value = read_gpio(mod_conf.WATER_LEVEL_SENSOR_PIN)
    return "empty" if value else "good"


def datetime_to_iso(time):
    gc.collect()
    return "{}-{}-{}T{}:{}:{}".format(*time)

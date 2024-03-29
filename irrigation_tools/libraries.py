import gc
import machine
import utime
import sys
import uos
import uio
import logging
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
from irrigation_tools import manage_data, smartthings_handler
from irrigation_tools.conf import PORT_PIN_MAPPING, LOG_DIR, SD_MOUNTING, WATER_LEVEL_SENSOR_PIN
from irrigation_tools.wifi import is_connected, get_mac_address
gc.collect()

_logger = logging.getLogger("libraries")


def get_irrigation_status():
    gc.collect()
    systems_info = get_irrigation_configuration()

    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = "on" if read_gpio(
                PORT_PIN_MAPPING.get(values["connected_to_port"], {}).get("pin_pump")) else "off"
            moisture = read_adc(PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
            systems_info["pump_info"][key]["moisture"] = moisture
            systems_info["pump_info"][key]["humidity"] = moisture_to_hum(values["connected_to_port"], moisture)
            systems_info["pump_info"][key]["threshold_pct"] = moisture_to_hum(values["connected_to_port"], values["moisture_threshold"])

    systems_info["water_level"] = get_watter_level()
    gc.collect()
    return systems_info


def moisture_to_hum(port, moisture):
    gc.collect()
    try:
        dry = PORT_PIN_MAPPING.get(port).get("dry_value")
        wet = PORT_PIN_MAPPING.get(port).get("water_value")
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


def start_irrigation(port, moisture, threshold, max_irrigation_time_ms=2000):
    gc.collect()
    _logger.info("Starting irrigation on Port {}".format(port))
    sensor_pin = PORT_PIN_MAPPING.get(port).get("pin_sensor")
    started = start_pump(port=port, notify=False)
    if started:
        t = utime.ticks_ms()
        while moisture > threshold * 0.9 and abs(utime.ticks_diff(utime.ticks_ms(), t)) < max_irrigation_time_ms:
            moisture = read_adc(sensor_pin)
            utime.sleep_ms(100)

        stop_pump(port=port, notify=False)

    st = get_st_handler(retry_num=1, retry_sec=1)
    if st:
        payload = {
            "type": "moisture_status",
            "body": {port: moisture_to_hum(port, moisture)}
        }
    st.notify(payload)



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
    st_payload = []
    try:
        for key, value in PORT_PIN_MAPPING.items():
            #  Initialize Pumps pin as OUT_PUTS
            machine.Pin(value["pin_pump"], machine.Pin.OUT, value=0)
            st_payload.append({"type": "pump_status", "body": {key: "off"}})

        #  TODO (uncomment the following line)
        import webrepl
        webrepl.stop()
        manage_data.save_webrepl_config(**{"enabled": False})
        #  TODO (Comment the following line)
        #import webrepl
        #webrepl.start(password=WEBREPL_PWD)
        #manage_data.save_webrepl_config(**{"enabled": True})

        # initialize Water Tank Level
        pin = machine.Pin(WATER_LEVEL_SENSOR_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        w_level = get_watter_level(pin.value())
        st_payload.append({
            "type": "water_level_status",
            "body": {
                "status": w_level
            }
        })
        st = get_st_handler(retry_num=5, retry_sec=1)
        if st:
            st.notify(st_payload)

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
    pin = PORT_PIN_MAPPING.get(port).get("pin_pump")
    try:
        if get_watter_level() != "empty":
            _logger.info("Starting Port {} in Pin: {}".format(port, pin))
            machine.Pin(pin).on()
            started = True
            if notify:
                st = get_st_handler(retry_num=1, retry_sec=1)
                if st:
                    payload = {"type": "pump_status", "body": {port: "on"}}
                    st.notify([payload])
        else:
            _logger.info("cannot start 'pump {}' since tank is empty".format(port))
    except Exception as e:
        _logger.exc(e, "Failed Starting Pump")
    finally:
        gc.collect()
        return started


def stop_pump(port, notify=True):
    gc.collect()
    pin = PORT_PIN_MAPPING.get(port).get("pin_pump")
    try:
        _logger.info("Stopping Port {} in Pin {}".format(port, pin))
        machine.Pin(pin).off()
        if notify:
            st = get_st_handler(retry_num=1, retry_sec=1)
            if st:
                payload = [{"type": "pump_status", "body": {port: "off"}}]
                st.notify(payload)

    except Exception as e:
        _logger.exc(e, "Failed Stopping Pump")
    finally:
        gc.collect()


def stop_all_pumps():
    gc.collect()
    try:
        _logger.info("Stopping all pumps")
        for key, value in PORT_PIN_MAPPING.items():
            stop_pump(key)
    except Exception as e:
        _logger.exc(e, "Failed Stopping ALL Pump")
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
                moisture = read_adc(PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                _logger.info("moisture_port_{}: {}".format(values["connected_to_port"], moisture))
                if start_pump(values["connected_to_port"], notify=False):
                    utime.sleep(4)
                    stop_pump(values["connected_to_port"], notify=False)
    except BaseException as e:
        _logger.exc(e, "Failed Test Irrigation System")
    finally:
        gc.collect()


def get_st_handler(retry_sec=1, retry_num=1):
    gc.collect()
    smartthings = None
    try:
        st_conf = get_smartthings_configuration()
        if st_conf.get("enabled"):
            smartthings = smartthings_handler.SmartThings(st_ip=st_conf.get("st_ip"),
                                                          st_port=st_conf.get("st_port"),
                                                          retry_sec=retry_sec,
                                                          retry_num=retry_num)
    except Exception as e:
        _logger.exc(e, "Failed to get ST handler")
    finally:
        gc.collect()
        return smartthings


def get_net_configuration():
    gc.collect()
    data = {"connected": False, "ssid": None, "ip": None, "mac": None}
    try:
        ip = is_connected()
        if ip:
            data.update({"connected": True, "ssid": manage_data.get_network_config().get('ssid', {}), "ip": ip})
        data.update({"mac": get_mac_address()})
    except Exception as e:
        _logger.exc(e, "Failed to get Network Configuration")
    finally:
        gc.collect()
        return data


def get_irrigation_configuration():
    gc.collect()
    conf = {
        "total_pumps": 0,
        "pump_info": {},
        "water_level": None
    }
    try:
        storage_conf = manage_data.read_irrigation_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get Irrigation configuration")
    finally:
        gc.collect()
        return conf


def get_web_repl_configuration():
    gc.collect()
    conf = {
        "enabled": False
    }
    try:
        storage_conf = manage_data.read_webrepl_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get webrepl configuration")
    finally:
        gc.collect()
        return conf


def get_smartthings_configuration():
    gc.collect()
    conf = {
        "enabled": False,
        "st_ip": None,
        "st_port": None
    }
    try:
        storage_conf = manage_data.read_smartthings_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get ST configuration")
    finally:
        gc.collect()
        return conf


def get_irrigation_state():
    gc.collect()
    state = {
        "running": None
    }
    try:
        storage_conf = manage_data.read_irrigation_state()
        if storage_conf:
            state.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed Getting Irrigation State")
    finally:
        gc.collect()
        return state


def get_log_files_names():
    gc.collect()
    files = []
    try:
        files = uos.listdir(LOG_DIR)
    except Exception as e:
        _logger.exc(e, "cannot get the log files name")
    finally:
        gc.collect()
        return files


def get_logs_files_info():
    gc.collect()
    files_info = []
    try:
        files = get_log_files_names()
    except Exception as e:
        _logger.exc(e, "Cannot get the logs files")

    if files:
        for file in files:
            try:
                with open("{}/{}".format(LOG_DIR, file), "r") as f:
                    ts_from = f.readline().split(",")[0]
                    for line in f:
                        pass
                    ts_to = line.split(",")[0]
                    files_info.append({
                        "file_name": file,
                        "ts_from": ts_from,
                        "ts_to": ts_to
                    })
            except Exception as e:
                _logger.exc(e, "Cannot read file '{}'".format(file))

    gc.collect()
    return files_info


def initialize_root_logger(level, logfile=None):
    gc.collect()
    try:
        logging.basicConfig(level=level)
        _logger = logging.getLogger()
        if logfile:
            rfh = RotatingFileHandler(logfile, maxBytes=10*1024, backupCount=5)
            _logger.addHandler(rfh)

    except Exception as e:
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        raise RuntimeError("Cannot Initialize loggers.\nError: {}".format(buf.getvalue()))
    finally:
        gc.collect()


def unmount_sd_card():
    if SD_MOUNTING and str(SD_MOUNTING) != "" and SD_MOUNTING in uos.listdir():
        uos.umount(SD_MOUNTING)


def mount_sd_card():
    gc.collect()
    if SD_MOUNTING and str(SD_MOUNTING) != "":
        try:
            sd = machine.SDCard(slot=2, freq=80000000)
        except Exception as e:
            buf = uio.StringIO()
            sys.print_exception(e, buf)
            print("Cannot Crete SDCard Object.\nError: {}".format(buf.getvalue()))

        try:
            uos.mount(sd, "/{}".format(SD_MOUNTING))
        except Exception as e:
            sd.deinit()
            buf = uio.StringIO()
            sys.print_exception(e, buf)
            print("Cannot Mount SD Card.\nError: {}".format(buf.getvalue()))
    gc.collect()


def get_watter_level(value=None):
    try:
        if not value:
            value = read_gpio(WATER_LEVEL_SENSOR_PIN)
    except Exception as e:
        _logger.exc(e, "Cannot read tank level")
        value = 1
    return "empty" if value else "good"


def datetime_to_iso(time):
    gc.collect()
    return "{}-{}-{}T{}:{}:{}".format(*time)

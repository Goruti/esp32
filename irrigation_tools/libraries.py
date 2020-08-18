from machine import Pin, ADC
import micropython
import utime
import gc
import sys

from irrigation_tools import manage_data, conf
from irrigation_tools.wifi import is_connected

micropython.alloc_emergency_exception_buf(100)


def get_net_configuration():
    ip = is_connected()
    if ip:
        data = {"connected": True, "ssid": manage_data.get_network_config().get('ssid', {}), "ip": ip}
    else:
        data = {"connected": False, "ssid": None, "ip": None}

    gc.collect()
    return data


def get_irrigation_configuration():
    conf = manage_data.read_irrigation_config()
    if not conf:
        conf = {
            "total_pumps": 0,
            "pump_info": {},
            "water_level": None,
            "WebRepl": False
        }
    gc.collect()
    return conf


def get_irrigation_status():
    systems_info = get_irrigation_configuration()

    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = "On" if read_gpio(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump")) else "Off"
            systems_info["pump_info"][key]["moisture"] = read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))

    systems_info["water_level"] = "good" if not read_gpio(conf.WATER_LEVEL_SENSOR_PIN) else "empty"
    gc.collect()
    return systems_info


def start_irrigation(pump_pin, sensor_pin, moisture, threshold, max_irrigation_time_s=10):
    start_pump(pump_pin)
    t = utime.time()
    while moisture > threshold and utime.ticks_diff(utime.time(), t) < max_irrigation_time_s:
        moisture = read_adc(sensor_pin)
    stop_pump(pump_pin)


def read_gpio(pin):
    gc.collect()
    return Pin(pin).value()


def read_adc(pin):
    adc = ADC(Pin(pin))  # create ADC object on ADC pin
    adc.atten(ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    read = 0
    for i in range(0, 5):
        read += adc.read()
        utime.sleep_ms(1)

    gc.collect()
    return read / 5


def initialize_irrigation_app():
    print("Initializing Ports")
    try:
        #  Initialize Water Sensor as IN_PUT and set low water interruption
        pir = Pin(conf.WATER_LEVEL_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        pir.irq(trigger=Pin.IRQ_FALLING, handler=water_level_interruption)

        for key, value in conf.PORT_PIN_MAPPING.items():
            #  Initialize Pumps pin as OUT_PUTS
            Pin(value["pin_pump"], Pin.OUT, value=1)

    except Exception as e:
        raise RuntimeError("Cannot initialize Irrigation APP: error: {}".format(e))


def water_level_interruption(pin):
    print("interruption has been triggered - {}: {}".format(pin, pin.value()))
    try:
        stop_all_pumps()
        irrigation_config = manage_data.get_irrigation_config()
        irrigation_config.update({"water_level": "empty"})
        manage_data.save_irrigation_config(**irrigation_config)
    except Exception as e:
        sys.print_exception(e)
    finally:
        gc.collect()


def start_pump(pin):
    print("starting pump: {}".format(pin))
    try:
        if read_gpio(conf.WATER_LEVEL_SENSOR_PIN):
            Pin(pin).off()
    except Exception as e:
        sys.print_exception(e)
    finally:
        gc.collect()


def stop_pump(pin):
    print("Stopping pump: {}".format(pin))
    try:
        Pin(pin).on()
    except Exception as e:
        sys.print_exception(e)
    gc.collect()


def stop_all_pumps():
    print("stopping all pumps")
    try:
        for key, value in conf.PORT_PIN_MAPPING.items():
            stop_pump(value["pin_pump"])
    except Exception as e:
        sys.print_exception(e)
        sys.exit()
    gc.collect()


def datetime_to_iso(time):
    return "{}-{}-{}T{}:{}:{}".format(time[0], time[1], time[2], time[3], time[4], time[5])




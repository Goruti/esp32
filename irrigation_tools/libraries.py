# from machine import Pin, ADC
import machine
import micropython
import utime
import gc
import sys
import webrepl
from collections import OrderedDict
import uasyncio as asyncio

from irrigation_tools import manage_data, conf, water_level
from irrigation_tools.wifi import is_connected, get_mac_address

micropython.alloc_emergency_exception_buf(100)


def get_net_configuration():
    ip = is_connected()
    if ip:
        data = {"connected": True, "ssid": manage_data.get_network_config().get('ssid', {}), "ip": ip}
    else:
        data = {"connected": False, "ssid": None, "ip": None}
    data["mac"] = get_mac_address()

    gc.collect()
    return data


def get_irrigation_configuration():
    conf = manage_data.read_irrigation_config()
    if not conf:
        conf = {
            "total_pumps": 0,
            "pump_info": {},
            "water_level": None
        }
    gc.collect()
    return conf


def get_web_repl_configuration():
    conf = manage_data.read_webrepl_config()
    if not conf:
        conf = {
            "enabled": False
        }
    gc.collect()
    return conf


def get_smartthings_configuration():
    conf = manage_data.read_smartthings_config()
    if not conf:
        conf = {
            "enabled": False
        }
    gc.collect()
    return conf


def get_irrigation_status():
    systems_info = get_irrigation_configuration()

    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = "On" if read_gpio(
                conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump")) else "Off"
            systems_info["pump_info"][key]["moisture"] = read_adc(
                conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))

    systems_info["water_level"] = water_level.get_watter_level()
    gc.collect()
    return systems_info


async def start_irrigation(pump_pin, sensor_pin, moisture, threshold, max_irrigation_time_ms=15000):
    started = start_pump(pump_pin)
    t = utime.ticks_ms()
    while started and (
            (moisture > threshold * 0.9 and abs(utime.ticks_diff(utime.ticks_ms(), t)) < max_irrigation_time_ms)
            or
            (abs(utime.ticks_diff(utime.ticks_ms(), t)) < 5000)):
        moisture = read_adc(sensor_pin)
        await asyncio.sleep(1)
    if started:
        stop_pump(pump_pin)


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
    print("Initializing Ports")
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
        # manage_data.save_webrepl_config(**{"enable": False})

        #  TODO (Comment the following line)
        webrepl.start(password=conf.WEBREPL_PWD)
        manage_data.save_webrepl_config(**{"enable": True})

    except Exception as e:
        raise RuntimeError("Cannot initialize Irrigation APP: error: {}".format(e))


def start_pump(pin):
    started = False
    try:
        if water_level.get_watter_level() != "empty":
            print("{} - Starting pump: {}".format(datetime_to_iso(utime.localtime()), pin))
            machine.Pin(pin).on()
            started = True
        else:
            print("{} - cannot start pump {} since tank is empty".format(datetime_to_iso(utime.localtime()), pin))
            gc.collect()
    except Exception as e:
        sys.print_exception(e)
    finally:
        gc.collect()
        return started


def stop_pump(pin):
    try:
        print("{} - Stopping pump: {}".format(datetime_to_iso(utime.localtime()), pin))
        machine.Pin(pin).off()
    except Exception as e:
        sys.print_exception(e)
    gc.collect()


def stop_all_pumps():
    try:
        print("{} - Stopping all pumps".format(datetime_to_iso(utime.localtime())))
        for key, value in conf.PORT_PIN_MAPPING.items():
            stop_pump(value["pin_pump"])
    except Exception as e:
        sys.print_exception(e)
        sys.exit()
    gc.collect()


def test_irrigation_system():
    try:
        systems_info = get_irrigation_configuration()

        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            systems_info["pump_info"] = OrderedDict(sorted(systems_info["pump_info"].items(), key=lambda t: t[0]))
            for key, values in systems_info["pump_info"].items():
                print("testing port {}".format(values["connected_to_port"]))
                moisture = read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                print("moisture_port_{}: {}".format(values["connected_to_port"], moisture))
                if start_pump(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump")):
                    utime.sleep(4)
                    stop_pump(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump"))
    except BaseException as e:
        sys.print_exception(e)
    finally:
        gc.collect()


def datetime_to_iso(time):
    return "{}-{}-{}T{}:{}:{}".format(time[0], time[1], time[2], time[3], time[4], time[5])

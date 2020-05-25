from machine import Pin, ADC, PWM
import micropython
import utime
import gc


from irrigation_tools import manage_data, conf
from irrigation_tools.wifi import is_connected

#micropython.alloc_emergency_exception_buf(100)

'''
def init_adc_and_outputs(): ## TODO
    adc_objects = []
    for pin, info in conf.sensor_pump_relation.items():
        try:
            adc = ADC(Pin(pin))  # create ADC object on ADC pin
            adc.atten(ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)

        except Exception as e:
            print("Failed to init ADC for pin '{}': Error: {}".format(moisture_sensor, e))
        else:
            adc_objects.append({"pin": moisture_sensor, "adc_object": adc})

    if not adc_objects:
        raise Exception('System Could not initialize any ADC for PINs: {}'.format(conf.sensor_pump_relation.keys()))
    return adc_objects
'''


def get_net_configuration():
    ip = is_connected()
    if ip:
        data = {"connected": True, "ssid": manage_data.get_network_config().get('ssid', {}), "ip": ip}
    else:
        data = {"connected": False, "ssid": None, "ip": None}

    gc.collect()
    return data


def get_irrigation_configuration():
    conf = manage_data.get_irrigation_config()
    if not conf:
        conf = {
            "total_pumps": 0,
            "pump_info": {}
        }
    gc.collect()
    return conf


def get_irrigation_status():
    systems_info = manage_data.get_irrigation_config()
    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = read_gpio(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_pump"))
            systems_info["pump_info"][key]["moisture"] = read_adc(conf.PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
    else:
        systems_info = {}

    systems_info["water_level"] = read_gpio(conf.WATER_LEVEL_SENSOR_PIN)

    gc.collect()
    return systems_info


def read_gpio(pin):
    gc.collect()
    return Pin(pin).value()


def read_adc(pin):
    '''adc = ADC(Pin(pin))  # create ADC object on ADC pin
    adc.atten(ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    read = 0
    for i in range(0, 5):
        read += adc.read()
        utime.sleep_ms(1)
    '''
    read = 4
    gc.collect()
    return read / 5


def initialize_irrigation_app():
    try:
        #  set low water interruption pin
        pir = Pin(conf.WATER_LEVEL_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        pir.irq(trigger=3, handler=water_level_interruption)

        #  set pumps pin as OUT_PUTS
        #for key, value in manage_data.get_irrigation_config()["pump_info"].items():

    except Exception as e:
        raise RuntimeError("Cannot initialize Irrigation APP: error: {}".format(e))


def water_level_interruption(irq):
    irrigation_config = manage_data.get_irrigation_config()
    utime.sleep(3)

    if Pin(conf.WATER_LEVEL_SENSOR_PIN).value():
        stop_pumps(irrigation_config["pump_info"])
        irrigation_config.update({"water_level": "empty"})
        manage_data.save_irrigation_config(**irrigation_config)
    else:
        irrigation_config.update({"water_level": "ok"})
        manage_data.save_irrigation_config(**irrigation_config)


def stop_pumps(pump_info):
    try:
        for key, value in pump_info.items():
            PWM(Pin(value["pin_pump"])).deinit()
            Pin(value["pin_pump"], Pin.OUT)(0)
    except Exception as e:
        print("Enable to stop Pumps. Exception: {}".format(e))
    gc.collect()


def datetime_to_iso(time):
    return "{}-{}-{}T{}:{}:{}".format(time[0], time[1], time[2], time[3], time[4], time[5])




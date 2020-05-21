from machine import Pin, ADC, PWM
import micropython
import utime
import gc
import uasyncio as asyncio

from irrigation_modules import wifi
from irrigation_modules import manage_data
from irrigation_modules import conf

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
    ip = wifi.is_connected()
    if not ip:
        data = {"connected": False, "ssid": None, "ip": None}
    else:
        data = {"connected": True, "ssid": manage_data.get_network_config().get('ssid', {}), "ip": ip}

    gc.collect()
    return data


def get_irrigation_status():
    systems_info = manage_data.get_irrigation_config()
    for key, values in systems_info["pump_info"].items():
        systems_info["pump_info"][key]["pump_status"] = read_port(values["pin_pump"])
        systems_info["pump_info"][key]["moisture"] = read_port(values["pin_sensor"], type="ADC")

    systems_info["water_level"] = read_port(conf.water_level_sensor_pin)

    gc.collect()
    return systems_info


def read_port(pin, type="GPIO"):

    if type == "GPIO_ADC":
        adc = ADC(Pin(pin))  # create ADC object on ADC pin
        adc.atten(ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
        read = 0
        for i in range(0, 5):
            read += adc.read()
            utime.sleep_ms(1)

        gc.collect()
        return read/5

    else:
        gc.collect()
        return Pin(pin).value()


def load_irrigation_configuration():
    #  set low water interruption pin
    pir = Pin(conf.water_level_sensor_pin, Pin.IN, Pin.PULL_UP)
    pir.irq(trigger=3, handler=water_level_interruption)

    #  set pumps pin as OUT_PUTS
    #for key, value in manage_data.get_irrigation_config()["pump_info"].items():


def water_level_interruption(irq):
    irrigation_config = manage_data.get_irrigation_config()
    utime.sleep(3)

    if Pin(conf.water_level_sensor_pin).value():
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


def get_irrigation_configuration():
    conf = manage_data.get_irrigation_config()
    gc.collect()
    return conf


async def initialize_rtc():
    while True:
        try:
            if wifi.is_connected():
                try:
                    from ntptime import settime
                    settime()
                    print("DateTime(UTC): {}".format(datetime_to_iso(utime.localtime())))
                except Exception as e:
                    print("Failed to initialize RTC: Error: {}".format(e))
            else:
                print("Device is Offline")
        except Exception as e:
            pass
        finally:
            gc.collect()
            await asyncio.sleep(3600)


def datetime_to_iso(time):
    return "{}-{}-{}T{}:{}:{}".format(time[0], time[1], time[2], time[3], time[4], time[5])




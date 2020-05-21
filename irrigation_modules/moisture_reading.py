import machine
import utime

def reading_process(adc_objects):
    pin = machine.Pin(2, machine.Pin.OUT)
    # adc_objects = [{"pin": moisture_sensor, "adc_object": adc}]
    while True:
        #for moisture_sensor in adc_objects:
        #    moisture = moisture_sensor["adc_object"].read()
        #    if moisture > conf.sensor_pump_relation[moisture_sensor["pin"]]["moisture_threshold"]:
        #        pass

        utime.sleep(1)
        pin(1)
        utime.sleep(1)
        #print("{}-off".format("light_sensor"))
        pin(0)
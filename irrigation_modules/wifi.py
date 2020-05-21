from network import WLAN, AP_IF, STA_IF
import machine
import gc
import utime

from irrigation_modules import manage_data


def is_connected():
    """
    Check if the WLAN is connected to a network.
    : if it's connected return the IP address
    : else None
    """
    ip_address = None
    wlan = WLAN(STA_IF)
    if wlan.active() and wlan.isconnected():
        details = wlan.ifconfig()
        ip_address = details[0] if details else None

    gc.collect()
    return ip_address


def start_ap():
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    ap = WLAN(AP_IF)
    ap.active(True)
    ap.config(essid='IrrigationSystem')
    ip = ap.ifconfig()[0]
    print("AP is ON. Please connect to 'IrrigationSystem' network. AP_GW: {}".format(ip))
    gc.collect()
    return {"ssid": 'IrrigationSystem', "ip": ip}


def stop_ap():
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    ap = WLAN(AP_IF)
    ap.active(False)
    print("AP is OFF")
    gc.collect()


def get_available_networks(wlan=None):
    if not wlan:
        wlan = WLAN(STA_IF)

    nets = [e[0].decode("utf-8") for e in wlan.scan()]
    print("Scanning wifi nets")
    if not nets:
        wlan.active(False)
        utime.sleep(2)
        wlan.active(True)
        utime.sleep(2)
        print("Re-scanning wifi nets")
        nets = [e[0].decode("utf-8") for e in wlan.scan()]

    gc.collect()
    return nets


def wifi_connect(network_config=None, re_config=False):
    """
    Connect to the WiFi network based on the configuration. Fails silently if there is no configuration.
    """
    if not network_config:
        network_config = manage_data.get_network_config()
        #network_config = {"ssid": "Mateo's Kingdom", "password": "Di3g0&C@rl@&M@t30"}

    if not network_config:
        gc.collect()
        raise Exception("There is not Network Configuration")

    try:
        wlan = WLAN(STA_IF)
        if re_config:
            wlan.active(False)
            utime.sleep(1)

        if not wlan.active():
            wlan.active(True)
            utime.sleep(2)

        nets = get_available_networks(wlan)

        if network_config["ssid"] in nets:
            wlan.connect(network_config["ssid"], network_config["password"])
            attempts = 150000
            while not wlan.isconnected():
                attempts -= 1
                if not attempts:
                    raise Exception("Reached the maximum (150000) number of attempts to connect to Wifi")
                machine.idle()
            print("Connected to {} with IP address: {}".format(network_config["ssid"], wlan.ifconfig()[0]))
            #  Disable AP since the device is already connected
            # stop_ap()
        else:
            raise Exception("Could not find network: {}".format(network_config["ssid"]))

    except Exception as e:
        print("Failed to connect to  '{}' network. \nError: {}".format(network_config["ssid"], e))
        raise

    finally:
        gc.collect()

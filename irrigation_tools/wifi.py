from network import WLAN, AP_IF, STA_IF
import machine
import gc
import utime


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


def start_ap(essid_name="ESP32 AP"):
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    ap = WLAN(AP_IF)
    if not ap.active():
        ap.config(essid=essid_name)
        ap.active(True)

    ip = ap.ifconfig()[0]
    essid = ap.config('essid')
    print("AP is ON. Please connect to '{}' network. AP_GW: {}".format(essid, ip))
    gc.collect()
    return {"ssid": essid, "ip": ip}


def stop_ap():
    """
    Stop WiFi Access Point
    """
    ap = WLAN(AP_IF)
    if ap.active():
        ap.active(False)
    print("AP is OFF")
    gc.collect()


def get_available_networks():
    wlan = WLAN(STA_IF)
    if not wlan.active():
        wlan.active(True)
        utime.sleep(2)
    print("Scanning wifi nets")
    nets = [e[0].decode("utf-8") for e in wlan.scan()]
    gc.collect()
    return nets


def wifi_connect(network_config=None):
    """
    Connect to the WiFi network based on the configuration. Fails if there is no configuration.
    """
    if not network_config:
        gc.collect()
        raise ValueError("Network Configuration was not provided")

    try:
        nets = get_available_networks()
        if network_config["ssid"] in nets:
            wlan = WLAN(STA_IF)
            wlan.connect(network_config["ssid"], network_config["password"])
            attempts = 150000
            while not wlan.isconnected():
                attempts -= 1
                if not attempts:
                    raise RuntimeError("Reached the maximum (150000) number of attempts to connect to Wifi")
                machine.idle()
            print("Connected to {} with IP address: {}".format(network_config["ssid"], wlan.ifconfig()[0]))
        else:
            raise RuntimeError("Could not find network: {}".format(network_config["ssid"]))

    except Exception as e:
        print("Failed to connect to  '{}' network. \nError: {}".format(network_config["ssid"], e))
        raise

    finally:
        gc.collect()

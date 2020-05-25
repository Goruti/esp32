#from network import WLAN, AP_IF, STA_IF
import network
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
    wlan = network.WLAN(network.STA_IF)
    if wlan.active() and wlan.isconnected():
        details = wlan.ifconfig()
        ip_address = details[0] if details else None

    gc.collect()
    return ip_address


def start_ap(essid_name="ESP32 AP"):
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    ap = network.WLAN(network.AP_IF)
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
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        ap.active(False)
    print("AP is OFF")
    gc.collect()


def get_available_networks():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
        utime.sleep(2)
    print("Scanning wifi nets")
    nets = [e[0].decode("utf-8") for e in wlan.scan()]
    gc.collect()
    return nets


def wifi_connect(network_config=None, timeout=10000):
    """
    Connect to the WiFi network based on the configuration. Fails if there is no configuration.
    """
    if not network_config:
        gc.collect()
        raise ValueError("Network Configuration was not provided")

    try:
        wlan = network.WLAN(network.STA_IF)

        if not wlan.isconnected():
            if not wlan.active():
                wlan.active(True)
                utime.sleep(1)

            wlan.connect(str(network_config["ssid"]), str(network_config["password"]))
            t = utime.ticks_ms()
            while not wlan.isconnected():
                if utime.ticks_diff(utime.ticks_ms(), t) > timeout:
                    wlan.disconnect()
                    utime.sleep_ms(100)
                    wlan_status = wlan.status()
                    if wlan_status == network.STAT_NO_AP_FOUND:
                        error_msg = "STAT_NO_AP_FOUND"
                    elif wlan_status == network.STAT_WRONG_PASSWORD or wlan_status == 8:
                        error_msg = "STAT_WRONG_PASSWORD"
                    elif wlan_status == network.STAT_ASSOC_FAIL:
                        error_msg = "STAT_ASSOC_FAIL"
                    elif wlan_status == network.STAT_HANDSHAKE_TIMEOUT:
                        error_msg = "HANDSHAKE_TIMEOUT"
                    else:
                        error_msg = "Undefined Error"
                    raise RuntimeError("Timeout. Could not connect to Wifi. Error: {}, Message: {}".format(wlan_status, error_msg))
                machine.idle()
            print("Connected to {} with IP address: {}".format(wlan.config("essid"), wlan.ifconfig()[0]))
        else:
            print("Device is already connected to {} with IP address: {}".format(wlan.config("essid"), wlan.ifconfig()[0]))

    except Exception as e:
        print("Failed to connect to  '{}' network. \nError: {}".format(network_config["ssid"], e))
        raise

    finally:
        gc.collect()
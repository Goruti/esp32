import gc
import network
import machine
import utime
import ubinascii


def is_connected():
    gc.collect()
    ip = None
    try:
        wlan = network.WLAN(network.STA_IF)
        if wlan.active() and wlan.isconnected():
            details = wlan.ifconfig()
            ip = details[0] if details else None
        gc.collect()
    except RuntimeError:
        ip = None
    return ip


def get_ip():
    gc.collect()
    try:
        ip = is_connected()
        if not ip:
            ap = network.WLAN(network.AP_IF)
            if ap.active():
                ip = ap.ifconfig()[0]
    except RuntimeError:
        ip = None
    return ip


def get_mac_address():
    gc.collect()
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    gc.collect()
    return mac


def start_ap(essid_name="ESP32 AP", password="ESP32 P@assword"):
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    gc.collect()
    ap_info = {"ssid": None, "ip": None}
    ap = network.WLAN(network.AP_IF)
    if not ap.active():
        ap.active(True)
        ap.config(essid=essid_name, authmode=network.AUTH_WPA_WPA2_PSK, password=password)

    ap_info["ip"] = ap.ifconfig()[0]
    ap_info["ssid"] = ap.config('essid')

    return ap_info


def stop_ap():
    """
    Stop WiFi Access Point
    """
    gc.collect()
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        ap.active(False)


def get_available_networks():
    gc.collect()
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
        utime.sleep(2)
    nets = [e[0].decode("utf-8") for e in wlan.scan()]
    return nets


def wifi_connect(network_config, timeout_ms=10000):
    """
    Connect to the WiFi network based on the configuration. Fails if there is no configuration.
    """
    gc.collect()

    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)

    if wlan.isconnected():
        wlan.disconnect()
    #wlan.active(False)
    #utime.sleep_ms(1)
    #wlan.active(True)
        utime.sleep_ms(100)

    wlan.connect(str(network_config["ssid"]), str(network_config["password"]))

    t = utime.ticks_ms()
    while not wlan.isconnected():
        if utime.ticks_diff(utime.ticks_ms(), t) < timeout_ms:
            machine.idle()
        else:
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


def wifi_disconnect():
    gc.collect()
    wlan = network.WLAN(network.STA_IF)
    if wlan.active():
        wlan.disconnect()

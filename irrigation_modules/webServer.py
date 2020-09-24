import gc
import picoweb
import utime
import machine
import logging
from irrigation_tools.conf import AP_SSID, AP_PWD, TEMPLATES_DIR, LOG_DIR, PORT_PIN_MAPPING, WEBREPL_PWD
from irrigation_tools.wifi import is_connected, wifi_disconnect, start_ap, get_ip, get_available_networks,\
    wifi_connect
from irrigation_tools.libraries import get_net_configuration, get_irrigation_state, get_irrigation_status,\
    test_irrigation_system, get_web_repl_configuration, get_log_files_names, get_smartthings_configuration,\
    start_pump, stop_pump, get_st_handler
from irrigation_tools.manage_data import save_network, save_webrepl_config, save_smartthings_config,\
    save_irrigation_config, read_irrigation_config

gc.collect()
_logger = logging.getLogger("webServer")


def index(request, response):
    gc.collect()
    if request.method == "GET":
        yield from index_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def enable_ap(request, response):
    gc.collect()
    if request.method == "GET":
        yield from enable_ap_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def wifi_config(request, response):
    gc.collect()
    if request.method == "GET":
        yield from wifi_config_get(request, response)
    elif request.method == "POST":
        yield from wifi_config_post(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def irrigation_config(request, response):
    gc.collect()
    if request.method == "GET":
        yield from irrigation_config_get(request, response)
    elif request.method == "POST":
        yield from irrigation_config_post(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def pump_action(request, response):
    gc.collect()
    if request.method == "GET":
        yield from pump_action_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def config_web_repl(request, response):
    gc.collect()
    if request.method == "GET":
        yield from config_web_repl_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def enable_smartthings(request, response):
    gc.collect()
    if request.method == "GET":
        yield from enable_smartthings_get(request, response)
    elif request.method == "POST":
        yield from enable_smartthings_post(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def restart_system(request, response):
    gc.collect()
    if request.method == "GET":
        yield from restart_system_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def test_system(request, response):
    gc.collect()
    if request.method == "GET":
        yield from test_system_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


def get_log_file(request, response):
    gc.collect()
    if request.method == "GET":
        yield from get_log_file_get(request, response)
    else:
        yield from picoweb.start_response(writer=response, status="405")
        yield from response.awrite(str("405 Method Not Allowed"))
        gc.collect()


################################################################################################################
################################################################################################################


def index_get(request, response):
    gc.collect()
    if b"text/html" in request.headers[b"Accept"]:
        try:
            data = {
                "net_config": get_net_configuration(),
                "irrigation_config": get_irrigation_status(),
                "irrigationState": get_irrigation_state(),
                "WebRepl": get_web_repl_configuration(),
                "smartThings": get_smartthings_configuration(),
                "log_files_name": get_log_files_names()
            }
        except Exception as e:
            _logger.exc(e, "Fail getting index")
            html_page = '''
                       <html>
                            <head><title>Irrigation System Home Page</title></head>
                            <body>
                               <p>Server couldn't complete your request</p>
                               <button onclick="window.location.href = '/' ;">Refresh</button>
                            </body>
                       </html>
                       '''
            gc.collect()
            yield from picoweb.start_response(writer=response, status="500")
            yield from response.awrite(str(html_page))
        else:
            yield from picoweb.start_response(response)
            yield from webapp.render_template(response, "index.tpl", (data,))
    else:
        try:
            data = {
                "type": "refresh",
                "body": get_irrigation_status()
            }
            yield from picoweb.jsonify(response, data)
        except Exception as e:
            _logger.exc(e, "Fail getting index")
            yield from picoweb.start_response(writer=response, status="500")
            yield from response.awrite("Server couldn't complete your request")

    gc.collect()


def enable_ap_get(request, response):
    gc.collect()
    error_code = "200"
    try:
        ap_info = start_ap(AP_SSID, AP_PWD)
    except BaseException as e:
        _logger.exc(e, "Fail Enabling AP")
        error_code = "500"
        html_page = '''
                       <html>
                            <head><title>Irrigation System Home Page</title></head>
                            <body>
                               <p>Server couldn't complete your request</p>
                               <button onclick="window.location.href = '/' ;">Cancel</button>
                            </body>
                       </html>
                       '''
    else:
        html_page = '''
               <html>
                    <head><title>Irrigation System Home Page</title></head>
                    <body>
                       <p>Please connect to <b>"{}"</b> Wifi Network and 
                       <a href="http://{}/config_wifi" title="Configuration Page">click here</a> to configure it</p>
                    </body>
               </html>
               '''.format(ap_info['ssid'], ap_info['ip'])

    finally:
        gc.collect()
        yield from picoweb.start_response(writer=response, status=error_code)
        yield from response.awrite(str(html_page))


def wifi_config_get(request, response):
    gc.collect()
    try:
        yield from picoweb.start_response(response)
        yield from webapp.render_template(response, "config_wifi.tpl", (get_available_networks(),))
    except BaseException as e:
        _logger.exc(e, "Fail Configuring Wifi")


def wifi_config_post(request, response):
    """
    Save Network Configuration
    """
    net_config = {}
    yield from request.read_form_data()
    gc.collect()
    for key in ['ssid', 'password']:
        if key in request.form:
            net_config[key] = request.form[key]

    # Now try to connect to the WiFi network
    _logger.debug("trying to connect to wifi with {}".format(net_config))
    try:
        wifi_connect(network_config=net_config)
    except Exception as e:
        _logger.exc(e, "Fail connecting to wifi")
        html_page = '''
                <html>
                    <head><title>Irrigation System Home Page</title></head>
                    <body>
                        <p style="color: red;">Fail to connect to Network: <b>"{}"</b</p><br>
                        <button onclick="window.location.href = '/config_wifi';">Try again</button>
                        <button onclick="window.location.href = '/' ;">Cancel</button>
                    </body>
                </html>
                '''.format(net_config["ssid"])
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
    else:
        save_network(**net_config)
        data = [net_config['ssid'], is_connected()]
        yield from picoweb.start_response(response)
        yield from webapp.render_template(response, "config_wifi_confirmation.tpl", (data,))
        utime.sleep(2)
        _logger.debug("restarting ESP-32")
        machine.reset()
    finally:
        gc.collect()


def irrigation_config_get(request, response):
    gc.collect()
    try:
        yield from webapp.sendfile(response, "{}/config_irrigation.html".format(TEMPLATES_DIR))
        # with open("{}/config_irrigation.html".format(TEMPLATES_DIR), 'r') as f:
        #    html_page = f.read()

    except Exception as e:
        _logger.exc(e, "cannot get irrigation Configuration")
        html_page = '''
                    <html>
                        <head><title>Irrigation System Home Page</title></head>
                       <body>
                           <p style="color: red;">Error loading the page.</p><br>
                            <p>Error: "{}"</p><br>
                            <button onclick="window.location.href = '/' ;">Home</button>
                       </body>
                   </html>'''.format(e)
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
    finally:
        gc.collect()


def irrigation_config_post(request, response):
    gc.collect()
    yield from request.read_form_data()
    try:
        config = {
            "total_pumps": int(request.form["total_pumps"])
        }
        pump_info = {}
        for pump in range(1, int(request.form["total_pumps"])+1):
            pump_info[pump] = {
                "moisture_threshold": int(request.form["moisture_threshold_{}".format(pump)]),
                "connected_to_port": request.form["connected_to_port_{}".format(pump)],
            }
        config.update({"pump_info": pump_info})

        st = get_st_handler(retry_sec=1, retry_num=5)
        if st:
            net_conf = get_net_configuration()
            payload = {
                "type": "system_configuration",
                "body": {
                    "ssid": net_conf["ssid"],
                    "ip": net_conf["ip"],
                    "system": config
                }
            }
        st.notify(payload)

        save_irrigation_config(**config)
        gc.collect()

    except Exception as e:
        _logger.exc(e, "Fail Saving Irrigation Configuration")
        html_page = '''
                <html>
                    <head><title>Irrigation System Home Page</title></head>
                   <body>
                       <p style="color: red;">Configuration Failed :(.</p><br>
                        <p>Error: "{}"</p><br>
                        <button onclick="window.location.href = '/irrigation_config';">Try Again</button>
                        <button onclick="window.location.href = '/' ;">Cancel</button>
                   </body>
               </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))

    else:
        html_page = '''
                <html>
                    <head><title>Irrigation System Home Page</title></head>
                    <body>
                        <p>Your system has been configured. In order to apply these changes, your device will be restarted</p>
                        <a href="http://{}/" title="Main Page">Visit Irrigation System main page</a>
                    </body>
                </html>
                '''.format(get_ip())
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        utime.sleep(1)
        wifi_disconnect()
        gc.collect()
        machine.reset()


def pump_action_get(request, response):
    gc.collect()
    try:
        request.parse_qs()
        port = request.form["pump"]
        action = request.form["action"]
        api_data = {
            "type": "pump_status",
            "body": {
                port: "off"
            }
        }
        if action == "on":
            started = start_pump(port)
            if started:
                api_data["body"][port] = "on"
        elif action == "off":
            stop_pump(port)

        if b"text/html" in request.headers[b"Accept"]:
            headers = {"Location": "/"}
            gc.collect()
            yield from picoweb.start_response(response, status="303", headers=headers)
        else:
            yield from picoweb.jsonify(response, api_data)

    except Exception as e:
        _logger.exc(e, "Fail to start/stop the pump")
        html_page = '''
                    <html>
                        <head><title>Irrigation System Home Page</title></head>
                       <body>
                           <p style="color: red;">Could not start/stop the pump. Check the logs on the device.</p><br>
                            <p>Error: "{}"</p><br>
                            <button onclick="window.location.href = '/';">Go Home Page</button>
                       </body>
                   </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))


def config_web_repl_get(request, response):
    import webrepl
    gc.collect()
    request.parse_qs()
    action = request.form["action"]

    if action == "enable":
        webrepl.start(password=WEBREPL_PWD)
        save_webrepl_config(**{"enabled": True})
    else:
        webrepl.stop()
        save_webrepl_config(**{"enabled": False})

    headers = {"Location": "/"}
    yield from picoweb.start_response(response, status="303", headers=headers)


def enable_smartthings_get(request, response):
    gc.collect()
    try:
        st = get_st_handler(retry_sec=1, retry_num=5)
        request.parse_qs()
        action = request.form["action"]
        if action == "enable":
            html_page = '''
                        <html>
                            <head>
                                <title>Irrigation System Home Page</title>
                            </head>
                            <body>
                            <h2>SmartThings Configuration</h2>
                                <form action="/enable_smartthings" method="post">
                                    <p>Configure SmartThings Connectivity</p>
                                    SmartTings IP: <input type="text" name="st_ip"><br><br>
                                    SmartTings Port:  <input type="text" name="st_port"><br><br>
                                    <input type="submit" value="OK">
                                    <input type="button" name="Cancel" value="Cancel" onClick="window.location='/';">
                                </form>
                            </body>
                        </html>'''

            gc.collect()
            yield from picoweb.start_response(response)
            yield from response.awrite(str(html_page))

        else:
            if st:
                payload = {
                    "type": "system_configuration",
                    "body": {
                        "status": "disable"
                    }
                }
                st.notify(payload)

            st_conf = {
                "enabled": False,
                "st_ip": None,
                "st_port": None
            }
            save_smartthings_config(**st_conf)

            headers = {"Location": "/"}
            gc.collect()
            yield from picoweb.start_response(response, status="303", headers=headers)

    except Exception as e:
        _logger.exc(e, "Fail to Configure SmartThings")
        html_page = '''
                        <html>
                            <head><title>Irrigation System Home Page</title></head>
                           <body>
                               <p style="color: red;">Smartthings Configuration Failed :(.</p><br>
                                <p>Error: "{}"</p><br>
                                <button onclick="window.location.href = '/enable_smartthings';">Try Again</button>
                        <button onclick="window.location.href = '/' ;">Cancel</button>
                           </body>
                       </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))


def enable_smartthings_post(request, response):
    gc.collect()
    try:
        yield from request.read_form_data()
        st_config = {}
        for key in ['st_ip', 'st_port']:
            if key in request.form:
                st_config[key] = request.form[key]
        st_config["enabled"] = True
        save_smartthings_config(**st_config)

        net_conf = get_net_configuration()
        payload = {
            "type": "system_configuration",
            "body": {
                "status": "enabled",
                "ssid": net_conf["ssid"],
                "ip": net_conf["ip"],
                "system": read_irrigation_config()
            }
        }
        st = get_st_handler(retry_num=5, retry_sec=1)
        if st:
            st.notify(payload)

    except Exception as e:
        _logger.exc(e, "Fail Saving ST configuration")
        html_page = '''
                    <html>
                        <head><title>Irrigation System Home Page</title></head>
                       <body>
                           <p style="color: red;">Smartthings Configuration Failed :(.</p><br>
                            <p>Error: "{}"</p><br>
                            <button onclick="window.location.href = '/enable_smartthings';">Try Again</button>
                    <button onclick="window.location.href = '/' ;">Cancel</button>
                       </body>
                   </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
    else:
        headers = {"Location": "/"}
        yield from picoweb.start_response(response, status="303", headers=headers)
    finally:
        gc.collect()


def restart_system_get(request, response):
    gc.collect()
    try:
        _logger.info("restarting system")
        html_page = '''
           <html>
               <head><title>Irrigation System Home Page</title></head>
               <body>
                   <p>Your system has been configured. In order to apply these changes, your device will be restarted</p>
                   <a href="http://{}/" title="Main Page">Visit Irrigation System main page</a>
               </body>
           </html>
       '''.format(get_ip())
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        utime.sleep(1)
        wifi_disconnect()
        gc.collect()
        machine.reset()

    except Exception as e:
        _logger.exc(e, "Fail restarting the system")
        html_page = '''
                    <html>
                        <head><title>Irrigation System Home Page</title></head>
                       <body>
                           <p style="color: red;">Could not restart the system. Check the logs on the device.</p><br>
                            <p>Error: "{}"</p><br>
                            <button onclick="window.location.href = '/';">Go Home Page</button>
                       </body>
                   </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))


def test_system_get(request, response):
    gc.collect()
    try:
        test_irrigation_system()
    except Exception as e:
        _logger.exc(e, "Fail testing the system")
        if b"text/html" in request.headers[b"Accept"]:
            html_page = '''
                        <html>
                            <head><title>Irrigation System Home Page</title></head>
                           <body>
                               <p style="color: red;">Could not test the system. Check the logs on the device.</p><br>
                                <p>Error: "{}"</p><br>
                                <button onclick="window.location.href = '/';">Go Home Page</button>
                           </body>
                       </html>'''.format(e)
            yield from picoweb.start_response(response)
            yield from response.awrite(str(html_page))
        else:
            yield from picoweb.start_response(writer=response, status="500")
            yield from response.awrite("Server couldn't complete your request")
    else:
        if b"text/html" in request.headers[b"Accept"]:
            headers = {"Location": "/"}
            yield from picoweb.start_response(response, status="303", headers=headers)
        else:
            data = {
                "type": "system_test",
                "body": "done"
            }
            yield from picoweb.jsonify(response, data)
    finally:
        gc.collect()


def get_log_file_get(request, response):
    gc.collect()
    try:
        request.parse_qs()
        file_name = request.form["file_name"]
        _logger.debug("File to fetch {}/{}".format(LOG_DIR, file_name))
        yield from webapp.sendfile(response, "{}/{}".format(LOG_DIR, file_name))
    except Exception as e:
        _logger.exc(e, "Fail Getting the logs")
        html_page = '''
                        <html>
                            <head><title>Irrigation System Home Page</title></head>
                           <body>
                               <p style="color: red;">Could not get the Logs. Check the logs on the device.</p><br>
                                <p>Error: "{}"</p><br>
                                <button onclick="window.location.href = '/';">Go Home Page</button>
                           </body>
                       </html>'''.format(e)
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
    finally:
        gc.collect()


ROUTES = [
    ('/', index),
    ('/enable_ap', enable_ap),
    ('/config_wifi', wifi_config),
    ('/irrigation_config', irrigation_config),
    ('/pump_action', pump_action),
    ('/config_web_repl', config_web_repl),
    ('/enable_smartthings', enable_smartthings),
    ('/restart_system', restart_system),
    ('/test_system', test_system),
    ('/get_log_file', get_log_file)
]

webapp = picoweb.WebApp(routes=ROUTES, tmpl_dir=TEMPLATES_DIR)

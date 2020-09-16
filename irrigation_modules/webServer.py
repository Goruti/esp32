import gc
gc.collect()
import picoweb
gc.collect()
import utime
gc.collect()
import machine
gc.collect()
import ubinascii
gc.collect()
import logging
gc.collect()
from irrigation_tools import conf, wifi, manage_data, libraries
gc.collect()
from micropython import const
gc.collect()

_looger = const(logging.getLogger("Irrigation"))


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
    data = {}
    try:
        data["net_config"] = libraries.get_net_configuration()
        data["irrigation_config"] = libraries.get_irrigation_status()
        data["irrigationState"] = libraries.get_irrigation_state()
        data["WebRepl"] = libraries.get_web_repl_configuration()
        data["smartThings"] = libraries.get_smartthings_configuration()
        data["log_files_name"] = libraries.get_log_files_names()

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
        try:
            if b"text/html" in request.headers[b"Accept"]:
                yield from picoweb.start_response(response)
                yield from webapp.render_template(response, "index.tpl", (data,))
            else:
                yield from picoweb.jsonify(response, data)
        except BaseException as e:
            _logger.exc(e, "Fail rendering the page")

    finally:
        gc.collect()


def enable_ap_get(request, response):
    gc.collect()
    error_code = "200"
    try:
        ap_info = wifi.start_ap(conf.AP_SSID, conf.AP_PWD)
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
        yield from webapp.render_template(response, "config_wifi.tpl", (wifi.get_available_networks(),))
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
        wifi.wifi_connect(network_config=net_config)
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
    else:
        manage_data.save_network(**net_config)
        data = [net_config['ssid'], wifi.is_connected()]

    finally:
        gc.collect()
        yield from picoweb.start_response(response)
        yield from webapp.render_template(response, "config_wifi_confirmation.tpl", (data,))
        utime.sleep(2)
        machine.reset()


def irrigation_config_get(request, response):
    gc.collect()
    try:
        with open("{}/config_irrigation.tpl".format(conf.TEMPLATES_DIR), 'r') as f:
            html_page = f.read().strip().replace(" ", "").replace("\n", "")
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
    finally:
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
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
        config["pump_info"] = pump_info

        net_conf = libraries.get_net_configuration()
        payload = {
            "type": "system_configuration",
            "body": {
                "ssid": net_conf["ssid"],
                "ip": net_conf["ip"],
                "system": config
            }
        }
        libraries.notify_st(payload)

        manage_data.save_irrigation_config(**config)
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
                '''.format(wifi.is_connected())
        #html_page = '''
        #   <html>
        #       <p>Configuration was saved successfully.</p>
        #       <p>Your System is being restarted. You will be redirected to the home page in <span id="counter">10</span> second(s).</p>
        #        <script type="text/javascript">
        #        function countdown() {
        #            var i = document.getElementById('counter');
        #            if (parseInt(i.innerHTML)<=0) {
        #                window.location.href = '/';
        #            }
        #            if (parseInt(i.innerHTML)!=0) {
        #                i.innerHTML = parseInt(i.innerHTML)-1;
        #            }
        #        }
        #        setInterval(function(){ countdown(); },1000);
        #        </script>
        #   </html>
        #'''

        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        utime.sleep(1)
        wifi.wifi_disconnect()
        gc.collect()
        machine.reset()


def pump_action_get(request, response):
    gc.collect()
    try:
        request.parse_qs()
        pump = request.form["pump"]
        action = request.form["action"]
        api_data = {"status": "off"}
        if action == "on":
            started = libraries.start_pump(conf.PORT_PIN_MAPPING.get(pump).get("pin_pump"))
            if started:
                api_data = {"status": "on"}
        elif action == "off":
            libraries.stop_pump(conf.PORT_PIN_MAPPING.get(pump).get("pin_pump"))

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
        webrepl.start(password=conf.WEBREPL_PWD)
        manage_data.save_webrepl_config(**{"enabled": True})
    else:
        webrepl.stop()
        manage_data.save_webrepl_config(**{"enabled": False})

    headers = {"Location": "/"}
    yield from picoweb.start_response(response, status="303", headers=headers)


def enable_smartthings_get(request, response):
    gc.collect()
    try:
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
            payload = {
                "type": "system_configuration",
                "body": {
                    "status": "disable"
                }
            }
            libraries.notify_st(payload)

            st_conf = {
                "enabled": False,
                "st_ip": None,
                "st_port": None
            }
            manage_data.save_smartthings_config(**st_conf)

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
        manage_data.save_smartthings_config(**st_config)

        net_conf = libraries.get_net_configuration()
        payload = {
            "type": "system_configuration",
            "body": {
                "status": "enabled",
                "ssid": net_conf["ssid"],
                "ip": net_conf["ip"],
                "system": manage_data.read_irrigation_config()
            }
        }
        libraries.notify_st(payload)

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
       '''.format(wifi.is_connected())

        #html_page = '''
        #   <html>
        #       <p>Your System is restarting. You will be redirected to the home page in <span id="counter">20</span> second(s).</p>
        #        <script type="text/javascript">
        #        function countdown() {
        #            var i = document.getElementById('counter');
        #            if (parseInt(i.innerHTML)<=0) {
        #                window.location.href = '/';
        #            }
        #            if (parseInt(i.innerHTML)!=0) {
        #                i.innerHTML = parseInt(i.innerHTML)-1;
        #            }
        #        }
        #        setInterval(function(){ countdown(); },1000);
        #        </script>
        #   </html>
        #'''
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        utime.sleep(1)
        wifi.wifi_disconnect()
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
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        gc.collect()


def test_system_get(request, response):
    gc.collect()
    try:
        libraries.test_irrigation_system()
    except Exception as e:
        _logger.exc(e, "Fail testing the system")
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
        headers = {"Location": "/"}
        yield from picoweb.start_response(response, status="303", headers=headers)
    finally:
        gc.collect()


def get_log_file_get(request, response):
    gc.collect()
    try:
        request.parse_qs()
        file_name = request.form["file_name"]
        yield from webapp.sendfile(response, "{}/{}".format(conf.LOG_DIR, file_name))
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


def require_auth(func):
    def auth(req, resp):
        auth = req.headers.get(b"Authorization")
        if not auth:
            yield from resp.awrite(
                'HTTP/1.0 401 NA\r\n'
                'WWW-Authenticate: Basic realm="Picoweb Realm"\r\n'
                '\r\n'
            )
            return

        auth = auth.split(None, 1)[1]
        auth = ubinascii.a2b_base64(auth).decode()
        req.username, req.passwd = auth.split(":", 1)
        yield from func(req, resp)

    return auth


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

webapp = picoweb.WebApp(routes=ROUTES, tmpl_dir=conf.TEMPLATES_DIR)
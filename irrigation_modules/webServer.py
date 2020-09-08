import gc
import picoweb
import utime
import machine
import sys

from irrigation_tools import conf, wifi, manage_data, libraries, smartthings_handler

webapp = picoweb.WebApp(tmpl_dir=conf.TEMPLATES_DIR)


@webapp.route('/', method='GET')
def index(request, response):
    """
    Main Page
    """
    gc.collect()
    data = {}
    try:
        data["net_config"] = libraries.get_net_configuration()
        data["irrigation_config"] = libraries.get_irrigation_status()
        data["WebRepl"] = libraries.get_web_repl_configuration()
        data["smartThings"] = libraries.get_smartthings_configuration()
    except Exception as e:
        sys.print_exception(e)
        html_page = '''
                       <html>
                            <head><title>Irrigation System Home Page</title></head>
                            <body>
                               <p>Server couldn't complete your request</p>
                               <button onclick="window.location.href = '/' ;">Cancel</button>
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
            sys.print_exception(e)


@webapp.route('/enable_ap', method='GET')
def wifi_config(request, response):
    gc.collect()
    error_code = "200"
    try:
        ap_info = wifi.start_ap(conf.AP_SSID, conf.AP_PWD)
    except BaseException as e:
        sys.print_exception(e)
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


@webapp.route('/config_wifi', method='GET')
def wifi_config(request, response):
    gc.collect()
    try:
        yield from picoweb.start_response(response)
        yield from webapp.render_template(response, "config_wifi.tpl", (wifi.get_available_networks(),))
    except BaseException as e:
        sys.print_exception(e)


@webapp.route('/config_wifi_2', method='POST')
def save_wifi_config(request, response):
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
    print("trying to connect to wifi with {}".format(net_config))
    try:
        wifi.wifi_connect(network_config=net_config)
    except Exception as e:
        sys.print_exception(e)
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


@webapp.route('/irrigation_config', method='GET')
def irrigation_config(request, response):
    gc.collect()
    html_page = open("{}/config_irrigation.tpl".format(conf.TEMPLATES_DIR), 'r').read()
    yield from picoweb.start_response(response)
    yield from response.awrite(str(html_page))


@webapp.route('/irrigation_config_2', method='POST')
def save_irrigation_config(request, response):
    """
    Save Irrigation Configuration
    """
    gc.collect()
    yield from request.read_form_data()
    try:
        smartthings = smartthings_handler.SmartThings()

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
        smartthings.notify(payload)

        manage_data.save_irrigation_config(**config)
        gc.collect()

    except Exception as e:
        sys.print_exception(e)
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


@webapp.route('/pump_action', method='GET')
def pump_action(request, response):
    gc.collect()
    try:
        request.parse_qs()
        pump = request.form["pump"]
        action = request.form["action"]

        if action == "ON":
            started = libraries.start_pump(conf.PORT_PIN_MAPPING.get(pump).get("pin_pump"))
        else:
            libraries.stop_pump(conf.PORT_PIN_MAPPING.get(pump).get("pin_pump"))

        headers = {"Location": "/"}
        gc.collect()
        yield from picoweb.start_response(response, status="303", headers=headers)

    except Exception as e:
        sys.print_exception(e)
        html_page = '''
                    <html>
                        <head><title>Irrigation System Home Page</title></head>
                       <body>
                           <p style="color: red;">Could not start the pump. Check the logs on the device.</p><br>
                            <p>Error: "{}"</p><br>
                            <button onclick="window.location.href = '/';">Go Home Page</button>
                       </body>
                   </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))


@webapp.route('/configWebRepl', method='GET')
def config_web_repl(request, response):
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


@webapp.route('/enableSmartThings', method='GET')
def enable_smartthings(request, response):
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
                                <form action="/configSmartthings" method="post">
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
            smartthings = smartthings_handler.SmartThings()
            payload = {
                "type": "system_configuration",
                "body": {
                    "status": "disable"
                }
            }
            smartthings.notify(payload)
            manage_data.save_smartthings_config(**{"enabled": False})

            headers = {"Location": "/"}
            gc.collect()
            yield from picoweb.start_response(response, status="303", headers=headers)

    except Exception as e:
        sys.print_exception(e)
        html_page = '''
                        <html>
                            <head><title>Irrigation System Home Page</title></head>
                           <body>
                               <p style="color: red;">Smartthings Configuration Failed :(.</p><br>
                                <p>Error: "{}"</p><br>
                                <button onclick="window.location.href = '/configureSmartThings';">Try Again</button>
                        <button onclick="window.location.href = '/' ;">Cancel</button>
                           </body>
                       </html>'''.format(e)
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))


@webapp.route('/configSmartthings', method='POST')
def save_smartthings_config(request, response):
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
                "ssid": net_conf["ssid"],
                "ip": net_conf["ip"],
                "system": manage_data.read_irrigation_config()
            }
        }
        smartthings = smartthings_handler.SmartThings()
        smartthings.notify(payload)



    except Exception as e:
        sys.print_exception(e)
        html_page = '''
                    <html>
                        <head><title>Irrigation System Home Page</title></head>
                       <body>
                           <p style="color: red;">Smartthings Configuration Failed :(.</p><br>
                            <p>Error: "{}"</p><br>
                            <button onclick="window.location.href = '/configureSmartThings';">Try Again</button>
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



@webapp.route('/restartSystem', method='GET')
def restart_system(request, response):
    gc.collect()
    try:
        print("restarting the system")
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
        sys.print_exception(e)
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


@webapp.route('/testSystem', method='GET')
def test_system(request, response):
    gc.collect()
    try:
        libraries.test_irrigation_system()
    except Exception as e:
        sys.print_exception(e)
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

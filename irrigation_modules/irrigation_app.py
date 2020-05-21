import gc
import picoweb
import uasyncio as asyncio
import ujson
import utime
import machine

from irrigation_modules import conf
from irrigation_modules import wifi
from irrigation_modules import manage_data
from irrigation_modules import libraries

webapp = picoweb.WebApp(None)

@webapp.route('/', method='GET')
def index(request, response):
    """
    The main page
    """
    gc.collect()
    data = {}
    print(request.headers[b"Accept"])

    try:
        data["net_config"] = libraries.get_net_configuration()
        data["irrigation_config"] = libraries.get_irrigation_configuration()
        data["irrigation_status"] = libraries.get_irrigation_status()

    except Exception as e:
        print("'GET /', Exception: {}".format(e))
        picoweb.http_error(response, "500")

    else:
        gc.collect()

        if b"text/html" in request.headers[b"Accept"]:
            yield from picoweb.start_response(response)
            yield from webapp.render_template(response, "index.tpl", (data,))
        else:
            yield from picoweb.jsonify(response, data)

    finally:
        gc.collect()


@webapp.route('/enable_ap', method='GET')
def wifi_config(request, response):
    ap_info = wifi.start_ap()
    gc.collect()
    html_page = '''
           <html>
                <head><title>Irrigation System Home Page</title></head>
                <body>
                   <p>Please connect to <b>"{}"</b> Wifi Network and 
                   <a href="http://{}/config_wifi" title="Configuration Page">click here</a> to configure it</p>
                </body>
           </html>
           '''.format(ap_info['ssid'], ap_info['ip'])

    gc.collect()
    yield from picoweb.start_response(response)
    yield from response.awrite(str(html_page))


@webapp.route('/config_wifi', method='GET')
def wifi_config(request, response):
    gc.collect()
    yield from picoweb.start_response(response)
    yield from webapp.render_template(response, "config_wifi.tpl", (wifi.get_available_networks(),))


@webapp.route('/config_wifi_2', method='POST')
def save_wifi_config(request, response):
    """
    Save Network Configuration
    """
    updated_net_config = {}
    yield from request.read_form_data()
    print("request.form[key]: ", request.form)
    gc.collect()
    for key in ['ssid', 'password']:
        if key in request.form:
            updated_net_config[key] = request.form[key]

    # Now try to connect to the WiFi network
    print("trying to connect to wifi with {}".format(updated_net_config))
    try:
        wifi.wifi_connect(network_config=updated_net_config, re_config=True)
    except Exception as e:
        print("fail to update Network Configuration. {}".format(e))
        html_page = '''
                <html>
                    <head><title>Irrigation System Home Page</title></head>
                    <body>
                        <p style="color: red;">Fail to connect to Network: <b>"{}"</b</p><br>
                        <button onclick="window.location.href = '/config_wifi';">Try again</button>
                    </body>
                </html>
                '''.format(updated_net_config["ssid"])
    else:
        manage_data.save_network(**updated_net_config)

        updated_net_config['message'] = "Please re-start your device"
        ip = wifi.is_connected()

        html_page = '''
        <html>
            <head><title>Irrigation System Home Page</title></head>
            <body>
                <p>Your are now connected to "{}" Wifi with ip: {}</p>
                <p><b>Your device will be reset it</b></p>
                <a href="http://{}/" title="Main Page">Visit Irrigation System main page</a>
            </body>
        </html>
        '''.format(updated_net_config['ssid'], ip, ip)

    finally:
        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        utime.sleep(2)
        machine.reset()


@webapp.route('/irrigation_config', method='GET')
def irrigation_config(request, response):
    gc.collect()
    html_page = open("irrigation_templates/config_irrigation.tpl", 'r').read()
    yield from picoweb.start_response(response)
    yield from response.awrite(str(html_page))


@webapp.route('/irrigation_config_2', method='POST')
def save_irrigation_config(request, response):
    """
    Save Irrigations Configuration
    """
    gc.collect()
    yield from request.read_form_data()
    try:
        config = {
            "total_pumps": int(request.form["total_pumps"])
        }

        pump_info = {}
        for pump in range(1, int(request.form["total_pumps"])+1):
            pump_info[pump] = {
                "output_power": int(request.form["output_power_{}".format(pump)]),
                "moisture_threshold": int(request.form["moisture_threshold_{}".format(pump)]),
                "connected_to_port": request.form["connected_to_port_{}".format(pump)],
                "pin_sensor": conf.port_pin_mapping[request.form["connected_to_port_{}".format(pump)]]["pin_sensor"],
                "pin_pump": conf.port_pin_mapping[request.form["connected_to_port_{}".format(pump)]]["pin_pump"],
            }
        config["pump_info"] = pump_info

        manage_data.save_irrigation_config(**config)
        gc.collect()

    except Exception as e:
        html_page = '''
                <html>
                    <head><title>Irrigation System Home Page</title></head>
                   <body>
                       <p style="color: red;">Configuration Failed :(.</p><br>
                        <p>Error: "{}"</p><br>
                        <button onclick="window.location.href = '/irrigation_config';">Try Again</button>
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
                       <p>Configuration was saved properly. Your device will be restarted :)</p>
                       <a href="/" title="Main Page">Go Back to the main page</a>
                   </body>
               </html>'''

        gc.collect()
        yield from picoweb.start_response(response)
        yield from response.awrite(str(html_page))
        utime.sleep(2)
        machine.reset()


def main_app():
    """
    Set up the tasks and start the event loop
    """
    libraries.init_irrigation_app()
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(libraries.initialize_rtc())
        #loop.create_task(calc_sunrise_sunset())
        #loop.create_task(door_check())

        #webapp.run(host="0.0.0.0", port=80, debug=True)

    except Exception as e:
        print(e)
        print("GOODBYE DUDE!!!")
        loop.close()





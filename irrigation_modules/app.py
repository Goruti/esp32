import gc
import picoweb
import uasyncio as asyncio
import utime
import machine
import sys
import ujson

from irrigation_tools import conf, wifi, manage_data, libraries
from irrigation_modules import main_loops


webapp = picoweb.WebApp(pkg="__main__", tmpl_dir=conf.TEMPLATES_DIR)


@webapp.route('/', method='GET')
def index(request, response):
    """
    Main Page
    """
    gc.collect()
    data = {}
    #print(request.headers[b"Accept"])

    try:
        data["net_config"] = libraries.get_net_configuration()
        data["irrigation_config"] = libraries.get_irrigation_configuration()
        data["irrigation_status"] = libraries.get_irrigation_status()
        #rendered_template = webapp.render_str("index.tpl", (data,))
    except Exception as e:
        sys.print_exception(e)
        yield from picoweb.http_error(response, "500", "Server could't complete your request.")
    else:
        gc.collect()
        try:
            if b"text/html" in request.headers[b"Accept"]:
                yield from picoweb.start_response(response)
                #yield from picoweb.template_string(response, rendered_template)
                yield from webapp.render_template(response, "index.tpl", (data,))
            else:
                yield from picoweb.jsonify(response, data)
        except BaseException as e:
            sys.print_exception(e)
    finally:
        gc.collect()


@webapp.route('/enable_ap', method='GET')
def wifi_config(request, response):
    gc.collect()
    try:
        ap_info = wifi.start_ap(conf.WIFI_SSID)
    except BaseException as e:
        sys.print_exception(e)
        yield from picoweb.http_error(response, "500", "Server could't complete your request")
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
        wifi.wifi_connect(network_config=updated_net_config)
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
                '''.format(updated_net_config["ssid"])
    else:
        manage_data.save_network(**updated_net_config)

        #updated_net_config['message'] = "Please re-start your device"
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
    html_page = open("{}/config_irrigation.tpl".format(conf.TEMPLATES_DIR), 'r').read()
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
                "moisture_threshold": int(request.form["moisture_threshold_{}".format(pump)]),
                "connected_to_port": request.form["connected_to_port_{}".format(pump)],
            }
        config["pump_info"] = pump_info

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


def main_app(loop=None):
    try:
        libraries.initialize_irrigation_app()

        """
        Set up the tasks and start the event loop
        """
        loop = asyncio.get_event_loop()
        loop.create_task(main_loops.initialize_rtc())
        #loop.create_task(main_loops.reading_process())
        webapp.run(host="0.0.0.0", port=80, debug=False)

    except BaseException as e:
        sys.print_exception(e)
        print("GOODBYE DUDE!!!")

    finally:
        if loop:
            loop.close()
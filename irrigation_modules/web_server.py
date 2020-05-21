from MicroWebSrv2 import *
from irrigation_modules.wifi import get_available_networks
import gc

import picoweb
app = picoweb.WebApp()

@WebRoute(GET, '/', name='Home Page')
def RequestTestPost(microWebSrv2, request):
    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>Irrigation System Home Page</title>
        </head>
        <body>
        <h1>Network Configuration</h1>
            <form action="/network_config" method="post">
                <p>Select a Wifi Network</p>
                SSID: <select input type="text" name="ssid" id="inject_networks">
                </select><br><br>
                Password:  <input type="text" name="password"><br><br>
                <input type="submit" value="OK">
            </form>
        <h1>Irrigation System Configuration</h1>
          <form action="/irrigation_config" method="post">
          Number of Pumps to control:  <input type="number" name="total_pumps" min="1" max="6" oninput="if(value>6)value=6;if(value<1)value=1" id="total_pumps" onchange="totalPumpsFunction()"><br><br>
            <p id="inject_pumps_config"></p>
          </form>
        </body>
    </html>
    
    <script>
      var net_wrapper = document.getElementById("inject_networks");
      var nets = %s
      var myHTML = '';
    
      nets.forEach(el => {
       myHTML += '<option value="' + el + '">' + el + '</option>';
      })
      net_wrapper.innerHTML = myHTML
      
      function totalPumpsFunction() {
        var total_pump = document.getElementById("total_pumps").value

        var sys_wrapper = document.getElementById("inject_pumps_config");
        var myHTML = '<h2> Pumps Configuration </h2>'
        
        for (var i = 1; i <= total_pump; i++) {
          myHTML += '<h3>Pump #' + i + '</h3>'
          myHTML += 'Power: <select input type="text" name="pump_power_' + i + '">';
          myHTML += '<option value=10>10%</option>'
          myHTML += '<option value=20>20%</option>'
          myHTML += '<option value=30>30%</option>'
          myHTML += '<option value=40>40%</option>'
          myHTML += '<option value=50>50%</option>'
          myHTML += '<option value=60>60%</option>'
          myHTML += '<option value=70>70%</option>'
          myHTML += '<option value=80>80%</option>'
          myHTML += '<option value=90>90%</option>'
          myHTML += '<option value=100>100%</option>'
          myHTML += '</select><br><br>';
          myHTML += 'Threashold:  <input type="number" value="400" name="moisture_threashold_' + i + '"><br><br>';
        }      
        myHTML += '<input type="submit" value="OK">'
        sys_wrapper.innerHTML = myHTML
      }
      
    </script>""" % str(get_available_networks())
    gc.collect()
    request.Response.ReturnOk(content)

# ------------------------------------------------------------------------

@WebRoute(POST, '/network_config', name='Network Configuration')
def RequestTestPost(microWebSrv2, request):
    data = request.GetPostedURLEncodedForm()
    try:
        ssid = data['ssid']
        password = data['password']
    except:
        request.Response.ReturnBadRequest()
        return
    print("ssid: {}, pwd: {}".format(ssid, password))
    gc.collect()
    request.Response.ReturnOk()


def start_web_server():
    print("starting web Server")
    mws2 = MicroWebSrv2()
    mws2.BindAddress = ('0.0.0.0', 80)
    mws2.SetEmbeddedConfig()
    mws2.BufferSlotsCount = 4
    #mws2.NotFoundURL = '/'
    mws2.RootPath = '/irrigation_modules/www'
    #mws2.AddDefaultPage('index.tpl')
    #mws2.LoadModule('PyhtmlTemplate')
    mws2.StartManaged()
    print("Is Web Server Started: {}".format(mws2.IsRunning))
    print("BindAddress: {}".format(mws2.BindAddress))
    # Main program loop until keyboard interrupt,
    try:
        while mws2.IsRunning:
            sleep(1)
    except KeyboardInterrupt:
        mws2.Stop()
        print('Bye')


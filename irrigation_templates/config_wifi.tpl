{% args data %}

<html>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h2>Network Configuration</h2>
        <form action="/config_wifi_2" method="post">
            <p>Select a Wifi Network</p>
            SSID: <select input type="text" name="ssid" id="inject_networks">
            </select><br><br>
            Password:  <input type="text" name="password"><br><br>
            <input type="submit" value="OK">
            <input type="button" name="Cancel" value="Cancel" onClick="window.location='/';">
        </form>
    </body>
</html>

<script>
  var net_wrapper = document.getElementById("inject_networks");
  var nets = {{data}}
  var myHTML = '';

  nets.forEach(el => {
   myHTML += '<option value="' + el + '">' + el + '</option>';
  })
  net_wrapper.innerHTML = myHTML
</script>
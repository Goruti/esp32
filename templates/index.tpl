{% args data %}

<html>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h1>Welcome to your Automated Irrigation System</h1>
    <h2>Network Configuration</h2>
        <div id="network_configuration">
        </div>
    <h2>Irrigation System Configuration</h2>
        <div id="irrigation_configuration">
        </div>
    </body>
</html>

<script>
    var net_wrapper = document.getElementById("network_configuration");
    var myHTML = `<p style="margin-left: 40px"><u>Wifi Connected</u>: <b>{{data["net_config"]["connected"]}}</b></p>`;

    if ( "{{data["net_config"]["connected"]}}" === "True" ) {
        myHTML += `<p style="margin-left: 40px"><u>SSID</u>: <b> {{data["net_config"]["ssid"]}}</b></p>`;
        myHTML += `<p style="margin-left: 40px"><u>IP</u>: <b>{{data["net_config"]["ip"]}}</b></p>`;
        myHTML += `<p><button onclick="window.location.href = '/enable_ap';">Reconfigure Wifi</button>`;
    } else {
         myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure a Wifi Network</b></p>`;
         myHTML += `<p><button onclick="window.location.href = '/enable_ap';">Configure Wifi</button>`;
    }
    net_wrapper.innerHTML = myHTML;

    var irrigation_wrapper = document.getElementById("irrigation_configuration");
    var myHTML = ``;
    if ( {{data["irrigation_config"]}} ) {
        var total_pump = {{data["irrigation_config"]["total_pumps"]}}
        var pump_info = {{data["irrigation_config"]["pump_info"]}}

        myHTML += `<p style="margin-left: 40px">Number of Pumps to control<: <b>` + total_pump + `</b></p>`;
        var myHTML = `<h2> Pumps Configuration </h2>`

        for (var i = 1; i <= total_pump; i++) {
            myHTML += `<h3>Pump #` + i + `</h3>`
            myHTML += `<p style="margin-left: 40px">Power: ` + pump_info[i]["output_power"] + `</p>`;
            myHTML += `<p style="margin-left: 40px">Threshold: ` + pump_info[i]["moisture_threshold"] + `</p>`;
            myHTML += `<p style="margin-left: 40px">Connected to Port: ` + pump_info[i]["connected_to_port"] + `</p>`;
        }

        myHTML += `<button onclick="window.location.href = '/irrigation_config';">Reconfigure Irrigation System</button>`;

    } else {
        myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure your Automated Irrigation System</b></p>`;
        myHTML += `<button onclick="window.location.href = '/irrigation_config';">Configure Irrigation System</button>`;
    }

    irrigation_wrapper.innerHTML = myHTML;

</script>
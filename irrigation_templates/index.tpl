{% args data %}

<html>
    <style>
        .choice_A{ background-color: #FFE800;font-weight: bold; padding: 3.5px }
        .choice_B{ background-color: #0f81f1;font-weight: bold; padding: 3.5px }
        .choice_C{ background-color: white;font-weight: bold; padding: 3.5px }
        .choice_D{ background-color: #f44336;font-weight: bold; padding: 3.5px }
        .choice_E{ background-color: #7f7f7f;font-weight: bold; padding: 3.5px }
    </style>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h1>Welcome to your Automated Irrigation System</h1>
    <h2>Web REPL</h2>
    <div id="web_repl_config">
    </div>
    <h2>Network Configuration</h2>
        <div id="network_configuration">
        </div>
    <h2>Irrigation System Configuration</h2>
        <div id="irrigation_configuration">
        </div>
    <h2>Restart the System</h2>
     <button onclick="window.location = '/restartSystem';">Restart </button>
    </body>
</html>

<script>
    var webRepl_wrapper = document.getElementById("web_repl_config");
    var myHTML = ``;
    if ("{{ data["WebRepl"]["enable"] }}" === "True") {
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=enable';" style="color: green;font-weight: bold;border-width: thin;opacity:0.6">Enable </button>`
        myHTML += `<button onclick="window.location = '/configWebRepl?action=disable';" style="color: red;margin-left:1em">Disable </button>`
    } else {
        myHTML += `<button onclick="window.location = '/configWebRepl?action=enable';" style="color: green;">Enable </button>`
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=disable';" style="color: red;margin-left:1em;font-weight: bold;border-width: thin;opacity:0.6">Disable </button>`
    }
    webRepl_wrapper.innerHTML = myHTML;

    var net_wrapper = document.getElementById("network_configuration");
    var myHTML = `<p style="margin-left: 40px"><u>Wifi Connected</u>: <b>{{ data["net_config"]["connected"] }}</b></p>`;

    if ("{{ data["net_config"]["connected"] }}" === "True") {
        myHTML += `<p style="margin-left: 40px"><u>SSID</u>: <b> {{ data["net_config"]["ssid"] }}</b></p>`;
        myHTML += `<p style="margin-left: 40px"><u>IP</u>: <b>{{ data["net_config"]["ip"] }}</b></p>`;
        myHTML += `<p><button onclick="window.location = '/enable_ap';">Reconfigure Wifi</button>`;
    } else {
         myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure a Wifi Network</b></p>`;
         myHTML += `<p><button onclick="window.location = '/config_wifi';">Configure Wifi</button>`;
    }
    net_wrapper.innerHTML = myHTML;

    var irrigation_wrapper = document.getElementById("irrigation_configuration");
    var myHTML = ``;
    myHTML += `<p style="margin-left: 40px">Water Level: <b>{{ data["irrigation_config"]["water_level"] }}</b></p>`;
    if ( "{{ data["irrigation_config"]["total_pumps"] }}" !== "0" ) {
        var total_pump = {{ data["irrigation_config"]["total_pumps"] }}
        var pump_info = {{ data["irrigation_config"]["pump_info"] }}

        myHTML += `<p style="margin-left: 40px">Number of Pumps to control: <b>` + total_pump + `</b></p>`;
        myHTML += `<h2> Pumps Configuration </h2>`

        for (var i = 1; i <= total_pump; i++) {
            myHTML += `<h3>Pump #` + i
            if ( pump_info[i]["pump_status"] === "On") {
                myHTML += `<button disabled onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="color: green;margin-left:3em; opacity:0.6">Start</button>`;
                myHTML += `<button onclick="window.location = '/pump_action?action=OFF&pump=` + pump_info[i]["connected_to_port"] + `';" style="color:red;font-weight:bold;margin-left:1em;;border-width: thin">Stop</button>`;
            }
            else {
                myHTML += `<button onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="color: green;font-weight: bold;margin-left:3em;;border-width: thin">Start</button>`;
                myHTML += `<button disabled onclick="window.location = '/pump_action?action=OFF&pump=` + pump_info[i]["connected_to_port"] + `';" style="color:red;margin-left:1em; opacity:0.6">Stop</button>`;

            }
            myHTML += `</h3>`
            myHTML += `<p style="margin-left: 40px">Connected to Port: <spam class="choice_` + pump_info[i]["connected_to_port"] + `">` + pump_info[i]["connected_to_port"] + `</spam></p>`;
            myHTML += `<p style="margin-left: 40px"> Status: ` + pump_info[i]["pump_status"] + `</p>`;
            myHTML += `<p style="margin-left: 40px">Threshold: ` + pump_info[i]["moisture_threshold"] + `; Moisture Value: ` + pump_info[i]["moisture"] + `</p>`;
        }
        myHTML += `<button onclick="window.location = '/irrigation_config';">Reconfigure Irrigation System</button>`;

    } else {
         myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure your Irrigation System</b></p>`;
         myHTML += `<p><button onclick="window.location = '/irrigation_config';">Configure Irrigation System</button>`;
    }
    irrigation_wrapper.innerHTML = myHTML;

    function onStartButton(pump_port) {
        if ( "{{ data["irrigation_config"]["water_level"] }}" === "empty" ) {
            alert("Water level is to low. Please refill the water tank before starting the pump")
        } else {
            console.log(pump_port)
            window.location = '/pump_action?action=ON&pump=' + pump_port;
        }
    }
</script>
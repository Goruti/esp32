{% args data %}

<html>
    <style>
        .row { display: flex; }
        .column { flex: 50%; text-align: center;}
        .choice_A { background-color:#FFE800; font-weight:bold; padding:2.5px; border:solid; border-color:black; border-width:thin; }
        .choice_B { background-color:#0f81f1; font-weight:bold; padding:2.5px; border:solid; border-color:black; border-width:thin; }
        .choice_C { background-color:white; font-weight:bold; padding:2.5px; border:solid; border-color:black; border-width:thin; }
        .choice_D { background-color:#f44336; font-weight:bold; padding:2.5px; border:solid; border-color:black; border-width:thin; }
        .choice_E { background-color:#7f7f7f; font-weight:bold; padding:2.5px; border:solid; border-color:black; border-width:thin; }
    </style>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h1 style="background: #e4e4e4;padding: 8px;">Welcome to your Automated Irrigation System</h1>
    <h2>System Tools</h2>
    <hr>
    <div class="row">
        <div class="column">
            <h2 style="text-align: left;margin-left: 40px;">Network Configuration</h2>
            <div id="network_configuration"></div>
        </div>
        <div class="column">
            <h3>Web REPL</h3>
            <div id="web_repl_config"><button disabled="" onclick="window.location = '/configWebRepl?action=enable';" style="font-weight: bold;border-width: thin;opacity:0.6">Enable </button><button onclick="window.location = '/configWebRepl?action=disable';" style="margin-left:1em">Disable </button></div>
        </div>
        <div class="column">
            <h3>Restart System</h3>
            <button onclick="window.location = '/restartSystem';">Restart</button>
        </div>
        <div class="column">
            <h3>Test System</h3>
            <button onclick="window.location = '/testSystem';">Test</button>
        </div>
    </div>
    <hr>
    <h2>Irrigation System Configuration</h2>
        <div id="irrigation_configuration"></div>
    </body>
</html>

<script>
    var webRepl_wrapper = document.getElementById("web_repl_config");
    var myHTML = ``;
    if ("{{ data["WebRepl"]["enable"] }}" === "True") {
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=enable';" style="font-weight: bold;border-width: thin;opacity:0.6">Enable </button>`
        myHTML += `<button onclick="window.location = '/configWebRepl?action=disable';" style="margin-left:1em">Disable </button>`
    } else {
        myHTML += `<button onclick="window.location = '/configWebRepl?action=enable';" style="">Enable </button>`
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=disable';" style="margin-left:1em;font-weight: bold;border-width: thin;opacity:0.6">Disable </button>`
    }
    webRepl_wrapper.innerHTML = myHTML;

    var net_wrapper = document.getElementById("network_configuration");
    var myHTML = `<p style="margin-left: 40px; text-align: left;"><u>Wifi Connected</u>: <b>{{ data["net_config"]["connected"] }}</b></p>`;

    if ("{{ data["net_config"]["connected"] }}" === "True") {
        myHTML += `<p style="margin-left: 40px; text-align: left;"><u>SSID</u>: <b> {{ data["net_config"]["ssid"] }}</b></p>`;
        myHTML += `<p style="margin-left: 40px; text-align: left;"><u>IP</u>: <b>{{ data["net_config"]["ip"] }}</b></p>`;
        myHTML += `<p style="margin-left: 40px; text-align: left;"><button onclick="window.location = '/enable_ap';">Reconfigure Wifi</button>`;
    } else {
         myHTML += `<p style="margin-left: 40px; text-align: left; color: #ff5722"><b>You need to configure a Wifi Network</b></p>`;
         myHTML += `<p style="margin-left: 40px; text-align: left;"><button onclick="window.location = '/config_wifi';">Configure Wifi</button>`;
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
            myHTML += `<h3>Plant #` + i
            if ( pump_info[i]["pump_status"] === "On") {
                myHTML += `<button disabled onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="margin-left:3em; opacity:0.6">Start</button>`;
                myHTML += `<button onclick="window.location = '/pump_action?action=OFF&pump=` + pump_info[i]["connected_to_port"] + `';" style="font-weight:bold;margin-left:1em;;border-width: thin">Stop</button>`;
            }
            else {
                myHTML += `<button onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="ont-weight: bold;margin-left:3em;;border-width: thin">Start</button>`;
                myHTML += `<button disabled onclick="window.location = '/pump_action?action=OFF&pump=` + pump_info[i]["connected_to_port"] + `';" style="margin-left:1em; opacity:0.6">Stop</button>`;
            }
            myHTML += `</h3>`
            myHTML += `<p style="margin-left: 40px">Connected to Port: <spam class="choice_` + pump_info[i]["connected_to_port"] + `">` + pump_info[i]["connected_to_port"] + `</spam></p>`;
            myHTML += `<p style="margin-left: 40px">Pump Status: ` + pump_info[i]["pump_status"] + `</p>`;
            myHTML += `<p style="margin-left: 40px">Moisture</p>`;
            myHTML += `<p style="margin-left: 40px">Threshold: ` + pump_info[i]["moisture_threshold"] + `; Value: ` + pump_info[i]["moisture"] + `</p>`;
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
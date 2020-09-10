{% args data %}

<html>
    <style>
        .row { display: flex; }
        .column { flex: 50%; text-align: left;}
        .choice_A { background-color:#FFE800; border-color:#000000;text-align:center;vertical-align:middle}
        .choice_B { background-color:#0f81f1; border-color:#000000;text-align:center;vertical-align:middle}
        .choice_C { background-color:white; border-color:#000000;text-align:center;vertical-align:middle }
        .choice_D { background-color:#f44336; border-color:#000000;text-align:center;vertical-align:middle }
        .choice_E { background-color:black; color: white; border-color:#000000;text-align:center;vertical-align:middle }
        .tg  {border-collapse:collapse;border-spacing:0;}
        .tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
          overflow:hidden;padding:10px 5px;word-break:normal;}
        .tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
          font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
        .tg .tg-18eh{border-color:#000000;font-weight:bold;text-align:center;vertical-align:middle}
        .tg .tg-xwyw{border-color:#000000;text-align:center;vertical-align:middle}
    </style>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <div id="irrigation_state"></div>
    <h2>System Tools</h2>
    <hr>
    <div class="row">
        <div class="column">
            <h3>Network Configuration</h3>
            <div id="network_configuration"></div>
        </div>
        <div class="column">
            <h3>Web REPL</h3>
            <div id="web_repl_config"></div>
            <h3>Smartthings</h3>
            <div id="smartthings_config"></div>
        </div>
        <div class="column">
            <h3>Restart System</h3>
            <button onclick="window.location = '/restartSystem';">Restart</button>
            <h3>Test System</h3>
            <button onclick="window.location = '/testSystem';">Test</button>
        </div>
    </div>
    <hr>
    <div class="row">
        <div class="column">
            <h2>Irrigation System Configuration</h2>
            <div id="irrigation_configuration"></div>
        </div>
        <div class="column">
            <h2>Last Error Message</h2>
            <div id="last_error"></div>
            <p><u>Timestamp:</u> {{ data["last_error"]["ts"] }}</p>
            <p><u>Error:</u> {{ data["last_error"]["error"] }}</p>
        </div>
    </div>
    </body>
</html>

<script>
    var webRepl_wrapper = document.getElementById("irrigation_state");
    var myHTML = ``;
    if ("{{ data["irrigationState"]["running"] }}" === "True") {
        myHTML += `<h1 style="background: #e4e4e4;padding: 8px;">Welcome to your Automated Irrigation System`
        myHTML += `<div style="font-size:14px; text-align:right; color:green;">Running</div>`
        myHTML += `</h1>`
    } else {
        myHTML += `<h1 style="background: #e4e4e4;padding: 8px;">Welcome to your Automated Irrigation System`
        myHTML += `div style="font-size:14px; text-align:right; color:red;">Stopped</div>`
        myHTML += `</h1>`
    }
    webRepl_wrapper.innerHTML = myHTML;

    var webRepl_wrapper = document.getElementById("web_repl_config");
    var myHTML = ``;
    if ("{{ data["WebRepl"]["enabled"] }}" === "True") {
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=enable';" style="font-weight: bold;border-width: thin;opacity:0.6">Enable </button>`
        myHTML += `<button onclick="window.location = '/configWebRepl?action=disable';" style="margin-left:1em">Disable </button>`
    } else {
        myHTML += `<button onclick="window.location = '/configWebRepl?action=enable';" style="">Enable </button>`
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=disable';" style="margin-left:1em;font-weight: bold;border-width: thin;opacity:0.6">Disable </button>`
    }
    webRepl_wrapper.innerHTML = myHTML;

    var webRepl_wrapper = document.getElementById("smartthings_config");
    var myHTML = ``;
    if ("{{ data["smartThings"]["enabled"] }}" === "True") {
        myHTML += `<button disabled onclick="window.location = '/enableSmartThings?action=enable';" style="font-weight: bold;border-width: thin;opacity:0.6">Enable </button>`
        myHTML += `<button onclick="window.location = '/enableSmartThings?action=disable';" style="margin-left:1em">Disable </button>`
        myHTML += `<p><u>SmartThings IP</u>: <b>{{ data["smartThings"]["st_ip"] }}</b></p>`;
        myHTML += `<p><u>SmartThings Port</u>: <b>{{ data["smartThings"]["st_port"] }}</b></p>`;
    } else {
        myHTML += `<button onclick="window.location = '/enableSmartThings?action=enable';" style="">Enable </button>`
        myHTML += `<button disabled onclick="window.location = '/enableSmartThings?action=disable';" style="margin-left:1em;font-weight: bold;border-width: thin;opacity:0.6">Disable </button>`
    }
    webRepl_wrapper.innerHTML = myHTML;

    var net_wrapper = document.getElementById("network_configuration");
    var myHTML = `<p><u>Wifi Connected</u>: <b>{{ data["net_config"]["connected"] }}</b></p>`;

    if ("{{ data["net_config"]["connected"] }}" === "True") {
        myHTML += `<p><u>SSID</u>: <b> {{ data["net_config"]["ssid"] }}</b></p>`;
        myHTML += `<p><u>IP</u>: <b>{{ data["net_config"]["ip"] }}</b></p>`;
        myHTML += `<p><u>Mac Address</u>: <b>{{ data["net_config"]["mac"] }}</b></p>`;
        myHTML += `<p><button onclick="window.location = '/enable_ap';">Reconfigure Wifi</button>`;
    } else {
         myHTML += `<p style="margin-left: 40px; text-align: left; color: #ff5722"><b>You need to configure a Wifi Network</b></p>`;
         myHTML += `<p style="margin-left: 40px; text-align: left;"><button onclick="window.location = '/config_wifi';">Configure Wifi</button>`;
    }
    net_wrapper.innerHTML = myHTML;

    var irrigation_wrapper = document.getElementById("irrigation_configuration");
    var myHTML = ``;
    myHTML += `<p><u>Water Level:</u> <b>{{ data["irrigation_config"]["water_level"] }}</b></p>`;

    if ( "{{ data["irrigation_config"]["total_pumps"] }}" !== "0" ) {
        var total_pump = {{ data["irrigation_config"]["total_pumps"] }}
        var pump_info = {{ data["irrigation_config"]["pump_info"] }}

        myHTML += `<p><u>Number of Plant(s) to Irrigate:</u> <b>` + total_pump + `</b></p>`;
        myHTML += `<p><u>Plant(s) Details</u></p>`;

        myHTML +=  `<table class="tg">`;
        myHTML +=  `<thead>`;
        myHTML +=  `<tr>`;
        myHTML +=  `<th class="tg-18eh" rowspan="2">Plant #</th>`;
        myHTML +=  `<th class="tg-18eh" rowspan="2">Connected to Port</th>`;
        myHTML +=  `<th class="tg-18eh" rowspan="2">Pump Status</th>`;
        myHTML +=  `<th class="tg-18eh" colspan="2">Moisture</th>`;
        myHTML +=  `<th class="tg-18eh" colspan="2" rowspan="2">Action</th>`;
        myHTML +=  `</tr>`;
        myHTML +=  `<tr>`;
        myHTML +=  `<td class="tg-18eh">Threshold</td>`;
        myHTML +=  `<td class="tg-18eh">Value</td>`;
        myHTML +=  `</tr>`;
        myHTML +=  `</thead>`;
        myHTML +=  `<tbody>`;

        for (var i = 1; i <= total_pump; i++) {
            myHTML += `<tr>`;

            myHTML += `<td class="tg-xwyw">#` + i + `</td>`;
            myHTML += `<td class="choice_` + pump_info[i]["connected_to_port"] + `">` + pump_info[i]["connected_to_port"] + `</td>`;
            myHTML += `<td class="tg-xwyw">` + pump_info[i]["pump_status"] + `</td>`;
            myHTML += `<td class="tg-xwyw">` + pump_info[i]["moisture_threshold"] + `</td>`;
            myHTML += `<td class="tg-xwyw">` + pump_info[i]["moisture"] + `</td>`;

            if ( pump_info[i]["pump_status"] === "On") {
                myHTML += `<td class="tg-xwyw"><button disabled onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="margin-left:3em; opacity:0.6">Start</button></td>`;
                myHTML += `<td class="tg-xwyw"><button onclick="window.location = '/pump_action?action=off&pump=` + pump_info[i]["connected_to_port"] + `';" style="margin-left:1em; border-width: thin">Stop</button></td>`;
            }
            else {
                myHTML += `<td class="tg-xwyw"><button onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="margin-left:3em;border-width: thin">Start</button></td>`;
                myHTML += `<td class="tg-xwyw"><button disabled onclick="window.location = '/pump_action?action=off&pump=` + pump_info[i]["connected_to_port"] + `';" style="margin-left:1em; opacity:0.6">Stop</button></td>`;
            }
            myHTML += `<tr>`;
        }
        myHTML += `</tbody>`;
        myHTML += `</table>`;

        myHTML += `<p><button onclick="window.location = '/irrigation_config';">Reconfigure Irrigation System</button></p>`;

    } else {
         myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure your Irrigation System</b></p>`;
         myHTML += `<p><button onclick="window.location = '/irrigation_config';">Configure Irrigation System</button>`;
    }
    irrigation_wrapper.innerHTML = myHTML;

    function onStartButton(pump_port) {
        if ( "{{ data["irrigation_config"]["water_level"] }}" === "empty" ) {
            alert("Water level is to low. Please refill the water tank before starting the pump")
        } else {
            window.location = '/pump_action?action=on&pump=' + pump_port;
        }
    }
</script>
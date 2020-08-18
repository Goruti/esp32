{% args data %}

<html>
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
    </body>
</html>

<script>
    var webRepl_wrapper = document.getElementById("web_repl_config");
    var myHTML = ``;
    if ("{{ data["WebRepl"] }}" === "True") {
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=enable';" style="color: green;font-weight: bold; opacity:0.6">Enable </button>`
        myHTML += `<button onclick="window.location = '/configWebRepl?action=disable';" style="color: red;font-weight: bold;">Disable </button>`
    } else {
        myHTML += `<button onclick="window.location = '/configWebRepl?action=enable';" style="color: green;font-weight: bold;">Enable </button>`
        myHTML += `<button disabled onclick="window.location = '/configWebRepl?action=disable';" style="color: red;font-weight: bold; opacity:0.6">Disable </button>
    }
    webRepl_wrapper.innerHTML = myHTML;

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
            myHTML += `<button onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="color: green;font-weight: bold;">Start</button>`;
            myHTML += `<button onclick="window.location = '/pump_action?action=OFF&pump=` + pump_info[i]["connected_to_port"] + `';" style="color: red;font-weight: bold;">Stop</button>`;
            myHTML += `</h3>`
            myHTML += `<p style="margin-left: 40px">Connected to Port: ` + pump_info[i]["connected_to_port"] + `; Status: ` + pump_info[i]["pump_status"] + `</p>`;
            myHTML += `<p style="margin-left: 40px">Threshold: ` + pump_info[i]["moisture_threshold"] + `; Moisture Value: ` + pump_info[i]["moisture"] + `</p>`;
        }
        myHTML += `<button onclick="window.location = '/irrigation_config';">Reconfigure Irrigation System</button>`;

    } else {
         myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure your Irrigation System</b></p>`;
         myHTML += `<p><button onclick="window.location = '/irrigation_config';">Configure Irrigation System</button>`;
    }
    irrigation_wrapper.innerHTML = myHTML;

    function onStartButton(pump) {
        if ( "{{ data["irrigation_config"]["water_level"] }}" === "empty" ) {
            alert("Water level is to low. Please refill the water tank")
        } else {
            return `"window.location = '/pump_action?action=ON&pump=` + pump + `';"`
        }
    }
</script>
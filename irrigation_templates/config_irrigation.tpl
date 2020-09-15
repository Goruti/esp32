<html>
<style>
.choice{ background-color: white;font-weight: normal }
.choice_A{ background-color:#FFE800; font-weight:bold; flex-wrap:wrap-reverse; padding-top:4px; }
.choice_B{ background-color:#0f81f1; font-weight:bold; flex-wrap:wrap-reverse; padding-top:4px; }
.choice_C{ background-colo: white; font-weight:bold; flex-wrap:wrap-reverse; padding-top:4px; }
.choice_D{ background-color:#f44336; font-weight:bold; flex-wrap:wrap-reverse; padding-top:4px; }
.choice_E{ background-color:#7f7f7f; font-weight:bold; flex-wrap:wrap-reverse; padding-top:4px; }
.selected_choice{ background-color: white;font-weight: bold}
</style>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h1>Irrigation System Configuration</h1>
      <form id="irrigationForm" action="/irrigation_config" method="post">
      Number of Plant(s) to Irrigate:  <input type="number" name="total_pumps" placeholder="Enter Value" style="font-weight: bold;width: 7.5em;" min="1" max="5" oninput="if(value>5)value=5;if(value<1)value=1" id="total_pumps" onchange="totalPumpsFunction()"><br><br>
        <p id="inject_pumps_config">
            <input type="button" name="Cancel" value="Cancel" onClick="window.location='/';"/>
        </p>
      </form>
    </body>
</html>

<script>
  function totalPumpsFunction() {
    var total_pump = document.getElementById("total_pumps").value

    var sys_wrapper = document.getElementById("inject_pumps_config");

    var myHTML = '<h2> Pumps Configuration </h2>'

    for (var i = 1; i <= total_pump; i++) {
      myHTML += '<h3>Pump #' + i + '</h3>'
      myHTML += 'Connected to Port:  <select input type="text" onchange="this.className=this.options[this.selectedIndex].className" name="connected_to_port_' + i + '" id="connected_to_port_' + i + '" required>';
      myHTML += '<option value="" class="choice" selected="selected">--Select Port--</option>'
      myHTML += '<option value="A" class="choice_A">&#x1F7E8; A</option>'
      myHTML += '<option value="B" class="choice_B">&#x1F7E6; B</option>'
      myHTML += '<option value="C" class="choice_C">&#x2B1C; C</option>'
      myHTML += '<option value="D" class="choice_D">&#x1F7E5; D</option>'
      myHTML += '<option value="E" class="choice_E">&#x2B1B; E</option>'
      myHTML += '</select><br><br>';
      myHTML += 'Threshold:  <input type="number" value="700" style="font-weight: bold" name="moisture_threshold_' + i + '" id="moisture_threshold_' + i + '" required><br><br>';
    }
    myHTML += `<input type="submit" value="Save" onclick="validateForm()">`
    myHTML += `<input type="button" name="Cancel" value="Cancel" onClick="window.location='/';">`

    sys_wrapper.innerHTML = myHTML
  }

</script>
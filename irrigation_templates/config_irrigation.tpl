<html>
<style>
.choice{ background-color: white;font-weight: normal }
.choice_A{ background-color: #009688;font-weight: bold }
.choice_B{ background-color: #FFEB3B;font-weight: bold }
.choice_C{ background-color: #f44336;font-weight: bold }
.choice_D{ background-color: #9c27b0;font-weight: bold }
.choice_E{ background-color: #03a9f4;font-weight: bold }
.choice_F{ background-color: #607d8b;font-weight: bold }
.choice_G{ background-color: #03a9f4;font-weight: bold }
.choice_H{ background-color: #607d8b;font-weight: bold }
.selected_choice{ background-color: white;font-weight: bold}
</style>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h1>Irrigation System Configuration</h1>
      <form id="irrigationForm" action="/irrigation_config_2" method="post">
      Number of Pumps to control:  <input type="number" name="total_pumps" placeholder="Enter Value" style="font-weight: bold;width: 7.5em;" min="1" max="6" oninput="if(value>6)value=6;if(value<1)value=1" id="total_pumps" onchange="totalPumpsFunction()"><br><br>
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
      myHTML += '<option value="" class="choice" selected="selected">--Please Select --</option>'
      myHTML += '<option value=A class="choice_A">A</option>'
      myHTML += '<option value=B class="choice_B">B</option>'
      myHTML += '<option value=C class="choice_C">C</option>'
      myHTML += '<option value=D class="choice_D">D</option>'
      myHTML += '<option value=E class="choice_E">E</option>'
      myHTML += '<option value=F class="choice_F">F</option>'
      myHTML += '<option value=G class="choice_G">E</option>'
      myHTML += '<option value=H class="choice_H">F</option>'
      myHTML += '</select><br><br>';
      myHTML += 'Threshold:  <input type="number" value="400" style="font-weight: bold" name="moisture_threshold_' + i + '" id="moisture_threshold_' + i + '" required><br><br>';
    }
    myHTML += `<input type="submit" value="Save" onclick="validateForm()">`
    myHTML += `<input type="button" name="Cancel" value="Cancel" onClick="window.location='/';">`

    sys_wrapper.innerHTML = myHTML
  }

</script>
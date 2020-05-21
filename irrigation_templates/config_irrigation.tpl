<html>
<style>
.choice{ background-color: white;font-weight: normal }
.choice_A{ background-color: #009688;font-weight: bold }
.choice_B{ background-color: #FFEB3B;font-weight: bold }
.choice_C{ background-color: #f44336;font-weight: bold }
.choice_D{ background-color: #9c27b0;font-weight: bold }
.choice_E{ background-color: #03a9f4;font-weight: bold }
.choice_F{ background-color: #607d8b;font-weight: bold }
.selected_choice{ background-color: white;font-weight: bold}
</style>
    <head>
        <title>Irrigation System Home Page</title>
    </head>
    <body>
    <h1>Irrigation System Configuration</h1>
      <form action="/irrigation_config_2" method="post">
      Number of Pumps to control:  <input type="number" name="total_pumps" placeholder="Enter Value" style="font-weight: bold;width: 7em;" min="1" max="6" oninput="if(value>6)value=6;if(value<1)value=1" id="total_pumps" onchange="totalPumpsFunction()"><br><br>
        <p id="inject_pumps_config"></p>
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
      myHTML += 'Power: <select input type="text" onchange="this.className=this.options[this.selectedIndex].className" name="output_power_' + i + '">';
      myHTML += '<option value="" class="choice" class="choice" selected="selected">--Please Select --</option>'
      myHTML += '<option value=10 class="selected_choice">10%</option>'
      myHTML += '<option value=20 class="selected_choice">20%</option>'
      myHTML += '<option value=30 class="selected_choice">30%</option>'
      myHTML += '<option value=40 class="selected_choice">40%</option>'
      myHTML += '<option value=50 class="selected_choice">50%</option>'
      myHTML += '<option value=60 class="selected_choice">60%</option>'
      myHTML += '<option value=70 class="selected_choice">70%</option>'
      myHTML += '<option value=80 class="selected_choice">80%</option>'
      myHTML += '<option value=90 class="selected_choice">90%</option>'
      myHTML += '<option value=100 class="selected_choice">100%</option>'
      myHTML += '</select><br><br>';
      myHTML += 'Threshold:  <input type="number" value="400" style="font-weight: bold" name="moisture_threshold_' + i + '"><br><br>';
      myHTML += 'Connected to Port:  <select input type="text" onchange="this.className=this.options[this.selectedIndex].className" name="connected_to_port_' + i + '">';
      myHTML += '<option value="" class="choice" selected="selected">--Please Select --</option>'
      myHTML += '<option value=A class="choice_A">A</option>'
      myHTML += '<option value=B class="choice_B">B</option>'
      myHTML += '<option value=C class="choice_C">C</option>'
      myHTML += '<option value=D class="choice_D">D</option>'
      myHTML += '<option value=E class="choice_E">E</option>'
      myHTML += '<option value=F class="choice_F">F</option>'
      myHTML += '</select><br><br>';
    }
    myHTML += '<input type="submit" value="Save">'
    sys_wrapper.innerHTML = myHTML
  }
</script>
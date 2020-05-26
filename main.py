from irrigation_tools.wifi import start_ap, stop_ap, wifi_connect
from irrigation_tools import manage_data, conf
from irrigation_modules.app import main_app
import gc
import os
import sys

try:
    wifi_connect(manage_data.get_network_config())
except Exception as e:
    print("main, no wifi connections".format(e))
    start_ap(conf.AP_SSID, conf.AP_PWD)
else:
    stop_ap()

#  Clean-up old irrigation_templates
for file in os.listdir('irrigation_templates'):
    if file.endswith("_tpl.py"):
        os.remove("irrigation_templates/{}".format(file))

gc.collect()

try:
    main_app()
except Exception as e:
    sys.print_exception(e)


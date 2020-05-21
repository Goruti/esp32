from irrigation_modules.wifi import start_ap, stop_ap, wifi_connect
from irrigation_modules.irrigation_app import main_app
import gc
import os

try:
    wifi_connect()
except Exception as e:
    print("main, no wifi connections".format(e))
    start_ap()
else:
    stop_ap()

#  Clean-up old templates
for file in os.listdir('templates'):
    if file.endswith("_tpl.py"):
        os.remove("templates/{}".format(file))

gc.collect()

load
try:
    main_app()
except Exception as e:
    print(e)


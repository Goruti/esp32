import gc
import uos
import sys
import logging

from irrigation_tools.wifi import start_ap, stop_ap, wifi_connect
from irrigation_tools.manage_data import create_dir, get_network_config
from irrigation_tools.conf import DB_DIR, AP_SSID, AP_PWD, LOG_DIR
from irrigation_tools.libraries import initialize_root_logger
from irrigation_modules.app import main_app

#  Initialize logger
create_dir(DB_DIR)
create_dir(LOG_DIR)
initialize_root_logger(logging.DEBUG)
_logger = logging.getLogger("Irrigation")
_logger.info("############# STARTING IRRIGATION SYSTEM #############")

try:
    wifi_connect(get_network_config())
except Exception as e:
    _logger.info("Device is Offline. Start AP")
    start_ap(AP_SSID, AP_PWD)
else:
    stop_ap()

#  Clean-up old irrigation_templates
for file in uos.listdir('irrigation_templates'):
    if file.endswith("_tpl.py"):
        uos.remove("irrigation_templates/{}".format(file))

gc.collect()
try:
    import uftp
    main_app()
except Exception as e:
    sys.print_exception(e)
    _logger.exc(e, "failed starting main application")


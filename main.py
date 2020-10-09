import gc
import uos
import logging

from irrigation_tools.wifi import start_ap, stop_ap, wifi_connect
from irrigation_tools.manage_data import create_dir, get_network_config
from irrigation_tools.conf import DB_DIR, AP_SSID, AP_PWD, LOG_DIR, LOG_FILENAME
from irrigation_tools.libraries import initialize_root_logger, mount_sd_card, unmount_sd_card
from irrigation_modules.app import main_app
gc.collect()

#  Initialize Logging
logfile = None
if mount_sd_card():
    create_dir(LOG_DIR)
    logfile = "{}/{}".format(LOG_DIR, LOG_FILENAME)
initialize_root_logger(level=logging.DEBUG, logfile=logfile)
_logger = logging.getLogger("main")
gc.collect()

_logger.info("############# STARTING IRRIGATION SYSTEM #############")
create_dir(DB_DIR)

try:
    wifi_connect(get_network_config())
except Exception as e:
    _logger.exc(e, "Failed to connect to Wifi")
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
    unmount_sd_card()
    _logger.exc(e, "failed starting main application")

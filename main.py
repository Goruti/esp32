import gc
import uos
import sys
import logging

from irrigation_tools.wifi import start_ap, stop_ap, wifi_connect
from irrigation_tools.manage_data import create_dir, get_network_config
from irrigation_tools.conf import DB_DIR, AP_SSID, AP_PWD, LOG_DIR, LOG_FILENAME, WEBREPL_PWD
from irrigation_tools.libraries import initialize_root_logger, mount_sd_card
from irrigation_modules.app import main_app
gc.collect()

#  Initialize Logging
logfile = None
SD_mounted = mount_sd_card()
if SD_mounted:
    create_dir(LOG_DIR)
    logfile = "{}/{}".format(LOG_DIR, LOG_FILENAME)
initialize_root_logger(level=logging.INFO, logfile=logfile)
_logger = logging.getLogger("main")
gc.collect()


try:
    wifi_connect(get_network_config())
except Exception as e:
    _logger.exc(e, "Failed to connecto to Wifi")
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
    if SD_mounted:
        create_dir(DB_DIR)
        _logger.info("############# STARTING IRRIGATION SYSTEM #############")
        main_app()
except Exception as e:
    sys.print_exception(e)
    _logger.exc(e, "failed starting main application")

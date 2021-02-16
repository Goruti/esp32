import gc
import uos
import uasyncio as asyncio
from irrigation_tools.libraries import initialize_irrigation_app, unmount_sd_card
from irrigation_modules import main_loops, webServer
from irrigation_tools.conf import SD_MOUNTING
import logging
gc.collect()

_logger = logging.getLogger("app")


def main_app():
    initialize_irrigation_app()
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(main_loops.initialize_rtc(frequency_loop=3600))
        loop.create_task(main_loops.reading_moister(frequency_loop_ms=600000, report_freq_ms=3600000))
        loop.create_task(main_loops.reading_water_level())
        webServer.webapp.run(host="0.0.0.0", port=80)

    except BaseException as e:
        _logger.exc(e, "GOODBYE DUDE!!!")

    finally:
        if loop:
            loop.close()
        unmount_sd_card()
        if SD_MOUNTING and str(SD_MOUNTING) != "" and SD_MOUNTING in uos.listdir():
            uos.umount(SD_MOUNTING)
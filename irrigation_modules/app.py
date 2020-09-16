import uasyncio as asyncio
from irrigation_tools import libraries
from irrigation_modules import main_loops, webServer
import logging

_logger= logging.getLogger("Irrigation")


def main_app():

    try:
        libraries.initialize_irrigation_app()

        """
        Set up the tasks and start the event loop
        """

        #_thread.start_new_thread(main_loops.initialize_rtc, ())
        #_thread.start_new_thread(main_loops.reading_moister, (300000,))
        #_thread.start_new_thread(webServer.webapp.run, ("0.0.0.0", 80))

        loop = asyncio.get_event_loop()
        loop.create_task(main_loops.initialize_rtc(frequency_loop=86400))
        loop.create_task(main_loops.reading_moister(frequency_loop_ms=3600000, report_freq_ms=3600000))
        #loop.create_task(main_loops.reading_water_level(frequency_loop=300))
        webServer.webapp.run(host="0.0.0.0", port=80)

    except BaseException as e:
        _logger.exc(e, "GOODBYE DUDE!!!")
        pass

    finally:
        if loop:
            loop.close()
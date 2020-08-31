import gc
import uasyncio as asyncio
import sys

from irrigation_tools import libraries
from irrigation_modules import main_loops, webServer


def main_app(loop=None):
    try:
        libraries.initialize_irrigation_app()

        """
        Set up the tasks and start the event loop
        """
        loop = asyncio.get_event_loop()
        loop.create_task(main_loops.initialize_rtc())
        # TODO (uncomment the following line)
        #loop.create_task(main_loops.reading_moister(frequency_loop=300))
        #loop.create_task(main_loops.reading_water_level(frequency_loop=300))
        webServer.webapp.run(host="0.0.0.0", port=80, debug=False)

    except BaseException as e:
        sys.print_exception(e)
        print("GOODBYE DUDE!!!")

    finally:
        if loop:
            loop.close()
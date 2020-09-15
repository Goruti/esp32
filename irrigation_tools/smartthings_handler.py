import gc
gc.collect()
import utime
gc.collect()
from irrigation_tools import libraries
gc.collect()
import urequests as requests
gc.collect()
import logging
gc.collect()

_logger = logging.getLogger("Irrigation")


class SmartThings:
    def __init__(self, retry_num=5, retry_sec=1, st_ip=None, st_port=None):

        if st_ip and st_port:
            self.URL = self.URL = "http://{}:{}".format(st_ip, st_port)
        else:
            self.URL = None

        self.retry_num = retry_num
        self.retry_sec = retry_sec
        self.requests = requests

    def notify(self, body):
        try:
            attempts = self.retry_num
            #_logger.debug("{} - Smartthings.notify, Sent body: {}".format(datetime_to_iso(utime.localtime()), body))
            if self.URL:
                while attempts and self._send_values(body):
                    attempts -= 1
                    #_logger.debug("{} - Smartthings.notify, Re-try: {} - Body: {}".format(datetime_to_iso(utime.localtime()),
                    #                                                              (self.retry_num - attempts), body))

                    utime.sleep(pow(2, (self.retry_num - attempts)) * self.retry_sec)

                if not attempts:
                    _logger.debug("{} - Smartthings.notify - Tried: {} times and it couldn't send readings. free_memory: {}".format(
                        libraries.datetime_to_iso(utime.localtime()), self.retry_num, gc.mem_free()))
            else:
                _logger.info("SmartThings is not configured. This how message would looks like: {}".format(body))

        except Exception as e:
            _logger.exc(e, "Failed to notify ST")

        finally:
            gc.collect()

    def _send_values(self, body):
        failed = True
        headers = {"Content-Type": "application/json"}

        try:
            gc.collect()
            r = self.requests.post(self.URL, json=body, headers=headers)
        except Exception as e:
            _logger.exc(e, "fail to send Value - free_memory: {}".format(gc.mem_free()))
        else:
            if r.status_code == 202 or r.status_code == 200:
                failed = False
            else:
                _logger.debug("{} - 'Smartthings.send_values' - HTTP_Status_Code: '{}' - HTTP_Reason: {}".format(
                    libraries.datetime_to_iso(utime.localtime()), r.get("status_code"), r.get("reason")))
            r.close()
        finally:
            gc.collect()
            return failed
import gc
import utime
from irrigation_tools import libraries, manage_data
import urequests as requests
import sys


class SmartThings():
    def __init__(self, retry_num=5, retry_sec=1):
        st_config = manage_data.read_smartthings_config()
        if not st_config or not st_config["enabled"]:
            self.URL = None
        else:
            self.URL = "http://{}:{}".format(st_config["st_ip"], st_config["st_port"])

        self.retry_num = retry_num
        self.retry_sec = retry_sec
        self.requests = requests

    def notify(self, body):
        try:
            attempts = self.retry_num
            #print("{} - Smartthings.notify, Sent body: {}".format(datetime_to_iso(utime.localtime()), body))
            if self.URL:
                while attempts and self._send_values(body):
                    attempts -= 1
                    #print("{} - Smartthings.notify, Re-try: {} - Body: {}".format(datetime_to_iso(utime.localtime()),
                    #                                                              (self.retry_num - attempts), body))

                    utime.sleep(pow(2, (self.retry_num - attempts)) * self.retry_sec)

                if not attempts:
                    print("{} - Smartthings.notify - Tried: {} times and it couldn't send readings. free_memory: {}".format(
                        libraries.datetime_to_iso(utime.localtime()), self.retry_num, gc.mem_free()))
            else:
                print("SmartThings is not configured. This how message would looks like: {}".format(body))

        except Exception as e:
            sys.print_exception(e)

        finally:
            gc.collect()

    def _send_values(self, body):
        failed = True
        headers = {"Content-Type": "application/json"}

        try:
            gc.collect()
            r = self.requests.post(self.URL, json=body, headers=headers)
        except Exception as e:
            print("{} - Smartthings.send_values' - 'Exception': {}, free_memory: {}".format(libraries.datetime_to_iso(utime.localtime()), e, gc.mem_free()))
            sys.print_exception(e)
        else:
            if r.status_code == 202 or r.status_code == 200:
                failed = False
            else:
                print("{} - 'Smartthings.send_values' - HTTP_Status_Code: '{}' - HTTP_Reason: {}".format(
                    libraries.datetime_to_iso(utime.localtime()), r.get("status_code"), r.get("reason")))
            r.close()
        finally:
            gc.collect()
            return failed
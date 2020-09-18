# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc
import micropython
from irrigation_tools.libraries import mount_sd_card


esp.osdebug(None)
micropython.alloc_emergency_exception_buf(100)
mount_sd_card()
gc.collect()

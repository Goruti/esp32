# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc
import micropython

esp.osdebug(None)
gc.collect()
micropython.alloc_emergency_exception_buf(100)

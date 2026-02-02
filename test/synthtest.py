from machine import Pin
import time
import random
import math

accent_p = Pin(12, Pin.OUT)
accent_v = Pin(13, Pin.OUT)
osc = Pin(10, Pin.OUT)
gate = Pin(11, Pin.OUT)

gate.on()
accent_p.on()
accent_v.off()
t = 0
while True:
    if(t%400>=200):
      osc.on()
      time.sleep_ms(4)
      osc.off()
      time.sleep_ms(4)
      osc.on()
      time.sleep_ms(4)
      osc.off()
      time.sleep_ms(4)
      if t % 50 == 0:
          gate.off()
      if t % 50 == 10:
          gate.on()
      t = t + 2
    else:
      osc.on()
      time.sleep_ms(8)
      osc.off()
      time.sleep_ms(8)
      if t % 50 == 0:
          gate.off()
      if t % 50 == 20:
          gate.on()
      t = t + 2

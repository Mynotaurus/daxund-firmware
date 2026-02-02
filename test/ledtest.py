import time
import machine, neopixel
import math

np = neopixel.NeoPixel(machine.Pin(27), 16)

def demo(np):
    t = 0
    n = 16
    while True:
        for i in range(n):
            np[i] = (math.floor(32+24*math.sin((t+i*20)/100)), 0, math.floor(32+24*math.cos((t+i*20)/100)))
            np.write()
            t = t + 1

demo(np)
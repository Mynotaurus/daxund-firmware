from machine import Pin, SPI, ADC
import neopixel
import time
from sh1122 import SH1122_SPI
import framebuf

WIDTH  = 256                                            # oled display width
HEIGHT = 64                                             # oled display height
sclk = Pin(6, Pin.OUT)
sdin = Pin(7, Pin.OUT)
spi = SPI(0,sck=sclk, mosi=sdin)                                            # Init I2C using I2C0 defaults, SCL=Pin(GP6), MOSI=Pin(GP7), freq=1MHz
dc = Pin(4, Pin.OUT)
dc.value(0)
res = Pin(3, Pin.OUT)
res.value(1)
cs = Pin(5, Pin.OUT)
cs.value(1)
oled = SH1122_SPI(WIDTH, HEIGHT, spi, dc, res, cs)


np = neopixel.NeoPixel(machine.Pin(27), 16)
rows = [Pin(0, Pin.IN,pull=Pin.PULL_DOWN),Pin(1, Pin.IN,pull=Pin.PULL_DOWN),Pin(2, Pin.IN,pull=Pin.PULL_DOWN)]
cols = [Pin(15, Pin.OUT),Pin(16, Pin.OUT),
        Pin(17, Pin.OUT),Pin(18, Pin.OUT),
        Pin(19, Pin.OUT),Pin(20, Pin.OUT),
        Pin(21, Pin.OUT),Pin(22, Pin.OUT)]
row = 0

def lightPin(row,col,r,g,b):
    if(row==0):
        np[15-col] = (r,g,b)
    else:
        np[7-col] = (r,g,b)
while True:
    np.fill((0,0,0))
    oled.fill(0)
    for j in range(8):
        cols[j].on()
        for i in range(3):
            if rows[i].value():
                lightPin(i-1,j,64,16,32)
                oled.fill_rect(j*18, i*18, 16, 16,12)
            else:
                oled.fill_rect(j*18, i*18, 16, 16,1)
        cols[j].off()
        time.sleep_ms(1)
    np.write()
    oled.show()

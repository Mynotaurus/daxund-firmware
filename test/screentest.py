# MicroPython SH1122 OLED driver, SPI interface
# fdufnews 2021/02/09
# based on Peter Hinch SSD1306 driver

from micropython import const
import framebuf


# register definitions

SET_COL_ADR_LSB = const(0X0)
SET_COL_ADR_MSB = const(0X10)
SET_DISP_START_LINE = const(0X40)
SET_CONTRAST = const(0X81)
SET_SEG_REMAP = const(0XA0)
SET_ENTIRE_ON = const(0XA4)
SET_NORM_INV = const(0XA6)
SET_MUX_RATIO = const(0XA8)
SET_CTRL_DCDC = const(0XAD)
SET_DISP = const(0XAE)
SET_ROW_ADR = const(0XB0)
SET_COM_OUT_DIR = const(0XC0)
SET_DISP_OFFSET = const(0XD3)
SET_DISP_CLK_DIV = const(0XD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_VSEG_LEVEL = const(0XDC)
SET_DISCHARGE_LEVEL = const(0X30)
           


# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SH1122(framebuf.FrameBuffer):
    @staticmethod
    def rgb(r, g, b):
        return int(max(r,g,b))  # perhaps not the better but .....

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pages = self.height // 2
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.GS4_HMSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_COL_ADR_LSB,
            SET_COL_ADR_MSB,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP,
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR,  # scan from COM0 to COM[N]
            SET_DISP_OFFSET,
            0x00,
            # display
            SET_CONTRAST,
            0x80,  # median
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def flip(self): # Rotates the display 180 degrees
        self.write_cmd(SET_DISP_START_LINE | 0x20)
        self.write_cmd(0XA1)
        self.write_cmd(0XC8)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        self.write_cmd(SET_COL_ADR_LSB)
        self.write_cmd(SET_COL_ADR_MSB)
        self.write_cmd(SET_ROW_ADR)
        self.write_data(self.buffer)


class SH1122_SPI(SH1122):
    def __init__(self, width, height, spi, dc, res, cs):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)
# Display a short animation on an SPI driven sh1122 OLED display 
# display connections to Pico
#   GND     ----->      GND (pin 38)
#   VCC     ----->      3V3 (pin 36)
#   SCLK    ----->      SCL GP6 (pin 9)
#   SDIN    ----->      SPI TX GP7 (pin 10)
#   RES     ----->      GP3 (pin 5)
#   DC      ----->      GP4 (pin 6)
#   CS      ----->      GP5 (pin 7)
#
#   A pot on GP26 (ADC0), used to change speed of the animation
#   A push-button on GP14, used to halt the script
#

# Display Image & text on an SPI driven sh1122 OLED display 
# display connections to Pico
#   GND     ----->      GND (pin 38)
#   VCC     ----->      3V3 (pin 36)
#   SCLK    ----->      SCL GP6 (pin 9)
#   SDIN    ----->      SPI TX GP7 (pin 10)
#   RES     ----->      GP3 (pin 5)
#   DC      ----->      GP4 (pin 6)
#   CS      ----->      GP5 (pin 7)

from machine import Pin, SPI


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


oled = SH1122_SPI(WIDTH, HEIGHT, spi, dc, res, cs)                  # Init oled display

# Raspberry Pi logo as 32x40 bytearray 16 levels of gray
# 2 pixels per byte
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\x45\x56\x41\x00\x00\x00\x00\x14\x55\x54\x11\x00\x00\x00\x16\x8A\xAA\xAA\xAA\x73\x00\x00\x36\x9A\xAA\xAA\xA9\x61\x00\x00\x18\xAA\xAA\xAA\xAA\xAA\x30\x02\xAA\xAA\xAA\xAA\xAA\x91\x00\x00\x18\xAA\x97\x8A\xAA\xAA\x80\x07\xAA\xAA\xA8\x79\xAA\x91\x00\x00\x07\xAA\xAA\x85\x7A\xAA\xA1\x0A\xAA\xA8\x58\xAA\xAA\x70\x00\x00\x03\xAA\xAA\xAA\x63\x9A\xA1\x0A\xA9\x45\xAA\xAA\xAA\x30\x00\x00\x00\x6A\xAA\xAA\xA8\x27\x40\x03\x72\x8A\xAA\xAA\xA7\x00\x00\x00\x00\x28\xAA\xAA\xAA\x91\x00\x00\x08\xAA\xAA\xAA\x83\x00\x00\x00\x00\x03\x8A\xAA\xAA\x70\x00\x00\x06\xAA\xAA\xA8\x30\x00\x00\x00\x00\x00\x15\x8A\x95\x00\x00\x00\x00\x59\xA9\x52\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x34\x43\x10\x00\x11\x00\x00\x00\x00\x00\x00\x00\x02\x55\x51\x26\x66\x66\x62\x05\x54\x20\x00\x00\x00\x00\x00\x00\x46\x66\x30\x66\x66\x66\x66\x12\x66\x65\x00\x00\x00\x00\x00\x03\x66\x63\x00\x46\x66\x66\x66\x10\x26\x66\x40\x00\x00\x00\x00\x06\x66\x20\x00\x03\x56\x66\x41\x00\x02\x66\x61\x00\x00\x00\x00\x16\x51\x01\x23\x20\x00\x00\x13\x54\x20\x15\x62\x00\x00\x00\x00\x13\x00\x36\x66\x65\x10\x01\x66\x66\x65\x00\x32\x00\x00\x00\x00\x00\x02\x66\x66\x66\x50\x04\x66\x66\x66\x40\x00\x00\x00\x00\x03\x40\x06\x66\x66\x66\x61\x06\x66\x66\x66\x62\x05\x40\x00\x00\x36\x60\x26\x66\x66\x66\x61\x06\x66\x66\x66\x64\x06\x64\x00\x00\x66\x61\x36\x66\x66\x66\x60\x05\x66\x66\x66\x64\x16\x66\x10\x02\x66\x60\x36\x66\x66\x66\x40\x02\x66\x66\x66\x64\x06\x66\x20\x02\x66\x50\x16\x66\x66\x66\x10\x00\x46\x66\x66\x61\x05\x66\x20\x01\x66\x40\x03\x66\x66\x51\x01\x10\x04\x66\x66\x30\x04\x66\x10\x00\x56\x20\x00\x13\x32\x03\x66\x66\x30\x12\x21\x00\x02\x65\x00\x00\x14\x00\x00\x00\x00\x46\x66\x66\x65\x00\x00\x02\x31\x31\x00\x00\x00\x36\x52\x00\x01\x66\x66\x66\x66\x20\x01\x56\x64\x00\x00\x00\x00\x66\x66\x30\x03\x66\x66\x66\x66\x40\x15\x66\x66\x00\x00\x00\x00\x66\x66\x63\x03\x66\x66\x66\x66\x40\x56\x66\x66\x00\x00\x00\x00\x56\x66\x66\x11\x66\x66\x66\x66\x22\x66\x66\x65\x00\x00\x00\x00\x36\x66\x66\x30\x46\x66\x66\x65\x04\x66\x66\x64\x00\x00\x00\x00\x05\x66\x66\x40\x03\x66\x66\x30\x05\x66\x66\x51\x00\x00\x00\x00\x01\x56\x66\x40\x00\x01\x10\x00\x05\x66\x65\x10\x00\x00\x00\x00\x00\x02\x33\x10\x01\x23\x32\x10\x02\x44\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x46\x66\x66\x65\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x66\x66\x66\x66\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x26\x66\x66\x62\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x43\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

# Load the raspberry pi logo into the framebuffer (the image is 32x40)
fb = framebuf.FrameBuffer(buffer, 32, 40, framebuf.GS4_HMSB)

# Clear the oled display in case it has junk on it.
oled.fill(0)

# Blit the image from the framebuffer to the oled display
oled.blit(fb, 112, 0)

# Add some text
oled.text("Raspberry Pi", 5, 5, 15)
oled.text("Pico", 5, 15, 15)
if (HEIGHT > 32):
    oled.text("This display", 5, 25, 12)
    oled.text("has more than", 5, 35, 8)
    oled.text(" 32 lines", 5, 45, 4)

if (WIDTH > 128):
    oled.text("This display", 149, 25, 12)
    oled.text("has more than", 149, 35, 8)
    oled.text(" 128 pixels", 149, 45, 4)
    
# Add a color scale
for i in range(0,16):
    oled.fill_rect(i*8, 55, 8, 8,15-i)
    oled.fill_rect(247-(i*8), 55, 8, 8,15-i)
    
# Finally update the oled display so the image & text are displayed
while True:
    oled.show()
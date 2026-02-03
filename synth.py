from sh1122 import SH1122_SPI
import framebuf
from machine import Pin, SPI, ADC
import neopixel
import time
import math
import mem32
import rp2

# -- PINOUT --

# DISPLAY -  RST:3 DC:4 CS:5 SCL:6 SCA:7
spi = SPI(0,sck=Pin(6, Pin.OUT), mosi=Pin(7, Pin.OUT))
dc = Pin(4, Pin.OUT)
dc.value(0)
res = Pin(3, Pin.OUT)
res.value(1)
cs = Pin(5, Pin.OUT)
cs.value(1)
oled = SH1122_SPI(256, 64, spi, dc, res, cs)

# SIGNALS - OSC:10 GATE:11 ACC_P:12 ACC_V:13
osc_pin = Pin(10, Pin.OUT)
gate_pin = Pin(11, Pin.OUT)
acc_pitch_pin = Pin(12, Pin.OUT)
acc_volume_pin = Pin(13, Pin.OUT)

# KEYPAD - Rows: GPIO 0-2. Columns: GPIO 15-22
matrix_row = [Pin(0, Pin.IN,pull=Pin.PULL_DOWN), Pin(1, Pin.IN,pull=Pin.PULL_DOWN), Pin(2, Pin.IN,pull=Pin.PULL_DOWN)]
matrix_col = [Pin(15, Pin.OUT),Pin(16, Pin.OUT),
        Pin(17, Pin.OUT),Pin(18, Pin.OUT),
        Pin(19, Pin.OUT),Pin(20, Pin.OUT),
        Pin(21, Pin.OUT),Pin(22, Pin.OUT)]

# ENCODER - A:8 B:9 SW:14
encoder = {
    "A":Pin(8, Pin.IN, pull=Pin.PULL_UP),
    "B":Pin(9, Pin.IN, pull=Pin.PULL_UP),
    "SW":Pin(14, Pin.IN, pull=Pin.PULL_DOWN)
}

# RGB - GPIO 27
np = neopixel.NeoPixel(Pin(27), 16)

# AUDIO IN - GPIO 28
audio_in = ADC(Pin(28))


#pio for:
# encoder driver
# AB clockwise: 11 -> 01 -> 00 -> 10 -> 
# counterclock: 11 -> 10 -> 00 -> 01 ->
# if it changes, interrupt with which direction its going
# most seem to implement this with a jump table from AB<<2 + newAB
# 0000 -  S -  1000 -  C
# 0001 -  C -  1001 -  I
# 0010 - CC -  1010 -  S
# 0011 -  I -  1011 - CC
# 0100 - CC -  1100 -  I
# 0101 -  S -  1101 - CC
# 0110 -  I -  1110 -  C
# 0111 -  C -  1111 -  S

#credit to https://github.com/GitJer/Rotary_encoder for the underlying logic
# origin 0 and pc start value 16 required
@rp2.asm_pio()
def rotary_encoder_PIO():
    jmp("nothing")
    jmp("clockwise")
    jmp("counterclockwise")
    jmp("nothing")
    jmp("counterclockwise")
    jmp("nothing")
    jmp("nothing")
    jmp("clockwise")
    jmp("clockwise")
    jmp("nothing")
    jmp("nothing")
    jmp("counterclockwise")
    jmp("nothing")
    jmp("counterclockwise")
    jmp("clockwise")
    jmp("nothing")

    in(pins,2) #lets load a first new AB into ISR - program starts here
    label("nothing")
    mov(osr,isr) #put isr into osr so we can...
    out(isr,2) #shift it back into the isr (and clear it)
    in(pins,2) #add a new state of AB to get our input 
    mov(exec,isr) #jump to our table

    label("counterclockwise")
    irq(0)
    jmp("nothing")
    label("clockwise")
    irq(1)
    jmp("nothing")

rot_sm = rp2.StateMachine(0, rotary_encoder_PIO, freq=2000, in_base=(encoder["A"]))

# oscillator
# set up a simple pio square wave and poke frequency with https://forums.raspberrypi.com/viewtopic.php?t=331490
# period of wave is 64 clock cycles
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def oscillator_PIO():
    set(pins,1)
    nop() [30]
    set(pins,0)
    nop() [30]

oscillator_sm = rp2.StateMachine(2, oscillator_PIO, freq=16000, set_base=(osc_pin))
OSC_CLKDIV = 0x50200000 + 0x0f8

def set_oscillator(freq):
    clockfreq = 0
    mem32[OSC_CLKDIV] = 0 #find values later

# matrix driver
# loop through columns
# measure each row and push to ISR
@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW),sideset_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW))
def matrix_PIO():
    set(pins,1) #col 1
    in(pins,3)
    set(pins,2) #col 2
    in(pins,3)
    set(pins,4) #col 3
    in(pins,3)
    set(pins,8) #col 4
    in(pins,3)
    set(pins,0).side(1) # clear col 4, set col 5
    in(pins,3)
    nop().side(2) #col 6
    in(pins,3)
    nop().side(4) #col 7
    in(pins,3)
    nop().side(8) #col 8
    in(pins,3)
    push(noblock).side(0) #push isr to RX and clear col 8
    irq(2) #okay we're done
matrix_sm = rp2.StateMachine(5, matrix_PIO, freq=20000, in_base=(matrix_row[0]), set_base=(matrix_col[0]), sideset_base=(matrix_col[4]))

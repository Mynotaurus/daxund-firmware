from sh1122 import SH1122_SPI
import framebuf
from machine import Pin, SPI, ADC, freq, Timer, mem32
logo = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xfe\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\x00\x00\x00\x01\xff\x80\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xc0\x00\x00\x00\xff\x8f\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xc0\x00\x00\x00?\xc7\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xc0\x00\x00\x00?\xe3\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xe0\x00\x00\x00?\xe3\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xe0\x00\x00\x00\x1ea\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xe0\x00\x00\x00\x00\x01\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xc0\x00\x00\x00?\xe3\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xc0\x00\x00\x00?\xf3\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xc0\x00\x00\x00\xff\xfb\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xc0\x00\x00\x01\xff\xfb\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xc0\x00\x00\x03\xff\xff\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xc0\x00\x00\x07\xff?\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xff\xc0\x01\xc7\xe7\xfc\x0f\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xff\xc0\x0f\xcf\xef\xf8\x0f\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x0f\xff\x80\x0f\x9f\xef\xf8\x0f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc0\x00\x1f\xff\x80\x07?\xcf\xf0\x07\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x00\x1f\xff\x80\x06\x7f\xcf\xf0\x0f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xe0\x00\x1f\xff\x80\x04\xff\xdf\xf0\x0f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xe0\x00?\xff\x00\x01\xff\xdf\xf0\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xe0\x00?\xfc\x00\x01\xff\xdf\xf0\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xe0\x00?\xf8\x00\x00\xff\xdf\xf0\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xe0\x00\x7f\xe0\x00\x00\xff\xcf\xf0\x1f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xf0\x00\x7f\x80\x00\x00\xff\xef\xf8\x1f\xf3\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xf0\x00\xff\x00\x00\x00\xff\xe7\xf8\x1f\xe7\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x8f\xf0\x00\xfc\x00\x00\x00?\xf7\xf8?\xff\xff\x80\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xef\xf8\x10\xf8\x00\x00\x00\x03\xf3\xff\x7f\xff\xff\xc0\x00\x00\x07\x80\x00\x00\x00\x00\x1f\xff\xf8<\xe0\x00\x00\x00\x00\x1b\xff\xff\xff\xff\xe0\x00\x07\xff\x80\x00\x00\x00\x00\x7f\xff\xf8~\x00\x00\x00\x00\x00\x01\xff\xfb\xff\xff\xe0\x00\x03\xff\x80\x0f\x00\x00\x00\xff\xff\xf8\xff\x00\x00\x00\x00\x00\x00\x7f\xe3\xfe?\xe0\x00\x01\xff\x8f\xff\x00\x00\x00\xff\x1f\xf9\xff\x00\x00\x00\x00\x00\x00\x0f\xc3\xfc\x1f\xe0\x00\x00\xff\x8f\xfe\x00\x00\x01\xfe\x07\xfd\xff\x80\x00\x00\x00\x00\x00\x01\x03\xf0\x1f\xe0\x00\x00\xff\x87\xfe\x00\xc3\xe1\xfe\x07\xfd\xff\x80\x00\x00\x00\x00\x00\x00\x03\xc0\x1f\xff\xfe\xff\xff\x03\xfe\x07\xcf\xfd\xfc\x03\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xfc\x7f\xff\x01\xfe\x7f\x9f\xff\xfc\x03\xfc~\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xff\xff\xfc?\xff\x01\xff\xff\x9f\xff\xfc\x03\xfc<\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xdf\xff\xf8\x1f\xff\x03\xfe\x7f?\xff\xfc\x03\xfe\x10\x00\x00\x00\x00\x00\x00\x00\x01\xff\x9f\xff\xfc\x1f\xff\x03\xfe\x7f\x7f\xff\xfc\x03\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\x1f\xf7\xfe?\xff\x03\xfe?\xfd\xff\xfe\x01\xfe0\x00\x00\x00\x00\x00\x00\x00\x03\xfe\x1f\xf3\xfe}\xff\x03\xfc?\xf0\xff\xfe\x01\xffp\x00\x00\x00\x00\x00\x00\x00\x03\xfc\x0f\xf3\xffy\xff\x03\xfc?\xe0\x7f\xfe\x01\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x07\xfc\x0f\xff\xff\xf1\xfe\x03\xfc?\xe0\x7f\xff\x01\xff\xf0\x00\x00\x00\x00\x00\x00\x00\x07\xfc\x1f\xff\xff\xc1\xfe\x03\xfc?\xe0\x7f\xff\x81\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x07\xfc\x1f\xff\x7f\xe1\xfe\x03\xfc?\xe0\x7f\xff\xc3\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x03\xfe\x1f\xfe?\xf1\xfe\x07\xfc?\xe0\x7f\xff\xff\xcf\x80\x00\x00\x00\x00\x00\x00\x00\x01\xff\xff\xfc\x1f\xf0\xff\x07\xfc?\xe0\x7f\xff\xff\xc7\x80\x00\x00\x00\x00\x00\x00\x00\x00\xff\xf8\xf8?\xf8\xff\xbf\xfd\xff\xe0\x7f\xbf\xff\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xf0`\x7f\xfc\x7f\xff\xff\xff\xe0\x7f\x9f\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xc0\x01\xff\xfe\x7f\xf9\xff\xff\xe0\x7f\x8f\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xf3\xff?\xf0\xff\xbf\xe0\x7f\x808\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xe1\xff\x07\xc0\xfe?\xe0\x7f\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xe0\xff\x80\x00x?\xe0\x7f\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xc0\xff\xc0\x00`?\xe0\x7f\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\x80\xff\xc0\x00\x00?\xe0\x7f\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x80\xff\xe0\x00\x00?\xc0?\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\x00\x7f\xe0\x00\x00?\xc0\x1f\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\x00\x7f\xe0\x00\x00?\xc0\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xfe\x00\x7f\xe0\x00\x00\x7f\xc0\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xfe\x00\x7f\xe0\x00\x00\x7f\xc0\x07\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xfc\x00\x7f\xe0\x00\x00\x7f\xc0\x07\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xfc\x00\x7f\xf0\x00\x00\x7f\xc0\x03\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf8\x00\x7f\xf0\x00\x00\x7f\x80\x01\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xf8\x00?\xf0\x00\x00\x7f\x80\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xf0\x00?\xf0\x00\x00\xff\x80\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xf0\x00?\xf0\x00\x00\xff\x80\x00\x7f\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xe0\x00?\xf0\x00\x00\xff\x80\x00?\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xe0\x00?\xf8\x00\x00\xff\x80\x00?\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc0\x00\x7f\xf8\x00\x01\xff\x80\x00?\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc0\x00\x7f\xf8\x00\x01\xff\x80\x00?\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xc0\x00\xff\xf8\x00\x03\xff\x00\x00\x7f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\x80\x00\xff\xf8\x00\x03\xff\x00\x00\xff\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
# DISPLAY -  RST:3 DC:4 CS:5 SCL:6 SCA:7 - set up first so we can display a loading screen quick
spi = SPI(0,sck=Pin(6, Pin.OUT), mosi=Pin(7, Pin.OUT))
dc = Pin(4, Pin.OUT)
dc.value(0)
res = Pin(3, Pin.OUT)
res.value(1)
cs = Pin(5, Pin.OUT)
cs.value(1)
oled = SH1122_SPI(256, 64, spi, dc, res, cs, 4 * 1024 * 1024) #default is 10MHz but it adds too much noise

oled.fill(0)
logobuf = framebuf.FrameBuffer(logo,184,80,framebuf.MONO_HLSB)
oled.blit(logobuf,36,24,0)

oled.text("loading...",90,8,1)
oled.show()

import gc
gc.threshold(180000)
import neopixel
import time
import math
import rp2
import _thread
from rotary_irq_rp2 import RotaryIRQ
from synth_graphics import sprites
import json
import os
import random

print("STATUS: all libraries loaded!")
def clamp(a,l,h):
    return max(l,min(a,h))

# -- PINOUT --

freq(125_000_000)

# SIGNALS - OSC:10 GATE:11 ACC_P:12 ACC_V:13
osc_pin = Pin(10, Pin.OUT)
gate_pin = Pin(11, Pin.OUT)
gate_pin.high()
acc_pitch_pin = Pin(12, Pin.OUT)
acc_volume_pin = Pin(13, Pin.OUT)

# KEYPAD - Rows: GPIO 0-2. Columns: GPIO 15-22
matrix_row = [Pin(0, Pin.IN,pull=Pin.PULL_DOWN), Pin(1, Pin.IN,pull=Pin.PULL_DOWN), Pin(2, Pin.IN,pull=Pin.PULL_DOWN)]
matrix_col = [Pin(15, Pin.OUT),Pin(16, Pin.OUT),
        Pin(17, Pin.OUT),Pin(18, Pin.OUT),
        Pin(19, Pin.OUT),Pin(20, Pin.OUT),
        Pin(21, Pin.OUT),Pin(22, Pin.OUT)]

# ENCODER - A:8 B:9 SW:14
encoder_switch = Pin(14, Pin.IN, pull=Pin.PULL_DOWN)

rotary_encoder = RotaryIRQ(pin_num_clk=8, 
              pin_num_dt=9, 
              min_val=0, 
              max_val=19, #20 pulses per rotation
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP,
            half_step=True,
              pull_up=True)

# RGB - GPIO 27
np = neopixel.NeoPixel(Pin(27), 16)
np.fill((0,0,0))
np.write()

# AUDIO IN - GPIO 28
audio_in = ADC(Pin(28))

onboard_led = Pin("LED", Pin.OUT)

# oscillator
# set up a simple pio square wave and poke frequency with https://forums.raspberrypi.com/viewtopic.php?t=331490
# period of wave is 64 clock cycles
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def oscillator_PIO():
    set(pins,1)
    nop() [30]
    nop() [31]
    nop() [31]
    nop() [31]
    set(pins,0)
    nop() [30]
    nop() [31]
    nop() [31]
    nop() [31]
oscillator_sm = rp2.StateMachine(5, oscillator_PIO, freq=16000, set_base=(osc_pin))
OSC_CLKDIV = 0x50300000 + 0x0e0
def set_oscillator(frequency):
    if(frequency!=0):
        divider = freq() / (256 * frequency)
        mem32[OSC_CLKDIV] = int(divider) * 65536 + int((divider - int(divider))*256) * 256

# matrix driver
# loop through columns
# measure each row and push to ISR
@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW),sideset_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW))
def matrix_PIO():
    set(pins,1) #col 1
    in_(pins,3)
    set(pins,2) #col 2
    in_(pins,3)
    set(pins,4) #col 3
    in_(pins,3)
    set(pins,8) #col 4
    in_(pins,3)
    set(pins,0).side(1) # clear col 4, set col 5
    in_(pins,3)
    nop().side(2) #col 6
    in_(pins,3)
    nop().side(4) #col 7
    in_(pins,3)
    nop().side(8) #col 8
    in_(pins,3)
    push(noblock).side(0) #push isr to RX and clear col 8
    irq(0) #okay we're done
matrix_sm = rp2.StateMachine(4, matrix_PIO, freq=2000, in_base=(matrix_row[0]), set_base=(matrix_col[0]), sideset_base=(matrix_col[4]))

def get_bit(word,i):
    if (word & (1<<i)):
        return 1
    else:
        return 0

def get_button_row(b,r):
    #we want bits 0, 3, 6, 9, 12, etc etc
    temp = 0
    for i in range(8):
        temp = temp + (get_bit(b, i*3+r) << i)
    return temp

#notes are logarithmically spaced across octaves - 2^(1/12) apart
frequency_letters = ["c ","c#","d ","d#","e ","f ","f#","g ","g#","a ","a#","b "]
#lets pre-calculate those frequencies actually
frequency_mult = [1.00000,1.05946,1.12246,1.18921,1.25992,1.33484,1.41421,1.49830,1.58740,1.68179,1.78180,1.88775]

def note_to_frequency(id):
    #we'll use the midi id of the piano key from https://en.wikipedia.org/wiki/Piano_key_frequencies?useskin=vector
    #A0 is 21 is 27.5Hz so 27.5/4 = 6.875 is at -3
    return 6.875 * (2 ** int((id+3)/12)) * frequency_mult[(id+3)%12]

def update_sequencer_frequencies(): #copy our note id list into the frequency list
    for i in range(len(sequence["note"])):
        if(sequence["note"][i]==0):
            sequence["frequency"][i] = 0
        else:
            sequence["frequency"][i] = note_to_frequency(sequence["note"][i])

# 2 ^ n/16
log_16_step = [1.00000,1.04427,1.09051,1.13879,1.18921,1.24186,1.29684,1.35426,1.41421,1.47683,1.54221,1.61049,1.68179,1.75625,1.83401,1.91521,2]

sequence = {
    "tempo":120,
    "length":16,
    "swing":0,
    "note":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "frequency":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "accent_p":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "accent_v":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "hold":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "tremolo":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
}
#function to be run every sequencer tick
seq_int = { #store all internal variables in a dict to namespace it, and also make it easy to make global
    "t":0,
    "gate_time_left":0,
    "note_hold":False,
    "current_note":0,
    "next_note":0,
    "current_tremolo":0,
    "gate_length":0.5,
    "shuffle":False,
    "pause":True,
    "rgb_brightness":-1
}

def randomise_sequence():
    for i in range(15): #fisher yates shuffle yay
        swap_index = random.randint(i,15)
        temphold = sequence["note"][swap_index]
        sequence["note"][swap_index] = sequence["note"][i]
        sequence["note"][i] = temphold
    update_sequencer_frequencies()

def sequencer_update(tx):
    global seq_int, sequence, gate_pin, acc_volume_pin, acc_pitch_pin, adc_buf
    seq_substeps = 32
    #we want to run this multiple times per beat
    if(seq_int["t"] % (seq_substeps*2) == 0) or (seq_int["t"] % (seq_substeps*2) == seq_substeps + sequence["swing"]):
        if(seq_int["pause"]):
            gate_pin.high()
            acc_volume_pin.low()
            acc_pitch_pin.low()
            return
        current_beat = int((seq_int["t"])/seq_substeps)%sequence["length"]
        if(seq_int["t"] % (seq_substeps*2) == seq_substeps + sequence["swing"]):
            current_beat = int((seq_int["t"] - sequence["swing"])/seq_substeps)%sequence["length"]
        if(sequence["frequency"][current_beat]): #if theres a note rn
            if(sequence["accent_v"][current_beat]):
                acc_volume_pin.high()
            else:
                acc_volume_pin.low()
            
            if(sequence["accent_p"][current_beat]):
                acc_pitch_pin.high()
            else:
                acc_pitch_pin.low()
            
            set_oscillator(sequence["frequency"][current_beat])
            seq_int["gate_time_left"] = int(seq_int["gate_length"]*seq_substeps)
            if(seq_int["t"] % (seq_substeps*2) == seq_substeps + sequence["swing"]): #set gate length based on swing
                seq_int["gate_time_left"] = min(int(seq_int["gate_length"]*seq_substeps),(seq_substeps-sequence["swing"]-1))
            else:
                seq_int["gate_time_left"] = min(int(seq_int["gate_length"]*seq_substeps),(seq_substeps+sequence["swing"]-1))
            gate_pin.low()
            
            seq_int["current_tremolo"] = sequence["tremolo"][current_beat]
            if(seq_int["current_tremolo"]):
                seq_int["gate_time_left"] = 24
            if(sequence["hold"][current_beat] and sequence["frequency"][(current_beat+1)%sequence["length"]]):
                seq_int["note_hold"] = True
                seq_int["current_note"] = sequence["frequency"][current_beat]
                seq_int["next_note"] = sequence["frequency"][(current_beat+1)%sequence["length"]]
                seq_int["note_gap"] = (seq_int["next_note"]-seq_int["current_note"])
            else:
                seq_int["note_hold"] = False
                
        else:
            acc_volume_pin.low() #clear volume if theres no note next

    if(seq_int["note_hold"]): #update oscillator pitch when sliding
        #to save calculation, we will use lookup tables for most of the logarithmic curves
        if(seq_int["t"] % seq_substeps % 2 == 0):
            i = (seq_int["t"] % seq_substeps) >> 1
            if seq_int["note_gap"]>0:
               #f = c + (t-c) * (2^x/16 - 1) to approximate a log going up
               set_oscillator(seq_int["current_note"] + seq_int["note_gap"] * (log_16_step[i] - 1))
            else:
               #f = t + (t-c) * (1 - 2^(16-x)/16) to approximate a log going down
               set_oscillator(seq_int["next_note"] + seq_int["note_gap"] * (1 - log_16_step[16-i]))
    if(seq_int["current_tremolo"]):
        if(seq_int["gate_time_left"]>0):
            if seq_int["gate_time_left"] % (24 // (2+seq_int["current_tremolo"]*2)) == 0:
                gate_pin.toggle()
            seq_int["gate_time_left"] -= 1
        else:
            gate_pin.high()
    elif not(seq_int["note_hold"]): #standard gate timing
        if(seq_int["gate_time_left"]<=0):
            gate_pin.high()
        else:
            seq_int["gate_time_left"] -= 1
        
    if((seq_int["t"]+1) % (seq_substeps*sequence["length"]) == 0 and seq_int["shuffle"]):
        randomise_sequence()
    
    onboard_led.value(not gate_pin.value())
    seq_int["t"] += 1
sequence_tick = Timer()

def set_tempo():
    sequence_tick.deinit()
    sequence_tick.init(freq=sequence["tempo"]/15*32, mode=Timer.PERIODIC, callback=sequencer_update)
    
pal1cache = {} #cache these when generated to save time later
def pal1bpp(b):
    if b in pal1cache.keys():
        return pal1cache[b]
    pal1cache[b] = framebuf.FrameBuffer(bytearray([b]),2,1,framebuf.GS4_HMSB)
    return pal1cache[b]

def pal15_bright(b):
    pal = bytearray(8)
    temp = 0
    for i in range(16):
        if(i%2==0):
            temp = clamp(math.ceil(i * b),0,15)
        else:
            pal[i >> 1] = temp * 16 + clamp(math.ceil(i * b),0,15)
    return framebuf.FrameBuffer(pal,16,1,framebuf.GS4_HMSB)

hexsymbols = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
def write_num(num,x,y,digits=0,padding=0,pal=15):
    xoff = x
    snum = str(int(num))
    if(digits!=0):
        snum = str(num+0.00017)
        if(len(snum.split(".")[0])<padding):
            xoff += (padding - len(snum.split(".")[0])) * 12
        snum = snum.split(".")[0] + "." + snum.split(".")[1][:digits]
    else:
        if(len(snum)<padding):
            xoff += (padding - len(snum.split(".")[0])) * 12
    for i in range(len(snum)):
        if(snum[i] == "."):
            oled.blit(framebuf.FrameBuffer(sprites["font"][snum[i]],8,15,framebuf.MONO_HLSB),xoff-1,y,0,pal1bpp(pal))
            xoff += 6
        elif(snum[i] == "-"):
            oled.blit(framebuf.FrameBuffer(sprites["font"][snum[i]],8,15,framebuf.MONO_HLSB),xoff+6,y,0,pal1bpp(pal))
            xoff += 12
        else:
            oled.blit(framebuf.FrameBuffer(sprites["font"][snum[i]],16,15,framebuf.MONO_HLSB),xoff,y,0,pal1bpp(pal))
            xoff += 12
            
def load_folder_to_str(filenum):
    temp = ""
    with open("save/"+str(filenum)+".json","r") as file:
        temp = file.read()
        file.close()
    return temp

def load(filenum,slot):
    global sequence
    with open("save/"+str(filenum)+".json","r") as file:
        loadobj = json.loads(file.read())
        if str(slot) not in loadobj.keys():
            return #no file yet!
        sequence = json.loads(json.dumps(loadobj[str(slot)]))
        file.close()
    update_sequencer_frequencies()
    set_tempo()

def save(filenum,slot):
    saveobj = {}
    with open("save/"+str(filenum)+".json","r") as file:
        saveobj = json.loads(file.read())
        file.close()
    saveobj[str(slot)] = json.loads(json.dumps(sequence))
    with open("save/"+str(filenum)+".json","w") as file:
        file.write(json.dumps(saveobj))
        file.close()
        
def save_config_entry(entry,val):
    saveobj = 0
    with open("save/config.json", "r") as file:
        saveobj = json.loads(file.read())
    if not saveobj:
        print("ERROR: did not save config")
        return #break if file op failed
    saveobj[str(entry)] = val
    with open("save/config.json", "w") as file:
        file.write(json.dumps(saveobj))
    print("FILE: saved "+entry+" as "+str(val))

#core1 tasks: display and input handling
def core1():
    def take_screenshot():
        if(gc.mem_free() < 20000):
            gc.collect()
        data = oled.buffer.hex()
        print(data)
        del data
    
    
    print("STATUS: core1 booted!")
    #set up files
    files = os.listdir()
    oled.rect(0,0,256,16,0,True)
    oled.text("core1 loaded...",68,8,1)
    oled.show()
    if "save" not in files:
        os.mkdir("save")
    
    oled.rect(0,0,256,16,0,True)
    oled.text("save dir ok....",68,8,1)
    oled.show()
    files = os.listdir("save")
    for i in range(16):
        if (str(i)+".json") not in files:
            with open("save/"+str(i)+".json", "w") as file:
                print("FILE: resetting slot #"+str(i)+".")
                file.write("{}")
        oled.rect(0,0,256,16,0,True)
        oled.text("savefile"+str(i)+"ok..",68,8,1)
        oled.show()
    
    oled.rect(0,0,256,16,0,True)
    oled.text("savefiles ok...",68,8,1)
    oled.show()
    confstr = '{"rgb_brightness":1,"rgb_color_palette":0,"screensaver_enabled":false,"current_file_id":-1,"shuffle":false, "gate_length":0.5}'
    if ("config.json") not in files:
        with open("save/config.json", "w") as file:
            print("FILE: resetting config.")
            file.write(confstr)
    else:
        with open("save/config.json", "r") as file:
            confstr = file.read()
    configfile = json.loads(confstr)
    oled.rect(0,0,256,16,0,True)
    oled.text("config loaded..",68,8,1)
    #initialise variables
    t = 0
    last_rot = rotary_encoder.value()
    current_rot = last_rot
    new_rot = 0
    current_buttons = 0
    button_history = [0]
    held_buttons = 0
    new_buttons = 0
    released_buttons = 0
    last_encsw = False
    current_encsw = False
    new_encsw = False
    in_menu = False
    menu_clear_timer = 0
    menu_save_timer = 0
    menu_load_timer = 0
    menu_shuffle_timer = 0
    tempo_taps = []
    swing_taps = []
    menu_safety_hold_threshold = 30
    seq_int["rgb_color_palette"] = configfile["rgb_color_palette"]
    file_picker_page = 0
    current_file_id = configfile["current_file_id"]
    temp_file_id = -1
    temp_folder = {}
    sequence_changed = False
    screensaver_enabled = configfile["screensaver_enabled"]
    screensaver_timer = 0
    seq_int["shuffle"] = configfile["shuffle"]
    seq_int["gate_length"] = configfile["gate_length"]
    
    popup_last_used = -99999
    popup_shown = "none"
    
    last_used_note = 48
    
    i = 0
    while i < 35: #fade in logo
        oled.fill(int(min(i,1)))
        for j in range(-32,64):
            oled.line(0,j*8+i,j*8+i,0,int(min(i,3)))
        oled.blit(logobuf,36,int(24-min((i**0.5)*6,27)),0,pal1bpp(min(i+1,15)))
        oled.show()
        for j in range(16):
            rgb = [(1+math.sin(j/2+i/4))*24 * configfile["rgb_brightness"] * min(1,i/40), 0, (1+math.cos(j/2+i/4))*24 * configfile["rgb_brightness"] * min(1,i/40)]
            #palettes
            if(seq_int["rgb_color_palette"] == 6):
                average = (rgb[0]+rgb[1]+rgb[2])/3
                rgb = [average,average,average]
            elif(seq_int["rgb_color_palette"] < 3):
                rgb = [rgb[(seq_int["rgb_color_palette"])%3],rgb[(seq_int["rgb_color_palette"]+1)%3],rgb[(seq_int["rgb_color_palette"]+2)%3]]
            else:
                rgb = [
                    (rgb[(seq_int["rgb_color_palette"])%3] + rgb[(seq_int["rgb_color_palette"]+1)%3])/2,
                    (rgb[(seq_int["rgb_color_palette"]+1)%3] + rgb[(seq_int["rgb_color_palette"]+2)%3])/2,
                    (rgb[(seq_int["rgb_color_palette"]+2)%3] + rgb[(seq_int["rgb_color_palette"])%3])/2
                ]
            rgb = [clamp(int(rgb[0]),0,240),clamp(int(rgb[1]),0,240),clamp(int(rgb[2]),0,240)]
            np[j] = tuple(rgb)
        np.write()
        i+=1
        if(get_button_row(matrix_sm.get(),0)):
            i+=2
    print("STATUS: system loaded!")
    seq_int["rgb_brightness"] = configfile["rgb_brightness"] #set this here to signal to core0 we are starting up
    seq_int["pause"] = False
    oled.fill(0)
    while True:
        #outline: fetch inputs, update state, refresh display

        #first we get our current inputs
        current_rot = rotary_encoder.value()
        if(matrix_sm.rx_fifo()):
            current_buttons = matrix_sm.get()
        else:
            current_buttons = button_history[0]
        current_encsw = encoder_switch.value()
        #find any new rising edges
        new_rot = (current_rot-last_rot+10)%20-10
        new_buttons = current_buttons & ~button_history[0]
        new_encsw = current_encsw and not last_encsw
        #and falling edges
        released_buttons = button_history[0] & ~current_buttons

        #look at past button states and see which ones are being held continuously
        hold_frames = 10
        if(len(button_history)>=hold_frames):
            while len(button_history)>hold_frames:
                button_history.pop(len(button_history)-1) #keep list short
            held_buttons = 0xFFFFFF #24 bits
            for i in range(hold_frames):
                held_buttons = held_buttons & button_history[i]
                #notably this gives us past held values but this is helpful for detecting releases from held inputs
                
        #check for new inputs
        #if a modifier button is newly pressed, check for current note buttons
        #if a modifier button is currently pressed, check for new note buttons
        #if a note button is held and then released, do nothing
        # if a note button is short-pressed, then toggle it
        new_mod_buttons = get_button_row(new_buttons,0)
        current_mod_buttons = get_button_row(current_buttons,0)
        new_note_buttons = get_button_row(new_buttons,1)*256+get_button_row(new_buttons,2)
        current_note_buttons = get_button_row(current_buttons,1)*256+get_button_row(current_buttons,2)
        
        if(screensaver_enabled):
            if(current_buttons or current_encsw or new_rot):
                screensaver_timer = 0
            else:
                screensaver_timer = min(screensaver_timer+1,1000000) #stop overflows

        if(new_mod_buttons & 0b00100000): #play/pause
            seq_int["pause"] = not seq_int["pause"]
        if(new_mod_buttons & 0b00010000): #menu
            if(file_picker_page>0):
                file_picker_page = 0
            else:
                in_menu = not in_menu
        if(new_mod_buttons & 0b10000000 and current_encsw) or (current_mod_buttons & 0b10000000 and new_encsw): #screenshot
            take_screenshot()
        
        if(file_picker_page>0): #pick file
            if(file_picker_page==1): #set folder
                if(new_note_buttons):
                    for i in range(16):
                        if(new_note_buttons & 0b10000000_00000000 >> i):
                            temp_file_id = i << 4
                    temp_folder = json.loads(load_folder_to_str(temp_file_id >> 4))
                    file_picker_page += 1
            elif(file_picker_page==2): #set file
                if(new_note_buttons):
                    for i in range(16):
                        if(new_note_buttons & 0b10000000_00000000 >> i):
                            temp_file_id += i
                    file_picker_page += 1
            elif(file_picker_page==3): #doublecheck
                if(new_note_buttons & 0b01): #cancel
                    file_picker_page = 0
                elif(new_note_buttons & 0b10):
                    file_picker_page = 0
                    current_file_id = temp_file_id
                    save_config_entry("current_file_id",current_file_id)
        elif(in_menu):
            released_note_buttons = get_button_row(released_buttons,1)*256+get_button_row(released_buttons,2)
            if(new_note_buttons & 0b10000000_00000000): #adjust gate length
                seq_int["gate_length"] -= 1/16
                seq_int["gate_length"] = max(seq_int["gate_length"], 1/16)
                save_config_entry("gate_length",seq_int["gate_length"])
            elif(new_note_buttons & 0b01000000_00000000):
                seq_int["gate_length"] += 1/16
                seq_int["gate_length"] = min(seq_int["gate_length"], 1)
                save_config_entry("gate_length",seq_int["gate_length"])
            elif(new_note_buttons & 0b00000100_00000000):
                file_picker_page = 1
            elif(released_note_buttons & 0b00000001_00000000):
                in_menu = False
            elif(new_note_buttons & 0b00000000_10000000): #adjust led brightness
                if(seq_int["rgb_brightness"] == 0):
                    seq_int["rgb_brightness"] = 0.125
                else:
                    seq_int["rgb_brightness"] = seq_int["rgb_brightness"] * 2
                if(seq_int["rgb_brightness"] >= 2.4):
                    seq_int["rgb_brightness"] = 0
                save_config_entry("rgb_brightness",seq_int["rgb_brightness"])
            elif(new_note_buttons & 0b00000000_01000000): #adjust led palette
                seq_int["rgb_color_palette"] = (seq_int["rgb_color_palette"] + 1)%7
                save_config_entry("rgb_color_palette",seq_int["rgb_color_palette"])
            elif(new_note_buttons & 0b00000000_00100000): #screensaver
                screensaver_enabled = not screensaver_enabled
                save_config_entry("screensaver_enabled", screensaver_enabled)
                screensaver_timer = 0
            
            if(current_note_buttons & 0b00001000_00000000)  and current_file_id != -1:
                menu_save_timer += 1
                if(menu_save_timer == menu_safety_hold_threshold):
                    save(current_file_id >> 4,current_file_id%16)
                    sequence_changed = False
            else:
                menu_save_timer = 0
            if(current_note_buttons & 0b00000010_00000000) and current_file_id != -1:
                menu_load_timer += 1
                if(menu_load_timer == menu_safety_hold_threshold):
                    load(current_file_id >> 4,current_file_id%16)
                    sequence_changed = False
            else:
                menu_load_timer = 0
            
            if(current_note_buttons &0b00000000_00000010):
                #clear sequence
                menu_shuffle_timer += 1
                if(menu_shuffle_timer == menu_safety_hold_threshold):
                    seq_int["shuffle"] = not seq_int["shuffle"]
                    save_config_entry("shuffle", seq_int["shuffle"])
            else:
                menu_shuffle_timer = 0
            
            if(current_note_buttons &0b00000000_00000001):
                #clear sequence
                menu_clear_timer += 1
                if(menu_clear_timer == menu_safety_hold_threshold):
                    sequence_changed = True
                    for i in range(sequence["length"]):
                        sequence["note"][i] = 0
                        sequence["frequency"][i] = 0
                        sequence["accent_p"][i] = 0
                        sequence["accent_v"][i] = 0
                        sequence["hold"][i] = 0
                        sequence["tremolo"][i] = 0
            else:
                menu_clear_timer = 0
        else:
            if(current_mod_buttons & 0b01000000): #tempo change
                popup_last_used = t
                popup_shown = "tempo"
                if new_rot:
                    if current_encsw: #enable fractional bpm adjustment
                        sequence["tempo"] = clamp(int(sequence["tempo"]*20 - new_rot)/20,1,1000)
                    else:
                        sequence["tempo"] = clamp(int(sequence["tempo"]) - new_rot,1,1000)
                    tempo_taps = []
                    set_tempo()
            if(new_mod_buttons & 0b01000000 and not new_rot): #if tempo is tapped
                tempo_taps.append(time.ticks_ms())
                if(len(tempo_taps)>4):
                    if(time.ticks_diff(tempo_taps[3],tempo_taps[0])<5000):
                       delta_ms = time.ticks_diff(tempo_taps[3],tempo_taps[0])/3
                       sequence["tempo"] = clamp(int((60000 / delta_ms)/0.01)*0.01,1,1000)
                       set_tempo()
                    tempo_taps.pop(0)
            if(current_mod_buttons & 0b10000000 and not current_encsw): #swing change
                popup_last_used = t
                popup_shown = "swing"
                if new_rot:
                    sequence["swing"] = clamp(sequence["swing"] - new_rot,-24,24)
            if(new_mod_buttons & 0b10000000 and not new_rot): #if swing is tapped
                swing_taps.append(time.ticks_ms())
                if(len(swing_taps)>=4 and len(swing_taps)%2==1):
                    if(time.ticks_diff(swing_taps[4],swing_taps[0])<5000):
                       delta_ms = time.ticks_diff(swing_taps[4],swing_taps[0]) #time of two note pairs
                       swing_val = (time.ticks_diff(swing_taps[1],swing_taps[0]) + time.ticks_diff(swing_taps[3],swing_taps[2])) / delta_ms #percentage length between 0 and 1 note
                       sequence["swing"] = clamp(int((32 * swing_val - 16)),-24,24)
                    swing_taps.pop(0)
                    swing_taps.pop(0)
            if(current_mod_buttons & 0b00100000 and seq_int["pause"]): #pan cursor when paused
                seq_int["t"] = (seq_int["t"]-32*new_rot)%(32*sequence["length"])
            if(new_buttons or released_buttons): #see if the buttons have changed
                if(new_mod_buttons and current_note_buttons): #punching modifiers while holding a note
                    if(new_mod_buttons & 0b00001000): #button 5
                        for i in range(16):
                            if(current_note_buttons & 1<<i): #if holding button
                                if sequence["accent_v"][15-i] == 0:
                                    sequence["accent_v"][15-i] = 1
                                else:
                                    sequence["accent_v"][15-i] = 0
                                sequence_changed = True
                    if(new_mod_buttons & 0b00000100): #button 6
                        for i in range(16):
                            if(current_note_buttons & 1<<i): #if holding button
                                if sequence["accent_p"][15-i] == 0:
                                    sequence["accent_p"][15-i] = 1
                                else:
                                    sequence["accent_p"][15-i] = 0
                                sequence_changed = True
                    if(new_mod_buttons & 0b00000010): #button 7
                        for i in range(16):
                            if(current_note_buttons & 1<<i): #if holding button
                                if sequence["hold"][15-i] == 0:
                                    sequence["hold"][15-i] = 1
                                else:
                                    sequence["hold"][15-i] = 0
                                sequence_changed = True
                    if(new_mod_buttons & 0b00000001): #button 8
                        for i in range(16):
                            if(current_note_buttons & 1<<i): #if holding button
                                sequence["tremolo"][15-i] = (sequence["tremolo"][15-i] + 1) % 4
                                sequence_changed = True
                elif (new_note_buttons and current_mod_buttons): #punching notes while holding a modifier
                    if(current_mod_buttons & 0b00001000): #button 5
                        for i in range(16):
                            if(new_note_buttons & 1<<i): #if new button
                                if sequence["accent_v"][15-i] == 0:
                                    sequence["accent_v"][15-i] = 1
                                else:
                                    sequence["accent_v"][15-i] = 0
                                sequence_changed = True
                    if(current_mod_buttons & 0b00000100): #button 6
                        for i in range(16):
                            if(new_note_buttons & 1<<i): #if new button
                                if sequence["accent_p"][15-i] == 0:
                                    sequence["accent_p"][15-i] = 1
                                else:
                                    sequence["accent_p"][15-i] = 0
                                sequence_changed = True
                    if(current_mod_buttons & 0b00000010): #button 7
                        for i in range(16):
                            if(new_note_buttons & 1<<i): #if new button
                                if sequence["hold"][15-i] == 0:
                                    sequence["hold"][15-i] = 1
                                else:
                                    sequence["hold"][15-i] = 0
                                sequence_changed = True
                    if(current_mod_buttons & 0b00000001): #button 8
                        for i in range(16):
                            if(new_note_buttons & 1<<i): #if new button
                                sequence["tremolo"][15-i] = (sequence["tremolo"][15-i] + 1) % 4
                                sequence_changed = True
                elif(not current_mod_buttons): #toggle notes
                    released_note_buttons = get_button_row(released_buttons,1)*256+get_button_row(released_buttons,2)
                    held_note_buttons = get_button_row(held_buttons,1)*256+get_button_row(held_buttons,2)
                    for i in range(16):
                        if(released_note_buttons & ~held_note_buttons & 1<<i): #if released but not from a hold
                            if sequence["note"][15-i] == 0:
                                sequence["note"][15-i] = last_used_note
                            else:
                                sequence["note"][15-i] = 0
                            sequence_changed = True
                            update_sequencer_frequencies()
            if(current_encsw and new_rot and not current_mod_buttons): #move all notes as one
                note_clip = False
                for i in range(16):
                    if ((sequence["note"][15-i] <= 1 and new_rot>0) or (sequence["note"][15-i] >=119 and new_rot<0)) and sequence["note"][15-i] != 0:
                        note_clip = True
                if not note_clip:
                    for i in range(16):
                        if sequence["note"][15-i] != 0:
                            sequence["note"][15-i] = sequence["note"][15-i] - new_rot
                    last_used_note -= new_rot
                    last_used_note = max(last_used_note,1)
                    update_sequencer_frequencies()
                    sequence_changed = True
            elif(new_rot and current_buttons):
                for i in range(16):
                    if(current_note_buttons & 1<<i):
                        if(sequence["note"][15-i] == 0):
                            sequence["note"][15-i] = last_used_note
                        sequence["note"][15-i] -= new_rot
                        sequence["note"][15-i] = max(sequence["note"][15-i],1)
                        sequence["note"][15-i] = min(sequence["note"][15-i],119)
                        last_used_note = sequence["note"][15-i]
                        sequence_changed = True
                        update_sequencer_frequencies()
            elif(new_rot):
                last_used_note -= new_rot
                last_used_note = max(last_used_note,1)     
        
        local_t = (seq_int["t"] / 32)%sequence["length"] #t as a value of fractional beats
        if(sequence["swing"]!=0):
            if seq_int["t"] % 64 > 32 + sequence["swing"]: #if its the second beat
                #get the pair then add on a fractional amount depending on how far through a beat you are
                local_t = (int(seq_int["t"] / 64)%(sequence["length"]/2)) * 2 + 1 + ((seq_int["t"] % 64 - (32+sequence["swing"])) / (32-sequence["swing"]))
            else:
                local_t = (int(seq_int["t"] / 64)%(sequence["length"]/2)) * 2 + ((seq_int["t"] % 64) / (32+sequence["swing"]))
        if(file_picker_page==3): #check sequence
            oled.fill(0)
            if(str(temp_file_id%16) in temp_folder.keys()):
                for i in range(len(temp_folder[str(temp_file_id%16)]["note"])):
                    oled.rect(i*16,0,10,2,1,True)
                    if temp_folder[str(temp_file_id%16)]["note"][i]!=0:
                        letter = frequency_letters[temp_folder[str(temp_file_id%16)]["note"][i]%12]
                        templet = framebuf.FrameBuffer(sprites["font"][letter[0]],16,15,framebuf.MONO_HLSB)
                        oled.blit(templet,i*16,8,0,pal1bpp(15))
                        if letter[1]=="#":
                            templet = framebuf.FrameBuffer(bytearray(b"\x50\xF8\x50\xF8\x50"),8,5,framebuf.MONO_HLSB)
                            oled.blit(templet,i*16+10,8,0,pal1bpp(15))
                        if temp_folder[str(temp_file_id%16)]["accent_v"][i]!=0:
                            oled.blit(framebuf.FrameBuffer(sprites["burst"],16,6,framebuf.MONO_HLSB),i*16,1,0,pal1bpp(15))
                        if temp_folder[str(temp_file_id%16)]["accent_p"][i]!=0:
                            oled.blit(framebuf.FrameBuffer(bytearray(b"\x99\x90\x66\x60"),16,2,framebuf.MONO_HLSB),i*16,24,0,pal1bpp(15))
                        if temp_folder[str(temp_file_id%16)]["tremolo"][i]!=0:
                            oled.text("x"+str(1+temp_folder[str(temp_file_id%16)]["tremolo"][i]),i*16-2,24+temp_folder[str(temp_file_id%16)]["accent_p"][i]*3,15)
            else:
                oled.text("this sequence is empty...",16,12,4)
            oled.hline(0,32,256,4)
            oled.vline(192,32,64,4)
            oled.vline(224,32,64,4)
            oled.blit(framebuf.FrameBuffer(sprites["folder"],16,15,framebuf.MONO_HLSB),0,40,0,pal1bpp(15))
            oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[temp_file_id>>4]],16,15,framebuf.MONO_HLSB),12,40,0,pal1bpp(15))
            oled.blit(framebuf.FrameBuffer(sprites["file"],16,15,framebuf.MONO_HLSB),24,40,0,pal1bpp(15))
            oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[temp_file_id%16]],16,15,framebuf.MONO_HLSB),36,40,0,pal1bpp(15))
            oled.text("use this file?",72,48,15)
            oled.text("yep",196,48,15)
            oled.text("no",232,48,15)
        elif(file_picker_page>0): #pick file
            oled.fill(0)
            if(file_picker_page==2): #folder is selected
                oled.text("choose sequence from",4,4,15)
                oled.blit(framebuf.FrameBuffer(sprites["folder"],16,15,framebuf.MONO_HLSB),172,1,0,pal1bpp(15))
                oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[temp_file_id>>4]],16,15,framebuf.MONO_HLSB),184,1,0,pal1bpp(15))
                for i in range(8):
                    if(str(i) in temp_folder.keys()):
                        if(sum(temp_folder[str(i)]["frequency"])!=0):
                            oled.blit(framebuf.FrameBuffer(sprites["burst"],16,6,framebuf.MONO_HLSB),i*32+10,18,0,pal1bpp(15))
                    if(str(i+8) in temp_folder.keys()):
                        if(sum(temp_folder[str(i+8)]["frequency"])!=0):
                            oled.blit(framebuf.FrameBuffer(sprites["burst"],16,6,framebuf.MONO_HLSB),i*32+10,42,0,pal1bpp(15))    
            else:
                oled.text("choose folder",4,4,15)
            for i in range(8):
                oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[i]],16,15,framebuf.MONO_HLSB),i*32+10,24,0,pal1bpp(15))
                oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[i+8]],16,15,framebuf.MONO_HLSB),i*32+10,48,0,pal1bpp(15))
            oled.hline(0,40,256,4)
            oled.vline( 32,16,48,4)
            oled.vline( 64,16,48,4)
            oled.vline( 96,16,48,4)
            oled.vline(128,16,48,4)
            oled.vline(160,16,48,4)
            oled.vline(192,16,48,4)
            oled.vline(224,16,48,4)
        elif(in_menu):
            oled.fill(0)
            #fake screws
            #oled.ellipse(32,32,2,2,1,True)
            #oled.ellipse(96,32,2,2,1,True)
            #oled.ellipse(160,32,2,2,1,True)
            #oled.ellipse(224,32,2,2,1,True)
            # gate length
            oled.text("note",0,0,15)
            oled.text("len",36,0,15)
            oled.rect(61,5,2,2,15)
            write_num(seq_int["gate_length"], 12, 9, 2)
            oled.hline(1,17,7,12)
            oled.hline(56,17,7,12)
            oled.vline(59,14,7,12)
            oled.hline(8,28,48,5)
            oled.hline(8,29,48,5)
            oled.hline(8,28,int(48*seq_int["gate_length"]),15)
            oled.hline(8,29,int(48*seq_int["gate_length"]),15)
            
            #save!
            if(current_file_id > -1):
                oled.blit(framebuf.FrameBuffer(sprites["folder"],16,15,framebuf.MONO_HLSB),152,0,0,pal1bpp(15))
                oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[current_file_id>>4]],16,15,framebuf.MONO_HLSB),164,0,0,pal1bpp(15))
                oled.blit(framebuf.FrameBuffer(sprites["file"],16,15,framebuf.MONO_HLSB),176,0,0,pal1bpp(15))
                oled.blit(framebuf.FrameBuffer(sprites["font"][hexsymbols[current_file_id%16]],16,15,framebuf.MONO_HLSB),188,0,0,pal1bpp(15))
            else:
                oled.text("NO FILE", 150, 3, 15)
            if(sequence_changed):
                oled.blit(framebuf.FrameBuffer(sprites["unsaved"],32,4,framebuf.MONO_HLSB),162,16,0,pal1bpp(7))
            if(current_file_id==-1):
                oled.text("save",128,22,2)
            elif(menu_save_timer >= menu_safety_hold_threshold):
                oled.text("OK!",128+4,22,15)
            else:
                oled.text("save",128,22,15)
                oled.hline(130,30,28,4)
            if(menu_save_timer > 0 and menu_save_timer < menu_safety_hold_threshold):
                perc = menu_save_timer / menu_safety_hold_threshold
                oled.rect(128,20,int(32*perc),12,15,True)
            
            #pick!
            oled.text("set",165,22,15)
            
            #load!
            if(current_file_id==-1):
                oled.text("load",192,22,2)
            elif(menu_load_timer >= menu_safety_hold_threshold):
                oled.text("OK!",192+4,22,15)
            else:
                oled.text("load",192,22,15)
                oled.hline(194,30,28,4)
            if(menu_load_timer > 0 and menu_load_timer < menu_safety_hold_threshold):
                perc = menu_load_timer / menu_safety_hold_threshold
                oled.rect(192,20,int(32*perc),12,15,True)
            
            #back!
            oled.text("back",225,12,15)
            
            #led brightness
            oled.text("brgt",-1,49,15)
            oled.text("ness",-1,57,15)
            #0.125, 0.25, 0.5, 1, 2
            for i in range(5):
                if(seq_int["rgb_brightness"]*8 >= (1 << i)):
                    oled.rect(i*6,42-2*i,5,5+2*i,15,True)
                else:
                    oled.rect(i*6,42-2*i,5,5+2*i,5,False)
            
            #led color
            oled.text("pal",36,32,15)
            oled.text("ette",32,40,15)
            oled.blit(framebuf.FrameBuffer(sprites["font"][chr(97+seq_int["rgb_color_palette"])],16,15,framebuf.MONO_HLSB),44,48,0,pal1bpp(15))
            
            #screensaver
            oled.text("scrn",64,32,15)
            oled.text("savr",64,40,15)
            if(screensaver_enabled):
                oled.text("ON!",68,52,15)
            else:
                oled.text("off",68,52,2)
            
            #shuffle
            if(menu_shuffle_timer >= menu_safety_hold_threshold):
                oled.text("togg",192,32,15)
                oled.text("led!",192,40,15)
            else:
                oled.text("shfl",192,34,15)
                oled.hline(194,63,28,4)
                
                if(seq_int["shuffle"]):
                    oled.blit(framebuf.FrameBuffer(sprites["shuffle"],24,15,framebuf.MONO_HLSB),196,40,0,pal1bpp(15))
                    oled.text("ON!",196,56,15)
                else:
                    oled.blit(framebuf.FrameBuffer(sprites["shuffle"],24,15,framebuf.MONO_HLSB),196,40,0,pal1bpp(8))
                    oled.text("OFF",196,56,2)
            if(menu_shuffle_timer > 0 and menu_shuffle_timer < menu_safety_hold_threshold):
                perc = menu_shuffle_timer / menu_safety_hold_threshold
                oled.rect(192,56,int(32*perc),8,15,True)
            
            #clear
            if(menu_clear_timer >= menu_safety_hold_threshold):
                oled.text("empt",224,38,15)
                oled.text("ied!",224,46,15)
            else:
                oled.text("WIPE",225,38,15)
                oled.text("SEQU",225,46,15)
                oled.text("ENCE",225,54,15)
                oled.hline(226,63,28,4)
            if(menu_clear_timer > 0 and menu_clear_timer < menu_safety_hold_threshold):
                perc = menu_clear_timer / menu_safety_hold_threshold
                oled.rect(224,32,int(32*perc),32,15,True)
            
                
            # dividers
            oled.hline(0,32,256,1)
            oled.vline( 32,32,32,1)
            oled.vline( 64, 0,64,1)
            oled.vline( 96, 0,64,1)
            oled.vline(128, 0,64,1)
            oled.vline(160,32,32,1)
            oled.vline(192,32,32,1)
            oled.vline(224, 0,64,1)
        else:
            oled.fill(0)
            if not(screensaver_enabled and screensaver_timer == 120): #dont draw the sweeper on the frame we activate screensaver
                oled.vline(int(local_t * 256 / sequence["length"]),2,32,1)
            for i in range(len(sequence["note"])):
                if sequence["hold"][i]!=0:
                    oled.rect(i*16+2,0,22,3,1,True)
                    if i==15:
                        oled.rect(-14,0,22,3,1,True)
                if(i%2==0):
                    oled.rect(i*16,1,10+math.ceil(sequence["swing"]/2),4,1, True)
                else:
                    oled.rect(i*16+math.ceil(sequence["swing"]/2),1,10-math.ceil(sequence["swing"]/2),4,1, True)
            for i in range(len(sequence["note"])):
                if sequence["note"][i]!=0:
                    letter = frequency_letters[sequence["note"][i]%12]
                    letspr = framebuf.FrameBuffer(sprites["font"][letter[0]],16,15,framebuf.MONO_HLSB)
                    oled.blit(letspr,i*16,24-int(sequence["note"][i]/4),0,pal1bpp(15))
                    del letspr
                    if letter[1]=="#":
                        oled.blit(framebuf.FrameBuffer(bytearray(b"\x50\xF8\x50\xF8\x50"),8,5,framebuf.MONO_HLSB),i*16+10,24-int(sequence["note"][i]/4),0,pal1bpp(15))
                    if sequence["accent_v"][i]!=0:
                        oled.blit(framebuf.FrameBuffer(sprites["burst"],16,6,framebuf.MONO_HLSB),i*16,17-int(sequence["note"][i]/4),0,pal1bpp(15))
                    if sequence["accent_p"][i]!=0:
                        oled.blit(framebuf.FrameBuffer(bytearray(b"\x99\x90\x66\x60"),16,2,framebuf.MONO_HLSB),i*16,40-int(sequence["note"][i]/4),0,pal1bpp(15))
                    if sequence["tremolo"][i]!=0:
                        oled.text("x"+str(1+sequence["tremolo"][i]),i*16-2,40+sequence["accent_p"][i]*2-int(sequence["note"][i]/4),15)
            oled.hline(0,44,256,15)
            if(seq_int["pause"]):
                oled.rect(18,50,4,12,12,True)
                oled.rect(24,50,4,12,12,True)
            else:
                oled.blit(framebuf.FrameBuffer(sprites["speech_bubble_end"],16,12,framebuf.MONO_HLSB),16,44,-1,pal1bpp(15))
            if(int(seq_int["t"] / 32)%16==12 or (seq_int["pause"] and int(t/5)%16==15)):
                oled.blit(framebuf.FrameBuffer(sprites["dog"]["blink"],16,12,framebuf.MONO_HLSB),-1,52-int(seq_int["t"] / 128)%2,0,pal1bpp(15))
            else:
                oled.blit(framebuf.FrameBuffer(sprites["dog"]["neutral"],16,12,framebuf.MONO_HLSB),-1,52-int(seq_int["t"] / 128)%2,0,pal1bpp(15))
                oled.vline(9,56-int(seq_int["t"] / 128)%2,2,6)
            oled.hline(0,63,8,15)
            
            letter = frequency_letters[last_used_note%12]
            oled.blit(framebuf.FrameBuffer(sprites["font"][letter[0]],16,15,framebuf.MONO_HLSB),233,48,0,pal1bpp(6))
            if letter[1]=="#":
                oled.blit(framebuf.FrameBuffer(bytearray(b"\x50\xF8\x50\xF8\x50"),8,5,framebuf.MONO_HLSB),242,48,0,pal1bpp(6))
            oled.text(str(int((last_used_note+3)/12)-1),242,56,6)
            
            if(popup_shown == "tempo" and t == popup_last_used):
                    oled.rect(30,26,64,48,0,True)
                    oled.rect(30,26,64,48,15)
                    oled.blit(framebuf.FrameBuffer(sprites["tempo"],48,15,framebuf.MONO_HLSB),40,28,0,pal1bpp(15))
                    oled.blit(framebuf.FrameBuffer(sprites["turn_knob"],40,4,framebuf.MONO_HLSB),44,42,0,pal1bpp(10))
                    write_num(sequence["tempo"],32,48,0,3,15)
                    oled.text("bpm", 67, 56, 15)
                    if not sequence["tempo"] == int(sequence["tempo"]):
                        if(sequence["tempo"]%1 >= 0.1):
                            oled.text(str(int((sequence["tempo"]%1)*100)), 67, 48, 14)
                        else:
                            oled.text("0"+str(int((sequence["tempo"]%1)*100)), 67, 48, 14)
            else:
                    write_num(sequence["tempo"],32,48,0,3,6)
                    oled.text("bpm", 67, 56, 6)
                    if not sequence["tempo"] == int(sequence["tempo"]):
                        if(sequence["tempo"]%1 >= 0.1):
                            oled.text(str(int((sequence["tempo"]%1)*100)), 67, 48, 5)
                        else:
                            oled.text("0"+str(int((sequence["tempo"]%1)*100)), 67, 48, 5)
            if(popup_shown == "swing" and t == popup_last_used):
                oled.rect(94,26,64,48,0,True)
                oled.rect(94,26,64,48,15)
                oled.blit(framebuf.FrameBuffer(sprites["swing"],48,15,framebuf.MONO_HLSB),107,28,0,pal1bpp(15))
                oled.blit(framebuf.FrameBuffer(sprites["turn_knob"],40,4,framebuf.MONO_HLSB),107,42,0,pal1bpp(10))
                write_num(32+sequence["swing"],100,48,0,2,15)
                oled.line(128,48,122,64,15)
                write_num(32-sequence["swing"],130,48,0,2,15)
            else:
                write_num(32+sequence["swing"],100,48,0,2,6)
                oled.line(128,48,122,64,6)
                write_num(32-sequence["swing"],130,48,0,2,6)
            if(sequence_changed):
                oled.blit(framebuf.FrameBuffer(sprites["unsaved"],32,4,framebuf.MONO_HLSB),224,39,0,pal1bpp(3))
            if(seq_int["shuffle"]):
                if(local_t>15.5 or local_t<0.5):
                    oled.blit(framebuf.FrameBuffer(sprites["shuffle"],24,15,framebuf.MONO_HLSB),196,48,0,pal1bpp(12))
                else:
                    oled.blit(framebuf.FrameBuffer(sprites["shuffle"],24,15,framebuf.MONO_HLSB),196,48,0,pal1bpp(9))
        #for i in range(24):
        #    if(last_buttons & (1 << i)):
        #        oled.fill_rect((24-i)*3, 28+(i%3)*9, 8, 8,6)
        #    else:
        #        oled.fill_rect((24-i)*3, 28+(i%3)*9, 8, 8,2)
        #if(encoder_switch.value()):   
        #    oled.fill_rect(90, 28, 8, 8, 6)
        #else:
        #    oled.fill_rect(90, 28, 8, 8, 2)
            
        #if(new_rot<0):   
        #    oled.fill_rect(83, 28, 6, 4, 6)
        #else:
        #    oled.fill_rect(83, 28, 6, 4, 2)
        
        #if(new_rot>0):   
        #    oled.fill_rect(99, 28, 6, 4, 6)
        #else:
        #    oled.fill_rect(99, 28, 6, 4, 2)

        if screensaver_enabled and screensaver_timer == 120:
            scrn = framebuf.FrameBuffer(oled.buffer,256,64,framebuf.GS4_HMSB)
            oled.blit(scrn, 0,0,-1, pal15_bright(0.25))
            del scrn
            if(in_menu):
                oled.rect(0,48,256,16,0,True)
            else:
                oled.rect(32,48,224,16,0,True)
                oled.rect(-1,48,12,16,0,True)
            oled.text("SCREENSAVER ACTIVE",60,48,12)
            oled.text("press any key to wake",44,56,12)
            oled.blit(framebuf.FrameBuffer(sprites["dog"]["blink"],16,12,framebuf.MONO_HLSB),-1,52,-1,pal1bpp(15))
            oled.text("z",13,48,15)
            oled.show()
            take_screenshot()
        if (not screensaver_enabled or screensaver_timer < 120):
            oled.show()
        last_rot = current_rot
        button_history.insert(0,current_buttons)
        last_encsw = current_encsw
        t+=1

_thread.stack_size(0)
_thread.start_new_thread(core1, ())

#core0 tasks: recieving interrupts and handling LEDs in idle time
matrix_sm.active(1)
oscillator_sm.active(1)
while True: #idling loop to wait for core1 to init
    try:
        if seq_int["rgb_brightness"] != -1:
            break
    except:
        pass

#start sequencer after load so it cant interrupt file operations
sequence_tick = Timer(freq=256, mode=Timer.PERIODIC, callback=sequencer_update)

def neopixel_refresh():
    global sequence, seq_int
    pixel_cols = [28.0, 39.5, 48.2, 51.9, 49.8, 42.3, 31.4, 19.6, 9.8, 4.5, 4.9, 11.1]
    while True:
        plocal_t = (seq_int["t"] / 32)%sequence["length"]
        if(sequence["swing"]!=0):
            if seq_int["t"] % 64 > 32 + sequence["swing"]: #if its the second beat
                #get the pair then add on a fractional amount depending on how far through a beat you are
                plocal_t = (int(seq_int["t"] / 64)%(sequence["length"]/2)) * 2 + 1 + ((seq_int["t"] % 64 - (32+sequence["swing"])) / (32-sequence["swing"]))
            else:
                plocal_t = (int(seq_int["t"] / 64)%(sequence["length"]/2)) * 2 + ((seq_int["t"] % 64) / (32+sequence["swing"]))
        np.fill((0,0,0))
        for i in range(16):
            if(sequence["note"][15-i]):
                #base color
                rgb = [pixel_cols[int(sequence["note"][15-i]%12)], 0, pixel_cols[int((sequence["note"][15-i]+6)%12)]]

                if(sequence["tremolo"][15-i]):
                    rgb[1] = sequence["tremolo"][15-i]*12
                #brightness for accents
                if(sequence["accent_v"][15-i]):
                    rgb = [rgb[0]*1.2,rgb[1]*1.2,rgb[2]*1.2]
                if(sequence["accent_p"][15-i]):
                    rgb = [rgb[0]*1.1,rgb[1]*1.1,rgb[2]*1.1]
                br = seq_int["rgb_brightness"]
                rgb = [rgb[0] * br, rgb[1] * br, rgb[2] * br]
                #palettes
                pal = seq_int["rgb_color_palette"]
                if(pal == 6):
                    average = (rgb[0]+rgb[1]+rgb[2])/3
                    rgb = [average,average,average]
                elif(pal < 3):
                    rgb = [rgb[(pal)%3],rgb[(pal+1)%3],rgb[(pal+2)%3]]
                else:
                    rgb = [
                        (rgb[(pal)%3] + rgb[(pal+1)%3])/2,
                        (rgb[(pal+1)%3] + rgb[(pal+2)%3])/2,
                        (rgb[(pal+2)%3] + rgb[(pal)%3])/2
                    ]                                      
                #normalisation yayy
                rgb = [clamp(int(rgb[0]),0,240),clamp(int(rgb[1]),0,240),clamp(int(rgb[2]),0,240)]
                np[i] = tuple(rgb)
                del rgb
            
            if(15-i == int(plocal_t) and seq_int["rgb_brightness"] > 0):
                chaser_brightness = clamp(int(6*seq_int["rgb_brightness"]),1,15)
                np[i] = (np[i][0] + chaser_brightness,np[i][1] + chaser_brightness,np[i][2] + chaser_brightness)
        np.write()

gc.enable() #automatic garbage collection
neopixel_refresh()

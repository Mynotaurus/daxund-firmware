from sh1122 import SH1122_SPI
import framebuf
from machine import Pin, SPI, ADC, freq, Timer
import neopixel
import time
import math
import mem32
import rp2
import _thread

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
oled.fill(0)

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
oscillator_sm = rp2.StateMachine(1, oscillator_PIO, freq=16000, set_base=(osc_pin))
OSC_CLKDIV = 0x50200000 + 0x0e0
def set_oscillator(frequency):
    if(frequency!=0):
        divider = freq() / (64 * frequency)
        mem32[OSC_CLKDIV] = math.floor(divider) * 2**16 + math.floor((divider - math.floor(divider))*256) * 2**8

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
    irq(0) #okay we're done
matrix_sm = rp2.StateMachine(5, matrix_PIO, freq=20000, in_base=(matrix_row[0]), set_base=(matrix_col[0]), sideset_base=(matrix_col[4]))

input_buffer = []
def pio0_input_handler(sm):
    #we recieve an interrupt from PIO0 but we have to figure out which it is
    irq_id = rp2.PIO(0).irq().flags() #256 for irq0, 512 for irq1, 1024 for irq2, 2048 for irq3
    if(irq_id==256):
        input_buffer.push("CW")
    if(irq_id==512):
        input_buffer.push("CCW")

current_button_input = 0
def pio1_input_handler(sm):
    #we recieve an interrupt from PIO1 but we have to figure out which it is
    irq_id = rp2.PIO(1).irq().flags() #256 for irq0, 512 for irq1, 1024 for irq2, 2048 for irq3
    if(irq_id==256):
        matrix_value = sm.get()
        if(matrix_value!=current_button_input): #only report changes
            input_buffer.push(matrix_value)
            current_button_input = matrix_value

def rot_button_handler():
    if(encoder["SW"].value()):
        input_buffer.push("E_P")
    else:
        input_buffer.push("E_R")

sequence = {
    "length":16,
    "note":[],
    "accent":[],
    "gate_length":0.5
}

#function to be run every sequencer tick
sequencer_time=0
gate_time_left = 0
def sequencer_update():
    seq_substeps = 32
    #we want to run this multiple times per beat
    if(sequencer_time%seq_substeps == 0):
        current_beat = math.floor(sequencer_time/seq_substeps)%sequence["length"]
        if(sequence["note"][current_beat]): #if theres a note rn
            set_oscillator(sequence["note"][current_beat])
            gate_time_left = math.floor(sequence["gate_length"] * seq_substeps)
            gate_pin.low()
            if(sequence["accent"][current_beat]):
                acc_volume_pin.high()
                acc_pitch_pin.high()
            else:
                acc_volume_pin.low()
                acc_pitch_pin.low()
        else:
            acc_volume_pin.low() #clear accents if theres no note next
            acc_pitch_pin.low()

    if(gate_time_left<=0):
        gate_pin.high()
    else:
        gate_time_left -= 1
        

    #gradual changes like slides
    sequencer_time+=1

#core1 tasks: display and input handling
def core1():
    while True:
        #outline: fetch inputs, update state, refresh display
        

        for i in range(0,16):
            oled.fill_rect(i*8, 28+math.sin(t/100)*25, 8, 8,15-i)
            oled.fill_rect(247-(i*8), 28+math.sin(t/100)*25, 8, 8,15-i)
        t+=1

_thread.start_new_thread(core1)

#core0 tasks: recieving interrupts
rot_sm.irq(pio0_input_handler)
matrix_sm.irq(pio1_input_handler)
encoder["SW"].irq(rot_button_handler, trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING)
sequence_tick = Timer(0,freq=5000, mode=Timer.PERIODIC, callback=sequencer_update,hard=True)
while True:
    pass
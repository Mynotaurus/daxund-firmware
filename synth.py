from sh1122 import SH1122_SPI
import framebuf
from machine import Pin, SPI, ADC, freq, Timer, mem32
import neopixel
import time
import math
import rp2
import _thread
from rotary_irq_rp2 import RotaryIRQ
from synth_graphics import sprites

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
encoder_switch = Pin(14, Pin.IN, pull=Pin.PULL_DOWN)

rotary_encoder = RotaryIRQ(pin_num_clk=8, 
              pin_num_dt=9, 
              min_val=0, 
              max_val=19, #20 pulses per rotation
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP,
              pull_up=True)

# RGB - GPIO 27
np = neopixel.NeoPixel(Pin(27), 16)

# AUDIO IN - GPIO 28
audio_in = ADC(Pin(28))

# oscillator
# set up a simple pio square wave and poke frequency with https://forums.raspberrypi.com/viewtopic.php?t=331490
# period of wave is 64 clock cycles
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def oscillator_PIO():
    set(pins,1)
    nop() [30]
    set(pins,0)
    nop() [30]
oscillator_sm = rp2.StateMachine(5, oscillator_PIO, freq=16000, set_base=(osc_pin))
OSC_CLKDIV = 0x50300000 + 0x0e0
def set_oscillator(frequency):
    if(frequency!=0):
        divider = freq() / (64 * frequency)
        mem32[OSC_CLKDIV] = math.floor(divider) * 65536 + math.floor((divider - math.floor(divider))*256) * 256

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
matrix_sm = rp2.StateMachine(4, matrix_PIO, freq=20000, in_base=(matrix_row[0]), set_base=(matrix_col[0]), sideset_base=(matrix_col[4]))

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
frequency_letters = ["A ","A#","B ","C ","C#","D ","D#","E ","F ","F#","G ","G#"]
#lets pre-calculate those frequencies actually
frequency_mult = [1.00000,1.05946,1.12246,1.18921,1.25992,1.33484,1.41421,1.49830,1.58740,1.68179,1.78180,1.88775]

def letter_to_frequency(id):
    #we'll use the number of the piano key from https://en.wikipedia.org/wiki/Piano_key_frequencies?useskin=vector shifted up by 2 octaves
    #A0 is 27.5Hz so our 0 is 27.5/4 = 6.875
    return 6.875 * (2 ** math.floor((id-1)/12)) * frequency_mult[(id-1)%12]

def update_sequencer_frequencies(): #copy our note id list into the frequency list
    for i in range(len(sequence["note"])):
        if(sequence["note"][i]==0):
            sequence["frequency"][i] = 0
        else:
            sequence["frequency"][i] = letter_to_frequency(sequence["note"][i])

# 2 ^ n/16
log_16_step = [1.00000,1.04427,1.09051,1.13879,1.18921,1.24186,1.29684,1.35426,1.41421,1.47683,1.54221,1.61049,1.68179,1.75625,1.83401,1.91521]

sequence = {
    "tempo":120,
    "length":16,
    "note":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "frequency":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "accent":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "hold":[0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    "gate_length":0.5,
    "pause":False
}
#function to be run every sequencer tick
seq_int = { #store all internal variables in a dict to namespace it, and also make it easy to make global
    "t":0,
    "gate_time_left":0,
    "note_hold":False,
    "current_note":0,
    "next_note":0
}
def sequencer_update(tx):
    global seq_int, sequence, gate_pin, acc_volume_pin, acc_pitch_pin, adc_buf
    seq_substeps = 32
    #we want to run this multiple times per beat
    if(seq_int["t"] % seq_substeps == 0):
        if(sequence["pause"]):
            gate_pin.high()
            acc_volume_pin.low()
            acc_pitch_pin.low()
            return
        current_beat = math.floor(seq_int["t"]/seq_substeps)%sequence["length"]
        if(sequence["frequency"][current_beat]): #if theres a note rn
            if(sequence["accent"][current_beat]):
                acc_volume_pin.high()
                acc_pitch_pin.low()
            else:
                acc_volume_pin.low()
                acc_pitch_pin.high()
            
            set_oscillator(sequence["frequency"][current_beat])
            seq_int["gate_time_left"] = math.floor(sequence["gate_length"] * seq_substeps)
            gate_pin.low()
            
            if(sequence["hold"][current_beat] and sequence["frequency"][(current_beat+1)%sequence["length"]]):
                seq_int["note_hold"] = True
                seq_int["current_note"] = sequence["frequency"][current_beat]
                seq_int["next_note"] = sequence["frequency"][(current_beat+1)%sequence["length"]]
                seq_int["note_gap"] = (seq_int["next_note"]-seq_int["current_note"])
            else:
                seq_int["note_hold"] = False
        else:
            acc_volume_pin.low() #clear volume if theres no note next

    if(seq_int["note_hold"]): #update oscillator pitch
        #to save calculation, we will use lookup tables for most of the logarithmic curves
        if(seq_int["t"] % seq_substeps % 2 == 0):
            i = (seq_int["t"] % seq_substeps) >> 1
            if seq_int["note_gap"]>0:
               #f = c + (t-c) * (2^x/16 - 1) to approximate a log going up
               set_oscillator(seq_int["current_note"] + seq_int["note_gap"] * (log_16_step[i] - 1))
            else:
               #f = c + (t-c) * (2^(16-x)/16 - 1) to approximate a log going down
               set_oscillator(seq_int["current_note"] + seq_int["note_gap"] * (log_16_step[15-i] - 1))
    else: #standard gate timing
        if(seq_int["gate_time_left"]<=0):
            gate_pin.high()
        else:
            seq_int["gate_time_left"] -= 1
        

    #gradual changes like slides
    seq_int["t"] += 1
sequence_tick = Timer()
def set_tempo():
    sequence_tick.deinit()
    sequence_tick.init(freq=sequence["tempo"]/15*32, mode=Timer.PERIODIC, callback=sequencer_update)

pal1bpp_15 = framebuf.FrameBuffer(bytearray([0x0F]),2,1,framebuf.GS4_HMSB)
#core1 tasks: display and input handling
def core1():
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
    
    last_used_note = 39
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
        
        if(new_mod_buttons & 0b10000000 or get_button_row(held_buttons,0) & 0b10000000): #tempo up
            sequence["tempo"] = sequence["tempo"] + 1
            set_tempo()
        if(new_mod_buttons & 0b01000000 or get_button_row(held_buttons,0) & 0b01000000): #tempo down
            sequence["tempo"] = sequence["tempo"] - 1
            set_tempo()
        
        if(new_buttons or released_buttons): #see if the buttons have changed
            
            if(new_mod_buttons and current_note_buttons): #punching modifiers while holding a note
                if(new_mod_buttons & 0b00001000): #button 5
                    for i in range(16):
                        if(current_note_buttons & 1<<i): #if holding button
                            if sequence["accent"][15-i] == 0:
                                sequence["accent"][15-i] = 1
                            else:
                                sequence["accent"][15-i] = 0
                if(new_mod_buttons & 0b00000100): #button 6
                    for i in range(16):
                        if(current_note_buttons & 1<<i): #if holding button
                            if sequence["hold"][15-i] == 0:
                                sequence["hold"][15-i] = 1
                            else:
                                sequence["hold"][15-i] = 0
            elif (new_note_buttons and current_mod_buttons): #punching notes while holding a modifier
                pass
            elif (new_mod_buttons):
                if(new_mod_buttons & 0b00100000): #play/pause
                    sequence["pause"] = not sequence["pause"]
                    
            else:
                released_note_buttons = get_button_row(released_buttons,1)*256+get_button_row(released_buttons,2)
                held_note_buttons = get_button_row(held_buttons,1)*256+get_button_row(held_buttons,2)
                for i in range(16):
                    if(released_note_buttons & ~held_note_buttons & 1<<i): #if released but not from a hold
                        if sequence["note"][15-i] == 0:
                            sequence["note"][15-i] = last_used_note
                        else:
                            sequence["note"][15-i] = 0
                        update_sequencer_frequencies()
        
        if(new_rot and current_buttons):
            note_buttons = get_button_row(current_buttons,1)*256+get_button_row(current_buttons,2)
            for i in range(16):
                if(note_buttons & 1<<i):
                    if(sequence["note"][15-i] == 0):
                        sequence["note"][15-i] = last_used_note
                    sequence["note"][15-i] += new_rot
                    sequence["note"][15-i] = max(sequence["note"][15-i],1)
                    sequence["note"][15-i] = min(sequence["note"][15-i],119)
                    last_used_note = sequence["note"][15-i]
                    update_sequencer_frequencies()
        elif(new_rot):
            last_used_note += new_rot
            last_used_note = max(last_used_note,1)
        
        oled.fill(0)
        oled.hline(0,44,256,15)
        oled.vline(math.floor(((seq_int["t"] / 32)%sequence["length"]) * 256 / sequence["length"]),2,32,1)
        for i in range(len(sequence["note"])):
            if sequence["hold"][i]!=0:
                oled.rect(i*16+2,0,22,3,1,True)
            oled.rect(i*16,1,10,4,1,True)
            if sequence["note"][i]!=0:
                subletter = ["a","a","b","c","c","d","d","e","f","f","g","g"]            
                templet = framebuf.FrameBuffer(sprites["font"][subletter[sequence["note"][i]%12]],16,15,framebuf.MONO_HLSB)
                oled.blit(templet,i*16,24-math.floor(sequence["note"][i]/4),0,pal1bpp_15)
                if sequence["note"][i]%12 in [1,4,6,9,11]:
                    templet = framebuf.FrameBuffer(bytearray(b"\x50\xF8\x50\xF8\x50"),8,5,framebuf.MONO_HLSB)
                    oled.blit(templet,i*16+10,24-math.floor(sequence["note"][i]/4),0,pal1bpp_15)
                if sequence["accent"][i]!=0:
                    oled.rect(i*16,40-math.floor(sequence["note"][i]/4),12,3,15,True)
        oled.blit(framebuf.FrameBuffer(sprites["speech_bubble_end"],16,12,framebuf.MONO_HLSB),16,44,-1,pal1bpp_15)
        oled.blit(framebuf.FrameBuffer(sprites["dog"]["neutral"],16,12,framebuf.MONO_HLSB),0,52+math.floor(seq_int["t"] / 128)%2,0,pal1bpp_15)
        oled.text(frequency_letters[last_used_note%12]+"-"+str(math.floor(last_used_note/12))+" "+str(last_used_note), 24, 56, 12)
        oled.text(str(sequence["tempo"]), 128, 56, 12)
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
        
        for i in range(16):
            if(sequence["note"][15-i]):
                np[i] = (math.floor(32+24*math.sin((sequence["note"][15-i]%12)/2)), 0, math.floor(32+24*math.cos((sequence["note"][15-i]%12)/2)))                
            else:
                np[i] = (0,0,0)
                
            if(15-i == math.floor(seq_int["t"] / 32)%16):
                np[i] = (np[i][0] + 4,np[i][1] + 4,np[i][2] + 4)
            np.write()
            
        oled.show()

        last_rot = current_rot
        button_history.insert(0,current_buttons)
        last_encsw = current_encsw
        t+=1

_thread.start_new_thread(core1, ())

#core0 tasks: recieving interrupts
sequence_tick = Timer(freq=256, mode=Timer.PERIODIC, callback=sequencer_update)
matrix_sm.active(1)
oscillator_sm.active(1)
while True:
    pass
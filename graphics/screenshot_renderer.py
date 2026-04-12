from PIL import Image
import serial
import re
conn = serial.Serial("COM4", 115200, timeout=0)
response = ""
validscr = re.compile(r"([0-9a-f]{16384})")

while True:
    new = conn.read()
    if(new.isalnum()):
        response += new.decode()
        if validscr.match(response):
            print("screenshot detected!")
            hexdump = validscr.match(response).group()
            bytestr = ""
            remap_table = {
                "0":"00", "1":"80", "2":"88", "3":"90",
                "4":"98", "5":"A0", "6":"A8", "7":"B0",
                "8":"B8", "9":"C0", "a":"C8", "b":"D0",
                "c":"D8", "d":"E0", "e":"E8", "f":"FF",
            }
            for i in range(len(hexdump)):
                bytestr += remap_table[hexdump[i]]
            im = Image.frombytes("L",(256,64),bytearray.fromhex(bytestr))

            im = im.crop((-4,-4,260,68))
            im = im.resize((1048,288), Image.Resampling.NEAREST)
            im.show()
            response = ""
    else:
        response = ""
    
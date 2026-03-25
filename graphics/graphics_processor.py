from PIL import Image
import math
results = {}
files = ["font_0.png","font_1.png","font_2.png","font_3.png","font_4.png",
         "font_5.png","font_6.png","font_7.png","font_8.png","font_9.png"]
for file_name in files:
    data = bytearray()
    with Image.open("C:/Users/Kirlia/Documents/synth/graphics/"+file_name) as im:
        for y in range(im.height):
            char = 0
            for x in range(8*math.ceil((im.width)/8)):
                char*=2
                if x < im.width:
                    if(im.getpixel((x,y))==1):
                        char += 1
                        print('#', end='')
                    else:
                        print('.', end='')
                if x%8 == 7:
                    data.append(char)
                    char = 0
            print('')

    print(data)
    results[file_name] = data
print(results)

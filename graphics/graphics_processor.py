from PIL import Image
import math
results = {}
files = ["burst.png"]
for file_name in files:
    data = bytearray()
    with Image.open("C:/Users/Kirlia/Documents/synth/graphics/"+file_name) as im:
        for y in range(im.height):
            char = 0
            for x in range(8*math.ceil((im.width)/8)):
                char*=2
                if x < im.width:
                    if(len(im.mode)>1):
                        if(im.getpixel((x,y))[0]):
                            char += 1
                            print('#', end='')
                        else:
                            print('.', end='')
                    elif(im.getpixel((x,y))):
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

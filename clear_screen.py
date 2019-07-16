from sense_hat import SenseHat
import sys

sense = SenseHat()

def set_base_layout(max):
    idx = max
    y_offset = 7

    while idx >= max - 7:
        if idx == 26:
            for x in range(0, 8):
                sense.set_pixel(x, y_offset, Y)
        elif idx == 28:
            for x in range(0, 8):
                sense.set_pixel(x, y_offset, R)
        else:
            for x in range(0, 8):
                sense.set_pixel(x, y_offset, N)

        idx -= 1
        y_offset -= 1

N = (0, 0, 0)       # null
R = (244, 67, 54)   # Red
Y = (255, 235, 59)  # Yellow
O = (63, 81, 181)   # Outdoors
I = (76, 175, 80)   # Indoors
M = (110, 188, 164) # Indoor and outdoor mixed
B = (33, 150, 243)  # Blue, no network connection

if len(sys.argv) != 2:
    print 'Invalid argument'
    print 'Usage: python clear_screen.py <max_temp>, where <max_temp> is the temperature of the top-most line of the display'
    exit
else:
    max_temp = int(sys.argv[1]) 
    set_base_layout(max_temp)

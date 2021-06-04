from sense_hat import SenseHat
import sys

sense = SenseHat()

WARM_TEMPERATURE = 26
HOT_TEMPERATURE = 28
PIXEL_DISPLAY_WIDTH = 7
PIXEL_COLORS = {
    "NULL": [0, 0, 0],
    "RED": [244, 67, 54],
    "YELLOW": [255, 235, 59],
}

def set_base_layout(max_temp):
    idx = max_temp
    y_offset = PIXEL_DISPLAY_WIDTH

    while idx >= max_temp - PIXEL_DISPLAY_WIDTH:
        if idx == WARM_TEMPERATURE:
            for x in range(0, 8):
                sense.set_pixel(x, y_offset, PIXEL_COLORS["YELLOW"])
        elif idx == HOT_TEMPERATURE:
            for x in range(0, 8):
                sense.set_pixel(x, y_offset, PIXEL_COLORS["RED"])
        else:
            for x in range(0, 8):
                sense.set_pixel(x, y_offset, PIXEL_COLORS["NULL"])

        idx -= 1
        y_offset -= 1


if len(sys.argv) != 2:
    print 'Invalid argument'
    print 'Usage: python clear_screen.py <max_temp>, where <max_temp> is the temperature of the top-most line of the display'
    exit
else:
    max_temp = int(sys.argv[1]) 
    set_base_layout(max_temp)

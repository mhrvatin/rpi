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

def draw_reference_lines(max_temp):
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

def remove_reference_lines():
    for x in xrange(0, 8):
        for y in xrange(0, 8):
            pixel = sense.get_pixel(x, y)

            if pixel == PIXEL_COLORS["RED"] or pixel == PIXEL_COLORS["YELLOW"]:
                sense.set_pixel(x, y, PIXEL_COLORS["NULL"])

def shift_hours_down():
    for x in xrange(0, 8):
        for y in xrange(0, 7):
            sense.set_pixel(x, y, sense.get_pixel(x, y + 1))

    for x in xrange(0, 8):
        sense.set_pixel(x, 7, PIXEL_COLORS["NULL"])

if len(sys.argv) != 2:
    print 'Invalid argument'
    print 'Usage: python clear_screen.py <max_temp>, where <max_temp> is the temperature of the top-most line of the display'
    exit
else:
    max_temp = int(sys.argv[1]) 
    draw_reference_lines(max_temp)

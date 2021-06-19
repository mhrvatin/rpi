from sense_hat import SenseHat
import sys
import utils

def draw_reference_lines(max_temp):
    idx = max_temp
    y_offset = utils.PIXEL_DISPLAY_WIDTH

    while idx >= max_temp - utils.PIXEL_DISPLAY_WIDTH:
        if idx == utils.WARM_TEMPERATURE:
            for x in xrange(0, 8):
                if sense.get_pixel(x, y_offset) == utils.PIXEL_COLORS["NULL"]:
                    sense.set_pixel(x, y_offset, utils.PIXEL_COLORS["YELLOW"])
        elif idx == utils.HOT_TEMPERATURE:
            for x in xrange(0, 8):
                if sense.get_pixel(x, y_offset) == utils.PIXEL_COLORS["NULL"]:
                    sense.set_pixel(x, y_offset, utils.PIXEL_COLORS["RED"])

        idx -= 1
        y_offset -= 1

def remove_reference_lines():
    for x in xrange(0, 8):
        for y in xrange(0, 8):
            pixel = sense.get_pixel(x, y)

            if pixel == utils.PIXEL_COLORS["RED"] or pixel == utils.PIXEL_COLORS["YELLOW"]:
                sense.set_pixel(x, y, utils.PIXEL_COLORS["NULL"])

def shift_hours(current_max, new_max):
    steps = current_max - new_max
    delta = abs(steps)

    for i in xrange(0, delta):
        for x in xrange(0, 8):
            if steps < 0: #shift down
                for y in xrange(0, 7):
                    sense.set_pixel(x, y, sense.get_pixel(x, y + 1))
                    sense.set_pixel(x, y + 1, utils.PIXEL_COLORS["NULL"])
            elif steps > 0: #shift up
                for y in xrange(7, 0, -1):
                    sense.set_pixel(x, y, sense.get_pixel(x, y - 1))
                    sense.set_pixel(x, y - 1, utils.PIXEL_COLORS["NULL"])

sense = SenseHat()

if len(sys.argv) == 2:
    max_temp = int(sys.argv[1]) 
    sense.clear()
    draw_reference_lines(max_temp)
elif len(sys.argv) == 3:
    current_max_temp = int(sys.argv[1]) 
    new_max_temp = int(sys.argv[2])

    shift_hours(current_max_temp, new_max_temp)
    draw_reference_lines(new_max_temp)
else:
    print "Invalid argument"
    print """Usage: python clear_screen.py `max_temp` [new_max_temp],
    where `max_temp` is the temperature of the top-most line of the display.
    Or, `max_temp` is the current top line and `new_max_temp` is the new top line you want to set"""
    exit

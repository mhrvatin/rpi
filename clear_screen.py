import sys
import utils

def draw_reference_lines(max_temp):
    idx = max_temp
    y_offset = utils.PIXEL_DISPLAY_WIDTH

    while idx >= max_temp - utils.PIXEL_DISPLAY_WIDTH:
        if idx == utils.WARM_TEMPERATURE:
            for x in range(0, 8):
                if utils.pixel_is(sense, x, y_offset, utils.PIXEL_COLORS["NULL"]):
                    sense.set_pixel(x, y_offset, utils.PIXEL_COLORS["YELLOW"])
        elif idx == utils.HOT_TEMPERATURE:
            for x in range(0, 8):
                if utils.pixel_is(sense, x, y_offset, utils.PIXEL_COLORS["NULL"]):
                    sense.set_pixel(x, y_offset, utils.PIXEL_COLORS["RED"])

        idx -= 1
        y_offset -= 1

def remove_reference_lines():
    for x in range(0, 8):
        for y in range(0, 8):
            if (utils.pixel_is(sense, x, y, utils.PIXEL_COLORS["RED"]) or
                    utils.pixel_is(sense, x, y, utils.PIXEL_COLORS["YELLOW"])):
                sense.set_pixel(x, y, utils.PIXEL_COLORS["NULL"])

def shift_hours(current_max, new_max):
    steps = current_max - new_max
    delta = abs(steps)

    for i in range(0, delta):
        for x in range(0, 8):
            if steps < 0: #shift down
                for y in range(0, 7):
                    sense.set_pixel(x, y, sense.get_pixel(x, y + 1))
                    sense.set_pixel(x, y + 1, utils.PIXEL_COLORS["NULL"])
            elif steps > 0: #shift up
                for y in range(7, 0, -1):
                    sense.set_pixel(x, y, sense.get_pixel(x, y - 1))
                    sense.set_pixel(x, y - 1, utils.PIXEL_COLORS["NULL"])

sense = utils.get_sense()

if len(sys.argv) == 1:
    sense.clear()
    draw_reference_lines(utils.MAX_TEMPERATURE)
elif len(sys.argv) == 2:
    old_max_temp = int(sys.argv[1])

    shift_hours(old_max_temp, utils.MAX_TEMPERATURE)
    draw_reference_lines(utils.MAX_TEMPERATURE)
else:
    print("Invalid arguments", file=sys.stderr)
    print("""Usage: python3 clear_screen.py [old_max_temp]

    With no argument, clear the display and draw the reference lines for the
    current scale, whose top is utils.MAX_TEMPERATURE ({}).

    With old_max_temp, shift the graph already on the display to line up
    with the current scale, then draw the reference lines. Use this after
    changing MAX_TEMPERATURE in utils.py.""".format(utils.MAX_TEMPERATURE),
          file=sys.stderr)
    sys.exit(1)

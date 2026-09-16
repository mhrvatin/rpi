import sys
import utils

def draw_reference_lines(max_temp):
    for row, color in utils.reference_rows(max_temp).items():
        for x in range(0, 8):
            if utils.pixel_is(sense, x, row, utils.PIXEL_COLORS["NULL"]):
                sense.set_pixel(x, row, color)

def remove_reference_lines():
    colors = [utils.PIXEL_COLORS[name]
              for name in utils.REFERENCE_TEMPERATURES.values()]

    for x in range(0, 8):
        for y in range(0, 8):
            if any(utils.pixel_is(sense, x, y, color) for color in colors):
                sense.set_pixel(x, y, utils.PIXEL_COLORS["NULL"])

sense = utils.get_sense()

max_temp = utils.max_temperature()

if len(sys.argv) == 1:
    sense.clear()
    draw_reference_lines(max_temp)
elif len(sys.argv) == 2:
    old_max_temp = int(sys.argv[1])

    utils.shift_scale(sense, old_max_temp, max_temp)
    draw_reference_lines(max_temp)
else:
    print("Invalid arguments", file=sys.stderr)
    print("""Usage: python3 clear_screen.py [old_max_temp]

    With no argument, clear the display and draw the reference lines for the
    scale the time of year calls for, whose top is currently {}.

    With old_max_temp, shift the graph already on the display from that top
    onto the current one first. check_temp.py does this by itself when the
    season turns, so this is only for putting a display right by hand.""".format(max_temp),
          file=sys.stderr)
    sys.exit(1)

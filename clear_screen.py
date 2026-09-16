import sys
import utils

def draw_reference_lines(max_temp):
    for row, color in utils.reference_rows(max_temp).items():
        for x in range(0, 8):
            if utils.pixel_is(sense, x, row, utils.PIXEL_COLORS["NULL"]):
                sense.set_pixel(x, row, color)

sense = utils.get_sense()

max_temp = utils.max_temperature()

if len(sys.argv) == 1:
    sense.clear()
    draw_reference_lines(max_temp)
    utils.write_scale_top(max_temp)
elif len(sys.argv) == 3 and sys.argv[1] == "--from-top":
    utils.shift_scale(sense, int(sys.argv[2]), max_temp)
    draw_reference_lines(max_temp)
    utils.write_scale_top(max_temp)
else:
    print("Invalid arguments", file=sys.stderr)
    print("""Usage: python3 clear_screen.py [--from-top OLD_TOP]

    With no argument, clear the display and draw the reference lines for the
    scale the time of year calls for, whose top is currently {}.

    With --from-top OLD_TOP, shift the graph already on the display from
    that top onto the current one instead of clearing it. check_temp.py does
    this by itself when the season turns, so this is only for putting a
    display right by hand.

    An earlier version took a bare number meaning the top to draw. That form
    is rejected rather than accepted, so it cannot quietly do the other
    thing.""".format(max_temp),
          file=sys.stderr)
    sys.exit(1)

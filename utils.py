import http.client
import os
import time
from datetime import datetime
from sense_hat import SenseHat

PIXEL_DISPLAY_WIDTH = 7

# Socialstyrelsen's indoor limits: 26 degrees over a sustained period, 28
# during a heat wave. Neither of them ever moves.
WARM_TEMPERATURE = 26
HOT_TEMPERATURE = 28

# Months when a heat wave is plausible here. During those the scale is
# topped at 28, which puts the heat wave line on the top row. The rest of
# the year it is topped at 26, which puts the sustained limit on the top
# row and buys two more rows at the cold end, where the readings actually
# sit. Keeping the 26 line on screen is what stops the top going any lower.
HEAT_WAVE_MONTHS = (5, 6, 7, 8, 9)

# Temperatures that get a marker line drawn across the display.
REFERENCE_TEMPERATURES = {
    WARM_TEMPERATURE: "YELLOW",
    HOT_TEMPERATURE: "RED"
}

# Remembers the scale the graph on the display was drawn against, so a
# change of scale can be spotted and the graph moved to match it.
SCALE_STATE = "scale_top.txt"

# Writing a gamma table of all zeroes is how the display is turned off. A
# low-light table turns it back on.
DISPLAY_OFF_GAMMA = [0] * 32

# Seconds to wait on any network call before giving up.
NETWORK_TIMEOUT = 5

# How many ambient readings to average, and the pause between them.
SENSOR_READ_COUNT = 3
SENSOR_READ_DELAY = 0.5

# The HAT sits above the CPU, so it reads warm. Subtracting the gap to the
# CPU divided by this factor is the usual correction for that.
CPU_TEMP_FACTOR = 1.5

PIXEL_COLORS = {
    "NULL": [0, 0, 0],
    "RED": [244, 67, 54],
    "YELLOW": [255, 235, 59],
    "BLUE": [56, 80, 176],
    "GREEN": [72, 172, 80],
    "PURPLE": [166, 98, 175],
    "WHITE": [255, 255, 255]
}

# Recorded with every row, so a missing outdoor reading can be told apart
# from a working one, and a dead API from a Pi that was offline.
STATUS_OK = "ok"
STATUS_API_ERROR = "api_error"
STATUS_NO_NETWORK = "no_network"

_sense = None

def get_sense():
    """Return the shared SenseHat, building it on first use.

    Constructing a SenseHat opens the board's framebuffer and sensors, which
    should not happen merely because some module imported this one.
    """
    global _sense

    if _sense is None:
        _sense = SenseHat()

    return _sense

def is_network_up(debug=False):
    """True when a HEAD request to google.com gets out of the house."""
    if debug:
        return True

    conn = http.client.HTTPConnection("www.google.com",
                                      timeout = NETWORK_TIMEOUT)

    try:
        conn.request("HEAD", "/")

        return True
    except (OSError, http.client.HTTPException):
        return False
    finally:
        conn.close()

def quantize(color):
    """Return `color` as the display will report it back.

    The HAT stores five bits of red, six of green and five of blue, so the
    low bits of a colour written with set_pixel are lost and get_pixel does
    not necessarily return what was written.
    """
    red, green, blue = color

    return [red & 0xF8, green & 0xFC, blue & 0xF8]

def pixel_is(sense, x, y, color):
    """True when the pixel at x, y holds `color`, allowing for that loss."""
    return sense.get_pixel(x, y) == quantize(color)

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()

    return(res.replace("temp=","").replace("'C\n",""))

def read_ambient_temp():
    """Average both HAT temperature sensors over several reads.

    The pressure and humidity sensors each carry their own offset and
    disagree by a few tenths of a degree, so the mean of the two is steadier
    than either one alone. A single reading also picks up whatever noise
    that instant happened to hold. The first read after start-up can be far
    off, so one pair is taken and thrown away before averaging begins.
    """
    sense = get_sense()

    sense.get_temperature_from_pressure()
    sense.get_temperature_from_humidity()

    readings = []

    while len(readings) < SENSOR_READ_COUNT:
        if readings:
            time.sleep(SENSOR_READ_DELAY)

        readings.append((sense.get_temperature_from_pressure() +
                         sense.get_temperature_from_humidity()) / 2)

    return sum(readings) / len(readings)

def calc_indoor_temp():
    cpu_temp = float(get_cpu_temp())
    ambient = read_ambient_temp()

    return ambient - ((cpu_temp - ambient) / CPU_TEMP_FACTOR)

def max_temperature(when=None):
    """Top of the displayed scale for the time of year."""
    if when is None:
        when = datetime.now()

    if when.month in HEAT_WAVE_MONTHS:
        return HOT_TEMPERATURE

    return WARM_TEMPERATURE

def shift_scale(sense, current_max, new_max):
    """Move the graph already on the display onto a different scale.

    Each row stands for a temperature, so changing the top of the scale
    moves every reading to a different row. Rows pushed past an edge are
    lost, which is inherent in rescaling and happened just the same when
    this was done by hand.
    """
    steps = current_max - new_max
    delta = abs(steps)

    for _ in range(0, delta):
        for x in range(0, 8):
            if steps < 0: # the top went up, so readings move toward row 0
                for y in range(0, PIXEL_DISPLAY_WIDTH):
                    sense.set_pixel(x, y, sense.get_pixel(x, y + 1))
                    sense.set_pixel(x, y + 1, PIXEL_COLORS["NULL"])
            elif steps > 0: # the top came down, so they move the other way
                for y in range(PIXEL_DISPLAY_WIDTH, 0, -1):
                    sense.set_pixel(x, y, sense.get_pixel(x, y - 1))
                    sense.set_pixel(x, y - 1, PIXEL_COLORS["NULL"])

def read_scale_top():
    """The top of the scale the display was last drawn against, or None."""
    try:
        with open(SCALE_STATE, encoding="utf-8") as state:
            return int(state.read().strip())
    except (OSError, ValueError):
        return None

def write_scale_top(max_temp):
    """Record the scale the display now shows.

    Every path that redraws the display has to call this, or the next run
    will think the scale changed and shift a graph that is already right.
    """
    with open(SCALE_STATE, "w", encoding="utf-8") as state:
        state.write("{}\n".format(max_temp))

def reference_rows(max_temp):
    """Return {row: color} for the reference lines a scale can display.

    A threshold outside the displayed range gets no row at all, so a
    HOT_TEMPERATURE above `max_temp` simply draws nothing.
    """
    min_temp = max_temp - PIXEL_DISPLAY_WIDTH
    rows = {}

    for temp, color in REFERENCE_TEMPERATURES.items():
        if min_temp <= temp <= max_temp:
            row = translate_temp(temp, min_temp, max_temp,
                                 0, PIXEL_DISPLAY_WIDTH)
            rows[int(round(row))] = PIXEL_COLORS[color]

    return rows

def translate_temp(temp, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    new_value = (((temp - old_min) * new_range) / old_range) + new_min

    return new_value

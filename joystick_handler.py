#!/usr/bin/env python3

from sense_hat import ACTION_PRESSED
import queue
import signal
import sys
import time
import binary_clock
import tilt_pixel
import utils

# How long the main loop waits for a press before looking again. Short
# enough that Ctrl-C is not left hanging.
IDLE_POLL = 1

# How often the clock redraws itself while it is on screen.
CLOCK_REFRESH = 0.2

# How often the tilt demo samples the accelerometer and redraws.
TILT_REFRESH = 0.05

# Bottom right corner of the binary clock.
CLOCK_ORIGIN_X = 6
CLOCK_ORIGIN_Y = 5

# The stick delivers events on a thread of its own that sense_hat starts
# when a direction callback is assigned. Two things follow from that, and
# both used to bite. Work done in a callback blocks every later event until
# it finishes, and calling sense.stick.get_events() from anywhere else
# returns nothing, because that thread has already taken the events.
#
# So the callbacks do one thing only: record which direction was pressed.
# The main loop below picks presses up from here and does the work.
presses = queue.Queue()

def remember_press(event):
    # The initial press only. Holding a direction also delivers repeats, and
    # queueing those replays the lot the moment a blocking action returns.
    if event.action == ACTION_PRESSED:
        presses.put(event.direction)

def next_press(timeout):
    """The next direction pressed, or None if `timeout` passes first."""
    try:
        return presses.get(timeout = timeout)
    except queue.Empty:
        return None

def drain_presses():
    """Discard whatever was pressed during a blocking action."""
    while True:
        try:
            presses.get_nowait()
        except queue.Empty:
            return

def display_is_on():
    return sense.low_light

def turn_display_on():
    sense.low_light = True

def turn_display_off():
    sense.gamma = utils.DISPLAY_OFF_GAMMA

def toggle_display():
    if display_is_on():
        turn_display_off()
    else:
        turn_display_on()

def show_temperature():
    """Scroll the current indoor temperature across the display."""
    was_off = not display_is_on()

    if was_off:
        turn_display_on()

    saved_pixels = sense.get_pixels()
    sense.clear()
    sense.rotation = 180
    sense.show_message(str(round(utils.calc_indoor_temp(), 1)),
                       text_colour = [255, 255, 0])
    sense.rotation = 0
    sense.set_pixels(saved_pixels)

    if was_off:
        turn_display_off()

def draw_binary_clock():
    now = time.localtime()
    binary_time = binary_clock.parse_decimal_time(now.tm_hour, now.tm_min,
                                                  now.tm_sec)
    x = CLOCK_ORIGIN_X

    for digit in binary_time:
        y = CLOCK_ORIGIN_Y

        for bit in digit:
            if bit == "1":
                color = utils.PIXEL_COLORS["GREEN"]
            else:
                color = utils.PIXEL_COLORS["RED"]

            sense.set_pixel(x, y, color)
            y -= 1

        x -= 1

def show_clock():
    """Show the binary clock until the middle of the stick is pressed again.

    This runs on the main thread, so the presses that end the clock or dim
    the display arrive through the same queue as any other press.
    """
    saved_pixels = sense.get_pixels()
    sense.clear()

    while True:
        draw_binary_clock()

        direction = next_press(CLOCK_REFRESH)

        if direction == "middle":
            break

        if direction == "down":
            toggle_display()

    sense.set_pixels(saved_pixels)

def show_tilt():
    """Shift a single pixel around the display by tilting the Pi.

    Ends the same way show_clock() does: the press that started it also
    ends it, and arrives through the same queue.
    """
    saved_pixels = sense.get_pixels()
    sense.clear()
    state = tilt_pixel.initial_state()
    last_position = None

    while True:
        accel = sense.get_accelerometer_raw()
        state = tilt_pixel.step(state, accel, TILT_REFRESH)
        position = tilt_pixel.pixel_position(state)

        if position != last_position:
            sense.clear()
            sense.set_pixel(position[0], position[1], utils.PIXEL_COLORS["WHITE"])
            last_position = position

        direction = next_press(TILT_REFRESH)

        if direction == "left":
            break

        if direction == "down":
            toggle_display()

    sense.set_pixels(saved_pixels)

def signal_handler(signal, frame):
    sys.exit(0)

sense = utils.get_sense()

sense.stick.direction_up = remember_press
sense.stick.direction_down = remember_press
sense.stick.direction_left = remember_press
sense.stick.direction_middle = remember_press

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while True:
    direction = next_press(IDLE_POLL)

    if direction == "up":
        show_temperature()
        drain_presses()
    elif direction == "down":
        toggle_display()
    elif direction == "left":
        show_tilt()
        drain_presses()
    elif direction == "middle":
        show_clock()
        drain_presses()

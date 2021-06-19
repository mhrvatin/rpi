#!/usr/bin/env python

from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import signal
import sys
import time
import binary_clock
import enum
import utils
#import fetch_from_db

class Clock(enum.Enum):
    On = True
    Off = False

def set_clock(state):
    global is_clock_on
    is_clock_on = state

def clock_status():
    global is_clock_on
    return is_clock_on

def toggle_display():
    if sense.low_light: # display is on
        sense.gamma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:               # display is off
        sense.low_light = True

def save_graph():
    global pixel_list

    pixel_list = sense.get_pixels()
    sense.clear()

def restore_graph():
    sense.set_pixels(pixel_list)

def show_clock():
    set_clock(Clock.On)

    while clock_status() == Clock.On:
        now = time.localtime()
        hour = now.tm_hour
        minute = now.tm_min
        second = now.tm_sec

        y_coordinate_offset = 5
        x_coordinate_offset = 6

        binary_time_array = binary_clock.parse_decimal_time(hour, minute, second)

        events = sense.stick.get_events()

        for elem_idx, elem in enumerate(binary_time_array):
            for bit_idx, bit in enumerate(elem):
                if bit == "1":
                    sense.set_pixel(x_coordinate_offset, y_coordinate_offset, utils.PIXEL_COLORS["GREEN"])
                else:
                    sense.set_pixel(x_coordinate_offset, y_coordinate_offset, utils.PIXEL_COLORS["RED"])

                y_coordinate_offset = y_coordinate_offset - 1

            y_coordinate_offset = 5
            x_coordinate_offset = x_coordinate_offset - 1

        # won't register turning display on or off
        for event in events:
            if event.direction == "middle" and event.action == "pressed":
                set_clock(Clock.Off)
            elif event.direction == "down" and event.action == "pressed":
                toggle_display()

        time.sleep(0.2)

def show_current_temp_handler(event):
    if event.action != ACTION_RELEASED:
        if sense.low_light: # display is on
            dim_display_after_showing_temp = False
        else:               # display is off
            toggle_display()
            dim_display_after_showing_temp = True
            
        save_graph()
        sense.rotation = 180
        indoor_temp = round(utils.calc_indoor_temp(), 1)
        sense.show_message(str(indoor_temp), text_colour=[255,255,0])
        sense.rotation = 0
        restore_graph()

        if dim_display_after_showing_temp:
            toggle_display()

def toggle_display_handler(event):
    if event.action != ACTION_RELEASED:
        toggle_display()

def show_clock_handler(event):
    if event.action != ACTION_RELEASED:
        if clock_status() == Clock.Off:
            save_graph()
            show_clock()
            restore_graph()

def pushed_left(event):
    global time_offset

    if event.action != ACTION_RELEASED:
        print "pushed left"

        time_offset += 1
        rows = fetch_from_db.fetch_left(time_offset)
        for row in rows:
            print row.indoor_temperature
            print row.outdoor_temperature


def pushed_right(event):
    if event.action != ACTION_RELEASED:
        print "pushed right"

def signal_handler(signal, frame):
    sys.exit(0)

sense = SenseHat()

is_clock_on = Clock.Off
pixel_list = []
time_offset = 7

sense.stick.direction_up = show_current_temp_handler
sense.stick.direction_down = toggle_display_handler
sense.stick.direction_middle = show_clock_handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.pause()

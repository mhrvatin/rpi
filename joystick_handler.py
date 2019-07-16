from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from signal import pause
import urllib2
import os
import time
import binary_clock
import fetch_from_db

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()

    return(res.replace("temp=","").replace("'C\n",""))

def calc_indoor_temp():
    cpu_temp = int(float(get_cpu_temp()))
    ambient = sense.get_temperature_from_pressure()

    return(ambient - ((cpu_temp - ambient) / 1.5))

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
    global clock_is_on

    while clock_is_on:
        now = time.localtime()
        hour = now.tm_hour
        minute = now.tm_min
        second = now.tm_sec

        y = 5
        x = 6

        binary_time_array = binary_clock.parse_decimal_time(hour, minute, second)

        events = sense.stick.get_events()

        for elem_idx, elem in enumerate(binary_time_array):
            for bit_idx, bit in enumerate(elem):
                if bit == "1":
                    sense.set_pixel(x, y, 0, 255, 0)
                else:
                    sense.set_pixel(x, y, 10, 0, 0)

                y = y - 1

            y = 5
            x = x - 1

        # won't register turning display on or off
        for event in events:
            if event.direction == "middle" and event.action == "pressed": # turn clock off
                clock_is_on = False
            elif event.direction == "down" and event.action == "pressed": # turn display off
                toggle_display()


        time.sleep(1)

def pushed_up(event):
    if event.action != ACTION_RELEASED:
        if sense.low_light: # display is on
            dim_display_after_showing_temp = False
        else:               # display is off
            toggle_display()
            dim_display_after_showing_temp = True
            
        save_graph()
        sense.rotation = 180
        indoor_temp = round(calc_indoor_temp(), 1)
        sense.show_message(str(indoor_temp), text_colour=[255,255,0])
        sense.rotation = 0
        restore_graph()

        if dim_display_after_showing_temp:
            toggle_display()

def pushed_down(event):
    if event.action != ACTION_RELEASED:
        toggle_display()

def pushed_middle(event):
    global clock_is_on

    if event.action != ACTION_RELEASED:
        if not clock_is_on:
            save_graph()
            clock_is_on = True
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

sense = SenseHat()

pixel_list = []
clock_is_on = False
time_offset = 7

sense.stick.direction_up = pushed_up
sense.stick.direction_down = pushed_down
sense.stick.direction_middle = pushed_middle
#sense.stick.direction_left = pushed_left
#sense.stick.direction_right = pushed_right
pause()

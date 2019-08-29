#!/usr/bin/python2.7
from sense_hat import SenseHat
from datetime import datetime
import time
import os
import httplib
import urllib2
import json
import requests
import secrets

def indoor_color_already_written_to_pixel(x, y):
    global I

    ret = False

    if sense.get_pixel(x, y) == I:
        ret = True

    return ret

def graph_is_showing():
    ret = False

    for y in range(0, 7):
        if sense.get_pixel(0, y) != [0, 0, 0]:
            ret = True
            break

    return ret

def network_is_up():
    conn = httplib.HTTPConnection("www.google.com", timeout = 5)

    try:
        conn.request("HEAD", "/")
        conn.close()
        
        return True
    except:
        conn.close()

        return False

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()

    return(res.replace("temp=","").replace("'C\n",""))

def set_indoor(x, y):
    if network_is_up():
        sense.set_pixel(x, y, I)
    else:
        sense.set_pixel(x, y, W)

def set_outdoor(x, y):
    if network_is_up():
        if indoor_color_already_written_to_pixel(x, y):
            sense.set_pixel(x, y, M)
        else:
            sense.set_pixel(x, y, O)

def translate_temp(temp, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)  
    new_range = (new_max - new_min)  
    new_value = (((temp - old_min) * new_range) / old_range) + new_min 

    return new_value

def shift_hours():
    for x in xrange(0, 8):
        for y in xrange(7, 0, -1):
            sense.set_pixel(y, x, sense.get_pixel(y - 1, x))

    clear_now()

def clear_now(): # refactor to get info from separate config file, where min/max is defined
    sense.set_pixel(0, 0, N)
    sense.set_pixel(0, 1, N)
    sense.set_pixel(0, 2, N)
    sense.set_pixel(0, 3, N)
    sense.set_pixel(0, 4, N)
    sense.set_pixel(0, 5, Y)
    sense.set_pixel(0, 6, N)
    sense.set_pixel(0, 7, R)

def calc_indoor_temp():
    cpu_temp = int(float(get_cpu_temp()))
    ambient = sense.get_temperature_from_pressure()

    return(ambient - ((cpu_temp - ambient) / 1.5))

def get_weather_data():
    url = "https://api.darksky.net/forecast/"+secrets.DARKSKY_API+"/57.71,11.97?units=si"

    if network_is_up():
        r = requests.get(url)

        if r.status_code == 200:
            data = json.loads(r.text)

            temp = data["currently"]["temperature"]
            wind_speed = data["currently"]["windSpeed"]
            precip = data["currently"]["precipIntensity"]
            
            if precip > 0:
                precip_type = data["currently"]["precipType"]
            else:
                precip_type = None

            ret = [temp, precip, precip_type, wind_speed]
        else:
            ret = [r.status_code, json.loads(r.text), 98.0, 98.0] # api error
    else:
        ret = [99.0, 99.0, 99.0, 99.0] # no network

    return ret

def turn_off_display():
    sense.gamma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def turn_on_display():
    sense.low_light = True

N = [0, 0, 0]       # null
R = [244, 67, 54]   # Red
Y = [255, 235, 59]  # Yellow
O = [63, 81, 181]   # Outdoors
I = [72, 172, 80]   # Indoors
M = [166, 98, 175]  # Indoor and outdoor mixed(purple)
W = [25, 255, 255]  # White, no network connection

now = datetime.now()
turn_off_time = now.replace(hour = 21, minute = 0, second = 0, microsecond = 0)
turn_on_time = now.replace(hour = 7, minute = 0, second = 0, microsecond = 0)

sense = SenseHat()

if now >= turn_off_time or now <= turn_on_time:
    turn_off_display()
else:
    turn_on_display()

indoor_temp = calc_indoor_temp()
indoor_rounded = round(indoor_temp)
weather_data = get_weather_data()
outdoor_temp = weather_data[0]
precip = weather_data[1]
precip_type = weather_data[2]
wind_speed = weather_data[3]
humidity = sense.get_humidity()
pressure = sense.get_pressure()

max_temp = 28
min_temp = max_temp - 7

#print "%.1f,%s,%s,%s,%.1f,%.1f,%s" % (indoor_temp, outdoor_temp, downfall, wind_speed, humidity, pressure, str(now))

print "{:2.1f},{:2.1f},{:2.1f},{},{:2.1f},{:2.1f},{:2.1f},{}".format(
    indoor_temp,
    outdoor_temp,
    precip,
    precip_type,
    wind_speed,
    humidity,
    pressure,
    str(now)
)

#if (graph_is_showing()):
shift_hours()

if indoor_rounded >= min_temp and indoor_rounded <= max_temp:
    set_indoor(0, translate_temp(indoor_rounded, min_temp, max_temp, 0, 7))

if outdoor_temp != 98 and outdoor_temp != 99:
    if outdoor_temp >= min_temp and outdoor_temp <= max_temp:
        set_outdoor(0, translate_temp(outdoor_temp, min_temp, max_temp, 0, 7))

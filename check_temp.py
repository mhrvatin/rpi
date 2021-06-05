#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from sense_hat import SenseHat
from datetime import datetime
import argparse
import os
import httplib
import json
import requests
import secrets

ADDRESS = "Träkilsgatan 46"
MAX_TEMPERATURE = 26
MIN_TEMPERATURE = MAX_TEMPERATURE - 7

PIXEL_COLORS = {
    "NULL": [0, 0, 0],
    "RED": [244, 67, 54],
    "YELLOW": [255, 235, 59],
    "OUTDOORS": [63, 81, 181],
    "INDOORS": [72, 172, 80],
    "MIXED": [166, 98, 175],
    "WHITE": [255, 255, 255]
}

ERROR_CODES = {
    "API_ERROR": 98.0,
    "NO_NETWORK": 99.0
}

def indoor_color_already_written_to_pixel(x, y):
    if sense.get_pixel(x, y) == PIXEL_COLORS["INDOORS"]:
        return True

    return False

def graph_is_showing():
    for y in range(0, 7):
        if sense.get_pixel(0, y) != PIXEL_COLORS["NULL"]:
            return True

    return False

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
        sense.set_pixel(x, y, PIXEL_COLORS["INDOORS"])
    else:
        sense.set_pixel(x, y, PIXEL_COLORS["WHITE"])

def set_outdoor(x, y):
    if network_is_up():
        if indoor_color_already_written_to_pixel(x, y):
            sense.set_pixel(x, y, PIXEL_COLORS["MIXED"])
        else:
            sense.set_pixel(x, y, PIXEL_COLORS["OUTDOORS"])

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
    sense.set_pixel(0, 0, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 1, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 2, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 3, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 4, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 5, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 6, PIXEL_COLORS["NULL"])
    sense.set_pixel(0, 7, PIXEL_COLORS["YELLOW"])

def calc_indoor_temp():
    cpu_temp = int(float(get_cpu_temp()))
    ambient = sense.get_temperature_from_pressure()

    return(ambient - ((cpu_temp - ambient) / 1.5))

def get_weather_data():
    url = "https://api.darksky.net/forecast/{}/57.71,11.97?units=si".format(secrets.DARKSKY_API)

    if network_is_up():
        r = requests.get(url)

        if r.status_code == 200:
            data = json.loads(r.text)

            temp = data["currently"]["temperature"]
            wind_speed = data["currently"]["windSpeed"]
            precip = float(data["currently"]["precipIntensity"])
            
            if precip > 0:
                precip_type = data["currently"]["precipType"]
            else:
                precip_type = None

            return [temp, precip, precip_type, wind_speed]
        else:
            return [ERROR_CODES["API_ERROR"],
                    ERROR_CODES["API_ERROR"],
                    "api error",
                    ERROR_CODES["API_ERROR"]]

    return [ERROR_CODES["NO_NETWORK"],
            ERROR_CODES["NO_NETWORK"],
            "no network",
            ERROR_CODES["NO_NETWORK"]]

def turn_off_display():
    sense.gamma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def turn_on_display():
    sense.low_light = True


now = datetime.now()
turn_off_time = now.replace(hour = 22, minute = 0, second = 0, microsecond = 0)
turn_on_time = now.replace(hour = 6, minute = 0, second = 0, microsecond = 0)

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

json_output = { "indoorTemperature": "{:2.1f}".format(indoor_temp),
        "outdoorTemperature": "{:2.1f}".format(outdoor_temp),
        "precipitation": "{:2.1f}".format(precip),
        "precipitationType": precip_type, 
        "windSpeed": "{:2.1f}".format(wind_speed),
        "humidity": "{:2.1f}".format(humidity),
        "pressure": "{:2.1f}".format(pressure),
        "address": ADDRESS,
        "timestamp": str(now) }

print(json.dumps(json_output))

shift_hours()

if indoor_rounded >= MIN_TEMPERATURE and indoor_rounded <= MAX_TEMPERATURE:
    set_indoor(0, translate_temp(indoor_rounded, MIN_TEMPERATURE, MAX_TEMPERATURE, 0, 7))

if outdoor_temp != int(ERROR_CODES["API_ERROR"]) and outdoor_temp != int(ERROR_CODES["NO_NETWORK"]):
    if outdoor_temp >= MIN_TEMPERATURE and outdoor_temp <= MAX_TEMPERATURE:
        set_outdoor(0, translate_temp(outdoor_temp, MIN_TEMPERATURE, MAX_TEMPERATURE, 0, 7))

#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from sense_hat import SenseHat
from datetime import datetime
import json
import requests
import secrets
import utils

ADDRESS = "Smörkärnegatan 25"
MAX_TEMPERATURE = 26
MIN_TEMPERATURE = MAX_TEMPERATURE - 7

def indoor_color_already_written_to_pixel(x, y):
    if sense.get_pixel(x, y) == utils.PIXEL_COLORS["GREEN"]:
        return True

    return False

def set_indoor(x, y, color):
    sense.set_pixel(x, y, color)

def set_outdoor(x, y):
    if indoor_color_already_written_to_pixel(x, y):
        sense.set_pixel(x, y, utils.PIXEL_COLORS["PURPLE"])
    else:
        sense.set_pixel(x, y, utils.PIXEL_COLORS["BLUE"])

def shift_hours_left():
    for y in xrange(0, 8):
        for x in xrange(7, 0, -1):
            sense.set_pixel(x, y, sense.get_pixel(x - 1, y))

    set_rightmost_column_default()

def set_rightmost_column_default():
    idx = MAX_TEMPERATURE
    y_offset = utils.PIXEL_DISPLAY_WIDTH

    while idx >= MAX_TEMPERATURE - utils.PIXEL_DISPLAY_WIDTH:
        if idx == utils.WARM_TEMPERATURE:
            sense.set_pixel(0, y_offset, utils.PIXEL_COLORS["YELLOW"])
        elif idx == utils.HOT_TEMPERATURE:
            sense.set_pixel(0, y_offset, utils.PIXEL_COLORS["RED"])
        else:
            sense.set_pixel(0, y_offset, utils.PIXEL_COLORS["NULL"])

        idx -= 1
        y_offset -= 1

def get_weather_data(is_network_up):
    url = "http://api.weatherapi.com/v1/current.json?key={}&q={}&aqi=no".format(secrets.API_KEY, secrets.LAT_LONG)

    if is_network_up:
        r = requests.get(url)

        if r.status_code == 200:
            data = json.loads(r.text)

            temp = data["current"]["temp_c"]
            wind_speed = data["current"]["wind_kph"]
            precip = float(data["current"]["precip_mm"])
            
            if precip > 0:
                precip_type = data["current"]["condition"]["text"]
            else:
                precip_type = None

            return [temp, precip, precip_type, wind_speed]
        else:
            return [utils.ERROR_CODES["API_ERROR"],
                    utils.ERROR_CODES["API_ERROR"],
                    "api error",
                    utils.ERROR_CODES["API_ERROR"]]

    return [utils.ERROR_CODES["NO_NETWORK"],
            utils.ERROR_CODES["NO_NETWORK"],
            "no network",
            utils.ERROR_CODES["NO_NETWORK"]]

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

indoor_temp = utils.calc_indoor_temp()
indoor_rounded = round(indoor_temp)
is_network_up = utils.is_network_up()
weather_data = get_weather_data(is_network_up)

outdoor_temp = weather_data[0]
precip = weather_data[1]
precip_type = weather_data[2]
wind_speed = weather_data[3]
humidity = sense.get_humidity()
pressure = sense.get_pressure()

shift_hours_left()

if is_network_up:
    if indoor_rounded >= MIN_TEMPERATURE and indoor_rounded <= MAX_TEMPERATURE:
        set_indoor(0, utils.translate_temp(indoor_rounded, MIN_TEMPERATURE, MAX_TEMPERATURE, 0, 7), utils.PIXEL_COLORS["GREEN"])

    if outdoor_temp >= MIN_TEMPERATURE and outdoor_temp <= MAX_TEMPERATURE:
        set_outdoor(0, utils.translate_temp(outdoor_temp, MIN_TEMPERATURE, MAX_TEMPERATURE, 0, 7))

else:
    set_indoor(0, utils.translate_temp(indoor_rounded, MIN_TEMPERATURE, MAX_TEMPERATURE, 0, 7), utils.PIXEL_COLORS["WHITE"])

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

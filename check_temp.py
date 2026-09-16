#!/usr/bin/env python3
from datetime import datetime
import json
import requests
import config
import utils

ADDRESS = "Smörkärnegatan 25"

def indoor_color_already_written_to_pixel(x, y):
    return utils.pixel_is(sense, x, y, utils.PIXEL_COLORS["GREEN"])

def set_indoor(x, y, color):
    sense.set_pixel(x, y, color)

def set_outdoor(x, y):
    if indoor_color_already_written_to_pixel(x, y):
        sense.set_pixel(x, y, utils.PIXEL_COLORS["PURPLE"])
    else:
        sense.set_pixel(x, y, utils.PIXEL_COLORS["BLUE"])

def shift_hours_left():
    for y in range(0, 8):
        for x in range(7, 0, -1):
            sense.set_pixel(x, y, sense.get_pixel(x - 1, y))

    set_rightmost_column_default()

def set_rightmost_column_default():
    reference_rows = utils.reference_rows(utils.MAX_TEMPERATURE)

    for row in range(0, utils.PIXEL_DISPLAY_WIDTH + 1):
        sense.set_pixel(0, row,
                        reference_rows.get(row, utils.PIXEL_COLORS["NULL"]))

def no_weather_data(status):
    """An outdoor reading that did not happen, carrying the reason why."""
    return {"status": status,
            "temp": None,
            "precip": None,
            "precip_type": None,
            "wind_speed": None}

def get_weather_data(is_network_up):
    url = "http://api.weatherapi.com/v1/current.json?key={}&q={}&aqi=no".format(config.API_KEY, config.LAT_LONG)

    if not is_network_up:
        return no_weather_data(utils.STATUS_NO_NETWORK)

    try:
        r = requests.get(url, timeout = utils.NETWORK_TIMEOUT)
    except requests.exceptions.RequestException:
        return no_weather_data(utils.STATUS_API_ERROR)

    if r.status_code != 200:
        return no_weather_data(utils.STATUS_API_ERROR)

    try:
        data = json.loads(r.text)

        temp = data["current"]["temp_c"]
        wind_speed = data["current"]["wind_kph"]
        precip = float(data["current"]["precip_mm"])
        condition = data["current"]["condition"]["text"]
    except (ValueError, KeyError, TypeError):
        return no_weather_data(utils.STATUS_API_ERROR)

    if precip > 0:
        precip_type = condition
    else:
        precip_type = None

    return {"status": utils.STATUS_OK,
            "temp": temp,
            "precip": precip,
            "precip_type": precip_type,
            "wind_speed": wind_speed}

def temp_is_displayable(temp):
    """True when a reading exists and falls inside the displayed scale."""
    if temp is None:
        return False

    return utils.MIN_TEMPERATURE <= temp <= utils.MAX_TEMPERATURE

def format_reading(value):
    """One decimal place, or null when the reading did not happen."""
    if value is None:
        return None

    return "{:2.1f}".format(value)

def temp_to_pixel_row(temp):
    """Map a temperature onto a display row.

    `translate_temp` returns a float, and Python 3 rejects a float offset
    when seeking in the framebuffer, so `set_pixel` needs an int.
    """
    row = utils.translate_temp(temp, utils.MIN_TEMPERATURE, utils.MAX_TEMPERATURE,
                               0, utils.PIXEL_DISPLAY_WIDTH)

    return int(round(row))

def turn_off_display():
    sense.gamma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def turn_on_display():
    sense.low_light = True

now = datetime.now()
turn_off_time = now.replace(hour = 22, minute = 0, second = 0, microsecond = 0)
turn_on_time = now.replace(hour = 6, minute = 0, second = 0, microsecond = 0)

sense = utils.get_sense()

if now >= turn_off_time or now <= turn_on_time:
    turn_off_display()
else:
    turn_on_display()

indoor_temp = utils.calc_indoor_temp()
indoor_rounded = round(indoor_temp)
is_network_up = utils.is_network_up()
weather_data = get_weather_data(is_network_up)

status = weather_data["status"]
outdoor_temp = weather_data["temp"]
precip = weather_data["precip"]
precip_type = weather_data["precip_type"]
wind_speed = weather_data["wind_speed"]
humidity = sense.get_humidity()
pressure = sense.get_pressure()

shift_hours_left()

if temp_is_displayable(indoor_rounded):
    if status == utils.STATUS_NO_NETWORK:
        indoor_color = utils.PIXEL_COLORS["WHITE"]
    else:
        indoor_color = utils.PIXEL_COLORS["GREEN"]

    set_indoor(0, temp_to_pixel_row(indoor_rounded), indoor_color)

if temp_is_displayable(outdoor_temp):
    set_outdoor(0, temp_to_pixel_row(outdoor_temp))

json_output = { "indoorTemperature": format_reading(indoor_temp),
        "outdoorTemperature": format_reading(outdoor_temp),
        "precipitation": format_reading(precip),
        "precipitationType": precip_type,
        "windSpeed": format_reading(wind_speed),
        "humidity": format_reading(humidity),
        "pressure": format_reading(pressure),
        "address": ADDRESS,
        "status": status,
        "timestamp": str(now) }

print(json.dumps(json_output))

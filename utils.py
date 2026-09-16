import http.client
import os
import time
from sense_hat import SenseHat

PIXEL_DISPLAY_WIDTH = 7
WARM_TEMPERATURE = 26
HOT_TEMPERATURE = 28

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

ERROR_CODES = {
    "API_ERROR": 98.0,
    "NO_NETWORK": 99.0
}

sense = SenseHat()

def is_network_up(debug=False):
    if debug:
        return True
    else:
        conn = http.client.HTTPConnection("www.google.com", timeout = 5)

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

def read_ambient_temp():
    """Average both HAT temperature sensors over several reads.

    The pressure and humidity sensors each carry their own offset and
    disagree by a few tenths of a degree, so the mean of the two is steadier
    than either one alone. A single reading also picks up whatever noise
    that instant happened to hold. The first read after start-up can be far
    off, so one pair is taken and thrown away before averaging begins.
    """
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

def translate_temp(temp, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)  
    new_range = (new_max - new_min)  
    new_value = (((temp - old_min) * new_range) / old_range) + new_min 

    return new_value

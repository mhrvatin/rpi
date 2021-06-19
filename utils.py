import httplib
import os
from sense_hat import SenseHat

PIXEL_DISPLAY_WIDTH = 7
WARM_TEMPERATURE = 26
HOT_TEMPERATURE = 28

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

def calc_indoor_temp():
    cpu_temp = int(float(get_cpu_temp()))
    ambient = sense.get_temperature_from_pressure()

    return(ambient - ((cpu_temp - ambient) / 1.5))

def translate_temp(temp, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)  
    new_range = (new_max - new_min)  
    new_value = (((temp - old_min) * new_range) / old_range) + new_min 

    return new_value

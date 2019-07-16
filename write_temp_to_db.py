from datetime import datetime
from peewee import *
import httplib
import secrets

formated_data = []
db = MySQLDatabase(secrets.DB,
                    host = secrets.HOST,
                    user = secrets.USER,
                    passwd = secrets.PASS)

def network_is_up():
    conn = httplib.HTTPConnection("www.google.com", timeout = 5)

    try:
        conn.request("HEAD", "/")
        conn.close()
        
        return True
    except:
        conn.close()

        return False

class Apartment_data(Model):
    indoor_temperature = DoubleField()
    outdoor_temperature = DoubleField()
    downfall = DoubleField()
    wind_speed = DoubleField()
    humidity = DoubleField()
    pressure = DoubleField()
    time = DateTimeField()

    class Meta:
        database = db

with open("apartment_data_buffer") as f:
    buffered_data = f.readlines()

buffered_data = [x.strip() for x in buffered_data]

for line in buffered_data:
    formated_data.append(line.split(","))

if network_is_up():
    db.connect()

    for hour in formated_data:
        if hour[1] == "no_network":
            formated_outdoor_temperature = 99
            formated_downfall = 99
            formated_wind_speed = 99
        elif hour[1] == "fetch_error":
            formated_outdoor_temperature = 98
            formated_downfall = 98
            formated_wind_speed = 98
        else:
            formated_outdoor_temperature = hour[1]
            formated_downfall = hour[2]
            formated_wind_speed = hour[3]

        apartment = Apartment_data(indoor_temperature = hour[0],
                                outdoor_temperature = formated_outdoor_temperature,
                                downfall = formated_downfall,
                                wind_speed = formated_wind_speed,
                                humidity = hour[4],
                                pressure = hour[5],
                                time = hour[6])
        apartment.save()

    db.close()

    open("apartment_data_buffer", "w").close()

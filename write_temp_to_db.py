from datetime import datetime
from peewee import * 
from utils import is_network_up
import json
import httplib
import secrets

db = MySQLDatabase(secrets.DB,
                   host = secrets.HOST,
                   user = secrets.USER,
                   passwd = secrets.PASS)

class Apartment_data(Model):
    indoor_temperature = DoubleField()
    outdoor_temperature = DoubleField()
    precipitation = DoubleField()
    precipitation_type = CharField(120)
    wind_speed = DoubleField()
    humidity = DoubleField()
    pressure = DoubleField()
    address = CharField(120)
    date = DateTimeField()

    class Meta:
        database = db

def log_data(data):
    with open("upload.log", "a") as log:
        log.write("{} {}\n".format(str(datetime.now()), data))

with open("apartment_data_buffer.json") as f:
    buffered_data = f.readlines()

if is_network_up():
    db.connect() 

    for raw_data in buffered_data:
        json_data = json.loads(raw_data)

        apartment = Apartment_data(indoor_temperature = json_data["indoorTemperature"],
                    outdoor_temperature = json_data["outdoorTemperature"],
                    precipitation = json_data["precipitation"],
                    precipitation_type = json_data["precipitationType"],
                    wind_speed = json_data["windSpeed"],
                    humidity = json_data["humidity"],
                    pressure = json_data["pressure"],
                    address = json_data["address"],
                    date = json_data["timestamp"])
        apartment.save()
        
        log_data("Upload successfull with data {}".format(json.dumps(json_data)))
        
    db.close()

    # flush buffer
    open("apartment_data_buffer.json", "w").close()
else:
    log_data("No internet conncetion")

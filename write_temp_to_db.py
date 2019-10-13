from datetime import datetime
from peewee import *
import httplib
import secrets

formatted_data = []
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
    precipitation = DoubleField()
    precipitation_type = CharField(120)
    wind_speed = DoubleField()
    humidity = DoubleField()
    pressure = DoubleField()
    address = CharField(120)
    date = DateTimeField()

    class Meta:
        database = db

with open("apartment_data_buffer") as f:
    buffered_data = f.readlines()

buffered_data = [x.strip() for x in buffered_data]

for line in buffered_data:
    formatted_data.append(line.split(","))

if network_is_up():
    db.connect()

    for hour in formatted_data:
        apartment = Apartment_data(indoor_temperature = hour[0],
                    outdoor_temperature = hour[1],
                    precipitation = hour[2],
                    precipitation_type = None if hour[3] == "None" else hour[3],
                    wind_speed = hour[4],
                    humidity = hour[5],
                    pressure = hour[6],
                    address = hour[7],
                    date  = hour[8])
        apartment.save()
    db.close()

    with open("upload.log", "a") as log:
        log.write("upload successfull at {}, with data {}\n".format(str(datetime.now()), formatted_data))

    open("apartment_data_buffer", "w").close()
else:
    with open("upload.log", "a") as log:
        log.write("upload failed at {} \n".format(str(datetime.now())))

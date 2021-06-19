from datetime import *
from peewee import *
from playhouse.shortcuts import model_to_dict
import httplib
import json
import secrets
import utils

db = MySQLDatabase(secrets.DB,
                   host = secrets.HOST,
                   user = secrets.USER,
                   passwd = secrets.PASS)

class Apartment_data(Model):
    indoor_temperature = DoubleField()
    outdoor_temperature = DoubleField()
    date = DateTimeField()

    class Meta:
        database = db

def fetch_latest(limit=7):
    if utils.network_is_up():
        db.connect()

        temperature_data = Apartment_data\
                .select(Apartment_data.indoor_temperature,
                    Apartment_data.outdoor_temperature,
                    Apartment_data.date)\
                .limit(limit)\
                .order_by(Apartment_data.date.desc())

        '''for row in temperature_data:
            print row.indoor_temperature
            print row.outdoor_temperature
            print row.date
            print "--------"'''

        db.close()

        return json.dumps([model_to_dict(e) for e in temperature_data], indent=4, default=str)

def fetch_left(offset): # wip
    if network_is_up():
        now = datetime.now()
        lower_bound = now.replace(minute = 0, second = 0, microsecond = 0)
        upper_bound = now.replace(minute = 59, second = 59, microsecond = 59)
        delta = timedelta(hours = offset)
        lower_diff = lower_bound - delta
        upper_diff = upper_bound - delta

        lower_bound_string = lower_diff.strftime("%Y-%m-%d %H:%M:%S")
        upper_bound_string = upper_diff.strftime("%Y-%m-%d %H:%M:%S")

        db.connect()

        temperature_data = (Apartment_data
                .select(Apartment_data.indoor_temperature,
                    Apartment_data.outdoor_temperature)
                .where(Apartment_data.date >= lower_bound_string and
                    Apartment_data.date <= upper_bound_string)
                .limit(1)
                .order_by(Apartment_data.date.desc()))

        '''for row in temperature_data:
            print row.indoor_temperature
            print row.outdoor_temperature
            print "--------"'''

        db.close()

        return temperature_data

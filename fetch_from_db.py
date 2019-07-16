from datetime import *
from peewee import *
import httplib
import time
import secrets

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
    time = DateTimeField()

    class Meta:
        database = db

def latest():
    if network_is_up():
        db.connect()

        temperature_data = (Apartment_data
                .select(Apartment_data.indoor_temperature,
                    Apartment_data.outdoor_temperature,
                    Apartment_data.time)
                .limit(7)
                .order_by(Apartment_data.time.desc()))

        '''for row in temperature_data:
            print row.indoor_temperature
            print row.outdoor_temperature
            print row.time
            print "--------"'''

        db.close()

        return temperature_data

def fetch_left(offset): # wip
    if network_is_up():
        now = datetime.now()
        lower_bound = now.replace(minute = 0, second = 0, microsecond = 0)
        upper_bound = now.replace(minute = 59, second = 59, microsecond = 59)
        d = timedelta(hours = offset)
        lower_diff = lower_bound - d
        upper_diff = upper_bound - d

        lower_bound_string = lower_diff.strftime("%Y-%m-%d %H:%M:%S")
        upper_bound_string = upper_diff.strftime("%Y-%m-%d %H:%M:%S")

        db.connect()

        temperature_data = (Apartment_data
                .select(Apartment_data.indoor_temperature,
                    Apartment_data.outdoor_temperature)
                .where(Apartment_data.time >= lower_bound_string and
                    Apartment_data.time <= upper_bound_string)
                .limit(1)
                .order_by(Apartment_data.time.desc()))

        '''for row in temperature_data:
            print row.indoor_temperature
            print row.outdoor_temperature
            print "--------"'''

        db.close()

        return temperature_data


#print db.get_conn()
#rows = latest()
row = fetch_left(1)

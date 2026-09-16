from datetime import datetime
from peewee import *
from utils import is_network_up, STATUS_OK
import json
import os
import sys
import config

# Seconds before a stalled database call gives up. Without this a run can
# hang past its hour and overlap the next one, which is how the same pending
# file gets uploaded twice.
DB_TIMEOUT = 30

BUFFER = "apartment_data_buffer.json"
PENDING = "apartment_data_buffer.pending.json"

db = MySQLDatabase(config.DB,
                   host = config.HOST,
                   user = config.USER,
                   passwd = config.PASS,
                   connect_timeout = DB_TIMEOUT,
                   read_timeout = DB_TIMEOUT,
                   write_timeout = DB_TIMEOUT)

class Apartment_data(Model):
    indoor_temperature = DoubleField()
    outdoor_temperature = DoubleField(null = True)
    precipitation = DoubleField(null = True)
    precipitation_type = CharField(120, null = True)
    wind_speed = DoubleField(null = True)
    humidity = DoubleField()
    pressure = DoubleField()
    address = CharField(120)
    status = CharField(20)
    date = DateTimeField()

    class Meta:
        database = db

def log_data(data):
    with open("upload.log", "a", encoding="utf-8") as log:
        log.write("{} {}\n".format(str(datetime.now()), data))

def take_buffer():
    """Move the buffer aside and return the path to work from.

    Reading the buffer and truncating it afterwards loses every row
    check_temp.py appended in between. Renaming it first means the next
    append creates a fresh buffer and nothing falls through the gap.

    A run that dies before deleting the file it renamed would strand those
    rows, so an existing one is picked up here and finished first.
    """
    if os.path.exists(PENDING):
        return PENDING

    if not os.path.exists(BUFFER):
        return None

    os.rename(BUFFER, PENDING)

    return PENDING

def row_from(json_data):
    return Apartment_data(indoor_temperature = json_data["indoorTemperature"],
                outdoor_temperature = json_data["outdoorTemperature"],
                precipitation = json_data["precipitation"],
                precipitation_type = json_data["precipitationType"],
                wind_speed = json_data["windSpeed"],
                humidity = json_data["humidity"],
                pressure = json_data["pressure"],
                address = json_data["address"],
                status = json_data.get("status", STATUS_OK),
                date = json_data["timestamp"])

if not is_network_up():
    log_data("No internet connection")
    sys.exit(0)

pending = take_buffer()

if pending is None:
    sys.exit(0)

with open(pending, encoding="utf-8") as f:
    buffered_data = f.readlines()

uploaded = []
skipped = []

db.connect()

try:
    # One transaction, so a failure part way through leaves nothing behind
    # to be inserted a second time when the file is retried.
    with db.atomic():
        for raw_data in buffered_data:
            # A line that will not parse, or that parses but is missing a
            # field, is skipped. Letting it raise would strand the file and
            # stall every later upload behind it, for good. A save() failure
            # is a different thing: that is the database's problem, so it
            # aborts the batch and the file is retried whole.
            try:
                json_data = json.loads(raw_data)
                row = row_from(json_data)
            except (ValueError, KeyError, TypeError):
                skipped.append(raw_data)
                continue

            row.save()
            uploaded.append(json_data)
except Exception as error:
    log_data("Upload failed, keeping {} for the next run: {}".format(pending, error))
    raise
finally:
    db.close()

for json_data in uploaded:
    log_data("Upload successful with data {}".format(json.dumps(json_data)))

for raw_data in skipped:
    log_data("Skipped unreadable buffer line {}".format(raw_data.strip()))

os.remove(pending)

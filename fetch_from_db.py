from datetime import datetime, timedelta
from peewee import *
from playhouse.shortcuts import model_to_dict
import json
import config
import utils

db = MySQLDatabase(config.DB,
                   host = config.HOST,
                   user = config.USER,
                   passwd = config.PASS)

class Apartment_data(Model):
    indoor_temperature = DoubleField()
    outdoor_temperature = DoubleField()
    date = DateTimeField()

    class Meta:
        database = db

def fetch_latest(limit=7):
    """The most recent readings as JSON, or None with no network."""
    if not utils.is_network_up():
        return None

    db.connect()

    try:
        # The query is lazy, so it has to be read while the connection is
        # still open. Closing first and iterating afterwards fails.
        rows = list(Apartment_data
                .select(Apartment_data.indoor_temperature,
                    Apartment_data.outdoor_temperature,
                    Apartment_data.date)
                .order_by(Apartment_data.date.desc())
                .limit(limit))
    finally:
        db.close()

    return json.dumps([model_to_dict(row) for row in rows],
                      indent=4, default=str)

def fetch_left(offset): # not wired up to anything yet
    """The reading from `offset` hours ago, or None with no network."""
    if not utils.is_network_up():
        return None

    now = datetime.now()
    delta = timedelta(hours = offset)
    lower_bound = now.replace(minute = 0, second = 0, microsecond = 0) - delta
    upper_bound = now.replace(minute = 59, second = 59,
                              microsecond = 999999) - delta

    db.connect()

    try:
        rows = list(Apartment_data
                .select(Apartment_data.indoor_temperature,
                    Apartment_data.outdoor_temperature)
                .where((Apartment_data.date >= lower_bound) &
                    (Apartment_data.date <= upper_bound))
                .order_by(Apartment_data.date.desc())
                .limit(1))
    finally:
        db.close()

    return rows

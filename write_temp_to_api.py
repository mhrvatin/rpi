#!/usr/bin/env python3
from datetime import datetime
from utils import is_network_up
import json
import os
import sys
import requests
import config

# Seconds before a stalled request gives up. Matches DB_TIMEOUT in
# write_temp_to_db.py so a run can't hang past its hour and overlap the next.
API_TIMEOUT = 30

BUFFER = "apartment_data_buffer.api_buffer.json"
PENDING = "apartment_data_buffer.api_buffer.pending.json"

def log_data(data):
    with open("api_upload.log", "a", encoding="utf-8") as log:
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

if not is_network_up():
    log_data("No internet connection")
    sys.exit(0)

pending = take_buffer()

if pending is None:
    sys.exit(0)

with open(pending, encoding="utf-8") as f:
    buffered_data = f.readlines()

rows = []
skipped = []

for raw_data in buffered_data:
    # A line that will not parse is skipped. Letting it raise would strand
    # the file and stall every later upload behind it, for good. A send
    # failure is a different thing: that is the endpoint's problem, so it
    # aborts the batch and the file is retried whole.
    try:
        json_data = json.loads(raw_data)
    except ValueError:
        skipped.append(raw_data)
        continue

    rows.append(json_data)

for raw_data in skipped:
    log_data("Skipped unreadable buffer line {}".format(raw_data.strip()))

if not rows:
    os.remove(pending)
    sys.exit(0)

headers = {"Authorization": "Bearer {}".format(config.TEMPERATURE_API_TOKEN)}

try:
    r = requests.post(config.TEMPERATURE_API_URL, json = rows,
                      headers = headers, timeout = API_TIMEOUT)
except requests.exceptions.RequestException as error:
    log_data("Upload failed, keeping {} for the next run: {}".format(pending, error))
    sys.exit(1)

if not (200 <= r.status_code < 300):
    log_data("Upload failed, keeping {} for the next run: {} {}".format(pending, r.status_code, r.text))
    sys.exit(1)

for json_data in rows:
    log_data("Upload successful with data {}".format(json.dumps(json_data)))

os.remove(pending)

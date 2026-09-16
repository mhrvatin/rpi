Records the temperature in my room with a Sense HAT on a Raspberry Pi.
Requires Python 3.

## Reprovisioning

1. Set correct date `sudo date -s 'yyyy-mm-dd hh:MM:ss'`
2. Update wifi credentials `sudo vim /etc/wpa_supplicant/wpa_supplicant.conf`
3. Connect to inet `wpa_cli -i wlan0 reconfigure`
4. Update package source
  * `sudo vim /etc/apt/sources.list.d/raspi.list`
  * `sudo vim /etc/apt/sources.list`
5. Update certificates `sudo apt update && sudo apt install ca-certificates`
6. Clone this repo
7. Copy files to `~`
8. Copy `config.example` to `config.py` and fill in the credentials
9. Install the schedule, see below

## Schedule

`crontab.example` is a template for the crontab that drives everything.
Compare it against `crontab -l` before installing it, because the live
schedule has only ever existed on the Pi.

`check_temp.py` takes a reading and prints one line of JSON, which cron
appends to `apartment_data_buffer.json`. `write_temp_to_db.py` then moves
that buffer aside, uploads the rows in one transaction and deletes it. A run
with no network leaves the buffer alone for the next one.

Every row carries a status of `ok`, `api_error` or `no_network`, so an hour
with no outdoor reading can be told apart from one that worked. The outdoor
columns are null in that case.

## Display

The graph plots one column per hour, newest on the left, over a scale whose
top is `MAX_TEMPERATURE` in `utils.py`. Indoor is green, outdoor is blue,
purple where the two land on the same pixel, and white when the Pi could not
reach the network. Marker lines come from `REFERENCE_TEMPERATURES`; a
threshold above the top of the scale is simply not drawn.

Run `python3 clear_screen.py` to clear the display and draw the marker
lines. After changing `MAX_TEMPERATURE`, pass the previous top temperature
to shift the graph already on the display onto the new scale.

## Joystick

`joystick_handler.py` runs in the background. Press up for the current
temperature, down to dim the display, and the middle for a binary clock.
Press the middle again to go back to the graph.

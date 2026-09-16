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

## Schema

The status column and the nullable outdoor columns need this once, before
the current code runs. Peewee does not alter the table itself.

```sql
ALTER TABLE apartment_data ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ok';
ALTER TABLE apartment_data MODIFY COLUMN outdoor_temperature DOUBLE NULL;
ALTER TABLE apartment_data MODIFY COLUMN precipitation DOUBLE NULL;
ALTER TABLE apartment_data MODIFY COLUMN wind_speed DOUBLE NULL;
```

The first statement marks every existing row `ok`, including the ones that
hold the old 98 and 99 degree error values. To label and clear those:

```sql
UPDATE apartment_data SET status = 'api_error' WHERE outdoor_temperature = 98.0;
UPDATE apartment_data SET status = 'no_network' WHERE outdoor_temperature = 99.0;
UPDATE apartment_data SET outdoor_temperature = NULL, precipitation = NULL,
    wind_speed = NULL, precipitation_type = NULL WHERE status <> 'ok';
```

`precipitation_type` is cleared along with the numbers because the old code
put the reason there, as the string `api error` or `no network`. Left alone
it would mix those in with real weather conditions.

Run the UPDATE statements **after** the first upload, not before. Whatever
is sitting in the buffer when the new code goes on still carries the old 98
and 99 values and has no status of its own, so it uploads as `ok`. Running
the updates afterwards catches those rows too.

Rolling back a failed upload needs InnoDB, which is the default. Check with
`SHOW TABLE STATUS LIKE 'apartment_data'` if in doubt.

## Display

The graph plots one column per hour, newest on the left, one row per degree.
Indoor is green, outdoor is blue, purple where the two land on the same
pixel, and white when the Pi could not reach the network.

The two marker lines are Socialstyrelsen's indoor limits: yellow at 26
degrees for a sustained period, red at 28 during a heat wave. Those numbers
never change. What changes is the top of the scale, and only between those
same two values:

| Months | Top | Range | Lines shown |
| --- | --- | --- | --- |
| May to September | 28 | 21-28 | red on the top row, yellow on row 5 |
| the rest | 26 | 19-26 | yellow on the top row |

Outside a heat wave the room never approaches 28, so a scale reaching that
high wastes two rows. Topping out at 26 spends them at the cold end instead,
where the readings are, and still keeps the sustained limit in view. The top
cannot go below 26 without pushing the yellow line off the display.

`check_temp.py` picks the top from the month, so the switch happens on its
own. It remembers the scale it last drew against in `scale_top.txt` and
shifts the graph already on the display when that changes. Readings pushed
past an edge by the shift are lost from the display; the database keeps
absolute temperatures either way. Change the months in `HEAT_WAVE_MONTHS`
in `utils.py`.

Which lines are showing says which scale is in force, so the display reads
correctly without having to remember the month.

`python3 clear_screen.py` clears the display and draws the marker lines for
the current scale. `python3 clear_screen.py --from-top 26` shifts the graph
already on the display from a top of 26 onto the current scale instead of
clearing it. That is only needed to put a display right by hand, for
instance on the first run after deploying, when `scale_top.txt` does not
exist yet. Either form records the scale it drew, so the next hourly run
does not shift a display that is already correct.

## Joystick

`joystick_handler.py` runs in the background. Press up for the current
temperature, down to dim the display, left to shift a pixel around the
display by tilting the Pi, and the middle for a binary clock. Press left
or the middle again, respectively, to go back to the graph.

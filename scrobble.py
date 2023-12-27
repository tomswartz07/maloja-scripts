import json
from time import sleep
from datetime import datetime
import re
import requests

# Key associated with a load transaction, to identify them later
key = 'tW6NZcij0EQTQRaJZ5okHjipfx4sopidf8Mr0mNl7C6sEzYcgsqulBhqnQYJFs7Q'

# Define the regular expression pattern for matching track information from the mpd Log File
pattern = r'^(?P<month>\w+)\s(?P<day>\d+)\s(?P<time>\d{1,2}:\d{2})(?P<log>\s:\splayer:\splayed\s\")(?P<artist>\b.*\b)/(?P<album>\b.*\b)/(?P<tracknum>\d*\s)(?P<track>.*)(?P<filetype>\..*)(\"$)'


def extract_track_info(log_line):
    "Define a function to extract track information from a log line"
    match = re.search(pattern, log_line)
    if match:
        artist = match.group('artist')
        album = match.group('album')
        title = match.group('track')
        # track_number = match.group('tracknum').strip()
        # filetype = match.group('filetype')
        raw_timestamp = f"2023 {match.group('month')} {match.group('day')} {match.group('time')}"
        timestamp = int(datetime.strptime(raw_timestamp, "%Y %b %d %H:%M").timestamp())
        return {
            'artist': artist,
            'title': title,
            'album': album,
            'time': timestamp,
            'key': key
        }
    return None


# Loop through each log line and extract the necessary information
parsed_scrobbles = []
url = "http://scrobble.tswartz.net:42011/apis/mlj_1/newscrobble"
loopcount = 0
with open("/tmp/mpd2023-fixed.log", "r", encoding="utf-8") as f:
    for log in f:
        result = extract_track_info(log)
        if result:
            print(result)
            parsed_scrobbles.append(result)
            response = requests.post(url, json=result, timeout=10)
            if response.status_code == 200:
                loopcount += 1
                if loopcount % 100 == 0:
                    print(f"Parsed {loopcount} records so far")
                continue
            print("Request failed", response.status_code)

with open("scrobble_data.json", "w", encoding='utf-8') as f:
    json.dump(parsed_scrobbles, f)

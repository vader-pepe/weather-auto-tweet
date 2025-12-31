from datetime import datetime
from dotenv import load_dotenv, find_dotenv

import requests
import time
import tweepy
import os


# ——————————————
# CONFIGURATION
# ——————————————

load_dotenv(find_dotenv())
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_KEY_SECRET')
bearer_token = os.getenv('BEARER_TOKEN')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
LOCATION_NAME = os.getenv('LOCATION_NAME')
client = tweepy.Client(bearer_token, api_key, api_secret,
                       access_token, access_token_secret)

# Schedule times (24h format)
# Change these strings to the times you want
SCHEDULE = {
    "pagi":   "08:00",
    "siang":  "12:00",
    "sore":   "17:00",
    "malam":  "20:00",
}

WEATHER_CODE_MAP = {
    0: "cerah",                    # Clear sky / Langit cerah
    1: "sebagian besar cerah",     # Mainly clear / Sebagian besar cerah
    2: "berawan sebagian",         # Partly cloudy / Berawan sebagian
    3: "berawan",                  # Overcast / Berawan
    45: "berkabut",                # Foggy / Berkabut
    48: "berkabut",                # Foggy / Berkabut
    51: "gerimis ringan",          # Light drizzle / Gerimis ringan
    53: "gerimis sedang",          # Moderate drizzle / Gerimis sedang
    55: "gerimis lebat",           # Dense drizzle / Gerimis lebat
    61: "hujan ringan",            # Light rain / Hujan ringan
    63: "hujan sedang",            # Moderate rain / Hujan sedang
    65: "hujan lebat",             # Heavy rain / Hujan lebat
    80: "hujan lokal",             # Rain showers / Hujan lokal / shower
    95: "badai petir",             # Thunderstorm / Badai petir
    99: "badai petir hebat"        # Severe thunderstorm / Badai petir hebat
}


def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&timezone=auto"
    )
    return requests.get(url).json()


def get_time_of_day(hour: int) -> str:
    if 5 <= hour < 12:
        return "pagi"
    if 12 <= hour < 16:
        return "siang"
    if 16 <= hour < 19:
        return "sore"
    return "malam"


def tweet(text):
    try:
        response = client.create_tweet(text=text)
        print("Tweet response:", response)
        return True  # success
    except Exception as e:
        print("Tweet failed:", e)
        return False  # failure


def build_weather_message(data, location_name="your area"):
    cw = data.get("current_weather", {})
    temp = cw.get("temperature")
    code = cw.get("weathercode")
    dt_str = cw.get("time")

    dt = datetime.fromisoformat(dt_str)
    tod = get_time_of_day(dt.hour)

    cond = WEATHER_CODE_MAP.get(code, "weather")

    templates = {
        "pagi": f"Pagi ini di {location_name} cuaca {cond}, sekitar {temp}°C.",
        "siang": f"Siang hari di {location_name} dengan {cond} dan suhu sekitar {temp}°C.",
        "sore": f"Sore di {location_name}, {cond} dengan temperature {temp}°C.",
        "malam": f"Malam di {location_name}, keadaan {cond} dengan suhu {temp}°C."
    }

    return templates.get(tod)


# Keeps track of last day of each run so we don’t do the same one twice
last_run_day = {k: None for k in SCHEDULE}

# ——————————————
# LOOP
# ——————————————

print("Scheduler started.")

while True:
    now = datetime.now()
    now_str = now.strftime("%H:%M")

    for label, target_time in SCHEDULE.items():
        # Check if it matches the scheduled time
        # exactly and not already run today
        if now_str == target_time and last_run_day[label] != now.date():

            print(f"Time to run {label} at {
                  target_time} — trying fetch weather...")

            # Retry loop for weather fetch
            success = False
            while not success:
                try:
                    data = fetch_weather(LATITUDE, LONGITUDE)
                    msg = build_weather_message(data, LOCATION_NAME)
                    print(msg)  # Replace with sending/posting logic
                    tweeted = tweet(msg)
                    if tweeted:
                        success = True
                    else:
                        print("Retrying tweet in 30 seconds...")
                        time.sleep(30)
                except Exception as e:
                    print("Fetch failed, retrying...", e)
                    time.sleep(30)  # wait before retry

            # Mark this schedule as done for today
            last_run_day[label] = now.date()

    # Sleep so this loop doesn’t block CPU too hard
    time.sleep(30)

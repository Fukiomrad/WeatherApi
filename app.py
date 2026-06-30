from flask import Flask, request, render_template
import requests
import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

cache = None
try:
    cache = redis.from_url(REDIS_URL)
    cache.ping()
except:
    pass

CACHE_TTL = 43200  # 12 hours

CONDITION_ICONS = {
    "rain": "🌧", "drizzle": "🌦", "shower": "🌧",
    "snow": "❄️", "sleet": "🌨", "ice": "🌨",
    "thunderstorm": "⛈", "storm": "⛈", "lightning": "⛈",
    "fog": "🌫", "mist": "🌫", "haze": "🌫",
    "cloudy": "☁️", "overcast": "☁️",
    "partly cloudy": "⛅", "partly cloudy": "⛅",
    "clear": "☀️", "sunny": "☀️",
    "windy": "💨", "breeze": "💨",
}


def get_condition_icon(conditions):
    conditions_lower = conditions.lower()
    for keyword, icon in CONDITION_ICONS.items():
        if keyword in conditions_lower:
            return icon
    return "🌡"


def fetch_weather(city):
    if not API_KEY:
        return None, "API key not configured"

    cache_key = f"weather:v2:{city.lower()}"

    if cache:
        cached = cache.get(cache_key)
        if cached:
            return json.loads(cached), None

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={API_KEY}"

    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.RequestException:
        return None, "Weather service unavailable"

    if resp.status_code == 400:
        return None, f"City '{city}' not found"
    if resp.status_code != 200:
        return None, "Could not fetch weather"

    data = resp.json()
    conditions = data["currentConditions"]["conditions"]
    result = {
        "city": city,
        "temp": data["currentConditions"]["temp"],
        "conditions": conditions,
        "icon": get_condition_icon(conditions),
    }

    if cache:
        cache.setex(cache_key, CACHE_TTL, json.dumps(result))

    return result, None


@app.route("/")
def home():
    city = request.args.get("city")
    if city:
        weather, error = fetch_weather(city)
        return render_template("index.html", weather=weather, error=error, city=city)
    return render_template("index.html", weather=None, error=None, city="")


@app.route("/weather")
def get_weather():
    city = request.args.get("city")
    if not city:
        return {"error": "city parameter is required"}, 400

    if not API_KEY:
        return {"error": "API key not configured"}, 500

    weather, error = fetch_weather(city)
    if error:
        status = 500
        if "not found" in error:
            status = 404
        elif "unavailable" in error:
            status = 502
        return {"error": error}, status
    return weather, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

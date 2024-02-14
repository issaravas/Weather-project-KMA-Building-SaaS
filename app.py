import datetime as dt
import requests
from flask import Flask, jsonify, request

API_KEY = "FUZZR78UGEZAYXR6PV9EQHD4Q"

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

def get_weather_data(location: str, date: str):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

    url = f"{base_url}{location}/{date}?unitGroup=metric&key={API_KEY}"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Weather Service.</h2></p>"

@app.route("/weather", methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    location = json_data.get("location")
    date = json_data.get("date")

    if not location or not date:
        raise InvalidUsage("Location and date are required", status_code=400)

    weather_data = get_weather_data(location, date)

    return jsonify(weather_data)

if __name__ == "__main__":
    app.run(debug=True)

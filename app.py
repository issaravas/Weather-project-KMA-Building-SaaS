import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = "[your special token]"
API_KEY ='API_KEY (from https://www.visualcrossing.com/account)'

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

def get_weather_data(location, date):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    url = f"{base_url}/{location}/{date}?key={API_KEY}&include=days&unitGroup=metric"

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
    
    if json_data.get("token") is None:
        raise InvalidUsage("Token is required", status_code=400)
    if json_data.get("requester_name") is None:
        raise InvalidUsage("Requester name is required", status_code=400)
    if json_data.get("location") is None:
        raise InvalidUsage("Location is required", status_code=400)
    if json_data.get("date") is None:
        raise InvalidUsage("Date is required", status_code=400)

    token = json_data.get("token")
    
    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    requester_name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")
    timestamp = dt.datetime.utcnow().replace(microsecond=0).isoformat()

    weather_data = get_weather_data(location, date)

    #converting windspeed from miles per hour to kilometres per hour
    windspeed_ml = weather_data.get("days")[0]["windspeed"]
    windspeed_kph = round(windspeed_ml * 1.609)
    
    #adding recommendation based on Precipitation Type
    preciptype = weather_data.get("days")[0]["preciptype"]   
    recommendation = ""
    if not preciptype:
        recommendation = "No precipitation information available."
    elif "rain" in preciptype:
        recommendation = "It's a rainy day, don't forget to bring an umbrella with you!"
    elif "snow" in preciptype:
        recommendation = "It's a snowy day, please dress warmly!"

    #outputting the result    
    result = {
        "requester_name": requester_name,
        "timestamp": timestamp,
        "location": location,
        "date": date,
        "weather": {
            "temp_c": weather_data.get("days")[0]["temp"],
            "feelslike": weather_data.get("days")[0]["feelslike"],
            "wind_kph": windspeed_kph,
            "preciptype": preciptype,
            "moonphase": weather_data.get("days")[0]["moonphase"],
            "sunrise": weather_data.get("days")[0]["sunrise"],            
            "sunset": weather_data.get("days")[0]["sunset"],
            "recommendation": recommendation
        }
    }
    return result

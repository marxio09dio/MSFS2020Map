from flask import Flask, jsonify, render_template, request
from SimConnect import *
from time import sleep
import random


app = Flask(__name__)


# Create simconnection
sm = SimConnect()
aq = AircraftRequests(sm, _time=10)

# Create request holders

request_location = [
	'ALTITUDE',
	'LATITUDE',
	'LONGITUDE',
	'HSI_DISTANCE',
]

# need to check whats the ground speed variable in SDK
request_speed = [
	'AIRSPEED_TRUE',
	'AIRSPEED_INDICATE',
	'GROUND_VELOCITY'

]

request_compass = [
	'MAGNETIC_COMPASS',  # Compass reading
]

request_vertical_speed = [
	'VELOCITY_BODY_Y',  # True vertical speed, relative to aircraft axis
	'RELATIVE_WIND_VELOCITY_BODY_Y',  # Vertical speed relative to wind
	'VERTICAL_SPEED',  # Vertical speed indication
	'GPS_WP_VERTICAL_SPEED',  # Vertical speed to waypoint
]


def thousandify(x):
	return f"{x:,}"


@app.route('/')
def glass():
	return render_template("map.html")


def get_dataset(data_type):
	if data_type == "navigation": request_to_action = request_location
	if data_type == "airspeed": request_to_action = request_speed
	if data_type == "compass": request_to_action = request_compass
	if data_type == "vertical_speed": request_to_action = request_vertical_speed

	return request_to_action


@app.route('/ui')
def output_ui_variables():

	# Initialise dictionary
	ui_friendly_dictionary = {}
	ui_friendly_dictionary["STATUS"] = "success"

	# Speed
	ui_friendly_dictionary["ALTITUDE"] = thousandify(round(aq.get("PLANE_ALTITUDE")))
	ui_friendly_dictionary["GROUND_VELOCITY"] = round(aq.get("GROUND_VELOCITY"))

	# Navigation
	ui_friendly_dictionary["LATITUDE"] = aq.get("PLANE_LATITUDE")
	ui_friendly_dictionary["LONGITUDE"] = aq.get("PLANE_LONGITUDE")
	ui_friendly_dictionary["MAGNETIC_COMPASS"] = round(aq.get("MAGNETIC_COMPASS"))
	ui_friendly_dictionary["VERTICAL_SPEED"] = round(aq.get("VERTICAL_SPEED"))
	ui_friendly_dictionary["HSI_DISTANCE"] = round(aq.get("HSI_DISTANCE"))


	return jsonify(ui_friendly_dictionary)



app.run(host='0.0.0.0', port=5000, debug=True)
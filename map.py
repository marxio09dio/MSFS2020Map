from flask import Flask, jsonify, render_template, request
from SimConnect import *
from time import sleep
import random


app = Flask(__name__)


# Create simconnection
sm = SimConnect()
ae = AircraftEvents(sm)
aq = AircraftRequests(sm, _time=10)

# Create request holders

request_location = [
	'ALTITUDE',
	'LATITUDE',
	'LONGITUDE',
	'KOHLSMAN',
]

request_airspeed = [
	'AIRSPEED_TRUE',
	'AIRSPEED_INDICATE',
	'AIRSPEED_TRUE CALIBRATE',
	'AIRSPEED_BARBER POLE',
	'AIRSPEED_MACH',
]

request_compass = [
	'WISKEY_COMPASS_INDICATION_DEGREES',
	'PARTIAL_PANEL_COMPASS',
	'ADF_CARD',  # ADF compass rose setting
	'MAGNETIC_COMPASS',  # Compass reading
	'INDUCTOR_COMPASS_PERCENT_DEVIATION',  # Inductor compass deviation reading
	'INDUCTOR_COMPASS_HEADING_REF',  # Inductor compass heading
]

request_vertical_speed = [
	'VELOCITY_BODY_Y',  # True vertical speed, relative to aircraft axis
	'RELATIVE_WIND_VELOCITY_BODY_Y',  # Vertical speed relative to wind
	'VERTICAL_SPEED',  # Vertical speed indication
	'GPS_WP_VERTICAL_SPEED',  # Vertical speed to waypoint
]


request_cabin = [
	'CABIN_SEATBELTS_ALERT_SWITCH',
	'CABIN_NO_SMOKING_ALERT_SWITCH'
]


def thousandify(x):
	return f"{x:,}"


@app.route('/')
def glass():
	return render_template("map.html")


def get_dataset(data_type):
	if data_type == "navigation": request_to_action = request_location
	if data_type == "airspeed": request_to_action = request_airspeed
	if data_type == "compass": request_to_action = request_compass
	if data_type == "vertical_speed": request_to_action = request_vertical_speed
	if data_type == 'cabin': request_to_action = request_cabin
	#if data_type == "ui": request_to_action = request_ui   # see comment above as to why I've removed this

	return request_to_action


@app.route('/ui')
def output_ui_variables():

	# Initialise dictionaru
	ui_friendly_dictionary = {}
	ui_friendly_dictionary["STATUS"] = "success"

	# Speed
	ui_friendly_dictionary["AIRSPEED_INDICATE"] = round(aq.get("AIRSPEED_INDICATED"))
	ui_friendly_dictionary["ALTITUDE"] = thousandify(round(aq.get("PLANE_ALTITUDE")))


	# Navigation
	ui_friendly_dictionary["LATITUDE"] = aq.get("PLANE_LATITUDE")
	ui_friendly_dictionary["LONGITUDE"] = aq.get("PLANE_LONGITUDE")
	ui_friendly_dictionary["MAGNETIC_COMPASS"] = round(aq.get("MAGNETIC_COMPASS"))
	ui_friendly_dictionary["VERTICAL_SPEED"] = round(aq.get("VERTICAL_SPEED"))


	return jsonify(ui_friendly_dictionary)



app.run(host='0.0.0.0', port=5000, debug=True)
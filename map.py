from flask import Flask, jsonify, render_template, request
from SimConnect import *
from time import sleep
import random


app = Flask(__name__)

# SIMCONNECTION RELATED STARTUPS

# Create simconnection
sm = SimConnect()
ae = AircraftEvents(sm)
aq = AircraftRequests(sm, _time=10)

# Create request holders

# Note: I have commented out request_ui as I don't think it makes sense to replicate the ui interface through JSON given the /ui endpoint returns a duplicate of this anyway
# I have not deleted it yet as it's handy to have this list of helpful variables here
#
#request_ui = [
#	'PLANE_ALTITUDE',
#	'PLANE_LATITUDE',
#	'PLANE_LONGITUDE',
#	'AIRSPEED_INDICATED',
#	'MAGNETIC_COMPASS',  # Compass reading
#	'VERTICAL_SPEED',  # Vertical speed indication
#	'FLAPS_HANDLE_PERCENT',  # Percent flap handle extended
#	'FUEL_TOTAL_QUANTITY',  # Current quantity in volume
#	'FUEL_TOTAL_CAPACITY',  # Total capacity of the aircraft
#	'GEAR_HANDLE_POSITION',  # True if gear handle is applied
#	'AUTOPILOT_MASTER',
#	'AUTOPILOT_NAV_SELECTED',
#	'AUTOPILOT_WING_LEVELER',
#	'AUTOPILOT_HEADING_LOCK',
#	'AUTOPILOT_HEADING_LOCK_DIR',
#	'AUTOPILOT_ALTITUDE_LOCK',
#	'AUTOPILOT_ALTITUDE_LOCK_VAR',
#	'AUTOPILOT_ATTITUDE_HOLD',
#	'AUTOPILOT_GLIDESLOPE_HOLD',
#	'AUTOPILOT_PITCH_HOLD_REF',
#	'AUTOPILOT_APPROACH_HOLD',
#	'AUTOPILOT_BACKCOURSE_HOLD',
#	'AUTOPILOT_VERTICAL_HOLD',
#	'AUTOPILOT_VERTICAL_HOLD_VAR',
#	'AUTOPILOT_PITCH_HOLD',
#	'AUTOPILOT_FLIGHT_DIRECTOR_ACTIVE',
#	'AUTOPILOT_AIRSPEED_HOLD',
#	'AUTOPILOT_AIRSPEED_HOLD_VAR'
#]

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


@app.route('/attitude-indicator')
def AttInd():
	return render_template("attitude-indicator/index.html")


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

	# Fuel
	ui_friendly_dictionary["AIRSPEED_INDICATE"] = round(aq.get("AIRSPEED_INDICATED"))
	ui_friendly_dictionary["ALTITUDE"] = thousandify(round(aq.get("PLANE_ALTITUDE")))


	# Navigation
	ui_friendly_dictionary["LATITUDE"] = aq.get("PLANE_LATITUDE")
	ui_friendly_dictionary["LONGITUDE"] = aq.get("PLANE_LONGITUDE")
	ui_friendly_dictionary["MAGNETIC_COMPASS"] = round(aq.get("MAGNETIC_COMPASS"))
	ui_friendly_dictionary["VERTICAL_SPEED"] = round(aq.get("VERTICAL_SPEED"))


	# Cabin
	ui_friendly_dictionary["CABIN_SEATBELTS_ALERT_SWITCH"] = aq.get("CABIN_SEATBELTS_ALERT_SWITCH")
	ui_friendly_dictionary["CABIN_NO_SMOKING_ALERT_SWITCH"] = aq.get("CABIN_NO_SMOKING_ALERT_SWITCH")

	return jsonify(ui_friendly_dictionary)


@app.route('/dataset/<dataset_name>/', methods=["GET"])
def output_json_dataset(dataset_name):
	dataset_map = {}  #I have renamed map to dataset_map as map is used elsewhere
	data_dictionary = get_dataset(dataset_name)
	for datapoint_name in data_dictionary:
		dataset_map[datapoint_name] = aq.get(datapoint_name)
	return jsonify(dataset_map)


def get_datapoint(datapoint_name, index=None):
	# This function actually does the work of getting the datapoint

	if index is not None and ':index' in datapoint_name:
		dp = aq.find(datapoint_name)
		if dp is not None:
			dp.setIndex(int(index))

	return aq.get(datapoint_name)


@app.route('/datapoint/<datapoint_name>/get', methods=["GET"])
def get_datapoint_endpoint(datapoint_name):
	# This is the http endpoint wrapper for getting a datapoint

	ds = request.get_json() if request.is_json else request.form
	index = ds.get('index')

	output = get_datapoint(datapoint_name, index)

	if isinstance(output, bytes):
		output = output.decode('ascii')

	return jsonify(output)


def set_datapoint(datapoint_name, index=None, value_to_use=None):
	# This function actually does the work of setting the datapoint

	if index is not None and ':index' in datapoint_name:
		clas = aq.find(datapoint_name)
		if clas is not None:
			clas.setIndex(int(index))

	sent = False
	if value_to_use is None:
		sent = aq.set(datapoint_name, 0)
	else:
		sent = aq.set(datapoint_name, int(value_to_use))

	if sent is True:
		status = "success"
	else:
		status = "Error with sending request: %s" % (datapoint_name)

	return status


@app.route('/datapoint/<datapoint_name>/set', methods=["POST"])
def set_datapoint_endpoint(datapoint_name):
	# This is the http endpoint wrapper for setting a datapoint

	ds = request.get_json() if request.is_json else request.form
	index = ds.get('index')
	value_to_use = ds.get('value_to_use')

	status = set_datapoint (datapoint_name, index, value_to_use)

	return jsonify(status)


def trigger_event(event_name, value_to_use = None):
	# This function actually does the work of triggering the event

	EVENT_TO_TRIGGER = ae.find(event_name)
	if EVENT_TO_TRIGGER is not None:
		if value_to_use is None:
			EVENT_TO_TRIGGER()
		else:
			EVENT_TO_TRIGGER(int(value_to_use))

		status = "success"
	else:
		status = "Error: %s is not an Event" % (event_name)

	return status


@app.route('/event/<event_name>/trigger', methods=["POST"])
def trigger_event_endpoint(event_name):
	# This is the http endpoint wrapper for triggering an event

	ds = request.get_json() if request.is_json else request.form
	value_to_use = ds.get('value_to_use')

	status = trigger_event(event_name, value_to_use)

	return jsonify(status)



app.run(host='0.0.0.0', port=5000, debug=True)
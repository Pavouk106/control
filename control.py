#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os.path, datetime, time
import RPi.GPIO as IO

debug = True

# PRE-SETUP

path_to_files = "/tmp/"

temps_values = [None] * 8

# GPIO pins assignments
# 21 = disconnect original control circuitry
# 20 = (circulation pump)
# 26 = three-way valve
# 16 = (???)
# 19 = (???)
# 13 = not used
# 12 = not used
# 17 = internal thermostat (parallel)
io_pins = [21, 20, 26, 16, 19, 13, 12, 17]
io_values = [False] * 8

# Set pins to OUTPUT
IO.setwarnings(False)
IO.setmode(IO.BCM)

for i in range(0, len(io_pins)):
	IO.setup(io_pins[i], IO.OUT)

# Number of failed attempts of something (read from file, temperature reading failed, etc.)
failed_count = 0

# Various state variables
heating_water = False # Water heating on/off

# DEFINE FUNCTIONS

# Print debug
def debug_print(text):
	if debug:
		print(text)

# Turn all outputs to low, cut-off control
def fail_safe():
	debug_print(time.strftime("%H:%M:%S") + ": " + "Fail-safe just kicked in, yo!")
	for i in range(0, len(io_pins)):
		io_values[i] = False # Set outputs to low (off)

# Load temperatures from file
def read_temps():
	global temps_values
	try: # Read temperatures from file
		tries = 0 # Number of tries before failing
		temps_values = [None] * 8
		while (len(temps_values) < 8 or temps_values[0] == None) and tries < 5: # If read didn't fail but loaded less than 8 lines
			temps_file = open(path_to_files + 'temps', 'r')
			temps_values = temps_file.read().splitlines() # Fill list with values
			temps_file.close()
			tries += 1
		debug_print("read_temps(): File opened")
	except: # Couldn't open the file (blocked by other process, file not found, etc.)
		debug_print("read_temps(): Can't open file")
		temps_values = ["---"] * 8 # Fill list with error string
		pass
	if len(temps_values) < 8: # Read from file ok, but less than 8 lines
		debug_print("read_temps(): Less than 8 lines loaded")
		temps_values = ["---"] * 8 # Fill list with error string

def read_states():
	global states_values
	try:
		tries = 0 # Number of tries before failing
		states_values = [None] * 4
		while (len(states_values) < 4 or states_values[0] == None) and tries < 5: # If read didn't fail but loaded less than 4 lines
			states_file = open(path_to_files + 'states', 'r')
			states_values = states_file.read().splitlines() # Fill list with values
			states_file.close()
			tries += 1
		debug_print("read_states(): File opened")
	except: # Couldn't open the file (blocked by other process, file not found, etc.)
		debug_print("read_states(): Can't open file")
		states_values = ["---"] * 4 # Fill list with error string
		pass
	if len(states_values) < 4: # Read from file ok, but less than 4 lines
		debug_print("read_states(): Less than 4 lines loaded")
		states_values = ["---"] * 4 # Fill list with error string

# Heat water if needed
# TO DO: and no other conditions block this
def heat_water():
	global failed_count, heating_water, temps_values, io_values
	if temps_values[4] == "---" or temps_values[4] == None: # Read failed
		if heating_water: # Apply only if water heating is on
			failed_count += 1 # Count failed attempts before action
			if failed_count >= 5: # 30 seconds before fail-safe
				fail_safe() # Activate failsafe
				heating_water = False # Reset state
	else: # Read ok
		failed_count = 0 # Reset failed attempts count
		if float(temps_values[4]) <= 55 and not heating_water: # Water is cold; TO DO: and no other conditions block this action
			heating_water = True
			debug_print("heat_water(): " + time.strftime("%H:%M:%S") + ": Heating water on")
			io_values[2] = True
			io_values[7] = True
		elif float(temps_values[4]) > 65 and heating_water: # Water heated; TO DO: and no othe conditions block this action
			heating_water = False
			debug_print("heat_water(): " + time.strftime("%H:%M:%S") + ": Heating water off")
			io_values[2] = False
			io_values[7] = False

# Set all the pins to their new values
def write_outputs():
	global io_pins, io_values
	debug_print("write_outputs(): " + format(io_values))
	for i in range(0, len(io_pins)):
		IO.output(io_pins[i], io_values[i])

# MAIN LOOP
while 1:
	read_temps()
	read_states()
	heat_water()
	write_outputs()

#	debug_print(temps_values)
#	debug_print(time.strftime("%H:%M:%S"))
#	debug_print(io_values)

	time.sleep(5)

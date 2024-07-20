#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os.path, re, time

debug = 0

path_to_files = "/tmp/"

temps_values = [None] * 8
dallas_address = [
"28-000006dbdc8f", # voda mix / water mix
"28-000001b47c96", # voda cerpadlo / water pump
"28-000006db6ccf", # voda vracecka / water return
"28-0316b49f45ff", # kotel nahore / boiler top
"28-0316a06b59ff", # bojler nahore / water heater top
"28-0316a347c9ff", # bojler dole / water heater bottom
"28-0516b497ccff", # solar tepla / solat hot
"28-0316b49ee9ff" # solar studena / solar cold
]

while 1:
	# Read dallas temperature sensors
	for i in range(0, len(dallas_address)):
		try:
			temp_file = open('/sys/bus/w1/devices/' + dallas_address[i] + '/w1_slave', 'r')
			file_lines = temp_file.read().splitlines()
			crc = re.compile('crc=.. (.*)')
			crc_value = crc.search(file_lines[0])
			if debug:
				print(crc_value.group(1))
			if crc_value.group(1) == "YES":
				temp = re.compile('t=(.*)')
				temp_value = temp.search(file_lines[1])
				if debug:
					print(temp_value.group(1))
				if temp_value.group(1) != "85000":
					temps_values[i] = round(float(temp_value.group(1)) / 1000, 1)
				else:
					temps_values[i] = u"---"
			else:
				temps_values[i] = u"---"
		except:
				temps_values[i] = u"---"
				if debug:
					print('DEBUG: ' + '/sys/bus/w1/devices/' + dallas_address[i] + '/w1_slave' + ' Temp read failed')
				pass

	# Write dallas temperature sensors readings to file
	try:
		temps_file_json = open(path_to_files + 'temps.json', 'w')
		temps_file_json.write('{ "Teplota vody (mix)": {"teplota": "%s"}, "Teplota vody (čerpadlo)": {"teplota": "%s"}, "Teplota vody (vracečka)": {"teplota": "%s"}, "Teplota vody (kotel)": {"teplota": "%s"}, "Teplota bojleru (nahoře)": {"teplota": "%s"}, "Teplota bojleru (dole)": {"teplota": "%s"}, "Solární ohřev (teplá)": {"teplota": "%s"}, "Solární ohřev (studená)": {"teplota": "%s"}}' % (temps_values[0], temps_values[1], temps_values[2], temps_values[3], temps_values[4], temps_values[5], temps_values[6], temps_values[7]))
		temps_file_json.close()
		temps_file = open(path_to_files + 'temps', 'w')
		for i in range(0, len(temps_values) + 1):
			if i < len(temps_values) and temps_values[i] == u"---":
				temps_file.write("%s\n" % temps_values[i])
			elif i < len(temps_values):
				temps_file.write("%s\n" % temps_values[i])
		temps_file.close()
	except:
		pass
	time.sleep(1)

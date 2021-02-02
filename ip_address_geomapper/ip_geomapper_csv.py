# API related packages
import requests
import json

# Import/Export related packages
import csv
import time
from datetime import datetime
import re

# Error messages
import logging

logging.basicConfig(level=logging.INFO)

# Takes in IP address, calls ipinfo.io, returns JSON received.
def retrieve_ip_details(user_ip):
	# Defines request
	endpoint = "https://ipinfo.io/"

	resp = requests.get(
	    (endpoint + user_ip)
		)

	if resp.status_code == 429:
		raise RateLimitError("Rate limit hit.")

	elif resp.status_code == 200:
		ip_details = json.loads(resp.text)

		print("Success: {} is found in:".format(user_ip))
		print("City: {}".format(ip_details["city"]))
		print("Region: {}".format(ip_details["region"]))
		print("Country: {}\n".format(ip_details["country"]))

	return(ip_details)

# Takes in a list of ip addresses, outputs json object with ip address details.
def create_ip_details_list(ip_list):
	
	skipped_ip_needs_retry = []
	output_list = []

	for ip_address in ip_list:
		try:
			details = retrieve_ip_details(ip_address)
			output_list.append(details)
		except RateLimitError:
			print("RateLimitError: Skipping IP")
			skipped_ip_needs_retry.append(ip_address)

	return(output_list)

# Exports .csv with a list of IP addresses
# Used when rate limit is hit
def export_skipped_ip(skipped_ip_needs_retry, export_name):
	
	# Failsafe to prevent overwriting
	now = datetime.now()
	current_time = now.strftime("H%H_M%M_S%S")
	print("Current Time = {}".format(current_time))

	g = csv.writer(open(export_name + current_time + ".csv","w", newline=""))

	for ip in skipped_ip_needs_retry:
		g.writerow(str(ip))

# Takes a text file, reads each line and looks for an IP address, outputs a list of IP addresses.
# Format of matched IP address will be in format [#.#.#], where # can be 0-999.
def txt_to_ip_list(doc_name):
	print("Opening {} and generating IP address list".format(str(doc_name)))
	file = open(doc_name, "r")
	out = []
	line_index = 0

	while True:
		line = file.readline()

		if not line: # If the line is empty
			break

		else:
			# Looks for only IP addresses
			pattern = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
			match_obj = pattern.search(line)
			ip_only = match_obj.group(0) # Entire match
			line_index += 1

			out.append(ip_only)

	file.close()

	print("Success: IP address list generated. Entries: %s", len(out))
	return(out)

# Start main
doc_name = "ip_list_test.txt"
print("Import: {}".format(doc_name))

test_list = [
	"192.168.1.1",
	"192.168.1.2",
	"192.168.1.3",
	"192.168.1.4",
	"192.168.1.5",
	"192.168.1.6",
	"192.168.1.7",
	"192.168.1.8",
	"192.168.1.9"
]

print("hello")
export_skipped_ip(test_list, "part1")


# b = txt_to_ip_list(doc_name)
# c = create_ip_details_list(b)




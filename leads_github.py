import requests
import json
import csv
import time
from datetime import datetime

# Sets access
AUTH_TOKEN = "65116425bc8f0d7d9a7b9e12e4659b1f8f828214"
USER_SEARCH_ENDPOINT = "https://api.github.com/search/users"

# NOTE: Delete if not needed but don't rename,
# these match the JSON response parameter names.
CSV_HEADERS = [
	"login",
	"id",
	"name",
	"email",
	"location",
	"bio",
	"company",
	"blog",
	"twitter_username",
	"public_repos",
	"followers",
	"hireable"
	]


# Search Setup
endpoint = USER_SEARCH_ENDPOINT
page_index = 1
pages = 10
params = {
	# MAKING CHANGES TO THE "Q" PARAMETER WILL DO NOTHING, SEE NOTE IN SEARCH REQUEST
	"q": "language:\"JavaScript\" location:\"India\"",
	"per_page": "100", # GitHub API has rule max 100.
}

# Headers (Optional)
headers = {
	"Authorization": "Bearer " + AUTH_TOKEN,
	"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
}

# Search Request
user_list = [] # user_list is an `list` of tuples that match order of CSV header ("login", "id", "name"...)
while page_index < (pages + 1):
	print("Processing page " + str(page_index) + "...")

	  params.update({"page": page_index})
	# Detail: r0 is a search request, r1 is a user request with info received from search results
	r0 = requests.get(
	    (endpoint),
	    headers=headers,
	    params=params
		)

	# # Outdated way of doing the same thing. 
	# Note that "params" must be updated in the while loop otherwise "page" will not advance.
	# r0 = requests.get(
	#     (endpoint + "?q=language:\"JavaScript\" location:\"India\"&per_page=100&page=" + str(page_index))
	# 	)

	# Load JSON
	s_resp = json.loads(r0.text)

	try:
		list_of_new_data = s_resp["items"] 	# "items" is the parent param of the JSON object with user list
											# s_resp["items"] is a list of the new users in that page of results
		user_list = user_list + list_of_new_data
		print(" ---> Success: user list now contains " + str(len(user_list)) + " entries." )
		page_index = page_index + 1
	except:
		
		# If error is received by GitHub API:

		# 403 Forbidden: commonly rate limit, looks for "limit" in API response
		if "limit" in s_resp["message"]:
			print("GitHub API Response:")
			print(json.dumps(s_resp, indent=4, sort_keys=True))
			print("API rate limit hit: sleeping for 60 seconds...")
			now = datetime.now()

			current_time = now.strftime("%H:%M:%S")
			print("Current Time =", current_time)

			time.sleep(60)

			print("Waking up, trying page " + str(page_index) + " again...")

			# Do not advance page_index counter and current page will be retried.

		# GitHub API has 1000 result max, this prevents script from halting when this limit is hit.
		elif "first" in s_resp["message"]:
			print("GitHub API Response:")
			print(s_resp["message"])
			print("SEARCH LIMIT DETECTED: script will stop adding more entries and will continue with current list.\n")
			break

		else:
			print("GitHub API Response:")
			print(s_resp["message"])


print("PROCESSING COMPLETE. PREPARING EXPORT...")

# Exported CSV setup
export_name = "github_user_search_export"
g = csv.writer(open(export_name + ".csv","w", newline=""))

g.writerow(CSV_HEADERS)

index = 0


for user_item in user_list:
	# Search request returns list of basic user info.
	# Search request does not return name, email etc.
	# user_item is used to request user profile from user ID
	# A second API request is made to retrieve name, email, etc.

	r1 = requests.get(
		(user_item["url"]),
		headers=headers,
		params=params
	)

	u_resp = json.loads(r1.text)

	profile = []

	print("\n######## Processing Lead #" + str(index + 1) + " of " + str(len(user_list)) + "... ########")
	for header_title in CSV_HEADERS:
		try:
			profile.append(u_resp[header_title])
			print(header_title + ": " + str(u_resp[header_title]))
		except:
			print("ERROR")
			print(u_resp)

	g.writerow(profile)

	index = index + 1

print("\nExport complete. File generated: " + export_name + ".csv\n")

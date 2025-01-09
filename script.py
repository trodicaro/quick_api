
import os
import time
import urllib

from dotenv import load_dotenv
import pandas
import requests 
from tenacity import retry, stop_after_attempt, wait_exponential

# response = requests.get(call_text, headers=auth_header)
# df = pandas.DataFrame(response.json()['value'])

# next_link =  response.json().get('@odata.nextLink')
# while next_link:
# 	time.sleep(30)
# 	response = requests.get(next_link, headers=auth_header)
# 	print(next_link)
# 	df = pandas.concat([df, pandas.DataFrame(response.json()['value'])])
# 	print(df.shape)
load_dotenv()
import pdb;pdb.set_trace()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1)) # it waits 2^x * 1 second between each retry; min=1 waits 1s to start retries
def call_property_endpoint(url, headers, params):
    response = requests.get(url, headers=headers, params=params) # type(response.content) = <class 'bytes'>
    response.raise_for_status()
    return response.json() # type(response.json()) = <class 'dict'>

url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
headers = {
    'x-rapidapi-key': os.getenv("API_KEY"),
    'x-rapidapi-host': "zillow-com1.p.rapidapi.com"
}
params = {
	"location": "Chicago, IL",
	"status_type": "ForSale",
	"home_type": "Houses", 
	"minPrice": "300000",
	# "maxPrice": "350000",
	# "bedsMin": "3",
	# "bedsMax": "3",
}

current_page = 1
response = call_property_endpoint(url, headers, params)
if response:
	df = pandas.DataFrame(pandas.json_normalize(response))
	import pdb;pdb.set_trace()


while current_page <= response['totalPages']:
	current_page += 1
	print("Making get request for page {current_page}")
	url = url + "&page={current_page}"
	try:
		response = call_property_endpoint(url, headers, params)  
		print("Response data:", response.text)
	except Exception as err:
		print(f"Error when making the get request: {err}")
	
	if response:
		pandas.concat([df, pandas.DataFrame(response)])
		import pdb;pdb.set_trace()


# while current_page <= response.totalPages:
# 	current_page += 1
# 	call_string += "&page={current_page}"
# 	res = conn.request("GET", call_string)
# 	time.sleep(30)

# 	res = conn.getresponse()
# 	data = res.read()
#   print(data.decode("utf-8"))








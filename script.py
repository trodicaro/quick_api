
import os
import time
import urllib

from dotenv import load_dotenv
import pandas
import requests 
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1)) # it waits 2^x * 1 second between each retry; min=1 waits 1s to start retries
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
	"home_type": "Houses, Townhomes",
	"minPrice": "400000",
	"maxPrice": "450000",
	"bedsMin": "3",
}

current_page = 1
response = call_property_endpoint(url, headers, params)
if response:
	df = pandas.DataFrame(pandas.json_normalize(response['props']))

while current_page <= response['totalPages']:
	current_page += 1
	print(f"Making get request for page {current_page}")
	params['page'] = current_page
	try:
		response = call_property_endpoint(url, headers=headers, params=params)
		print(f"Current response record count: {response['resultsPerPage']}")
	except Exception as err:
		print(f"Error when making the get request: {err.__repr__()}")
	if response:
		addl_df = pandas.DataFrame(pandas.json_normalize(response['props']))
		df = pandas.concat([df, addl_df], ignore_index=True) # sub-frame indices are not relevant here

print(f"Total records before applying filters: {len(df)}")

# filter based on area; eg: east of Cicero Ave
df = df[df['longitude'].le(87.7450)]
print(f"Total records after applying longitude filter: {len(df)}")

# remove from set if contingent or on the market for too long
df = df[df['contingentListingType'].notnull() | df['daysOnZillow'].lt(180)]
print(f"Total records after applying contingent and days on market filters: {len(df)}")

# add column to mark records of particular interest
df['estimateDifference'] = df['zestimate'] - df['price']
df['specialInterest'] = (df['priceChange'] < 10000) | df['estimateDifference'].ge(10000)

df.to_csv("data.txt", sep='\t')









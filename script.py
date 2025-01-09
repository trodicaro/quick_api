
import os
import time
import urllib

import boto3
from dotenv import load_dotenv
import pandas
import requests 
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

############# PART 1 - API CALLS TO COLLECT DATA #############
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1)) # it waits 2^x * 1 second between each retry; min=1 waits 1s to start retries
def call_property_endpoint(url, headers, params):
    response = requests.get(url, headers=headers, params=params) # type(response.content) = <class 'bytes'>

    response.raise_for_status()
    return response.json() # type(response.json()) = <class 'dict'>

# /property endpoint has more detailed individual data
# /propertyExtendedSearch returns the property images
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
print(f"Making get request for first page")

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
	except Exception as error:
		print(f"Error when making the get request: {error.__repr__()}")
	if response:
		addl_df = pandas.DataFrame(pandas.json_normalize(response['props']))
		df = pandas.concat([df, addl_df], ignore_index=True) # sub-frame indices are not relevant here

############# PART 2 - DATA MANIPULATION #############

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

############# PART 3 - UPLOADING IMAGES TO AWS S3 #############

s3_client = boto3.client(
	's3',
	aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
	aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
	region_name=os.getenv('AWS_REGION')
)
s3_bucket = 'quickapi'

for row in df[['carouselPhotos', 'zpid']].itertuples(index=False): # zpid is the unique property identifier on zillow
	print(f"Starting upload for record {row.zpid}")
	for index, record in enumerate(row.carouselPhotos):
		print(f"Currently on image index {index}")
		# part 1 - load from weblink to a stream file
		try:
			response = requests.get(record['url'], stream=True)
			response.raise_for_status()
		except Exception as error:
			print(f"Error loading file: {error}")

		# part 2 - upload to S3
		s3_filepath = f"{row.zpid} - {index}"
		try:
			# s3_client.upload_file(s3_filepath, s3_bucket, object_name)
			s3_client.put_object(
				Bucket=s3_bucket,
				Key=s3_filepath,
				Body=response.content,
				ContentType=response.headers.get('Content-Type'),
				ACL='public-read'
			)
			print(f"File uploaded successfully to {s3_bucket}/{s3_filepath}")
		except Exception as error:
			print(f"Error uploading file: {error}")








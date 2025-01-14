Commands to run main script:

```python
pipenv shell
pipenv sync
python script.py
```
Note: a `.env` file is needed with the following:
```
API_KEY=
AWS_SECRET_ACCESS_KEY=
AWS_ACCESS_KEY_ID=
AWS_REGION=
```

The last section of the script downloads pictures from API and uploads to a public S3 bucket. Sample link to a random image in the bucket:
https://quickapi.s3.us-east-2.amazonaws.com/2061567773+-+2. 

Sample image:

![Sample photo](https://quickapi.s3.us-east-2.amazonaws.com/2061567773+-+2)

This script can be used: 

1. To further enrich real estate data for the collection of properties pulled (endpoint `/property`).
2. To perform various data analysis of properties available for sale.
3. To filter based on personal criteria and arrive at a small set of high-interest properties (anyone looking for a new place?).
4. To create a regular process that collects the records pulled by this script; additionally it could send a notification or trigger another process when done.
4. Download images to feed into ML computer vision algorithms; for this purpose, adding the use of [threads](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) would allow for faster downloads.
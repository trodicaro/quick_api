### Alternate way of making the api call
_avoids need to install the requests package; a bit more verbose though_
```python
import http.client
conn = http.client.HTTPSConnection("zillow-com1.p.rapidapi.com")
conn.request("GET", call_string, headers=headers)
res = conn.getresponse()
data = res.read().decode("utf-8")
```

### If issues with passing params in the api call -> build the query string of params
* space is encoded as %20; ampersand (&) is encoded as %26; etc
* parameters are linked with "&"
* apply encoding only once; either `urlencode` for a dictionary or `quote` for a query string
if special characters in one of the params, wrap with ```quote```
* I once pulled my hair debugging a failing call because of a single quote versus a double quote in the query string

```python
from urllib.parse import urlencode, quote
params = {
    "location": "Chicago, IL; Lincolnwood, IL",
	"status_type": "ForSale",
	"home_type": "Houses", 
}
urlencode(params)
# location=Chicago%2C+IL%3B+Lincolnwood%2C+IL&status_type=ForSale&home_type=Houses

raw_call_string = "&".join(["=".join([a,b]) for (a,b,) in zip(params.keys(), params.values())])
# location=Chicago, IL; Lincolnwood, IL&status_type=ForSale&home_type=Houses
quote(raw_query_string)
# location%3DChicago%2C%20IL%3B%20Lincolnwood%2C%20IL%26status_type%3DForSale%26home_type%3DHouses

```
### Strategies for rate limiting (API's implement this in order to prevent abuse of their servers)
* naive fix: add time delays; eg: ```import time; time.sleep(30)```
* fine tune  the api query to reduce the total data received response: 
  * query for specific fields only
  * use filters if made available by the API
* query in "incremental" mode: pull records newer than a date or timestamp, save results to avoid re-pulling
* likely you need to retry failed api calls, but add guardrails to control the delay time
  *  `tenacity` package
        ```python
        from tenacity import retry
        @retry(stop=stop_after_attempt(3), wait=wait_exponential()) # it waits 2^x * 1 second between each retry
        def perform_api_call():
            ...
        ```
  *  `urllib3.util.Retry` with `requests` - https://docs.python-requests.org/en/latest/user/advanced/#example-automatic-retries
        ```python
        from urllib3.util import Retry
        from requests import Session
        from requests.adapters import HTTPAdapter

        session = Session()
        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504], # 5xx are server side errors; eg: 504 - timeout
            allowed_methods={'POST'},
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        ```





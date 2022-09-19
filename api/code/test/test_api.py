import requests

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': '*/*'
}

def call_api(date, region: str=None, box: str=None):
    if region and box:
        endpoint = f'http://localhost:5000/v1/weekly_avg_trips?date={date}&region={region}&box={box}'
    elif region:
        endpoint = f'http://localhost:5000/v1/weekly_avg_trips?date={date}&region={region}'
    elif box:
        endpoint = f'http://localhost:5000/v1/weekly_avg_trips?date={date}&box={box}'
    else:
        endpoint = f'http://localhost:5000/v1/weekly_avg_trips?date={date}'
    print(endpoint)
    response = requests.get(endpoint, headers=HEADERS)
    print(response.status_code)
    print(response.reason)
    if response.status_code == 200:
        return response.json()
    else:
        return None

print(call_api(date='2018-05-28'))
print(call_api(date='2018-05-28', region='Hamburg'))
print(call_api(date='2018-05-28', box='(-100 -100,-100 100,100 100,100 -100,-100 -100)'))
print(call_api(date='2018-05-28', region='Hamburg', box='(-100 -100,-100 100,100 100,100 -100,-100 -100)'))
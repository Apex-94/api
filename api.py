import requests
import json
from datetime import datetime
times = []
parameters = {
    "lat":40.71,
    "lon":-74
}
response2=requests.get("http://api.open-notify.org/iss-pass.json",parameters)
response = requests.get("http://api.open-notify.org/astros.json")
pass_times = response2.json()['response']

print(response.status_code)
# print(response.json())


def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

risetimes=[]

for d in pass_times:
    time=d['risetime']
    risetimes.append(time)

for rt in risetimes:
    time=datetime.fromtimestamp(rt)
    times.append(time)
    print(time)

print(risetimes)
# jprint(response.json())
#
# jprint(response2.json())

#jprint(pass_times)


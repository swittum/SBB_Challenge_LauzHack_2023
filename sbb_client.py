import requests
import json
import numpy as np
import isodate
import matplotlib.pyplot as plt

def duration_to_minutes(duration_str):
    duration_obj = isodate.parse_duration(duration_str)
    duration_in_minutes = duration_obj.total_seconds()/60
    return duration_in_minutes

API_URL = "https://journey-service-int.api.sbb.ch"
CLIENT_SECRET = "MU48Q~IuD6Iawz3QfvkmMiKHtfXBf-ffKoKTJdt5"
CLIENT_ID = "f132a280-1571-4137-86d7-201641098ce8"
SCOPE = "c11fa6b1-edab-4554-a43d-8ab71b016325/.default"

def get_token():
    params = {
        'grant_type': 'client_credentials',
        'scope': SCOPE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    return requests.post('https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token',
                         data=params).json()

def get_journey(origin, destination):
    auth = get_token()['access_token']
    headers = {
        'Authorization': f"Bearer {auth}",
        'Content-Type': 'application/json'
    }

    json_data =  {
        "origin": f"{str(origin)}",
        "destination": f"{str(destination)}",
        "date": "2023-04-18",   
        "time": "13:07",  
        "mobilityFilter":
            {
                "walkSpeed": 50
            },   
        "includeAccessibility": "ALL", 
        }

    out = requests.post('https://journey-service-int.api.sbb.ch/v3/trips/by-origin-destination',
                        headers=headers, json=json_data).json()
    trips = out['trips']
    durations = [0]*len(trips)
    routes = []
    for i, trip in enumerate(trips):
        routes.append([])
        legs = trip['legs']
        for leg in legs:
            if 'start' in leg:
                starttime = leg['start']['timeAimed']
                # print(starttime)
            if 'serviceJourney' in leg:
                elements = leg['serviceJourney']['stopPoints']
                for el in elements:
                    coords = el['place']['centroid']['coordinates']
                    routes[i].append(coords)
            duration = duration_to_minutes(leg['duration'])
            durations[i] += duration

    durations = np.array(durations)
    indices = np.argsort(durations)
    durations = durations[indices]
    routes = [routes[i] for i in indices]
    out['trips'] = [out['trips'][i] for i in indices]
    return durations, routes, out

origin = [8.38520, 47.08442]
destination = [8.58150, 47.39696]

coords_geneva = [6.13566, 46.30221]
coords_biel = [7.24317, 47.14001]
coords_SG = [9.43092, 47.45227]

if __name__ == '__main__':
    
    durations, routes, out = get_journey(coords_geneva, coords_biel)

    with open('output.json', 'w') as file:
        json.dump(out, file, indent=4)

    plt.figure()
    for (duration, route) in zip(durations, routes):
        route = np.array(route)
        plt.plot(route[:, 0], route[:, 1], label=f"{duration:.0f} min", ls='--', marker='o', markersize=3)
    plt.legend()
    plt.savefig('test.png')

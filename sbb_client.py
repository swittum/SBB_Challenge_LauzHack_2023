import requests
import json
import isodate
import dotenv
import numpy as np


def timestring_to_minutes(duration_str):
    """
    Takes time string of format 'PT#1H#2M' and converts it to
    minutes with datatype float
    """
    duration_float_seconds = isodate.parse_duration(duration_str)
    duration_float_minutes = duration_float_seconds.total_seconds()/60
    return duration_float_minutes


# API_URL = "https://journey-service-int.api.sbb.ch"
# CLIENT_SECRET = "MU48Q~IuD6Iawz3QfvkmMiKHtfXBf-ffKoKTJdt5"
# CLIENT_ID = "f132a280-1571-4137-86d7-201641098ce8"
# SCOPE = "c11fa6b1-edab-4554-a43d-8ab71b016325/.default"
API_URL = dotenv.get_key('.env', 'API_URL')
CLIENT_SECRET = dotenv.get_key('.env', 'CLIENT_SECRET')
CLIENT_ID = dotenv.get_key('.env', 'CLIENT_ID')
SCOPE = dotenv.get_key('.env', 'SCOPE')


def get_sbb_token():
    """
    Creates a token for the SBB API
    """
    params = {
        'grant_type': 'client_credentials',
        'scope': SCOPE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    return requests.post('https://login.microsoftonline.com/2cda5d11-f0ac-46b3-967d-af1b2e1bd01a/oauth2/v2.0/token',
                         data=params).json()


def get_sbb_journey(origin, destination):
    """
    Takes coordinates of origin and destination and returns durations, routes
    and verbose sbb_output sorted by duration
    """
    auth = get_sbb_token()['access_token']
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

    sbb_output = requests.post('https://journey-service-int.api.sbb.ch/v3/trips/by-origin-destination',
                        headers=headers, json=json_data).json()
    trips = sbb_output['trips']
    durations_sorted = [0]*len(trips)
    routes_sorted = []
    for i, trip in enumerate(trips):
        routes_sorted.append([])
        legs = trip['legs']
        for leg in legs:
            # if 'start' in leg:
            #     starttime = leg['start']['timeAimed']
            if 'serviceJourney' in leg:
                stoppoints = leg['serviceJourney']['stopPoints']
                for stoppoint in stoppoints:
                    stoppoint_coordinates = stoppoint['place']['centroid']['coordinates']
                    routes_sorted[i].append(stoppoint_coordinates)
            duration = timestring_to_minutes(leg['duration'])
            durations_sorted[i] += duration

    durations_sorted = np.array(durations_sorted)
    indices = np.argsort(durations_sorted)
    durations_sorted = durations_sorted[indices]
    routes_sorted = [routes_sorted[i] for i in indices]
    sbb_output['trips'] = [sbb_output['trips'][i] for i in indices]
    return durations_sorted, routes_sorted, sbb_output


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from coordinates import COORDINATES_SG, COORDINATES_GENEVA
    durations, routes, sbb_output = get_sbb_journey(COORDINATES_SG, COORDINATES_GENEVA)
    with open('output.json', 'w') as file:
        json.dump(sbb_output, file, indent=4)
    plt.figure()
    for (duration, route) in zip(durations, routes):
        route = np.array(route)
        plt.plot(route[:, 0], route[:, 1], label=f"{duration:.0f} min", ls='--', marker='o', markersize=3)
    plt.legend()
    plt.savefig('sbb_routes.png')

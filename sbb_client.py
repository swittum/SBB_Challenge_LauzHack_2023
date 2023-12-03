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


def get_sbb_journey(origin, destination, time='13:07'):
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
        "time": time,  
        "mobilityFilter":
            {
                "walkSpeed": 50
            },   
        "includeAccessibility": "ALL", 
        }

    sbb_output = requests.post('https://journey-service-int.api.sbb.ch/v3/trips/by-origin-destination',
                        headers=headers, json=json_data).json()

    try: 
        trips = sbb_output['trips']
    except:
        raise ValueError('No trips found')

    output_data = []
    for i, trip in enumerate(trips):
        output_data.append({})
        # Data to be put into dictionary
        route = []
        changing_points = []
        changing_times = []
        modes = []
        total_duration = 0
        legs = trip['legs']
        
        for leg in legs:
            mode = leg['mode']
            modes.append(mode)
            if mode == 'FOOT':
                if leg['end']['place']['type'] != 'Address':
                    changing_points.append(leg['end']['place']['name'])
                    changing_times.append(leg['end']['timeAimed'])
            else:
                stoppoints = leg['serviceJourney']['stopPoints']
                n = len(stoppoints)
                for stoppoint in stoppoints:
                    stoppoint_coordinates = stoppoint['place']['centroid']['coordinates']
                    route.append(stoppoint_coordinates)
                changing_points.append(stoppoint['place']['name'])
                changing_times.append(stoppoint['arrival']['timeAimed'])
            duration = timestring_to_minutes(leg['duration'])
            total_duration += duration
        output_data[i]['route'] = np.array(route)
        output_data[i]['changing_points'] = changing_points
        output_data[i]['changing_times'] = changing_times
        output_data[i]['modes'] = modes
        output_data[i]['duration'] = total_duration
        
    durations = [output_data[i]['duration'] for i in range(len(output_data))]
    indices = np.argsort(durations)
    output_data_sorted = [output_data[i] for i in indices]
    sbb_output['trips'] = [sbb_output['trips'][i] for i in indices]
    return output_data, sbb_output


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from coordinates import COORDINATES_BERN, COORDINATES_BASEL
    output_data, sbb_output = get_sbb_journey(COORDINATES_BERN, COORDINATES_BASEL)
    with open('output.json', 'w') as file:
        json.dump(sbb_output, file, indent=4)
    durations = [output_data[i]['duration'] for i in range(len(output_data))]
    routes = [output_data[i]['route'] for i in range(len(output_data))]
    plt.figure()
    for (duration, route) in zip(durations, routes):
        plt.plot(route[:, 0], route[:, 1], label=f"{duration:.0f} min", ls='--', marker='o', markersize=3)
    plt.legend()
    plt.savefig('sbb_routes.png')
import json
import openrouteservice as ors
import requests
import dotenv
import matplotlib.pyplot as plt
import numpy as np

api_key = dotenv.get_key('.env', 'api_key')
client = ors.Client(key=api_key)

def get_driving_time(origin, destination):
    coordinates = [origin, destination]
    route = client.directions(
        coordinates=coordinates,
        profile='driving-car',
        format='geojson',
        validate=False,
    )
    duration = route['features'][0]['properties']['segments'][0]['duration']
    coordinates = np.array(route['features'][0]['geometry']['coordinates'])
    return duration/60, coordinates

if __name__ == '__main__':
    # origin = [6.16765465, 46.29848883]
    # destination = [6.16765465, 46.29848883]

    origin = [6.13566, 46.30221]
    destination = [6.16765465, 46.29848883]

    duration, coordinates = get_driving_time([8.38520, 47.08442], [8.58150, 47.39696])
    plt.plot(coordinates[:, 0], coordinates[:, 1])
    plt.savefig('test.png')

    print(duration)




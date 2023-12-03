import json
import requests
import dotenv
import numpy as np
import openrouteservice as ors


api_key = dotenv.get_key('.env', 'api_key')
client = ors.Client(key=api_key)


def get_driving_time(origin, destination):
    """
    Takes origin and destination, returns travel time by car in minutes
    and coordinates of the route (as suggested by openrouteservice)
    """
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
    import matplotlib.pyplot as plt
    from coordinates import COORDINATES_SG, COORDINATES_GENEVA, COORDINATES_BIEL

    duration, coordinates = get_driving_time(COORDINATES_BIEL, COORDINATES_GENEVA)
    plt.plot(coordinates[:, 0], coordinates[:, 1])
    plt.savefig('car_route.png')
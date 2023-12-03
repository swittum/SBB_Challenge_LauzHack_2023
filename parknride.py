import os
from math import radians, sin, cos, sqrt, atan2 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Reading mobility data
path = os.path.join(os.path.dirname(__file__), 'data', 'mobilitat.csv')
data = pd.read_csv(path, sep=';')


# Extracting long- and latitudes
geopositions = data['Geopos']
longitudes, latitudes = [], []
for geoposition in geopositions:
    latitude_closest, longitude_closest = geoposition.split(',')
    longitudes.append(float(longitude_closest))
    latitudes.append(float(latitude_closest))
longitudes = np.array(longitudes)
latitudes = np.array(latitudes)


def calculate_distance(long1, lat1, long2, lat2):
    """
    Takes long- and latitudes of two points on the globe and
    calculates the distance between them in km
    """
    long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])
    # Haversine formula
    dlon = long2-long1
    dlat = lat2-lat1
    a = sin(dlat/2)**2+cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    distance = 6371*c
    return distance


def get_closest_pnr(longitude_start, latitude_start):
    """
    Takes long- and latitudes of a starting point and returns index position
    of P&R with correspoding distances and coordinates sorted by distance
    to the starting point
    """
    distances_sorted = []
    for (longitude_pnr, latitude_pnr) in zip(longitudes, latitudes):
        distances_sorted.append(calculate_distance(longitude_pnr, latitude_pnr, longitude_start, latitude_start))
    distances_sorted = np.array(distances_sorted)
    closest_pnr_index = np.argsort(distances_sorted)
    distances_sorted = distances_sorted[closest_pnr_index]
    longitudes_sorted = longitudes[closest_pnr_index]
    latitudes_sorted = latitudes[closest_pnr_index]
    coordinates_sorted = [longitudes_sorted, latitudes_sorted]
    return closest_pnr_index, distances_sorted, coordinates_sorted


if __name__ == '__main__':

    longitude = 9.75996
    latitude = 47.10115
   
    indices, distances, coordinates = get_closest_pnr(latitude, longitude)
    longitude_closest = longitudes[indices[0]]
    latitude_closest = latitudes[indices[0]]

    
    plt.scatter(longitudes, latitudes)
    plt.scatter(longitude, latitude, c='r')
    plt.scatter(longitude_closest, latitude_closest, c='b', marker='x')
    plt.savefig('PNR_positions.png', dpi=300)
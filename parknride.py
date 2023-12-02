from math import radians, sin, cos, sqrt, atan2 
import pandas as pd
import numpy as np

path = '/Users/simonwittum/Documents/Arbeit/LauzHack/SBB/data/mobilitat.csv'

data = pd.read_csv(path, sep=';')

import matplotlib.pyplot as plt
tmp = data['Geopos']
long, lat = [], []
for el in tmp:
    c1, c2 = el.split(',')
    long.append(float(c2))
    lat.append(float(c1))
long = np.array(long)
lat = np.array(lat)

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2-lon1
    dlat = lat2-lat1
    a = sin(dlat/2)**2+cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    distance = 6371*c

    return distance

def get_closest_station(lat_person, long_person):
    distances = []
    for (lat_stat, lon_stat) in zip(lat, long):
        distances.append(calculate_distance(lat_stat, lon_stat, lat_person, long_person))

    distances = np.array(distances)
    indices = np.argsort(distances)
    distances = distances[indices]
    lat_out = lat[indices]
    long_out = long[indices]
    coords = [lat_out, long_out]
    
    return indices, distances, coords


if __name__ == '__main__':

    # lat_ = 47.3769
    # long_ = 8.5417

    lat_ = 47.10115
    long_ = 9.75996

    indices, distances, coords = get_closest_station(lat_, long_)
    c1 = lat[indices[0]]
    c2 = long[indices[0]]

    plt.scatter(long, lat)
    plt.scatter(long_, lat_, c='r')
    plt.scatter(c2, c1, c='b', marker='x')
    plt.savefig('test.png', dpi=300)

    # distances = get_closest_station(lat_, long_)
    # indices = np.argsort(distances)
    # distances = distances[indices]
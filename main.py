import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from parknride import get_closest_station
from sbb_client import get_journey
from sbb_client import coords_geneva, coords_biel, coords_SG
from cartravel import get_driving_time

indices, distances, coords = get_closest_station(coords_geneva[1], coords_geneva[0])
ycoord, xcoord = coords
startpoint = [xcoord[0], ycoord[0]]

durations, routes, out = get_journey(startpoint, coords_biel)
duration, coords = get_driving_time(startpoint, coords_biel)

plt.scatter(xcoord, ycoord)
for (route, duration) in zip(routes, durations):
    route = np.array(route)
    plt.plot(route[:, 0], route[:, 1], label=f"{duration:.0f} min", ls='--', marker='o', markersize=3)
plt.plot(coords[:, 0], coords[:, 1], label=f"Car, duration={duration:.0f}", c='r')
plt.legend()
plt.savefig('journey.png', dpi=300)
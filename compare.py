import numpy as np
import matplotlib.pyplot as plt

from parknride import get_closest_station
from sbb_client import get_journey
from cartravel import get_driving_time

# Get data
from sbb_client import coords_geneva, coords_biel, coords_SG

def compare(origin, destination):
    # Method 1: SBB from origin to destination

    durations, routes, out = get_journey(origin, destination)

    # Pick only the fastest route
    duration = durations[0]
    route = np.array(routes[0])
    print(f"Duration: {duration:.0f} min")

    # Method 2: Car from origin to destination
    duration_car, coords_car = get_driving_time(origin, destination)
    print(f"Duration: {duration_car:.0f} min")

    # Method 3: Car to P&R, then SBB to destination
    indices, distances, coords = get_closest_station(origin[1], origin[0])
    coords = np.array(coords)

    # Pick only the clostest P&R
    coords = coords[:, 0]
    coords = coords[::-1]

    origin = origin
    coords = coords.tolist()
    duration_pr, coords_pr = get_driving_time(origin, coords)

    durations, routes, out = get_journey(coords, destination)
    duration_ = duration_pr + durations[0]
    route_ = np.array(routes[0])

    return [route, duration], [coords_car, duration_car], [coords_pr, route_, duration_]


if __name__ == '__main__':
    # coords_random = [9.75996, 47.10115]
    sbb, car, mix = compare(coords_geneva, coords_biel)
    route_sbb, duration_sbb = sbb[0], sbb[1]
    route_car, duration_car = car[0], car[1]
    route_mix1, route_mix2, duration_mix = mix[0], mix[1], mix[2]

    plt.plot(route_sbb[:, 0], route_sbb[:, 1], label=f"sbb: {duration_sbb:.0f}")
    plt.plot(route_car[:, 0], route_car[:, 1], label=f"car: {duration_car:.0f}")
    plt.plot(route_mix1[:, 0], route_mix1[:, 1], label=f"car: {duration_mix:.0f}", c="r", ls='--')
    plt.plot(route_mix2[:, 0], route_mix2[:, 1], c="r")
    plt.legend()
    plt.savefig('test.png', dpi=300)





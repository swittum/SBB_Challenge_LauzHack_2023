import numpy as np
from parknride import get_closest_pnr
from sbb_client import get_sbb_journey
from cartravel import get_driving_time


def compare_connections(origin, destination):
    """
    Takes coordinates of origin and destination and returns durations and routes
    for three methods: SBB from door to door, car from door to door and car to
    P&R, then SBB to destination
    """
    # Method 1: SBB from origin to destination
    durations_sbb_combi, routes_sbb_combi, sbb_output_combi = get_sbb_journey(origin, destination)
    # Pick only the fastest route
    duration_sbb = durations_sbb_combi[0]
    route_sbb = np.array(routes_sbb_combi[0])
    print(f"Duration SBB: {duration_sbb:.0f} min")

    # Method 2: Car from origin to destination
    duration_car, routes_car = get_driving_time(origin, destination)
    print(f"Duration car: {duration_car:.0f} min")

    # Method 3: Car to P&R, then SBB to destination
    indices_pnr, distances_pnr, coordinates_pnr = get_closest_pnr(*origin)
    coordinates_pnr = np.array(coordinates_pnr)

    # Pick only the clostest P&R
    duration_final_combi = 1e10
    route_final_combi = None

    for i in range(5):
        coordinates_pnr_close = coordinates_pnr[:, i]
        coordinates_pnr_close = coordinates_pnr_close.tolist()
        duration_pnr, route_to_pnr = get_driving_time(origin, coordinates_pnr_close)
        durations_sbb_combi, routes_sbb_combi, sbb_output_combi = get_sbb_journey(coordinates_pnr_close, destination)
        duration_total = duration_pnr + durations_sbb_combi[0]
        if duration_total < duration_final_combi:
            duration_final_combi = duration_total
            route_final_combi = np.array(routes_sbb_combi[0])

    print(f"Duration PNR: {duration_final_combi:.0f} min")
    return [route_sbb, duration_sbb], [routes_car, duration_car], [route_to_pnr, route_final_combi, duration_total]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from coordinates import COORDINATES_SG, COORDINATES_GENEVA, COORDINATES_BIEL

    sbb, car, mix = compare_connections(COORDINATES_GENEVA, COORDINATES_SG)
    route_sbb, duration_sbb = sbb[0], sbb[1]
    route_car, duration_car = car[0], car[1]
    route_mix1, route_mix2, duration_mix = mix[0], mix[1], mix[2]

    plt.plot(route_sbb[:, 0], route_sbb[:, 1], label=f"sbb: {duration_sbb:.0f}")
    plt.plot(route_car[:, 0], route_car[:, 1], label=f"car: {duration_car:.0f}")
    plt.plot(route_mix1[:, 0], route_mix1[:, 1], label=f"car: {duration_mix:.0f}", c="r", ls='--')
    plt.plot(route_mix2[:, 0], route_mix2[:, 1], c="r")
    plt.legend()
    plt.savefig('comparison.png', dpi=300)
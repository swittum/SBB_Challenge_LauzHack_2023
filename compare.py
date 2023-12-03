import numpy as np
from parknride import get_closest_pnr
from sbb_client import get_sbb_journey
from cartravel import get_driving_time


def compare_connections(origin, destination, time='13:07'):
    """
    Takes coordinates of origin and destination and returns durations and routes
    for three methods: SBB from door to door, car from door to door and car to
    P&R, then SBB to destination
    """
    # Method 1: SBB from origin to destination
    data_sbb, sbb_output_combi = get_sbb_journey(origin, destination, time)
    data_sbb_fastest = data_sbb[0]

    # Method 2: Car from origin to destination
    duration_car, route_car = get_driving_time(origin, destination)

    # Method 3: Car to P&R, then SBB to destination
    indices_pnr, distances_pnr, coordinates_pnr = get_closest_pnr(*origin)
    coordinates_pnr = np.array(coordinates_pnr)

    # Initializing params
    duration_final_combi = 1e10
    data_combi_fastest = None

    for i in range(5):
        coordinates_pnr_close = coordinates_pnr[:, i]
        coordinates_pnr_close = coordinates_pnr_close.tolist()
        duration_pnr, route_to_pnr = get_driving_time(origin, coordinates_pnr_close)
        data_sbb_combi, sbb_output_combi = get_sbb_journey(coordinates_pnr_close, destination, time)
        data_sbb_combi_fastest = data_sbb_combi[0]
        duration_total = duration_pnr + data_sbb_combi_fastest['duration']
        if duration_total < duration_final_combi:
            duration_final_combi = duration_total
            # route_final_combi = data_sbb_combi_fastest['route']
            data_combi_fastest = data_sbb_combi_fastest
            data_combi_fastest['duration_car'] = duration_pnr
            data_combi_fastest['route_car'] = route_to_pnr
            data_combi_fastest['duration_total'] = duration_total

    return data_sbb_fastest, [route_car, duration_car], data_combi_fastest


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from coordinates import COORDINATES_SG, COORDINATES_GENEVA, COORDINATES_BIEL

    data_sbb, data_car, data_combi = compare_connections(COORDINATES_GENEVA, COORDINATES_SG)
    route_sbb = data_sbb['route']
    duration_sbb = data_sbb['duration']
    route_car = data_car[0]
    duration_car = data_car[1]
    route_combi_car = data_combi['route_car']
    route_combi_sbb = data_combi['route']
    duration_combi = data_combi['duration_total']

    plt.plot(route_sbb[:, 0], route_sbb[:, 1], label=f"SBB: {duration_sbb:.0f}")
    plt.plot(route_car[:, 0], route_car[:, 1], label=f"Car: {duration_car:.0f}")
    plt.plot(route_combi_car[:, 0], route_combi_car[:, 1], label=f"Mix: {duration_combi:.0f}", c="r", ls='--')
    plt.plot(route_combi_sbb[:, 0], route_combi_sbb[:, 1], c="r")
    plt.legend()
    plt.savefig('comparison.png', dpi=300)
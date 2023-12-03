import matplotlib.pyplot as plt
from compare import compare_connections
from coordinates import COORDINATES_SG, COORDINATES_BIEL, COORDINATES_GENEVA


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




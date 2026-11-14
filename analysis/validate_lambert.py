
import numpy as np
from scipy.integrate import solve_ivp

from transfer_analysis import (
    load_vectors,
    lambert_universal,
    MU_SUN,
    AU_DAY_TO_KM_S
)

EARTH_FILE = "data_raw/solar_system/earth/earth_vectors.csv"
MARS_FILE = "data_raw/solar_system/mars/mars_vectors.csv"

KM_PER_AU = 149597870.7


def solar_gravity(t, state):
    r = state[:3]
    v = state[3:]

    distance = np.linalg.norm(r)
    acceleration = -MU_SUN * r / distance**3

    return np.concatenate((v, acceleration))


def validate_case(earth, mars, label):
    dt = mars["jd"] - earth["jd"]

    solution = lambert_universal(
        earth["r"],
        mars["r"],
        dt,
        MU_SUN
    )

    print("\n==========", label, "==========")

    if solution is None:
        print("Lambert solver returned no solution.")
        return

    v_departure, v_arrival_lambert = solution

    initial_state = np.concatenate((
        earth["r"],
        v_departure
    ))

    result = solve_ivp(
        solar_gravity,
        (0, dt),
        initial_state,
        method="DOP853",
        rtol=1e-11,
        atol=1e-13
    )

    if not result.success:
        print("Integration failed:", result.message)
        return

    final_state = result.y[:, -1]

    propagated_position = final_state[:3]
    propagated_velocity = final_state[3:]

    position_error_au = np.linalg.norm(
        propagated_position - mars["r"]
    )

    position_error_km = position_error_au * KM_PER_AU

    velocity_error_km_s = np.linalg.norm(
        propagated_velocity - v_arrival_lambert
    ) * AU_DAY_TO_KM_S

    print("Transfer duration:", dt, "days")
    print("Integration successful:", result.success)
    print("Mars position error:", position_error_km, "km")
    print("Arrival velocity error:", velocity_error_km_s, "km/s")


if __name__ == "__main__":
    earth_data = load_vectors(EARTH_FILE)
    mars_data = load_vectors(MARS_FILE)

    earth = earth_data[0]

    candidate_arrivals = [
        "A.D. 2029-Jul-22 00:00:00.0000",
        "A.D. 2029-Aug-31 00:00:00.0000"
    ]

    for arrival_date in candidate_arrivals:
        mars = next(
            item for item in mars_data
            if item["date"] == arrival_date
        )

        validate_case(
            earth,
            mars,
            arrival_date
        )

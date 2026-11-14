
import numpy as np

from transfer_analysis import (
    load_vectors,
    lambert_universal,
    MU_SUN,
    AU_DAY_TO_KM_S
)

EARTH_FILE = "data_raw/solar_system/earth/earth_vectors.csv"
MARS_FILE = "data_raw/solar_system/mars/mars_vectors.csv"


def diagnose(earth, mars):

    dt = mars["jd"] - earth["jd"]

    result = lambert_universal(
        earth["r"],
        mars["r"],
        dt,
        MU_SUN
    )

    print("\n" + "=" * 60)
    print("TRANSFER DIAGNOSTIC")
    print("=" * 60)

    if result is None:
        print("No Lambert solution.")
        return

    v1, v2 = result

    r1 = earth["r"]
    r2 = mars["r"]

    h = np.cross(r1, v1)
    h_mag = np.linalg.norm(h)

    inclination = np.degrees(
        np.arccos(np.clip(h[2] / h_mag, -1, 1))
    )

    transfer_angle = np.degrees(
        np.arccos(
            np.clip(
                np.dot(r1, r2) /
                (np.linalg.norm(r1) * np.linalg.norm(r2)),
                -1, 1
            )
        )
    )

    print("Departure:", earth["date"])
    print("Arrival:", mars["date"])
    print("Duration:", dt, "days")

    print("\n--- Position Vectors (AU) ---")
    print("Earth position:", r1)
    print("Mars position:", r2)

    print("\n--- Velocity Vectors (AU/day) ---")
    print("Earth velocity:", earth["v"])
    print("Mars velocity:", mars["v"])
    print("Spacecraft departure velocity:", v1)
    print("Spacecraft arrival velocity:", v2)

    print("\n--- Departure Velocity (km/s) ---")
    print(v1 * AU_DAY_TO_KM_S)

    print("\n--- Angular Momentum Vector ---")
    print(h)

    print("\n--- Geometry ---")
    print("Transfer angle:", transfer_angle, "degrees")
    print("Inclination:", inclination, "degrees")
    print("Angular momentum magnitude:", h_mag)

    print("\n--- Z Components ---")
    print("Earth position Z:", r1[2])
    print("Mars position Z:", r2[2])
    print("Spacecraft departure velocity Z:", v1[2])


if __name__ == "__main__":

    earth_data = load_vectors(EARTH_FILE)
    mars_data = load_vectors(MARS_FILE)

    earth = earth_data[0]

    dates = [
        "A.D. 2029-Jul-22 00:00:00.0000",
        "A.D. 2029-Aug-31 00:00:00.0000"
    ]

    for date in dates:

        mars = next(
            item for item in mars_data
            if item["date"] == date
        )

        diagnose(earth, mars)

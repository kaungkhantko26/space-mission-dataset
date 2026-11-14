
import numpy as np

from transfer_analysis import (
    load_vectors,
    lambert_universal,
    MU_SUN,
    AU_DAY_TO_KM_S
)

EARTH_FILE = "data_raw/solar_system/earth/earth_vectors.csv"
MARS_FILE = "data_raw/solar_system/mars/mars_vectors.csv"

AU_KM = 149597870.7


def analyze_orbit(earth, mars, label):

    dt = mars["jd"] - earth["jd"]

    result = lambert_universal(
        earth["r"],
        mars["r"],
        dt,
        MU_SUN
    )

    print("\n" + "=" * 55)
    print(label)
    print("=" * 55)

    if result is None:
        print("No Lambert solution.")
        return

    r = earth["r"]
    v = result[0]

    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)

    # Specific orbital energy
    energy = (v_mag ** 2 / 2) - MU_SUN / r_mag

    # Specific angular momentum
    h = np.cross(r, v)
    h_mag = np.linalg.norm(h)

    # Eccentricity vector
    e_vector = np.cross(v, h) / MU_SUN - r / r_mag
    eccentricity = np.linalg.norm(e_vector)

    # Inclination relative to ecliptic plane
    inclination = np.degrees(
        np.arccos(np.clip(h[2] / h_mag, -1, 1))
    )

    # Semi-major axis
    if abs(energy) < 1e-15:
        semi_major_axis = float("inf")
    else:
        semi_major_axis = -MU_SUN / (2 * energy)

    # Perihelion and aphelion
    if eccentricity < 1:
        perihelion = semi_major_axis * (1 - eccentricity)
        aphelion = semi_major_axis * (1 + eccentricity)
    else:
        perihelion = semi_major_axis * (1 - eccentricity)
        aphelion = None

    # Arrival velocity
    arrival_v = result[1]

    departure_vinf = np.linalg.norm(
        v - earth["v"]
    ) * AU_DAY_TO_KM_S

    arrival_vinf = np.linalg.norm(
        arrival_v - mars["v"]
    ) * AU_DAY_TO_KM_S

    c3 = departure_vinf ** 2

    print(f"Departure: {earth['date']}")
    print(f"Arrival:   {mars['date']}")
    print(f"Duration:  {dt:.1f} days")

    print("\n--- Orbit Geometry ---")

    print(f"Specific energy: {energy:.10f} AU^2/day^2")
    print(f"Semi-major axis: {semi_major_axis:.6f} AU")
    print(f"Eccentricity:    {eccentricity:.6f}")
    print(f"Inclination:     {inclination:.6f} degrees")

    print(f"Perihelion:      {perihelion:.6f} AU")

    if aphelion is not None:
        print(f"Aphelion:        {aphelion:.6f} AU")
    else:
        print("Aphelion:        Unbounded")

    print("\n--- Mission Parameters ---")
    print(f"Departure C3:    {c3:.6f} km^2/s^2")
    print(f"Departure v_inf: {departure_vinf:.6f} km/s")
    print(f"Arrival v_inf:   {arrival_vinf:.6f} km/s")

    print("\n--- Direction ---")

    if energy < 0:
        print("Orbit type: Elliptical")
    elif energy > 0:
        print("Orbit type: Hyperbolic")
    else:
        print("Orbit type: Parabolic")

    if h[2] > 0:
        print("Direction: Prograde")
    else:
        print("Direction: Retrograde")


if __name__ == "__main__":

    earth_data = load_vectors(EARTH_FILE)
    mars_data = load_vectors(MARS_FILE)

    earth = earth_data[0]

    arrival_dates = [
        "A.D. 2029-Jul-22 00:00:00.0000",
        "A.D. 2029-Aug-31 00:00:00.0000"
    ]

    for date in arrival_dates:

        mars = next(
            item for item in mars_data
            if item["date"] == date
        )

        analyze_orbit(
            earth,
            mars,
            "EARTH TO MARS TRANSFER"
        )

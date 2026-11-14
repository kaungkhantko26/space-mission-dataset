
import csv
import math
from pathlib import Path

import numpy as np

# ==========================================
# 1. CONFIGURATION
# ==========================================

EARTH_FILE = Path("data_raw/solar_system/earth/earth_vectors.csv")
MARS_FILE = Path("data_raw/solar_system/mars/mars_vectors.csv")

OUTPUT_DIR = Path("analysis")
OUTPUT_FILE = OUTPUT_DIR / "transfer_results.csv"

# Sun gravitational parameter (AU^3 / day^2)
MU_SUN = 0.0002959122082855911

# AU/day to km/s
AU_DAY_TO_KM_S = 149597870.7 / 86400.0

MIN_TRANSFER_DAYS = 100
MAX_TRANSFER_DAYS = 450


# ==========================================
# 2. LOAD HORIZONS CSV DATA
# ==========================================

def load_vectors(file_path):
    records = []

    with open(file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            position = np.array([
                float(row["X_AU"]),
                float(row["Y_AU"]),
                float(row["Z_AU"])
            ])

            velocity = np.array([
                float(row["VX_AU_per_day"]),
                float(row["VY_AU_per_day"]),
                float(row["VZ_AU_per_day"])
            ])

            records.append({
                "date": row["Calendar_Date_TDB"],
                "jd": float(row["JD_TDB"]),
                "r": position,
                "v": velocity
            })

    return records


# ==========================================
# 3. STUMPFF FUNCTIONS
# ==========================================

def stumpff_c(z):
    if z > 1e-8:
        return (1 - math.cos(math.sqrt(z))) / z
    elif z < -1e-8:
        return (math.cosh(math.sqrt(-z)) - 1) / (-z)
    return 0.5


def stumpff_s(z):
    if z > 1e-8:
        root = math.sqrt(z)
        return (root - math.sin(root)) / (root ** 3)
    elif z < -1e-8:
        root = math.sqrt(-z)
        return (math.sinh(root) - root) / (root ** 3)
    return 1.0 / 6.0


# ==========================================
# 4. LAMBERT SOLVER
# ==========================================

def lambert_universal(r1, r2, dt, mu):
    r1_mag = np.linalg.norm(r1)
    r2_mag = np.linalg.norm(r2)

    cos_theta = np.dot(r1, r2) / (r1_mag * r2_mag)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    theta = math.acos(cos_theta)

    cross_z = np.cross(r1, r2)[2]

    # Prograde transfer
    if cross_z < 0:
        theta = 2 * math.pi - theta

    denominator = 1 - math.cos(theta)

    if denominator < 1e-12:
        return None

    A = math.sin(theta) * math.sqrt(
        r1_mag * r2_mag / denominator
    )

    if abs(A) < 1e-12:
        return None

    def calculate_time(z):
        C = stumpff_c(z)
        S = stumpff_s(z)

        if C <= 0:
            return None

        y = r1_mag + r2_mag + A * (
            z * S - 1
        ) / math.sqrt(C)

        if y < 0:
            return None

        x = math.sqrt(y / C)

        return (
            (x ** 3) * S + A * math.sqrt(y)
        ) / math.sqrt(mu)

    # Find a valid bracket for bisection
    z_values = np.linspace(-50, 4 * math.pi ** 2 - 1e-5, 300)

    bracket = None

    for i in range(len(z_values) - 1):
        z1 = z_values[i]
        z2 = z_values[i + 1]

        t1 = calculate_time(z1)
        t2 = calculate_time(z2)

        if t1 is None or t2 is None:
            continue

        if (t1 - dt) * (t2 - dt) <= 0:
            bracket = (z1, z2)
            break

    if bracket is None:
        return None

    low, high = bracket

    for _ in range(100):
        mid = (low + high) / 2
        t_mid = calculate_time(mid)

        if t_mid is None:
            low = mid
            continue

        if abs(t_mid - dt) < 1e-8:
            break

        t_low = calculate_time(low)

        if t_low is None:
            low = mid
            continue

        if (t_low - dt) * (t_mid - dt) <= 0:
            high = mid
        else:
            low = mid

    z = (low + high) / 2

    C = stumpff_c(z)
    S = stumpff_s(z)

    y = r1_mag + r2_mag + A * (
        z * S - 1
    ) / math.sqrt(C)

    f = 1 - y / r1_mag
    g = A * math.sqrt(y / mu)
    g_dot = 1 - y / r2_mag

    if abs(g) < 1e-12:
        return None

    v1 = (r2 - f * r1) / g
    v2 = (g_dot * r2 - r1) / g

    return v1, v2


# ==========================================
# 5. TRANSFER ANALYSIS
# ==========================================

def analyze_transfers(earth_data, mars_data):
    results = []

    for earth in earth_data:
        for mars in mars_data:

            dt = mars["jd"] - earth["jd"]

            if not (
                MIN_TRANSFER_DAYS <= dt <= MAX_TRANSFER_DAYS
            ):
                continue

            solution = lambert_universal(
                earth["r"],
                mars["r"],
                dt,
                MU_SUN
            )

            if solution is None:
                continue

            v_departure, v_arrival = solution

            # Relative velocity to Earth and Mars
            v_inf_departure = (
                v_departure - earth["v"]
            )

            v_inf_arrival = (
                v_arrival - mars["v"]
            )

            departure_v_inf = (
                np.linalg.norm(v_inf_departure)
                * AU_DAY_TO_KM_S
            )

            arrival_v_inf = (
                np.linalg.norm(v_inf_arrival)
                * AU_DAY_TO_KM_S
            )

            c3 = departure_v_inf ** 2

            results.append({
                "departure_date": earth["date"],
                "arrival_date": mars["date"],
                "transfer_days": dt,
                "departure_c3_km2_s2": c3,
                "departure_vinf_km_s": departure_v_inf,
                "arrival_vinf_km_s": arrival_v_inf
            })

    return results


# ==========================================
# 6. SAVE RESULTS
# ==========================================

def save_results(results):
    if not results:
        print("No valid transfer solutions found.")
        return

    results.sort(
        key=lambda item: (
            item["departure_c3_km2_s2"],
            item["arrival_vinf_km_s"]
        )
    )

    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n========== TRANSFER ANALYSIS ==========")
    print("Valid solutions:", len(results))
    print("Results saved to:", OUTPUT_FILE)

    print("\nTop 10 candidates:")

    for i, item in enumerate(results[:10], start=1):
        print(f"\nCandidate {i}")
        print("Departure:", item["departure_date"])
        print("Arrival:", item["arrival_date"])
        print("Duration:", round(item["transfer_days"], 2), "days")
        print("Departure C3:", round(
            item["departure_c3_km2_s2"], 3
        ), "km^2/s^2")
        print("Departure v-infinity:", round(
            item["departure_vinf_km_s"], 3
        ), "km/s")
        print("Arrival v-infinity:", round(
            item["arrival_vinf_km_s"], 3
        ), "km/s")


# ==========================================
# 7. MAIN
# ==========================================

if __name__ == "__main__":

    print("Loading Earth and Mars ephemeris data...")

    earth_data = load_vectors(EARTH_FILE)
    mars_data = load_vectors(MARS_FILE)

    print("Earth records:", len(earth_data))
    print("Mars records:", len(mars_data))

    print("\nCalculating transfer trajectories...")

    results = analyze_transfers(
        earth_data,
        mars_data
    )

    save_results(results)

    print("\nAnalysis completed.")

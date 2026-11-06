"""pandas demo on the verified CSV exports (pip install pandas). Run `python3 tools/export_data.py` first if exports/ is missing.
    python3 examples/pandas_demo.py"""
import os, pandas as pd
CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", "csv")
planets = pd.read_csv(f"{CSV}/planets.csv")
print(planets[["id", "data_class", "gravitational_parameter_km3_s2", "mean_radius_m", "derived.escape_velocity_m_s"]].round(2).to_string(index=False))
nh = pd.read_csv(f"{CSV}/nhats_targets.csv")
print(f"\nNHATS targets: {len(nh)}; median min delta-v {nh.min_delta_v_km_s.median():.2f} km/s")
print(nh.sort_values("min_delta_v_km_s")[["designation", "min_delta_v_km_s", "min_delta_v_trip_days", "size_max_m", "H_mag"]].head(8).to_string(index=False))
neo = pd.read_csv(f"{CSV}/neo_catalog.csv")
print("\nNEOs with measured diameter by orbit class:")
print(neo.groupby("orbit_class").agg(n=("id", "count"), largest_km=("diameter_km", "max")).to_string())

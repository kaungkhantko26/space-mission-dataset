"""pandas demo on the CSV exports (pip install pandas). Run `python3 tools/export_data.py` first if exports/ is missing.
    python3 examples/pandas_demo.py"""
import os, pandas as pd
CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", "csv")
planets = pd.read_csv(f"{CSV}/planets.csv")
print(planets[["id", "data_class", "gravitational_parameter_km3_s2", "mean_radius_m", "derived.escape_velocity_m_s"]].round(2).to_string(index=False))
eng = pd.read_csv(f"{CSV}/rocket_engines.csv")
print("\nEngines: Isp vs thrust (nulls are 'not recorded')")
print(eng[["name", "isp_vac_s", "thrust_vac_n", "dry_mass_kg", "data_class"]].sort_values("isp_vac_s", ascending=False).head(8).to_string(index=False))
sx = pd.read_csv(f"{CSV}/spacex_launches.csv", parse_dates=["date_utc"])
print("\nSpaceX launches per year (2010-2018 file):")
print(sx.groupby(sx.date_utc.dt.year).agg(launches=("id", "count"), landing_successes=("landing_successes", "sum")).to_string())

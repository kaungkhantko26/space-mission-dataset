"""pandas demo on the verified CSV exports (pip install pandas). Run `python3 tools/export_data.py` first if exports/ is missing.
    python3 examples/pandas_demo.py"""
import os, pandas as pd
CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", "csv")
planets = pd.read_csv(f"{CSV}/planets.csv")
print(planets[["id", "data_class", "gravitational_parameter_km3_s2", "mean_radius_m", "derived.escape_velocity_m_s"]].round(2).to_string(index=False))
lv = pd.read_csv(f"{CSV}/launch_vehicle_configs.csv")
act = lv[(lv.active == True) & (lv.leo_capacity_kg > 0)].copy()
act["usd_per_kg_leo"] = act.launch_cost_usd / act.leo_capacity_kg
print("\nCheapest $/kg to LEO among active launchers with a published price:")
print(act.dropna(subset=["usd_per_kg_leo"]).sort_values("usd_per_kg_leo")[["full_name", "leo_capacity_kg", "launch_cost_usd", "usd_per_kg_leo"]].head(8).round(0).to_string(index=False))
sx = pd.read_csv(f"{CSV}/spacex_launch_history.csv", parse_dates=["date_utc"])
print("\nSpaceX launches per year, successes:")
print(sx.groupby(sx.date_utc.dt.year).agg(launches=("id", "count"), ok=("status", lambda s: (s == "Launch Successful").sum())).tail(8).to_string())

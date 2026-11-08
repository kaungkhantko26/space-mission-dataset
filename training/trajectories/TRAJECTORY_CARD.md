# Trajectories: Earth → Moon / planets (paths, durations, delta-v)

Built by `python3 tools/make_trajectories.py`, sanity-checked by `tools/validate_trajectories.py` against textbook values (Mars 259 d, Venus 146 d, Jupiter 997 d, Moon 5 d, Mars synodic period 780 d). All numbers are `derived` from **verified** GM, radii and semi-major axes.

| File | Content |
|---|---|
| `transfers.csv` | 9 rows: Earth(200 km LEO) → Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Moon, plus LEO → GEO. Columns: `transfer_time_days`, `departure_dv_from_leo_m_s`, `c3_km2_s2`, `vinf_*`, `capture_dv_m_s` (circular parking orbit), `total_dv_m_s`, `synodic_period_days` (launch windows repeat), `phase_angle_deg` (how far the target must lead Earth at departure), one-way light time min/max |
| `transfer_paths.json` | 91 `[x,y]` points (metres) per transfer, for drawing the path; Sun-centred for planets, Earth-centred for Moon/GEO. Departure at angle 0, arrival at 180° |
| `trajectory_qa.jsonl` | Chat Q&A on each transfer (duration, delta-v, windows, light time) |

Key results: Moon 5.0 d, TLI 3,133 m/s, lunar capture 822 m/s · Venus 146 d · Mars 259 d (3,613 m/s to leave LEO, 2,091 m/s to capture) · Jupiter 997 d · Neptune 30.6 yr.

The mission-design set (`../design/designs.csv`) now includes `transfer_days`, `total_mission_days` (engine burn time + coast) and `one_way_light_time_min` for each design.

## Limits
* Idealised coplanar circular Hohmann / patched conics: no inclination, eccentricity, gravity assists, low-thrust spirals or real launch geometry. Real missions often differ (e.g. Apollo 11 took ~3 days to reach the Moon on a faster trajectory; the idealised minimum-energy value is 5 d).
* **No calendar launch dates:** the verified data has mean elements but no mean longitudes, so only the window *spacing* (synodic period) and the phase angle are given.
* Mars/Moon design checks in `design/` are fly-by style (departure burn only); use `capture_dv_m_s` here if your game needs orbit insertion.
* Round-trip/stay times and gravity-assist routes (Voyager-style) are not included.

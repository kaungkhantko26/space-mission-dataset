# External (user-supplied) data report
> **Read first:** no source document was retrieved when this package was built (the sandbox proxy returned 403 for nasa.gov, jpl.nasa.gov and esa.int). Every external figure is therefore `unverified` (written from recalled published values with a subjective confidence tag). Derived results inherit that status. Optimization catalog values are `estimated`; credits are `fictional`.


Two files were supplied by the user and normalized by `tools/ingest_external.py` (raw copies in `data_raw/`, SHA-256 recorded in each output file and re-checked by `tools/validate.py`). Their original publisher, license and accuracy are **not verified**; the SpaceX file is described by the user as Kaggle `scoleman/spacex-launch-data`, which could not be opened from the build sandbox.

## SpaceX launch table → `missions/spacex_launch_history.json`
* 57 rows, 2010-06-04 → 2018-06-04. **The file ends at flight 56** — later launches and Block 5 maturity are absent.
* Mission success 56/57 (95% Wilson 90.7–99.7%). Landing attempts (pad/drone ship only) 25/31 = 81% (Wilson 64–91%). Rows with a re-flown booster: 12 (21%).
* Normalization: ISO dates/times, booster family and serials split, payload mass parsed to kg (approximate `~` flagged; "Classified"/blank → null; 4 unknown), orbit classes, landing outcomes parsed per booster (Falcon Heavy has three), `CCAFS LC-40`/`SLC-40` treated as one pad (assumption).
* Use in the project: observed launch reliability feeds the Simulator's optional launch-reliability factor and the Mission-fit evidence line. It does **not** replace vehicle specifications and must not be extrapolated beyond 2010–2018.

## NASA facilities table → `infrastructure/nasa_facilities.json`
* 485 facilities, all with parsed coordinates. By status: {'active': 371, 'not_recorded': 86, 'inactive': 25, 'under_rehabilitation': 3}. By derived category: {'other': 256, 'materials_lab': 73, 'acoustic_vibration_structural': 41, 'propulsion_test': 30, 'antenna_ground_station': 28, 'thermal_vacuum': 24, 'wind_tunnel': 17, 'launch_infrastructure': 16}.
* Data-quality issues found: 86 rows without status; 1 truncated status value "Under" (assumed Under Rehabilitation); 340 without URL; 92 without occupied date.
* `category` is a keyword classifier on the facility name (derived, unreviewed; 256 fall into `other`). 28 entries look like antennas/ground stations (diameter/band parsed from the name where present).
* Use in the project: reference list of ground-test and ground-station infrastructure; it is not wired into the optimizer.

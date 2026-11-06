# Verification report
> **Read first:** 25 celestial records (Sun, planets, dwarf planets, moons, small bodies) have their core physical fields verified against retrieved JPL/NASA pages (198 field checks matched; 16 conflicts were resolved to the sourced value). Six SLS/RS-25 launch figures were also verified against the NASA SLS page; all other launch-vehicle, engine, spacecraft, instrument and mission figures are still unverified (recalled values), as are two user-supplied tables (SpaceX launches 2010-2018, NASA facilities). Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: other launch-vehicle, engine, spacecraft-component, instrument and mission sources (spacex.com and api.spacexdata.com unreachable; others not attempted); those records remain unverified.


## What "verified" means here
A value is `verified` only if it was compared with a value parsed from a **retrieved local copy** of the cited page (kept in `data_raw/retrieved/`, SHA-256 in `MANIFEST.json`) within a stated tolerance. Each check stores the original text, unit, conversion, URL, retrieval date, file hash and tolerance, in `metadata/verification_celestial.json`, `metadata/verification_launch.json` and in each record's `field_verification`.
A **celestial record** is classed `verified` when its GM and mean radius are verified; its other fields are individually listed in `field_verification` or, if not checked, in `unverified_fields` (surface temperature, magnetic field, many moon orbits, ...). A **launch record** stays `unverified` as a whole; only the fields in its `field_verification` are verified (`verified_field_count`).

## Coverage
* Celestial: 198 field checks matched; 16 recalled values disagreed and were replaced by the sourced value (table below). 25 of 25 celestial records verified at core level.
* Launch: 6/6 checks against the NASA SLS page matched (table below). All other launch vehicles, engines, spacecraft components, instruments, missions, propellants and atmospheres remain **unverified**. spacex.com and api.spacexdata.com were not reachable.

## Recalled values that were wrong or outdated (now replaced)
| Record | Field | Recalled | Source | Source text | Source id |
|---|---|---:|---:|---|---|
| uranus | surface_gravity_m_s2 | 8.69 | 8.87 | 8.87 [ * ] | S02 |
| eris | mean_radius_m | 1163000.0 | 1200000.0 | 1200 [ S ] ±50 | S02 |
| eris | surface_gravity_m_s2 | 0.82 | 0.77 | 0.77 [ * ] | S02 |
| eris | rotation_period_h | 380.0 | 25.896 | 1.079 [ Y ] | S02 |
| deimos | mass_kg | 1476200000000000.0 | 1441349654645431.0 | 0.0000962 0.0000028 MAR097 | S03 |
| triton | gravitational_parameter_km3_s2 | 1427.6 | 1428.49546 | 1428.49546 0.61603 NEP097 | S03 |
| charon | gravitational_parameter_km3_s2 | 105.88 | 106.1 | 106.1 0.3 PLU060 | S03 |
| bennu | mean_radius_m | 245.5 | 242.22 | 0.48444 | S40 |
| ceres | orbital_elements.eccentricity | 0.0758 | 0.0797 | 0.0797 | S40 |
| vesta | mean_radius_m | 262700.0 | 261385.0 | 522.77 | S40 |
| vesta | orbital_elements.eccentricity | 0.0887 | 0.0902 | 0.0902 | S40 |
| pluto | orbital_elements.semi_major_axis_au | 39.48 | 39.6 | 39.6 | S40 |
| pluto | orbital_elements.eccentricity | 0.2488 | 0.252 | 0.252 | S40 |
| eris | orbital_elements.semi_major_axis_au | 67.78 | 67.9 | 67.9 | S40 |
| eris | orbital_elements.eccentricity | 0.4407 | 0.438 | 0.438 | S40 |
| eris | orbital_elements.inclination_deg | 44.0 | 43.9 | 43.9 | S40 |

Notes: JPL gives Eris mean radius 1200±50 km (no diameter in SBDB); a more precise occultation-based figure (~1163 km) exists in the literature but was not retrieved, so it is not used. Small-body elements from SBDB are osculating at the stated epoch, so they differ from older mean values.

## SLS-related launch checks
| Record | Field | Recalled | Source | Source text | Statement |
|---|---|---:|---:|---|---|
| sls_b1 | height_m | 98.0 | 98 | stands 322 ft | point value |
| sls_b1 | liftoff_mass_kg | 2,608,000 | 2,608,156 | weighs 5.75 million lbs. fueled | point value |
| sls_b1 | thrust_sl_n | 39,100,000 | 39,144,350 | produces 8.8 million lbs. of maximum thrust | point value |
| sls_b1 | payloads[TLI].payload_kg | 27,000 | 27,000 | can send more than 27 metric tons | lower bound ('more than') |
| sls_srb | thrust_sl_n | 16,000,000 | 16,013,598 | produces a maximum of 3.6 million lbs. of thrust during launch | point value |
| rs25d | thrust_vac_n | 2,279,000 | 2,277,489 | maximum of 512,000 lbs. of thrust | point value |

## Retrieved files
* `data_raw/retrieved/jpl_approx_pos.html` — https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-06, sha256 `9f7b30ca81cc…`)
* `data_raw/retrieved/jpl_planets_phys_par.html` — https://ssd.jpl.nasa.gov/planets/phys_par.html (retrieved 2026-11-06, sha256 `e49a48794729…`)
* `data_raw/retrieved/jpl_sats_phys_par.html` — https://ssd.jpl.nasa.gov/sats/phys_par/ (retrieved 2026-11-06, sha256 `9a9c004d9509…`)
* `data_raw/retrieved/nasa_sls_reference.html` — https://www.nasa.gov/reference/space-launch-system/ (retrieved 2026-11-06, sha256 `dacd12643163…`)
* `data_raw/retrieved/nssdc_earth.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html (retrieved 2026-11-06, sha256 `1b06e3ec3124…`)
* `data_raw/retrieved/nssdc_jupiter.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/jupiterfact.html (retrieved 2026-11-06, sha256 `9ac7835ae538…`)
* `data_raw/retrieved/nssdc_mars.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html (retrieved 2026-11-06, sha256 `366b0ce9b69c…`)
* `data_raw/retrieved/nssdc_mercury.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/mercuryfact.html (retrieved 2026-11-06, sha256 `170d9f2d2ba7…`)
* `data_raw/retrieved/nssdc_moon.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html (retrieved 2026-11-06, sha256 `a468979dfb41…`)
* `data_raw/retrieved/nssdc_neptune.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/neptunefact.html (retrieved 2026-11-06, sha256 `4b9166f959be…`)
* `data_raw/retrieved/nssdc_pluto.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html (retrieved 2026-11-06, sha256 `cdf13d454e44…`)
* `data_raw/retrieved/nssdc_saturn.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/saturnfact.html (retrieved 2026-11-06, sha256 `6d09ba010cac…`)
* `data_raw/retrieved/nssdc_sun.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html (retrieved 2026-11-06, sha256 `bcc186a51829…`)
* `data_raw/retrieved/nssdc_uranus.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/uranusfact.html (retrieved 2026-11-06, sha256 `02389139f834…`)
* `data_raw/retrieved/nssdc_venus.html` — https://nssdc.gsfc.nasa.gov/planetary/factsheet/venusfact.html (retrieved 2026-11-06, sha256 `473c61da0bf7…`)
* `data_raw/retrieved/sbdb_bennu.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=101955&phys-par=1 (retrieved 2026-11-06, sha256 `9b8fa7ba677f…`)
* `data_raw/retrieved/sbdb_ceres.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=1&phys-par=1 (retrieved 2026-11-06, sha256 `c8d2c7b1d5f5…`)
* `data_raw/retrieved/sbdb_eris.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=136199&phys-par=1 (retrieved 2026-11-06, sha256 `569355f0b075…`)
* `data_raw/retrieved/sbdb_pluto.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=134340&phys-par=1 (retrieved 2026-11-06, sha256 `fe9a7fa6a202…`)
* `data_raw/retrieved/sbdb_vesta.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=4&phys-par=1 (retrieved 2026-11-06, sha256 `78b6e24f9d65…`)

## How to extend
Run `tools/fetch_sources.sh`, add parsers following `tools/verify_celestial.py`, and re-run the pipeline in `README.md`. Candidate next sources: NTRS documents for Saturn V stages and engines, manufacturer user guides (PDF) for Falcon, Atlas, Ariane and Electron once their hosts are allowed.

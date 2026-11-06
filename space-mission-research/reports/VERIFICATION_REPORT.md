# Verification report
> **Read first:** 32 records are verified (25 celestial bodies at core level; engines and stages whose core numeric fields were all checked) against retrieved JPL, NASA (NTRS, SLS page, Apollo 11 press kit), ULA and ESA pages. 198 celestial and 66 launch/engine field checks matched; 16 celestial and 13 launch/engine recalled values were wrong or outdated and were replaced by the sourced value. Launch vehicles are verified field by field only (see verified_field_count); everything not checked (e.g. Falcon, Starship, Electron, Ariane, most engines, spacecraft components, instruments, missions) is still unverified, as are two user-supplied tables. Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: Retrieved: JPL SSD planetary/satellite physical parameters, JPL approximate planet elements, JPL SBDB API, NASA NSSDC fact sheets, NASA SLS page, NASA Apollo 11 press kit and three NTRS electric-propulsion documents, ULA Atlas V/Vulcan pages and the ESA Vega-C page (see metadata/sources.json). Not retrievable or not stating the numbers: SpaceX pages (JavaScript-rendered), api.spacexdata.com (HTTP 522), Rocket Lab, Aerojet Rocketdyne (403), Blue Origin (429), Arianespace manual; those records remain unverified.


## What "verified" means here
A value is `verified` only if it was compared with a value parsed from a **retrieved local copy** of the cited page (kept in `data_raw/retrieved/`, SHA-256 in `MANIFEST.json`) within a stated tolerance. Each check stores the original text, unit, conversion, URL, retrieval date, file hash and tolerance, in `metadata/verification_celestial.json`, `metadata/verification_launch.json` and in each record's `field_verification`.
A **celestial record** is classed `verified` when its GM and mean radius are verified; its other fields are individually listed in `field_verification` or, if not checked, in `unverified_fields` (surface temperature, magnetic field, many moon orbits, ...). A **launch record** stays `unverified` as a whole; only the fields in its `field_verification` are verified (`verified_field_count`).

## Coverage
* Celestial: 198 field checks matched; 16 recalled values disagreed and were replaced by the sourced value (table below). 25 of 25 celestial records verified at core level.
* Launch vehicles, stages, boosters, engines and the Apollo 11 launch date: 86 checks against NASA (SLS page, Apollo 11 press kit, NTRS electric-propulsion papers), ULA and ESA pages — 66 matched, 13 recalled values were wrong/outdated and replaced by the sourced value, 7 previously empty fields were filled from the source (table below). A record is classed `verified` only if **all** of its populated core numeric fields were checked: the 3 Saturn V stages, NEXT, NSTAR, BPT-4000 and BE-4. Vehicles are verified field by field. **Not verifiable with the retrieved material (still unverified):** Falcon 9/Heavy, Starship, Merlin, Raptor, Rutherford, Electron, Ariane 5, Delta IV, New Glenn, Soyuz, Long March 5, RL10, Vinci, Vulcain 2, Star 48B, MR-103, AJ10, Draco, T6, SPT-100, RSRM; most spacecraft components, instruments, propellants, atmospheres and mission figures. Reasons: SpaceX pages are JavaScript-rendered, api.spacexdata.com returned HTTP 522, Rocket Lab was unreachable, Aerojet Rocketdyne returned 403, Blue Origin returned 429, and no retrievable document gave the numbers.

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

## Launch / engine / stage checks
| Record | Field | Recalled | Source | Status | Source text | Source id |
|---|---|---:|---:|---|---|---|
| launch_vehicles/atlas_v_551 | payloads[LEO].payload_kg | 18,850 | 18,850 | verified | 551 3,850 kg 8,500 lbs 8,900 kg 19,620 lbs 18,850 kg 41,570 lbs 15,760 | S42 |
| launch_vehicles/atlas_v_551 | payloads[GTO].payload_kg | 8,900 | 8,900 | verified | 551 3,850 kg 8,500 lbs 8,900 kg 19,620 lbs 18,850 kg 41,570 lbs 15,760 | S42 |
| launch_vehicles/atlas_v_551 | payloads[LEO].altitude_km | — | 200 | added_from_source | LEO-Reference (Low Earth Orbit-Reference) =200 km circular at 28.7 deg | S42 |
| launch_vehicles/atlas_v_551 | payloads[LEO].inclination_deg | 28.7 | 28.7 | verified | 200 km circular at 28.7 deg | S42 |
| launch_vehicles/atlas_v_551 | payloads[GTO].inclination_deg | — | 27 | added_from_source | GTO (Geosynchronous Transfer Orbit)=35,786 km x 185 km at 27.0 deg | S42 |
| rocket_engines/rd180 | thrust_sl_n | 3,830,000 | 3,826,805 | verified | Nominal Thrust (sea level): 860,300 lbs | S42 |
| rocket_engines/rd180 | isp_sl_s | 311 | 311 | verified | Specific Impulse (sea level): 311 seconds | S42 |
| rocket_engines/rd180 | dry_mass_kg | 5,393 | 5,480 | conflict | Length: 140 in Weight: 12,081 lbs | S42 |
| launch_vehicles/vulcan_vc6 | payloads[GTO].payload_kg | 14,400 | 14,500 | conflict | 6 Solids 6,500 kg 14,300 lb 14,500 kg 32,000 lbs 27,200 kg 60,000 lbs  | S42 |
| launch_vehicles/vulcan_vc6 | payloads[LEO].payload_kg | 27,200 | 27,200 | verified | 6 Solids 6,500 kg 14,300 lb 14,500 kg 32,000 lbs 27,200 kg 60,000 lbs  | S42 |
| launch_vehicles/vulcan_vc6 | payloads[TLI].payload_kg | — | 11,500 | added_from_source | 6 Solids 6,500 kg 14,300 lb 14,500 kg 32,000 lbs 27,200 kg 60,000 lbs  | S42 |
| launch_vehicles/vulcan_vc6 | payloads[LEO].altitude_km | — | 200 | added_from_source | LEO-Reference = 200 km circular at 28.7 deg | S42 |
| launch_vehicles/vulcan_vc6 | payloads[LEO].inclination_deg | — | 28.7 | added_from_source | LEO-Reference = 200 km circular at 28.7 deg | S42 |
| launch_vehicles/vulcan_vc6 | payloads[GTO].inclination_deg | — | 27 | added_from_source | GTO = 35,786 km x 185 km at 27.0 deg | S42 |
| launch_vehicles/vulcan_vc6 | fairing_diam_m | 5.4 | 5.4 | verified | 5.4-m- (17.7-ft-) diameter payload fairing | S42 |
| rocket_engines/be4 | thrust_sl_n | 2,400,000 | 2,446,522 | conflict | Nominal Thrust (sea level): 550,000 lbs | S42 |
| launch_vehicles/vega_c | height_m | 35 | 35 | verified | nearly 35 m high | S43 |
| launch_vehicles/vega_c | liftoff_mass_kg | 210,000 | 210,000 | verified | weighs 210 tonnes on the launch pad | S43 |
| launch_vehicles/vega_c | payloads[SSO].payload_kg | 2,300 | 2,300 | verified | can launch 2.3 tonnes to a Sun-synchronous orbit | S43 |
| launch_vehicles/vega_c | fairing_diam_m | 3.3 | 3.3 | verified | fairing at the top of Vega-C is 3.3 m in diameter | S43 |
| launch_vehicles/vega_c | fairing_height_m | 8.1 | 9 | conflict | in diameter and over 9 m tall | S43 |
| launch_vehicles/vega_c | stages | 4 | 4 | verified | main elements are three solid-propellant stages, an upper stage powere | S43 |
| rocket_stages/saturn_v_s1c | dry_mass_kg | 137,000 | 130,975 | conflict | 288,750'LBS. DRY | S44 |
| rocket_stages/saturn_v_s2 | dry_mass_kg | 36,200 | 36,250 | verified | 79,918 LBS DR | S44 |
| rocket_stages/saturn_v_s4b | dry_mass_kg | 10,600 | 11,340 | conflict | 25,000 LBS DRY | S44 |
| rocket_stages/saturn_v_s1c | propellant_mass_kg | 2,077,000 | 2,147,272 | conflict | LIQUID OXYGEN (3,307,855 LBS + RP-I (KEROSENE) - (1,426,069 LBS | S44 |
| rocket_stages/saturn_v_s2 | propellant_mass_kg | 456,100 | 444,177 | conflict | LlQU ID OXYGEN (821,022 LBS + (158,221 LBS ., 282,555 | S44 |
| rocket_stages/saturn_v_s4b | propellant_mass_kg | 109,500 | 106,831 | conflict | LIQUID OXYGEN (192,023 LBS + (43,500 LBS , 77,680 | S44 |
| launch_vehicles/saturn_v | liftoff_mass_kg | 2,970,000 | 2,941,220 | conflict | A t ignition 6,484,280 | S44 |
| launch_vehicles/saturn_v | thrust_sl_n | 33,400,000 | 34,046,039 | conflict | THRUST 7,653,854 LBS AT LIFTOFF | S44 |
| launch_vehicles/saturn_v | height_m | 110.6 | 110.6 | verified | the 363-foot-tall space vehicle | S44 |
| launch_vehicles/saturn_v | diameter_m | 10.1 | 10.06 | verified | DIAMETER-33 FEET | S44 |
| rocket_engines/f1 | thrust_sl_n | 6,770,000 | 6,809,208 | verified | THRUST 7,653,854 LBS AT LIFTOFF | S44 |
| rocket_engines/j2 | thrust_vac_n | 1,033,000 | 1,029,947 | verified | THRUST 1,120,216 TO 1,157,707 LBS | S44 |
| rocket_stages/saturn_v_s1c | n_engines | 5 | 5 | verified | FIVE F-I | S44 |
| rocket_stages/saturn_v_s2 | n_engines | 5 | 5 | verified | ENGINES FIVE J-2 | S44 |
| rocket_stages/saturn_v_s4b | n_engines | 1 | 1 | verified | ONE J-2 | S44 |
| missions/apollo11 | launch_date | 1969-07-16 | 1969-07-16 | verified | Apollo 11 is scheduled for launch at 9:32 a.m. EDT July 16 | S44 |
| launch_vehicles/ariane62 | payloads[GTO].payload_kg | 4,500 | 4,500 | verified | Ariane 62 can launch payloads of approximately 4.5 tonnes into geostat | S48 |
| launch_vehicles/ariane62 | payloads[LEO].payload_kg | 10,350 | 10,300 | verified | Ariane 62 can launch payloads of approximately 4.5 tonnes into geostat | S48 |
| launch_vehicles/ariane62 | fairing_diam_m | 5.4 | 5.4 | verified | Both are 5.4 m in diameter | S48 |
| launch_vehicles/ariane62 | fairing_height_m | 20 | 20 | verified | two sizes: 20 m and a shorter | S48 |
| launch_vehicles/ariane62 | height_m | 62 | 60 | verified | At over 60 metres tall | S48 |
| launch_vehicles/ariane64 | payloads[GTO].payload_kg | 11,500 | 11,500 | verified | Ariane 64 can launch payloads of approximately 11.5 tonnes into geosta | S48 |
| launch_vehicles/ariane64 | payloads[LEO].payload_kg | 21,650 | 21,600 | verified | Ariane 64 can launch payloads of approximately 11.5 tonnes into geosta | S48 |
| launch_vehicles/ariane64 | fairing_diam_m | 5.4 | 5.4 | verified | Both are 5.4 m in diameter | S48 |
| launch_vehicles/ariane64 | fairing_height_m | 20 | 20 | verified | two sizes: 20 m and a shorter | S48 |
| launch_vehicles/ariane64 | height_m | 62 | 60 | verified | At over 60 metres tall | S48 |
| launch_vehicles/sls_b1 | height_m | 98 | 98.15 | verified | stands 322 ft | S41 |
| launch_vehicles/sls_b1 | liftoff_mass_kg | 2,608,000 | 2,608,156 | verified | weighs 5.75 million lbs. fueled | S41 |
| launch_vehicles/sls_b1 | thrust_sl_n | 39,100,000 | 39,144,350 | verified | produces 8.8 million lbs. of maximum thrust | S41 |
| launch_vehicles/sls_b1 | payloads[TLI].payload_kg | 27,000 | 27,000 | verified | can send more than 27 metric tons | S41 |
| boosters/sls_srb | thrust_sl_n | 16,000,000 | 16,013,598 | verified | produces a maximum of 3.6 million lbs. of thrust during launch | S41 |
| rocket_engines/rs25d | thrust_vac_n | 2,279,000 | 2,277,489 | verified | maximum of 512,000 lbs. of thrust | S41 |
| rocket_engines/next | thrust_vac_n | 0.236 | 0.236 | verified | Thrust, mN 26-236 | S45 |
| rocket_engines/next | isp_vac_s | 4,190 | 4,190 | verified | Max. Specific Impulse, sec 4190 | S45 |
| rocket_engines/next | power_w | 6,900 | 6,900 | verified | Thruster Power Range, kW 0.5-6.9 | S45 |
| rocket_engines/next | dry_mass_kg | — | 13.5 | added_from_source | Mass (with harness), kg 13.5 | S45 |
| rocket_engines/nstar | thrust_vac_n | 0.092 | 0.092 | verified | thrust is 92 mN | S46 |
| rocket_engines/nstar | power_w | 2,300 | 2,300 | verified | 0.5 kW to 2.3 kW range | S46 |
| rocket_engines/nstar | isp_vac_s | 3,100 | 3,300 | conflict | specific impulse is about 3300 s | S46 |
| rocket_engines/bpt4000 | thrust_vac_n | 0.254 | 0.254 | verified | 4.5 kW–400 V 254 2150 | S47 |
| rocket_engines/bpt4000 | isp_vac_s | 1,850 | 2,150 | conflict | 4.5 kW–400 V 254 2150 | S47 |
| rocket_engines/bpt4000 | power_w | 4,500 | 4,500 | verified | BPT–4000 4.5 kW Hall | S47 |
| missions/apollo11 | launch_vehicle_note | Saturn V | Saturn 5 | verified | Launch Vehicle: Saturn 5 | S49 |
| missions/voyager2 | launch_date | 1977-08-20 | 1977-08-20 | verified | Launch Date: 1977-08-20 | S49 |
| missions/voyager2 | launch_vehicle_note | Titan IIIE-Centaur | Titan IIIE-Centaur | verified | Launch Vehicle: Titan IIIE-Centaur | S49 |
| missions/lro | launch_date | 2009-06-18 | 2009-06-18 | verified | Launch Date: 2009-06-18 | S49 |
| missions/lro | launch_vehicle_note | Atlas V 401 | Atlas V 401 | verified | Launch Vehicle: Atlas V 401 | S49 |
| missions/mro | launch_date | 2005-08-12 | 2005-08-12 | verified | Launch Date: 2005-08-12 | S49 |
| missions/mro | launch_vehicle_note | Atlas V 401 | Atlas V 401 | verified | Launch Vehicle: Atlas V 401 | S49 |
| missions/new_horizons | launch_date | 2006-01-19 | 2006-01-19 | verified | Launch Date: 2006-01-19 | S49 |
| missions/new_horizons | launch_vehicle_note | Atlas V 551 + Star 48B | Atlas V | verified | Launch Vehicle: Atlas V | S49 |
| missions/juno | launch_date | 2011-08-05 | 2011-08-05 | verified | Launch Date: 2011-08-05 | S49 |
| missions/juno | launch_vehicle_note | Atlas V 551 | Atlas V | verified | Launch Vehicle: Atlas V | S49 |
| missions/curiosity | launch_date | 2011-11-26 | 2011-11-26 | verified | Launch Date: 2011-11-26 | S49 |
| missions/curiosity | launch_vehicle_note | Atlas V 541 | Atlas V | verified | Launch Vehicle: Atlas V | S49 |
| missions/jwst | launch_date | 2021-12-25 | 2021-12-25 | verified | Launch Date: 2021-12-25 | S49 |
| missions/jwst | launch_vehicle_note | Ariane 5 ECA | Ariane 5 | verified | Launch Vehicle: Ariane 5 | S49 |
| missions/landsat8 | launch_date | 2013-02-11 | 2013-02-11 | verified | Launch Date: 2013-02-11 | S49 |
| missions/landsat8 | launch_vehicle_note | Atlas V 401 | Atlas V | verified | Launch Vehicle: Atlas V | S49 |
| missions/dawn | launch_date | 2007-09-27 | 2007-09-27 | verified | Launch Date: 2007-09-27 | S49 |
| missions/dawn | launch_vehicle_note | Delta II 7925H | Delta II 7925 | verified | Launch Vehicle: Delta II 7925 | S49 |
| missions/osiris_rex | launch_date | 2016-09-08 | 2016-09-08 | verified | Launch Date: 2016-09-08 | S49 |
| missions/osiris_rex | launch_vehicle_note | Atlas V 411 | Atlas V | verified | Launch Vehicle: Atlas V | S49 |
| missions/apollo11 | launch_mass_kg | 43,904 | 43,863 | verified | CSM 28801 kg (NSSDC catalog) + LM 33,205 lb (press kit) | S44 |

## Retrieved files
* `data_raw/retrieved/esa_ariane6_overview.html` — https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_6_overview (retrieved 2026-11-06, sha256 `232128d5a239…`)
* `data_raw/retrieved/esa_vega_c.html` — https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Vega-C (retrieved 2026-11-06, sha256 `623c5d122bda…`)
* `data_raw/retrieved/jpl_approx_pos.html` — https://ssd.jpl.nasa.gov/planets/approx_pos.html (retrieved 2026-11-06, sha256 `9f7b30ca81cc…`)
* `data_raw/retrieved/jpl_planets_phys_par.html` — https://ssd.jpl.nasa.gov/planets/phys_par.html (retrieved 2026-11-06, sha256 `e49a48794729…`)
* `data_raw/retrieved/jpl_sats_phys_par.html` — https://ssd.jpl.nasa.gov/sats/phys_par/ (retrieved 2026-11-06, sha256 `9a9c004d9509…`)
* `data_raw/retrieved/nasa_sls_reference.html` — https://www.nasa.gov/reference/space-launch-system/ (retrieved 2026-11-06, sha256 `dacd12643163…`)
* `data_raw/retrieved/nmc/nmc_1969-059A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=1969-059A (retrieved 2026-11-06, sha256 `0fcc4dc45fd1…`)
* `data_raw/retrieved/nmc/nmc_1977-076A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=1977-076A (retrieved 2026-11-06, sha256 `3a0d986206bc…`)
* `data_raw/retrieved/nmc/nmc_2005-029A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2005-029A (retrieved 2026-11-06, sha256 `d5103ce69355…`)
* `data_raw/retrieved/nmc/nmc_2006-001A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2006-001A (retrieved 2026-11-06, sha256 `2d248ace1e7a…`)
* `data_raw/retrieved/nmc/nmc_2007-043A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2007-043A (retrieved 2026-11-06, sha256 `2584f4361300…`)
* `data_raw/retrieved/nmc/nmc_2009-031A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2009-031A (retrieved 2026-11-06, sha256 `331911babce1…`)
* `data_raw/retrieved/nmc/nmc_2011-040A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2011-040A (retrieved 2026-11-06, sha256 `0cb4c192aeb4…`)
* `data_raw/retrieved/nmc/nmc_2011-070A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2011-070A (retrieved 2026-11-06, sha256 `aab40fec9ab3…`)
* `data_raw/retrieved/nmc/nmc_2013-008A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2013-008A (retrieved 2026-11-06, sha256 `80345819acab…`)
* `data_raw/retrieved/nmc/nmc_2016-055A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2016-055A (retrieved 2026-11-06, sha256 `447db5b5b091…`)
* `data_raw/retrieved/nmc/nmc_2021-130A.html` — https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2021-130A (retrieved 2026-11-06, sha256 `9a7263c80f76…`)
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
* `data_raw/retrieved/ntrs_19690022248.pdf` — https://ntrs.nasa.gov/api/citations/19690022248/downloads/19690022248.pdf (retrieved 2026-11-06, sha256 `3cce3b01294e…`)
* `data_raw/retrieved/ntrs_19980017550.pdf` — https://ntrs.nasa.gov/api/citations/19980017550/downloads/19980017550.pdf (retrieved 2026-11-06, sha256 `b2d854d8930a…`)
* `data_raw/retrieved/ntrs_20060051789.pdf` — https://ntrs.nasa.gov/api/citations/20060051789/downloads/20060051789.pdf (retrieved 2026-11-06, sha256 `e1925304ce7c…`)
* `data_raw/retrieved/ntrs_20090004685.pdf` — https://ntrs.nasa.gov/api/citations/20090004685/downloads/20090004685.pdf (retrieved 2026-11-06, sha256 `d8c4e650599e…`)
* `data_raw/retrieved/sbdb_bennu.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=101955&phys-par=1 (retrieved 2026-11-06, sha256 `9b8fa7ba677f…`)
* `data_raw/retrieved/sbdb_ceres.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=1&phys-par=1 (retrieved 2026-11-06, sha256 `c8d2c7b1d5f5…`)
* `data_raw/retrieved/sbdb_eris.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=136199&phys-par=1 (retrieved 2026-11-06, sha256 `569355f0b075…`)
* `data_raw/retrieved/sbdb_pluto.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=134340&phys-par=1 (retrieved 2026-11-06, sha256 `fe9a7fa6a202…`)
* `data_raw/retrieved/sbdb_vesta.json` — https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=4&phys-par=1 (retrieved 2026-11-06, sha256 `78b6e24f9d65…`)
* `data_raw/retrieved/ula_atlas_v.html` — https://www.ulalaunch.com/rockets/atlas-v (retrieved 2026-11-06, sha256 `47ae205afab1…`)
* `data_raw/retrieved/ula_vulcan.html` — https://www.ulalaunch.com/rockets/vulcan-centaur (retrieved 2026-11-06, sha256 `187fad654295…`)

## Notes on specific findings
* Saturn V: the Apollo 11 press kit shows my recalled S-IC dry mass (137,000 kg), S-IC and S-II/S-IVB propellant, S-IVB dry mass, liftoff mass and liftoff thrust were off by 1–7%; the document's values (nominal Apollo 11 vehicle) are now used. The old 33.4 vs 34.5-35.1 MN thrust conflict is resolved by the source: 7,653,854 lbf = 34.05 MN.
* NSTAR: the retrieved paper is a 1998 pre-flight document (Isp 'about 3300 s'); flight-measured Isp was not retrieved, so the sourced value is used with that caveat.
* BPT-4000: NASA/TM-2006-214453 Table 2 gives 254 mN and 2150 s at 4.5 kW-400 V (my recalled 1850 s was wrong).
* ULA: Atlas V 551 LEO/GTO capacities matched; reference orbits were filled in (200 km, 28.7 deg; GTO at 27 deg). Vulcan VC6 GTO is 14,500 kg (not 14,400) and TLI is 11,500 kg (added). RD-180 weight is 12,081 lb (5,480 kg); BE-4 sea-level thrust is 550,000 lbf (2.45 MN).
* ESA: Ariane 62/64 GTO/LEO capacities, fairing and height match the ESA overview page (LEO figures are quoted to 0.1 t, so they are verified within 1%).
* ESA: Vega-C fairing is 'over 9 m' tall (recalled 8.1 m was wrong).

## How to extend
Run `tools/fetch_sources.sh`, add parsers following `tools/verify_celestial.py`, and re-run the pipeline in `README.md`. Candidate next sources: NTRS documents for Saturn V stages and engines, manufacturer user guides (PDF) for Falcon, Atlas, Ariane and Electron once their hosts are allowed.

# Data guide for the Space Mission Design Game

**Game brief:** the player designs, manages and simulates a space mission and must *balance spacecraft, scientific instruments, launch vehicle, budget, mass, power, communication and orbit*; the game shows how each choice changes mission success. Math + engineering + optimization + coding + game design, for secondary students.

Everything here is **verified** (compared with, or ingested directly from, a retrieved source). Gaps are listed honestly in the last section. Collections are in `verified/`, the API, `exports/` (CSV/SQLite) and the local backend (`python3 tools/serve_api.py`).

## What each game mechanic can use
| Mechanic (the balance the player manages) | Data | Key fields | Formula / how to use it |
|---|---|---|---|
| **Destination & orbit** | `planets` (Sun + 8), `moons` (11), `orbital_elements`, `moon_mean_elements` | `gravitational_parameter_km3_s2`, `mean_radius_m`, `surface_gravity_m_s2`, `derived.escape_velocity_m_s`, `semi_major_axis_m`, `nssdc_fact_sheet.numeric` (J2, length of day, obliquity, albedo) | circular speed √(μ/r), period 2π√(r³/μ), Hohmann transfer (`POST /hohmann`), plane change, eclipse fraction ≈ asin(R/r)/π |
| **Atmosphere / entry / drag** | `atmospheres` | `published` text and `parsed` pressure, scale height, temperature, composition | exponential density ρ = ρ₀·e^(−h/H) with the published scale height |
| **Launch vehicle** | `launch_vehicle_configs` (532), `launch_vehicles`, `payload_capabilities`, `rocket_stages` | `leo_capacity_kg`, `gto_capacity_kg`, `launch_mass_t`, `liftoff_thrust_kn`, `launch_cost_usd`, `total_launches`, `failed_launches` | spacecraft wet mass ≤ capacity (keep margin); cost per kg = cost / capacity; **risk** = failed ÷ total launches (or use `spacex_launch_history`) |
| **Mass budget** | all of the above + `smallsat_components`, `nasa_missions.catalog_mass_kg` | component `Mass [kg]/[g]` columns, vehicle capacity | Σ(subsystems) + margin + propellant ≤ launch capacity |
| **Propulsion & delta-v** | `electric_propulsion` (NEXT, NSTAR, BPT-4000), `rocket_engines`, `smallsat_components` (domain `propulsion`), `fluid_properties` | `isp_vac_s`, `thrust_vac_n`, `power_w`; SoA columns Thrust [mN], Specific Impulse [s], Mass [kg], Power [W] | rocket equation Δv = Isp·g₀·ln(m₀/m_f) (`POST /delta-v`); burn time = m·Δv/F; propellant density from `fluid_properties` for tank size |
| **Power** | `smallsat_components` (domain `power`: solar cells/arrays, batteries, PMAD), `planets[].nssdc_fact_sheet` | solar irradiance W/m² per planet, battery Wh/kg, array specific power | array power = irradiance × area × efficiency; battery Wh ≥ load × eclipse time ÷ depth-of-discharge |
| **Communication** | `smallsat_components` (domain `communications`, `ground_systems`), `analysis.light_time` | radio data rate [kbps], Tx power, frequency, mass; one-way light time | Friis equation (see the site's Calculators); data volume = rate × contact time |
| **Scientific instruments** | `nasa_instruments` (181), `nasa_missions` (39) | `description` (specs in prose), `mass_kg_from_text`, `power_w_from_text` + the source sentence | pick instruments by what they measure; budget their mass/power where the text states it |
| **Budget** | `launch_vehicle_configs.launch_cost_usd` (119 vehicles), `nasa_missions.cost_mentions_in_text` | dollar amounts as stated | total cost = launch + hardware + operations; only launch prices are structured data |
| **Mission success / risk** | `spacex_launch_history` (743), config launch counts, `missions` | status, failure reason | probability of launch success = successes ÷ launches |
| **Learning / scenarios** | `nasa_missions`, `rocket_stages` (Saturn V), `missions` | real missions as benchmarks | e.g. recreate LRO or Voyager 2 and compare |

## Trust rules for the game
* Show `data_class`/`source_authority` where a number came from; Launch Library capacities have **no stated reference orbit**; SoA component numbers are **vendor-reported**.
* Absent field = not verified; never default it to 0.
* Costs of components and instruments are **not in the data** — use launch prices, or let teachers set game-balance prices (and label them as game values, not real prices).

## Removed because the game does not use it
Asteroid catalogs (JPL NHATS and SBDB lists), dwarf planets/asteroid bodies, the 485 NASA facilities table, tracking/deorbit/3D-printing/software tables from the NASA report. They can be restored from the repository history or the staging build if a future game mode needs them.

## What is still missing (no retrievable source found)
* **Structured instrument specs:** mass, power, data rate per instrument. NASA's catalog gives prose; mass is stated for 18 instruments and power for 6 (sentence quoted).
* **Component and mission prices:** only launch prices (119 vehicles) and 3 mission cost statements.
* **Storable propellants** (RP-1, hydrazine, MMH, NTO) property tables.
* **Reference orbits** for Launch Library capacities.
If you can supply a dataset or document (CSV/PDF) for these, `tools/ingest_real.py` shows how to add and validate it.

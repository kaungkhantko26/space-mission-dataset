# Engineering analysis
> **Read first:** 25 celestial records (Sun, planets, dwarf planets, moons, small bodies) have their core physical fields verified against retrieved JPL/NASA pages (198 field checks matched; 16 conflicts were resolved to the sourced value). Six SLS/RS-25 launch figures were also verified against the NASA SLS page; all other launch-vehicle, engine, spacecraft, instrument and mission figures are still unverified (recalled values), as are two user-supplied tables (SpaceX launches 2010-2018, NASA facilities). Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: other launch-vehicle, engine, spacecraft-component, instrument and mission sources (spacex.com and api.spacexdata.com unreachable; others not attempted); those records remain unverified.


Methods: two-body/patched-conic orbital mechanics, Tsiolkovsky rocket equation, Friis link budget, inverse-square solar flux (`tools/astro.py`). All approximations are idealizations (impulsive burns, circular coplanar orbits, no losses) and are labelled as such in the JSON.

## Stack ideal Δv (Tsiolkovsky)
Ideal Δv ignores gravity, drag and steering losses, so it must not be read as orbital insertion capability (real ascent to LEO needs roughly 9.3–9.5 km/s including losses — a commonly cited range, not retrieved here).

| Vehicle | Ideal Δv, low (m/s) | Ideal Δv, high (m/s) |
|---|---:|---:|
| saturn_v | 9,132 | 9,615 |
| sls_b1 | 1,707 | 2,108 |
| falcon9_b5 | 7,938 | 8,300 |
| electron | 11,573 | 11,996 |

**Do not trust these rows without the accounting check below.** *Electron*'s recorded stage masses sum exactly to its liftoff mass (no payload/fairing room), so its ≈12 km/s figure is an overestimate and flags inconsistent inputs. *SLS* is core-stage-only (boosters not modeled) so its total is not a vehicle capability.

## Mass accounting check (liftoff − Σ recorded stage masses)
| Vehicle | Liftoff (kg) | Σ stages (kg) | Residual (kg) |
|---|---:|---:|---:|
| saturn_v | 2,970,000 | 2,826,400 | 143,600 |
| sls_b1 | 2,608,000 | 1,072,300 | 1,535,700 |
| falcon9_b5 | 549,054 | 517,970 | 31,084 |
| electron | 12,500 | 12,500 | 0 |

Residual should equal payload + fairing + interstages (+ boosters). Falcon 9's 31 t residual exceeds payload+fairing implied by its own payload record, so at least one input is likely wrong — retrieval needed.

## Historical mission mass fractions
| Mission | Launch (kg) | Dry (kg) | Non-dry fraction |
|---|---:|---:|---:|
| lro | 1,916 | 1,018 | 46.9% |
| mro | 2,180 | 1,031 | 52.7% |
| juno | 3,625 | 1,593 | 56.1% |

## Interplanetary reference (circular, coplanar Hohmann; 400 km parking/capture orbits)
| Target | v∞ dep. (m/s) | Departure Δv from LEO (m/s) | Capture Δv to 400 km circular (m/s) | Transfer (d) | Synodic (d) |
|---|---:|---:|---:|---:|---:|
| venus | 2,495 | 3,461 | 3,298 | 146 | 584 |
| mars | 2,945 | 3,571 | 2,081 | 259 | 780 |
| jupiter | 8,793 | 6,293 | 17,847 | 998 | 399 |
| saturn | 10,289 | 7,280 | 10,945 | 2,208 | 378 |
| uranus | 11,281 | 7,980 | 6,718 | 5,857 | 370 |
| neptune | 11,654 | 8,251 | 7,195 | 11,182 | 367 |

Outer-planet capture into low circular orbit is unrealistically expensive; real missions capture into highly elliptical orbits or aerobrake. Real transfers use gravity assists, eccentric/inclined orbits.

## Power
Eclipse (circular, β=0, cylindrical shadow): LEO 500 km 35.7 min (38% of period); LEO 400 km 36.0 min (39% of period); GEO 69.3 min (5% of period); Lunar orbit 100 km 46.5 min (39% of period); Mars orbit 400 km 41.6 min (35% of period).

## Communications
Free-space loss at X-band (8.4 GHz): Moon (mean) 222.6 dB; Mars min 265.8 dB; Mars max 283.0 dB; Jupiter (mean) 288.8 dB; Saturn (mean) 294.0 dB; Neptune (mean) 304.0 dB.

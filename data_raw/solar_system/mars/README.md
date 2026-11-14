\# Mars Heliocentric State Vector Dataset



\## Overview

This dataset contains Mars' heliocentric position and velocity vectors obtained from NASA/JPL Horizons.



\## Data Source

\- Provider: NASA/JPL Solar System Dynamics

\- Tool: JPL Horizons System

\- URL: https://ssd.jpl.nasa.gov/horizons/app.html

\- Target: Mars (499)

\- Center: Sun (10)

\- Ephemeris Source: DE441



\## Query Configuration

\- Start Date: 2028-12-15 (TDB)

\- Stop Date: 2029-08-31 (TDB)

\- Sampling Interval: 1 day

\- Reference Frame: Ecliptic of J2000.0

\- Output Type: Geometric Cartesian States

\- Distance Unit: AU

\- Velocity Unit: AU/day



\## Dataset Files

\- mars\_vectors\_raw.txt: Original Horizons output.

\- mars\_vectors.csv: Extracted and structured vector data.



\## CSV Structure



| Column | Description | Unit |

|---|---|---|

| JD\_TDB | Julian Date (TDB) | day |

| Calendar\_Date\_TDB | Calendar date (TDB) | - |

| X\_AU | Heliocentric X position | AU |

| Y\_AU | Heliocentric Y position | AU |

| Z\_AU | Heliocentric Z position | AU |

| VX\_AU\_per\_day | X velocity | AU/day |

| VY\_AU\_per\_day | Y velocity | AU/day |

| VZ\_AU\_per\_day | Z velocity | AU/day |



\## Data Validation

\- Total data rows: 260

\- Total columns: 8

\- CSV structure: Validated

\- Date range: 2028-12-15 to 2029-08-31 (TDB)

\- Date alignment with Earth dataset: Verified



\## Important Notes

This dataset represents Mars' heliocentric state vectors. It is not a simulated spacecraft trajectory or a validated Earth-to-Mars transfer trajectory.



The mission dates are provisional simulation dates. Further trajectory analysis is required before using them as actual mission parameters.



\## License and Attribution

Data source: NASA/JPL Horizons.

Please refer to the official source and its applicable data-use and attribution policies.


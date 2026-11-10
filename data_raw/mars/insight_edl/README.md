\# InSight EDL Atmospheric Dataset



\## Overview

This dataset contains atmospheric measurements reconstructed from the NASA InSight Entry, Descent, and Landing (EDL) event at Mars.



\## Source

\- \*\*Original source:\*\* NASA Planetary Data System (PDS)

\- \*\*Data file:\*\* `edl\_atmosphere.tab`

\- \*\*Official source:\*\* https://atmos.nmsu.edu/PDS/data/PDS4/insight\_edl\_bundle/data/edl\_atmosphere.tab

\- \*\*Metadata:\*\* https://atmos.nmsu.edu/PDS/data/PDS4/insight\_edl\_bundle/data/edl\_atmosphere.xml



\## Clean Dataset

\- \*\*Filename:\*\* `edl\_atmosphere\_clean.csv`

\- \*\*Records:\*\* 37,470

\- \*\*Columns:\*\* 17

\- \*\*File format:\*\* CSV

\- \*\*File size:\*\* Approximately 7.30 MB



\## Data Cleaning

The original NASA data was converted from whitespace-separated `.tab` format into CSV.



Rows containing the `-999` placeholder in any of the following atmospheric measurement columns were excluded:

\- Atmospheric Density (Column L)

\- Atmospheric Pressure (Column N)

\- Atmospheric Temperature (Column P)



The original raw data was preserved without modification.



\## Key Measurement Units

\- Planetocentric Altitude: meter (m)

\- Atmospheric Density: kg/m³

\- Atmospheric Pressure: Pascal (Pa)

\- Atmospheric Temperature: Kelvin (K)



\## Important Notes

\- This dataset represents reconstructed measurements from a specific Mars landing event, not a global Mars atmospheric dataset.

\- The cleaned dataset is intended for scientific reference, analysis, and Mars landing simulation development.

\- Always refer to the original NASA PDS metadata for complete field definitions and units.



\## Project

NASA Hackathon – Mars Mission Simulation Game


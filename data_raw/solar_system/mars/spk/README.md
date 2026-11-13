\# MAVEN SPICE SPK — Reconstructed Cruise Trajectory



\## 1. Dataset Overview



This dataset contains the reconstructed cruise trajectory of NASA's Mars Atmosphere and Volatile Evolution (MAVEN) spacecraft.



The data is provided as a binary SPICE SPK (Spacecraft and Planet Kernel) file, which contains spacecraft position and velocity information over a specified time interval.



\*\*Mission:\*\* Mars Atmosphere and Volatile Evolution (MAVEN)  

\*\*Spacecraft:\*\* MAVEN  

\*\*Target Body:\*\* Mars  

\*\*Kernel Type:\*\* SPK  

\*\*Data Type:\*\* Reconstructed Cruise Trajectory  

\*\*Processing Level:\*\* Derived



\## 2. Files



| Filename | Description |

|---|---|

| `maven\_cru\_rec\_131118\_140923\_v1.bsp` | Binary SPICE SPK trajectory kernel |

| `maven\_cru\_rec\_131118\_140923\_v1.xml` | NASA PDS4 metadata describing the SPK file |



\## 3. Temporal Coverage



\- \*\*Start:\*\* 2013-11-18 19:20:42 UTC

\- \*\*End:\*\* 2014-09-23 11:58:53 UTC



The coverage includes the cruise phase leading to Mars and the period surrounding the Mars Orbit Insertion (MOI) event on September 21, 2014.



Note: The metadata describes this product as a reconstructed cruise trajectory. The exact coverage and availability of individual trajectory segments should be verified before using it for detailed MOI maneuver analysis.



\## 4. Data Source



\*\*Provider:\*\* NASA / Jet Propulsion Laboratory (JPL) — NAIF  

\*\*Mission Data Archive:\*\* MAVEN SPICE Archive



\- \[MAVEN SPICE Documentation](https://naif.jpl.nasa.gov/pub/naif/pds/pds4/maven/maven\_spice/document/spiceds\_v005.html)

\- \[SPK Kernel Directory](https://naif.jpl.nasa.gov/pub/naif/pds/pds4/maven/maven\_spice/spice\_kernels/spk/)



\## 5. File Integrity



The downloaded SPK file was verified against the MD5 checksum provided in its official NASA PDS4 XML metadata.



\*\*Expected MD5:\*\*

`8d7c55ef3bb935ad487c529f5be5343d`



\*\*Calculated MD5:\*\*

`8d7c55ef3bb935ad487c529f5be5343d`



\*\*Verification Result:\*\* Passed



\## 6. Usage Notes



\- The `.bsp` file is a binary SPICE kernel and is not directly readable as a CSV or plain-text table.

\- SPICE Toolkit software is required to extract trajectory information.

\- The kernel provides reconstructed spacecraft trajectory data, not a complete record of every spacecraft maneuver.

\- Additional SPICE kernels may be required for time conversion, reference frames, and planetary ephemerides.



\## 7. Limitations



\- This dataset represents a specific historical MAVEN mission trajectory.

\- It should not be treated as a universal Mars approach trajectory for other spacecraft.

\- Detailed orbit-insertion maneuver parameters should be verified using appropriate mission documentation and supporting SPICE products.



\## 8. Provenance



Original SPK filename: `trj\_c\_131118-140923\_rec\_v1.bsp`



Created by: MAVEN Navigation Team, NASA/JPL  

Metadata publication year: 2015  

Original file creation date: 2015-05-24



The dataset is retained in its original binary format. The accompanying XML metadata is preserved for provenance and documentation.


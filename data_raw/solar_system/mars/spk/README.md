# MAVEN SPICE SPK — Reconstructed Cruise Trajectory

## 1. Dataset Overview

This dataset contains the reconstructed cruise trajectory of NASA's Mars Atmosphere and Volatile Evolution (MAVEN) spacecraft.

The data is provided as a binary SPICE SPK (Spacecraft and Planet Kernel) file, which contains spacecraft position and velocity information over a specified time interval.

**Spacecraft:** MAVEN
**Mission Destination:** Mars
**Kernel Type:** SPK
**Data Type:** Reconstructed Cruise Trajectory

## 2. Files

| Filename | Description |
|---|---|
| `maven_cru_rec_131118_140923_v1.bsp` | Binary SPICE SPK trajectory kernel |
| `maven_cru_rec_131118_140923_v1.xml` | NASA PDS4 metadata describing the SPK file |

## 3. SPK Technical Inspection

### 3.1 Trajectory Phases by Center Body

The SPICE BRIEF utility (`-utc -c` options), together with the NAIF Leap Seconds Kernel (`naif0012.tls`), was used to inspect the MAVEN spacecraft trajectory coverage and group the results by center body.

| Trajectory Phase | Center Body ID | Center Body | Start Time (UTC) | End Time (UTC) |
|---|---:|---|---|---|
| Earth-centered phase | 399 | Earth | 2013-NOV-18 19:20:42.160 | 2013-NOV-21 13:07:56.081 |
| Sun-centered phase | 10 | Sun | 2013-NOV-21 13:07:56.081 | 2014-SEP-20 01:09:08.964 |
| Mars-system phase | 4 | Mars Barycenter | 2014-SEP-20 01:09:08.964 | 2014-SEP-23 11:58:52.817 |

**Note:** The final phase is centered on the Mars Barycenter (ID 4), not directly on Mars (ID 499). Mars (ID 499) is listed separately in the SPK summary as a body whose state is defined relative to the Mars Barycenter. These are distinct SPK entries and should not be confused.

The three rows above represent the trajectory coverage grouped by center body. They do not indicate that the MAVEN spacecraft trajectory consists of only three individual SPK records.

**Verification:** Coverage and center-body information were inspected using NAIF's SPICE BRIEF utility (Version 4.1.0), with the NAIF Leap Seconds Kernel (`naif0012.tls`) for UTC conversion.

### 3.2 Reference Frame and SPK Data Type

The NAIF SPACIT utility, using the NAIF Leap Seconds Kernel (`naif0012.tls`), was used to inspect the detailed SPK segment information.

**MAVEN Spacecraft Trajectory:**
- **Target Body ID:** -202 (MAVEN)
- **Reference Frame:** J2000 (Frame ID 1)
- **SPK Data Type:** Type 1
- **Data Description:** Modified Difference Array

The MAVEN spacecraft trajectory is represented by multiple SPK Type 1 records. These records use different center bodies depending on the spacecraft's trajectory phase:

- **Earth (399):** Earth-centered trajectory records
- **Sun (10):** Sun-centered trajectory records
- **Mars Barycenter (4):** Mars-system trajectory records

**Additional Ephemeris Data:**

The SPK file also contains planetary and natural satellite ephemeris data, including Mars (499), Phobos (401), and Deimos (402). These are separate SPK entries and use different SPK data types. They should not be confused with the MAVEN spacecraft trajectory records.

**Verification:** Reference frame, target body, center body, and SPK data type were inspected using the NAIF SPACIT utility.

## 4. Data Source

**Provider:** NASA / Jet Propulsion Laboratory (JPL) — NAIF

**Mission Data Archive:** MAVEN SPICE Archive

- [MAVEN SPICE Documentation](https://naif.jpl.nasa.gov/pub/naif/pds/pds4/maven/maven_spice/document/spiceds_v005.html)
- [SPK Kernel Directory](https://naif.jpl.nasa.gov/pub/naif/pds/pds4/maven/maven_spice/spice_kernels/spk/)

## 5. File Integrity

The downloaded SPK file was verified against the MD5 checksum provided in its official NASA PDS4 XML metadata.

**Expected MD5:**

`8d7c55ef3bb935ad487c529f5be5343d`

**Calculated MD5:**

`8d7c55ef3bb935ad487c529f5be5343d`

**Verification Result:** Passed

The calculated MD5 checksum matches the checksum recorded in the accompanying XML metadata.

## 6. Usage Notes

- The `.bsp` file is a binary SPICE kernel and is not directly readable as a CSV or plain-text table.
- SPICE Toolkit software is required to extract trajectory information.
- The kernel provides reconstructed spacecraft trajectory data, not a complete record of every spacecraft maneuver.
- Additional SPICE kernels may be required for time conversion, reference frames, and planetary ephemerides.

## 7. Limitations

- This dataset represents a specific historical MAVEN mission trajectory.
- It should not be treated as a universal Mars approach trajectory for other spacecraft.
- Detailed orbit-insertion maneuver parameters should be verified using appropriate mission documentation and supporting SPICE products.

## 8. Provenance

**Original SPK Filename:** `trj_c_131118-140923_rec_v1.bsp`

**Created by:** MAVEN NAV Team, NASA/JPL
**Metadata Publication Year:** 2015
**Original File Creation Date:** 2015-05-24T07:43:23

**PDS4 Logical Identifier:**

`urn:nasa:pds:maven.spice:spice_kernels:spk_maven_cru_rec_131118_140923_v1.bsp`

The dataset is retained in its original binary format. The accompanying XML metadata is preserved for provenance and documentation.
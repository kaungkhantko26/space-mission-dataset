# Ephemeris validation report

Date prepared: 2026-11-14

## Kernel inventory

| File | Size (bytes) | SHA-256 | Result |
|---|---:|---|---|
| `raw\naif\de440s.official.bsp` | 32,726,016 | `C1C7FEEAB882263FC493A9D5A5B2DDD71B54826CDF65D8D17A76126B260A49F` | PASS: read by NAIF `brief.exe` N0067 |
| `raw\naif\latest_leapseconds.tls` | 5,257 | `678E32BDB5A744117A467CD9601CD6B373F0E9BC9BBDE1371D5EEE39600A039B` | Present; used by `STATES` |
| `raw\naif\pck00011.tpc` | 131,226 | `3DFF7B1DBECEAA01F25467767D3FA25816051C85D162D1EDF04ACB310EE28BB1` | Present |

## SPICE-derived state vectors

The three CSV files contain 4,018 rows each, daily from 2026-01-01 through 2037-01-01 inclusive. Targets are Earth (399), Moon (301), and Sun (10); observer is solar-system-barycenter (0). Frame is J2000, corrections are `NONE`, time scale is UTC-labelled output from the STATES run, and units are km and km/s. The source is DE440S through CSPICE `STATES` N0067.

Checks performed:

- PASS: all three targets were successfully read and returned states for all requested epochs.
- PASS: row counts are equal (4,018 per target).
- PASS: no missing numeric state fields were observed during CSV conversion.
- PASS: requested endpoint dates are present.
- PASS: DE440S SPK was independently opened by `brief.exe`; coverage includes the full requested interval.

## Horizons and cross-check status

NOT COMPLETE: raw Horizons response files have not been saved here, and no direct timestamp-by-timestamp Horizons-vs-DE440S comparison is reported. The API configuration to use is: target 399/301/10; center `@0`; vectors; 2026-01-01 to 2037-01-01; step `1 d`; TDB; `KM-S`; geometric corrections `NONE`; ICRF/J2000-compatible request. Any final comparison must record the actual Horizons frame/source header rather than assuming it.


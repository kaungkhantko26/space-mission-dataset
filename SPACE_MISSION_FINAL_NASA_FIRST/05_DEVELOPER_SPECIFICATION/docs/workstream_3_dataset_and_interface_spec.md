# Workstream 3 — Developer Dataset and Interface Specification (Draft 0.1)

**Architecture confirmed by the team:** browser-based application using React + TypeScript and Three.js.  
**Scope:** developer-facing data contracts, time/frame/unit conventions, telemetry, event display, rendering adapter, integration and validation.  
**Excluded:** independent Earth–Moon/Earth–Mars transfer research, landing calculations, surface operations and material gathering; those belong to other researchers.

## 1. What this package provides

This is not another planetary trajectory dataset. It provides the common technical conventions and data structures that allow the launch module, the teammate-owned transfer module and the browser visualizer to exchange consistent state.

Included:
- Unit, time-scale, reference-frame and coordinate-transform registries.
- Mission-phase, telemetry-field and module-handoff registries.
- JSON Schema Draft 2020-12 contracts for state, telemetry, events and module handoffs.
- A small NASA Artemis I event-time reference CSV for timeline UI testing.
- A catalogue of the official Artemis II Orion environmental CSVs and SPICE assets, plus a downloader script.
- A Three.js render-only coordinate adapter; it does not perform orbital mechanics.
- Validation test matrix and source-selection decisions.

## 2. Recommended module boundaries

1. **Mission configuration (React/TypeScript):** collects player choices and validates mission configuration.
2. **Scientific simulation module:** computes launch/vehicle/trajectory states using physical units. It must not depend on Three.js scene coordinates.
3. **Transfer module:** receives a launch-to-transfer handoff and returns time-tagged states. Earth–Moon/Earth–Mars transfer algorithms and datasets remain owned by the other researcher.
4. **Mission/event manager:** stores event identifiers and timestamps with explicit time basis.
5. **Telemetry adapter:** maps internal simulation states into the telemetry contract; marks missing and estimated fields explicitly.
6. **Three.js renderer:** consumes already computed state, applies a declared frame transform, local-origin rebasing, and visual scale, then renders meshes/lines.

## 3. Canonical cross-module state

Use kilometres and kilometres per second for orbital/transfer state exchange. Workstream 1 launch helpers may calculate in SI metres and metres per second internally, but convert at the launch/transfer boundary. Every state must declare:

- exact `reference_frame` name;
- exact `origin`/observer;
- `epoch_tdb_seconds_past_j2000` for ephemeris computation;
- `epoch_utc` as a display/provenance timestamp when known;
- Cartesian position and velocity vectors;
- data-quality status and source/quality flags.

Do not assume a frame name automatically supplies the origin. Do not combine J2000 and ECLIPJ2000 states without a transform. NAIF defines SPICE ET as TDB and documents J2000 epoch as 2000-01-01 12:00:00 TDB. Use SPICE `pxform` for position-vector transformations and `sxform` for six-component state transformations.

## 4. Time handling

- UTC is for user display, mission logs and published event dates.
- TDB/ET seconds past J2000 is for SPICE ephemeris/state computation.
- MET is elapsed time relative to a named mission start event; it is not an independent absolute time scale.
- SCLK is only required when decoding spacecraft-clock-tagged products and requires the relevant SCLK kernel.
- Keep the leap-second kernel (LSK) in the SPICE kernel set for UTC/TDB conversions.

## 5. Frame handling

- Preserve each source's exact frame label and origin.
- J2000 and ECLIPJ2000 are distinct frames.
- J2000 and ICRF are closely aligned; some modern JPL data products use ICRF axes while being labelled J2000 for SPICE compatibility. Do not silently relabel arbitrary source files; follow the source/kernel documentation.
- Body-fixed frames such as IAU_EARTH, IAU_MOON and IAU_MARS require suitable orientation kernels and the relevant epoch.
- WGS84 geodetic launch-site coordinates are not inertial coordinates. Convert geodetic coordinates to Earth-fixed Cartesian, then transform to inertial at the selected launch epoch if the simulation requires it.
- Three.js scene coordinates are render-only. The default Object3D up direction is +Y; the project must select and document the mapping from the scientific frame to the scene axes.

## 6. Three.js rendering rule

The scientific simulation owns the physical state. Three.js receives a position already transformed into the chosen rendering frame. Before applying display scale:

1. subtract a local render origin from large world coordinates;
2. apply the explicitly configured axis mapping/rotation;
3. multiply by `sceneUnitsPerKm`;
4. set the corresponding mesh/trajectory position.

Changing scene scale or camera controls must never change the physical simulation state. The supplied `sceneCoordinates.ts` only performs local rebasing, signed-axis selection and scaling; it does not transform J2000 into ITRF, compute ephemerides or propagate a trajectory.

## 7. NASA reference fixtures

### Artemis I event sequence

`data/artemis_i_mission_event_reference.csv` contains selected NASA-published Mission Elapsed Time values for launch, maximum dynamic pressure, booster separation, jettisons, core-stage events, perigee raise and TLI. It supports event sorting/marker tests only. It is not a continuous trajectory or telemetry series.

### Artemis II environment records

The Artemis II PDS Mission Bundle contains two HOBO locker data logger CSV products with companion PDS4 XML labels. PDS describes the products as temperature, relative humidity and dew point sampled every 60 seconds from March 26 to April 21, 2026. These are environment records for Orion storage lockers, not spacecraft navigation states. Inspect the CSV headers and XML labels before ingesting exact units/columns.

### Artemis II SPICE reference

The NAIF archive provides a meta-kernel and SPICE kernels. The reconstructed Orion SPK and gap-fill kernel can serve as a reference fixture to validate state retrieval, timestamp/frame handling and the Three.js render adapter. The filename indicates an April 2–10, 2026 reconstructed SPK interval; query exact SPK coverage with the Toolkit and do not extrapolate outside it. The archive documentation itself says coverage begins at launch for the overall archive, but individual kernels have their own coverage.

## 8. Optional NASA announced sources

- **DONKI:** optional space-weather event panel; not a trajectory force model. Use a server-side/serverless proxy for API keys; never hardcode a private key into the browser bundle.
- **OSDR:** defer unless gameplay includes astronaut biology/health. Not a launch/trajectory source.
- **FIRMS:** defer to surface/environment features or the landing researcher; requires a Map Key for its area API.
- **SPHEREx:** optional scientific sky context only; its DR1/QR3 products are FITS spectral images/cubes and are not a substitute for star catalogs or planetary ephemerides.
- **NASA Open Data:** use as a discovery catalogue; follow each record to the authoritative archive.
- **Kaggle:** discovery only; verify any candidate against its original publisher and licence.

## 9. Required error behavior

- Reject missing or ambiguous frame/origin metadata.
- Reject mismatched vector units or convert at a documented boundary.
- Report SPICE out-of-coverage errors rather than extrapolating silently.
- Keep null/unavailable telemetry distinct from numeric zero.
- Retain quality flags for published, reconstructed, calculated, estimated and game-configurable values.
- If optional DONKI/FIRMS/SPHEREx services fail, core mission simulation must continue.

## 10. What developers should implement next

1. Validate incoming JSON messages against the included schemas.
2. Agree with transfer and landing researchers on a shared frame, origin and epoch convention before integration.
3. Implement a scientific-frame adapter outside Three.js.
4. Implement the render-only scene adapter and choose scale/axis configuration.
5. Connect telemetry and mission events to UI panels and 3D markers.
6. Run `simulation_validation_test_matrix.csv` and retain validation outcomes.

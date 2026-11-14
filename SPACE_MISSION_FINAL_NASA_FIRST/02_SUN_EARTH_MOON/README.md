# Sun-Earth-Moon (NASA NAIF)

Use the shared NAIF DE440S SPK, LSK and PCK under `../01_COMMON_FOUNDATION/naif_kernels/`. The project-owned processed Earth, Moon, Sun state-vector CSVs (4,018 rows each) are preserved under `QA_HOLD/` for traceability only. Their `epoch_utc` labels drift from exact UTC midnight: 2026-01-02 appears as 00:00:22, 2026-01-03 as 00:00:43. They are therefore not certified for direct timestamp-based propagation or intercomparison. Re-extract state vectors with a correctly time-converted SPICE query; validate TDB/UTC, frame J2000, origin SSB, NAIF target IDs 10/399/301, and compare against Horizons with matched conditions.

The Moon transfer trajectory itself belongs to the teammate; this folder contains foundations, not an Earth-Moon maneuver solution.

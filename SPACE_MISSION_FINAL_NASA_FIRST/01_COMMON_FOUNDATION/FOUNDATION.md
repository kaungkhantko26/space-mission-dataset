# Shared scientific foundation for exactly two mission systems

Scope: Sun-Earth-Moon and Sun-Earth-Mars. The shared Sun, Earth, time-scale, physical-unit, ephemeris and frame conventions live here ONCE. This avoids duplicated and conflicting constants.

- NAIF IDs: Sun=10, Earth=399, Moon=301, Mars=499, Solar System Barycenter=0.
- State vectors use km and km/s, and every state must declare its **frame, origin and epoch/time scale**.
- NASA DE440S SPICE kernel is the shared reference kernel; do not load multiple duplicate copies.
- Time: NASA SPICE ET is TDB seconds past J2000; UTC display times require correct SPICE LSK conversion.
- Frame: J2000/NAIF and ECLIPJ2000 are distinct frames; perform state-frame transformations correctly before combining data.
- Modules exchange spacecraft state; the launch module must not implement the other researcher's Moon/Mars transfer solutions.
- Store one physical source; create mission-specific **views** or links to shared foundations.

Data quality warning: processed 2026-2037 Earth/Moon/Sun CSVs in the original final_ephemiris archive show non-midnight UTC drift and are held in a QA folder, not certified time series. The NAIF SPK remains the primary scientific asset until re-extraction and verification.

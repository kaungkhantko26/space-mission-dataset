# Source manifest

Retrieval date for this package: 2026-11-14 (Asia/Rangoon).

| ID | Source | Exact URL | Local file | Use | License/attribution |
|---|---|---|---|---|---|
| JPL-SSD-PHYS | JPL Solar System Dynamics, Planetary Physical Parameters | https://ssd.jpl.nasa.gov/planets/phys_par.html | `raw/planetary_constants/jpl_planetary_physical_parameters.html` | radii, mass, gravity, escape velocity reference | NASA/JPL public technical data; retain attribution and source URL |
| JPL-SSD-SAT | JPL Solar System Dynamics, Planetary Satellite Physical Parameters | https://ssd.jpl.nasa.gov/sats/phys_par/ | `raw/planetary_constants/jpl_satellite_physical_parameters.html` | Moon GM/radius reference | NASA/JPL public technical data; retain attribution and source URL |
| NAIF-PCK | NASA/JPL NAIF generic planetary constants kernel | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc | `raw/naif/pck00011.tpc` | body radii, orientation/rotation constants | NAIF/SPICE data; preserve kernel comments and attribution |
| NAIF-LSK | NASA/JPL NAIF latest generic leap-second kernel | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/latest_leapseconds.tls | `raw/naif/latest_leapseconds.tls` | UTC/TAI/ET conversion support | NAIF/SPICE data; preserve kernel comments and attribution |
| NAIF-DE440S | NASA/JPL NAIF DE440 short planetary ephemeris kernel | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp | `raw/naif/de440s.bsp` | planetary and lunar barycentric states | NAIF/JPL SPICE data; preserve kernel comments and attribution |
| NASA-GRC-ATM | NASA Glenn Research Center, Earth atmosphere equation (metric) | https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/earth-atmosphere-equation-metric/ | `raw/earth_atmosphere/nasa_grc_earth_atmosphere_equation_metric.html` | standard-atmosphere equations/assumptions | NASA public-domain material; retain NASA attribution |
| NASA-GRC-TABLE | NASA Glenn Research Center, ICAO standard-atmosphere table | https://www.grc.nasa.gov/WWW/K-12/WindTunnel/Activities/lift_formula.html | `raw/earth_atmosphere/nasa_grc_icao_standard_atmosphere_table.html` | tabulated density/speed-of-sound reference | NASA public-domain material; retain NASA attribution |
| JPL-HORIZONS | JPL Horizons API | https://ssd.jpl.nasa.gov/api/horizons.api | `raw/ephemeris/horizons_query_template.json` | configurable mission ephemeris retrieval | NASA/JPL service; cite URL and retrieval date for each generated result |

The GitHub repository inspected before creation was https://github.com/minm01210-svg/Space-mission-. Existing files include `atmospheric_properties.csv`, `celestial_bodies.csv`, `launch_site_specs.csv`, `orbit_targets.csv`, `planetary_ephemeris_template.csv`, `source_register.csv`, and other game data. None were overwritten or copied here.

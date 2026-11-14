# Sun-Earth-Mars (NASA/JPL only)

This folder contains the original JPL Horizons Earth and Mars geometric vector responses and a parsed CSV with 244 observations (122 epochs per body). They use **TDB**, **ECLIPJ2000**, **Solar System Barycenter** as origin, and **km/km-s**. They are DE441/mar099 Horizons solutions, not DE440S/J2000, and must not be joined directly to the Earth-Moon-Sun CSVs without a frame/time/source conversion.

Shared Sun reference and NAIF kernels live in `../01_COMMON_FOUNDATION/`. Solar state is not included as a matched ECLIPJ2000/DE441 Horizons vector here; to use Sun-Earth-Mars gravitational calculations, obtain the Sun vector in exactly the agreed frame/time/origin, or query it from the same approved NAIF model/kernel in the agreed frame.

Data interval is the source's 43,200-minute (30-day) step. Do not treat this sparse table as a high-resolution mission transfer path. The transfer algorithm and further data belong to your teammate.

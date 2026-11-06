# Data licensing and attribution

*This is a practical summary, not legal advice. The repository owner chose the defaults below; change them if you prefer.*

| Part of the repository | Status |
|---|---|
| **Compilation, normalization, derived values, analysis, optimization results, reports** (`space-mission-research/`, `docs/data`, `docs/api`, `exports/`) created for this project | Offered under **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/) — attribute "kaungkhantko26/space-mission-dataset". |
| **Facts and figures taken from NASA / JPL / NSSDC / NTRS documents** | U.S. Government works are generally not subject to copyright in the United States; please credit NASA/JPL and the cited document. Source URLs and file hashes are in `metadata/sources.json` and `data_raw/retrieved/MANIFEST.json`. |
| **Figures taken from ULA and ESA web pages** (Atlas V, Vulcan, Vega-C, Ariane 6) | Factual specifications quoted for verification, with attribution to the source page. The page text itself is not redistributed except short quoted snippets in `field_verification`; the cached HTML copies in `data_raw/retrieved/` are kept only so checks are reproducible. Remove them if a rights holder objects. |
| **JPL satellite mean elements** (`verified/`, `docs/data`, `exports/`) | Ingested directly from NASA/JPL services; credit NASA/JPL (SSD). |
| **NASA Small Spacecraft SoA report tables; NSSDC catalog pages/descriptions** | NASA material; credit NASA. SoA values are vendor-reported (verify with the vendor before relying on them). |
| **NIST WebBook fluid data** | NIST Standard Reference Data; credit NIST (see https://webbook.nist.gov/ for its terms). |
| **The Space Devs Launch Library 2 data** (`launch_vehicle_configs`, `spacex_launch_history`) | Third-party aggregator. **Its terms of use were not verified** (the API is free to use with attribution and is aimed at non-commercial use; check https://thespacedevs.com/llapi before commercial use). Credit "The Space Devs - Launch Library 2". |
| **`data_raw/spacex_launch_data.csv`** and **`data_raw/NASA_Facilities.csv`** (the latter is not used by the game and not published) | **Supplied by the repository owner; origin and licence not verified; excluded from the public verified dataset** (kept only in `data_raw/` and the staging build). The SpaceX table is described as Kaggle `scoleman/spacex-launch-data`; check that dataset's licence before redistributing. Do not assume commercial reuse is permitted. |
| **Values marked `unverified`** | Recalled values, not copied from a licensed source; treat as unverified facts. |
| **`estimated` / `fictional` values** (optimizer catalog, credits, science weights) | Original, created for this project (CC BY 4.0). Not real hardware or prices. |
| **Code** | MIT (see `LICENSE`). |

NASA does not endorse this project. Do not use NASA, JPL, ESA, ULA or SpaceX logos or names to imply endorsement.

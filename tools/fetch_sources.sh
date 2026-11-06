#!/usr/bin/env bash
# Re-fetches the source pages used for verification into data_raw/retrieved/ (needs network access to the hosts below).
# Afterwards: python3 -I tools/verify_celestial.py && python3 -I tools/verify_launch.py && python3 tools/build.py && python3 tools/validate.py
set -euo pipefail
cd "$(dirname "$0")/../data_raw/retrieved"
get() { curl -sS --fail -m 60 -L -A "Mozilla/5.0 (research-dataset retrieval)" -o "$2" "$1" && echo "ok  $2"; }
get https://ssd.jpl.nasa.gov/planets/phys_par.html            jpl_planets_phys_par.html
get https://ssd.jpl.nasa.gov/sats/phys_par/                   jpl_sats_phys_par.html
get https://ssd.jpl.nasa.gov/planets/approx_pos.html          jpl_approx_pos.html
for p in mercury venus earth mars jupiter saturn uranus neptune moon pluto sun; do
  get "https://nssdc.gsfc.nasa.gov/planetary/factsheet/${p}fact.html" "nssdc_${p}.html"
done
get "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=101955&phys-par=1" sbdb_bennu.json
get "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=1&phys-par=1"      sbdb_ceres.json
get "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=4&phys-par=1"      sbdb_vesta.json
get "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=134340&phys-par=1" sbdb_pluto.json
get "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=136199&phys-par=1" sbdb_eris.json
get https://www.nasa.gov/reference/space-launch-system/        nasa_sls_reference.html
get https://www.ulalaunch.com/rockets/atlas-v                  ula_atlas_v.html
get https://www.ulalaunch.com/rockets/vulcan-centaur          ula_vulcan.html
get https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Vega-C                esa_vega_c.html
get https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_6_overview    esa_ariane6_overview.html
for id in 19690022248 19980017550 20090004685 20060051789; do
  get "https://ntrs.nasa.gov/api/citations/$id/downloads/$id.pdf" "ntrs_$id.pdf"
  pdftotext -layout "ntrs_$id.pdf" "ntrs_$id.txt"; pdftotext "ntrs_$id.pdf" "ntrs_${id}_raw.txt"
done
